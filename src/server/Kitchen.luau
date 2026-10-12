-- Postes de cuisine : cagettes/frigos, planches, pianos, passe, poubelles.
-- Chaque joueur tient au plus une chose : un ingrédient ou une assiette.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Recipes = require(ReplicatedStorage.Shared.Recipes)
local ItemVisuals = require(ReplicatedStorage.Shared.ItemVisuals)

local Kitchen = {}

export type Held = { kind: "item", id: string } | { kind: "plate", contents: { string } }

local held: { [Player]: Held? } = {}
local heldModel: { [Player]: Model? } = {}

local remotes = Instance.new("Folder")
remotes.Name = "Remotes"
local notifyEvent = Instance.new("RemoteEvent")
notifyEvent.Name = "Notify"
notifyEvent.Parent = remotes
remotes.Parent = ReplicatedStorage

function Kitchen.notify(player: Player?, text: string, kind: string?)
	if player then
		notifyEvent:FireClient(player, text, kind or "info")
	else
		notifyEvent:FireAllClients(text, kind or "info")
	end
end

local function setAnchored(model: Model, anchored: boolean)
	for _, p in model:GetDescendants() do
		if p:IsA("BasePart") then
			p.Anchored = anchored
		end
	end
end
Kitchen.setAnchored = setAnchored

local function heldText(h: Held?): string
	if not h then
		return ""
	end
	if h.kind == "item" then
		return Recipes.label(h.id)
	end
	local dish = Recipes.matchDish(h.contents)
	if dish then
		return dish.emoji .. " " .. dish.label
	end
	if #h.contents == 0 then
		return "Assiette vide"
	end
	local names = {}
	for _, id in h.contents do
		table.insert(names, Recipes.label(id))
	end
	return "Assiette : " .. table.concat(names, ", ")
end
Kitchen.heldText = heldText

local function refreshHeld(player: Player)
	local old = heldModel[player]
	if old then
		old:Destroy()
		heldModel[player] = nil
	end
	local h = held[player]
	player:SetAttribute("Holding", heldText(h))
	local char = player.Character
	local hrp = char and char:FindFirstChild("HumanoidRootPart") :: BasePart?
	if not h or not hrp then
		return
	end
	local at = hrp.CFrame * CFrame.new(0, -0.1, -1.7)
	local model = if h.kind == "item" then ItemVisuals.item(h.id, at, 1) else ItemVisuals.plate(h.contents, at)
	model.Name = "Held"
	local weld = Instance.new("WeldConstraint")
	weld.Part0 = hrp
	weld.Part1 = model.PrimaryPart
	weld.Parent = model.PrimaryPart
	ItemVisuals.label(model.PrimaryPart :: BasePart, heldText(h), 1.8)
	model.Parent = char
	heldModel[player] = model
end

function Kitchen.getHeld(player: Player): Held?
	return held[player]
end

function Kitchen.setHeld(player: Player, h: Held?)
	held[player] = h
	refreshHeld(player)
end

-- ------------------------------------------------------------------ prompts
local function makePrompt(part: BasePart, action: string, object: string, hold: number?): ProximityPrompt
	local prompt = Instance.new("ProximityPrompt")
	prompt.ActionText = action
	prompt.ObjectText = object
	prompt.HoldDuration = hold or 0
	prompt.MaxActivationDistance = 8
	prompt.RequiresLineOfSight = false
	prompt.Parent = part
	return prompt
end

local function sparkle(part: BasePart, color: Color3)
	local att = Instance.new("Attachment")
	att.Position = Vector3.new(0, part.Size.Y / 2 + 0.3, 0)
	att.Parent = part
	local pe = Instance.new("ParticleEmitter")
	pe.Color = ColorSequence.new(color)
	pe.Size = NumberSequence.new(0.25, 0)
	pe.Lifetime = NumberRange.new(0.3, 0.6)
	pe.Speed = NumberRange.new(4, 7)
	pe.SpreadAngle = Vector2.new(180, 180)
	pe.Rate = 0
	pe.Parent = att
	pe:Emit(14)
	task.delay(1, function()
		att:Destroy()
	end)
end

-- Cagette / frigo : on prend un ingrédient brut
local function setupCrate(part: BasePart)
	local id = part:GetAttribute("Ingredient") :: string
	if not Recipes.Items[id] then
		return -- cagette décorative
	end
	local prompt = makePrompt(part, "Prendre", Recipes.label(id))
	prompt.Triggered:Connect(function(player)
		if held[player] then
			Kitchen.notify(player, "Tu as déjà les mains pleines !", "warn")
			return
		end
		Kitchen.setHeld(player, { kind = "item", id = id })
	end)
end

-- Planche à découper
local function setupBoard(part: BasePart)
	local prompt = makePrompt(part, "Couper", "Planche", 1.1)
	prompt.Triggered:Connect(function(player)
		local h = held[player]
		if not h or h.kind ~= "item" then
			Kitchen.notify(player, "Apporte un ingrédient à couper.", "warn")
			return
		end
		local it = Recipes.Items[h.id]
		if not it or it.prep ~= "Board" or not it.result then
			Kitchen.notify(player, Recipes.label(h.id) .. " ne se coupe pas.", "warn")
			return
		end
		Kitchen.setHeld(player, { kind = "item", id = it.result })
		sparkle(part, it.color)
	end)
end

-- Piano de cuisson
type StoveState = { raw: string, current: string, start: number, model: Model?, gui: BillboardGui, fill: Frame, smoke: ParticleEmitter }

local function setupStove(part: BasePart)
	local state: StoveState? = nil
	local prompt = makePrompt(part, "Utiliser", "Piano")

	local function clear()
		if state then
			if state.model then
				state.model:Destroy()
			end
			state.gui:Destroy()
			state.smoke:Destroy()
			state = nil
		end
	end

	local function showItem(id: string)
		if not state then
			return
		end
		if state.model then
			state.model:Destroy()
		end
		local at = part.CFrame * CFrame.new(0, part.Size.Y / 2 + 0.35, -0.4)
		local m = ItemVisuals.item(id, at, 1.1)
		setAnchored(m, true)
		m.Parent = part
		state.model = m
	end

	prompt.Triggered:Connect(function(player)
		local h = held[player]
		if not state then
			if h and h.kind == "item" then
				local it = Recipes.Items[h.id]
				if it and it.prep == "Stove" then
					local gui = Instance.new("BillboardGui")
					gui.Size = UDim2.fromOffset(90, 12)
					gui.StudsOffset = Vector3.new(0, 2.2, 0)
					gui.AlwaysOnTop = true
					gui.MaxDistance = 50
					local bg = Instance.new("Frame")
					bg.Size = UDim2.fromScale(1, 1)
					bg.BackgroundColor3 = Color3.fromRGB(30, 30, 34)
					bg.Parent = gui
					local fill = Instance.new("Frame")
					fill.Size = UDim2.fromScale(0, 1)
					fill.BackgroundColor3 = Color3.fromRGB(255, 170, 40)
					fill.BorderSizePixel = 0
					fill.Parent = bg
					Instance.new("UICorner").Parent = bg
					Instance.new("UICorner").Parent = fill
					gui.Parent = part
					local smoke = Instance.new("ParticleEmitter")
					smoke.Color = ColorSequence.new(Color3.fromRGB(235, 235, 235))
					smoke.Transparency = NumberSequence.new(0.6, 1)
					smoke.Size = NumberSequence.new(0.6, 2.2)
					smoke.Lifetime = NumberRange.new(1, 2)
					smoke.Speed = NumberRange.new(2, 4)
					smoke.Rate = 6
					smoke.Parent = part
					state = { raw = h.id, current = h.id, start = os.clock(), gui = gui, fill = fill, smoke = smoke }
					showItem(h.id)
					Kitchen.setHeld(player, nil)
					return
				end
				Kitchen.notify(player, Recipes.label(h.id) .. " ne se cuit pas.", "warn")
			else
				Kitchen.notify(player, "Pose un steak ou des pâtes sur le piano.", "warn")
			end
			return
		end
		-- le piano est occupé : on récupère
		if not h then
			Kitchen.setHeld(player, { kind = "item", id = state.current })
			clear()
		elseif h.kind == "plate" and Recipes.isPlateable(state.current) then
			if table.find(h.contents, state.current) then
				Kitchen.notify(player, "Il y en a déjà sur l'assiette.", "warn")
				return
			end
			table.insert(h.contents, state.current)
			Kitchen.setHeld(player, h)
			clear()
		else
			Kitchen.notify(player, "Les mains pleines ! Pose d'abord ce que tu tiens.", "warn")
		end
	end)

	RunService.Heartbeat:Connect(function()
		if not state then
			return
		end
		local it = Recipes.Items[state.raw]
		local t = os.clock() - state.start
		local cook, burn = it.cookTime or 6, it.burnTime or 16
		local target = state.raw
		if t >= burn then
			target = Recipes.Burnt[state.raw] or state.raw
			state.fill.Size = UDim2.fromScale(1, 1)
			state.fill.BackgroundColor3 = Color3.fromRGB(200, 40, 40)
			state.smoke.Color = ColorSequence.new(Color3.fromRGB(60, 60, 60))
			state.smoke.Rate = 20
		elseif t >= cook then
			target = it.result or state.raw
			state.fill.Size = UDim2.fromScale(1, 1)
			local blink = math.floor(t * 4) % 2 == 0
			state.fill.BackgroundColor3 = if t > burn - 5 and blink then Color3.fromRGB(230, 90, 40) else Color3.fromRGB(90, 200, 90)
			state.smoke.Rate = 10
		else
			state.fill.Size = UDim2.fromScale(t / cook, 1)
		end
		if target ~= state.current then
			state.current = target
			showItem(target)
		end
	end)
end

-- Emplacement d'assiette sur la passe
local function setupPass(part: BasePart)
	local contents: { string }? = nil
	local model: Model? = nil
	local prompt = makePrompt(part, "Utiliser", "Assiette")

	local function redraw()
		if model then
			model:Destroy()
			model = nil
		end
		if contents then
			local m = ItemVisuals.plate(contents, CFrame.new(part.Position + Vector3.new(0, part.Size.X / 2 + 0.01, 0)))
			setAnchored(m, true)
			ItemVisuals.label(m.PrimaryPart :: BasePart, heldText({ kind = "plate", contents = contents }), 2.2)
			m.Parent = part
			model = m
		end
	end

	prompt.Triggered:Connect(function(player)
		local h = held[player]
		if h and h.kind == "item" then
			if not Recipes.isPlateable(h.id) then
				local it = Recipes.Items[h.id]
				local msg = if it and it.raw then "Prépare d'abord : " .. it.label .. (if it.prep == "Board" then " → planche" else " → piano") else "Ça ne va pas dans une assiette !"
				Kitchen.notify(player, msg, "warn")
				return
			end
			contents = contents or {}
			if table.find(contents :: { string }, h.id) then
				Kitchen.notify(player, "Il y en a déjà sur l'assiette.", "warn")
				return
			end
			if #(contents :: { string }) >= 4 then
				Kitchen.notify(player, "L'assiette est pleine.", "warn")
				return
			end
			table.insert(contents :: { string }, h.id)
			Kitchen.setHeld(player, nil)
			redraw()
		elseif h and h.kind == "plate" then
			if contents then
				Kitchen.notify(player, "Il y a déjà une assiette ici.", "warn")
				return
			end
			contents = h.contents
			Kitchen.setHeld(player, nil)
			redraw()
		else
			if not contents then
				-- mains vides : on prend une assiette propre
				Kitchen.setHeld(player, { kind = "plate", contents = {} })
				return
			end
			Kitchen.setHeld(player, { kind = "plate", contents = contents :: { string } })
			contents = nil
			redraw()
		end
	end)
end

local function setupTrash(part: BasePart)
	local prompt = makePrompt(part, "Jeter", "Poubelle")
	prompt.Triggered:Connect(function(player)
		if held[player] then
			Kitchen.setHeld(player, nil)
		end
	end)
end

function Kitchen.start(map: Instance)
	local count = 0
	for _, part in map:GetDescendants() do
		if part:IsA("BasePart") then
			local station = part:GetAttribute("Station")
			if station == "Crate" then
				setupCrate(part)
			elseif station == "Board" then
				setupBoard(part)
			elseif station == "Stove" then
				setupStove(part)
			elseif station == "Pass" then
				setupPass(part)
			elseif station == "Trash" then
				setupTrash(part)
			end
			if station then
				count += 1
			end
		end
	end
	print(("[Kitchen] %d postes prêts"):format(count))

	local function onPlayer(player: Player)
		player:SetAttribute("Holding", "")
		player.CharacterAdded:Connect(function()
			held[player] = nil
			heldModel[player] = nil
			player:SetAttribute("Holding", "")
		end)
	end
	Players.PlayerAdded:Connect(onPlayer)
	for _, player in Players:GetPlayers() do
		onPlayer(player)
	end
	Players.PlayerRemoving:Connect(function(player)
		held[player] = nil
		heldModel[player] = nil
	end)
end

return Kitchen

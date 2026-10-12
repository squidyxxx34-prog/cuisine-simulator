-- Clients : arrivent par le trottoir, s'installent, commandent, mangent, paient.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Recipes = require(ReplicatedStorage.Shared.Recipes)
local ItemVisuals = require(ReplicatedStorage.Shared.ItemVisuals)
local Npc = require(script.Parent.Npc)
local Kitchen = require(script.Parent.Kitchen)
local Economy = require(script.Parent.Economy)

local Customers = {}

local rng = Random.new()
local folder = Instance.new("Folder")
folder.Name = "Customers"
folder.Parent = workspace

local spots: { BasePart } = {}
local taken: { [BasePart]: boolean } = {}
local active = 0
local wp: { [string]: Vector3 } = {}
local frontZ = 0
local ignoreList: { Instance } = { folder }

local function freeSpot(): BasePart?
	local free = {}
	for _, s in spots do
		if not taken[s] then
			table.insert(free, s)
		end
	end
	if #free == 0 then
		return nil
	end
	return free[rng:NextInteger(1, #free)]
end

local function orderGui(parent: BasePart, dish): (BillboardGui, Frame, TextLabel)
	local gui = Instance.new("BillboardGui")
	gui.Name = "Order"
	gui.Size = UDim2.fromOffset(150, 64)
	gui.StudsOffset = Vector3.new(0, 3.4, 0)
	gui.AlwaysOnTop = true
	gui.MaxDistance = 70
	local bubble = Instance.new("Frame")
	bubble.Size = UDim2.fromScale(1, 1)
	bubble.BackgroundColor3 = Color3.fromRGB(255, 252, 245)
	bubble.Parent = gui
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(0, 12)
	c.Parent = bubble
	local stroke = Instance.new("UIStroke")
	stroke.Color = Color3.fromRGB(31, 74, 59)
	stroke.Thickness = 2
	stroke.Parent = bubble
	local text = Instance.new("TextLabel")
	text.BackgroundTransparency = 1
	text.Size = UDim2.new(1, -10, 0.62, 0)
	text.Position = UDim2.fromOffset(5, 3)
	text.Font = Enum.Font.FredokaOne
	text.TextScaled = true
	text.TextColor3 = Color3.fromRGB(31, 40, 36)
	text.Text = dish.emoji .. " " .. dish.label
	text.Parent = bubble
	local barBg = Instance.new("Frame")
	barBg.Size = UDim2.new(1, -16, 0, 10)
	barBg.Position = UDim2.new(0, 8, 1, -18)
	barBg.BackgroundColor3 = Color3.fromRGB(220, 215, 205)
	barBg.BorderSizePixel = 0
	barBg.Parent = bubble
	Instance.new("UICorner").Parent = barBg
	local bar = Instance.new("Frame")
	bar.Size = UDim2.fromScale(1, 1)
	bar.BackgroundColor3 = Color3.fromRGB(90, 190, 90)
	bar.BorderSizePixel = 0
	bar.Parent = barBg
	Instance.new("UICorner").Parent = bar
	gui.Parent = parent
	return gui, bar, text
end

local function emote(parent: BasePart, text: string, duration: number)
	local gui = Instance.new("BillboardGui")
	gui.Size = UDim2.fromOffset(60, 60)
	gui.StudsOffset = Vector3.new(0, 3.6, 0)
	gui.AlwaysOnTop = true
	local lbl = Instance.new("TextLabel")
	lbl.BackgroundTransparency = 1
	lbl.Size = UDim2.fromScale(1, 1)
	lbl.TextScaled = true
	lbl.Text = text
	lbl.Parent = gui
	gui.Parent = parent
	task.delay(duration, function()
		gui:Destroy()
	end)
end

local function floatingCoins(parent: BasePart, amount: number)
	local gui = Instance.new("BillboardGui")
	gui.Size = UDim2.fromOffset(120, 40)
	gui.StudsOffset = Vector3.new(0, 4, 0)
	gui.AlwaysOnTop = true
	local lbl = Instance.new("TextLabel")
	lbl.BackgroundTransparency = 1
	lbl.Size = UDim2.fromScale(1, 1)
	lbl.Font = Enum.Font.FredokaOne
	lbl.TextScaled = true
	lbl.TextColor3 = Color3.fromRGB(255, 205, 60)
	lbl.TextStrokeTransparency = 0
	lbl.Text = "+" .. amount .. " 🪙"
	lbl.Parent = gui
	gui.Parent = parent
	task.spawn(function()
		for i = 1, 40 do
			gui.StudsOffset = Vector3.new(0, 4 + i * 0.06, 0)
			lbl.TextTransparency = math.max(0, (i - 20) / 20)
			task.wait(0.03)
		end
		gui:Destroy()
	end)
end

local function runCustomer()
	local spot = freeSpot()
	if not spot then
		return
	end
	taken[spot] = true
	active += 1
	local npc = Npc.new(folder)
	local fromLeft = rng:NextNumber() < 0.5
	local street = if fromLeft then wp.StreetLeft else wp.StreetRight
	local exitStreet = if rng:NextNumber() < 0.5 then wp.StreetLeft else wp.StreetRight
	local aisle = spot:GetAttribute("Aisle") :: number
	local seat = spot.CFrame
	local aislePoint = Vector3.new(aisle, 0, seat.Position.Z)
	local seatGround = Vector3.new(seat.Position.X, Npc.floorY(aislePoint, ignoreList), seat.Position.Z)
	local path = {
		wp.Curb,
		wp.Door,
		wp.FrontAisle,
		Vector3.new(aisle, 0, frontZ),
		Vector3.new(aisle, 0, seat.Position.Z),
		seatGround,
	}

	local startPos = street + Vector3.new(0, 0, rng:NextNumber(-1, 1))
	npc:standAt(Vector3.new(startPos.X, Npc.floorY(startPos, ignoreList), startPos.Z), Vector3.new(if fromLeft then 1 else -1, 0, 0))
	npc:walk(path, 10, ignoreList)
	npc:sit(seat)

	-- commande
	local dish = Recipes.randomDish(rng)
	local patience = 70 + #dish.items * 15
	local t0 = os.clock()
	local gui, bar = orderGui(npc.torso, dish)
	local prompt = Instance.new("ProximityPrompt")
	prompt.ActionText = "Servir"
	prompt.ObjectText = npc.name .. " · " .. dish.label
	prompt.MaxActivationDistance = 8
	prompt.RequiresLineOfSight = false
	prompt.Parent = npc.torso

	local served: Player? = nil
	prompt.Triggered:Connect(function(player)
		if served then
			return
		end
		local h = Kitchen.getHeld(player)
		if not h or h.kind ~= "plate" then
			Kitchen.notify(player, npc.name .. " attend : " .. dish.emoji .. " " .. dish.label, "info")
			return
		end
		local got = Recipes.matchDish(h.contents)
		if not got or got.id ~= dish.id then
			Kitchen.notify(player, "Ce n'est pas ma commande ! Je veux : " .. dish.label, "warn")
			emote(npc.torso, "🤨", 1.5)
			return
		end
		served = player
		Kitchen.setHeld(player, nil)
	end)

	while not served and os.clock() - t0 < patience do
		local frac = 1 - (os.clock() - t0) / patience
		bar.Size = UDim2.fromScale(math.max(frac, 0), 1)
		bar.BackgroundColor3 = if frac > 0.5 then Color3.fromRGB(90, 190, 90) elseif frac > 0.25 then Color3.fromRGB(240, 180, 50) else Color3.fromRGB(220, 70, 60)
		task.wait(0.2)
	end
	prompt:Destroy()
	gui:Destroy()

	if served then
		local frac = math.clamp(1 - (os.clock() - t0) / patience, 0, 1)
		local tip = math.floor(dish.price * 0.6 * frac + 0.5)
		-- assiette posée sur la table
		local offset = if spot:GetAttribute("Stool") then CFrame.new(0, 0.86, -1.95) else CFrame.new(0, 1.41, -1.85)
		local flat = CFrame.new(seat.Position) * (seat - seat.Position)
		local plate = ItemVisuals.plate(Recipes.dishById(dish.id).items, flat * offset)
		Kitchen.setAnchored(plate, true)
		plate.Parent = npc.model
		emote(npc.torso, "😋", 6)
		task.wait(6)
		plate:Destroy()
		local total = dish.price + tip
		if served.Parent then
			Economy.reward(served, total)
			Kitchen.notify(served, ("%s a adoré ! +%d 🪙 (pourboire %d)"):format(npc.name, total, tip), "good")
		end
		floatingCoins(npc.torso, total)
		emote(npc.torso, "❤️", 1.5)
		task.wait(1)
	else
		emote(npc.torso, "😠", 2)
		Kitchen.notify(nil, npc.name .. " est parti sans manger…", "bad")
		task.wait(1.5)
	end

	-- départ
	taken[spot] = nil
	npc:standAt(seatGround, -seat.LookVector)
	local back = {
		Vector3.new(aisle, 0, seat.Position.Z),
		Vector3.new(aisle, 0, frontZ),
		wp.FrontAisle,
		wp.Door,
		wp.Curb,
		exitStreet,
	}
	npc:walk(back, 10, ignoreList)
	npc:destroy()
	active -= 1
end

function Customers.start(map: Instance)
	local gameplay = map:WaitForChild("Gameplay")
	for _, s in gameplay:WaitForChild("CustomerSpots"):GetChildren() do
		if s:IsA("BasePart") then
			table.insert(spots, s)
		end
	end
	for _, p in gameplay:WaitForChild("Waypoints"):GetChildren() do
		if p:IsA("BasePart") then
			wp[p.Name] = p.Position
		end
	end
	frontZ = wp.FrontAisle.Z
	print(("[Customers] %d places"):format(#spots))

	task.spawn(function()
		task.wait(3)
		while true do
			local n = #Players:GetPlayers()
			local maxActive = math.clamp(1 + n * 2, 3, 10)
			if n > 0 and active < maxActive then
				task.spawn(function()
					local ok, err = pcall(runCustomer)
					if not ok then
						warn("[Customers]", err)
					end
				end)
			end
			task.wait(rng:NextNumber(7, 13) / math.max(1, math.sqrt(n)))
		end
	end)
end

return Customers

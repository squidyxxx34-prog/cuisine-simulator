-- Construit les modèles 3D des ingrédients et des assiettes (pièces non ancrées, sans collision).

local Recipes = require(script.Parent.Recipes)

local ItemVisuals = {}

local function newPart(model: Model, size: Vector3, color: Color3, cf: CFrame, shape: Enum.PartType?, material: Enum.Material?): BasePart
	local p = Instance.new("Part")
	p.Size = size
	p.Color = color
	p.Material = material or Enum.Material.SmoothPlastic
	if shape then
		p.Shape = shape
	end
	p.CFrame = cf
	p.Anchored = false
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.Massless = true
	p.CastShadow = false
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Parent = model
	return p
end

local UP = CFrame.Angles(0, 0, math.rad(90)) -- cylindre vertical

-- Ajoute la forme d'un item dans `model`, posée sur `base` (CFrame du dessous). Renvoie la hauteur.
local function addShape(model: Model, id: string, base: CFrame, scale: number): number
	local it = Recipes.Items[id]
	if not it then
		return 0
	end
	local s = scale
	local c = it.color
	local shape = it.shape
	if shape == "ball" then
		newPart(model, Vector3.one * 0.8 * s, c, base * CFrame.new(0, 0.4 * s, 0), Enum.PartType.Ball)
		newPart(model, Vector3.new(0.1, 0.2, 0.1) * s, Color3.fromRGB(56, 142, 60), base * CFrame.new(0, 0.85 * s, 0))
		return 0.8 * s
	elseif shape == "lettuce" then
		newPart(model, Vector3.one * 1.1 * s, c, base * CFrame.new(0, 0.55 * s, 0), Enum.PartType.Ball, Enum.Material.Grass)
		newPart(model, Vector3.one * 0.7 * s, Color3.fromRGB(197, 225, 165), base * CFrame.new(0, 0.95 * s, 0), Enum.PartType.Ball, Enum.Material.Grass)
		return 1.1 * s
	elseif shape == "baguette" then
		newPart(model, Vector3.new(2.4, 0.45, 0.45) * s, c, base * CFrame.new(0, 0.22 * s, 0), Enum.PartType.Cylinder, Enum.Material.Sand)
		return 0.45 * s
	elseif shape == "wedge" then
		local w = Instance.new("WedgePart")
		w.Size = Vector3.new(0.9, 0.6, 1.0) * s
		w.Color = c
		w.Material = Enum.Material.SmoothPlastic
		w.CFrame = base * CFrame.new(0, 0.3 * s, 0)
		w.Anchored, w.CanCollide, w.CanQuery, w.CanTouch, w.Massless, w.CastShadow = false, false, false, false, true, false
		w.Parent = model
		return 0.6 * s
	elseif shape == "patty" then
		newPart(model, Vector3.new(0.3, 1.3, 1.3) * s, c, base * CFrame.new(0, 0.15 * s, 0) * UP, Enum.PartType.Cylinder)
		return 0.3 * s
	elseif shape == "pack" then
		newPart(model, Vector3.new(0.7, 1.0, 0.35) * s, c, base * CFrame.new(0, 0.5 * s, 0))
		newPart(model, Vector3.new(0.72, 0.3, 0.37) * s, Color3.fromRGB(31, 90, 166), base * CFrame.new(0, 0.7 * s, 0))
		return 1.0 * s
	elseif shape == "slices" then
		for i = 0, 2 do
			newPart(model, Vector3.new(0.12, 0.7, 0.7) * s, c, base * CFrame.new((i - 1) * 0.35 * s, 0.06 * s + i * 0.01, 0) * UP, Enum.PartType.Cylinder)
		end
		return 0.12 * s
	elseif shape == "leaves" then
		for i = 0, 3 do
			local a = i * math.pi / 2
			newPart(model, Vector3.new(0.6, 0.1, 0.45) * s, c, base * CFrame.new(math.cos(a) * 0.25 * s, 0.05 * s, math.sin(a) * 0.25 * s) * CFrame.Angles(0, a, 0.15), nil, Enum.Material.Grass)
		end
		return 0.12 * s
	elseif shape == "bun" then
		newPart(model, Vector3.new(0.35, 1.3, 1.3) * s, c, base * CFrame.new(0, 0.17 * s, 0) * UP, Enum.PartType.Cylinder, Enum.Material.Sand)
		return 0.35 * s
	elseif shape == "heap" then
		newPart(model, Vector3.new(1.1, 0.45, 1.1) * s, c, base * CFrame.new(0, 0.22 * s, 0), Enum.PartType.Ball, Enum.Material.Sand)
		return 0.4 * s
	end
	newPart(model, Vector3.one * 0.6 * s, c, base * CFrame.new(0, 0.3 * s, 0))
	return 0.6 * s
end

local function finish(model: Model, root: BasePart): Model
	model.PrimaryPart = root
	for _, p in model:GetDescendants() do
		if p:IsA("BasePart") and p ~= root then
			local weld = Instance.new("WeldConstraint")
			weld.Part0 = root
			weld.Part1 = p
			weld.Parent = p
		end
	end
	return model
end

local function makeRoot(model: Model, at: CFrame): BasePart
	local root = newPart(model, Vector3.new(0.2, 0.2, 0.2), Color3.new(1, 1, 1), at)
	root.Name = "Root"
	root.Transparency = 1
	return root
end

-- Modèle d'un ingrédient isolé ; son Root est au centre du dessous.
function ItemVisuals.item(id: string, at: CFrame, scale: number?): Model
	local model = Instance.new("Model")
	model.Name = "Item_" .. id
	local root = makeRoot(model, at)
	addShape(model, id, at, scale or 1)
	return finish(model, root)
end

-- Modèle d'une assiette garnie.
function ItemVisuals.plate(contents: { string }, at: CFrame): Model
	local model = Instance.new("Model")
	model.Name = "Plate"
	local root = makeRoot(model, at)
	newPart(model, Vector3.new(0.12, 2.1, 2.1), Color3.fromRGB(250, 250, 246), at * CFrame.new(0, 0.06, 0) * UP, Enum.PartType.Cylinder)
	newPart(model, Vector3.new(0.13, 1.5, 1.5), Color3.fromRGB(236, 233, 226), at * CFrame.new(0, 0.07, 0) * UP, Enum.PartType.Cylinder)
	local hasBun = table.find(contents, "PainTranche") ~= nil
	if hasBun then
		-- burger / croque empilé : pain, garniture, pain
		local y = 0.13
		y += addShape(model, "PainTranche", at * CFrame.new(0, y, 0), 0.9)
		for _, id in contents do
			if id ~= "PainTranche" then
				y += addShape(model, id, at * CFrame.new(0, y, 0), 0.85)
			end
		end
		addShape(model, "PainTranche", at * CFrame.new(0, y, 0), 0.9)
	else
		for i, id in contents do
			local n = #contents
			local a = (i - 1) / math.max(n, 1) * math.pi * 2
			local r = if n > 1 then 0.45 else 0
			addShape(model, id, at * CFrame.new(math.cos(a) * r, 0.13, math.sin(a) * r), 0.7)
		end
	end
	return finish(model, root)
end

-- Étiquette flottante
function ItemVisuals.label(parent: Instance, text: string, offset: number?)
	local old = parent:FindFirstChild("ItemLabel")
	if old then
		old:Destroy()
	end
	if text == "" then
		return
	end
	local gui = Instance.new("BillboardGui")
	gui.Name = "ItemLabel"
	gui.Size = UDim2.fromOffset(160, 34)
	gui.StudsOffset = Vector3.new(0, offset or 1.6, 0)
	gui.AlwaysOnTop = true
	gui.MaxDistance = 40
	local lbl = Instance.new("TextLabel")
	lbl.Size = UDim2.fromScale(1, 1)
	lbl.BackgroundColor3 = Color3.fromRGB(20, 22, 26)
	lbl.BackgroundTransparency = 0.25
	lbl.TextColor3 = Color3.new(1, 1, 1)
	lbl.Font = Enum.Font.FredokaOne
	lbl.TextScaled = true
	lbl.Text = text
	local corner = Instance.new("UICorner")
	corner.CornerRadius = UDim.new(0, 8)
	corner.Parent = lbl
	local pad = Instance.new("UIPadding")
	pad.PaddingLeft = UDim.new(0, 6)
	pad.PaddingRight = UDim.new(0, 6)
	pad.Parent = lbl
	lbl.Parent = gui
	gui.Parent = parent
end

return ItemVisuals

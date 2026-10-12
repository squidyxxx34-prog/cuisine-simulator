-- Client PNJ « blocky » animé à la main (pièces ancrées + BulkMoveTo).

local Npc = {}
Npc.__index = Npc

local SKINS = { Color3.fromRGB(255, 220, 185), Color3.fromRGB(234, 184, 146), Color3.fromRGB(198, 134, 98), Color3.fromRGB(141, 85, 54), Color3.fromRGB(92, 58, 38) }
local SHIRTS = { Color3.fromRGB(46, 94, 78), Color3.fromRGB(179, 48, 45), Color3.fromRGB(47, 93, 138), Color3.fromRGB(236, 223, 196), Color3.fromRGB(122, 74, 140), Color3.fromRGB(230, 160, 60), Color3.fromRGB(60, 60, 64) }
local PANTS = { Color3.fromRGB(40, 48, 70), Color3.fromRGB(70, 60, 50), Color3.fromRGB(30, 30, 32), Color3.fromRGB(120, 110, 95), Color3.fromRGB(60, 80, 110) }
local HAIR = { Color3.fromRGB(40, 28, 20), Color3.fromRGB(110, 70, 40), Color3.fromRGB(220, 180, 110), Color3.fromRGB(20, 20, 20), Color3.fromRGB(160, 60, 40) }
local NAMES = { "Camille", "Lucas", "Léa", "Hugo", "Chloé", "Louis", "Inès", "Jules", "Manon", "Arthur", "Zoé", "Gabriel", "Emma", "Noah", "Jade", "Paul", "Alice", "Raphaël", "Lina", "Victor" }

local rng = Random.new()

local function pick<T>(list: { T }): T
	return list[rng:NextInteger(1, #list)]
end

local function newPart(model: Model, name: string, size: Vector3, color: Color3): BasePart
	local p = Instance.new("Part")
	p.Name = name
	p.Size = size
	p.Color = color
	p.Anchored = true
	p.CanCollide = false
	p.CanTouch = false
	p.CanQuery = name == "Torso"
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Parent = model
	return p
end

function Npc.new(parent: Instance)
	local self = setmetatable({}, Npc)
	self.name = pick(NAMES)
	local model = Instance.new("Model")
	model.Name = "Client_" .. self.name
	local skin, shirt, pants = pick(SKINS), pick(SHIRTS), pick(PANTS)
	self.torso = newPart(model, "Torso", Vector3.new(2, 2, 1), shirt)
	self.head = newPart(model, "Head", Vector3.new(2, 1, 1), skin)
	local mesh = Instance.new("SpecialMesh")
	mesh.MeshType = Enum.MeshType.Head
	mesh.Scale = Vector3.new(1.25, 1.25, 1.25)
	mesh.Parent = self.head
	local face = Instance.new("Decal")
	face.Texture = "rbxasset://textures/face.png"
	face.Face = Enum.NormalId.Front
	face.Parent = self.head
	self.hair = newPart(model, "Hair", Vector3.new(1.35, 0.35, 1.3), pick(HAIR))
	self.hat = nil
	if rng:NextNumber() < 0.3 then
		self.hat = newPart(model, "Beret", Vector3.new(0.25, 1.7, 1.7), if rng:NextNumber() < 0.5 then Color3.fromRGB(20, 20, 22) else Color3.fromRGB(150, 30, 40))
		self.hat.Shape = Enum.PartType.Cylinder
	end
	self.armL = newPart(model, "LeftArm", Vector3.new(1, 2, 1), skin)
	self.armR = newPart(model, "RightArm", Vector3.new(1, 2, 1), skin)
	self.sleeveL = newPart(model, "LeftSleeve", Vector3.new(1.05, 0.9, 1.05), shirt)
	self.sleeveR = newPart(model, "RightSleeve", Vector3.new(1.05, 0.9, 1.05), shirt)
	self.legL = newPart(model, "LeftLeg", Vector3.new(1, 2, 1), pants)
	self.legR = newPart(model, "RightLeg", Vector3.new(1, 2, 1), pants)
	self.shoeL = newPart(model, "LeftShoe", Vector3.new(1.05, 0.4, 1.15), Color3.fromRGB(35, 30, 28))
	self.shoeR = newPart(model, "RightShoe", Vector3.new(1.05, 0.4, 1.15), Color3.fromRGB(35, 30, 28))
	model.PrimaryPart = self.torso
	self.model = model
	self.root = CFrame.new()
	self.sitting = false
	self.phase = 0
	model.Parent = parent
	return self
end

-- Calcule et applique la pose. `root` = centre du torse.
function Npc:pose(root: CFrame, swing: number, sitting: boolean)
	local parts, cfs = {}, {}
	local function put(p: BasePart?, cf: CFrame)
		if p then
			table.insert(parts, p)
			table.insert(cfs, cf)
		end
	end
	local legA = if sitting then math.rad(90) else swing
	local legB = if sitting then math.rad(90) else -swing
	local armA = if sitting then math.rad(35) else -swing * 0.8
	local armB = if sitting then math.rad(35) else swing * 0.8
	put(self.torso, root)
	local headCf = root * CFrame.new(0, 1.5, 0)
	put(self.head, headCf)
	put(self.hair, headCf * CFrame.new(0, 0.58, 0.08))
	if self.hat then
		put(self.hat, headCf * CFrame.new(0.1, 0.72, 0) * CFrame.Angles(0, 0, math.rad(80)))
	end
	local aL = root * CFrame.new(-1.5, 1, 0) * CFrame.Angles(armA, 0, 0) * CFrame.new(0, -1, 0)
	local aR = root * CFrame.new(1.5, 1, 0) * CFrame.Angles(armB, 0, 0) * CFrame.new(0, -1, 0)
	put(self.armL, aL)
	put(self.armR, aR)
	put(self.sleeveL, aL * CFrame.new(0, 0.55, 0))
	put(self.sleeveR, aR * CFrame.new(0, 0.55, 0))
	local lL = root * CFrame.new(-0.5, -1, 0) * CFrame.Angles(legA, 0, 0) * CFrame.new(0, -1, 0)
	local lR = root * CFrame.new(0.5, -1, 0) * CFrame.Angles(legB, 0, 0) * CFrame.new(0, -1, 0)
	put(self.legL, lL)
	put(self.legR, lR)
	put(self.shoeL, lL * CFrame.new(0, -0.82, -0.08))
	put(self.shoeR, lR * CFrame.new(0, -0.82, -0.08))
	workspace:BulkMoveTo(parts, cfs, Enum.BulkMoveMode.FireCFrameChanged)
	self.root = root
	self.sitting = sitting
end

-- Hauteur du sol sous un point
local params = RaycastParams.new()
params.FilterType = Enum.RaycastFilterType.Exclude

function Npc.floorY(pos: Vector3, ignore: { Instance }): number
	params.FilterDescendantsInstances = ignore
	local hit = workspace:Raycast(pos + Vector3.new(0, 6, 0), Vector3.new(0, -20, 0), params)
	return if hit then hit.Position.Y else pos.Y
end

-- Marche le long d'une liste de points (au sol). Bloquant.
function Npc:walk(points: { Vector3 }, speed: number?, ignore: { Instance })
	local spd = speed or 9
	local pos = self.root.Position - Vector3.new(0, 3, 0)
	for _, target in points do
		-- Y > 0.5 : hauteur imposée ; sinon on cherche le sol
		local gy = if target.Y > 0.5 then target.Y else Npc.floorY(target, ignore)
		local goal = Vector3.new(target.X, gy, target.Z)
		local flat = Vector3.new(goal.X - pos.X, 0, goal.Z - pos.Z)
		local dist = flat.Magnitude
		if dist > 0.05 then
			local look = flat.Unit
			local t0 = os.clock()
			local dur = dist / spd
			while true do
				local a = math.min((os.clock() - t0) / dur, 1)
				local p = pos:Lerp(goal, a)
				self.phase += 0.016 * spd * 0.9
				local swing = math.sin(self.phase * 1.6) * 0.65
				local bob = math.abs(math.cos(self.phase * 1.6)) * 0.12
				self:pose(CFrame.lookAt(p + Vector3.new(0, 3 + bob, 0), p + Vector3.new(0, 3, 0) + look), swing, false)
				if a >= 1 then
					break
				end
				task.wait()
			end
		end
		pos = goal
	end
end

-- S'assoit sur une place (CFrame de la surface d'assise, regard = direction de la table)
function Npc:sit(seat: CFrame)
	self:pose(seat * CFrame.new(0, 1.05, 0.25), 0, true)
end

function Npc:standAt(pos: Vector3, look: Vector3)
	self:pose(CFrame.lookAt(pos + Vector3.new(0, 3, 0), pos + Vector3.new(0, 3, 0) + look), 0, false)
end

function Npc:destroy()
	self.model:Destroy()
end

return Npc

-- Ambiance locale : ventilateurs qui tournent, jets de la fontaine.

local RunService = game:GetService("RunService")

local map = workspace:WaitForChild("Map")

-- attend que la map soit répliquée
task.wait(2)

local fans: { { model: Model, base: CFrame } } = {}
for _, m in map:GetDescendants() do
	if m:IsA("Model") and m:GetAttribute("Spin") then
		table.insert(fans, { model = m, base = m:GetPivot() })
	elseif m:IsA("BasePart") and m:GetAttribute("FountainJet") then
		-- les cylindres ont leur axe sur X local : on émet vers le haut du monde
		local upIsX = m.CFrame.RightVector.Y > 0.9
		local att = Instance.new("Attachment")
		att.Position = if upIsX then Vector3.new(m.Size.X / 2, 0, 0) else Vector3.new(0, m.Size.Y / 2, 0)
		att.Parent = m
		local pe = Instance.new("ParticleEmitter")
		pe.Color = ColorSequence.new(Color3.fromRGB(200, 232, 255))
		pe.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.3), NumberSequenceKeypoint.new(1, 1) })
		pe.Size = NumberSequence.new(0.35, 0.15)
		pe.Lifetime = NumberRange.new(0.9, 1.2)
		pe.Speed = NumberRange.new(9, 11)
		pe.SpreadAngle = Vector2.new(8, 8)
		pe.Acceleration = Vector3.new(0, -26, 0)
		pe.Rate = 70
		pe.LightEmission = 0.3
		pe.EmissionDirection = if upIsX then Enum.NormalId.Right else Enum.NormalId.Top
		pe.Parent = att
	end
end

local angle = 0
RunService.RenderStepped:Connect(function(dt)
	angle += dt * 4
	for _, f in fans do
		f.model:PivotTo(f.base * CFrame.Angles(0, angle, 0))
	end
end)

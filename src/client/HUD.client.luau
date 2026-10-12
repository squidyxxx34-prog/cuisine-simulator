-- Interface : pièces, objet en main, notifications, livre de recettes.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local Recipes = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Recipes"))

local player = Players.LocalPlayer
local GREEN = Color3.fromRGB(31, 74, 59)
local CREAM = Color3.fromRGB(255, 249, 236)
local GOLD = Color3.fromRGB(214, 166, 72)

local gui = Instance.new("ScreenGui")
gui.Name = "BistroHUD"
gui.ResetOnSpawn = false
gui.IgnoreGuiInset = false
gui.Parent = player:WaitForChild("PlayerGui")

local function corner(parent: Instance, r: number?)
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(0, r or 12)
	c.Parent = parent
end

local function stroke(parent: Instance, color: Color3?, thick: number?)
	local s = Instance.new("UIStroke")
	s.Color = color or GOLD
	s.Thickness = thick or 2
	s.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	s.Parent = parent
end

local function label(parent: Instance, text: string, size: UDim2, pos: UDim2, color: Color3?): TextLabel
	local l = Instance.new("TextLabel")
	l.BackgroundTransparency = 1
	l.Size = size
	l.Position = pos
	l.Font = Enum.Font.FredokaOne
	l.TextScaled = true
	l.TextColor3 = color or CREAM
	l.Text = text
	l.Parent = parent
	return l
end

-- ---------- pièces
local coinsBox = Instance.new("Frame")
coinsBox.Size = UDim2.fromOffset(190, 52)
coinsBox.Position = UDim2.fromOffset(16, 16)
coinsBox.BackgroundColor3 = GREEN
coinsBox.Parent = gui
corner(coinsBox)
stroke(coinsBox)
local coinsText = label(coinsBox, "🪙 0", UDim2.new(1, -20, 0.62, 0), UDim2.fromOffset(10, 4), GOLD)
coinsText.TextXAlignment = Enum.TextXAlignment.Left
local servedText = label(coinsBox, "0 plats servis", UDim2.new(1, -20, 0.3, 0), UDim2.new(0, 10, 0.64, 0))
servedText.TextXAlignment = Enum.TextXAlignment.Left

local function bindStats()
	local stats = player:WaitForChild("leaderstats")
	local coins = stats:WaitForChild("Pièces") :: IntValue
	local served = stats:WaitForChild("Servis") :: IntValue
	local function update()
		coinsText.Text = "🪙 " .. coins.Value
		servedText.Text = served.Value .. " plats servis"
	end
	coins.Changed:Connect(function()
		update()
		coinsBox.Size = UDim2.fromOffset(204, 56)
		TweenService:Create(coinsBox, TweenInfo.new(0.25, Enum.EasingStyle.Back), { Size = UDim2.fromOffset(190, 52) }):Play()
	end)
	served.Changed:Connect(update)
	update()
end
task.spawn(bindStats)

-- ---------- en main
local holdBox = Instance.new("Frame")
holdBox.AnchorPoint = Vector2.new(0.5, 1)
holdBox.Size = UDim2.fromOffset(320, 44)
holdBox.Position = UDim2.new(0.5, 0, 1, -90)
holdBox.BackgroundColor3 = Color3.fromRGB(20, 22, 26)
holdBox.BackgroundTransparency = 0.25
holdBox.Visible = false
holdBox.Parent = gui
corner(holdBox, 10)
local holdText = label(holdBox, "", UDim2.new(1, -20, 1, -8), UDim2.fromOffset(10, 4))

local function updateHold()
	local h = player:GetAttribute("Holding")
	holdBox.Visible = type(h) == "string" and h ~= ""
	holdText.Text = "En main : " .. tostring(h)
end
player:GetAttributeChangedSignal("Holding"):Connect(updateHold)
updateHold()

-- ---------- notifications
local toastArea = Instance.new("Frame")
toastArea.BackgroundTransparency = 1
toastArea.AnchorPoint = Vector2.new(0.5, 0)
toastArea.Size = UDim2.fromOffset(460, 200)
toastArea.Position = UDim2.new(0.5, 0, 0, 16)
toastArea.Parent = gui
local list = Instance.new("UIListLayout")
list.Padding = UDim.new(0, 6)
list.HorizontalAlignment = Enum.HorizontalAlignment.Center
list.SortOrder = Enum.SortOrder.LayoutOrder
list.Parent = toastArea

local KIND_COLORS = {
	info = Color3.fromRGB(40, 44, 52),
	warn = Color3.fromRGB(176, 110, 20),
	good = Color3.fromRGB(46, 125, 50),
	bad = Color3.fromRGB(170, 40, 40),
}
local order = 0

local function toast(text: string, kind: string)
	order += 1
	local f = Instance.new("Frame")
	f.Size = UDim2.fromOffset(440, 40)
	f.BackgroundColor3 = KIND_COLORS[kind] or KIND_COLORS.info
	f.LayoutOrder = order
	f.Parent = toastArea
	corner(f, 10)
	local l = label(f, text, UDim2.new(1, -20, 1, -10), UDim2.fromOffset(10, 5))
	task.delay(3.2, function()
		TweenService:Create(f, TweenInfo.new(0.4), { BackgroundTransparency = 1 }):Play()
		TweenService:Create(l, TweenInfo.new(0.4), { TextTransparency = 1 }):Play()
		task.wait(0.45)
		f:Destroy()
	end)
	local kids = 0
	for _, c in toastArea:GetChildren() do
		if c:IsA("Frame") then
			kids += 1
		end
	end
	if kids > 4 then
		for _, c in toastArea:GetChildren() do
			if c:IsA("Frame") and c ~= f then
				c:Destroy()
				break
			end
		end
	end
end

local remotes = ReplicatedStorage:WaitForChild("Remotes")
remotes:WaitForChild("Notify").OnClientEvent:Connect(toast)

-- ---------- livre de recettes
local bookBtn = Instance.new("TextButton")
bookBtn.AnchorPoint = Vector2.new(1, 0)
bookBtn.Size = UDim2.fromOffset(150, 46)
bookBtn.Position = UDim2.new(1, -16, 0, 16)
bookBtn.BackgroundColor3 = GREEN
bookBtn.Font = Enum.Font.FredokaOne
bookBtn.TextScaled = true
bookBtn.TextColor3 = GOLD
bookBtn.Text = "📖 Recettes"
bookBtn.Parent = gui
corner(bookBtn)
stroke(bookBtn)

local book = Instance.new("Frame")
book.AnchorPoint = Vector2.new(1, 0)
book.Size = UDim2.fromOffset(380, 420)
book.Position = UDim2.new(1, -16, 0, 72)
book.BackgroundColor3 = CREAM
book.Visible = false
book.Parent = gui
corner(book, 14)
stroke(book, GREEN, 3)
local title = label(book, "Le Petit Bistro — Recettes", UDim2.new(1, -20, 0, 34), UDim2.fromOffset(10, 8), GREEN)
title.Font = Enum.Font.Fondamento
local scroll = Instance.new("ScrollingFrame")
scroll.BackgroundTransparency = 1
scroll.Size = UDim2.new(1, -20, 1, -54)
scroll.Position = UDim2.fromOffset(10, 46)
scroll.ScrollBarThickness = 6
scroll.AutomaticCanvasSize = Enum.AutomaticSize.Y
scroll.CanvasSize = UDim2.new()
scroll.Parent = book
local sl = Instance.new("UIListLayout")
sl.Padding = UDim.new(0, 8)
sl.Parent = scroll

for _, dish in Recipes.Dishes do
	local card = Instance.new("Frame")
	card.Size = UDim2.new(1, -8, 0, 30 + #dish.items * 22)
	card.BackgroundColor3 = Color3.fromRGB(244, 236, 218)
	card.Parent = scroll
	corner(card, 10)
	local head = label(card, ("%s %s — %d 🪙"):format(dish.emoji, dish.label, dish.price), UDim2.new(1, -16, 0, 24), UDim2.fromOffset(8, 4), GREEN)
	head.TextXAlignment = Enum.TextXAlignment.Left
	for i, id in dish.items do
		local l = label(card, "• " .. Recipes.label(id) .. "  (" .. Recipes.howTo(id) .. ")", UDim2.new(1, -24, 0, 18), UDim2.fromOffset(16, 6 + i * 22), Color3.fromRGB(70, 60, 50))
		l.Font = Enum.Font.Gotham
		l.TextXAlignment = Enum.TextXAlignment.Left
	end
end

local help = label(scroll, "Prends une assiette sur la passe, garnis-la, puis apporte-la au client. Plus tu es rapide, plus le pourboire est gros !", UDim2.new(1, -8, 0, 64), UDim2.new(), Color3.fromRGB(90, 80, 70))
help.Font = Enum.Font.Gotham
help.TextWrapped = true

bookBtn.MouseButton1Click:Connect(function()
	book.Visible = not book.Visible
end)

task.delay(2, function()
	toast("Bienvenue au Petit Bistro ! Ouvre 📖 Recettes pour commencer.", "good")
end)

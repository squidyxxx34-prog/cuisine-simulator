-- Pièces, plats servis, sauvegarde DataStore.

local DataStoreService = game:GetService("DataStoreService")
local Players = game:GetService("Players")

local Economy = {}

local store: DataStore? = nil
do
	local ok, result = pcall(function()
		return DataStoreService:GetDataStore("CuisineSim_v1")
	end)
	if ok then
		store = result
	else
		warn("[Economy] DataStore indisponible (active l'accès API en Studio) :", result)
	end
end

local function key(player: Player): string
	return "p_" .. player.UserId
end

function Economy.setup(player: Player)
	local stats = Instance.new("Folder")
	stats.Name = "leaderstats"
	local coins = Instance.new("IntValue")
	coins.Name = "Pièces"
	coins.Parent = stats
	local served = Instance.new("IntValue")
	served.Name = "Servis"
	served.Parent = stats
	stats.Parent = player

	if store then
		local ok, data = pcall(function()
			return (store :: DataStore):GetAsync(key(player))
		end)
		if ok and type(data) == "table" then
			coins.Value = tonumber(data.coins) or 0
			served.Value = tonumber(data.served) or 0
		end
	end
end

function Economy.save(player: Player)
	if not store then
		return
	end
	local stats = player:FindFirstChild("leaderstats")
	if not stats then
		return
	end
	local data = {
		coins = (stats :: any)["Pièces"].Value,
		served = (stats :: any).Servis.Value,
	}
	local ok, err = pcall(function()
		(store :: DataStore):SetAsync(key(player), data)
	end)
	if not ok then
		warn("[Economy] Sauvegarde échouée :", err)
	end
end

function Economy.reward(player: Player, coins: number)
	local stats = player:FindFirstChild("leaderstats")
	if stats then
		(stats :: any)["Pièces"].Value += coins;
		(stats :: any).Servis.Value += 1
	end
end

function Economy.start()
	Players.PlayerAdded:Connect(Economy.setup)
	for _, p in Players:GetPlayers() do
		task.spawn(Economy.setup, p)
	end
	Players.PlayerRemoving:Connect(Economy.save)
	game:BindToClose(function()
		for _, p in Players:GetPlayers() do
			Economy.save(p)
		end
	end)
	task.spawn(function()
		while true do
			task.wait(120)
			for _, p in Players:GetPlayers() do
				task.spawn(Economy.save, p)
			end
		end
	end)
end

return Economy

-- Point d'entrée serveur du Cuisine Simulator.

local Economy = require(script.Parent.Economy)
local Kitchen = require(script.Parent.Kitchen)
local Customers = require(script.Parent.Customers)

local map = workspace:WaitForChild("Map")

Economy.start()
Kitchen.start(map)
Customers.start(map)

print("[Le Petit Bistro] Service ouvert !")

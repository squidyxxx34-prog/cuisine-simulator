--!strict
-- Ingrédients, préparations et plats du Petit Bistro.

local Recipes = {}

export type Item = {
	label: string,
	color: Color3,
	shape: string, -- forme utilisée par ItemVisuals
	raw: boolean,
	prep: string?, -- "Board" (planche) ou "Stove" (piano)
	result: string?, -- nom de l'item une fois préparé
	cookTime: number?,
	burnTime: number?,
}

-- Tous les objets qu'un joueur peut tenir (bruts et préparés)
Recipes.Items = {
	Tomate = { label = "Tomate", color = Color3.fromRGB(211, 47, 47), shape = "ball", raw = true, prep = "Board", result = "TomateCoupee" },
	Salade = { label = "Salade", color = Color3.fromRGB(139, 195, 74), shape = "lettuce", raw = true, prep = "Board", result = "SaladeCoupee" },
	Pain = { label = "Pain", color = Color3.fromRGB(211, 155, 82), shape = "baguette", raw = true, prep = "Board", result = "PainTranche" },
	Fromage = { label = "Fromage", color = Color3.fromRGB(246, 201, 69), shape = "wedge", raw = true, prep = "Board", result = "FromageRape" },
	Steak = { label = "Steak cru", color = Color3.fromRGB(196, 72, 78), shape = "patty", raw = true, prep = "Stove", result = "SteakCuit", cookTime = 6, burnTime = 16 },
	Pates = { label = "Pâtes crues", color = Color3.fromRGB(242, 193, 78), shape = "pack", raw = true, prep = "Stove", result = "PatesCuites", cookTime = 8, burnTime = 20 },

	TomateCoupee = { label = "Tomate coupée", color = Color3.fromRGB(211, 47, 47), shape = "slices", raw = false },
	SaladeCoupee = { label = "Salade coupée", color = Color3.fromRGB(139, 195, 74), shape = "leaves", raw = false },
	PainTranche = { label = "Pain tranché", color = Color3.fromRGB(214, 160, 88), shape = "bun", raw = false },
	FromageRape = { label = "Fromage râpé", color = Color3.fromRGB(250, 214, 92), shape = "heap", raw = false },
	SteakCuit = { label = "Steak cuit", color = Color3.fromRGB(110, 62, 38), shape = "patty", raw = false },
	PatesCuites = { label = "Pâtes cuites", color = Color3.fromRGB(240, 214, 140), shape = "heap", raw = false },
	SteakBrule = { label = "Steak brûlé", color = Color3.fromRGB(30, 26, 24), shape = "patty", raw = false },
	PatesBrulees = { label = "Pâtes brûlées", color = Color3.fromRGB(70, 55, 35), shape = "heap", raw = false },
} :: { [string]: Item }

Recipes.Burnt = { Steak = "SteakBrule", Pates = "PatesBrulees" }

export type Dish = { id: string, label: string, emoji: string, price: number, items: { string }, weight: number }

Recipes.Dishes = {
	{ id = "Salade", label = "Salade", emoji = "🥗", price = 15, items = { "SaladeCoupee", "TomateCoupee" }, weight = 5 },
	{ id = "Croque", label = "Croque", emoji = "🥪", price = 25, items = { "PainTranche", "FromageRape" }, weight = 4 },
	{ id = "Burger", label = "Burger", emoji = "🍔", price = 30, items = { "PainTranche", "SteakCuit", "SaladeCoupee" }, weight = 4 },
	{ id = "Pates", label = "Pâtes", emoji = "🍝", price = 35, items = { "PatesCuites", "TomateCoupee", "FromageRape" }, weight = 3 },
	{ id = "Cheeseburger", label = "Cheeseburger", emoji = "🧀", price = 45, items = { "PainTranche", "SteakCuit", "FromageRape", "TomateCoupee" }, weight = 2 },
} :: { Dish }

-- Items autorisés sur une assiette (ceux qui apparaissent dans au moins un plat)
local plateable: { [string]: boolean } = {}
for _, dish in Recipes.Dishes do
	for _, it in dish.items do
		plateable[it] = true
	end
end

function Recipes.label(id: string): string
	local it = Recipes.Items[id]
	return if it then it.label else id
end

function Recipes.isPlateable(id: string): boolean
	return plateable[id] == true
end

local function sorted(list: { string }): { string }
	local c = table.clone(list)
	table.sort(c)
	return c
end

-- Renvoie le plat correspondant exactement au contenu de l'assiette
function Recipes.matchDish(contents: { string }): Dish?
	local key = table.concat(sorted(contents), "+")
	for _, dish in Recipes.Dishes do
		if table.concat(sorted(dish.items), "+") == key then
			return dish
		end
	end
	return nil
end

function Recipes.dishById(id: string): Dish?
	for _, dish in Recipes.Dishes do
		if dish.id == id then
			return dish
		end
	end
	return nil
end

function Recipes.randomDish(rng: Random): Dish
	local total = 0
	for _, d in Recipes.Dishes do
		total += d.weight
	end
	local r = rng:NextNumber() * total
	for _, d in Recipes.Dishes do
		r -= d.weight
		if r <= 0 then
			return d
		end
	end
	return Recipes.Dishes[1]
end

-- Texte d'aide pour une préparation
function Recipes.howTo(id: string): string
	local steps = {}
	for raw, it in Recipes.Items do
		if it.result == id then
			table.insert(steps, it.label .. (if it.prep == "Board" then " → planche" else " → piano"))
		end
	end
	return table.concat(steps, ", ")
end

return Recipes

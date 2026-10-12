# 🍳 Cuisine Simulator — Le Petit Bistro

Jeu Roblox de simulation de cuisine : tu fais tourner un bistrot parisien, tu prépares les plats et tu sers les clients avant qu'ils perdent patience.

## Ouvrir le jeu dans Studio

1. Onglet **Releases** → `latest` → télécharge `CuisineSimulator.rbxlx` (reconstruit à chaque push sur `main`).
2. Double-clic → s'ouvre dans Roblox Studio, entièrement modifiable.
3. **Play** pour tester. Pour la sauvegarde des pièces : *Game Settings → Security → Enable Studio Access to API Services*.

## La map

Tout est généré par `tools/build_map.py` (~5 100 pièces) :

| Zone | Contenu |
|---|---|
| **Façade** | Brique, pilastres, corniche, 5 stores rayés, enseigne dorée, lanternes, jardinières, enseigne drapeau, chevalet menu |
| **Salle** | Parquet, lambris + cimaise, poutres, 6 tables nappées (24 couverts), bar avec tireuse et 5 tabourets, miroir et bouteilles, 3 banquettes cuir, cave à vin, tableaux, ardoise menu, ventilateurs, suspensions |
| **Cuisine** | Carrelage damier, faïence, 4 pianos sous hotte, friteuse, îlot avec 4 planches + batterie de casseroles suspendue, passe avec lampes chauffantes, 2 frigos, cagettes, plonge double, lave-vaisselle, étagères garnies |
| **Rue** | Route, passage piéton, trottoirs, terrasse (4 tables + parasols), lampadaires, arbres, voitures, abribus, boîte aux lettres, vélos |
| **Parc** | Fontaine à 3 vasques, étang avec canards et ponton, kiosque à musique, marchand de glaces, massifs fleuris, haies, bancs |
| **Quartier** | 4 immeubles (boulangerie, fleuriste, librairie, fromagerie), ruelle de livraison, skyline |

Éclairage : moteur *Future*, fin d'après-midi, bloom + atmosphère.

## Gameplay

1. Prends un ingrédient (cagettes, frigos **Viande** / **Crèmerie**, pâtes au fond).
2. **Planche** pour couper (tomate, salade, pain, fromage), **piano** pour cuire (steak, pâtes — attention ça brûle !).
3. Sur la **passe**, prends une assiette et garnis-la.
4. Apporte-la au client : prix du plat + pourboire selon la rapidité.

| Plat | Ingrédients | Prix |
|---|---|---|
| 🥗 Salade | salade coupée, tomate coupée | 15 |
| 🥪 Croque | pain tranché, fromage râpé | 25 |
| 🍔 Burger | pain tranché, steak cuit, salade coupée | 30 |
| 🍝 Pâtes | pâtes cuites, tomate coupée, fromage râpé | 35 |
| 🧀 Cheeseburger | pain tranché, steak cuit, fromage râpé, tomate coupée | 45 |

## Structure

```
tools/build_map.py   générateur de la map → map/*.model.json
tools/props.py       mobilier & accessoires
tools/preview.py     rendu d'aperçu PNG (vérif sans Studio)
src/server/          Kitchen, Customers, Npc, Economy
src/client/          HUD, ambiance (ventilos, fontaine)
src/shared/          Recipes, ItemVisuals
```

## Dev local (Rojo)

```bash
python tools/build_map.py      # régénère map/
rojo serve                     # + plugin Rojo dans Studio
rojo build -o CuisineSimulator.rbxlx
```

## Publication automatique (optionnel)

Dans *Settings → Secrets and variables → Actions* :
- secret `ROBLOX_API_KEY` (Creator Dashboard → Credentials, permission *universe-places:write*)
- variables `ROBLOX_UNIVERSE_ID`, `ROBLOX_PLACE_ID`
- variable `AUTO_PUBLISH=true` pour publier à chaque push, sinon lance le workflow à la main avec « Publier ».

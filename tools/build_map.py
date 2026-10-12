"""Génère toute la map du jeu dans ../map/*.model.json

    python tools/build_map.py

Plan (studs, Y vers le haut, la rue est côté -Z) :
  - Restaurant « Le Petit Bistro » : x -40..40, z -39..21
      salle   z -38..-6   (bar à gauche, 6 tables, 3 banquettes à droite)
      cuisine z -5..20    (4 pianos, îlot de découpe, passe, frigos, cagettes, plonge)
  - Trottoir + terrasse z -58..-39, route z -78..-58, parc au sud avec fontaine
  - Immeubles voisins, ruelle de livraison derrière, skyline en fond
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from lib import Builder, hx, shade, point_light, spot_light, text_gui, R  # noqa: E402
from props import *  # noqa: E402,F401,F403

OUT = os.path.join(os.path.dirname(__file__), "..", "map")
Y0 = 1.0          # niveau du sol intérieur
CEIL = 16.0       # plafond intérieur
WALL_TOP = 17.0
PARAPET = 19.0
SIDEWALK = 0.6

TABLE_X = [-14, 3, 20]
TABLE_Z = [-28, -16]
AISLES = [-23.5, -5.5, 11.5, 28.5]
FRONT_AISLE_Z = -34.5
STOOL_Z = [-30, -26.5, -23, -19.5, -16]
BOOTH_Z = [-32, -22, -12]

FRONT_WINDOWS = [(-34, -22), (-19, -8), (8, 19), (22, 34)]
RIGHT_WINDOWS = [(-35, -29), (-25, -19), (-15, -9)]


# ---------------------------------------------------------------- murs
def wall(b, name, axis, a0, a1, c, thick, y0, y1, openings, color, mat, **kw):
    """Mur plein le long de `axis` ('x' ou 'z') avec ouvertures (a0, a1, y0, y1)."""
    pts = sorted({a0, a1} | {min(max(o[0], a0), a1) for o in openings} | {min(max(o[1], a0), a1) for o in openings})
    segs = []
    for p, q in zip(pts, pts[1:]):
        if q - p < 1e-6:
            continue
        gaps = sorted((o[2], o[3]) for o in openings if o[0] <= p + 1e-6 and o[1] >= q - 1e-6)
        solids, cur = [], y0
        for g0, g1 in gaps:
            if g0 > cur + 1e-6:
                solids.append((cur, min(g0, y1)))
            cur = max(cur, g1)
        if cur < y1 - 1e-6:
            solids.append((cur, y1))
        if segs and segs[-1][2] == solids and abs(segs[-1][1] - p) < 1e-6:
            segs[-1] = (segs[-1][0], q, solids)
        else:
            segs.append((p, q, solids))
    for p, q, solids in segs:
        for s0, s1 in solids:
            if s1 - s0 < 1e-3:
                continue
            mid, ym = (p + q) / 2, (s0 + s1) / 2
            if axis == "x":
                b.part(name, (q - p, s1 - s0, thick), (mid, ym, c), color, mat, **kw)
            else:
                b.part(name, (thick, s1 - s0, q - p), (c, ym, mid), color, mat, **kw)


def window(b, name, center, w, h, ry, cols=2, rows=2, frame=None, sill=True, transom=True, glass=None):
    """Fenêtre à petits bois, face extérieure vers -Z local."""
    frame = frame or P["green"]
    glass = glass or P["glass"]
    t = 0.35
    with b.group(name, pos=center, ry=ry):
        b.part("Glass", (w, h, 0.12), (0, 0, 0), glass, "Glass", transp=0.55, refl=0.15)
        for sy in (-1, 1):
            b.part("Frame", (w, t, 0.7), (0, sy * (h / 2 - t / 2), 0), frame, "Wood", collide=False)
        for sx in (-1, 1):
            b.part("Frame", (t, h, 0.7), (sx * (w / 2 - t / 2), 0, 0), frame, "Wood", collide=False)
        top = h / 2
        if transom:
            ty = h / 2 - h * 0.22
            b.part("Transom", (w, 0.25, 0.6), (0, ty, 0), frame, "Wood", collide=False)
            top = ty
        for i in range(1, cols):
            x = -w / 2 + w * i / cols
            b.part("Mullion", (0.18, top + h / 2, 0.5), (x, (top - h / 2) / 2, 0), frame, "Wood", collide=False)
        for j in range(1, rows):
            y = -h / 2 + (top + h / 2) * j / rows
            b.part("Muntin", (w, 0.15, 0.45), (0, y, 0), frame, "Wood", collide=False)
        if sill:
            b.part("Sill", (w + 0.8, 0.3, 1.0), (0, -h / 2 - 0.15, -0.35), P["trim"], "Concrete", collide=False)


def awning(b, name, x0, x1, ytop=12.9, depth=3.8, drop=1.9, zwall=-39.0):
    n = max(2, round((x1 - x0) / 1.0))
    w = (x1 - x0) / n
    ang = math.degrees(math.atan2(drop, depth))
    length = math.hypot(drop, depth)
    with b.group(name):
        for i in range(n):
            xc = x0 + w * (i + 0.5)
            col = P["red"] if i % 2 == 0 else P["cream"]
            b.part("Stripe", (w + 0.01, 0.15, length), (xc, ytop - drop / 2, zwall - depth / 2), col, "Fabric",
                   rx=-ang, collide=False)
            b.part("Valance", (w + 0.01, 0.45, 0.1), (xc, ytop - drop - 0.2, zwall - depth - 0.05), col, "Fabric",
                   collide=False, shadow=False)
            b.cylz("Scallop", w * 0.9, 0.1, (xc, ytop - drop - 0.42, zwall - depth - 0.05), col, "Fabric",
                   collide=False, shadow=False)
        for xe in (x0, x1):
            b.wedge("Side", (0.12, drop, depth), (xe, ytop - drop / 2, zwall - depth / 2), P["red"], "Fabric",
                    collide=False)
            b.cylz("Bracket", 0.12, depth, (xe, ytop - drop - 0.1, zwall - depth / 2), P["black"], "Metal",
                   collide=False, shadow=False)


# ------------------------------------------------------------ restaurant
def build_restaurant():
    b = Builder()
    # fondations & toiture
    b.part("Foundation", (80, 0.8, 60), (0, 0.4, -9), P["concrete"], "Concrete")
    b.part("RoofSlab", (80, 1.0, 60), (0, 16.5, -9), P["concrete"], "Concrete")
    b.part("RoofGravel", (78.4, 0.1, 58.4), (0, 17.05, -9), hx("#5d5e61"), "Slate")

    # --- murs extérieurs (peau brique) et intérieurs (peau enduit)
    front_open = [(-4, 4, Y0, 10.5)] + [(a, c, 3.5, 11.5) for a, c in FRONT_WINDOWS]
    right_open = [(a, c, 6, 13) for a, c in RIGHT_WINDOWS] + [(1, 7, 7, 11)]
    back_open = [(30, 34, Y0, 10)]
    part_open = [(-9, 9, 4.4, 8.5), (22, 26, Y0, 10)]
    with b.folder("Walls"):
        wall(b, "FrontBrick", "x", -40, 40, -38.75, 0.5, 0, WALL_TOP, front_open, P["brick"], "Brick")
        wall(b, "LeftBrick", "z", -39, 21, -39.75, 0.5, 0, WALL_TOP, [], P["brick"], "Brick")
        wall(b, "RightBrick", "z", -39, 21, 39.75, 0.5, 0, WALL_TOP, right_open, P["brick"], "Brick")
        wall(b, "BackBrick", "x", -40, 40, 20.75, 0.5, 0, WALL_TOP, back_open, P["brick2"], "Brick")
        # peaux intérieures salle (vert bistro) / cuisine (blanc)
        wall(b, "DiningFront", "x", -38.5, 38.5, -38.25, 0.5, Y0, CEIL, front_open, P["green2"], "Plaster")
        wall(b, "DiningLeft", "z", -38.5, -6, -39.25, 0.5, Y0, CEIL, [], P["green2"], "Plaster")
        wall(b, "DiningRight", "z", -38.5, -6, 39.25, 0.5, Y0, CEIL, right_open, P["green2"], "Plaster")
        wall(b, "PartitionDining", "x", -39, 39, -5.75, 0.5, Y0, CEIL, part_open, P["green2"], "Plaster")
        wall(b, "PartitionKitchen", "x", -39, 39, -5.25, 0.5, Y0, CEIL, part_open, P["plaster"], "Plaster")
        wall(b, "KitchenLeft", "z", -5, 20.5, -39.25, 0.5, Y0, CEIL, [], P["plaster"], "Plaster")
        wall(b, "KitchenRight", "z", -5, 20.5, 39.25, 0.5, Y0, CEIL, right_open, P["plaster"], "Plaster")
        wall(b, "KitchenBack", "x", -39, 39, 20.25, 0.5, Y0, CEIL, back_open, P["plaster"], "Plaster")
        # parapets
        for z in (-38.75, 20.75):
            b.part("Parapet", (80, PARAPET - WALL_TOP, 0.8), (0, (WALL_TOP + PARAPET) / 2, z), P["brick"], "Brick")
        for x in (-39.75, 39.75):
            b.part("Parapet", (0.8, PARAPET - WALL_TOP, 60), (x, (WALL_TOP + PARAPET) / 2, -9), P["brick"], "Brick")
        b.part("ParapetCap", (81.4, 0.4, 1.4), (0, PARAPET + 0.2, -38.9), P["trim"], "Concrete")
        b.part("ParapetCap", (81.4, 0.4, 1.2), (0, PARAPET + 0.2, 20.8), P["trim"], "Concrete")
        for x in (-39.8, 39.8):
            b.part("ParapetCap", (1.2, 0.4, 60), (x, PARAPET + 0.2, -9), P["trim"], "Concrete")

    # --- façade
    with b.folder("Facade"):
        for x0, x1 in ((-40, -4), (4, 40)):
            b.part("Plinth", (x1 - x0, 2.0, 0.35), ((x0 + x1) / 2, 1.6, -39.15), P["stone"], "Slate")
        for x in (-39.4, -20.5, -6, 6, 20.5, 39.4):
            w = 1.2 if abs(x) > 39 else 1.4
            b.part("Pilaster", (w, 13.7, 0.5), (x, 9.45, -39.25), P["trim"], "Concrete")
            b.part("PilasterBase", (w + 0.3, 1.0, 0.7), (x, 2.6 + 0.5, -39.3), P["trim"], "Concrete")
            b.part("PilasterCap", (w + 0.4, 0.5, 0.8), (x, 16.05, -39.35), P["trim"], "Concrete")
        b.part("Cornice", (81.6, 1.0, 1.5), (0, 16.8, -39.5), P["trim"], "Concrete")
        b.part("Frieze", (80.4, 0.3, 0.7), (0, 15.9, -39.25), P["trim"], "Concrete")
        x = -39.2
        while x <= 39.2:
            b.part("Dentil", (0.5, 0.4, 0.5), (x, 16.15, -39.6), P["trim"], "Concrete", collide=False, shadow=False)
            x += 1.6
        # fenêtres de façade + jardinières
        for i, (x0, x1) in enumerate(FRONT_WINDOWS):
            window(b, f"FrontWindow{i + 1}", ((x0 + x1) / 2, 7.5, -38.5), x1 - x0, 8, 0, cols=3, rows=2)
            flower_box(b, "FlowerBox", ((x0 + x1) / 2, 2.7, -39.75), x1 - x0 - 0.5)
            awning(b, f"Awning{i + 1}", x0 - 0.4, x1 + 0.4)
        awning(b, "DoorAwning", -5, 5)
        # enseigne
        with b.group("Sign", pos=(0, 14.5, -39.35)):
            b.part("Board", (23, 2.5, 0.4), (0, 0, 0), P["green"], "Wood",
                   children=[text_gui("Le Petit Bistro", color=(0.86, 0.68, 0.32), font="Fondamento", stroke=0.7,
                                      ppu=40, light=0)])
            for sy in (-1, 1):
                b.part("Frame", (23.6, 0.3, 0.6), (0, sy * 1.4, -0.05), P["gold"], "Metal", collide=False)
            for sx in (-1, 1):
                b.part("Frame", (0.3, 2.5, 0.6), (sx * 11.65, 0, -0.05), P["gold"], "Metal", collide=False)
            for lx in (-8, 0, 8):
                b.cylz("LampArm", 0.15, 2.0, (lx, 1.75, -1.0), P["black"], "Metal", collide=False, shadow=False)
                b.cyl("LampShade", 0.9, 0.6, (lx, 1.6, -2.0), P["black"], "Metal", collide=False)
                b.ball("LampBulb", 0.45, (lx, 1.25, -2.0), [1, 0.85, 0.6], "Neon", collide=False, shadow=False,
                       children=[spot_light("Bottom", 10, 2.2, 90, (1, 0.85, 0.6))])
        # enseigne drapeau
        with b.group("BladeSign", pos=(37, 12.5, -39)):
            b.cylz("Arm", 0.2, 3.6, (0, 1.6, -1.8), P["black"], "Metal", collide=False)
            b.cylx("Disk", 3.2, 0.25, (0, 0, -2.6), P["green"], "Wood", collide=False,
                   children=[text_gui("BISTRO", face="Left", color=(0.86, 0.68, 0.32), font="Fondamento"),
                             text_gui("BISTRO", face="Right", color=(0.86, 0.68, 0.32), font="Fondamento")])
            b.cylx("DiskRim", 3.4, 0.15, (0, 0, -2.6), P["gold"], "Metal", collide=False)
        # lanternes murales
        for lx in (-6, 6):
            with b.group("WallLantern", pos=(lx, 8.2, -39.6)):
                b.part("Bracket", (0.2, 0.2, 0.9), (0, 1.1, -0.3), P["black"], "Metal", collide=False)
                b.part("Cap", (1.0, 0.25, 1.0), (0, 0.85, -0.7), P["black"], "Metal", collide=False)
                b.part("Glass", (0.75, 1.3, 0.75), (0, 0.1, -0.7), [1, 0.82, 0.55], "Neon", collide=False,
                       shadow=False, transp=0.15, children=[point_light(16, 1.2, WARM)])
                b.part("Base", (0.9, 0.2, 0.9), (0, -0.6, -0.7), P["black"], "Metal", collide=False)
        b.part("Plaque", (1.0, 0.8, 0.1), (6, 6.0, -39.55), hx("#1e3f8a"), collide=False,
               children=[text_gui("12", color=(1, 1, 1), stroke=1)])
        # porte d'entrée (battants ouverts)
        for sx in (-1, 1):
            b.part("DoorJamb", (0.5, 9.5, 0.9), (sx * 4.2, Y0 + 4.75, -38.5), P["green"], "Wood", collide=False)
        b.part("DoorHead", (8.9, 0.4, 0.9), (0, 9.6, -38.5), P["green"], "Wood", collide=False)
        b.part("Transom", (7.9, 0.8, 0.12), (0, 10.05, -38.5), P["glass"], "Glass", transp=0.5, collide=False,
               children=[text_gui("BIENVENUE", color=(0.86, 0.68, 0.32), font="Fondamento", stroke=1)])
        b.part("Step", (9.5, 0.3, 1.6), (0, 0.75, -39.8), P["stone"], "Slate")
        for hinge, sgn in ((-4, 1), (4, -1)):
            with b.group("DoorLeaf", pos=(hinge, Y0, -38.4), ry=-75 * sgn):
                cx = sgn * 1.95
                b.part("Glass", (3.3, 7.2, 0.1), (cx, 4.6, 0), P["glass"], "Glass", transp=0.5, collide=False)
                for sy in (0.25, 8.35):
                    b.part("Rail", (3.9, 0.5 if sy > 1 else 1.4, 0.3), (cx, sy + (0.45 if sy < 1 else 0), 0),
                           P["green"], "Wood", collide=False)
                for ex in (0.2, 3.7):
                    b.part("Stile", (0.3, 8.6, 0.3), (sgn * ex, 4.3, 0), P["green"], "Wood", collide=False)
                b.part("KickPlate", (3.4, 0.8, 0.05), (cx, 0.7, -0.18), P["gold"], "Metal", collide=False)
                b.part("Handle", (0.15, 2.4, 0.15), (sgn * 3.3, 4.2, -0.35), P["gold"], "Metal", collide=False)
                if sgn == 1:
                    b.part("OpenSign", (1.8, 0.7, 0.05), (cx, 6.2, -0.1), hx("#123d2a"), collide=False,
                           children=[text_gui("OUVERT", color=(0.4, 1, 0.55), stroke=1, light=0)])
        # chevalet menu
        with b.group("MenuEasel", pos=(-6.8, SIDEWALK, -43)):
            menu = "<b>MENU DU JOUR</b>\nSalade · 15\nBurger · 30\nCroque · 25\nCheeseburger · 45\nPâtes · 35"
            b.part("Front", (2.8, 4.4, 0.15), (0, 2.1, -0.45), hx("#26302b"), "Slate", rx=12,
                   children=[text_gui(menu, color=(0.97, 0.95, 0.9), font="PermanentMarker", stroke=1, ppu=50,
                                      rich=True)])
            b.part("Back", (2.8, 4.4, 0.15), (0, 2.1, 0.45), hx("#26302b"), "Slate", rx=-12)
            b.part("FrameTop", (2.9, 0.3, 0.6), (0, 4.2, 0), P["wood"], "Wood", collide=False)

    # --- côtés & arrière
    with b.folder("SidesAndBack"):
        for i, (z0, z1) in enumerate(RIGHT_WINDOWS):
            window(b, f"SideWindow{i + 1}", (39.6, 9.5, (z0 + z1) / 2), z1 - z0, 7, -90, cols=2, rows=2)
        window(b, "KitchenWindow", (39.6, 9, 4), 6, 4, -90, cols=2, rows=1, transom=False, frame=P["white"])
        for x in (-40.3, 40.3):
            b.cyl("Downpipe", 0.5, 17.5, (x, 8.75, -37.2), P["steel_dk"], "Metal", collide=False)
            b.cyl("Downpipe", 0.5, 17.5, (x, 8.75, 19.5), P["steel_dk"], "Metal", collide=False)
        # porte de service
        b.part("BackDoorHead", (5, 0.4, 1.2), (32, 10.2, 20.75), P["steel_dk"], "Metal", collide=False)
        for x in (29.8, 34.2):
            b.part("BackDoorJamb", (0.4, 9.2, 1.2), (x, 5.6, 20.75), P["steel_dk"], "Metal", collide=False)
        with b.group("BackDoor", pos=(30, Y0, 20.6), ry=70):
            b.part("Leaf", (4, 8.8, 0.3), (2, 4.4, 0), hx("#4a5560"), "Metal", collide=False)
            b.part("Bar", (3.2, 0.3, 0.3), (2, 4.0, -0.25), P["steel"], "Metal", collide=False)
        b.part("Canopy", (7, 0.35, 3.5), (32, 11.2, 22.7), P["steel_dk"], "Metal")
        b.part("DeliverySign", (5, 0.9, 0.1), (32, 12.4, 21.06), P["cream"], collide=False,
               children=[text_gui("LIVRAISONS", face="Back", color=(0.2, 0.2, 0.2), stroke=1)])
        b.part("BackLamp", (0.8, 0.5, 0.8), (32, 10.8, 22.3), [1, 0.9, 0.7], "Neon", collide=False, shadow=False,
               children=[point_light(18, 1.2, WARM)])
        b.part("BackStep", (6, 0.3, 2.4), (32, 0.75, 22.2), P["concrete"], "Concrete")
        b.part("VentGrille", (4, 2.5, 0.2), (-11.5, 13, 21.1), hx("#55595e"), "DiamondPlate", collide=False)

    # --- toit
    with b.folder("Roof"):
        for i, (x, z) in enumerate(((22, 6), (28, -20))):
            with b.group(f"ACUnit{i + 1}", pos=(x, 17.1, z)):
                b.part("Body", (6, 3, 5), (0, 1.5, 0), hx("#b9bcc0"), "Metal")
                b.cyl("Fan", 3.4, 0.2, (0, 3.05, 0), hx("#2c2f33"), "DiamondPlate", collide=False)
                for k in range(-2, 3):
                    b.part("Fin", (0.1, 2.2, 4.6), (k * 1.1, 1.5, 0), hx("#8f9399"), "Metal", collide=False,
                           shadow=False)
        with b.group("Exhaust", pos=(-11.5, 17.1, 18)):
            b.part("Duct", (3.4, 4.5, 3.4), (0, 2.25, 0), P["steel"], "Metal", refl=0.15)
            b.part("Cap", (4.4, 0.4, 4.4), (0, 5.4, 0), P["steel_dk"], "Metal")
            b.part("CapNeck", (3.6, 0.8, 3.6), (0, 4.9, 0), hx("#3a3d42"), "DiamondPlate", collide=False)
        b.cyl("Antenna", 0.2, 7, (-30, 20.6, 10), P["steel_dk"], "Metal", collide=False)
        for k in range(3):
            b.cylx("AntennaBar", 0.12, 3 - k * 0.7, (-30, 22.5 + k * 1.2, 10), P["steel_dk"], "Metal", collide=False)
        b.cylz("Dish", 2.6, 0.3, (-26, 18.8, 14), hx("#e6e6e6"), "SmoothPlastic", rx=-30, collide=False)
        b.cyl("DishPole", 0.3, 1.6, (-26, 17.9, 14), P["steel_dk"], "Metal", collide=False)
        b.part("RoofHatch", (4, 1, 4), (10, 17.6, -2), P["steel_dk"], "Metal")
    b.save(os.path.join(OUT, "Restaurant.model.json"))
    return b.count


# ---------------------------------------------------------------- salle
def build_dining():
    b = Builder()
    spots = []
    with b.group("Interior", pos=(0, Y0, 0)):
        b.part("Floor", (78, 0.2, 32), (0, -0.1, -22), hx("#8a5a36"), "WoodPlanks")
        b.part("Ceiling", (78, 0.4, 32.5), (0, CEIL - Y0 - 0.2, -22), P["cream"], "Plaster")
        for x in range(-32, 33, 8):
            b.part("Beam", (0.9, 0.7, 32), (x, CEIL - Y0 - 0.75, -22), P["wood_dk"], "Wood", collide=False)
        # lambris, cimaise, plinthes, corniche
        fo = [(-4, 4, 0, 9.5)] + [(a, c, 2.5, 10.5) for a, c in FRONT_WINDOWS]
        ro = [(a, c, 5, 12) for a, c in RIGHT_WINDOWS]
        po = [(-9, 9, 3.4, 7.5), (22, 26, 0, 9)]
        runs = [("x", -38, 38, -37.9, fo), ("z", -38, -6, -38.9, []), ("z", -38, -6, 38.9, ro),
                ("x", -38.8, 38.8, -6.1, po)]
        with b.folder("Wainscot"):
            for axis, a0, a1, c, op in runs:
                wall(b, "Panel", axis, a0, a1, c, 0.2, 0, 4.5, op, P["wood_dk"], "Wood", collide=False)
                wall(b, "ChairRail", axis, a0, a1, c, 0.4, 4.5, 4.85, op, P["wood"], "Wood", collide=False)
                wall(b, "Baseboard", axis, a0, a1, c, 0.35, 0, 0.6, op, hx("#2e1c10"), "Wood", collide=False)
                wall(b, "Crown", axis, a0, a1, c, 0.4, CEIL - Y0 - 0.6, CEIL - Y0, [], P["cream"], "Plaster",
                     collide=False)
            # moulures des panneaux (côté gauche et cloison, sans ouvertures)
            for z in [z for z in range(-36, -7, 4) if not (-33 <= z <= -13)]:
                b.part("Molding", (0.1, 2.6, 2.8), (-38.75, 2.3, z + 0.5), P["wood"], "Wood", collide=False,
                       shadow=False)
            for x in [x for x in range(-36, 37, 4) if not (-11 <= x <= 11) and not (20 <= x <= 28)]:
                b.part("Molding", (2.8, 2.6, 0.1), (x + 0.5, 2.3, -6.25), P["wood"], "Wood", collide=False,
                       shadow=False)

        # ---- tables + chaises
        with b.folder("Tables"):
            for ti, tz in enumerate(TABLE_Z):
                for tj, tx in enumerate(TABLE_X):
                    tid = ti * 3 + tj + 1
                    table_square(b, f"Table{tid}", (tx, 0, tz))
                    pendant(b, f"TableLamp{tid}", (tx, CEIL - Y0 - 0.4, tz), drop=6.2, shadows=(tid in (2, 5)))
                    for side, (dx, dz, ry) in {"N": (0, -3.3, 180), "S": (0, 3.3, 0), "E": (3.3, 0, 90),
                                               "W": (-3.3, 0, -90)}.items():
                        cx, cz = tx + dx, tz + dz
                        chair(b, f"Chair{tid}{side}", (cx, 0, cz), ry=ry)
                        if side == "E":
                            aisle = min(a for a in AISLES if a > cx)
                        elif side == "W":
                            aisle = max(a for a in AISLES if a < cx)
                        else:
                            aisle = min(AISLES, key=lambda a: abs(a - cx))
                        spots.append(((cx, Y0 + 1.93, cz), ry, aisle, f"T{tid}{side}"))
        # ---- bar
        with b.folder("Bar"):
            b.part("Counter", (4, 3.4, 20), (-33.5, 1.7, -23), P["wood_dk"], "Wood")
            b.part("CounterTop", (4.8, 0.25, 20.6), (-33.4, 3.52, -23), hx("#3b2416"), "Wood", refl=0.12)
            for k in range(8):
                b.part("Panel", (0.1, 2.2, 2.0), (-31.45, 1.8, -32 + k * 2.55 + 0.25), P["wood"], "Wood",
                       collide=False, shadow=False)
            b.cylz("FootRail", 0.3, 20, (-30.9, 0.7, -23), P["gold"], "Metal", refl=0.3, collide=False)
            for z in (-32, -23, -14):
                b.part("RailPost", (0.6, 0.15, 0.15), (-31.2, 0.7, z), P["gold"], "Metal", collide=False)
            # tireuse
            with b.group("BeerTap", pos=(-33.2, 3.65, -24)):
                b.part("Tower", (0.6, 1.8, 1.8), (0, 0.9, 0), P["steel"], "Metal", refl=0.25, collide=False)
                for k, col in enumerate((P["gold"], P["red"], P["green"])):
                    b.part("Handle", (0.25, 1.0, 0.25), (0.45, 1.8, -0.6 + k * 0.6), col, collide=False)
                b.part("DripTray", (1.2, 0.1, 2.0), (0.7, 0.05, 0), P["steel_dk"], "DiamondPlate", collide=False)
            with b.group("Register", pos=(-34.2, 3.65, -16)):
                b.part("Base", (1.6, 0.6, 1.4), (0, 0.3, 0), P["black"], collide=False)
                b.part("Screen", (0.15, 0.9, 1.2), (0.4, 1.0, 0), hx("#163b5c"), "Neon", rz=-15, collide=False,
                       shadow=False)
            for k in range(4):
                b.cyl("Glass", 0.45, 0.8, (-34.6, 4.05, -30 + k * 0.6), P["glass"], "Glass", transp=0.5,
                      collide=False, shadow=False)
            b.cyl("FruitBowl", 1.4, 0.4, (-34, 3.85, -20.5), P["white"], collide=False)
            for k in range(4):
                b.ball("Lemon", 0.45, (-34 + R.uniform(-.35, .35), 4.15, -20.5 + R.uniform(-.35, .35)),
                       hx("#f5d33f"), collide=False, shadow=False)
            # arrière-bar
            b.part("BackCabinet", (2, 3.2, 20), (-38, 1.6, -23), P["wood_dk"], "Wood")
            b.part("BackTop", (2.2, 0.2, 20.2), (-38, 3.3, -23), P["marble"], "Marble")
            b.part("Mirror", (0.1, 5.2, 19), (-38.9, 6.7, -23), hx("#3c4a50"), "Glass", refl=0.45, collide=False)
            for y in (4.6, 6.6, 8.6):
                b.part("Shelf", (1.4, 0.15, 19), (-38.2, y, -23), P["wood"], "Wood", collide=False)
                z = -32.2
                while z < -13.8:
                    bottle(b, (-38.2, y + 0.08, z), R.choice(BOTTLE_COLS))
                    z += R.uniform(0.55, 0.9)
            b.part("BarSign", (0.15, 1.6, 7), (-38.85, 10.6, -23), P["green"], "Wood", collide=False,
                   children=[text_gui("BAR", face="Right", color=(0.86, 0.68, 0.32), font="Fondamento")])
            for z in (-30, -23, -16):
                pendant(b, "BarLamp", (-33.5, CEIL - Y0 - 0.4, z), drop=5.4, shade_col=P["gold"])
            for i, z in enumerate(STOOL_Z):
                stool(b, f"Stool{i + 1}", (-29.8, 0, z))
                spots.append(((-29.8, Y0 + 2.78, z), 90, AISLES[0], f"B{i + 1}"))
        # ---- cave à vin
        with b.group("WineRack", pos=(-38.3, 0, -9.1)):
            b.part("Frame", (1.4, 8, 5.2), (0, 4, 0), P["wood_dk"], "Wood")
            for r in range(6):
                b.part("ShelfSlot", (1.5, 0.12, 5.0), (-0.05, 1.0 + r * 1.2, 0), P["wood"], "Wood", collide=False)
                for c in range(5):
                    b.cylx("Bottle", 0.42, 1.3, (0.2, 1.35 + r * 1.2, -2 + c * 1.0), R.choice(BOTTLE_COLS), "Glass",
                           collide=False, shadow=False)
        # ---- banquettes
        with b.folder("Booths"):
            for i, c in enumerate(BOOTH_Z):
                with b.group(f"Booth{i + 1}", pos=(35.5, 0, c)):
                    b.part("TableTop", (6, 0.3, 3.4), (0, 3.15, 0), P["wood_dk"], "Wood")
                    b.part("TableEdge", (6.1, 0.12, 3.5), (0, 2.95, 0), P["gold"], "Metal", collide=False)
                    b.cyl("Pedestal", 0.5, 3, (-0.5, 1.5, 0), P["black"], "Metal", collide=False)
                    b.part("Foot", (3, 0.15, 1.2), (-0.5, 0.08, 0), P["black"], "Metal")
                    centerpiece(b, (-0.8, 3.3, 0))
                    for s in (-1, 1):
                        b.part("Seat", (7, 0.5, 1.9), (0.2, 1.9, s * 2.9), P["leather"], "Leather")
                        b.part("SeatBase", (7, 1.65, 1.8), (0.2, 0.82, s * 2.9), P["wood_dk"], "Wood")
                        b.part("Back", (7, 3.0, 0.6), (0.2, 3.5, s * 4.05), P["leather"], "Leather")
                        b.part("BackCap", (7.1, 0.3, 0.8), (0.2, 5.1, s * 4.05), P["wood_dk"], "Wood", collide=False)
                        for k in range(5):
                            b.part("Tuft", (0.1, 2.4, 0.05), (-2.6 + k * 1.4, 3.5, s * 3.73), shade(P["leather"], 0.7),
                                   collide=False, shadow=False)
                    pendant(b, "BoothLamp", (0, CEIL - Y0 - 0.4, 0), drop=6.0, shade_col=P["gold"])
        # ---- déco
        with b.folder("Decor"):
            b.part("Rug", (6, 0.05, 6), (0, 0.03, -34.8), hx("#8e2430"), "Carpet", collide=False)
            b.part("RugBorder", (6.6, 0.04, 6.6), (0, 0.02, -34.8), P["gold"], "Fabric", collide=False)
            with b.group("HostStand", pos=(8.5, 0, -36.2)):
                b.part("Podium", (2.6, 3.8, 1.4), (0, 1.9, 0), P["wood_dk"], "Wood")
                b.part("Top", (3.0, 0.2, 1.8), (0, 3.9, 0), P["wood"], "Wood", rx=-10)
                b.part("Book", (1.2, 0.15, 0.9), (-0.3, 4.05, 0), P["red"], rx=-10, collide=False)
                b.cyl("LampPole", 0.12, 1.0, (0.9, 4.5, 0.3), P["gold"], "Metal", collide=False)
                b.ball("Lamp", 0.5, (0.9, 5.05, 0.3), [1, 0.85, 0.6], "Neon", collide=False, shadow=False,
                       children=[point_light(8, 0.8, WARM)])
            with b.group("CoatRack", pos=(-9, 0, -36.8)):
                b.cyl("Pole", 0.3, 7, (0, 3.5, 0), P["wood_dk"], "Wood")
                b.cyl("Base", 1.6, 0.3, (0, 0.15, 0), P["wood_dk"], "Wood")
                for k, col in enumerate((hx("#3d4f7a"), hx("#9a6b3f"), hx("#2b2b2b"))):
                    a = math.radians(k * 120)
                    b.part("Coat", (1.0, 2.6, 0.7), (0.55 * math.cos(a), 5.2, 0.55 * math.sin(a)), col, "Fabric",
                           ry=-k * 120, collide=False)
            plant(b, "PlantCorner", (-37, 0, -36.4), 1.0, tall=True)
            plant(b, "PlantHost", (13, 0, -36.6), 0.8)
            plant(b, "PlantBack", (-28, 0, -8), 1.0, tall=True)
            plant(b, "PlantBack2", (30.5, 0, -7.9), 0.9)
            painting(b, "Painting1", (-31, 8.6, -6.25), 5, 3.6)
            painting(b, "Painting2", (-20, 8.3, -6.25), 4.4, 3.2)
            painting(b, "Painting3", (15, 8.4, -6.25), 4.2, 3.2)
            chalkboard(b, "MenuBoard", (-13, 8.6, -6.3), 3.8, 5,
                       "<b>MENU</b>\nSalade 15\nBurger 30\nCroque 25\nPâtes 35\nCheese 45")
            b.part("KitchenSign", (4.2, 0.9, 0.1), (24, 9.7, -6.25), P["green"], "Wood", collide=False,
                   children=[text_gui("CUISINE", color=(0.86, 0.68, 0.32), font="Fondamento", stroke=1)])
            wall_clock(b, "Clock", (32, 10.5, -6.3))
            for x in (-5.5, 11.5):
                ceiling_fan(b, "CeilingFan", (x, CEIL - Y0 - 0.4, -22))
            # passe côté salle
            b.part("PickupLedge", (18.6, 0.25, 1.4), (0, 3.52, -6.75), P["steel"], "Metal", refl=0.2)
            for sx in (-1, 1):
                b.part("HatchTrim", (0.4, 4.6, 0.3), (sx * 9.2, 5.45, -6.15), P["wood_dk"], "Wood", collide=False)
            b.part("HatchTrim", (18.8, 0.4, 0.3), (0, 7.7, -6.15), P["wood_dk"], "Wood", collide=False)
            for z in (-35.5, -27.5, -19.5, -11.5):
                with b.group("Sconce", pos=(-38.85, 11.5, z)):
                    b.part("Plate", (0.1, 0.8, 0.5), (0, 0, 0), P["gold"], "Metal", collide=False)
                    b.ball("Bulb", 0.55, (0.4, 0.2, 0), [1, 0.85, 0.6], "Neon", collide=False, shadow=False,
                           children=[point_light(10, 0.6, WARM)])
    b.save(os.path.join(OUT, "Dining.model.json"))
    return b.count, spots


# -------------------------------------------------------------- cuisine
def build_kitchen():
    b = Builder()
    with b.group("Interior", pos=(0, Y0, 0)):
        b.part("Floor", (78, 0.2, 26), (0, -0.1, 7.5), P["tile_w"], "Concrete")
        nx, nz = 26, 8
        tw, td = 78 / nx, 25.5 / nz
        with b.folder("FloorTiles"):
            for i in range(nx):
                for j in range(nz):
                    if (i + j) % 2 == 0:
                        b.part("Tile", (tw, 0.04, td), (-39 + tw * (i + 0.5), 0.02, -5.25 + td * (j + 0.5)),
                               P["tile_dk"], "CeramicTiles", collide=False, shadow=False)
        b.part("Ceiling", (78, 0.4, 26), (0, CEIL - Y0 - 0.2, 7.5), P["white"], "Plaster")
        # faïence murale
        ro = [(1, 7, 6, 10)]
        with b.folder("WallTiles"):
            wall(b, "Tiles", "z", -5, 20, -38.95, 0.1, 0, 8, [], P["tile_w"], "CeramicTiles", collide=False)
            wall(b, "Tiles", "z", -5, 20, 38.95, 0.1, 0, 8, ro, P["tile_w"], "CeramicTiles", collide=False)
            wall(b, "Tiles", "x", -39, 39, 19.95, 0.1, 0, 8, [(30, 34, 0, 9)], P["tile_w"], "CeramicTiles",
                 collide=False)
            wall(b, "Tiles", "x", -39, 39, -4.95, 0.1, 0, 8, [(-9, 9, 3.4, 7.5), (22, 26, 0, 9)], P["tile_w"],
                 "CeramicTiles", collide=False)
            for axis, a0, a1, c, op in (("z", -5, 20, -38.9, []), ("z", -5, 20, 38.9, ro),
                                        ("x", -39, 39, 19.9, [(30, 34, 0, 9)]),
                                        ("x", -39, 39, -4.9, [(-9, 9, 3.4, 7.5), (22, 26, 0, 9)])):
                wall(b, "TileTrim", axis, a0, a1, c, 0.2, 8, 8.3, op, hx("#2b6f7e"), "CeramicTiles",
                     collide=False)
        with b.folder("Lights"):
            for x in (-26, -9, 8, 25):
                for z in (2, 13):
                    fluorescent(b, "Fluorescent", (x, CEIL - Y0 - 0.55, z))

        # ---- ligne de cuisson
        with b.folder("CookLine"):
            for i, x in enumerate((-22, -15, -8, -1)):
                stove(b, f"Stove{i + 1}", (x, 0, 18.2), idx=i + 1)
            range_hood(b, "Hood", (-11.5, 10.6, 17.6), 28)
            b.part("Mat", (28, 0.06, 2.6), (-11.5, 0.03, 15.0), hx("#151515"), "Rubber", collide=False)
            with b.group("Fryer", pos=(4.3, 0, 18.2)):
                b.part("Body", (3.2, 3.2, 3.5), (0, 1.6, 0), P["steel"], "Metal", refl=0.15)
                b.part("Oil", (2.6, 0.1, 2.4), (0, 3.15, 0.2), hx("#c78a19"), "Glass", transp=0.2, collide=False)
                for sx in (-0.65, 0.65):
                    b.part("Basket", (1.1, 0.8, 1.6), (sx, 3.4, -0.2), hx("#3d3d3d"), "DiamondPlate", collide=False)
                    b.part("BasketHandle", (0.15, 0.15, 1.6), (sx, 3.9, -1.5), P["black"], collide=False)
                b.part("Panel", (3.2, 0.5, 0.1), (0, 2.8, -1.8), P["black"], collide=False)
            cabinet(b, "PrepCounter", (16.75, 0, 18.25), 20.5)
            with b.group("Mixer", pos=(9.5, 3.42, 18.6)):
                b.part("Base", (1.4, 0.4, 2.0), (0, 0.2, 0), hx("#c0392b"), collide=False)
                b.part("Column", (1.0, 2.0, 0.9), (0, 1.2, 0.6), hx("#c0392b"), collide=False)
                b.part("Head", (1.0, 0.9, 2.2), (0, 2.4, 0.1), hx("#c0392b"), collide=False)
                b.cyl("Bowl", 1.3, 1.0, (0, 0.9, -0.3), P["steel"], "Metal", refl=0.3, collide=False)
            with b.group("Microwave", pos=(14, 3.42, 18.8)):
                b.part("Body", (3, 1.8, 2.0), (0, 0.9, 0), P["black"], "Metal", collide=False)
                b.part("Door", (2.0, 1.4, 0.05), (-0.4, 0.9, -1.02), hx("#1f2a33"), "Glass", collide=False)
                b.part("Panel", (0.6, 1.4, 0.05), (1.1, 0.9, -1.02), hx("#3f4448"), collide=False)
            for x in (18, 19.6):
                plate_stack(b, "Plates", (x, 3.42, 18.3), 8)
            for k in range(3):
                b.cyl("Bowl", 1.4 - k * 0.25, 0.5, (23, 3.67 + k * 0.4, 18.3), P["steel"], "Metal", refl=0.3,
                      collide=False)
            jar_shelf(b, "BackShelf", (16.5, 7.6, 19.3), 20, ry=180)
            jar_shelf(b, "BackShelf", (16.5, 9.8, 19.3), 20, ry=180)
            cabinet(b, "PastryCounter", (-30.75, 0, 18.25), 9.5)
            crate(b, "CratePates", (-31.5, 3.42, 18.4), "Pates", "Pâtes")
            for k in range(2):
                b.part("FlourSack", (1.6, 2.2, 1.2), (-27.8 + k * 0.4, 4.5, 18.3 + k * 0.2), hx("#efe7d4"), "Fabric",
                       rz=k * 6, collide=False, children=[text_gui("FARINE", color=(0.4, 0.3, 0.2), stroke=1)])
            jar_shelf(b, "LeftBackShelf", (-30.75, 7.6, 19.3), 9, ry=180)

        # ---- frigos & cagettes (côté gauche)
        with b.folder("Pantry"):
            fridge(b, "FridgeViande", (-37.3, 0, 16.4), -90, "VIANDE", "Steak")
            fridge(b, "FridgeCremerie", (-37.3, 0, 10.8), -90, "CRÈMERIE", "Fromage")
            with b.group("ProduceRack", pos=(-37.2, 0, 1.5)):
                b.part("Top", (3.6, 0.25, 12), (0, 2.3, 0), P["wood"], "Wood")
                b.part("LowShelf", (3.6, 0.2, 12), (0, 0.6, 0), P["wood"], "Wood", collide=False)
                for z in (-5.8, 0, 5.8):
                    for x in (-1.6, 1.6):
                        b.part("Leg", (0.3, 2.3, 0.3), (x, 1.15, z), P["black"], "Metal", collide=False)
                for z, ing in ((-3.8, "Oignon"), (0, "Tomate"), (3.8, "Salade")):
                    with b.group("SpareCrate", pos=(0, 0.7, z), ry=-90):
                        b.part("Crate", (3.2, 1.3, 2.4), (0, 0.65, 0), shade(P["wood_lt"], 0.9), "WoodPlanks",
                               collide=False)
                        fill_crate(b, ing)
            crate(b, "CrateTomate", (-37.2, 2.42, 5.3), "Tomate", "Tomates", ry=-90)
            crate(b, "CrateSalade", (-37.2, 2.42, 1.6), "Salade", "Salade", ry=-90)
            crate(b, "CratePain", (-37.2, 2.42, -2.1), "Pain", "Pain", ry=-90)
            jar_shelf(b, "PantryShelf", (-38.3, 8.2, 1.5), 12, ry=-90)

        # ---- plonge (côté droit)
        with b.folder("Dish"):
            sink_unit(b, "Sink", (37.3, 0, 4), 8, ry=90)
            with b.group("Dishwasher", pos=(37.3, 0, 9.5), ry=90):
                b.part("Body", (2.8, 3.25, 3.4), (0, 1.62, 0), P["steel"], "Metal", refl=0.15)
                b.part("Panel", (2.6, 0.4, 0.1), (0, 3.0, -1.75), P["black"], collide=False)
                b.part("Led", (0.3, 0.15, 0.05), (0.8, 3.0, -1.82), [0.3, 1, 0.4], "Neon", collide=False,
                       shadow=False)
                b.cylx("Handle", 0.15, 2.2, (0, 2.5, -1.85), P["steel_dk"], "Metal", collide=False)
            cabinet(b, "SideCounter", (37.3, 0, 13), 4, ry=90)
            plate_stack(b, "CleanPlates", (37.4, 3.42, 12.3), 10)
            plate_stack(b, "CleanPlates", (37.4, 3.42, 13.8), 7)
            with b.group("WireRack", pos=(37.2, 0, 17)):
                for x in (-1.6, 1.6):
                    for z in (-1.8, 1.8):
                        b.cyl("Post", 0.15, 7.5, (x, 3.75, z), P["steel"], "Metal", collide=False)
                for k, y in enumerate((0.6, 2.4, 4.2, 6.0)):
                    b.part("Wire", (3.4, 0.1, 3.8), (0, y, 0), P["steel"], "DiamondPlate", collide=(k == 0))
                    for m in range(2):
                        b.part("Box", (1.4, 1.1, 1.6), (-0.8 + m * 1.6, y + 0.6, R.uniform(-0.8, 0.8)),
                               R.choice([hx("#c9a26b"), hx("#d8d2c4"), hx("#9e7b52")]), "Cardboard", collide=False)
            jar_shelf(b, "SinkShelf", (38.3, 7.4, 12.5), 6, ry=90)
            with b.group("MopBucket", pos=(36.5, 0, -2.6)):
                b.part("Bucket", (1.8, 1.4, 1.4), (0, 0.7, 0), hx("#f2c14e"), collide=False)
                b.cyl("Mop", 0.15, 5.5, (0.3, 3.2, 0), P["wood_lt"], "Wood", rz=8, collide=False)

        # ---- îlot de découpe
        with b.folder("PrepIsland"):
            cabinet(b, "Island", (0, 0, 7.8), 26, depth=4.4, top=P["marble"])
            for i, x in enumerate((-9.75, -3.25, 3.25, 9.75)):
                cutting_board(b, f"Board{i + 1}", (x, 3.42, 7.8), i + 1)
            for x in (-12.2, 12.2):
                b.cyl("HerbPot", 0.9, 0.8, (x, 3.82, 7.2), P["terracotta"], collide=False)
                b.ball("Herbs", 1.0, (x, 4.5, 7.2), P["leaf3"], "Grass", collide=False, shadow=False)
            b.cyl("Bowl", 1.3, 0.5, (-12.2, 3.67, 8.9), P["steel"], "Metal", refl=0.3, collide=False)
            pot_rack(b, "PotRack", (0, 12, 7.8), 20)

        # ---- passe
        with b.folder("Pass"):
            cabinet(b, "PassCounter", (0, 0, -3.7), 20, depth=2.6, ry=180, top=P["steel"], top_mat="Metal")
            for i, x in enumerate((-7.5, -2.5, 2.5, 7.5)):
                b.cyl(f"PlateSpot{i + 1}", 2.3, 0.04, (x, 3.44, -3.7), hx("#e6e1d6"), "SmoothPlastic",
                      attrs={"Station": "Pass", "Id": i + 1}, collide=False, shadow=False)
                heat_lamp(b, f"HeatLamp{i + 1}", (x, 7.1, -3.7))
                b.cyl("LampRod", 0.1, 7.6, (x, 11.1, -3.7), P["black"], "Metal", collide=False, shadow=False)
            with b.group("Bell", pos=(9.4, 3.42, -2.7)):
                b.cyl("Base", 0.9, 0.12, (0, 0.06, 0), P["black"], collide=False)
                b.ball("Dome", 0.75, (0, 0.38, 0), P["gold"], "Metal", refl=0.3, collide=False)
                b.cyl("Button", 0.15, 0.25, (0, 0.8, 0), P["gold"], "Metal", collide=False)
            plate_stack(b, "PassPlates", (-9.3, 3.42, -2.8), 9)
            b.part("TicketRail", (18, 0.3, 0.4), (0, 8.5, -4.75), P["steel"], "Metal", collide=False)
            for k in range(6):
                b.part("Ticket", (1.0, 1.4, 0.04), (-7 + k * 2.6 + R.uniform(-.3, .3), 7.75, -4.6), P["white"],
                       collide=False, shadow=False, rz=R.uniform(-4, 4))
            jar_shelf(b, "PassShelf", (-24.5, 7.6, -4.3), 19, ry=0)
            jar_shelf(b, "PassShelf", (-24.5, 9.8, -4.3), 19, ry=0)
            jar_shelf(b, "PassShelf2", (16, 8.2, -4.3), 9, ry=0)
            wall_clock(b, "KitchenClock", (32, 10.5, -4.85), ry=180)

        # ---- poubelles, portes, sécurité
        with b.folder("Misc"):
            trash_bin(b, "TrashIsland", (15.8, 0, 7.8))
            trash_bin(b, "TrashPass", (-12.8, 0, -3.3))
            for hinge, sgn in ((22, 1), (26, -1)):
                with b.group("SwingDoor", pos=(hinge, 0, -5.5), ry=-25 * sgn):
                    b.part("Leaf", (1.95, 8.2, 0.25), (sgn * 0.98, 4.4, 0), P["steel"], "Metal", refl=0.15,
                           collide=False)
                    b.cylz("Porthole", 1.0, 0.3, (sgn * 0.98, 6.2, 0), hx("#1f2a33"), "Glass", transp=0.3,
                           collide=False)
                    b.cylz("PortholeRim", 1.2, 0.27, (sgn * 0.98, 6.2, 0), P["steel_dk"], "Metal", collide=False)
                    b.part("KickPlate", (1.8, 1.2, 0.3), (sgn * 0.98, 0.8, 0), P["steel_dk"], "DiamondPlate",
                           collide=False)
            b.part("ExitSign", (2.6, 0.9, 0.2), (32, 9.8, 19.7), hx("#0f7a3a"), "Neon", collide=False, shadow=False,
                   children=[text_gui("SORTIE", face="Front", color=(1, 1, 1), stroke=1)])
            with b.group("Extinguisher", pos=(36.5, 2.6, 19.6)):
                b.cyl("Body", 0.8, 2.2, (0, 0, 0), hx("#c62828"), "Metal", collide=False)
                b.ball("Top", 0.6, (0, 1.2, 0), P["black"], collide=False)
                b.part("Hose", (0.15, 1.6, 0.15), (0.45, 0.3, 0), P["black"], collide=False)
            b.part("FirstAid", (1.4, 1.2, 0.4), (28, 6, 19.8), P["white"], collide=False,
                   children=[text_gui("+", color=(0.85, 0.1, 0.1), stroke=1)])
            for x, z in ((-11.5, 12.5), (20, 3)):
                b.part("Drain", (1.2, 0.05, 1.2), (x, 0.03, z), hx("#555b61"), "DiamondPlate", collide=False,
                       shadow=False)
    b.save(os.path.join(OUT, "Kitchen.model.json"))
    return b.count


# ------------------------------------------------------------------ rue
def build_street():
    b = Builder()
    b.part("Ground", (2048, 2, 2048), (0, -1, -40), hx("#5f8f45"), "Grass")
    with b.folder("Road"):
        b.part("Asphalt", (2048, 0.2, 20), (0, 0.1, -68), P["asphalt"], "Asphalt")
        for z, (z0, z1) in ((-48.5, (-58, -39)), (-81, (-84, -78))):
            b.part("Sidewalk", (900, SIDEWALK, z1 - z0), (0, SIDEWALK / 2, (z0 + z1) / 2), P["pave"], "Pavement")
        for z in (-58.3, -77.7):
            b.part("Curb", (900, SIDEWALK + 0.05, 0.6), (0, (SIDEWALK + 0.05) / 2, z), P["concrete"], "Concrete")
        x = -444
        while x < 444:
            if not (40 < x < 60):
                b.part("Dash", (6, 0.04, 0.45), (x, 0.22, -68), P["white"], "SmoothPlastic", collide=False,
                       shadow=False)
            x += 12
        for z in (-59.4, -76.6):
            b.part("EdgeLine", (900, 0.04, 0.3), (0, 0.22, z), P["white"], collide=False, shadow=False)
        for k in range(8):
            b.part("Zebra", (7, 0.05, 1.1), (50, 0.22, -60 + -2.2 * k), P["white"], collide=False, shadow=False)
        x = -160
        while x <= 160:
            b.part("PaveJoint", (0.12, 0.02, 18.4), (x, SIDEWALK + 0.01, -48.5), shade(P["pave"], 0.85),
                   collide=False, shadow=False)
            x += 8
    with b.folder("StreetFurniture"):
        for x in range(-144, 145, 24):
            street_lamp(b, "StreetLamp", (x, SIDEWALK, -56.0))
            if abs(x + 12) > 1 and abs(x + 12) < 150:
                tree(b, "StreetTree", (x + 12, SIDEWALK, -55.6), 0.9)
            street_lamp(b, "StreetLampFar", (x + 12, SIDEWALK, -80.2), ry=180)
        hydrant(b, "Hydrant", (-47, SIDEWALK, -56.5))
        for x in (-38, 38, -100, 100):
            with b.group("StreetBin", pos=(x, SIDEWALK, -56.6)):
                b.cyl("Post", 0.25, 3.4, (0, 1.7, 0), P["green"], "Metal")
                b.cyl("Ring", 1.5, 0.15, (0, 3.0, -0.8), P["green"], "Metal", collide=False)
                b.cyl("Bag", 1.35, 2.2, (0, 2.0, -0.8), hx("#9cc79a"), "Plastic", transp=0.3, collide=False)
        with b.group("StreetSign", pos=(41.2, SIDEWALK, -56.8)):
            b.cyl("Pole", 0.3, 9, (0, 4.5, 0), P["green"], "Metal")
            b.part("Plaque", (4.6, 1.2, 0.15), (2.2, 8.2, 0), hx("#1e3f8a"), "Metal", collide=False,
                   children=[text_gui("RUE DES LILAS", color=(1, 1, 1), stroke=1, font="Oswald"),
                             text_gui("RUE DES LILAS", face="Back", color=(1, 1, 1), stroke=1, font="Oswald")])
            b.part("PlaqueRim", (4.8, 1.4, 0.1), (2.2, 8.2, 0.03), P["green"], "Metal", collide=False)
        for x, z in ((20, -64), (-60, -72), (100, -64), (-130, -72)):
            b.cyl("Manhole", 2.8, 0.06, (x, 0.22, z), hx("#2a2a2c"), "DiamondPlate", collide=False, shadow=False)
        with b.group("BikeRack", pos=(60, SIDEWALK, -43.5)):
            for k in range(4):
                b.part("Hoop", (0.2, 2.4, 0.2), (k * 1.6 - 2.4, 1.2, 0), P["steel_dk"], "Metal")
            b.part("Bar", (5.2, 0.2, 0.2), (0, 2.4, 0), P["steel_dk"], "Metal", collide=False)
            for k, col in enumerate((hx("#c0392b"), hx("#2f5d8a"))):
                bx = -1.6 + k * 3.2
                for wz in (-1.4, 1.4):
                    b.cylx("Wheel", 2.2, 0.15, (bx, 1.1, wz), hx("#1c1c1c"), "Rubber", collide=False)
                    b.cylx("Hub", 0.5, 0.2, (bx, 1.1, wz), P["steel"], "Metal", collide=False)
                b.part("Frame", (0.18, 0.18, 2.8), (bx, 1.7, 0), col, "Metal", rx=-8, collide=False)
                b.part("Down", (0.18, 1.4, 0.18), (bx, 1.6, -0.3), col, "Metal", rx=30, collide=False)
                b.part("Saddle", (0.5, 0.2, 0.9), (bx, 2.3, 0.6), P["black"], "Leather", collide=False)
                b.part("Handlebar", (1.4, 0.15, 0.15), (bx, 2.4, -1.2), P["black"], "Metal", collide=False)
        bench(b, "Bench", (-70, SIDEWALK, -44), ry=0)
        bench(b, "Bench", (72, SIDEWALK, -44), ry=0)
        with b.group("PostBox", pos=(44.5, SIDEWALK, -43)):
            b.cyl("Post", 0.4, 3, (0, 1.5, 0), P["black"], "Metal")
            b.part("Box", (1.8, 2.2, 1.4), (0, 3.6, 0), hx("#f2c300"), "Metal")
            b.part("Slot", (1.0, 0.12, 0.05), (0, 4.2, -0.72), P["black"], collide=False)
            b.part("Logo", (1.0, 0.6, 0.05), (0, 3.4, -0.72), hx("#1e3f8a"), collide=False,
                   children=[text_gui("POSTE", color=(1, 0.9, 0.2), stroke=1)])
        # abribus
        with b.group("BusStop", pos=(112, SIDEWALK, -52)):
            b.part("Roof", (12, 0.4, 5), (0, 8.2, 0), P["steel_dk"], "Metal")
            b.part("BackGlass", (11.6, 6.5, 0.15), (0, 4.4, 2.2), P["glass"], "Glass", transp=0.6)
            for x in (-5.8, 5.8):
                b.part("Post", (0.3, 8, 0.3), (x, 4, 2.2), P["steel_dk"], "Metal")
            b.part("Bench", (8, 0.3, 1.4), (0, 1.8, 1.3), P["steel"], "Metal")
            b.part("Ad", (0.2, 6, 3.6), (5.9, 4.4, 0.2), [1, 1, 1], "Neon", collide=False,
                   children=[text_gui("Le Petit Bistro\nmeilleur burger\ndu quartier !", face="Left",
                                      color=(0.12, 0.29, 0.23), font="Fondamento", stroke=1, light=0),
                             text_gui("CUISINE\nSIMULATOR", face="Right", color=(0.7, 0.18, 0.18), stroke=1)])
            b.cyl("SignPole", 0.3, 10, (-7.5, 5, -1.5), P["steel_dk"], "Metal")
            b.part("SignBus", (2, 2, 0.2), (-7.5, 9.5, -1.5), hx("#1e6fbf"), collide=False,
                   children=[text_gui("BUS 12", color=(1, 1, 1), stroke=1),
                             text_gui("BUS 12", face="Back", color=(1, 1, 1), stroke=1)])
        car(b, "CarRed", (-72, 0.2, -61.5), 0, hx("#b3302d"))
        car(b, "CarBlue", (88, 0.2, -61.5), 180, hx("#2f5d8a"))
        car(b, "CarCream", (-128, 0.2, -61.5), 0, hx("#e8dcc0"))
        car(b, "CarGreen", (-30, 0.2, -74.5), 180, hx("#3c6e4f"))

    # terrasse
    with b.folder("Terrace"):
        cols = [hx("#b3302d"), P["green"], hx("#b3302d"), P["green"]]
        for i, x in enumerate((-27, -14.5, 14.5, 27)):
            round_table(b, f"TerraceTable{i + 1}", (x, SIDEWALK, -46))
            bistro_chair(b, "TerraceChair", (x - 2.4, SIDEWALK, -46), ry=-90)
            bistro_chair(b, "TerraceChair", (x + 2.4, SIDEWALK, -46), ry=90)
            parasol(b, f"Parasol{i + 1}", (x, SIDEWALK, -46), cols[i])
        for x0, x1 in ((-34, -8), (8, 34)):
            with b.group("PlanterRow", pos=((x0 + x1) / 2, SIDEWALK, -51)):
                b.part("Planter", (x1 - x0, 1.8, 1.4), (0, 0.9, 0), P["green"], "Wood")
                b.part("PlanterTrim", (x1 - x0 + 0.2, 0.2, 1.6), (0, 1.85, 0), P["wood_lt"], "Wood", collide=False)
                n = int((x1 - x0) / 1.3)
                for k in range(n):
                    bx = -(x1 - x0) / 2 + 0.7 + k * 1.3
                    b.ball("Shrub", R.uniform(1.4, 1.9), (bx, 2.4, R.uniform(-.15, .15)),
                           R.choice([P["leaf"], P["leaf2"]]), "Grass", collide=False)
                    if k % 3 == 0:
                        b.ball("Bloom", 0.5, (bx + 0.3, 3.1, -0.3), R.choice([hx("#ff8fab"), hx("#fff3b0")]),
                               collide=False, shadow=False)
        b.part("SpawnLocation", (8, 0.1, 6), (0, SIDEWALK + 0.05, -47.5), P["pave"], "Pavement", cls="SpawnLocation",
               ry=180, transp=1, collide=False, extra={"Neutral": True, "Duration": 0})
    b.save(os.path.join(OUT, "Street.model.json"))
    return b.count


# ----------------------------------------------------------------- parc
def build_park():
    b = Builder()
    pz = -112
    # clôture
    with b.folder("Fence"):
        x = -150
        while x <= 150:
            if not -7 < x < 7:
                b.part("Post", (0.3, 3.6, 0.3), (x, 1.8, -84.6), P["black"], "Metal")
                b.ball("Finial", 0.45, (x, 3.75, -84.6), P["gold"], "Metal", collide=False, shadow=False)
            x += 3
        for x0, x1 in ((-150, -7), (7, 150)):
            for y in (1.0, 3.0):
                b.part("Rail", (x1 - x0, 0.2, 0.2), ((x0 + x1) / 2, y, -84.6), P["black"], "Metal")
        for x in (-7, 7):
            b.part("GatePillar", (1.4, 5, 1.4), (x, 2.5, -84.6), P["stone"], "Slate")
            b.ball("GateLamp", 0.9, (x, 5.5, -84.6), [1, 0.85, 0.6], "Neon", collide=False, shadow=False,
                   children=[point_light(16, 1, WARM)])
    with b.folder("Paths"):
        sand = hx("#cdb88f")
        b.part("MainPath", (7, 0.12, 22), (0, 0.06, -95.5), sand, "Ground")
        b.part("CrossPath", (130, 0.12, 6), (0, 0.06, pz), sand, "Ground")
        b.cyl("Plaza", 34, 0.14, (0, 0.07, pz), sand, "Ground")
        b.cyl("PlazaRing", 35, 0.12, (0, 0.06, pz), P["stone"], "Cobblestone")
    with b.group("Fountain", pos=(0, 0, pz)):
        b.cyl("Basin", 18, 1.8, (0, 0.9, 0), P["stone"], "Limestone")
        b.cyl("BasinRim", 18.6, 0.3, (0, 1.65, 0), shade(P["stone"], 1.15), "Limestone")
        b.cyl("Water", 16.6, 0.12, (0, 1.86, 0), hx("#4fa3c7"), "Glass", transp=0.15, refl=0.25, collide=False)
        b.cyl("Pedestal", 2.4, 4.4, (0, 3.6, 0), P["stone"], "Limestone")
        b.cyl("Bowl", 7, 0.6, (0, 5.9, 0), P["stone"], "Limestone")
        b.cyl("BowlWater", 6.4, 0.12, (0, 6.26, 0), hx("#4fa3c7"), "Glass", transp=0.15, collide=False)
        b.cyl("Column", 1.0, 2.4, (0, 7.4, 0), P["stone"], "Limestone")
        b.cyl("TopBowl", 3, 0.4, (0, 8.7, 0), P["stone"], "Limestone")
        b.ball("Finial", 0.9, (0, 9.3, 0), P["gold"], "Metal", collide=False,
               attrs={"FountainJet": True})
        for k in range(8):
            a = math.radians(k * 45)
            b.cyl("Jet", 0.35, 0.5, (7.2 * math.cos(a), 2.1, 7.2 * math.sin(a)), P["gold"], "Metal", collide=False,
                  attrs={"FountainJet": True})
    with b.folder("Benches"):
        for k in range(4):
            a = k * 90 + 45
            r = 19.5
            bench(b, "Bench", (r * math.sin(math.radians(a)), 0, pz - r * math.cos(math.radians(a))), ry=-a + 180)
    with b.folder("Trees"):
        for i, (x, z) in enumerate(((-40, -95), (-56, -132), (-24, -138), (32, -133), (55, -96), (110, -140),
                                    (-82, -104), (98, -108), (-104, -138), (114, -96), (-124, -98), (128, -134),
                                    (-140, -120), (142, -110), (-18, -96), (20, -95))):
            tree(b, f"ParkTree{i + 1}", (x, 0, z), R.uniform(0.9, 1.3), planter=False)
        for x, z in ((-30, -125), (30, -122), (-70, -96), (68, -116)):
            with b.group("FlowerBed", pos=(x, 0, z)):
                b.cyl("Edge", 8, 0.6, (0, 0.3, 0), P["stone"], "Cobblestone")
                b.cyl("Soil", 7.4, 0.62, (0, 0.32, 0), P["soil"], "Ground", collide=False)
                for k in range(14):
                    a = R.uniform(0, 2 * math.pi)
                    r = R.uniform(0, 3)
                    b.ball("Flower", R.uniform(0.6, 1.0), (r * math.cos(a), 0.9, r * math.sin(a)),
                           R.choice([hx("#e53950"), hx("#ff8fab"), hx("#fff3b0"), hx("#c77dff"), hx("#ffb703")]),
                           collide=False, shadow=False)
        for z in (-90, -100):
            street_lamp(b, "ParkLamp", (-4.5, 0, z), ry=-90)
            street_lamp(b, "ParkLamp", (4.5, 0, z), ry=90)
        for x0, x1 in ((-60, -18), (18, 60)):
            hedge(b, "Hedge", (x1 - x0, 2.2, 1.6), ((x0 + x1) / 2, 1.1, pz - 4.5))
            hedge(b, "Hedge", (x1 - x0, 2.2, 1.6), ((x0 + x1) / 2, 1.1, pz + 4.5))
    # étang
    with b.group("Pond", pos=(-80, 0, -124)):
        b.cyl("Rim", 26, 0.6, (0, 0.3, 0), P["stone"], "Cobblestone")
        b.cyl("Water", 24, 0.12, (0, 0.66, 0), hx("#3f8fb0"), "Glass", transp=0.15, refl=0.25, collide=False)
        for k in range(9):
            a = R.uniform(0, 2 * math.pi)
            r = R.uniform(2, 10)
            b.cyl("LilyPad", R.uniform(1.2, 1.8), 0.06, (r * math.cos(a), 0.76, r * math.sin(a)), hx("#4f8a3a"),
                  collide=False, shadow=False)
            if k % 3 == 0:
                b.ball("Lily", 0.45, (r * math.cos(a) + 0.2, 0.85, r * math.sin(a)), hx("#ffc8dd"), collide=False,
                       shadow=False)
        for k, (dx, dz, ry) in enumerate(((-3, 2, 30), (1, -4, -60), (4, 3, 160))):
            with b.group("Duck", pos=(dx, 0.65, dz), ry=ry):
                col = P["white"] if k else hx("#8d6e4b")
                b.ball("Body", 1.2, (0, 0.4, 0), col, collide=False)
                b.ball("Head", 0.7, (0, 1.0, -0.5), hx("#2e6b3a") if k == 0 else col, collide=False)
                b.part("Beak", (0.3, 0.12, 0.4), (0, 0.95, -0.95), hx("#f2a43a"), collide=False, shadow=False)
        for k in range(12):
            a = math.radians(200 + k * 9)
            b.cyl("Reed", 0.12, R.uniform(2.2, 3.4), (12.6 * math.cos(a), 1.5, 12.6 * math.sin(a)), hx("#6b8e3a"),
                  collide=False, shadow=False)
            b.cyl("Cattail", 0.3, 0.7, (12.6 * math.cos(a), 3.1, 12.6 * math.sin(a)), hx("#6d4c2f"),
                  collide=False, shadow=False)
        with b.group("Dock", pos=(12, 0, 0)):
            for k in range(6):
                b.part("Plank", (1.0, 0.25, 4), (-k * 1.05, 1.0, 0), shade(P["wood_lt"], R.uniform(.8, 1)),
                       "WoodPlanks")
            for px in (0, -5.2):
                for pz in (-1.8, 1.8):
                    b.cyl("Pile", 0.4, 1.4, (px, 0.5, pz), P["wood_dk"], "Wood", collide=False)
    # kiosque à musique
    with b.group("Bandstand", pos=(80, 0, -128)):
        b.cyl("Base", 17, 1.4, (0, 0.7, 0), P["trim"], "Limestone")
        b.cyl("Floor", 16, 0.1, (0, 1.42, 0), P["wood"], "WoodPlanks")
        for k in range(8):
            a = math.radians(k * 45 + 22.5)
            x, z = 7.3 * math.cos(a), 7.3 * math.sin(a)
            b.cyl("Post", 0.5, 8, (x, 5.4, z), P["white"], "Wood")
            if k != 5:
                a2 = math.radians((k + 1) * 45 + 22.5)
                x2, z2 = 7.3 * math.cos(a2), 7.3 * math.sin(a2)
                ang = math.degrees(math.atan2(z2 - z, x2 - x))
                ln = math.hypot(x2 - x, z2 - z)
                b.part("Rail", (ln, 0.25, 0.25), ((x + x2) / 2, 3.6, (z + z2) / 2), P["white"], "Wood", ry=-ang)
                b.part("Balusters", (ln, 1.8, 0.08), ((x + x2) / 2, 2.6, (z + z2) / 2), P["white"], "Wood",
                       ry=-ang, transp=0.35, collide=False)
        for k, (d, y) in enumerate(((18, 9.6), (14, 10.3), (10, 11.0), (6, 11.7), (2.6, 12.3))):
            b.cyl("Roof", d, 0.75, (0, y, 0), P["green"] if k % 2 == 0 else shade(P["green"], 1.2), "Metal")
        b.cyl("RoofTrim", 18.4, 0.3, (0, 9.2, 0), P["gold"], "Metal", collide=False)
        b.ball("Finial", 1.0, (0, 13.0, 0), P["gold"], "Metal", collide=False)
        for k in range(3):
            b.part("Step", (4, 0.45, 1.2), (0, 0.22 + k * 0.45, -9.6 + k * 1.0), P["trim"], "Limestone")
        b.ball("Lantern", 0.9, (0, 8.3, 0), [1, 0.85, 0.6], "Neon", collide=False, shadow=False,
               children=[point_light(22, 1.1, WARM)])
        for k in range(3):
            with b.group("MusicStand", pos=(-2 + k * 2, 1.45, 1.5)):
                b.cyl("Pole", 0.1, 2.6, (0, 1.3, 0), P["black"], "Metal", collide=False)
                b.part("Desk", (1.2, 0.8, 0.05), (0, 2.7, 0), P["black"], "Metal", rx=-20, collide=False)
    # marchand de glaces
    with b.group("IceCreamCart", pos=(10, 0, -99), ry=-90):
        b.part("Body", (5, 2.8, 2.6), (0, 2.2, 0), hx("#ffd6e0"), "SmoothPlastic")
        b.part("Stripe", (5.05, 0.5, 2.65), (0, 2.6, 0), hx("#e05780"), collide=False)
        b.part("Counter", (5.2, 0.2, 2.8), (0, 3.7, 0), P["white"], collide=False)
        for k, col in enumerate((hx("#fff3b0"), hx("#ff8fab"), hx("#7b4b2a"), hx("#9ad18b"))):
            b.ball("Scoop", 0.8, (-1.6 + k * 1.05, 4.05, 0), col, collide=False, shadow=False)
        for sx in (-1.6, 1.6):
            b.cylz("Wheel", 1.8, 0.3, (sx, 0.9, -1.4), P["black"], "Rubber", collide=False)
            b.cylz("Wheel", 1.8, 0.3, (sx, 0.9, 1.4), P["black"], "Rubber", collide=False)
        b.cyl("UmbrellaPole", 0.18, 6, (2, 5.5, 0.6), P["white"], "Metal", collide=False)
        b.cyl("Umbrella", 6, 0.25, (2, 8.4, 0.6), hx("#e05780"), "Fabric", collide=False)
        b.cyl("Umbrella2", 3.5, 0.35, (2, 8.7, 0.6), P["cream"], "Fabric", collide=False)
        b.part("Sign", (3, 0.9, 0.1), (0, 2.2, -1.36), hx("#e05780"), collide=False,
               children=[text_gui("GLACES", color=(1, 1, 1), stroke=1)])
    b.save(os.path.join(OUT, "Park.model.json"))
    return b.count


# -------------------------------------------------------------- quartier
def facade_building(b, name, x0, x1, height, floors, color, mat, shop_text, shop_col, roof_col=None):
    z0, z1 = -39, 15
    w = x1 - x0
    xc = (x0 + x1) / 2
    with b.group(name):
        b.part("Shell", (w, height, z1 - z0), (xc, height / 2, (z0 + z1) / 2), color, mat)
        b.part("Roof", (w + 0.6, 0.6, z1 - z0 + 0.6), (xc, height + 0.3, (z0 + z1) / 2), roof_col or P["stone"],
               "Slate")
        b.part("Cornice", (w + 1.2, 1.0, 1.4), (xc, height - 0.5, z0 - 0.5), P["trim"], "Concrete")
        b.part("FloorBand", (w, 0.6, 0.5), (xc, 10.5, z0 - 0.25), P["trim"], "Concrete")
        # devanture
        sw = w - 6
        b.part("ShopGlass", (sw, 6.5, 0.2), (xc, 4.2, z0 - 0.1), hx("#2a3a44"), "Glass", transp=0.2, refl=0.2,
               children=[{"ClassName": "SurfaceLight", "Properties": {"Face": "Front", "Range": 8,
                                                                      "Brightness": 0.5, "Color": list(WARM)}}])
        for k in range(int(sw / 5) + 1):
            b.part("ShopMullion", (0.35, 6.5, 0.4), (xc - sw / 2 + k * sw / int(sw / 5), 4.2, z0 - 0.2), shop_col,
                   "Wood", collide=False)
        b.part("ShopBase", (sw + 0.6, 0.9, 0.5), (xc, 0.45 + SIDEWALK, z0 - 0.25), shop_col, "Wood")
        b.part("ShopHead", (sw + 0.6, 0.6, 0.5), (xc, 7.75, z0 - 0.25), shop_col, "Wood", collide=False)
        b.part("ShopSign", (min(sw, 22), 1.8, 0.4), (xc, 9.2, z0 - 0.3), shop_col, "Wood", collide=False,
               children=[text_gui(shop_text, color=(0.97, 0.94, 0.85), font="Fondamento", stroke=0.8)])
        n = max(2, round(sw / 1.0))
        ww = sw / n
        for i in range(n):
            col = shop_col if i % 2 == 0 else P["cream"]
            b.part("AwningStripe", (ww + 0.01, 0.15, 3.4), (xc - sw / 2 + ww * (i + 0.5), 8.0, z0 - 1.6), col,
                   "Fabric", rx=-20, collide=False)
        # étages
        nwin = max(2, int(w / 7))
        for f in range(1, floors):
            y = 10.5 + (f - 0.5) * (height - 12) / max(1, floors - 1)
            for i in range(nwin):
                wx = x0 + (i + 0.5) * w / nwin
                window(b, "Window", (wx, y, z0 - 0.05), 3.4, 5, 0, cols=2, rows=2, frame=P["white"],
                       glass=hx("#4a6272"))
                for s in (-1, 1):
                    b.part("Shutter", (1.6, 5.2, 0.15), (wx + s * 2.6, y, z0 - 0.15), shade(shop_col, 1.1), "Wood",
                           collide=False)
                if f == 1 and i % 2 == 0:
                    b.part("Balcony", (5, 0.3, 1.6), (wx, y - 2.7, z0 - 0.8), P["stone"], "Concrete")
                    b.part("Railing", (5, 1.4, 0.1), (wx, y - 1.9, z0 - 1.55), P["black"], "Metal", transp=0.3,
                           collide=False)


def build_neighborhood():
    b = Builder()
    with b.folder("Neighbors"):
        facade_building(b, "Boulangerie", -95, -42, 26, 3, hx("#e8dcc4"), "Plaster", "BOULANGERIE", hx("#2f5d8a"))
        facade_building(b, "Fleuriste", -150, -97, 33, 4, hx("#d4a373"), "Plaster", "FLEURISTE", hx("#3c6e2d"))
        facade_building(b, "Librairie", 42, 95, 29, 3, hx("#9fb8ad"), "Plaster", "LIBRAIRIE", hx("#6d2532"))
        facade_building(b, "Fromagerie", 97, 150, 22, 2, hx("#e3c7a6"), "Plaster", "FROMAGERIE", hx("#b8862b"))
    with b.folder("Skyline"):
        for i in range(26):
            side = i % 4
            hgt = R.uniform(30, 70)
            col = R.choice([hx("#b9b3a8"), hx("#a7b0b5"), hx("#c8bba4"), hx("#9aa29c")])
            if side == 0:
                pos, size = (R.uniform(-220, 220), hgt / 2, R.uniform(80, 130)), (R.uniform(25, 50), hgt, 30)
            elif side == 1:
                pos, size = (R.uniform(-220, 220), hgt / 2, R.uniform(-210, -180)), (R.uniform(25, 50), hgt, 30)
            elif side == 2:
                pos, size = (R.uniform(-260, -200), hgt / 2, R.uniform(-150, 60)), (30, hgt, R.uniform(25, 50))
            else:
                pos, size = (R.uniform(200, 260), hgt / 2, R.uniform(-150, 60)), (30, hgt, R.uniform(25, 50))
            b.part("Tower", size, pos, col, "Concrete", shadow=False)
            b.part("TowerTop", (size[0] + 1, 1, size[2] + 1), (pos[0], hgt + 0.5, pos[2]), shade(col, 0.8),
                   "Concrete", shadow=False)
    with b.folder("BackAlley"):
        b.part("AlleyFloor", (84, 0.15, 26), (0, 0.075, 34), P["concrete"], "Concrete")
        for x in range(-42, 43, 2):
            b.part("FenceBoard", (1.8, 6, 0.3), (x, 3, 47), shade(P["wood_lt"], R.uniform(0.75, 0.95)), "WoodPlanks")
        dumpster(b, "Dumpster", (-30, 0.15, 25.6), 0, hx("#2f6b3a"))
        dumpster(b, "Dumpster", (-22.5, 0.15, 25.6), 0, hx("#2f5d8a"))
        for k in range(5):
            b.part("Pallet", (4, 0.5, 4), (-10, 0.4 + k * 0.5, 24.5), shade(P["wood_lt"], 0.85), "WoodPlanks")
        for k, (dx, dy) in enumerate(((0, 0), (2.6, 0), (1.3, 1.6))):
            b.part("StackCrate", (2.4, 1.6, 2.4), (-4 + dx, 0.95 + dy, 24.4), P["wood_lt"], "WoodPlanks")
        for x in (36.5, 37.6):
            b.cyl("GasBottle", 1.0, 3.2, (x, 1.75, 22.9), hx("#9cc3d5"), "Metal")
        van(b, "DeliveryVan", (8, 0.15, 36), 180, P["white"], "Primeur Bio · Livraison")
        with b.group("Condenser", pos=(-36, 0.15, 24)):
            b.part("Body", (4, 3.4, 3), (0, 1.7, 0), hx("#d3d6da"), "Metal")
            b.cylz("Fan", 2.4, 0.2, (0, 1.8, -1.55), hx("#2c2f33"), "DiamondPlate", collide=False)
    b.save(os.path.join(OUT, "Neighborhood.model.json"))
    return b.count


# ------------------------------------------------------------ gameplay
def build_gameplay(spots):
    b = Builder(cls="Folder")
    with b.folder("CustomerSpots"):
        for (pos, ry, aisle, sid) in spots:
            b.part(f"Spot_{sid}", (1.6, 0.2, 1.6), pos, P["white"], ry=ry, transp=1, collide=False, shadow=False,
                   attrs={"Aisle": aisle, "SpotId": sid, "Stool": sid.startswith("B")})
    with b.folder("Waypoints"):
        for name, pos in (("StreetLeft", (-150, SIDEWALK, -53.5)), ("StreetRight", (150, SIDEWALK, -53.5)),
                          ("Curb", (0, SIDEWALK, -53.5)), ("Door", (0, Y0, -39)),
                          ("FrontAisle", (0, Y0, FRONT_AISLE_Z))):
            b.part(name, (1, 1, 1), pos, P["white"], transp=1, collide=False, shadow=False)
    b.save(os.path.join(OUT, "Gameplay.model.json"))
    return b.count


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    total = build_restaurant()
    n, spots = build_dining()
    total += n
    total += build_kitchen()
    total += build_street()
    total += build_park()
    total += build_neighborhood()
    total += build_gameplay(spots)
    print(f"Map générée : {total} pièces, {len(spots)} places clients")

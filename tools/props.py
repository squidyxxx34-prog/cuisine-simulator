"""Mobilier et accessoires réutilisables. Toutes les fonctions prennent un Builder
et des coordonnées locales (sol = y 0, avant de l'objet = -Z)."""
from lib import hx, shade, point_light, spot_light, surface_light, text_gui, R

# ---------- palette ----------
P = {
    "brick": hx("#8f3d2c"), "brick2": hx("#7a3325"), "trim": hx("#efe4cc"), "green": hx("#1f4a3b"),
    "green2": hx("#2e5e4e"), "gold": hx("#c99a3f"), "wood_dk": hx("#4a2e1b"), "wood": hx("#7d4f2c"),
    "wood_lt": hx("#b7895a"), "steel": hx("#c3c7cc"), "steel_dk": hx("#8a8f96"), "black": hx("#1d1d1f"),
    "tile_w": hx("#f1f0ea"), "tile_dk": hx("#2b2c33"), "marble": hx("#e8e4dd"), "red": hx("#b3302d"),
    "cream": hx("#f6efe0"), "plaster": hx("#f3efe6"), "leather": hx("#7a1f24"), "glass": hx("#a9c6d6"),
    "warm": [1, 0.78, 0.5], "leaf": hx("#4f8a3a"), "leaf2": hx("#3c6e2d"), "leaf3": hx("#6aa84f"),
    "terracotta": hx("#b4603c"), "soil": hx("#3b2a1e"), "white": hx("#fbfbf8"), "asphalt": hx("#3a3b3f"),
    "pave": hx("#b9b5ad"), "concrete": hx("#a8a59e"), "stone": hx("#6f6b66"),
}
WARM = (1, 0.8, 0.55)


# ---------- assises & tables ----------
def chair(b, name, pos, ry=0, wood=None, seat_col=None):
    wood = wood or P["wood_dk"]
    seat_col = seat_col or P["leather"]
    with b.group(name, pos=pos, ry=ry):
        b.part("Seat", (2, 0.35, 2), (0, 1.75, 0), seat_col, "Leather")
        b.part("SeatFrame", (2.1, 0.15, 2.1), (0, 1.52, 0), wood, "Wood")
        for sx in (-0.85, 0.85):
            for sz in (-0.85, 0.85):
                b.part("Leg", (0.22, 1.5, 0.22), (sx, 0.75, sz), wood, "Wood", collide=False)
            b.part("Post", (0.22, 2.6, 0.22), (sx, 3.1, 0.9), wood, "Wood", collide=False)
        b.part("BackRest", (1.7, 0.9, 0.18), (0, 3.5, 0.9), seat_col, "Leather", collide=False)
        b.part("BackTop", (2, 0.22, 0.25), (0, 4.35, 0.9), wood, "Wood", collide=False)
        b.part("Rung", (1.6, 0.12, 0.12), (0, 0.5, -0.85), wood, "Wood", collide=False)


def table_square(b, name, pos, cloth=True):
    with b.group(name, pos=pos):
        b.part("Top", (4.4, 0.3, 4.4), (0, 3.1, 0), P["wood_dk"], "Wood")
        b.cyl("Pedestal", 0.55, 2.9, (0, 1.5, 0), P["black"], "Metal", collide=False)
        b.cyl("Foot", 2.4, 0.2, (0, 0.1, 0), P["black"], "Metal", collide=False)
        if cloth:
            b.part("Cloth", (4.7, 0.06, 4.7), (0, 3.28, 0), P["white"], "Fabric", collide=False)
            for s in (-1, 1):  # retombées de nappe
                b.part("ClothSide", (4.7, 0.9, 0.05), (0, 2.88, s * 2.35), P["white"], "Fabric", collide=False)
                b.part("ClothSide", (0.05, 0.9, 4.7), (s * 2.35, 2.88, 0), P["white"], "Fabric", collide=False)
            b.part("Runner", (1.1, 0.07, 4.75), (0, 3.3, 0), P["red"], "Fabric", collide=False)
        centerpiece(b, (0, 3.32, 0))
        # sel / poivre
        b.cyl("Salt", 0.22, 0.45, (0.7, 3.55, 0.6), P["white"], "Glass", collide=False, shadow=False)
        b.cyl("Pepper", 0.22, 0.45, (0.95, 3.55, 0.6), P["black"], "SmoothPlastic", collide=False, shadow=False)


def centerpiece(b, pos):
    x, y, z = pos
    b.cyl("Vase", 0.38, 0.8, (x - 0.3, y + 0.4, z), P["glass"], "Glass", transp=0.35, collide=False, shadow=False)
    b.cyl("Stem", 0.06, 0.6, (x - 0.3, y + 1.0, z), P["leaf2"], collide=False, shadow=False)
    flower = R.choice([hx("#e04f5f"), hx("#f2c14e"), hx("#f7f3ee"), hx("#d96ba8")])
    b.ball("Flower", 0.38, (x - 0.3, y + 1.35, z), flower, "SmoothPlastic", collide=False, shadow=False)
    b.cyl("Candle", 0.24, 0.5, (x + 0.35, y + 0.25, z), P["cream"], collide=False, shadow=False)
    b.ball("Flame", 0.14, (x + 0.35, y + 0.58, z), [1, 0.62, 0.25], "Neon", collide=False, shadow=False,
           children=[point_light(7, 0.7, (1, 0.65, 0.35))])


def stool(b, name, pos, ry=0):
    with b.group(name, pos=pos, ry=ry):
        b.cyl("Base", 1.8, 0.2, (0, 0.1, 0), P["black"], "Metal")
        b.cyl("Pole", 0.3, 2.4, (0, 1.3, 0), P["steel"], "Metal", refl=0.2, collide=False)
        b.cyl("FootRing", 1.4, 0.1, (0, 1.0, 0), P["gold"], "Metal", collide=False)
        b.cyl("Seat", 1.7, 0.35, (0, 2.6, 0), P["leather"], "Leather")
        b.cyl("SeatRim", 1.75, 0.08, (0, 2.42, 0), P["black"], "Metal", collide=False)


def round_table(b, name, pos, d=3.2, top_col=None):
    with b.group(name, pos=pos):
        b.cyl("Top", d, 0.2, (0, 3.0, 0), top_col or P["marble"], "Marble")
        b.cyl("Pole", 0.3, 2.9, (0, 1.5, 0), P["black"], "Metal", collide=False)
        b.cyl("Foot", 1.6, 0.15, (0, 0.08, 0), P["black"], "Metal")


def bistro_chair(b, name, pos, ry=0):
    """Chaise de terrasse en rotin/métal."""
    with b.group(name, pos=pos, ry=ry):
        b.part("Seat", (1.6, 0.2, 1.6), (0, 1.8, 0), hx("#c9a26b"), "Fabric")
        for sx in (-0.7, 0.7):
            for sz in (-0.7, 0.7):
                b.part("Leg", (0.12, 1.7, 0.12), (sx, 0.85, sz), P["black"], "Metal", collide=False)
            b.part("Post", (0.12, 2.0, 0.12), (sx, 2.8, 0.75), P["black"], "Metal", collide=False)
        for i in range(3):
            b.part("Weave", (1.5, 0.22, 0.08), (0, 2.6 + i * 0.5, 0.75), hx("#c9a26b"), "Fabric", collide=False)


def parasol(b, name, pos, color):
    with b.group(name, pos=pos):
        b.cyl("Pole", 0.22, 9, (0, 4.5, 0), P["wood_lt"], "Wood", collide=False)
        b.cyl("Canopy", 9, 0.25, (0, 8.6, 0), color, "Fabric", collide=False)
        b.cyl("Canopy2", 6, 0.35, (0, 8.9, 0), color, "Fabric", collide=False)
        b.cyl("Canopy3", 2.6, 0.4, (0, 9.2, 0), color, "Fabric", collide=False)
        b.cyl("Rim", 9.05, 0.6, (0, 8.25, 0), P["cream"], "Fabric", collide=False, transp=0)
        b.ball("Finial", 0.5, (0, 9.6, 0), P["wood_lt"], "Wood", collide=False)


# ---------- éclairage & déco ----------
def pendant(b, name, pos, drop=4, shade_col=None, shadows=False):
    x, y, z = pos  # y = hauteur du plafond
    shade_col = shade_col or P["green"]
    with b.group(name, pos=(x, y, z)):
        b.cyl("Cord", 0.08, drop, (0, -drop / 2, 0), P["black"], collide=False, shadow=False)
        b.cyl("Shade", 1.9, 0.9, (0, -drop - 0.3, 0), shade_col, "Metal", collide=False)
        b.cyl("ShadeCap", 0.9, 0.4, (0, -drop + 0.3, 0), shade_col, "Metal", collide=False)
        b.cyl("ShadeRim", 1.95, 0.1, (0, -drop - 0.75, 0), P["gold"], "Metal", collide=False)
        b.ball("Bulb", 0.6, (0, -drop - 0.75, 0), [1, 0.85, 0.6], "Neon", collide=False, shadow=False,
               children=[point_light(20, 1.15, WARM, shadows)])


def plant(b, name, pos, size=1.0, tall=False):
    s = size
    with b.group(name, pos=pos):
        b.cyl("Pot", 2.2 * s, 2.0 * s, (0, 1.0 * s, 0), P["terracotta"], "Plastic")
        b.cyl("PotRim", 2.45 * s, 0.35 * s, (0, 1.9 * s, 0), shade(P["terracotta"], 0.9), "Plastic", collide=False)
        b.cyl("Soil", 2.0 * s, 0.1 * s, (0, 2.1 * s, 0), P["soil"], "Ground", collide=False)
        if tall:
            b.cyl("Trunk", 0.3 * s, 4.5 * s, (0, 4.2 * s, 0), P["wood"], "Wood", collide=False)
            for i in range(7):
                ox, oz = R.uniform(-0.9, 0.9) * s, R.uniform(-0.9, 0.9) * s
                b.ball("Leaves", R.uniform(1.8, 2.6) * s, (ox, (5.2 + R.uniform(0, 2.2)) * s, oz),
                       R.choice([P["leaf"], P["leaf2"], P["leaf3"]]), "Grass", collide=False)
        else:
            for i in range(6):
                ox, oz = R.uniform(-0.6, 0.6) * s, R.uniform(-0.6, 0.6) * s
                b.ball("Leaves", R.uniform(1.0, 1.6) * s, (ox, (2.5 + R.uniform(0, 0.9)) * s, oz),
                       R.choice([P["leaf"], P["leaf2"], P["leaf3"]]), "Grass", collide=False)


def painting(b, name, pos, w, h, ry=0):
    """Tableau abstrait, face vers -Z local."""
    with b.group(name, pos=pos, ry=ry):
        b.part("Back", (w, h, 0.1), (0, 0, 0), P["cream"], "Fabric", collide=False)
        t = 0.3
        for sy in (-1, 1):
            b.part("Frame", (w + 2 * t, t, 0.3), (0, sy * (h / 2 + t / 2), -0.05), P["gold"], "Metal", collide=False)
        for sx in (-1, 1):
            b.part("Frame", (t, h, 0.3), (sx * (w / 2 + t / 2), 0, -0.05), P["gold"], "Metal", collide=False)
        pal = [hx("#d1495b"), hx("#edae49"), hx("#00798c"), hx("#30638e"), hx("#003d5b"), hx("#7a9e7e"), hx("#e6aace")]
        for i in range(R.randint(3, 5)):
            cw, ch = R.uniform(0.2, 0.55) * w, R.uniform(0.2, 0.55) * h
            cx = R.uniform(-(w - cw) / 2, (w - cw) / 2)
            cy = R.uniform(-(h - ch) / 2, (h - ch) / 2)
            b.part("Paint", (cw, ch, 0.04), (cx, cy, -0.07 - i * 0.01), R.choice(pal), collide=False, shadow=False)


def chalkboard(b, name, pos, w, h, text, ry=0):
    with b.group(name, pos=pos, ry=ry):
        b.part("Board", (w, h, 0.15), (0, 0, 0), hx("#26302b"), "Slate", collide=False,
               children=[text_gui(text, color=(0.96, 0.94, 0.88), font="PermanentMarker", stroke=1, ppu=60, rich=True)])
        t = 0.25
        for sy in (-1, 1):
            b.part("Frame", (w + 2 * t, t, 0.3), (0, sy * (h / 2 + t / 2), 0), P["wood"], "Wood", collide=False)
        for sx in (-1, 1):
            b.part("Frame", (t, h, 0.3), (sx * (w / 2 + t / 2), 0, 0), P["wood"], "Wood", collide=False)


def wall_clock(b, name, pos, ry=0):
    with b.group(name, pos=pos, ry=ry):
        b.cylz("Body", 2.2, 0.3, (0, 0, 0), P["white"], collide=False)
        b.cylz("Rim", 2.4, 0.2, (0, 0, 0.1), P["black"], "Metal", collide=False)
        b.part("HourHand", (0.12, 0.6, 0.05), (0, 0.25, -0.18), P["black"], collide=False, shadow=False)
        b.part("MinuteHand", (0.75, 0.08, 0.05), (0.35, 0, -0.2), P["black"], collide=False, shadow=False)
        for i in range(12):
            import math
            a = i * math.pi / 6
            b.part("Tick", (0.08, 0.2, 0.04), (0.9 * math.sin(a), 0.9 * math.cos(a), -0.17), P["black"],
                   rz=-i * 30, collide=False, shadow=False)


def ceiling_fan(b, name, pos):
    x, y, z = pos
    with b.group(name, pos=(x, y, z)):
        b.cyl("Rod", 0.18, 2, (0, -1, 0), P["gold"], "Metal", collide=False)
        b.cyl("Motor", 1.1, 0.6, (0, -2.2, 0), P["gold"], "Metal", collide=False)
        with b.group("Blades", pos=(0, -2.45, 0), attrs={"Spin": True}):
            b.cyl("Hub", 0.8, 0.2, (0, 0, 0), P["wood_dk"], "Wood", collide=False)
            for i in range(5):
                b.part("Blade", (3.4, 0.08, 0.9), (2.0, 0, 0), P["wood_dk"], "Wood", ry=i * 72, collide=False)
        b.ball("Light", 0.7, (0, -2.75, 0), [1, 0.9, 0.7], "Neon", collide=False, shadow=False)


# ---------- cuisine ----------
def cabinet(b, name, pos, length, depth=3.4, ry=0, body=None, top=None, top_mat="Marble", doors=True):
    body = body or P["steel"]
    top = top or P["marble"]
    with b.group(name, pos=pos, ry=ry):
        b.part("Body", (length, 3.0, depth - 0.25), (0, 1.6, 0.12), body, "Metal", refl=0.08)
        b.part("Kick", (length, 0.35, depth - 0.6), (0, 0.18, 0.3), P["black"], collide=False)
        b.part("Top", (length + 0.1, 0.32, depth + 0.1), (0, 3.26, 0), top, top_mat)
        if doors:
            n = max(1, round(length / 2.6))
            w = length / n
            for i in range(n):
                cx = -length / 2 + w * (i + 0.5)
                b.part("Door", (w - 0.15, 2.5, 0.06), (cx, 1.75, -depth / 2 + 0.1), shade(body, 0.96), "Metal",
                       collide=False, refl=0.1)
                b.cyl("Handle", 0.12, 1.0, (cx + w / 2 - 0.45, 2.3, -depth / 2 - 0.02), P["steel_dk"], "Metal",
                      collide=False, shadow=False)


def stove(b, name, pos, ry=0, idx=1):
    with b.group(name, pos=pos, ry=ry):
        b.part("Body", (6.4, 3.0, 3.5), (0, 1.6, 0), P["steel"], "Metal", refl=0.15)
        b.part("Kick", (6.2, 0.35, 3.0), (0, 0.18, 0.2), P["black"], collide=False)
        b.part("OvenDoor", (5.2, 1.9, 0.12), (0, 1.35, -1.78), P["steel_dk"], "Metal", collide=False, refl=0.1)
        b.part("OvenGlass", (3.6, 0.9, 0.05), (0, 1.35, -1.85), hx("#1a1a1a"), "Glass", collide=False, refl=0.25,
               children=[surface_light("Front", 4, 0.5, 60, (1, 0.6, 0.3))])
        b.cylx("OvenHandle", 0.18, 4.6, (0, 2.45, -1.95), P["steel"], "Metal", collide=False)
        b.part("Panel", (6.4, 0.5, 0.1), (0, 2.85, -1.78), P["black"], "Metal", collide=False)
        for i, kx in enumerate((-2.2, -0.75, 0.75, 2.2)):
            b.cylz("Knob", 0.38, 0.25, (kx, 2.85, -1.9), P["black"], collide=False, shadow=False)
            b.part("KnobMark", (0.06, 0.16, 0.05), (kx, 2.92, -2.03), P["white"], collide=False, shadow=False)
        b.part("Backsplash", (6.4, 1.3, 0.25), (0, 3.85, 1.62), P["steel"], "Metal", collide=False)
        top = b.part("Cooktop", (6.4, 0.18, 3.5), (0, 3.18, 0), hx("#222327"), "Metal",
                     attrs={"Station": "Stove", "Id": idx})
        for bx in (-1.6, 1.6):
            for bz in (-0.8, 0.8):
                b.cyl("BurnerRing", 1.5, 0.08, (bx, 3.3, bz), hx("#34353a"), "Metal", collide=False, shadow=False)
                b.cyl("Burner", 0.7, 0.1, (bx, 3.31, bz), hx("#111111"), "Metal", collide=False, shadow=False)
                for g in range(2):
                    b.part("Grate", (1.6, 0.1, 0.12), (bx, 3.38, bz), P["black"], "Metal", ry=g * 90, collide=False,
                           shadow=False)
        # casserole décorative sur un feu arrière
        b.cyl("PotBody", 1.3, 1.0, (1.6, 3.9, 0.8), P["steel"], "Metal", refl=0.2, collide=False)
        b.cyl("PotLid", 1.35, 0.1, (1.6, 4.45, 0.8), P["steel_dk"], "Metal", collide=False)
        b.ball("PotKnob", 0.25, (1.6, 4.55, 0.8), P["black"], collide=False)
    return top


def fridge(b, name, pos, ry, label, ingredient):
    with b.group(name, pos=pos, ry=ry):
        body = b.part("Body", (5, 8.4, 3.2), (0, 4.2, 0), P["steel"], "Metal", refl=0.18,
                      attrs={"Station": "Crate", "Ingredient": ingredient})
        for sx in (-1.25, 1.25):
            b.part("Door", (2.42, 6.6, 0.12), (sx, 3.9, -1.66), shade(P["steel"], 1.03), "Metal", collide=False,
                   refl=0.2)
            b.part("Handle", (0.14, 3.2, 0.2), (sx - sx * 0.85, 4.5, -1.82), P["steel_dk"], "Metal", collide=False)
        b.part("Grille", (4.8, 1.2, 0.1), (0, 7.75, -1.65), P["black"], "DiamondPlate", collide=False)
        b.part("Display", (1.2, 0.5, 0.05), (1.4, 7.75, -1.72), hx("#0f2a3d"), "Glass", collide=False,
               children=[text_gui("2°C", color=(0.4, 0.9, 1), stroke=1)])
        b.part("Label", (3, 0.7, 0.05), (-0.9, 7.75, -1.72), P["cream"], collide=False,
               children=[text_gui(label, color=(0.15, 0.15, 0.15), stroke=1, ppu=50)])
        b.part("Feet", (4.8, 0.3, 3), (0, 0.15, 0), P["black"], collide=False)
    return body


def crate(b, name, pos, ingredient, label, ry=0):
    """Cagette en bois remplie, avec étiquette ardoise."""
    with b.group(name, pos=pos, ry=ry):
        body = b.part("Crate", (3.2, 1.3, 2.4), (0, 0.65, 0), P["wood_lt"], "WoodPlanks",
                      attrs={"Station": "Crate", "Ingredient": ingredient})
        for sy in (0.25, 0.85):
            b.part("Slat", (3.25, 0.12, 2.45), (0, sy, 0), shade(P["wood_lt"], 0.8), "Wood", collide=False,
                   shadow=False)
        for sx in (-1.55, 1.55):
            for sz in (-1.15, 1.15):
                b.part("Corner", (0.18, 1.35, 0.18), (sx, 0.68, sz), shade(P["wood_lt"], 0.7), "Wood",
                       collide=False)
        fill_crate(b, ingredient)
        b.part("Tag", (1.8, 0.6, 0.06), (0, 0.65, -1.25), hx("#26302b"), "Slate", collide=False,
               children=[text_gui(label, color=(0.97, 0.95, 0.9), font="PermanentMarker", stroke=1, ppu=60)])
    return body


def fill_crate(b, ingredient):
    y = 1.35
    if ingredient == "Tomate":
        for ix in range(5):
            for iz in range(4):
                b.ball("Tomato", 0.6, (-1.25 + ix * 0.62 + R.uniform(-.05, .05), y + R.uniform(-.05, .1),
                                       -0.9 + iz * 0.6), hx("#d32f2f"), collide=False, shadow=False)
    elif ingredient == "Salade":
        for ix in range(3):
            for iz in range(2):
                b.ball("Lettuce", 1.0, (-1.0 + ix * 1.0, y + 0.1, -0.5 + iz * 1.0), hx("#8bc34a"), "Grass",
                       collide=False, shadow=False)
                b.ball("Lettuce", 0.6, (-1.0 + ix * 1.0, y + 0.45, -0.5 + iz * 1.0), hx("#c5e1a5"), "Grass",
                       collide=False, shadow=False)
    elif ingredient == "Pain":
        for i in range(5):
            b.cylx("Baguette", 0.42, 2.9, (0, y + (i % 2) * 0.3, -0.85 + i * 0.42), hx("#d39b52"), "Sand",
                   collide=False, shadow=False)
    elif ingredient == "Pates":
        for ix in range(4):
            for iz in range(2):
                b.part("Pack", (0.6, 0.9, 0.9), (-1.0 + ix * 0.68, y + 0.2, -0.5 + iz * 1.0),
                       hx("#1f5aa6") if (ix + iz) % 2 else hx("#f2c14e"), collide=False, shadow=False)
    elif ingredient == "Oignon":
        for ix in range(5):
            for iz in range(4):
                b.ball("Onion", 0.55, (-1.25 + ix * 0.62, y, -0.9 + iz * 0.6), hx("#c98b4e"), collide=False,
                       shadow=False)


def cutting_board(b, name, pos, idx, ry=0):
    with b.group(name, pos=pos, ry=ry):
        board = b.part("Board", (2.8, 0.18, 1.9), (0, 0.09, 0), hx("#c8955f"), "Wood",
                       attrs={"Station": "Board", "Id": idx})
        b.part("Blade", (1.3, 0.05, 0.28), (0.45, 0.22, 0.55), P["steel"], "Metal", refl=0.3, ry=20, collide=False,
               shadow=False)
        b.part("KnifeHandle", (0.6, 0.12, 0.18), (-0.45, 0.24, 0.85), P["black"], ry=20, collide=False, shadow=False)
    return board


def trash_bin(b, name, pos):
    with b.group(name, pos=pos):
        body = b.cyl("Bin", 2.2, 3.0, (0, 1.5, 0), hx("#5a6068"), "Metal", attrs={"Station": "Trash"})
        b.cyl("Lid", 2.35, 0.25, (0, 3.1, 0), hx("#3d4248"), "Metal", collide=False)
        b.part("Pedal", (0.8, 0.15, 0.6), (0, 0.15, -1.25), P["black"], "Metal", collide=False)
        b.part("Sign", (1.2, 0.8, 0.05), (0, 1.8, -1.12), hx("#2e7d32"), collide=False,
               children=[text_gui("♻", color=(1, 1, 1), stroke=1)])
    return body


def plate_stack(b, name, pos, n=6):
    with b.group(name, pos=pos):
        for i in range(n):
            b.cyl("Plate", 1.4, 0.1, (0, 0.06 + i * 0.12, 0), P["white"], "SmoothPlastic", collide=False,
                  shadow=False)


def jar_shelf(b, name, pos, length, ry=0):
    """Étagère murale garnie de bocaux, épices et casseroles."""
    with b.group(name, pos=pos, ry=ry):
        b.part("Board", (length, 0.2, 1.4), (0, 0, 0), P["wood"], "Wood", collide=False)
        for sx in (-length / 2 + 0.6, length / 2 - 0.6):
            b.part("Bracket", (0.15, 0.8, 1.2), (sx, -0.5, 0.05), P["black"], "Metal", collide=False)
        x = -length / 2 + 0.5
        while x < length / 2 - 0.5:
            kind = R.random()
            if kind < 0.45:
                h = R.uniform(0.7, 1.2)
                b.cyl("Jar", 0.6, h, (x, 0.1 + h / 2, 0), P["glass"], "Glass", transp=0.4, collide=False, shadow=False)
                b.cyl("JarContent", 0.5, h * 0.7, (x, 0.1 + h * 0.35, 0),
                      R.choice([hx("#e0b04a"), hx("#7d4f2c"), hx("#c62828"), hx("#f5f0e1"), hx("#558b2f")]),
                      collide=False, shadow=False)
                b.cyl("Lid", 0.65, 0.12, (x, 0.1 + h + 0.06, 0), R.choice([P["red"], P["gold"], P["black"]]),
                      collide=False, shadow=False)
                x += 0.8
            elif kind < 0.75:
                for k in range(3):
                    b.cyl("Spice", 0.3, 0.6, (x + k * 0.36, 0.4, -0.3 + R.uniform(0, .5)),
                          R.choice([hx("#b71c1c"), hx("#f9a825"), hx("#33691e"), hx("#4e342e")]), collide=False,
                          shadow=False)
                x += 1.2
            else:
                b.cyl("Pot", 1.2, 0.8, (x + 0.3, 0.5, 0), P["steel"], "Metal", refl=0.2, collide=False)
                b.cylx("PotHandle", 0.12, 0.5, (x + 1.05, 0.75, 0), P["black"], collide=False, shadow=False)
                x += 1.6


def heat_lamp(b, name, pos):
    with b.group(name, pos=pos):
        b.part("Housing", (2.8, 0.45, 1.0), (0, 0, 0), hx("#9c2a24"), "Metal", collide=False)
        b.part("Glow", (2.5, 0.08, 0.7), (0, -0.25, 0), [1, 0.45, 0.15], "Neon", collide=False, shadow=False,
               children=[spot_light("Bottom", 9, 1.6, 80, (1, 0.55, 0.25))])


def pot_rack(b, name, pos, length=12):
    x, y, z = pos
    with b.group(name, pos=(x, y, z)):
        for sx in (-length / 2, length / 2):
            for sz in (-1, 1):
                b.cyl("Chain", 0.08, 3, (sx, 1.5, sz), P["black"], "Metal", collide=False, shadow=False)
        for sz in (-1, 1):
            b.cylx("Rail", 0.18, length, (0, 0, sz), P["black"], "Metal", collide=False)
        for sx in (-length / 2, length / 2):
            b.cylz("Rail", 0.18, 2, (sx, 0, 0), P["black"], "Metal", collide=False)
        n = int(length / 1.6)
        for i in range(n):
            px = -length / 2 + 0.9 + i * (length - 1.8) / max(1, n - 1)
            sz = -1 if i % 2 else 1
            d = R.uniform(1.1, 1.6)
            b.cyl("Hook", 0.06, 0.5, (px, -0.25, sz), P["steel_dk"], "Metal", collide=False, shadow=False)
            b.part("Handle", (0.14, 1.0, 0.14), (px, -1.0, sz), P["black"], collide=False, shadow=False)
            col = R.choice([hx("#b87333"), P["steel"], hx("#2b2b2b")])
            b.cylz("Pan", d, 0.25, (px, -1.5 - d / 2, sz), col, "Metal", refl=0.15, collide=False)


def sink_unit(b, name, pos, length, ry=0):
    with b.group(name, pos=pos, ry=ry):
        cabinet(b, "Cabinet", (0, 0, 0), length, body=P["steel"], top=P["steel"], top_mat="Metal")
        for sx in (-length / 4, length / 4):
            b.part("Basin", (length / 2 - 0.8, 0.06, 2.2), (sx, 3.44, -0.1), hx("#7d838a"), "Foil", collide=False,
                   refl=0.3)
            b.part("Drain", (0.4, 0.07, 0.4), (sx, 3.45, -0.1), P["black"], collide=False, shadow=False)
            # robinet
            b.cyl("TapBase", 0.35, 0.4, (sx, 3.6, 1.25), P["steel"], "Metal", refl=0.3, collide=False)
            b.cyl("TapPipe", 0.2, 1.8, (sx, 4.5, 1.25), P["steel"], "Metal", refl=0.3, collide=False)
            b.cylz("TapSpout", 0.2, 1.3, (sx, 5.35, 0.65), P["steel"], "Metal", refl=0.3, collide=False)
            b.cylx("TapLever", 0.12, 0.8, (sx + 0.5, 4.1, 1.25), P["steel_dk"], "Metal", collide=False)


def range_hood(b, name, pos, length, depth=4.8):
    with b.group(name, pos=pos):
        b.part("Hood", (length, 2.4, depth), (0, 0, 0), P["steel"], "Metal", refl=0.15, collide=False)
        b.part("Lip", (length + 0.2, 0.4, 0.3), (0, -1.2, -depth / 2), P["steel_dk"], "Metal", collide=False)
        n = int(length / 4)
        for i in range(n):
            fx = -length / 2 + 2 + i * 4
            b.part("Filter", (3.4, 0.08, depth - 1.2), (fx, -1.22, 0.2), hx("#4a4d52"), "DiamondPlate",
                   collide=False, shadow=False)
            b.part("HoodLight", (1.2, 0.06, 0.6), (fx, -1.25, -depth / 2 + 0.6), [1, 0.95, 0.85], "Neon",
                   collide=False, shadow=False, children=[spot_light("Bottom", 12, 1.3, 90)])
        b.part("Duct", (4, 4.5, 3), (0, 3.4, 0.6), P["steel"], "Metal", collide=False)


def fluorescent(b, name, pos):
    with b.group(name, pos=pos):
        b.part("Frame", (7, 0.25, 1.8), (0, 0, 0), P["white"], "Metal", collide=False)
        b.part("Tube", (6.6, 0.1, 1.4), (0, -0.15, 0), [0.97, 0.98, 1], "Neon", collide=False, shadow=False,
               children=[surface_light("Bottom", 18, 1.1, 120, (0.97, 0.98, 1))])


def bottle(b, pos, col):
    x, y, z = pos
    h = R.uniform(1.0, 1.4)
    b.cyl("Bottle", 0.42, h, (x, y + h / 2, z), col, "Glass", transp=0.15, collide=False, shadow=False, refl=0.1)
    b.cyl("Neck", 0.18, 0.45, (x, y + h + 0.22, z), col, "Glass", transp=0.15, collide=False, shadow=False)


BOTTLE_COLS = [hx("#2e5d32"), hx("#7a4a12"), hx("#c9d6c3"), hx("#5a1b2a"), hx("#b38b2d"), hx("#1e3d59")]


# ---------- extérieur ----------
def street_lamp(b, name, pos, ry=0):
    with b.group(name, pos=pos, ry=ry):
        b.cyl("Base", 1.2, 1.2, (0, 0.6, 0), P["green"], "Metal")
        b.cyl("Pole", 0.45, 12, (0, 6.5, 0), P["green"], "Metal")
        b.cylz("Arm", 0.25, 2.6, (0, 12.2, -1.2), P["green"], "Metal", collide=False)
        b.part("LampTop", (1.4, 0.4, 1.4), (0, 12.4, -2.4), P["green"], "Metal", collide=False)
        b.part("LampGlass", (1.0, 1.2, 1.0), (0, 11.6, -2.4), [1, 0.86, 0.6], "Neon", collide=False, shadow=False,
               transp=0.1, children=[point_light(32, 1.4, WARM)])
        b.part("LampBottom", (1.2, 0.2, 1.2), (0, 10.95, -2.4), P["green"], "Metal", collide=False)


def tree(b, name, pos, size=1.0, planter=True):
    s = size
    with b.group(name, pos=pos):
        if planter:
            b.part("Grate", (4, 0.15, 4), (0, 0.08, 0), hx("#2b2b2b"), "DiamondPlate")
        b.cyl("Trunk", 1.1 * s, 7 * s, (0, 3.5 * s, 0), hx("#5d4330"), "Wood")
        b.cyl("Branch", 0.5 * s, 3 * s, (0.6 * s, 7 * s, 0), hx("#5d4330"), "Wood", rz=-30, collide=False)
        for i in range(8):
            ox, oz = R.uniform(-2.2, 2.2) * s, R.uniform(-2.2, 2.2) * s
            b.ball("Foliage", R.uniform(4, 6.2) * s, (ox, (8 + R.uniform(0, 3.5)) * s, oz),
                   R.choice([P["leaf"], P["leaf2"], P["leaf3"], hx("#5b8f3e")]), "LeafyGrass", collide=False)


def bench(b, name, pos, ry=0):
    with b.group(name, pos=pos, ry=ry):
        for i in range(3):
            b.part("Slat", (6, 0.22, 0.5), (0, 1.8, -0.6 + i * 0.6), P["wood"], "Wood")
        for i in range(2):
            b.part("BackSlat", (6, 0.5, 0.18), (0, 2.7 + i * 0.7, 0.75), P["wood"], "Wood", rx=-10, collide=False)
        for sx in (-2.6, 2.6):
            b.part("Frame", (0.25, 1.8, 2), (sx, 0.9, 0), P["black"], "Metal")
            b.part("BackFrame", (0.25, 2.2, 0.25), (sx, 3.0, 0.8), P["black"], "Metal", collide=False)


def hydrant(b, name, pos):
    with b.group(name, pos=pos):
        b.cyl("Body", 0.9, 2.2, (0, 1.1, 0), hx("#c62828"), "Metal")
        b.ball("Cap", 0.95, (0, 2.25, 0), hx("#c62828"), "Metal", collide=False)
        b.cylx("Nozzle", 0.4, 1.4, (0, 1.5, 0), hx("#b71c1c"), "Metal", collide=False)


def car(b, name, pos, ry, color):
    """Voiture compacte, longueur selon X."""
    with b.group(name, pos=pos, ry=ry):
        b.part("Body", (11, 2.0, 5), (0, 1.9, 0), color, "SmoothPlastic", refl=0.15)
        b.part("Hood", (2.8, 0.5, 4.8), (4.0, 3.1, 0), color, refl=0.15, collide=False)
        b.part("Trunk", (1.8, 0.5, 4.8), (-4.6, 3.1, 0), color, refl=0.15, collide=False)
        b.part("Cabin", (6.2, 2.0, 4.6), (-0.5, 4.0, 0), hx("#1f2a33"), "Glass", transp=0.15, refl=0.3)
        b.part("Roof", (5.2, 0.25, 4.7), (-0.7, 5.1, 0), color, refl=0.15, collide=False)
        b.wedge("Windshield", (4.6, 2.0, 1.2), (3.0, 4.0, 0), hx("#1f2a33"), "Glass", ry=-90, transp=0.15,
                collide=False)
        for sx in (-3.4, 3.4):
            for sz in (-2.3, 2.3):
                b.cylz("Tire", 2.3, 0.9, (sx, 1.15, sz), hx("#151515"), "Rubber", collide=False)
                b.cylz("Rim", 1.3, 0.95, (sx, 1.15, sz), P["steel"], "Metal", collide=False)
        for sz in (-1.7, 1.7):
            b.part("Headlight", (0.15, 0.5, 1.0), (5.55, 2.3, sz), [1, 0.97, 0.85], "Neon", collide=False,
                   shadow=False)
            b.part("Taillight", (0.15, 0.4, 0.9), (-5.55, 2.4, sz), [0.9, 0.1, 0.1], "Neon", collide=False,
                   shadow=False)
        b.part("BumperF", (0.4, 0.6, 5.1), (5.6, 1.2, 0), P["black"], collide=False)
        b.part("BumperR", (0.4, 0.6, 5.1), (-5.6, 1.2, 0), P["black"], collide=False)
        for sz in (-2.6, 2.6):
            b.part("Mirror", (0.4, 0.4, 0.5), (2.0, 3.5, sz), color, collide=False)


def van(b, name, pos, ry, color, text):
    with b.group(name, pos=pos, ry=ry):
        b.part("Cargo", (10, 6.5, 5.6), (-1.5, 4.4, 0), color, refl=0.1,
               children=[text_gui(text, face="Front", color=(0.15, 0.3, 0.2), stroke=1, ppu=30),
                         text_gui(text, face="Back", color=(0.15, 0.3, 0.2), stroke=1, ppu=30)])
        b.part("Cab", (3.6, 4.6, 5.6), (5.3, 3.4, 0), color, refl=0.1)
        b.part("Windshield", (0.2, 2.0, 5.0), (7.15, 4.4, 0), hx("#1f2a33"), "Glass", transp=0.15, refl=0.3,
               collide=False)
        for sz in (-2.81, 2.81):
            b.part("SideWindow", (2.2, 1.8, 0.1), (5.6, 4.4, sz), hx("#1f2a33"), "Glass", transp=0.15, collide=False)
        for sx in (-4.5, 4.8):
            for sz in (-2.5, 2.5):
                b.cylz("Tire", 2.4, 1.0, (sx, 1.2, sz), hx("#151515"), "Rubber", collide=False)
                b.cylz("Rim", 1.3, 1.05, (sx, 1.2, sz), P["steel"], "Metal", collide=False)
        b.part("Bumper", (0.4, 0.7, 5.7), (7.2, 1.4, 0), P["black"], collide=False)
        for sz in (-2.0, 2.0):
            b.part("Headlight", (0.15, 0.5, 0.9), (7.2, 2.4, sz), [1, 0.97, 0.85], "Neon", collide=False,
                   shadow=False)


def flower_box(b, name, pos, length):
    with b.group(name, pos=pos):
        b.part("Box", (length, 0.9, 1.2), (0, 0, 0), P["green"], "Wood", collide=False)
        n = int(length / 0.55)
        for i in range(n):
            fx = -length / 2 + 0.3 + i * 0.55
            b.ball("Leaf", 0.75, (fx, 0.55, R.uniform(-0.25, 0.25)), R.choice([P["leaf"], P["leaf2"]]), "Grass",
                   collide=False, shadow=False)
            if i % 2 == 0:
                b.ball("Bloom", 0.42, (fx + 0.1, 0.95, R.uniform(-0.3, 0.2)),
                       R.choice([hx("#e53950"), hx("#ff8fab"), hx("#fff3b0"), hx("#c77dff")]), collide=False,
                       shadow=False)


def hedge(b, name, size, pos):
    b.part(name, size, pos, hx("#3e6b2f"), "LeafyGrass")


def dumpster(b, name, pos, ry, color):
    with b.group(name, pos=pos, ry=ry):
        b.part("Body", (6, 4, 4), (0, 2.4, 0), color, "Metal")
        b.wedge("Lid", (6.1, 0.8, 4.1), (0, 4.8, 0), shade(color, 0.85), "Metal", ry=180, collide=False)
        for sx in (-2.4, 2.4):
            for sz in (-1.6, 1.6):
                b.cyl("Wheel", 0.6, 0.4, (sx, 0.3, sz), P["black"], "Rubber", collide=False)

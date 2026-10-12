"""Petite lib de modélisation : génère des instances Roblox au format Rojo .model.json.

Repère Roblox : Y vers le haut, l'avant d'un objet = -Z local.
Chaque Group applique une transformation (position + rotations en degrés,
ordre CFrame.Angles = Rx*Ry*Rz) à tout ce qu'on y ajoute.
"""
import json
import math
import random

R = random.Random(42)


# ---------- maths ----------
def _rx(a):
    c, s = math.cos(a), math.sin(a)
    return [[1, 0, 0], [0, c, -s], [0, s, c]]


def _ry(a):
    c, s = math.cos(a), math.sin(a)
    return [[c, 0, s], [0, 1, 0], [-s, 0, c]]


def _rz(a):
    c, s = math.cos(a), math.sin(a)
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]]


def mmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def mvec(m, v):
    return [sum(m[i][k] * v[k] for k in range(3)) for i in range(3)]


def angles(rx=0, ry=0, rz=0):
    return mmul(mmul(_rx(math.radians(rx)), _ry(math.radians(ry))), _rz(math.radians(rz)))


I3 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]


def clean(x):
    x = round(x, 4)
    return 0 if x == 0 else x


# ---------- couleurs ----------
def hx(h):
    h = h.lstrip("#")
    return [round(int(h[i:i + 2], 16) / 255, 4) for i in (0, 2, 4)]


def shade(color, f):
    return [round(min(1, max(0, c * f)), 4) for c in color]


# ---------- attributs ----------
def attr_value(v):
    if isinstance(v, bool):
        return {"Bool": v}
    if isinstance(v, (int, float)):
        return {"Float64": float(v)}
    return {"String": str(v)}


class Builder:
    """Construit un arbre d'instances. Utilisation :

        b = Builder("Restaurant")
        with b.group("Table1", pos=(0, 0, 0), ry=90):
            b.part("Top", (4, .4, 4), (0, 3, 0), hx("#8b5a2b"), "Wood")
        b.save("map/Restaurant.model.json")
    """

    def __init__(self, cls="Model"):
        self.root = {"ClassName": cls, "Children": []}
        self.stack = [(self.root, I3, [0, 0, 0])]
        self.count = 0

    # transformation courante
    def _world(self, pos, rot):
        _, m, o = self.stack[-1]
        wp = [o[i] + mvec(m, pos)[i] for i in range(3)]
        wm = mmul(m, rot)
        return wp, wm

    def group(self, name, pos=(0, 0, 0), rx=0, ry=0, rz=0, cls="Model", attrs=None):
        b = self

        class _Ctx:
            def __enter__(self_inner):
                wp, wm = b._world(list(pos), angles(rx, ry, rz))
                inst = {"Name": name, "ClassName": cls, "Children": []}
                if attrs:
                    inst["Properties"] = {"Attributes": {"Attributes": {k: attr_value(v) for k, v in attrs.items()}}}
                b.stack[-1][0]["Children"].append(inst)
                b.stack.append((inst, wm, wp))
                return inst

            def __exit__(self_inner, *a):
                b.stack.pop()

        return _Ctx()

    def folder(self, name):
        return self.group(name, cls="Folder")

    def add(self, inst):
        self.stack[-1][0]["Children"].append(inst)
        return inst

    def part(self, name, size, pos, color, mat="SmoothPlastic", rx=0, ry=0, rz=0,
             shape=None, cls="Part", collide=True, transp=0, refl=0, shadow=True,
             attrs=None, children=None, touch=False, extra=None):
        wp, wm = self._world(list(pos), angles(rx, ry, rz))
        props = {
            "Anchored": True,
            "Size": [clean(s) for s in size],
            "CFrame": {"CFrame": {"position": [clean(v) for v in wp],
                                  "orientation": [[clean(v) for v in row] for row in wm]}},
            "Color": color,
            "Material": mat,
            "TopSurface": "Smooth",
            "BottomSurface": "Smooth",
        }
        if shape:
            props["Shape"] = shape
        if not collide:
            props["CanCollide"] = False
            props["CanQuery"] = bool(attrs)
        if not touch:
            props["CanTouch"] = False
        if transp:
            props["Transparency"] = transp
        if refl:
            props["Reflectance"] = refl
        if not shadow:
            props["CastShadow"] = False
        if attrs:
            props["Attributes"] = {"Attributes": {k: attr_value(v) for k, v in attrs.items()}}
        if extra:
            props.update(extra)
        inst = {"Name": name, "ClassName": cls, "Properties": props}
        if children:
            inst["Children"] = children
        self.count += 1
        return self.add(inst)

    # cylindre vertical (axe Y) : size = (diamètre, hauteur)
    def cyl(self, name, d, h, pos, color, mat="SmoothPlastic", **kw):
        rz = kw.pop("rz", 0) + 90
        return self.part(name, (h, d, d), pos, color, mat, rz=rz, shape="Cylinder", **kw)

    # cylindre horizontal selon X
    def cylx(self, name, d, length, pos, color, mat="SmoothPlastic", **kw):
        return self.part(name, (length, d, d), pos, color, mat, shape="Cylinder", **kw)

    # cylindre horizontal selon Z
    def cylz(self, name, d, length, pos, color, mat="SmoothPlastic", **kw):
        ry = kw.pop("ry", 0) + 90
        return self.part(name, (length, d, d), pos, color, mat, ry=ry, shape="Cylinder", **kw)

    def ball(self, name, d, pos, color, mat="SmoothPlastic", **kw):
        return self.part(name, (d, d, d), pos, color, mat, shape="Ball", **kw)

    def wedge(self, name, size, pos, color, mat="SmoothPlastic", **kw):
        return self.part(name, size, pos, color, mat, cls="WedgePart", **kw)

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.root, f, ensure_ascii=False, separators=(",", ":"))


# ---------- enfants utiles ----------
def point_light(rng=12, brightness=1, color=(1, 0.85, 0.65), shadows=False):
    return {"ClassName": "PointLight", "Properties": {"Range": rng, "Brightness": brightness,
                                                       "Color": list(color), "Shadows": shadows}}


def spot_light(face="Bottom", rng=16, brightness=2, angle=70, color=(1, 0.9, 0.75)):
    return {"ClassName": "SpotLight", "Properties": {"Face": face, "Range": rng, "Brightness": brightness,
                                                      "Angle": angle, "Color": list(color)}}


def surface_light(face="Bottom", rng=14, brightness=1.2, angle=90, color=(1, 1, 1)):
    return {"ClassName": "SurfaceLight", "Properties": {"Face": face, "Range": rng, "Brightness": brightness,
                                                         "Angle": angle, "Color": list(color)}}


def text_gui(text, face="Front", color=(1, 1, 1), font="FredokaOne", stroke=0.6, bg=None, ppu=40,
             light=0, align="Center", rich=False):
    label = {"ClassName": "TextLabel", "Properties": {
        "Size": {"UDim2": [[1, 0], [1, 0]]},
        "BackgroundTransparency": 1 if bg is None else 0,
        "Text": text, "TextScaled": True, "Font": font, "TextColor3": list(color),
        "TextStrokeTransparency": stroke, "TextXAlignment": align, "RichText": rich,
    }}
    if bg is not None:
        label["Properties"]["BackgroundColor3"] = list(bg)
        label["Properties"]["BorderSizePixel"] = 0
    return {"ClassName": "SurfaceGui", "Properties": {"Face": face, "LightInfluence": light,
                                                      "SizingMode": "PixelsPerStud", "PixelsPerStud": ppu},
            "Children": [label]}


def decal(texture, face="Front"):
    return {"ClassName": "Decal", "Properties": {"Texture": texture, "Face": face}}

"""Rendu d'aperçu (z-buffer logiciel) des fichiers map/*.model.json → PNG.

    python tools/preview.py out_dir
Sert uniquement à vérifier la mise en place sans ouvrir Studio.
"""
import glob
import json
import math
import os
import sys

import numpy as np
from PIL import Image

MAP = os.path.join(os.path.dirname(__file__), "..", "map")


def load_parts():
    parts = []

    def walk(node):
        props = node.get("Properties", {})
        if "Size" in props and "CFrame" in props:
            cf = props["CFrame"]["CFrame"]
            parts.append({
                "name": node.get("Name", ""), "cls": node.get("ClassName"),
                "size": np.array(props["Size"], float), "pos": np.array(cf["position"], float),
                "rot": np.array(cf["orientation"], float), "color": np.array(props.get("Color", [0.6, 0.6, 0.6])),
                "shape": props.get("Shape", "Block"), "transp": props.get("Transparency", 0),
                "neon": props.get("Material") == "Neon",
            })
        for c in node.get("Children", []):
            walk(c)

    for f in sorted(glob.glob(os.path.join(MAP, "*.model.json"))):
        walk(json.load(open(f)))
    return parts


def unit_mesh(shape, cls):
    if cls == "WedgePart":
        v = np.array([[-1, -1, -1], [1, -1, -1], [-1, -1, 1], [1, -1, 1], [-1, 1, 1], [1, 1, 1]], float) * 0.5
        tris = [(0, 2, 1), (1, 2, 3), (2, 4, 3), (3, 4, 5), (0, 1, 4), (1, 5, 4), (0, 4, 2), (1, 3, 5)]
        return v, tris
    if shape == "Cylinder":
        n = 10
        v = []
        for x in (-0.5, 0.5):
            for k in range(n):
                a = 2 * math.pi * k / n
                v.append([x, 0.5 * math.cos(a), 0.5 * math.sin(a)])
        tris = []
        for k in range(n):
            k2 = (k + 1) % n
            tris += [(k, k2, n + k), (k2, n + k2, n + k)]
            if 0 < k < n - 1:
                tris += [(0, k + 1, k), (n, n + k, n + k + 1)]
        return np.array(v), tris
    s = 0.5 if shape != "Ball" else 0.42
    v = np.array([[x, y, z] for x in (-s, s) for y in (-s, s) for z in (-s, s)], float)
    q = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    tris = []
    for a, b, c, d in q:
        tris += [(a, b, c), (a, c, d)]
    return v, tris


def render(parts, eye, target, out, w=1280, h=720, fov=60, clip=None, ortho=None):
    eye, target = np.array(eye, float), np.array(target, float)
    fwd = target - eye
    fwd /= np.linalg.norm(fwd)
    up0 = np.array([0, 1, 0.0]) if abs(fwd[1]) < 0.99 else np.array([0, 0, 1.0])
    right = np.cross(fwd, up0)
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    f = 1 / math.tan(math.radians(fov) / 2)
    img = np.zeros((h, w, 3))
    sky = np.linspace(0, 1, h)[:, None]
    img[:] = (np.array([0.98, 0.82, 0.62]) * (1 - sky) + np.array([0.55, 0.7, 0.9]) * sky)[::-1][:, None, :][:, 0:1, :]
    zbuf = np.full((h, w), np.inf)
    light = np.array([-0.4, 0.75, -0.5])
    light /= np.linalg.norm(light)
    cache = {}
    for p in parts:
        if p["transp"] >= 0.5:
            continue
        if clip and not clip(p):
            continue
        key = (p["shape"], p["cls"])
        if key not in cache:
            cache[key] = unit_mesh(*key)
        uv, tris = cache[key]
        verts = (p["rot"] @ (uv * p["size"]).T).T + p["pos"]
        rel = verts - eye
        cx, cy, cz = rel @ right, rel @ up, rel @ fwd
        if ortho:
            sx = (cx / ortho + 1) * w / 2
            sy = (1 - cy / ortho * w / h) * h / 2
            depth = cz
        else:
            if np.all(cz < 0.3):
                continue
            sx = (cx / np.maximum(cz, 1e-3) * f * h / 2) + w / 2
            sy = h / 2 - (cy / np.maximum(cz, 1e-3) * f * h / 2)
            depth = cz
        for t in tris:
            i0, i1, i2 = t
            if not ortho and (cz[i0] < 0.3 or cz[i1] < 0.3 or cz[i2] < 0.3):
                continue
            n = np.cross(verts[i1] - verts[i0], verts[i2] - verts[i0])
            nl = np.linalg.norm(n)
            if nl < 1e-9:
                continue
            n /= nl
            shade = 1.0 if p["neon"] else 0.45 + 0.55 * abs(float(n @ light))
            col = np.clip(p["color"] * shade * (1.4 if p["neon"] else 1), 0, 1)
            xs = np.array([sx[i0], sx[i1], sx[i2]])
            ys = np.array([sy[i0], sy[i1], sy[i2]])
            zs = np.array([depth[i0], depth[i1], depth[i2]])
            x0, x1 = int(max(0, math.floor(xs.min()))), int(min(w - 1, math.ceil(xs.max())))
            y0, y1 = int(max(0, math.floor(ys.min()))), int(min(h - 1, math.ceil(ys.max())))
            if x0 > x1 or y0 > y1:
                continue
            gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            d = (ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2])
            if abs(d) < 1e-9:
                continue
            a = ((ys[1] - ys[2]) * (gx - xs[2]) + (xs[2] - xs[1]) * (gy - ys[2])) / d
            b = ((ys[2] - ys[0]) * (gx - xs[2]) + (xs[0] - xs[2]) * (gy - ys[2])) / d
            c = 1 - a - b
            m = (a >= -1e-4) & (b >= -1e-4) & (c >= -1e-4)
            if not m.any():
                continue
            if ortho:
                z = a * zs[0] + b * zs[1] + c * zs[2]
            else:
                z = 1.0 / (a / zs[0] + b / zs[1] + c / zs[2])
            sub = zbuf[y0:y1 + 1, x0:x1 + 1]
            m &= z < sub
            sub[m] = z[m]
            img[y0:y1 + 1, x0:x1 + 1][m] = col
    # brume
    fog = np.clip((zbuf - 120) / 500, 0, 0.6)[..., None]
    fog[np.isinf(zbuf)] = 0
    img = img * (1 - fog) + np.array([0.93, 0.82, 0.7]) * fog
    Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save(out)
    print("→", out)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    parts = load_parts()
    print(len(parts), "pièces")
    inside = lambda p: not (-41 < p["pos"][0] < 41 and -40 < p["pos"][2] < 22 and p["pos"][1] > 15.4)
    render(parts, (-70, 45, -120), (0, 6, -30), f"{out}/1_aerien.png")
    render(parts, (18, 6, -66), (0, 9, -38), f"{out}/2_facade.png", fov=70)
    render(parts, (6, 6.5, -37), (-8, 4, -14), f"{out}/3_salle.png", fov=80, clip=inside)
    render(parts, (24, 7.5, -3), (-10, 3, 14), f"{out}/4_cuisine.png", fov=80, clip=inside)
    render(parts, (0, 200, -9.01), (0, 0, -9), f"{out}/5_plan.png", w=1200, h=1000, ortho=46,
           clip=lambda p: p["pos"][1] < 14.5 or not (-41 < p["pos"][0] < 41 and -40 < p["pos"][2] < 22))
    render(parts, (0, 120, -200), (0, 0, -70), f"{out}/6_quartier.png", fov=60)

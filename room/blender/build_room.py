"""Builds the room scene from code. Run with Blender's Python module (bpy).

    python build_room.py --out DIR [--stills] [--samples N] [--blend]

Axes: +X east (window), +Y north (bookshelf), -Y south (desk), -X west (door, mirror, rack). Z up. Metres.
"""
import bpy, bmesh, math, random, sys, os, argparse
from mathutils import Vector, Euler, Matrix

ap = argparse.ArgumentParser()
ap.add_argument("--out", default=".")
ap.add_argument("--stills", action="store_true")
ap.add_argument("--samples", type=int, default=64)
ap.add_argument("--res", type=int, default=1280)
ap.add_argument("--views", default="north,east,south,west")
ap.add_argument("--blend", action="store_true")
ap.add_argument("--bake", action="store_true", help="bake light into one texture per group and export room.glb")
ap.add_argument("--bake-res", type=int, default=2048)
ap.add_argument("--bake-samples", type=int, default=48)
ap.add_argument("--only", default="", help="comma list of groups to bake")
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import art, library
art.CACHE = os.path.join(os.path.abspath(args.out), "art")

R = random.Random(7)
W, D, H = 4.1, 3.8, 2.6            # room: x width, y depth, height
HX, HY = W / 2, D / 2

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
COL = scene.collection
GROUP = ["room"]                   # current label group; objects get it as a custom property


# ----------------------------------------------------------------------------- materials
def _principled(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    return m, nt, nt.nodes["Principled BSDF"]


def _set(b, key, val):
    if key in b.inputs:
        b.inputs[key].default_value = val


_cache = {}


def flat(name, color, rough=0.6, metal=0.0, emit=None, emit_strength=0.0, sheen=0.0, bump=0.0, bump_scale=200.0):
    if name in _cache:
        return _cache[name]
    m, nt, b = _principled(name)
    _set(b, "Base Color", (*color, 1))
    _set(b, "Roughness", rough)
    _set(b, "Metallic", metal)
    if sheen:
        _set(b, "Sheen Weight", sheen)
    if emit:
        _set(b, "Emission Color", (*emit, 1))
        _set(b, "Emission Strength", emit_strength)
    if bump:
        tc = nt.nodes.new("ShaderNodeTexCoord")
        n = nt.nodes.new("ShaderNodeTexNoise")
        n.inputs["Scale"].default_value = bump_scale
        n.inputs["Detail"].default_value = 4
        bp = nt.nodes.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = bump
        bp.inputs["Distance"].default_value = 0.002
        nt.links.new(tc.outputs["Object"], n.inputs["Vector"])
        nt.links.new(n.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    _cache[name] = m
    return m


def wood(name, dark, light, axis="x", scale=6.0, rough=0.45, stretch=14.0):
    """Wood with the grain running along `axis` of the object."""
    key = (name, axis)
    if key in _cache:
        return _cache[key]
    m, nt, b = _principled(f"{name}_{axis}")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    s = [scale * stretch] * 3
    s["xyz".index(axis)] = scale
    mp.inputs["Scale"].default_value = s
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = 1.0
    n.inputs["Detail"].default_value = 8
    n.inputs["Roughness"].default_value = 0.62
    n.inputs["Distortion"].default_value = 0.6
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.32
    ramp.color_ramp.elements[0].color = (*dark, 1)
    ramp.color_ramp.elements[1].position = 0.72
    ramp.color_ramp.elements[1].color = (*light, 1)
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.08
    bp.inputs["Distance"].default_value = 0.002
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], n.inputs["Vector"])
    nt.links.new(n.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(n.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    _set(b, "Roughness", rough)
    _cache[key] = m
    return m


def floor_mat():
    m, nt, b = _principled("floorboards")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.offset = 0.37
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Brick Width"].default_value = 1.35
    br.inputs["Row Height"].default_value = 0.115
    br.inputs["Mortar Size"].default_value = 0.0025
    br.inputs["Color1"].default_value = (0.36, 0.20, 0.10, 1)
    br.inputs["Color2"].default_value = (0.50, 0.30, 0.15, 1)
    br.inputs["Mortar"].default_value = (0.06, 0.03, 0.015, 1)
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (3.0, 60.0, 3.0)
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = 1.0
    n.inputs["Detail"].default_value = 8
    n.inputs["Distortion"].default_value = 0.5
    mix = nt.nodes.new("ShaderNodeMixRGB")
    mix.blend_type = "MULTIPLY"
    mix.inputs["Fac"].default_value = 0.75
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.25
    ramp.color_ramp.elements[0].color = (0.45, 0.45, 0.45, 1)
    ramp.color_ramp.elements[1].position = 0.8
    ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.12
    bp.inputs["Distance"].default_value = 0.003
    nt.links.new(tc.outputs["Object"], br.inputs["Vector"])
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], n.inputs["Vector"])
    nt.links.new(n.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(br.outputs["Color"], mix.inputs["Color1"])
    nt.links.new(ramp.outputs["Color"], mix.inputs["Color2"])
    nt.links.new(mix.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(br.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    _set(b, "Roughness", 0.38)
    return m


def strings_mat():
    m, nt, b = _principled("racket_strings")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.offset = 0.0
    br.inputs["Scale"].default_value = 90.0
    br.inputs["Mortar Size"].default_value = 0.012
    br.inputs["Brick Width"].default_value = 0.5
    br.inputs["Row Height"].default_value = 0.5
    nt.links.new(tc.outputs["Object"], br.inputs["Vector"])
    nt.links.new(br.outputs["Fac"], b.inputs["Alpha"])
    _set(b, "Base Color", (0.9, 0.88, 0.8, 1))
    return m


M_OAK = lambda a="x": wood("oak", (0.30, 0.17, 0.08), (0.55, 0.36, 0.19), a)
M_WALNUT = lambda a="x": wood("walnut", (0.11, 0.055, 0.03), (0.27, 0.15, 0.08), a, rough=0.35)
M_PINE = lambda a="x": wood("pine", (0.52, 0.36, 0.19), (0.72, 0.55, 0.33), a, rough=0.5)
M_PLASTER = flat("plaster", (0.80, 0.72, 0.58), rough=0.92, bump=0.25, bump_scale=60)
M_CEIL = flat("ceiling", (0.84, 0.80, 0.70), rough=0.95)
M_TRIM = flat("trim_paint", (0.83, 0.79, 0.68), rough=0.5)
M_BRASS = flat("brass", (0.78, 0.57, 0.24), rough=0.32, metal=1.0)
M_BLACK = flat("black_metal", (0.025, 0.025, 0.028), rough=0.45, metal=0.9)
M_PAPER = flat("paper", (0.86, 0.82, 0.70), rough=0.8)
M_WHITE = flat("white_paper", (0.90, 0.89, 0.84), rough=0.8)
M_CORK = flat("cork", (0.50, 0.33, 0.18), rough=0.95, bump=0.6, bump_scale=300)
M_MIRROR = flat("mirror_glass", (0.9, 0.9, 0.9), rough=0.02, metal=1.0)
M_TERRA = flat("terracotta", (0.55, 0.24, 0.13), rough=0.85, bump=0.2)
M_LEAF = flat("leaf", (0.07, 0.22, 0.07), rough=0.45)
M_CERAMIC = flat("ceramic", (0.85, 0.82, 0.74), rough=0.25)
M_RUBBER = flat("rubber", (0.04, 0.04, 0.04), rough=0.8)


def cloth(name, color, sheen=0.4):
    return flat("cloth_" + name, color, rough=0.9, sheen=sheen, bump=0.5, bump_scale=700)


BOOK_COLORS = [(0.42, 0.07, 0.06), (0.06, 0.10, 0.25), (0.07, 0.20, 0.12), (0.62, 0.42, 0.08), (0.75, 0.68, 0.52),
               (0.03, 0.03, 0.035), (0.72, 0.28, 0.06), (0.05, 0.25, 0.28), (0.30, 0.14, 0.07), (0.55, 0.50, 0.42),
               (0.20, 0.06, 0.16), (0.50, 0.12, 0.10), (0.12, 0.17, 0.30), (0.78, 0.60, 0.22), (0.24, 0.26, 0.20)]


def book_mat(i):
    return flat(f"book_{i}", BOOK_COLORS[i % len(BOOK_COLORS)], rough=0.62)


# ----------------------------------------------------------------------------- geometry helpers
def _finish(name, bm, mat, loc, rot):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    ob = bpy.data.objects.new(name, mesh)
    COL.objects.link(ob)
    if mat:
        mesh.materials.append(mat)
    ob.location = loc
    if rot:
        ob.rotation_euler = Euler(rot)
    ob["group"] = GROUP[0]
    return ob


def box(name, size, loc, mat, bevel=0.004, rot=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]; v.co.y *= size[1]; v.co.z *= size[2]
    b = min(bevel, min(size) * 0.45)
    if b > 0:
        bmesh.ops.bevel(bm, geom=bm.edges[:], offset=b, segments=2, profile=0.5, affect="EDGES")
    return _finish(name, bm, mat, loc, rot)


def cyl(name, r1, r2, h, loc, mat, seg=28, rot=None, caps=True):
    """Cylinder or cone frustum along local Z, centred. r1 bottom, r2 top."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=seg, radius1=r1, radius2=r2, depth=h)
    for f in bm.faces:
        f.smooth = abs(f.normal.z) < 0.95
    for e in bm.edges:
        if len(e.link_faces) == 2 and (e.link_faces[0].smooth != e.link_faces[1].smooth):
            e.smooth = False
    return _finish(name, bm, mat, loc, rot)


def sphere(name, r, loc, mat, scale=(1, 1, 1), rot=None, seg=24):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=r)
    for v in bm.verts:
        v.co.x *= scale[0]; v.co.y *= scale[1]; v.co.z *= scale[2]
    for f in bm.faces:
        f.smooth = True
    return _finish(name, bm, mat, loc, rot)


def prism(name, pts, depth, loc, mat, rot=None, bevel=0.0):
    """Extrudes a 2D outline (local x,z) by `depth` along local y, centred on y."""
    bm = bmesh.new()
    vs = [bm.verts.new((p[0], -depth / 2, p[1])) for p in pts]
    f = bm.faces.new(vs)
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    for v in [g for g in r["geom"] if isinstance(g, bmesh.types.BMVert)]:
        v.co.y += depth
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if bevel:
        bmesh.ops.bevel(bm, geom=bm.edges[:], offset=bevel, segments=2, profile=0.5, affect="EDGES")
    return _finish(name, bm, mat, loc, rot)


def group(name):
    GROUP[0] = name


def image_mat(path, rough=0.6):
    key = ("img", path, rough)
    if key in _cache:
        return _cache[key]
    m, nt, b = _principled("img_" + os.path.basename(path))
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(path)
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    _set(b, "Roughness", rough)
    _cache[key] = m
    return m


def decal(name, w, h, loc, rot, path, rough=0.6):
    """A flat picture, w wide and h tall, facing local -Y. Decals bake into their own sharp texture."""
    bm = bmesh.new()
    vs = [bm.verts.new(c) for c in ((-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2))]
    f = bm.faces.new(vs)
    uv = bm.loops.layers.uv.new("UVMap")
    for loop, co in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        loop[uv].uv = co
    ob = _finish(name, bm, image_mat(path, rough), loc, rot)
    ob["detail"] = 1
    return ob


def skinned_ball(name, r, loc, rot, path):
    bm = bmesh.new()
    bm.loops.layers.uv.new("UVMap")
    bmesh.ops.create_uvsphere(bm, u_segments=40, v_segments=20, radius=r, calc_uvs=True)
    for f in bm.faces:
        f.smooth = True
    ob = _finish(name, bm, image_mat(path, 0.7), loc, rot)
    ob["detail"] = 1
    return ob


UP = lambda yaw=0.0: (-math.pi / 2, 0, math.pi + yaw)      # decal lying flat, read from the north side
SOUTH_WALL = (0, 0, math.pi)                                # decal on the south wall, facing the room


def titled_book(x_left, y_front, z, b):
    """One of Caleb's books, standing with a printed spine. Returns the x of its right side."""
    w, h, d = b["w"], b["h"], b["d"]
    spec = {k: v for k, v in b.items() if k not in ("w", "h", "d")}
    c = Vector((x_left + w / 2, y_front + d / 2, z + h / 2))
    box("own_book", (w, d, h), c, flat("cover_" + spec.get("bg", "#222222"), art.lin(spec.get("bg", "#222222")), rough=0.6), bevel=0.0015)
    box("own_book_pages", (w * 0.8, d * 0.96, h * 0.97), c + Vector((0, 0.005, 0)), M_PAPER, bevel=0)
    decal("spine", w - 0.003, h - 0.003, (c.x, y_front - 0.0004, c.z), None, art.spine(spec, w - 0.003, h - 0.003))
    return x_left + w + 0.0008


def own_shelf(items, x, y_front, z):
    for it in items:
        if "case" not in it:
            x = titled_book(x, y_front, z, it)
            continue
        books = it["books"]
        inner = sum(b["w"] + 0.0008 for b in books)
        hh, dd, t = max(b["h"] for b in books), max(b["d"] for b in books), 0.004
        m = flat("case_" + it["case"], art.lin(it["colour"]), rough=0.7)
        cx = x + t + inner / 2
        box("case_bottom", (inner + 2 * t, dd + 0.01, t), (cx, y_front + dd / 2, z + t / 2), m, bevel=0.001)
        for sx in (x + t / 2, x + t + inner + t / 2):
            box("case_side", (t, dd + 0.01, hh + 0.008), (sx, y_front + dd / 2, z + (hh + 0.008) / 2), m, bevel=0.001)
        if it["case"] == "tolkien":       # a tray with a tall front lip that carries the name
            lip = 0.07
            box("case_lip", (inner + 2 * t, t, lip), (cx, y_front - 0.006, z + lip / 2), m, bevel=0.001)
            decal("case_label", inner, lip - 0.01, (cx, y_front - 0.0086, z + lip / 2), None,
                  art.plate(it["label"], inner, lip - 0.01, it["colour"], library.GOLD, "cinzel", 0.34, 0.04), rough=0.7)
        else:
            box("case_top", (inner + 2 * t, dd + 0.01, t), (cx, y_front + dd / 2, z + hh + 0.008 + t / 2), m, bevel=0.001)
        bx = x + t
        for b in books:
            bx = titled_book(bx, y_front + 0.003, z + t, b)
        x = x + inner + 2 * t + 0.001
    return x



# ----------------------------------------------------------------------------- shell
def build_shell():
    group("room")
    T = 0.28
    fl = box("floor", (W + 2 * T, D + 2 * T, 0.1), (0, 0, -0.05), floor_mat(), bevel=0)
    box("ceiling", (W + 2 * T, D + 2 * T, 0.1), (0, 0, H + 0.05), M_CEIL, bevel=0)
    box("wall_n", (W + 2 * T, T, H), (0, HY + T / 2, H / 2), M_PLASTER, bevel=0)
    box("wall_s", (W + 2 * T, T, H), (0, -HY - T / 2, H / 2), M_PLASTER, bevel=0)
    box("wall_w", (T, D, H), (-HX - T / 2, 0, H / 2), M_PLASTER, bevel=0)
    # east wall with a window opening: y -0.95..0.95, z 0.95..2.28
    wy, z0, z1 = 0.46, 0.95, 2.28
    x = HX + T / 2
    box("wall_e_low", (T, D, z0), (x, 0, z0 / 2), M_PLASTER, bevel=0)
    box("wall_e_top", (T, D, H - z1), (x, 0, (H + z1) / 2), M_PLASTER, bevel=0)
    side = HY - wy
    box("wall_e_l", (T, side, z1 - z0), (x, -wy - side / 2, (z0 + z1) / 2), M_PLASTER, bevel=0)
    box("wall_e_r", (T, side, z1 - z0), (x, wy + side / 2, (z0 + z1) / 2), M_PLASTER, bevel=0)
    # baseboards
    bh, bt = 0.11, 0.018
    box("base_n", (W, bt, bh), (0, HY - bt / 2, bh / 2), M_TRIM)
    box("base_s", (W, bt, bh), (0, -HY + bt / 2, bh / 2), M_TRIM)
    box("base_e", (bt, D, bh), (HX - bt / 2, 0, bh / 2), M_TRIM)
    box("base_w", (bt, 2.63, bh), (-HX + bt / 2, 0.585, bh / 2), M_TRIM)
    # picture rail
    for nm, sz, lc in [("n", (W, 0.02, 0.035), (0, HY - 0.01, 2.46)), ("s", (W, 0.02, 0.035), (0, -HY + 0.01, 2.46)),
                       ("w", (0.02, D, 0.035), (-HX + 0.01, 0, 2.46))]:
        box("rail_" + nm, sz, lc, M_TRIM)

    # window frame and mullions, set at the outside face of the reveal
    group("window")
    fx = HX + T - 0.06
    ft = 0.055
    box("win_frame_top", (0.07, 2 * wy, ft), (fx, 0, z1 - ft / 2), M_TRIM)
    box("win_frame_bot", (0.07, 2 * wy, ft), (fx, 0, z0 + ft / 2), M_TRIM)
    box("win_frame_l", (0.07, ft, z1 - z0 - 2 * ft), (fx, -wy + ft / 2, (z0 + z1) / 2), M_TRIM)
    box("win_frame_r", (0.07, ft, z1 - z0 - 2 * ft), (fx, wy - ft / 2, (z0 + z1) / 2), M_TRIM)
    box("win_mullion_v", (0.05, 0.04, z1 - z0 - 2 * ft), (fx, 0, (z0 + z1) / 2), M_TRIM)
    box("win_mullion_h", (0.045, 2 * wy - 2 * ft, 0.035), (fx, 0, z0 + (z1 - z0) * 0.62), M_TRIM)
    box("win_sill", (T + 0.06, 2 * wy + 0.1, 0.035), (HX + T / 2 - 0.03, 0, z0 + 0.012), M_TRIM)
    # inner casing
    cw = 0.08
    box("win_case_top", (0.02, 2 * wy + 2 * cw, cw), (HX - 0.01, 0, z1 + cw / 2), M_TRIM)
    box("win_case_l", (0.02, cw, z1 - z0), (HX - 0.01, -wy - cw / 2, (z0 + z1) / 2), M_TRIM)
    box("win_case_r", (0.02, cw, z1 - z0), (HX - 0.01, wy + cw / 2, (z0 + z1) / 2), M_TRIM)

    # rug
    group("room")
    box("rug_border", (2.2, 1.5, 0.012), (0.0, 0.0, 0.006), cloth("rug_red", (0.30, 0.05, 0.04), 0.2), bevel=0.003)
    box("rug_band", (2.02, 1.32, 0.013), (0.0, 0.0, 0.0075), cloth("rug_cream", (0.62, 0.52, 0.36), 0.2), bevel=0.002)
    box("rug_field", (1.92, 1.22, 0.014), (0.0, 0.0, 0.009), cloth("rug_navy", (0.06, 0.09, 0.17), 0.2), bevel=0.002)
    box("rug_inner", (1.3, 0.66, 0.015), (0.0, 0.0, 0.0105), cloth("rug_red", (0.30, 0.05, 0.04), 0.2), bevel=0.002)
    box("rug_centre", (0.86, 0.3, 0.016), (0.0, 0.0, 0.012), cloth("rug_cream", (0.62, 0.52, 0.36), 0.2), bevel=0.002)


# ----------------------------------------------------------------------------- small props
def book(x, y, z, w, d, h, ci, axis="up", lean=0.0, yaw=0.0):
    """A book with its spine facing -Y. (x,y,z) is the centre of the bottom of the book."""
    m = book_mat(ci)
    if axis == "up":
        rot = (0, lean, yaw)
        off = Vector((math.sin(lean) * h / 2, 0, math.cos(lean) * h / 2 + abs(math.sin(lean)) * w / 2))
        c = Vector((x, y, z)) + off
        box("book", (w, d, h), c, m, bevel=0.002, rot=rot)
        box("book_pages", (w * 0.78, d * 0.96, h * 0.965), c + Vector((0, 0.006, 0)), M_PAPER, bevel=0, rot=rot)
        if R.random() < 0.55:
            lab = flat("label_gold", (0.75, 0.6, 0.3), rough=0.4) if R.random() < 0.5 else M_PAPER
            lz = (R.random() - 0.3) * h * 0.5
            p = c + Euler(rot).to_matrix() @ Vector((0, -d / 2 - 0.0005, lz))
            box("book_label", (w * 0.8, 0.001, h * R.uniform(0.06, 0.2)), p, lab, bevel=0, rot=rot)
    else:  # lying flat: w is thickness
        box("book", (h, d, w), (x, y, z + w / 2), m, bevel=0.002, rot=(0, 0, yaw))
        box("book_pages", (h * 0.965, d * 0.96, w * 0.78), (x, y + 0.004, z + w / 2), M_PAPER, bevel=0, rot=(0, 0, yaw))


def trophy(x, y, z, s=1.0, mat=None):
    mat = mat or M_BRASS
    box("trophy_base", (0.09 * s, 0.09 * s, 0.035 * s), (x, y, z + 0.0175 * s), M_WALNUT("x"))
    cyl("trophy_stem", 0.012 * s, 0.008 * s, 0.07 * s, (x, y, z + 0.07 * s), mat)
    cyl("trophy_cup", 0.018 * s, 0.05 * s, 0.11 * s, (x, y, z + 0.16 * s), mat)


def frame(name, w, h, loc, rot, mat_frame, mat_inner, t=0.02, border=0.03, picture=None):
    """Picture frame in the local XZ plane, facing local -Y. `picture` is a function (w, h) -> image path."""
    box(name, (w, t, h), loc, mat_frame, rot=rot)
    c = Vector(loc) + Euler(rot).to_matrix() @ Vector((0, -t / 2 - 0.001, 0))
    box(name + "_inner", (w - 2 * border, 0.004, h - 2 * border), c, mat_inner, bevel=0, rot=rot)
    if picture:
        pw, ph = w - 2 * border - 0.004, h - 2 * border - 0.004
        decal(name + "_art", pw, ph, Vector(loc) + Euler(rot).to_matrix() @ Vector((0, -t / 2 - 0.0036, 0)), rot, picture(pw, ph))


def mug(x, y, z, mat=None):
    cyl("mug", 0.038, 0.04, 0.09, (x, y, z + 0.045), mat or M_CERAMIC)
    cyl("mug_coffee", 0.034, 0.034, 0.004, (x, y, z + 0.086), flat("coffee", (0.05, 0.025, 0.01), rough=0.1))
    box("mug_handle", (0.012, 0.035, 0.05), (x, y + 0.05, z + 0.045), mat or M_CERAMIC, bevel=0.005)


def plant(x, y, z, s=1.0):
    cyl("pot", 0.075 * s, 0.1 * s, 0.16 * s, (x, y, z + 0.08 * s), M_TERRA)
    cyl("pot_soil", 0.092 * s, 0.092 * s, 0.01, (x, y, z + 0.152 * s), flat("soil", (0.04, 0.025, 0.015), rough=1))
    for i in range(9):
        a = i * 2.4
        hgt = R.uniform(0.28, 0.5) * s
        tilt = R.uniform(0.05, 0.3)
        r = 0.035 * s
        ob = cyl("leaf", 0.03 * s, 0.004, hgt, (x + math.cos(a) * r, y + math.sin(a) * r, z + 0.15 * s + hgt / 2 * math.cos(tilt)),
                 M_LEAF, seg=8, rot=(tilt * math.sin(a), -tilt * math.cos(a), a))
        ob.scale = (1, 0.25, 1)


# ----------------------------------------------------------------------------- north: bookshelf
def build_bookshelf():
    group("bookshelf")
    bw, bd, bh = 2.8, 0.32, 2.1
    y0 = HY - bd            # front face plane
    yc = HY - bd / 2
    t = 0.03
    levels = [0.09, 0.5, 0.9, 1.3, 1.7]
    box("case_back", (bw, 0.012, bh), (0, HY - 0.008, bh / 2), M_OAK("z"))
    for sx in (-1, 1):
        box("case_side", (t, bd, bh), (sx * (bw / 2 - t / 2), yc, bh / 2), M_OAK("z"))
    divs = [-0.46, 0.46]
    for dx in divs:
        box("case_div", (0.025, bd - 0.02, bh - 0.05), (dx, yc + 0.01, bh / 2), M_OAK("z"))
    box("case_top", (bw + 0.06, bd + 0.03, 0.04), (0, yc - 0.015, bh), M_OAK("x"))
    box("case_plinth", (bw, bd - 0.02, 0.09), (0, yc + 0.01, 0.045), M_OAK("x"))
    for z in levels[1:]:
        box("shelf", (bw - 2 * t, bd - 0.015, 0.025), (0, yc + 0.0075, z - 0.0125), M_OAK("x"))
    bays = [(-bw / 2 + t, divs[0] - 0.0125), (divs[0] + 0.0125, divs[1] - 0.0125), (divs[1] + 0.0125, bw / 2 - t)]

    def row(x0, x1, z, zmax, fill=1.0):
        x = x0 + 0.004
        end = x0 + (x1 - x0) * fill
        while True:
            w = R.uniform(0.022, 0.052)
            if x + w > end:
                break
            h = min(R.uniform(0.19, 0.30), zmax - 0.02)
            d = R.uniform(0.14, 0.21)
            ci = R.randrange(len(BOOK_COLORS))
            book(x + w / 2, y0 + 0.03 + d / 2 + R.uniform(0, 0.02), z, w, d, h, ci)
            x += w + R.uniform(0.0005, 0.002)
        return x

    def stack(xc, z, n):
        zz = z
        for _ in range(n):
            w = R.uniform(0.025, 0.045)
            book(xc + R.uniform(-0.01, 0.01), y0 + 0.15, zz, w, R.uniform(0.15, 0.19), R.uniform(0.21, 0.26),
                 R.randrange(len(BOOK_COLORS)), axis="flat", yaw=R.uniform(-0.08, 0.08))
            zz += w
        return zz

    plan = {  # (level index, bay index) -> content kind
        (4, 0): "books", (4, 1): "trophies", (4, 2): "books_stack",
        (3, 0): "own_list", (3, 1): "own_photo", (3, 2): "radio",
        (2, 0): "globe", (2, 1): "books", (2, 2): "books_lean",
        (1, 0): "books", (1, 1): "books_stack", (1, 2): "books",
        (0, 0): "binders", (0, 1): "books", (0, 2): "box",
    }
    for (li, bi), kind in plan.items():
        z = levels[li]
        zmax = (levels[li + 1] - 0.025 - z) if li + 1 < len(levels) else (bh - 0.02 - z)
        x0, x1 = bays[bi]
        mid = (x0 + x1) / 2
        if kind == "books":
            row(x0, x1, z, zmax)
        elif kind == "own_photo":
            xe = own_shelf(library.PHOTO_SHELF, x0 + 0.03, y0 + 0.035, z)
            box("bookend", (0.006, 0.11, 0.15), (xe + 0.006, y0 + 0.09, z + 0.075), M_BLACK, bevel=0.001)
            box("bookend_foot", (0.09, 0.11, 0.004), (xe + 0.05, y0 + 0.09, z + 0.002), M_BLACK, bevel=0.001)
        elif kind == "own_list":
            xe = own_shelf(library.LIST_SHELF, x0 + 0.012, y0 + 0.035, z)
            box("bookend", (0.006, 0.11, 0.15), (xe + 0.006, y0 + 0.09, z + 0.075), M_BRASS, bevel=0.001)
            # the Kore baseball on a small stand, and the Leland cap
            bx_ = xe + 0.1
            cyl("ball_stand", 0.03, 0.022, 0.012, (bx_, y0 + 0.1, z + 0.006), M_WALNUT("x"))
            skinned_ball("baseball", 0.037, (bx_, y0 + 0.1, z + 0.012 + 0.035), (0.0, 0.0, BALL_YAW), art.baseball("Kore"))
            cap_x, cap_y = xe + 0.29, y0 + 0.17
            capm = flat("cap_black", (0.012, 0.012, 0.014), rough=0.95, sheen=0.05, bump=0.4, bump_scale=700)
            sphere("cap_crown", 0.088, (cap_x, cap_y + 0.012, z + 0.05), capm, scale=(1.0, 0.9, 0.95))
            box("cap_front", (0.125, 0.03, 0.075), (cap_x, cap_y - 0.07, z + 0.058), capm, bevel=0.012, rot=(-0.2, 0, 0))
            box("cap_brim", (0.165, 0.085, 0.007), (cap_x, cap_y - 0.118, z + 0.016), capm, bevel=0.003, rot=(0.06, 0, 0))
            decal("cap_text", 0.092, 0.034, (cap_x, cap_y - 0.0895, z + 0.06), (-0.2, 0, 0), art.cap_front(0.092, 0.034), rough=0.9)
        elif kind == "books_lean":
            xe = row(x0, x1, z, zmax, fill=0.72)
            book(xe + 0.035, y0 + 0.13, z, 0.035, 0.17, min(0.24, zmax - 0.03), R.randrange(15), lean=-0.22)
        elif kind == "books_stack":
            xe = row(x0, x1, z, zmax, fill=0.6)
            top = stack(xe + 0.16, z, 4)
            if li == 4:
                plant(xe + 0.16, y0 + 0.15, top) if False else trophy(xe + 0.16, y0 + 0.15, top, 0.8)
            else:
                sphere("tennis_ball", 0.033, (xe + 0.16, y0 + 0.14, top + 0.033), flat("tennis", (0.62, 0.75, 0.10), rough=0.9, sheen=0.5))
        elif kind == "trophies":
            trophy(mid - 0.3, y0 + 0.16, z, 1.5)
            trophy(mid - 0.05, y0 + 0.14, z, 1.1, flat("silver", (0.7, 0.7, 0.72), rough=0.3, metal=1))
            frame("shelf_photo", 0.2, 0.26, (mid + 0.28, y0 + 0.2, z + 0.128), (-0.14, 0, -0.15), M_WALNUT("z"), flat("photo_bw", (0.35, 0.33, 0.30), rough=0.3))
        elif kind == "radio":
            row(x0, x1, z, zmax, fill=0.42)
            rx = x0 + (x1 - x0) * 0.72
            box("radio", (0.34, 0.16, 0.2), (rx, y0 + 0.14, z + 0.1), M_WALNUT("x"), bevel=0.012)
            box("radio_grill", (0.19, 0.004, 0.15), (rx - 0.055, y0 + 0.058, z + 0.1), cloth("grill", (0.42, 0.34, 0.20), 0.1), bevel=0)
            box("radio_dial", (0.085, 0.004, 0.06), (rx + 0.105, y0 + 0.058, z + 0.135), flat("dial", (0.85, 0.75, 0.5), emit=(1, 0.75, 0.4), emit_strength=0.6), bevel=0)
            for k in range(2):
                cyl("radio_knob", 0.014, 0.012, 0.014, (rx + 0.08 + k * 0.05, y0 + 0.052, z + 0.06), M_BRASS, rot=(math.pi / 2, 0, 0))
        elif kind == "globe":
            row(x0 + 0.42, x1, z, zmax)
            gx = x0 + 0.2
            cyl("globe_base", 0.07, 0.05, 0.02, (gx, y0 + 0.16, z + 0.01), M_WALNUT("x"))
            cyl("globe_stem", 0.008, 0.008, 0.06, (gx, y0 + 0.16, z + 0.05), M_BRASS)
            sphere("globe", 0.115, (gx, y0 + 0.16, z + 0.19), flat("globe_sea", (0.10, 0.22, 0.30), rough=0.35))
            sphere("globe_land", 0.1158, (gx, y0 + 0.16, z + 0.19), flat("globe_land", (0.55, 0.45, 0.25), rough=0.5), scale=(0.72, 0.9, 0.62), rot=(0.3, 0.2, 0.5))
        elif kind == "binders":
            x = x0 + 0.01
            for k in range(6):
                bwid = 0.065
                box("binder", (bwid, 0.25, 0.31), (x + bwid / 2, y0 + 0.16, z + 0.155), flat(f"binder{k % 3}", [(0.03, 0.03, 0.035), (0.08, 0.12, 0.24), (0.36, 0.33, 0.28)][k % 3], rough=0.5), bevel=0.004)
                box("binder_label", (0.04, 0.001, 0.1), (x + bwid / 2, y0 + 0.034, z + 0.2), M_WHITE, bevel=0)
                x += bwid + 0.004
            stack(x + 0.2, z, 3)
        elif kind == "box":
            row(x0, x0 + 0.5, z, zmax)
            box("crate", (0.42, 0.26, 0.26), (x1 - 0.27, y0 + 0.16, z + 0.13), M_PINE("x"), bevel=0.006)
            box("crate_label", (0.14, 0.002, 0.07), (x1 - 0.27, y0 + 0.029, z + 0.15), M_PAPER, bevel=0)
    # on top of the case
    plant(-1.05, yc, bh + 0.02, 0.62)
    box("top_box", (0.5, 0.26, 0.2), (0.9, yc, bh + 0.12), flat("archive_box", (0.36, 0.28, 0.18), rough=0.9), bevel=0.005)
    box("top_box_lid", (0.52, 0.28, 0.05), (0.9, yc, bh + 0.235), flat("archive_box", (0.36, 0.28, 0.18), rough=0.9), bevel=0.005)
    stackz = bh + 0.02
    for _ in range(3):
        w = R.uniform(0.03, 0.05)
        book(0.1, yc, stackz, w, 0.19, 0.27, R.randrange(15), axis="flat", yaw=R.uniform(-0.1, 0.1))
        stackz += w
    # small framed print on the wall left of the case


# ----------------------------------------------------------------------------- east: window nook
def curtain(name, y0, y1, ztop, zbot, x, mat, folds=7, amp=0.035):
    bm = bmesh.new()
    ny, nz = 72, 10
    grid = []
    for i in range(ny + 1):
        u = i / ny
        col = []
        for j in range(nz + 1):
            v = j / nz
            a = amp * (0.55 + 0.45 * v)
            xx = x + a * math.sin(u * folds * 2 * math.pi) + 0.006 * math.sin(u * 37 + v * 5)
            col.append(bm.verts.new((xx, y0 + (y1 - y0) * u, ztop + (zbot - ztop) * v)))
        grid.append(col)
    for i in range(ny):
        for j in range(nz):
            f = bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
            f.smooth = True
    return _finish(name, bm, mat, (0, 0, 0), None)


WEST_FACE = (0, 0, -math.pi / 2)                 # decal on the east wall, facing the room


def build_nook():
    """East wall: a piano on the north half, a window in the middle, a reading chair on the south half."""
    # ---- window dressing
    group("window")
    lin = flat("linen_curtain", (0.80, 0.70, 0.52), rough=0.95, sheen=0.3, bump=0.3, bump_scale=500)
    curtain("curtain_l", -0.86, -0.5, 2.385, 0.9, HX - 0.07, lin, folds=5)
    curtain("curtain_r", 0.5, 0.86, 2.385, 0.9, HX - 0.07, lin, folds=5)
    cyl("curtain_rod", 0.012, 0.012, 1.9, (HX - 0.07, 0, 2.40), M_BRASS, rot=(math.pi / 2, 0, 0))
    for sy in (-1, 1):
        sphere("rod_finial", 0.025, (HX - 0.07, sy * 0.96, 2.40), M_BRASS)
    zz = 0.97
    for k, w in enumerate((0.03, 0.022, 0.035)):  # paperbacks on the sill
        book(HX + 0.13, -0.2, zz, w, 0.11, 0.18, 6 + k * 3, axis="flat", yaw=1.57 + R.uniform(-0.1, 0.1))
        zz += w
    plant(HX + 0.12, 0.2, 0.97, 0.45)
    # the two balls under the window
    skinned_ball("basketball", 0.12, (HX - 0.2, 0.2, 0.12), (0.4, 0.2, 2.2), art.basketball())
    skinned_ball("soccer_ball", 0.11, (HX - 0.3, -0.1, 0.11), (0.5, 0.3, 2.6), art.soccer_ball())

    # ---- piano, north half. It faces west.
    group("piano")
    ebony = flat("piano_black", (0.012, 0.011, 0.01), rough=0.16)
    pw, pd, ph = 1.42, 0.36, 1.2                       # width along y, depth of the case, height
    py = 1.02                                          # centre along the wall
    xb = HX - pd / 2 - 0.02                            # case centre
    xf = HX - pd - 0.02                                # case front face
    box("piano_case", (pd, pw, ph - 0.1), (xb, py, (ph - 0.1) / 2 + 0.1), ebony, bevel=0.006)
    box("piano_lid", (pd + 0.03, pw + 0.03, 0.025), (xb - 0.005, py, ph + 0.0125), ebony, bevel=0.006)
    box("piano_plinth", (pd + 0.02, pw + 0.02, 0.1), (xb, py, 0.05), ebony, bevel=0.006)
    kd = 0.3                                           # key bed sticks out toward the room
    box("piano_keybed", (kd, pw, 0.06), (xf - kd / 2, py, 0.66), ebony, bevel=0.006)
    for sy in (-1, 1):
        box("piano_cheek", (kd, 0.05, 0.14), (xf - kd / 2, py + sy * (pw / 2 - 0.025), 0.75), ebony, bevel=0.006)
        box("piano_leg", (0.07, 0.07, 0.63), (xf - kd + 0.06, py + sy * (pw / 2 - 0.045), 0.315), ebony, bevel=0.008)
    kw = pw - 0.12                                     # the keyboard
    box("piano_keys", (0.145, kw, 0.02), (xf - 0.16, py, 0.7), flat("ivory", (0.82, 0.78, 0.66), rough=0.3), bevel=0.002)
    decal("piano_key_lines", kw - 0.004, 0.14, (xf - 0.16, py, 0.7102), UP(math.pi / 2), art.piano_keys(kw - 0.004, 0.14), rough=0.3)
    step = kw / 52
    for i in range(51):                                # black keys: none after E and B
        if i % 7 in (1, 4):
            continue
        y = py + kw / 2 - (i + 1) * step
        box("piano_black_key", (0.09, step * 0.56, 0.012), (xf - 0.135, y, 0.716), ebony, bevel=0.0015)
    box("piano_fallboard", (0.02, kw, 0.13), (xf - 0.012, py, 0.775), ebony, bevel=0.004, rot=(0, 0.12, 0))
    box("piano_felt", (0.012, kw, 0.012), (xf - 0.082, py, 0.712), flat("felt_red", (0.4, 0.03, 0.03), rough=1), bevel=0)
    box("piano_desk", (0.012, 0.62, 0.24), (xf - 0.03, py, 1.0), ebony, bevel=0.004, rot=(0, 0.16, 0))
    box("piano_desk_ledge", (0.04, 0.62, 0.012), (xf - 0.04, py, 0.875), ebony, bevel=0.003)
    decal("sheet_music", 0.44, 0.3, (xf - 0.043, py, 1.03), (-0.16, 0, -math.pi / 2), art.sheet_music(0.44, 0.3), rough=0.8)
    for k in (-1, 0, 1):
        box("piano_pedal", (0.09, 0.03, 0.012), (xf - 0.06, py + k * 0.09, 0.06), M_BRASS, bevel=0.004, rot=(0, -0.15, 0))
    plate_ = art.plate("H A Y M O R E", 0.2, 0.02, "#030303", library.GOLD, "cinzel", 0.6, 0.1)
    decal("piano_name", 0.2, 0.02, (xf - 0.0245, py, 0.79), (-0.12, 0, -math.pi / 2), plate_, rough=0.3)
    # on top: a metronome, a framed photo, a small lamp
    prism("metronome", [(-0.045, 0), (0.045, 0), (0.016, 0.2), (-0.016, 0.2)], 0.09, (xb, py + 0.45, ph + 0.025), M_WALNUT("z"), bevel=0.004)
    box("metronome_arm", (0.004, 0.004, 0.15), (xb - 0.047, py + 0.45, ph + 0.11), M_BRASS, bevel=0, rot=(0.25, 0, 0))
    frame("piano_photo", 0.2, 0.15, (xb - 0.02, py - 0.42, ph + 0.1), (0.15, 0, -math.pi / 2 + 0.25), M_BRASS, flat("photo_warm", (0.5, 0.4, 0.3), rough=0.3), t=0.012, border=0.016)
    zz = ph + 0.025
    for k, w in enumerate((0.012, 0.02, 0.01)):       # music books lying on the lid
        book(xb, py - 0.05, zz, w, 0.23, 0.31, [4, 9, 14][k], axis="flat", yaw=R.uniform(-0.12, 0.12))
        zz += w
    # bench
    bx_ = xf - kd - 0.33
    box("bench_seat", (0.36, 0.78, 0.05), (bx_, py, 0.47), ebony, bevel=0.008)
    box("bench_pad", (0.33, 0.74, 0.04), (bx_, py, 0.51), flat("bench_leather", (0.07, 0.03, 0.02), rough=0.5), bevel=0.018)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box("bench_leg", (0.04, 0.04, 0.45), (bx_ + sx * 0.14, py + sy * 0.34, 0.225), ebony, bevel=0.006)

    # ---- reading chair, south half
    group("nook")
    leather = flat("chair_leather", (0.30, 0.12, 0.045), rough=0.42, bump=0.25, bump_scale=160)
    cx, cy, yaw = HX - 0.52, -1.06, 0.22               # the chair turns a little toward the room
    rm = Euler((0, 0, yaw)).to_matrix()

    def cp(v):                                         # chair-local: -x is the front (toward the room), y is along the wall
        return Vector((cx, cy, 0)) + rm @ Vector(v)
    rz = (0, 0, yaw)
    box("armchair_base", (0.78, 0.8, 0.22), cp((0, 0, 0.23)), leather, bevel=0.03, rot=rz)
    box("armchair_seat", (0.6, 0.54, 0.15), cp((-0.08, 0, 0.4)), leather, bevel=0.05, rot=rz)
    box("armchair_back", (0.2, 0.62, 0.66), cp((0.28, 0, 0.66)), leather, bevel=0.07, rot=(0, -0.2, yaw))
    for sy in (-1, 1):
        box("armchair_arm", (0.74, 0.16, 0.34), cp((0.0, sy * 0.35, 0.45)), leather, bevel=0.06, rot=rz)
        for sx in (-1, 1):
            cyl("armchair_leg", 0.022, 0.016, 0.12, cp((sx * 0.32, sy * 0.33, 0.06)), M_WALNUT("z"), seg=12)
    box("armchair_pillow", (0.12, 0.4, 0.34), cp((0.12, 0.02, 0.62)), cloth("pillow_cream", (0.72, 0.64, 0.50)), bevel=0.055, rot=(0, -0.3, yaw + 0.1))
    bl = cloth("blanket_plaid", (0.30, 0.08, 0.07))
    box("blanket_over_arm", (0.5, 0.2, 0.04), cp((0.02, -0.35, 0.64)), bl, bevel=0.018, rot=rz)
    box("blanket_drop", (0.5, 0.035, 0.3), cp((0.02, -0.445, 0.5)), bl, bevel=0.015, rot=rz)
    box("blanket_drop_in", (0.5, 0.035, 0.16), cp((0.02, -0.262, 0.57)), bl, bevel=0.015, rot=rz)
    box("footstool", (0.42, 0.5, 0.2), cp((-0.78, 0.05, 0.25)), leather, bevel=0.05, rot=rz)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl("footstool_leg", 0.02, 0.014, 0.15, cp((-0.78 + sx * 0.15, 0.05 + sy * 0.19, 0.075)), M_WALNUT("z"), seg=12)
    # side table by the window with the open book and a mug
    tx, ty = HX - 0.3, -0.45
    cyl("side_table_top", 0.2, 0.2, 0.025, (tx, ty, 0.56), M_WALNUT("x"), seg=40)
    cyl("side_table_stem", 0.02, 0.02, 0.53, (tx, ty, 0.28), M_WALNUT("z"), seg=14)
    cyl("side_table_foot", 0.15, 0.16, 0.02, (tx, ty, 0.01), M_WALNUT("x"), seg=32)
    zt = 0.5725
    box("open_book_l", (0.15, 0.21, 0.018), (tx - 0.02, ty - 0.07, zt + 0.011), M_PAPER, bevel=0.003, rot=(0, 0.1, 1.2))
    box("open_book_cover", (0.16, 0.22, 0.006), (tx - 0.02, ty - 0.07, zt + 0.003), book_mat(1), bevel=0.002, rot=(0, 0, 1.2))
    mug(tx + 0.03, ty + 0.1, zt)
    # El Capitan above the chair
    frame("el_capitan", 0.72, 0.54, (HX - 0.012, -1.25, 1.62), WEST_FACE, M_OAK("x"), M_WHITE, border=0.055, picture=art.el_capitan)
    # floor lamp in the south-east corner, over the reader's shoulder
    lx, ly = HX - 0.22, -1.68
    cyl("lamp_base", 0.12, 0.11, 0.025, (lx, ly, 0.0125), M_BRASS)
    cyl("lamp_pole", 0.011, 0.011, 1.42, (lx, ly, 0.73), M_BRASS)
    shade = flat("lamp_shade", (0.85, 0.68, 0.42), rough=0.9, emit=(1.0, 0.50, 0.18), emit_strength=0.3)
    cyl("lamp_shade", 0.17, 0.11, 0.24, (lx, ly, 1.52), shade, caps=False)
    add_point("floor_lamp_light", (lx, ly, 1.5), (1.0, 0.62, 0.3), 14, 0.07)


# ----------------------------------------------------------------------------- south: desk
def build_desk():
    group("desk")
    dw, dd, dh = 1.55, 0.72, 0.75
    dx = -0.48
    yc = -HY + dd / 2 + 0.02
    box("desk_top", (dw, dd, 0.035), (dx, yc, dh - 0.0175), M_WALNUT("x"), bevel=0.006)
    px = dx + dw / 2 - 0.23                         # drawer pedestal on the right
    box("desk_pedestal", (0.42, dd - 0.06, dh - 0.09), (px, yc, (dh - 0.09) / 2 + 0.055), M_WALNUT("z"))
    for k in range(3):
        z = 0.14 + k * 0.2
        box("drawer", (0.38, 0.016, 0.18), (px, yc + dd / 2 - 0.028, z + 0.09), M_WALNUT("x"), bevel=0.004)
        sphere("drawer_knob", 0.014, (px, yc + dd / 2 - 0.01, z + 0.09), M_BRASS)
    for ly in (-1, 1):
        box("desk_leg", (0.045, 0.045, dh - 0.035), (dx - dw / 2 + 0.05, yc + ly * (dd / 2 - 0.05), (dh - 0.035) / 2), M_WALNUT("z"))
        box("pedestal_foot", (0.045, 0.045, 0.055), (px + 0.17, yc + ly * (dd / 2 - 0.06), 0.0275), M_WALNUT("z"))
        box("pedestal_foot", (0.045, 0.045, 0.055), (px - 0.17, yc + ly * (dd / 2 - 0.06), 0.0275), M_WALNUT("z"))
    box("desk_apron", (dw - 0.5, 0.02, 0.07), (dx - 0.22, yc - dd / 2 + 0.04, dh - 0.07), M_WALNUT("x"))
    box("desk_drawer_thin", (0.7, 0.016, 0.07), (dx - 0.28, yc + dd / 2 - 0.03, dh - 0.072), M_WALNUT("x"))
    sphere("drawer_knob", 0.012, (dx - 0.28, yc + dd / 2 - 0.014, dh - 0.072), M_BRASS)
    z = dh
    # laptop
    alu = flat("laptop_alu", (0.42, 0.42, 0.43), rough=0.35, metal=1.0)
    lx, ly = dx - 0.08, yc + 0.02
    box("laptop_base", (0.33, 0.23, 0.014), (lx, ly, z + 0.007), alu, bevel=0.004)
    box("laptop_keys", (0.28, 0.11, 0.002), (lx, ly - 0.03, z + 0.0145), flat("keys", (0.03, 0.03, 0.03), rough=0.6), bevel=0)
    tilt = -0.28
    sc = Vector((lx, ly - 0.115 - math.sin(-tilt) * 0.11, z + 0.014 + math.cos(tilt) * 0.11))
    box("laptop_lid", (0.33, 0.008, 0.22), sc, alu, bevel=0.003, rot=(tilt, 0, 0))
    scr = flat("laptop_screen", (0.02, 0.02, 0.02), rough=0.15, emit=(0.80, 0.86, 1.0), emit_strength=1.6)
    box("laptop_screen", (0.31, 0.002, 0.2), sc + Euler((tilt, 0, 0)).to_matrix() @ Vector((0, 0.0052, 0)), scr, bevel=0, rot=(tilt, 0, 0))
    # banker's lamp
    bx, by = dx - 0.55, yc - 0.14
    box("banker_base", (0.2, 0.12, 0.022), (bx, by, z + 0.011), M_BRASS, bevel=0.006)
    cyl("banker_stem", 0.009, 0.009, 0.25, (bx, by, z + 0.147), M_BRASS)
    green = flat("banker_glass", (0.02, 0.22, 0.09), rough=0.12, emit=(0.05, 0.6, 0.2), emit_strength=0.5)
    ob = cyl("banker_shade", 0.062, 0.062, 0.26, (bx, by + 0.03, z + 0.3), green, rot=(0, math.pi / 2, 0))
    ob.scale = (0.75, 1.25, 1)
    add_point("banker_light", (bx, by + 0.05, z + 0.2), (1.0, 0.72, 0.4), 9, 0.03)
    # calculator (financial, landscape), legal pad, pen, mug, books, photo
    box("calculator", (0.13, 0.08, 0.014), (dx + 0.22, yc + 0.2, z + 0.007), flat("calc_body", (0.05, 0.04, 0.035), rough=0.4), bevel=0.003, rot=(0, 0, -0.2))
    decal("calc_face", 0.126, 0.076, (dx + 0.22, yc + 0.2, z + 0.0146), UP(-0.2), art.calculator_face(0.126, 0.076), rough=0.4)
    box("legal_pad", (0.21, 0.3, 0.012), (dx + 0.3, yc - 0.03, z + 0.006), flat("legal_yellow", (0.85, 0.72, 0.25), rough=0.8), bevel=0.002, rot=(0, 0, 0.12))
    cyl("pen", 0.004, 0.004, 0.14, (dx + 0.32, yc + 0.0, z + 0.017), M_BLACK, seg=10, rot=(math.pi / 2, 0, 0.7))
    mug(dx - 0.35, yc + 0.22, z, flat("mug_navy", (0.05, 0.08, 0.2), rough=0.25))
    cyl("pen_cup", 0.04, 0.04, 0.1, (dx + 0.62, yc - 0.2, z + 0.05), flat("pen_cup", (0.1, 0.1, 0.1), rough=0.5), caps=True)
    for k in range(5):
        a = k * 1.3
        cyl("pencil", 0.0035, 0.0035, 0.16, (dx + 0.62 + math.cos(a) * 0.015, yc - 0.2 + math.sin(a) * 0.015, z + 0.11),
            flat(f"pencil{k % 2}", [(0.8, 0.55, 0.05), (0.1, 0.1, 0.4)][k % 2]), seg=8, rot=(0.12 * math.cos(a), 0.12 * math.sin(a), 0))
    zz = z
    for k, w in enumerate((0.045, 0.035, 0.03)):
        book(dx + 0.55, yc + 0.02, zz, w, 0.19, 0.26, [0, 12, 4][k], axis="flat", yaw=1.57 + R.uniform(-0.1, 0.1))
        zz += w
    bs = library.BIG_SHORT                                   # The Big Short, cover up, on top of the stack
    box("big_short", (bs["d"], bs["h"], bs["w"]), (dx + 0.55, yc + 0.02, zz + bs["w"] / 2), flat("cover_bigshort", art.lin(bs["bg"]), rough=0.5), bevel=0.002, rot=(0, 0, 0.1))
    box("big_short_pages", (bs["d"] * 0.97, bs["h"] * 0.97, bs["w"] * 0.8), (dx + 0.552, yc + 0.02, zz + bs["w"] / 2), M_PAPER, bevel=0, rot=(0, 0, 0.1))
    decal("big_short_cover", bs["d"] - 0.004, bs["h"] - 0.004, (dx + 0.55, yc + 0.02, zz + bs["w"] + 0.0005), UP(0.1), art.big_short_cover(bs["d"] - 0.004, bs["h"] - 0.004), rough=0.35)
    frame("desk_photo", 0.13, 0.17, (dx - 0.36, yc - 0.24, z + 0.083), (0.2, 0, math.pi + 0.3), M_BRASS, flat("photo_warm", (0.5, 0.4, 0.3), rough=0.3), t=0.012, border=0.014)
    # chair
    cx, cy = dx - 0.12, yc + 0.62
    rz = 0.35
    rm = Euler((0, 0, rz)).to_matrix()

    def cp(v):
        return Vector((cx, cy, 0)) + rm @ Vector(v)
    box("chair_seat", (0.44, 0.42, 0.035), cp((0, 0, 0.45)), M_OAK("x"), bevel=0.01, rot=(0, 0, rz))
    box("chair_cushion", (0.4, 0.38, 0.045), cp((0, 0, 0.49)), cloth("chair_green", (0.10, 0.17, 0.11)), bevel=0.02, rot=(0, 0, rz))
    for sx in (-1, 1):
        box("chair_leg_f", (0.035, 0.035, 0.44), cp((sx * 0.19, -0.18, 0.22)), M_OAK("z"), rot=(0, 0, rz))
        box("chair_leg_b", (0.035, 0.035, 0.95), cp((sx * 0.19, 0.19, 0.475)), M_OAK("z"), rot=(0, 0, rz))
    for zz2 in (0.66, 0.78, 0.9):
        box("chair_slat", (0.38, 0.018, 0.06), cp((0, 0.19, zz2)), M_OAK("x"), rot=(0, 0, rz))
    # wastebasket
    cyl("wastebasket", 0.11, 0.14, 0.3, (dx - dw / 2 - 0.25, -HY + 0.25, 0.15), flat("basket", (0.25, 0.17, 0.09), rough=0.8, bump=0.6, bump_scale=120))
    # on the wall: corkboard, certificates, pennant, clock
    wy_ = -HY + 0.012
    bxc = dx - 0.15
    box("cork_frame", (1.06, 0.022, 0.72), (bxc, wy_, 1.5), M_OAK("x"))
    box("cork", (1.0, 0.006, 0.66), (bxc, wy_ + 0.012, 1.5), M_CORK, bevel=0)
    notes = [M_WHITE, flat("note_yellow", (0.9, 0.8, 0.3)), flat("note_pink", (0.85, 0.5, 0.5)), M_PAPER, flat("note_blue", (0.5, 0.65, 0.8)), flat("photo_bw", (0.35, 0.33, 0.30), rough=0.3)]
    spots = [(-0.36, 0.17, 0.15, 0.2), (-0.14, 0.2, 0.1, 0.1), (0.05, 0.16, 0.21, 0.27), (0.33, 0.2, 0.14, 0.1), (-0.34, -0.14, 0.2, 0.14),
             (-0.1, -0.16, 0.1, 0.1), (0.3, -0.12, 0.16, 0.2), (0.34, 0.05, 0.09, 0.09), (-0.13, 0.03, 0.12, 0.15), (0.12, -0.2, 0.1, 0.07)]
    for i, (sx, sz, w, h) in enumerate(spots):
        rr = R.uniform(-0.12, 0.12)
        box("note", (w, 0.0015, h), (bxc + sx, wy_ + 0.017 + i * 0.0004, 1.5 + sz), notes[i % len(notes)], bevel=0, rot=(0, rr, 0))
        words = {0: ("#e9e6dc", ["read 30 pages", "every day"], True), 2: ("#e3c14a", ["tennis", "7 am"], False), 4: ("#e9e6dc", ["finish", "the book"], True), 6: ("#e6ded0", ["call home"], False)}
        if i in words:
            bgc, lines_, ruled = words[i]
            decal("note_text", w - 0.004, h - 0.004, (bxc + sx, wy_ + 0.0182 + i * 0.0004, 1.5 + sz), (0, -rr, math.pi), art.note(w - 0.004, h - 0.004, bgc, lines_, ruled=ruled))
        sphere("pin", 0.007, (bxc + sx, wy_ + 0.022, 1.5 + sz + h / 2 - 0.015), flat("pin_red", (0.7, 0.05, 0.04), rough=0.3), seg=10)
    cert = flat("certificate", (0.86, 0.82, 0.70), rough=0.7)
    frame("cert_a", 0.34, 0.27, (dx + 0.72, wy_, 1.72), (0, 0, math.pi), M_BLACK, cert,
          picture=lambda w, h: art.certificate(w, h, ["BYU MARRIOTT SCHOOL OF BUSINESS", "First Place", "Marriott Case Competition", "2025"]))
    frame("cert_b", 0.34, 0.27, (dx + 0.72, wy_, 1.38), (0, 0, math.pi), flat("gilt", (0.6, 0.45, 0.2), rough=0.4, metal=1), cert,
          picture=lambda w, h: art.certificate(w, h, ["BALLARD CENTER", "Third Place", "Ballard Center Case Competition", "2025"], seal=(120, 70, 40)))
    felt = cloth("pennant_navy", (0.04, 0.07, 0.2), 0.6)
    prism("pennant", [(0, 0.11), (0.62, 0), (0, -0.11)], 0.004, (dx + 0.26, wy_ + 0.002, 2.24), felt, rot=(0, 0.06, 0))
    box("pennant_band", (0.03, 0.005, 0.22), (dx + 0.276, wy_ + 0.003, 2.239), cloth("pennant_cream", (0.8, 0.72, 0.55)), bevel=0, rot=(0, 0.06, 0))
    ckx = 0.86
    cyl("clock_rim", 0.16, 0.16, 0.04, (ckx, wy_ + 0.01, 2.17), M_BRASS, rot=(math.pi / 2, 0, 0), seg=40)
    cyl("clock_face", 0.145, 0.145, 0.042, (ckx, wy_ + 0.011, 2.17), flat("clock_face", art.lin("#eae2cc"), rough=0.6), rot=(math.pi / 2, 0, 0), seg=40)
    decal("clock_numbers", 0.2, 0.2, (ckx, wy_ + 0.0326, 2.17), SOUTH_WALL, art.clock_face(0.2))
    box("clock_hand_h", (0.012, 0.004, 0.08), (ckx + 0.02, wy_ + 0.034, 2.195), M_BLACK, bevel=0, rot=(0, 0.7, 0))
    box("clock_hand_m", (0.008, 0.004, 0.12), (ckx - 0.035, wy_ + 0.036, 2.205), M_BLACK, bevel=0, rot=(0, -0.9, 0))


def build_desk_wall_extras():
    group("desk")
    wy_ = -HY + 0.012
    # floating shelf above the corkboard
    sx = -0.63
    box("wall_shelf", (1.3, 0.2, 0.03), (sx, -HY + 0.1, 2.02), M_OAK("x"))
    for k in (-1, 1):
        box("wall_shelf_bracket", (0.02, 0.16, 0.12), (sx + k * 0.5, -HY + 0.08, 1.95), M_BLACK)
    xx = sx - 0.6
    for k in range(9):
        w = R.uniform(0.025, 0.045)
        hgt = R.uniform(0.18, 0.25)
        box("book", (w, 0.15, hgt), (xx + w / 2, -HY + 0.1, 2.035 + hgt / 2), book_mat(R.randrange(15)), bevel=0.002)
        xx += w + 0.002
    plant_small = cyl("pot_small", 0.05, 0.065, 0.1, (sx + 0.42, -HY + 0.1, 2.085), M_CERAMIC)
    for i in range(7):
        a = i * 0.9
        sphere("vine_leaf", 0.035, (sx + 0.42 + math.cos(a) * 0.05, -HY + 0.1 + math.sin(a) * 0.04, 2.15 + 0.02 * math.sin(i * 2.1)), M_LEAF, scale=(1, 0.8, 0.35), rot=(0.4 * math.sin(a), 0.4 * math.cos(a), a), seg=10)
    for i in range(6):
        sphere("vine_leaf", 0.03, (sx + 0.5 + 0.012 * math.sin(i), -HY + 0.19, 2.1 - i * 0.07), M_LEAF, scale=(1, 0.35, 0.9), rot=(0, 0.5 * math.sin(i * 1.7), 0), seg=10)
    box("camera_body", (0.13, 0.06, 0.08), (sx + 0.12, -HY + 0.1, 2.075), M_BLACK, bevel=0.008)
    cyl("camera_lens", 0.03, 0.03, 0.05, (sx + 0.12, -HY + 0.15, 2.075), flat("lens", (0.02, 0.02, 0.02), rough=0.2, metal=1), rot=(math.pi / 2, 0, 0))
    # record cabinet with turntable, east of the desk
    cx, cyy = 0.86, -HY + 0.24
    box("cab_top", (0.95, 0.44, 0.03), (cx, cyy, 0.645), M_WALNUT("x"), bevel=0.006)
    box("cab_bottom", (0.95, 0.44, 0.03), (cx, cyy, 0.195), M_WALNUT("x"), bevel=0.006)
    box("cab_back", (0.95, 0.02, 0.45), (cx, cyy - 0.21, 0.42), M_WALNUT("x"), bevel=0)
    for sxk in (-1, 1):
        box("cab_side", (0.03, 0.44, 0.45), (cx + sxk * 0.46, cyy, 0.42), M_WALNUT("z"), bevel=0.004)
    for sxk in (-1, 1):
        for syk in (-1, 1):
            cyl("cab_leg", 0.016, 0.01, 0.18, (cx + sxk * 0.4, cyy + syk * 0.16, 0.09), M_WALNUT("z"), seg=12)
    xx = cx - 0.42
    for k in range(26):
        w = R.uniform(0.006, 0.012)
        box("record_sleeve", (w, 0.3, 0.31), (xx + w / 2, cyy + 0.07, 0.385 + R.uniform(0, 0.004)), book_mat(R.randrange(15)), bevel=0.001, rot=(0, R.uniform(-0.03, 0.03), 0))
        xx += w + 0.003
        if xx > cx + 0.12:
            break
    box("cab_box", (0.22, 0.3, 0.2), (cx + 0.29, cyy + 0.07, 0.33), M_PINE("x"))
    box("turntable", (0.44, 0.36, 0.07), (cx - 0.2, cyy, 0.695), M_OAK("x"), bevel=0.008)
    cyl("platter", 0.15, 0.15, 0.012, (cx - 0.24, cyy, 0.736), flat("platter", (0.3, 0.3, 0.31), rough=0.3, metal=1), seg=48)
    cyl("record", 0.148, 0.148, 0.003, (cx - 0.24, cyy, 0.744), flat("vinyl", (0.01, 0.01, 0.012), rough=0.22), seg=48)
    cyl("record_label", 0.05, 0.05, 0.004, (cx - 0.24, cyy, 0.745), flat("record_label", (0.75, 0.3, 0.1), rough=0.6), seg=32)
    cyl("tonearm", 0.005, 0.005, 0.2, (cx - 0.05, cyy - 0.02, 0.76), M_BRASS, seg=8, rot=(math.pi / 2 - 0.05, 0, 0.35))
    cyl("tonearm_pivot", 0.016, 0.016, 0.03, (cx - 0.02, cyy - 0.11, 0.745), M_BRASS, seg=14)
    zz = 0.66
    for k, w in enumerate((0.03, 0.035, 0.025)):
        book(cx + 0.28, cyy, zz, w, 0.2, 0.27, [9, 2, 13][k], axis="flat", yaw=R.uniform(-0.15, 0.15))
        zz += w
    mug(cx + 0.28, cyy - 0.02, zz, flat("mug_rust", (0.5, 0.18, 0.08), rough=0.3))
    frame("poster_e", 0.56, 0.78, (cx, wy_, 1.52), (0, 0, math.pi), M_OAK("z"), flat("poster_teal", (0.07, 0.22, 0.24), rough=0.7), border=0.025, picture=art.ridge_poster)
    # two prints west of the desk
    frame("print_sw_a", 0.34, 0.44, (-1.74, wy_, 1.7), (0, 0, math.pi), M_BLACK, flat("print_cream", (0.8, 0.74, 0.6), rough=0.7), border=0.05, picture=art.shapes_print)
    frame("print_sw_b", 0.28, 0.28, (-1.74, wy_, 1.24), (0, 0, math.pi), M_OAK("z"), flat("print_rust", (0.5, 0.2, 0.1), rough=0.7), border=0.04, picture=art.court_print)


# ----------------------------------------------------------------------------- west: door, mirror, rack
def build_west():
    x = -HX
    # door (facing west: left is south, so the door is at negative y)
    group("door")
    dy0, dy1, dz = -1.72, -0.82, 2.05
    dyc = (dy0 + dy1) / 2
    cw = 0.09
    box("door_case_l", (0.03, cw, dz), (x + 0.015, dy0 - cw / 2, dz / 2), M_TRIM)
    box("door_case_r", (0.03, cw, dz), (x + 0.015, dy1 + cw / 2, dz / 2), M_TRIM)
    box("door_case_top", (0.03, dy1 - dy0 + 2 * cw, cw), (x + 0.015, dyc, dz + cw / 2), M_TRIM)
    dm = wood("door_wood", (0.16, 0.08, 0.04), (0.34, 0.19, 0.10), "z", rough=0.4)
    box("door_slab", (0.04, dy1 - dy0, dz), (x + 0.012, dyc, dz / 2), dm)
    pw = (dy1 - dy0 - 0.3) / 2
    for r_, (pz, ph) in enumerate([(0.2, 0.55), (0.87, 0.6), (1.59, 0.32)]):
        for c in (-1, 1):
            box("door_panel", (0.014, pw, ph), (x + 0.036, dyc + c * (pw / 2 + 0.045), pz + ph / 2), dm, bevel=0.01)
    cyl("door_rose", 0.03, 0.03, 0.008, (x + 0.038, dy1 - 0.08, 1.0), M_BRASS, rot=(0, math.pi / 2, 0))
    cyl("door_neck", 0.01, 0.01, 0.05, (x + 0.06, dy1 - 0.08, 1.0), M_BRASS, rot=(0, math.pi / 2, 0))
    sphere("door_knob", 0.03, (x + 0.09, dy1 - 0.08, 1.0), M_BRASS, scale=(0.75, 1, 1))
    box("light_switch", (0.006, 0.075, 0.12), (x + 0.004, dy1 + 0.22, 1.2), M_TRIM, bevel=0.003)
    box("switch_toggle", (0.012, 0.012, 0.03), (x + 0.01, dy1 + 0.22, 1.205), M_TRIM, bevel=0.002)
    # leaning floor mirror
    group("mirror")
    my, mw, mh, lean = -0.08, 0.62, 1.72, 0.11
    mc = Vector((x + 0.03 + math.sin(lean) * mh / 2 + 0.02, my, math.cos(lean) * mh / 2))
    rot = (0, lean, 0)
    box("mirror_frame", (0.035, mw, mh), mc, M_WALNUT("z"), bevel=0.008, rot=rot)
    box("mirror_glass", (0.004, mw - 0.09, mh - 0.09), mc + Euler(rot).to_matrix() @ Vector((0.018, 0, 0)), M_MIRROR, bevel=0, rot=rot)

    # clothing rack
    group("rack")
    ry0, ry1, rx, rh = 0.42, 1.5, x + 0.42, 1.68
    for yy in (ry0, ry1):
        cyl("rack_post", 0.014, 0.014, rh, (rx, yy, rh / 2), M_BLACK)
        cyl("rack_foot", 0.014, 0.014, 0.5, (rx, yy, 0.014), M_BLACK, rot=(0, math.pi / 2, 0))
    cyl("rack_rail", 0.014, 0.014, ry1 - ry0 + 0.06, (rx, (ry0 + ry1) / 2, rh), M_BLACK, rot=(math.pi / 2, 0, 0))
    box("rack_shelf", (0.4, ry1 - ry0, 0.018), (rx, (ry0 + ry1) / 2, 0.16), M_PINE("y"))
    garments = [("blazer_navy", (0.035, 0.045, 0.09), 0.78, 0.085, 0.46), ("oxford_white", (0.82, 0.82, 0.80), 0.74, 0.04, 0.42),
                ("oxford_blue", (0.42, 0.55, 0.72), 0.74, 0.04, 0.42), ("flannel_red", (0.42, 0.07, 0.05), 0.72, 0.05, 0.44),
                ("denim", (0.12, 0.20, 0.34), 0.66, 0.07, 0.46), ("polo_white", (0.86, 0.86, 0.84), 0.62, 0.035, 0.42),
                ("sweater_oat", (0.62, 0.52, 0.36), 0.64, 0.075, 0.46), ("jacket_olive", (0.17, 0.19, 0.09), 0.70, 0.08, 0.48)]
    gy = ry0 + 0.1
    step = (ry1 - ry0 - 0.2) / (len(garments) - 1)
    for i, (nm, colr, length, thick, sh_w) in enumerate(garments):
        m = cloth(nm, colr)
        hw = sh_w / 2
        yaw = math.pi / 2 + R.uniform(-0.12, 0.12)      # garment plane across the rail
        pts = [(-hw, -0.06), (-0.06, 0.0), (0.06, 0.0), (hw, -0.06), (hw + 0.012, -length), (-hw - 0.012, -length)]
        top = rh - 0.07
        prism("garment_" + nm, pts, thick, (rx, gy, top), m, rot=(0, 0, yaw), bevel=min(0.015, thick * 0.3))
        for s in (-1, 1):                                # sleeves
            sl = length * R.uniform(0.72, 0.9) if "polo" not in nm else 0.24
            off = Euler((0, 0, yaw)).to_matrix() @ Vector((s * (hw + 0.035), 0, 0))
            box("sleeve_" + nm, (0.085, thick * 0.9, sl), Vector((rx, gy, top - 0.07 - sl / 2)) + off, m, bevel=min(0.02, thick * 0.4), rot=(0, s * 0.09, yaw))
        cyl("hanger_hook", 0.003, 0.003, 0.075, (rx, gy, rh - 0.03), flat("hanger_steel", (0.6, 0.6, 0.6), rough=0.3, metal=1), seg=8)
        prism("hanger", [(-hw, -0.055), (0, 0.005), (hw, -0.055), (hw, -0.07), (0, -0.012), (-hw, -0.07)], 0.012, (rx, gy, top + 0.004), M_PINE("x"), rot=(0, 0, yaw))
        gy += step
    # shoes on the rack shelf: toes point into the room
    def shoe(yy, upper, sole, yaw, tag_text=None):
        m = flat("shoe_" + str(upper), upper, rough=0.75, bump=0.3, bump_scale=900)
        sm = flat("sole_" + str(sole), sole, rough=0.6)
        c = Vector((rx + 0.02, yy, 0.169))
        rm_ = Euler((0, 0, yaw)).to_matrix()
        def taper(ob):                                  # round the toe and narrow the heel, seen from above
            for vtx in ob.data.vertices:
                t = vtx.co.x / 0.14
                vtx.co.y *= (1 - 0.42 * max(0.0, t - 0.25) ** 2 / 0.5625) if t > 0 else (1 - 0.16 * t * t)
        taper(box("shoe_sole", (0.285, 0.104, 0.03), c + Vector((0, 0, 0.015)), sm, bevel=0.012, rot=(0, 0, yaw)))
        prof = [(-0.132, 0.0), (0.138, 0.0), (0.14, 0.018), (0.11, 0.04), (0.05, 0.056), (0.0, 0.092), (-0.04, 0.108), (-0.115, 0.104), (-0.137, 0.075)]
        taper(prism("shoe_upper", prof, 0.092, c + Vector((0, 0, 0.028)), m, rot=(0, 0, yaw), bevel=0.014))
        box("shoe_laces", (0.07, 0.034, 0.006), c + rm_ @ Vector((0.045, 0, 0.088)), flat("laces_" + str(upper), tuple(min(1, v * 1.1) for v in upper), rough=0.9), bevel=0.003, rot=(0, 0.42, yaw))
        box("shoe_opening", (0.085, 0.05, 0.004), c + rm_ @ Vector((-0.06, 0, 0.133)), flat("shoe_inside", (0.02, 0.02, 0.02), rough=1), bevel=0.001, rot=(0, 0, yaw))
        if tag_text:                                    # the black label on the side and on the tongue
            decal("shoe_tag", 0.034, 0.013, c + rm_ @ Vector((-0.07, -0.0468, 0.07)), (0, 0, yaw), art.tag(tag_text, 0.034, 0.013), rough=0.6)
            decal("shoe_tag_tongue", 0.026, 0.011, c + rm_ @ Vector((0.008, 0, 0.128)), (-1.1, 0, yaw + math.pi / 2), art.tag(tag_text, 0.026, 0.011), rough=0.6)
    white, off = (0.86, 0.86, 0.84), (0.9, 0.9, 0.88)
    shoe(ry0 + 0.16, white, off, 0.06, "VANS"); shoe(ry0 + 0.285, white, off, -0.04, "VANS")
    shoe(ry0 + 0.52, (0.16, 0.08, 0.04), (0.5, 0.35, 0.2), 0.03); shoe(ry0 + 0.64, (0.16, 0.08, 0.04), (0.5, 0.35, 0.2), -0.05)
    shoe(ry0 + 0.86, (0.07, 0.09, 0.14), (0.85, 0.84, 0.8), 0.08); shoe(ry0 + 0.98, (0.07, 0.09, 0.14), (0.85, 0.84, 0.8), 0.0)
    # tennis racket leaning between the mirror and the rack: dark green frame with copper at the throat
    ty = 0.31
    tl = 0.2                                            # lean away from the wall
    base = Vector((x + 0.2, ty, 0.0))
    rmat = Euler((0, tl, 0)).to_matrix()
    grip = flat("racket_grip", (0.02, 0.02, 0.02), rough=0.9, bump=0.5, bump_scale=400)
    fr = flat("racket_frame", (0.02, 0.075, 0.05), rough=0.25, metal=0.55)
    copper = flat("racket_copper", (0.42, 0.17, 0.06), rough=0.3, metal=0.7)
    cyl("racket_butt", 0.02, 0.02, 0.012, base + rmat @ Vector((0, 0, 0.006)), flat("butt_cap", (0.8, 0.8, 0.78), rough=0.4), rot=(0, tl, 0), seg=14)
    cyl("racket_handle", 0.0165, 0.0155, 0.19, base + rmat @ Vector((0, 0, 0.107)), grip, rot=(0, tl, 0), seg=8)
    cyl("racket_shaft", 0.013, 0.013, 0.05, base + rmat @ Vector((0, 0, 0.225)), fr, rot=(0, tl, 0), seg=12)
    hz, a_, b_ = 0.535, 0.125, 0.165                    # head centre height, half width, half height
    for sy in (-1, 1):                                  # the open throat: two arms from the shaft to the head
        p0 = Vector((0, sy * 0.008, 0.245))
        p1 = Vector((0, sy * a_ * 0.8, hz - b_ * 0.62))
        mid, dvec = (p0 + p1) / 2, (p1 - p0)
        ob = cyl("racket_throat", 0.0085, 0.0085, dvec.length, base + rmat @ mid, copper, seg=10)
        ob.rotation_euler = (rmat @ dvec.to_track_quat("Z", "Y").to_matrix()).to_euler()
    bpy.ops.mesh.primitive_torus_add(major_radius=a_, minor_radius=0.0095, major_segments=48, minor_segments=10)
    head = bpy.context.object
    head.name = "racket_head"
    head.data.materials.append(fr)
    bpy.ops.object.shade_smooth()
    head.scale = (1, b_ / a_, 1)
    head.rotation_euler = (rmat @ Euler((math.pi / 2, 0, math.pi / 2)).to_matrix()).to_euler()
    head.location = base + rmat @ Vector((0, 0, hz))
    head["group"] = "rack"
    ob = cyl("racket_strings", a_ - 0.006, a_ - 0.006, 0.002, base + rmat @ Vector((0, 0, hz)), strings_mat(), seg=48)
    ob.scale = (1, b_ / a_, 1)
    ob.rotation_euler = head.rotation_euler
    box("racket_bumper", (0.024, 0.16, 0.012), base + rmat @ Vector((0, 0, hz + b_ + 0.002)), flat("bumper", (0.02, 0.02, 0.02), rough=0.6), bevel=0.004, rot=(0, tl, 0))
    ball = flat("tennis", (0.62, 0.75, 0.10), rough=0.9, sheen=0.5)
    sphere("tennis_ball", 0.033, (x + 0.33, 0.27, 0.033), ball)
    sphere("tennis_ball", 0.033, (x + 0.55, 0.2, 0.033), ball)


# ----------------------------------------------------------------------------- outside, lights, camera
def add_point(name, loc, color, watts, radius):
    ld = bpy.data.lights.new(name, "POINT")
    ld.energy = watts
    ld.color = color
    ld.shadow_soft_size = radius
    ob = bpy.data.objects.new(name, ld)
    ob.location = loc
    COL.objects.link(ob)
    return ob


BALL_YAW = -1.57
SUN_TRAVEL = Vector((-1.0, 0.42, -0.26)).normalized()   # direction the sunlight travels


def build_outside():
    group("outside")
    # ground far below (the room is on an upper floor) and layered ridges to the east
    box("ground", (400, 400, 0.2), (150, 0, -6), flat("valley", (0.035, 0.03, 0.022), rough=1), bevel=0)
    layers = [(55, 8, (0.035, 0.03, 0.035)), (85, 15, (0.07, 0.05, 0.07)), (125, 27, (0.14, 0.09, 0.11)), (170, 42, (0.26, 0.16, 0.15))]
    for i, (dist, peak, colr) in enumerate(layers):
        rr = random.Random(20 + i)
        pts = [(-dist * 1.6, -8)]
        n = 90
        ph = [rr.uniform(0, 6.28) for _ in range(4)]
        for k in range(n + 1):
            u = k / n * 6.28
            hgt = peak * (0.55 + 0.22 * math.sin(1.3 * u + ph[0]) + 0.13 * math.sin(3.1 * u + ph[1]) + 0.07 * math.sin(7.3 * u + ph[2]) + 0.03 * math.sin(17 * u + ph[3]))
            pts.append((-dist * 1.6 + k * dist * 3.2 / n, hgt))
        pts.append((dist * 1.6, -8))
        prism(f"ridge_{i}", pts, 0.5, (dist, 0, -6), flat(f"ridge_{i}", colr, rough=1), rot=(0, 0, math.pi / 2))
    # trees close to the window
    for k, (ty, th, tx) in enumerate([]):
        cyl(f"tree_trunk{k}", 0.18, 0.1, th + 6, (tx, ty, (th + 6) / 2 - 6), flat("bark", (0.07, 0.05, 0.03), rough=1), seg=10)
        sphere(f"tree_crown{k}", 1.9, (tx, ty, th - 1.0), flat("foliage", (0.045, 0.055, 0.02), rough=1), scale=(1, 1, 1.5), seg=14)

    world = bpy.data.worlds.new("world")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    bg = nt.nodes["Background"]
    to_sun = -SUN_TRAVEL
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")          # height gradient: horizon haze to zenith
    e = ramp.color_ramp.elements
    e[0].position = 0.0; e[0].color = (1.0, 0.50, 0.20, 1)
    e[1].position = 0.55; e[1].color = (0.16, 0.26, 0.48, 1)
    mid = ramp.color_ramp.elements.new(0.12); mid.color = (0.95, 0.66, 0.42, 1)
    mid2 = ramp.color_ramp.elements.new(0.28); mid2.color = (0.50, 0.52, 0.62, 1)
    nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    dot = nt.nodes.new("ShaderNodeVectorMath"); dot.operation = "DOT_PRODUCT"
    dot.inputs[1].default_value = to_sun
    nrm = nt.nodes.new("ShaderNodeVectorMath"); nrm.operation = "NORMALIZE"
    nt.links.new(tc.outputs["Generated"], nrm.inputs[0])
    nt.links.new(nrm.outputs["Vector"], dot.inputs[0])
    pw = nt.nodes.new("ShaderNodeMath"); pw.operation = "POWER"; pw.use_clamp = True
    pw.inputs[1].default_value = 6.0
    clampn = nt.nodes.new("ShaderNodeMath"); clampn.operation = "MAXIMUM"; clampn.inputs[1].default_value = 0.0
    nt.links.new(dot.outputs["Value"], clampn.inputs[0])
    nt.links.new(clampn.outputs[0], pw.inputs[0])
    glow = nt.nodes.new("ShaderNodeMixRGB"); glow.blend_type = "ADD"
    glow.inputs["Color2"].default_value = (2.6, 1.5, 0.6, 1)
    nt.links.new(pw.outputs[0], glow.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], glow.inputs["Color1"])
    nt.links.new(glow.outputs["Color"], bg.inputs["Color"])
    lp = nt.nodes.new("ShaderNodeLightPath")
    st = nt.nodes.new("ShaderNodeMapRange")
    st.inputs["To Min"].default_value = 1.6
    st.inputs["To Max"].default_value = 0.3
    nt.links.new(lp.outputs["Is Camera Ray"], st.inputs["Value"])
    nt.links.new(st.outputs[0], bg.inputs["Strength"])

    sd = bpy.data.lights.new("sun", "SUN")
    sd.energy = 9.0
    sd.color = (1.0, 0.60, 0.30)
    sd.angle = math.radians(1.6)
    so = bpy.data.objects.new("sun", sd)
    so.rotation_euler = SUN_TRAVEL.to_track_quat("-Z", "Y").to_euler()
    COL.objects.link(so)


VIEWS = {"north": (0, 1), "east": (1, 0), "south": (0, -1), "west": (-1, 0)}


def camera_for(view):
    dx, dy = VIEWS[view]
    cd = bpy.data.cameras.new("cam_" + view)
    cd.lens = 22
    cd.sensor_width = 36
    cd.clip_start = 0.05
    ob = bpy.data.objects.new("cam_" + view, cd)
    back = 0.6
    ob.location = (-dx * back, -dy * back, 1.38)
    ob.rotation_euler = Vector((dx, dy, -0.03)).to_track_quat("-Z", "Y").to_euler()
    COL.objects.link(ob)
    return ob


build_shell()
_n0 = set(o.name for o in scene.objects)
build_bookshelf()
for o in scene.objects:                       # the case is built centred, then moved west to clear the piano
    if o.name not in _n0:
        o.location.x -= 0.2
build_nook()
build_desk()
build_desk_wall_extras()
build_west()
build_outside()

scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = args.samples
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 8
scene.cycles.diffuse_bounces = 5
scene.cycles.sample_clamp_indirect = 8.0
scene.render.resolution_x = args.res
scene.render.resolution_y = int(args.res * 0.625)
scene.view_settings.view_transform = "AgX"
try:
    scene.view_settings.look = "AgX - Medium High Contrast"
except TypeError:
    pass
scene.view_settings.exposure = 1.1

os.makedirs(args.out, exist_ok=True)
if args.blend:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(args.out, "room.blend"))
CLOSE = {"piano": ((0.3, 0.9, 1.35), (2.05, 1.0, 0.95)), "chair": ((0.2, -0.8, 1.35), (2.05, -1.05, 0.95)), "shoes": ((-1.0, 0.75, 0.75), (-1.7, 0.7, 0.2)), "shelf": ((-0.45, 0.75, 1.5), (-0.45, 1.9, 1.5)), "desktop": ((-0.1, -0.75, 1.25), (0.0, -1.9, 0.8)), "deskwall": ((0.2, -0.3, 1.6), (0.2, -1.9, 1.6))}


def close_camera(v):
    eye, look = CLOSE[v]
    cd = bpy.data.cameras.new("cam_" + v)
    cd.lens = 26
    cd.clip_start = 0.05
    ob = bpy.data.objects.new("cam_" + v, cd)
    ob.location = eye
    ob.rotation_euler = (Vector(look) - Vector(eye)).to_track_quat("-Z", "Y").to_euler()
    COL.objects.link(ob)
    return ob


if args.stills:
    for v in args.views.split(","):
        scene.camera = close_camera(v) if v in CLOSE else camera_for(v)
        scene.render.filepath = os.path.join(args.out, f"still_{v}.png")
        bpy.ops.render.render(write_still=True)
        print("RENDERED", v, flush=True)
print("OBJECTS", len(bpy.data.objects))


# ----------------------------------------------------------------------------- bake and export
# Materials the website draws itself, so they stay out of the baked textures.
LIVE = {"mirror_glass": "live_mirror", "laptop_screen": "live_screen", "racket_strings": "live_strings"}
BAKE_SIZE = {"room": 2, "bookshelf": 2, "bookshelf__detail": 2}        # multiplier on --bake-res


def bake_and_export():
    import json, time
    view = bpy.context.view_layer
    groups = {}
    live = []
    for ob in list(scene.objects):
        if ob.type != "MESH":
            continue
        mname = ob.data.materials[0].name if ob.data.materials else ""
        if mname in LIVE:
            ob.name = LIVE[mname] + "_" + ob.get("group", "room")
            live.append(ob)
            continue
        g = ob.get("group", "room")
        groups.setdefault(g + "__detail" if ob.get("detail") else g, []).append(ob)
    merged = {}
    for g, obs in groups.items():
        bpy.ops.object.select_all(action="DESELECT")
        for ob in obs:
            ob.select_set(True)
        view.objects.active = obs[0]
        bpy.ops.object.join()
        m = view.objects.active
        m.name = g
        m.data.name = g
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        merged[g] = m
        print("JOINED", g, len(m.data.polygons), flush=True)
    only = [x for x in args.only.split(",") if x]
    manifest = {"groups": {}, "live": [o.name for o in live]}
    scene.cycles.samples = args.bake_samples
    scene.render.bake.margin = 6
    scene.render.bake.use_clear = True
    for g, m in merged.items():
        if g == "outside":
            continue
        t0 = time.time()
        bpy.ops.object.select_all(action="DESELECT")
        m.select_set(True)
        view.objects.active = m
        # Pictures keep their own UV map ("UVMap"). The bake gets a second map, which becomes the only one on export.
        if "UVMap" not in m.data.uv_layers:
            m.data.uv_layers.new(name="UVMap")
        m.data.uv_layers["UVMap"].active_render = True
        bake_uv = m.data.uv_layers.new(name="bake")
        m.data.uv_layers.active = bake_uv
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        if g.endswith("__detail"):
            # Pictures already have clean UVs. Copy them, size each island by its real area, and pack.
            bpy.ops.object.mode_set(mode="OBJECT")
            buf = [0.0] * (2 * len(m.data.loops))
            m.data.uv_layers["UVMap"].data.foreach_get("uv", buf)
            m.data.uv_layers["bake"].data.foreach_set("uv", buf)
            m.data.uv_layers.active = m.data.uv_layers["bake"]
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_all(action="SELECT")
            bpy.ops.uv.select_all(action="SELECT")
            bpy.ops.uv.average_islands_scale()
            bpy.ops.uv.pack_islands(margin=0.004)
        else:
            bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.0015, area_weight=0.0, scale_to_bounds=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        res = args.bake_res * BAKE_SIZE.get(g, 1)
        manifest["groups"][g] = {"texture": f"{g}.jpg", "size": res, "triangles": sum(len(p.vertices) - 2 for p in m.data.polygons)}
        print("UV", g, round(time.time() - t0, 1), flush=True)
        if only and g not in only:
            continue
        m.data.uv_layers["UVMap"].active_render = True
        m.data.uv_layers.active = m.data.uv_layers["bake"]
        img = bpy.data.images.new("bake_" + g, res, res, alpha=False)
        for slot in m.material_slots:
            nt = slot.material.node_tree
            n = nt.nodes.get("BAKE") or nt.nodes.new("ShaderNodeTexImage")
            n.name = "BAKE"
            n.image = img
            nt.nodes.active = n
        bpy.ops.object.bake(type="COMBINED")
        scene.render.image_settings.file_format = "JPEG"
        scene.render.image_settings.quality = 90
        img.save_render(os.path.join(args.out, f"{g}.jpg"), scene=scene)   # applies the view transform (AgX, exposure)
        print("BAKED", g, res, round(time.time() - t0, 1), flush=True)
    # export geometry only; the website applies the baked textures itself
    for g, m in merged.items():
        if g == "outside":
            continue                      # the outside keeps its materials: it is photographed below
        m.data.materials.clear()
        if "bake" in m.data.uv_layers and "UVMap" in m.data.uv_layers:
            m.data.uv_layers.remove(m.data.uv_layers["UVMap"])
    bpy.ops.object.select_all(action="DESELECT")
    for ob in list(merged.values()) + live:
        if ob.name != "outside":
            ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(args.out, "room.glb"), use_selection=True, export_yup=True,
                              export_apply=True, export_materials="NONE", export_normals=True, export_texcoords=True,
                              export_draco_mesh_compression_enable=False)
    # the view outside: one picture taken from the middle of the room, shown on a plane beyond the window
    for ob in scene.objects:
        if ob.type == "MESH":
            ob.hide_render = ob.name != "outside"
    cd = bpy.data.cameras.new("plate")
    cd.lens = 18
    cd.sensor_width = 36
    cam = bpy.data.objects.new("plate", cd)
    cam.location = (0, 0, 1.4)
    cam.rotation_euler = Vector((1, 0, 0)).to_track_quat("-Z", "Y").to_euler()
    COL.objects.link(cam)
    scene.camera = cam
    scene.cycles.samples = 48
    scene.render.resolution_x = 2048
    scene.render.resolution_y = 1280
    scene.render.image_settings.file_format = "JPEG"
    scene.render.image_settings.quality = 90
    scene.render.filepath = os.path.join(args.out, "outside.jpg")
    bpy.ops.render.render(write_still=True)
    dist = 14.0
    manifest["outside"] = {"texture": "outside.jpg", "eye": [0, 0, 1.4], "distance": dist, "width": 2 * dist * 18 / 18, "height": 2 * dist * 0.625}
    json.dump(manifest, open(os.path.join(args.out, "manifest.json"), "w"), indent=1)
    print("EXPORTED", flush=True)


if args.bake:
    bake_and_export()

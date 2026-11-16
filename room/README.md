# The room

The home page is being rebuilt as a 3D room. This folder holds the scene source.

- `blender/build_room.py` builds the whole room from code with Blender's Python module (`pip install bpy`). It has no binary source files.
- Axes: +X east (window and reading nook), +Y north (bookshelf), -Y south (desk), -X west (door, mirror, clothing rack). Z is up. Units are metres.
- Every object carries a `group` property (`bookshelf`, `nook`, `desk`, `door`, `mirror`, `rack`, `room`, `window`, `outside`). The website uses the group to decide what an object opens.

Render four test views, one for each wall:

```sh
python room/blender/build_room.py --out /tmp/room --stills --samples 72 --res 1440
```

Status: look development. The light bake, the GLB export, and the three.js viewer are not built yet.

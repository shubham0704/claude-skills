# ParaView → Blender Pipeline

Procedure for turning a finite element simulation into a photorealistic animation. This is the workflow behind Flaschel Fig. 4 (the dog-bone tensile-test render).

It exists because ParaView gives you *correct* visualizations — mesh, fields, contours — but its surface rendering is utilitarian. Blender Cycles gives you publication-grade lighting and materials but doesn't speak FEM. The bridge is a per-timestep `.obj` sequence consumed by the **Stop-motion-OBJ** Blender add-on.

## Prerequisites

- ParaView ≥ 5.10
- Blender `4.5`
- Stop-motion-OBJ Blender add-on: <https://github.com/neverhood311/Stop-motion-OBJ>
- Disk space: a 120-frame sequence at moderate mesh resolution is typically 50–500 MB of `.obj` files. Use a scratch directory.

## Stage 1 — Export `.obj` sequence from ParaView

The mesh deforms over time, so each frame's geometry is different — you cannot use a single static mesh.

In ParaView:

1. Load the simulation result (`.pvd`, `.vtu` series, or whatever your solver writes).
2. Apply any filters that should affect the visible surface (e.g. `Extract Surface`, `Warp by Vector` to apply displacements to nodal positions).
3. **File → Save Animation** → choose `.obj` (Wavefront) as the format.
4. Set the frame range and stride. Save into `frames/` with a numbered prefix (e.g. `frame_0001.obj` … `frame_0120.obj`).

Pitfalls:

- If `Save Animation` doesn't offer `.obj`, you need to enable the OBJ writer plugin under **Tools → Manage Plugins**.
- ParaView writes one `.obj` *and* one `.mtl` per frame by default. Keep both — Stop-motion-OBJ ignores the `.mtl` but Blender warns if it's missing.
- The `.obj` files include the deformed surface only. If you also want the *reference* configuration in shot, export it once separately and import as a static mesh.

## Stage 2 — Configure Blender

One-time setup:

1. Open Blender 4.5.
2. **Edit → Preferences → Add-ons → Install** → select the Stop-motion-OBJ `.zip` from GitHub releases.
3. Enable the add-on (checkbox). It now appears under **File → Import → Mesh Sequence**.
4. Save preferences.

## Stage 3 — Import the sequence

1. **File → Import → Mesh Sequence**.
2. **Root Folder**: `frames/`.
3. **File Name Prefix**: `frame_` (or whatever you used).
4. **Cache Mode**: `Streaming` for sequences > 100 MB; `Cached` for shorter sequences (faster scrubbing, more RAM).
5. Click **Load Mesh Sequence**.

Blender creates a single object whose mesh data swaps per frame. The timeline now plays the FEM animation.

## Stage 4 — Material and lighting

Stop-motion-OBJ does not preserve materials from ParaView (the `.mtl` is solver-default and ugly). Apply Blender materials:

- **Surface**: Principled BSDF, base color from the field of interest if you want field visualization, or a neutral gray for a pure-deformation render.
- **Subsurface scattering**: small (0.05–0.15) for a rubbery / soft look — works well for elastomers and biological tissue.
- **Lighting**: three-point setup. Key (warm, ~3500 K, area light at 45°), fill (cool, ~6500 K, opposite side at lower intensity), rim (white, behind the object, picks out silhouette).
- **Background**: HDRI for realism, or a flat dark color (`#0a1230`) for the lecture-slide look.

To map a scalar field (e.g. von Mises stress) to color:

1. In ParaView, before Stage 1, add a `Cell Data to Point Data` filter and bake the field into vertex colors via `Generate Surface Normals` + a custom Python annotation that writes vertex color to `Mesh Quality`.
2. In Blender, the imported mesh has a `Color Attribute` you can plug into the material's `Base Color` via an `Attribute` node (set to `Vertex Color`, name `Col`).

This is fiddly — for a first pass, render geometry only and add fields later.

## Stage 5 — Render

Headless render:

```bash
blender --background --python render.py
```

Where `render.py`:

```python
import bpy

scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.samples = 128       # bump to 512 for the final render
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = 120
scene.render.image_settings.file_format = "FFMPEG"
scene.render.ffmpeg.format = "MPEG4"
scene.render.ffmpeg.codec = "H264"
scene.render.filepath = "//render/animation_"
bpy.ops.render.render(animation=True)
```

Render time scales linearly with frame count and quadratically with sample count. Budget ≈ 5–30 s per frame on a recent GPU (Cycles X with OptiX).

## Common failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| Blender shows only the first frame | Add-on not enabled, or frames imported as separate objects | Re-import via **Mesh Sequence**, not **Wavefront (.obj)** |
| Mesh flickers black | Inconsistent normals across frames | In Blender, with the sequence object selected: **Object Data → Normals → Auto Smooth** |
| Sequence misaligned with camera | ParaView export coordinates differ from Blender's | Apply `Transform → Rotation X = -90°` after import (ParaView is Z-up, Blender is Z-up but obj is Y-up by default) |
| Render is grainy on a smooth mesh | Too few Cycles samples | Bump `cycles.samples` to ≥ 256 |
| Render is fast but flat-looking | Eevee, not Cycles | Check `scene.render.engine == "CYCLES"` |
| Field colors don't appear | Vertex colors didn't survive `.obj` round-trip | Bake field-to-color into the mesh in ParaView before export, or use UV-mapped image textures |

## When to skip Blender

If the simulation result is going into a paper figure that will be printed in greyscale, **don't bother with the Blender render** — a ParaView screenshot with proper labels beats a photoreal render the printer will mangle. Use this pipeline when:

- The output is for a slide deck, lecture video, or web supplement (i.e., color survives).
- Surface geometry is the message (lighting and shading reveal curvature you can't read from contours).
- The figure is the *hero* — first or last figure in the paper, or the cover image.

For everything else, ParaView's native screenshots are fine.

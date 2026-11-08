# Level 3: Blender

Use Blender when the product should look filmed. The user installs it from blender.org and never has to open it: Claude
runs it with no window, using `blender -b -P scene.py -- ...`. The conversation looks the same as the other levels, with
a storyboard, approval and a render, and the render just takes longer.

Find Blender first. Common places are `/Applications/Blender.app/Contents/MacOS/Blender`, `/opt/homebrew/bin/blender` and
`C:\Program Files\Blender Foundation\Blender <version>\blender.exe`.

## Start from the example

`scripts/blender/example_scene.py` is a small working scene. Copy `kit.py`, `tracks.py` and the example next to your
assets, then check it runs before building on it:

```
python3 example_scene.py mesh
blender -b -P example_scene.py -- frames 1280 24 0.5 2 3.5
```

Arguments after `--` are the output folder, width, samples, optionally `flat`, then optional times (leave them out for
every frame). Finished frames are skipped, so a crashed render picks up where it stopped.

## Get the model right first

Wrong shapes are the first thing people notice, and Claude won't notice them unless it compares against a reference.

1. **Use a real model if there is one.** `kit.load_model()` reads GLB, glTF and OBJ. Check the licence if it's going
   to be published.
2. **Otherwise build it with distance functions** in `mesh_from_sdf.py`. This gives clean, smooth surfaces: smooth unions
   for bodies, `revolve()` for caps and bells, `rounded_pocket()` for recesses, smooth cuts for slots.
3. **Study reference from every angle.** Ask for a screen recording of a 3D viewer turning the product, plus wireframes
   if the viewer has them. Pull frames with ffmpeg, crop in at full resolution, and write down proportions and
   details. Screen recordings saved through the floating thumbnail can sit in a protected temp folder, so ask the
   user to save them somewhere normal.
4. **Render check shots next to the reference.** Add a grey world and a few still poses, put them side by side with
   the reference, and go round until they match. It takes seconds, so do this before any animation.

Modelling notes:
- Mirror the second of a pair with a negative scale, then check the left and right are the correct way round.
- Details like vents look proud on a curved surface if placed as flat discs. Use an ellipsoid sunk into the surface with
  a matching curve (depth about `a² / surface radius`).
- Heavy smoothing fills small holes and blurs steps, so smooth small parts less.
- Keep creases and seam lines faint. What looks right as a thin line in a reference often looks too harsh when lit.
- Interior detail matters if the object opens: pockets, hinges, rims. Use the wireframes.
- Check how things fit when closed or moving. Parts can poke through a lid, or stems can cut through a case if they
  rotate on the way out. Move them straight out first, then rotate. Hide anything inside a closed object until it opens.

## Light and camera

- **One light source**: `kit.key_light()`, a big soft area light, with a nearly black world. This makes it look cinematic.
- Use a long lens (about 70–90mm) and let the camera get very close for macro beats.
- Build every move from `tracks.py`, with one curve per move. Render a few frames either side of a handover, as a change
  in speed there reads as a jolt even if the position matches.
- Plan the path to show the detail you care about. Turn the object so its most recognisable feature faces the camera.

## Render settings and time

- Render at 1920 wide with 24 samples and motion blur, then upscale to 4K when compositing. On an M2 Pro this took about
  8 seconds a frame, so about 30 minutes for 8 seconds at 25 fps. Close-ups are slower.
- Test at 1280 wide on about 15 frames for the storyboard, which takes a couple of minutes.
- It's heavy on the GPU and the computer may slow down, so warn the user, and don't run anything else big alongside it.
- Render with a transparent background. That makes it easy to put it on black, on footage, or over text.
- If only the end of an animation changes, re-render only those frames and reuse the rest.

## Flat silhouette version

Pure black and white, no shading, no lines. It's a striking look, and it blends well into silhouetted footage.

Pass `flat` to a scene that calls `kit.flat_mode(black_materials=('grille', 'vent'))`. Everything turns pure white except
the named materials. It renders quickly, as there's no real lighting to calculate, so lower samples are fine.

Keep only the parts that are really black on the product. Hide lettering, status lights, seams and hardware: the
fewer the details, the stronger it looks. Black lines between parts are possible, but they look like a drawing rather
than a silhouette, so offer them only if the shape doesn't read.

A variation that works well: start shaded, flash one inverted frame (a negative of the picture, on a fast movement,
with a shutter sound), and carry on as a flat silhouette.

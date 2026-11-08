# 3D: UI panels in space (gl3d.js)

`scripts/gl3d.js` is a tiny WebGL2 stage. Everything is a flat **panel** whose texture you draw with ordinary 2D-canvas
code, so UI text and icons stay razor sharp, then placed in 3D and seen through a perspective camera. Start from
`templates/template-3d.html`. Render with `--gpu` (headless Chrome has no WebGL2 without it).

## API
```js
const S3 = GL3D.create(width, height);
const tex = S3.texture(canvas);        // tex.update() after redrawing the canvas
S3.render(panels, opts) -> canvas      // draw onto your 2D frame
S3.project([x,y,z], opts) -> [px,py]   // world → screen, for screen-space extras (glows, cursors)
// panel: {tex, w, h, pos:[x,y,z], rot:[rx,ry,rz], scale, alpha, light, bias, blur, sheen, sheenPos, reflect}
// opts:  {eye, target, up?, fov, focus, aperture, fog:{near,far,color}, floorY?, ground?:[panels]}
```
- World units ≈ screen px when the camera is ~1600 from the subject at fov ~34–38. y is up.
- Panels sort back-to-front by depth along the view direction, minus `bias`. Stacked UI on one card (title over body,
  play button over cover) needs a bias (8 for art over a card; 400+ for text that must always sit on top).
- `blur` and `aperture`/`focus` give depth of field by mip bias. `fog` fades distant panels into the background colour.
- `sheen` adds a moving highlight band (glass / glossy cards).
- Rotation order matches the model matrix (Ry·Rx·Rz). To make a panel face the camera: `rx = -asin(dy/|d|)`, `ry = atan2(dx, dz)`.

## Patterns that worked
- **Textures**: one `panel(w, h, pad, draw)` per element with a `redraw(args)` that skips identical args (fast
  per-frame animation of a texture). Supersample textures 2×; draw big screenshots (phone screens) at 2× their pixels.
- **Motion blur**: render 12 sub-frames across a 180° shutter and average them (`alpha = 1/(i+1)`). 5 sub-frames shows
  ghost copies on fast moves.
- **Glow**: a screen-space radial gradient at the projected hero position, drawn before the 3D layer.
- **Morphs in 3D**: animate a panel's texture (circle → rounded square → card) while its 3D position eases to the next
  layout. A card "becomes" a grid tile by shrinking into the tile's slot while the other tiles cascade in around it.
- **Infinite grids**: repeat a 3×3 set of tiles with `mod3(col)`, `mod3(row)` across −3…5; cull tiles behind the
  camera (depth along view < ~90) and off-screen ones by projection.
- **Phones**: screen panel (2× texture), black glass body panel, 12 thin edge slices behind for thickness, a dynamic
  island, a faint glass-reflection panel that slides with rotation. Fade the whole phone away (smooth sine, not a snap)
  as you close in on one icon, and overlay that icon as its own high-res vector panel so it never pixelates.
- **Orbit swap**: orbit the camera round the clicked card; the plane is edge-on when the camera direction is
  perpendicular to its normal (`phi = atan2(dir.z, dir.x)` for a y-axis orbit), which is the frame to swap objects.
- **Audio pulses**: expanding soft rings (a radial-gradient panel) behind the phone, starting the instant it appears.

## Real 3D models (GLB / glTF / FBX / OBJ)
gl3d.js only does flat panels. For true models (a character, a product, a building from Blender or a licensed kit),
build the page with **three.js** instead (pin an exact version from a CDN, e.g. `three@0.160.0` and its `GLTFLoader`),
keep the same page contract, and render with `--gpu`.
- Use models the user owns or is licensed to use. Ask for GLB/glTF with textures (best), or FBX/OBJ. Play built-in animations with `AnimationMixer`, driving
  `mixer.setTime(t)` from `renderAt(t)` so frames are deterministic.
- Light it simply (an environment map + one key light), keep the same camera rules (one continuous move, never
  reversing), and layer flat UI (Figma exports as 4× PNG or SVG) as screen-space overlays or textured planes.
- Can't sculpt a detailed character from scratch to a studio standard: get the model files. Flat renders of 3D can
  still float in 3D as panels, but they won't turn properly.

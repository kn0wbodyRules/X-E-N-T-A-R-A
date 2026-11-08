# Pitfalls (each one happened)

| Symptom | Cause | Fix |
|---|---|---|
| Black / empty frames on a 3D page | headless Chrome without a GPU has no WebGL2 | `--gpu` on every still and render |
| Ghost copies of fast-moving things | too few motion-blur sub-frames | 12 sub-frames over a 180° shutter |
| Text hidden behind a card in 3D | depth sort puts it behind | give overlay panels a `bias` (400+ for text) |
| A morphing curve flips inside out | interpolating to a target with opposite curvature | rise/bend to the rim's curvature first, then travel along it |
| Morphing parts overlap | they travel at different speeds | one shared angle; each part starts when the one ahead is a third away |
| A grid's lines appear and vanish | 1–2 px lines resampled by the shot's push-in | ~3.5 px lines, lower opacity, integer offsets |
| End logo off-centre | the logo PNG's centre isn't its visible centre, and the camera drifts | centre by bounding box; no drift on the end shot |
| Phone side buttons look wrong | hard to place them accurately on a rebuilt phone | leave them off |
| Icon pixelates on the final push | it's part of a screenshot texture | overlay it as its own high-res vector panel |
| Phone fade "snaps" off | an ease that ends fast (inCubic) | a symmetric sine fade over ~1s |
| Cut-out loses a yellow folder / light trousers | enclosed-pocket removal or a flood from the bottom edge | `--keep-pockets` / `--no-bottom` |
| Cut-up layers have missing edges | overlapping objects cut apart | redraw the scene as shapes |
| Gradient on a headline is unreadable | gradient text on a colour field | solid ink on fields; gradients only on dark |
| Posterised motion looks uneven at 25 fps | 25/8 isn't whole | render posterised ads at 24 fps |
| Canvas shadow offset wrong at 4K | shadow offsets ignore the transform | multiply offsets by the render scale |
| A mid-line `//` comment swallowed the code after it | comments in long one-line statements | end-of-line comments only; check stills after edits |
| Two renders fight over a port/profile | shared Chrome ports | render.mjs uses its own port + profile per run |
| The Mac freezes during renders | many parallel 4K encodes | 1–2 renders at a time |
| The screen recording can't be opened | it's still in the protected temp folder from the screenshot thumbnail | ask the user to save it somewhere normal |
| Tips or parts poke through a closed lid | they stick out further than the case allows | hide them until the lid opens, or shrink them slightly as it opens |
| Stems cut through the case | rotating before they've cleared it | fly straight out first, then rotate |
| A kink in a smooth move | two paths joined at a handover | one continuous curve for the whole move (`tracks.py`) |
| Details stand proud on a curved surface | flat discs on a curve | curved ellipsoids sunk into the surface |
| A hole fills in | heavy smoothing, or the surface covering a disc | smooth small parts less; check the disc sits above the floor |
| A white object vanishes on white | no edge between them | a thin dark outline as it reaches the white |
| Hard lines around filled gaps in a frame | the fill stops at the anti-aliased edge | dilate the fill mask a few pixels |
| A render stopped halfway or the computer crashed | it's a heavy job | re-run the same command: finished frames are skipped. Test at 1080 before going higher |
| A blank contact sheet from ffmpeg | `-frames:v N` with `tile` counts sheets, not frames | trim with `-t`, then `tile`, then `-frames:v 1` |

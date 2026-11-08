# 2D: flat illustrations, puppet pins, layers and shape rebuilds

Start from `templates/template-2d.html`. It already has: flat fields with a drifting grid and bottom glow, shape-morph
transitions (flood with the next colour, ease in), word-by-word swipe-up headlines, a push-and-drift camera per shot,
posterised time, line boil and sticker shadows.

## 1. Cut the art out — `scripts/key.py`
`python3 key.py <art.png> <out.png> [--keep-pockets] [--no-bottom]`
Flood-fills the single background colour from the edges, so background-coloured details inside the figure survive.
- `--keep-pockets` when an object is the same colour as the background (a yellow folder on yellow).
- `--no-bottom` when a figure is cut off by the bottom edge and has light clothes (otherwise the fill leaks in).
- Specks are dropped automatically. Check every cut-out over a loud red background before using it.
- Gradient or paper-texture backgrounds don't key: either use the whole image as one layer and puppet it (a smooth
  gradient bends invisibly), or rebuild the scene from shapes.

## 2. Puppet pins (people only) — `scripts/puppet.js`
After Effects-style puppet: a triangle mesh over the cut-out, bent by pins. Each pin has a rigid move (translate,
rotate, scale about a pivot); every vertex blends the pins' moves by inverse distance.
```js
const P = Puppet.create(img, [{x,y}, ...], { cols: 64 });             // pins in image pixels
P.draw(ctx2d, moves, x*SCALE, y*SCALE, s*SCALE, canvas.width, canvas.height);
// moves[i]: { dx, dy, rot, s, ox, oy }   (ox/oy = pivot, e.g. a shoulder for an arm, the neck for the head)
```
- Find pin coordinates with `python3 grid.py cutout.png grid.jpg`.
- Typical rig: hair top, face, neck, each hand, the held object, chest, elbow(s), hips, and **two planted pins on the
  feet/legs** (empty moves) so the figure doesn't drift.
- Motion that reads as alive: a beat-locked gesture (megaphone punch, tablet tap) with a smaller echo after it, the
  head following a frame late, hair lagging the head (same curve, phase-shifted), a tiny breathing bob on the chest.
- Only puppet **people**. Hands holding objects, magnets, cards and folders look better moving as plain layers.
- Sticker shadows work on puppets: set `ctx.shadow*` (offsets in device pixels) before `P.draw`.
- Puppet pages need `--gpu`.

## 3. Layers — `scripts/split.py`
`python3 split.py cutout.png '{"card":[[x,y],...],"ticks":[...]}'` writes same-size layer PNGs plus a `-base.png`, so
parts (two profile cards, motion ticks, a cloud) can slide, wobble and pop on their own. Fine for separate islands.

## 4. Redraw as shapes (preferred for objects)
Cut-up layers leave awkward missing edges where one object overlapped another. When a scene has several overlapping
objects (files in a folder, coins and notes, a cloud and arrow), **redraw it with canvas paths in the original art's
pixel space**: bold `#111` outlines (~6 px at 1080p), flat fills, rounded joins, no gradients on figures. Then every part
is its own layer: files rise out from behind the folder front, wings flap, coins spin (ellipse width = |cos|, rim on
the edge-on side), arrows draw on with a dash offset, clouds pop (fat ink pass first, then white fill, gives one clean
union outline).

## 5. Posterised time and feel
- `tp = floor(t * POST) / POST` for every animation input. 12 poses/s (2 frames at 24 fps) is smooth; 8 is chunkier.
  Render at 24 fps so poses hold an exact number of frames.
- Line boil: offset each layer by a seeded 1–2 px per pose. Sticker shadow: flat, hard, ~16/18 px offset, 25% ink.
- Extras on payoff beats: ink pop bursts (6–10 radial ticks over 3 poses), tick stamps,
  brand-colour confetti with gravity, a glow flash on the logo landing, a light sweep across the wordmark
  (`source-atop` gradient band on an offscreen copy of the logo).

## 6. End card
Pure black (#000), logo dead centre by its visible bounds (no camera drift on this shot), logo slides up through a mask,
tagline word by word with the payoff in the brand gradient, then a small CTA (a search box typing the URL with a
blinking caret works well). Never use a badge or icon the brand doesn't actually use.

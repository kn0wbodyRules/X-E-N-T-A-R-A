# Style rules (and why)

Every rule here came from a designer's notes on real rounds. Apply them to every graphic, not just the one a note was about.

## Story
- A short ad tells one **journey** in 5–10 beats (an app: open → content → browse → choose → use → brand; a marketplace:
  post → found → apply → matched → hired → logo). One beat per VO line.
- Hook in the first second: the brand colour filling the frame, the logo flying in, or a character mid-action.
- Each example in a series should feel different (different camera grammar, different look), not the same move again.
- Slower than you think. First drafts are almost always too fast; give holds room, and slow fast flips by ~50% if
  anyone squints at them.

## Camera
- **One continuous camera** for 3D ads. Fast first, then slow for a long time (exponential ease-out on the opening
  pull-back), then gentle pushes. Never a speed spike mid-move.
- **Direction never reverses** (≤90° turns): no push in then pull out on the same subject, no orbit that settles and
  rotates back. If something must end flat to camera, let a slow drift *arrive* there instead of stopping and turning
  back.
- Exceptions people like: a camera locked on a card while the world loads around it, then moving *backwards through a
  gap in a grid* (the card stays the same size in frame, tiles arrive from the edges, then it slots in); an orbit around
  a card that hides a swap at the moment the card is edge-on (invisible), then reveals the next object.
- Change the angle on long moves (start high-left, swing to high-right while scrolling) so a scroll isn't static.
- Always something moving, never a dead static moment, especially between two big moves.

## Transitions (the heart of it)
- Every shot change is a **shape morph**: the outgoing shot's key object (logo disc, telescope lens, a card, a file, a
  badge) grows to fill the frame and becomes the next shot. Circles ↔ squares ↔ rounded squares.
- Flood the growing shape with the next shot's background colour first, then let the next shot ease in (93% → 100%).
  It reads smoother than revealing the next shot raw.
- Give the source object an **anticipation**: a ~8% squash one pose before it grows.
- Logo constructions should be mechanical and satisfying: pieces hold for a beat, rotate together "on the spot" first,
  then move; parts travelling round a ring move at **one shared speed, evenly spaced**, each becoming an equal third;
  curves keep their curvature (never invert through straight); a stroke can become a card's background in one fluid move
  with no stop between.
- Things that should appear at the same time should: the card becomes the tile *while* the grid loads, not after.

## Depth
- In browser-built 3D, shallow depth of field makes it feel shot on a real camera. Keep the subject sharp and let the background go soft.
- For physical products, light from one source (see `blender.md`).

## Ending
- Spec or not, know what the ad asks the viewer to do, and say it: "On the App Store now", a URL, a sign-up.

## Framing
- Dead centre for the subject (invisible crosshair). Keep end cards perfectly centred: no camera drift on the last shot,
  and centre the logo by its visible bounding box, not the image file's centre.
- Leave room for headlines (top) and any on-screen safe zones the edit needs.

## Text
- The brand's font (e.g. Poppins SemiBold for headlines). Tight tracking (about −3%), sentence case, short, ending in a
  full stop. One payoff phrase in the brand gradient only on dark backgrounds (gradients vanish on colour fields).
- **Animate word by word**: each word fades up from blurred to sharp with a small rise, ~0.06–0.09s stagger, and leaves the
  same way. Avoid a hard reveal line, letter fades, bounces and scale pops. Text on a card title can roll (old line up, new line in from below) behind a
  soft top/bottom fade so it never collides with the line under it.
- A gradient can add polish: solid in the top half of the letters, fading to mid grey at the bottom. If it's too subtle, nobody sees it.
- Keep text away from where things will move, and off any background it would disappear against.
- Taglines/URLs on end cards are small (a third to half the wordmark size) and sit low, centred. A search box that types
  the URL (with a caret) is a good, honest CTA.

## UI and assets
- Real UI beats invented UI. Use the user's screenshots, cleaned: cover profile pictures with a grey placeholder, remove
  personal apps and notification badges, show the right state (playing → pause icon).
- Rebuild anything the camera gets close to as vector (icons, the home screen, wordmarks) so it's sharp at 4K.
- Phones: build them (black glass, thin bezel, titanium or space-black frame with depth slices, dynamic island, subtle
  glass reflection). Skip side buttons unless you can place them exactly.
- Brand illustration systems: cut characters out and puppet them; **redraw objects as shapes** rather than cutting them
  into awkward pieces (see `engine-2d-puppet.md`).
- Spec ads: small disclaimer at the end; never claim to be the brand or reuse their campaign lines.

## Feel
- Posterised time (8–12 poses a second, rendered at 24 fps) gives flat 2D a hand-made animation feel. 12 fps is
  smoother; 8 fps is chunkier. Add line boil (1–2 px jitter per pose) and flat sticker shadows for depth.
- Small celebratory details on payoff beats: ink pop bursts, ticks stamping on, brand-colour confetti, a glow
  flash when the logo lands, a light sweep across the wordmark.
- Avoid: drop shadows that look 2010, lens flares, light-leak packs, ghosted motion blur (use enough sub-frames),
  wiggly bounces on text, glows on everything.

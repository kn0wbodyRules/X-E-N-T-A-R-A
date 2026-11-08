---
name: saas-animation
description: Make short, high-end SaaS, app, product and brand animations (about 8–20s) with Claude, built as code and rendered to 4K video, without any AI video or image generator. Covers storyboards, one continuous camera, shots that transform into each other, real app UI in 3D space, puppet-animated illustrations, photoreal product shots in Blender, flat black and white silhouette looks, blending an ad into real footage, sound design, music prompts and voiceovers. Use this whenever someone asks for a SaaS animation, motion ad, spec ad, product launch video, app promo, logo animation, 3D product shot, "a video for" a brand or product, or wants notes applied to one of these, even if they never say "motion graphics".
---

# SaaS animation

Build a short ad as code, check it frame by frame, render it to 4K, then add sound. Because it's all code, a note like
"slower here" is a quick edit and a re-render, not a re-shoot. Nothing here needs an AI video or image model.

## Pick a level

Match the brief. Each level uses the same workflow and adds one thing.

| Level | Adds | Use it for | Tools |
|---|---|---|---|
| 1. Assets only | Real logo, font, colours, screenshots | Apps and software. Clean UI flying through 3D space, or a game world | `templates/template-3d.html`, three.js for real models. See `references/engine-3d.md` |
| 2. Brand art and voice | Existing illustrations, puppet animation, voiceover, music | Brands with illustrations or characters | `templates/template-2d.html`. See `references/engine-2d-puppet.md` and `references/sound-and-music.md` |
| 3. Blender | Realistic light and a cinematic look. It's free and the user never has to open it, but it renders more slowly | Physical products, or anything that should look shot in a studio | `scripts/blender/`. See `references/blender.md` |

If the ad has to run into real footage, also read `references/into-footage.md`.

## The workflow

1. **Brief and ingredients.** Ask for the product, the audience, the length, whether it needs a voiceover, and where it
   will be seen. Put everything for the ad in one folder. Search that folder and the computer for logos, fonts, colours,
   illustrations and screenshots before inventing anything, and read any brand guidelines.
   - Check resolution. If an asset is too small for how close the camera gets, ask for a better one or rebuild it
     as vector shapes, then compare the rebuild with the original. Don't crop logos out of screenshots, and don't draw a
     logo from memory unless the user agrees and checks it.
   - For physical products, get reference that shows every angle: a 3D viewer turning it, wireframes, or several photos.
2. **Decide the ending.** What should the viewer do next (App Store, website, sign up), or what footage does it cut
   into? The end of the animation is designed backwards from that.
3. **Numbered storyboard, then wait.** 5–10 numbered shots, each with a time range, a frame made with real assets, any
   on-screen line, what moves, and how it turns into the next shot. Fill `templates/storyboard.html` and screenshot it.
   Show it and wait for notes. This is the cheapest place to change anything: nothing has been rendered, so it saves
   usage and time, and the numbers let the user say "the move from 4 into 5 doesn't work".
4. **Build.** Copy the right template and scripts next to the assets. Keep the page contract: canvas `#c`,
   `window.renderAt(t)`, `window.TOTAL`, `window.ready`, `window.EVENTS`, `?t=` for a still, `?scale=2` for 4K. Put every
   beat time in one block at the top, so re-timing is a one-line change.
5. **Review stills as a motion designer.** `node scripts/render.mjs stills page.html out/ 0.5 1.2 …` (add `--gpu` for
   3D), then `python3 scripts/contact_sheet.py out/ sheet.jpg`, and look at it. Check each transition at 3–4 points, not
   just the holds. Compare against real life: Claude won't notice a wrong shape, the wrong left and right, or parts passing
   through each other unless it looks for them. Fix what the rules below would flag before showing anyone.
6. **Render.** `node scripts/render.mjs video page.html "Brand ad - 4K.mp4" --fps 25 --scale 2 [--gpu]`. Use 24 fps for
   posterised animation. Run one or two 4K renders at a time, as more can freeze the computer. Then look at a key-frame sheet:
   `ffmpeg -i ad.mp4 -vf "fps=2,scale=640:-1,tile=4x10" -frames:v 1 sheet.jpg`.
7. **Sound, once the picture is approved.** A changed animation moves every beat. See `references/sound-and-music.md`.
8. **Notes rounds.** Back up the page before each round, apply every note, re-check stills, and report what changed
   in plain words. Save a new version unless the user asks you to replace one, and never delete their files. Be honest
   about what you checked: stills aren't playback, and you can't hear a mix.

**Paid tools:** ElevenLabs, Suno and any other paid service use the user's credits, so generate only when they ask.

## The rules that make it look good

These came from many rounds of a designer's notes. `references/style-rules.md` has the full list and the reasons.

- **Every shot transforms into the next.** No cross dissolves between shots. A shape or object in this shot becomes the
  next one, which keeps the eye in the same place and keeps people engaged. Look at the storyboard and ask how
  this shape can turn into that shape.
- **Keep what matters dead centre,** so the eye never has to go looking for it. Imagine an invisible crosshair.
- **Something is always moving.** It doesn't have to be big: a slow camera push or drift is enough. A still frame feels stale.
- **Direction never suddenly changes.** No zoom in then out, no scale up then down, no orbit that stops and turns back.
  Drive each move with one continuous curve, as a join between two paths shows up as a kink.
- **Fast, then slow for longer.** First drafts are nearly always too quick.
- **Shapes keep their shape.** Curves don't invert mid-morph, and parts moving together keep an even speed and spacing.
- **Text:** the brand font, short lines, sentence case. Each word fades up from blurred to sharp with a small rise,
  with no hard reveal edge. A subtle gradient on the lower half of the letters adds polish. No bounces or scale pops.
- **Light from one source** for 3D and product work. That's most of what makes it look cinematic.
- **Shallow depth of field** makes even browser-built 3D feel filmed: put the background out of focus.
- **Real UI, cleaned up.** Real screenshots or faithful rebuilds, with personal details and notification badges removed.
- **A clear call to action.** "On the App Store now", a URL, a search box. Think about what the viewer does next.
- **Direction beats a clever prompt.** A one-line prompt gives something generic. Ask the user about the idea, the style and
  the personality, and treat their notes as the real work.

## Keep it above board

Check these with the user before anything is published:
- **Brands.** Make ads for brands the user owns or has permission to use. A spec ad for any other brand is a practice or
  portfolio piece: end it with a small "Spec ad. Not affiliated with <brand>." line, don't imitate the brand's real
  campaigns, don't present it as official, and don't run it as paid advertising. Logos and names stay the property of
  their owners.
- **Assets.** Only use footage, images, fonts, sounds, music and 3D models the user made or is licensed to use, and check
  the licence covers this use.
- **Claims.** Everything on screen or in a voiceover must be true and backed up by the user. No guarantees of money or
  results, no invented stats, reviews or badges.
- **Privacy.** Remove personal details from screenshots and footage, and get consent from anyone who appears.

## Where to read more

| When you are… | Read |
|---|---|
| deciding look, motion, transitions, text, endings | `references/style-rules.md` |
| building UI or game worlds in 3D in the browser | `references/engine-3d.md` |
| animating illustrations | `references/engine-2d-puppet.md` |
| making a photoreal product or a flat silhouette version | `references/blender.md` |
| running the ad into real footage | `references/into-footage.md` |
| adding sound, a voiceover or music | `references/sound-and-music.md` |
| something looks wrong | `references/pitfalls.md` |

## Setup

Needs Node 18+, Python 3 with Pillow, numpy, scipy and opencv-python, ffmpeg, and Google Chrome or Chromium. Level 3 also
needs Blender (free from blender.org). Works on Mac and Windows; on Windows use `python` instead of `python3`, and
set the `CHROME` environment variable if Chrome isn't found. If something's missing, say what it is and how to install
it before starting.

## Scripts

- `render.mjs`: stills or 4K video from any page (`--gpu` for WebGL, `--audio` to add sound, `events` to dump the beat list).
- `contact_sheet.py`: tiles stills into one labelled review sheet.
- `key.py`, `split.py`, `grid.py`: cut illustrations out, split them into layers, read off coordinates.
- `gl3d.js`: the WebGL panel engine. `puppet.js`: the puppet-pin mesh warp.
- `mix.py`: places sound effects on the animation's beats and checks the sync. `synth_sfx.py`: builds a free sound kit.
- `blender/`: `kit.py`, `tracks.py`, `mesh_from_sdf.py`, `example_scene.py`.
- `compose_into_clip.py`: runs a transparent render on into real footage.

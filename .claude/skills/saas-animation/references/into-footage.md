# Running an ad into real footage

Use footage the user filmed or has the rights to. Give Claude the first frame of the next clip at the start, and say the animation has to end on it. Claude then designs
the whole ending backwards from that frame.

## Line it up

1. Pull the exact target frame: `ffmpeg -ss <seconds> -i clip.mp4 -frames:v 1 target.png`.
2. Measure the object in the frame: its position, size and angle. Keep these values in one place, then set the final
   pose so that the render lands right on it. Overlay the last render on the target to check, and adjust the pose.
3. Check the frame rate of the clip. Many clips are 24 fps even if named otherwise.
4. Check left and right against the real thing, and which way round the object sits.

## Choose the blend

**Black falls away (object already in place).** The ad is on black, the object shrinks to its target, and the black fades
away to show the frame held still. Then the rendered object melts onto the real one over about 0.5s, and the clip plays.
`scripts/compose_into_clip.py` does exactly this. Also export a version with a transparent end (ProRes 4444) so an editor
can adjust it.

**Pull back from black (object goes into a hand, onto a desk, into a scene).** If there's a silhouette in the next shot,
the black can be that silhouette, enlarged:
- Freeze the target frame, and scale it from huge down to 100%, anchored on a dark area, so white edges creep in as you
  pull back.
- Scale the rendered object at the same rate. If both are locked together, it feels like one move.
- Start the frame further in than the object, then bring the two together, so the screen stays black at first.
- Blend the object's position towards where the frame's matching point will be, so it arrives at the hand from a natural path.
- Paint the real object out of the frame during the pull back, and fill small gaps inside dark shapes. Dilate those
  fills by a few pixels, or a faint outline shows. Bring the real frame back just before the end.
- Use the foreground's dark shape as a mask, so fingers and similar parts pass in front of the rendered object.
- Melt the render into the real object in the last quarter second.
- Give a white object a thin dark outline on a white background, or it vanishes. Check if the footage has one to match.

## Matching looks

Mismatch is what stops things blending. If shaded 3D has to go into flat silhouette footage, make it flat too (see the
silhouette section of `blender.md`), or bright enough to read as flat by the handover. Try several versions and compare
them in motion, as stills won't show you whether a blend works.

## Check it

- Measure the average frame-to-frame difference around the join. A spike means a visible pop.
- Remember the held frame is frozen during the blend, and the clip's motion starts abruptly from still if the
  footage is moving quickly. Tell the user to check this at full speed. Slowing the clip's first few frames can ease it.
- Text must not land on a background the same colour: remove or move any line that would vanish in the white.
- Keep the sound's tail running over the join rather than cutting it at the end of the ad.

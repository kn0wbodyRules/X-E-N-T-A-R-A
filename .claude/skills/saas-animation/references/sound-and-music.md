# Sound design, voiceover and music

Do sound **after** the picture is approved. Visual changes move every beat.

## Sound design — `scripts/mix.py`
1. **Sync from the page, never by hand.** Give the page a `window.EVENTS` list built from the same timing constants
   that drive the animation (`[{name: 'card.open', t: B.card[0]}, …]`, including derived beats: each flip step, each
   landing, pulses, word reveals), then dump it: `node render.mjs events page.html events.json [--gpu]`. Cues then say
   `"event": "card.open"` (plus an optional `"offset"`), so a re-timed animation re-times its sound automatically. For a
   posterised ad pass `--quant 12` (or 8) so each cue lands on the pose where the change first appears.
2. Find the user's sound library (ask, or search for folders of WAVs, e.g. UI packs). Survey it by category
   (`find … | sed` the names, count by prefix) before choosing. A specific set for this ad can go in the ad's folder. A licensed
   library gives the richest sound, so check its licence covers this use. If there's none, `python3 synth_sfx.py sounds/` builds a small free kit, not as rich but
   nothing is downloaded or charged, and you can extend the script with new sounds for a specific ad.
3. Write `cues.json`, one entry per beat: `{"at": 3.15, "file": "part of the file name", "db": -14, "align": "peak"}`.
   - `align: peak` for hits, pops, whooshes (the loudest moment lands on the beat); `start` for beds and long whooshes;
     `end` for risers that should finish on the reveal.
   - `pitch` to vary a repeated sound (a rising ratchet: one tonal click per song flip, pitch 0.90 → 1.30), `lp`/`hp`
     to soften, `dur` to trim long tails, `pan` for width.
4. `python3 mix.py cues.json "Brand ad - SFX.wav" --lib "<folder>" [--lib "<another>"] --events events.json --gain <dB>`.
   It prints every cue's offset from its beat (should be 0 ms; anything over one frame is a bug) and the peak.
   Layer it: 2–4 **ambient beds** (`"type": "bed"`: a tonal pad in one key, a high filtered air/noise layer, a quiet tech
   texture) with fades and an `env` that lifts into the reveal; subtle whooshes (−26 to −33 dB) under every movement;
   the hits and pops on top; a second riser and a low sub under the final reveal. Check loudness
   (`ffmpeg -i x.wav -af loudnorm=print_format=summary -f null -`) and a waveform
   (`showwavespic`) for dead gaps; aim around −20 LUFS for an SFX-only stem with peaks under −2 dBFS, leaving room for
   music.
5. Mux a watch copy: `ffmpeg -i ad.mp4 -i sfx.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest "ad (sound).mp4"`.
   Keep the silent master and the WAV for the editor.

Rules that kept it tasteful:
- Subtle, clean, product-launch UI sound: soft pops, tonal clicks, marimba, airy/granular whooshes, mechanical clicks.
- **Whooshes only for movement** (a camera move, a slide). A cut or shape-morph gets a pop, tick or soft hit, not a whoosh.
- No dings or bells, no typing sounds, no hums. Don't repeat one sample identically: vary pitch and level.
- Map sounds to meaning: a logo's pieces landing = tonal clicks; a card opening = slide-appear; an app shrinking into its
  icon = mechanical suction; audio pulses = soft low drum hits; the final reveal = a riser ending on it plus a swell and a
  low hit.

## Voiceover script (for ElevenLabs or a human)
Connecting ElevenLabs to Claude (a connector) beats using its website, because Claude built the video, so it already knows the
exact length and what's on screen. It can write the words to fit the shots and make the voice in the same chat, instead of the
user guessing and cutting it up by hand. It uses their ElevenLabs credits, so only generate when they ask. Without the connector, give them the script to paste in.
- ~2.2 words per second leaves room to breathe: 10s ≈ 18–22 words, with the last 2s for the end card.
- One line per shot, short and direct, the brand's own voice and phrases; land on the brand line.
- Only say what's true and what the user can back up. No guarantees of money or results.
- Include delivery notes (upbeat, conversational, one beat each on the list lines, a pause before the brand name) and an
  alternative angle (e.g. for buyers instead of creators). Then re-time the page constants to the real take.

## Music (Suno prompts)
Write the prompt with the exact length needed. The user makes the track in Suno and gives you the audio file, then you add it and
set the levels under the sound and voice. Suno announced its own beta connector in late October 2026 (early access, uses Suno credits), so check
whether the user has it before assuming a manual step. Music from Suno may need a paid plan for commercial use, so mention it.
Match the BPM to anything rhythmic in the picture (e.g. pulses every 0.62s → 97 BPM). Give 2–3 options, each with a
**Style** box line and a **Lyrics** box structure (Instrumental, Intro / Build / Drop / Outro) so there's a lift to land
on the reveal. Example style lines:
- Clean tech pop: "minimal electronic pop, 97 BPM, instrumental, punchy kick, crisp claps, warm sub bass, plucky synth
  arpeggio, airy pads, glassy bell plucks, polished product launch, optimistic, sidechained"
- Future garage: "future garage, deep house groove, 97 BPM, instrumental, shuffled hats, soft rimshots, rubbery bass,
  wordless vocal chops, dreamy Rhodes, vinyl warmth, smooth and stylish"
- Synthwave: "modern synthwave, 97 BPM, instrumental, gated snare, driving analog bass, shimmering arpeggios, lush retro
  pads, neon night drive, glossy 80s production with modern punch"
Cut a section so the drop lands on the reveal, and sit music 8–10 dB under the SFX so the details still read.

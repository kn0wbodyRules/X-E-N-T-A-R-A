# Xtreeme demo site: design plan

This is the plan the frontend-design skill asks for before any code is written. Read it alongside `index.html` to see how each decision turns into CSS.

## Brief

- **Subject:** Xtreeme Fitness Studio, New Town, Thiruverumbur, Trichy.
- **Audience:** local people (workers, students, first-timers) checking the gym on their phone, usually from Instagram or Google Maps.
- **The page's one job:** get them to book a free trial on WhatsApp or call.

## Colour: weight-plate colours

Gym sites usually default to black with neon red or yellow. Instead, the palette comes from Olympic bumper plates, which every lifter knows:

| Token | Hex | Plate | Used for |
|---|---|---|---|
| `--red` | #c8202f | 25 kg | Main action buttons, the first fact |
| `--blue` | #1d5bb5 | 20 kg | Cardio floor, focus rings |
| `--yellow` | #e9ad16 | 15 kg | Stars, one coach |
| `--green` | #2d8a47 | 10 kg | Timings fact, one coach |
| `--concrete` | #e3e5e2 | Gym floor | Page background |
| `--ink` | #15233b | Iron | Text |

The site also has a dark mode (`prefers-color-scheme: dark`) that keeps the same plate colours, slightly brighter.

## Type

- **Big Shoulders Display** for headings. It's a condensed industrial face that feels like gym signage.
- **Atkinson Hyperlegible** for body text. It was designed for low-vision readers, so it stays clear on cheap phone screens.

## Layout

```
[XTREEME]                     [nav]  [Book a trial]
Two floors of iron in
New Town, Thiruverumbur.            <- huge, left aligned
lede + [WhatsApp] [Call]
=====|█|█|█|█|=================     <- barbell, plates slide on
• 4.9★   • 45+   • 3,500   • 5 AM   <- facts, colour-matched to plates
---------------------------------
Two floors  | Programmes | Coaches (plate discs) | 4.9 + quote
Plans | Timings / Find us / First visit
[Call] [WhatsApp]                   <- sticky bar on phones
```

All content is left aligned, with no centred text blocks.

## Principles

1. **Put the boldness in one place.** The barbell is the only loud element, and everything else is quiet.
2. **One animation.** The plates slide onto the bar once on load, and the animation is turned off if the user's phone has reduced motion enabled.
3. **Use real content only.** Every fact comes from public listings (see `/research`). Copy marked below is a guess.
4. **Make WhatsApp reachable from every screen** on mobile.

## Confirm with the owner before going live

- That +91 72005 62916 is on WhatsApp (every booking button uses it).
- The equipment lists on the two floor cards and the programme list are typical gym offerings, not confirmed.
- Coach roles and photos. Sudhakar is "Managing director" only because a review says so.
- Plan names and fees. No fees are shown on purpose until the owner agrees.
- Logo, real photos of the floors and transformation pictures. These should replace the plate graphics on the coach cards.

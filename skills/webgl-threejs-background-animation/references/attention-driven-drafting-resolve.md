# Attention-Driven Drafting Resolve — pattern reference

The interaction metaphor where a batched line-art scene starts as a dashed
"unconfirmed sketch" and resolves to solid ink as the visitor pays attention
(hover / click), with an idle floor so short visits still see the payoff.
First shipped in the retail-space-planner blueprint, refined into the
lizliz.xyz "Paper Ink Garden", and re-proven on inquiry-foundry's landing
hero (FoundryDraftingCanvas, 2026-08-30). This doc records the three-source
survey and the Foundry adaptation contract.

## Three-source survey

| | shelfplan `Landing3DBackground` | lizliz.xyz `HeroCanvas` | dieline-generator `DieCutAssembly3D` |
|---|---|---|---|
| Metaphor | architectural floor plan (blueprint) | botanical plate / ink garden | die-cut box: flat dieline folds into a 3D box |
| Resolve driver | **attention progress** (hover/click/idle) — the origin of the pattern | same, refined | **time-driven fold cycle** (fold→hold→unfold→hold loop); progress = cycle position, not attention |
| Progress constants | hover 0.015/s, click 0.06 (500ms debounce), idleTarget 0.32 / ramp 3.5s, smoothK 2, MAX 0.7 | identical values | none (autonomous loop); crossfade tied to fold windows |
| Material model | CATEGORIES config → per category one dashed + one solid material, `applyVisualState(progress, t)` crossfades + breath pulse + dash-gap shrink | same + theme-rebuild (paletteKey remount) | shared cut(dashed)/edge(solid)/fold/fill materials, `applyMaterials(progress)` |
| Batch discipline | 4 line categories × 2 + paper + vertical accent + 2 grids ≈ 11 draw calls | 4 × 2 + paper + 2 grids ≈ 11 | per-face dual materials in a fold hierarchy (more draws, still tiny scene) |
| Worth stealing | touch channels (touchmove/touchend), progress bar UI, portrait FOV/radius boost, zone fills, `depth:false` renderer, dimension-string helper | theme via `buildCategories(dark)` + MutationObserver on `data-theme`, grid drift "paper breathing", `initedRef.current = false` inside dispose to re-arm StrictMode remount | pivot-hierarchy kinematics (`FaceDef`/`applyFold` with per-stage windows), reduced-motion static frame at a *representative* progress (0.78) not 0, ResizeObserver alongside window resize |

Mechanism invariants across all three: `alpha:true` transparent canvas over
the page's own background; fog color matched to the local backdrop so line
fades read as paper depth; full dispose incl. `forceContextLoss`; context
loss → dispose + `failed → null`; IntersectionObserver + visibilitychange
gate the loop; `powerPreference:'low-power'`; pixelRatio clamped.

## The progress model (copy verbatim, tune in TUNING only)

```
target        = max(progressTarget, idleTarget * ramp(elapsed, 0, idleRampSeconds))
progress     += (target - progress) * (1 - exp(-smoothK * dt))
progressEffect = smoothstep(progress, 0, PROGRESS_MAX)

dashMat.opacity  = pulse * (1 - progressEffect * 0.7)
solidMat.opacity = pulse * progressEffect * 0.85
dashMat.gapSize  = baseGap * (1 - progressEffect * 0.6)   // dashes literally close up
```

- Interaction channels: `mousemove` accumulate throttled to 33ms;
  `click` + `touchend` share one 500ms debounce (stops touch
  double-counting); `touchmove` mirrors mousemove.
- The idle floor (0.32 over 3.5s) is non-negotiable: most visits never
  hover long enough to see the resolve otherwise.
- Note the arithmetic trap found on Foundry: with stock gains
  (0.015/s + 0.06/click), a short interaction burst (~+0.18) stays *below*
  the idle floor — attention adds nothing visible until several clicks.
  On a compact panel, raise gains ~2x in TUNING (Foundry ships 0.028/s,
  0.07/click) and keep the floor fixed.

## Foundry adaptation (V3 palette, panel slot)

- Metaphor mapping: dashed sitemap + pipeline sketch = 未确认的设计方案;
  hover/click attention = 人工确认; solid resolve = 可生成上线. An HTML
  legend inside the container names the two states (虚线·待确认 / 实线·已确认).
- Geometry families: sitemap tree (double-rect home node, rect/circle page
  nodes, bezier "stems"), 4-station delivery pipeline with arrows, amber
  confirmation marquee (4 corner ticks) on the human-confirm step,
  dimension strings, section marker, paper grain. ~500 segments total.
- V3 palette contract (no cyan/green anywhere):
  | role | dashed | solid (resolved) |
  |---|---|---|
  | map (heavy) | `#e8e8ec` | `#2b6bff` — confirm blue |
  | flow (medium) | `#9a9aa4` | `#155dfc` |
  | annot (light) | `#9a9aa4` @0.34 | `#b9bac3` (neutral lift, stays out of blue's way) |
  | accent | amber `#F59E0B` dots + marquee only | same |
  grid `#2a2c36`, paper grain `#8f9099`, fog `#0a0c12`.
- Slot decision: the canvas *replaces* the previous shader accent panel
  (Paper Design `Water`) in the hero's empty right zone — hero-anchored
  `position:absolute` (NOT inside the fixed atmosphere layer, which is
  `pointer-events:none` by contract; the canvas needs pointer capture,
  and the zone has no clickable elements so capture is safe). Feathered
  radial mask + opacity cap 0.94 keep it ambient next to the opaque
  product mock. Hidden ≤1000px, matching the old panel's breakpoint;
  IO gating then also stops the loop on mobile where it never shows.
- Reduced motion: single static frame at idleTarget rendered from the IO
  callback (also keeps `setState` out of the synchronous effect body for
  the react/set-state-in-effect lint rule).
- rAF probe on the shipped build (1440×900, Edge headless, 60-frame
  average): hero 10.1ms avg (baseline 8.3–13ms), scrolled 8.8ms with the
  loop fully stopped — no regression vs the page without it.

## When not to use

- The page has another living atmosphere layer (orb / mesh shader) —
  one dynamic atmosphere per view.
- The product story has no "draft → confirmed" arc; then a pure
  parallax line scene (no progress model) is the honest choice.
- The hero zone contains primary CTAs — pointer capture would steal
  clicks; use a window-level pointer listener like dieline instead and
  drop the click channel.

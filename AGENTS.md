# AGENTS.md — Storyworld bootstrap for AI agents

You are continuing an autonomous build. Read in this order, then check git log.

1. `docs/HANDOFF.md` — current state, what's next, session log.
2. `docs/decision_log.md` — every load-bearing decision + why.
3. `docs/master_workplan.md` — milestones M1–M8.
4. `docs/rnd_production_render.md` — render pipeline research (MCP verdict, HDRI audit).
5. `README.md` — layout + run instructions.

## Iron rules
- Verify with your own eyes: render stills via `read` on PNGs, drive the
  live player with the `agent-browser` skill (screenshot + console).
- Blender coords are X-right / Y-forward / Z-up. Never author in Y-up here.
  Use `P(x,h,d)` or explicit `(x, depth, height)` ordering. After aiming any
  camera, call `frame_check` (tools/blender/lib.py) and read the numbers.
- Never `select_all + delete` except in `clean_scene()`. Name objects `GEO-*`,
  materials `MAT-*`. Overlap joined parts; bevel before subsurf.
- Principled BSDF only. Metallic is 0 or 1, never between. Textures: diffuse +
  rough at 1K; normals dropped for GLB weight (measured, see decision log).
- Night scenes keep the art-directed gradient sky (audited HDRIs wash out);
  day/dawn/dusk/interiors use CC0 Poly Haven HDRIs in tools/blender/vendor/.
- Push thinking with code: update `docs/decision_log.md` + `docs/HANDOFF.md`
  in the same commit as any behavior change. Push to main regularly.
- Never commit secrets. The GitHub token lives OUTSIDE this repo
  (`../token-test.txt`); use it via `Authorization: Bearer` header or
  `git -c http.extraHeader=...` so it never touches git config.

## Quick commands (from repo root)
- `node tools/validate-content/validate.mjs` — 48 content checks
- `npm test` — unit + contract suites
- `npm run build` — all 4 apps
- `apps/web`: `npm run dev` (:5173) · `apps/studio` :5176 · editors :5174/:5175
- Blender: `& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
  --background --python tools/blender/<script>.py [-- args]`

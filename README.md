# Storyworld — MVP (Mahabharata Ch.01 playable proof)

Reusable story-to-world-to-platform pipeline. First run: Adi Parva, 12 portal-linked scenes, Canvas infinite-zoom player.

## Layout
- `apps/web/` — player (port 5173, preview 5199)
- `apps/studio/` — asset-pipeline dashboard (port 5176, preview 5196)
- `apps/world-editor/` — world-bible editor (port 5174)
- `apps/seam-editor/` — transition/seam editor (port 5175)
- `packages/narrative-runtime/` — package loading + navigation
- `packages/world-runtime/` — zoom math (r=0.5) + deterministic seeds
- `packages/asset-loader/` — bounded-concurrency preloading
- `packages/audio-engine/` — TTS narration + procedural WebAudio ambience
- `packages/story-schema/schemas/` — schemas (from kit `06_SCHEMAS/`)
- `content/stories/mahabharata/chapter-01-adi-parva/` — full chapter package (keyframe art v1)
- `tools/validate-content/` — structural validator (`npm run validate` from root)
- `tools/package-build/` — copies package into app `public/` dirs
- `tests/` — chapter contract tests; `npm test` runs all suites
- `docs/` — workplan, decisions, pipeline run, quality/risk

## Run
```
cd storyworld
npm install
npm run validate
npm test
cd apps/web
npm run dev
```

## Kit mapping
Implements kit order: intake → research → narrative → scene graph → world design → asset plan → package → runtime → QA, per `04_EXECUTION_PLAN/`. Renderer follows `08_REFERENCE_INPUTS/` finding: illustration↔software contract first (nested frames r=0.5, ≤4 live), Canvas now, Three.js/WebGPU later.

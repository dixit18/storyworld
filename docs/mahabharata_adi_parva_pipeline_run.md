# Pipeline Run — Mahabharata Chapter 01 (Adi Parva) v0.1.0

Date: 2026-09-21. Status: COMPLETE (procedural-placeholder tier).

## Chain executed
1. Intake → `content/.../story_intake.json` (schema-validated)
2. Bible → `story_bible.json` (thesis: inheritance/promises/legitimacy; no pure good/evil)
3. Scene graph → `scene_graph.json` (12 scenes, portal-typed)
4. World bible → `world_bible.json` (palette gold/river-blue/ivory/forest-green; illustrated/2.5d/procedural mix)
5. Asset plan → `assets_manifest.json` (12 keyframes + 4 ambience + 2 textures + shader stub + particle config = 20 assets)
6. Asset build → `tools/optimize-assets/`: `synth-audio.mjs` (4 seamless WAV loops) + `optimize.mjs` (minify, gzip report, posters, `lod_manifest.json`, `assets_report.json`, `build_log.md`)
7. Package → `package_manifest.json` + `transitions.json` (r=0.5, loop closed adi-12→adi-01) + `narration.json` + `audio_manifest.json` + `subtitles.json`
8. Validation → `node tools/validate-content/validate.mjs` → 48/48 PASS
9. Tests → `npm test` → 15/15 PASS
10. Runtime → `apps/web` (Three.js: Draco GLBs, JPG keyframe loader, firelight flicker,
    ember/firefly particles, grain/vignette, Tour mode) + `apps/studio` pipeline
    dashboard + world/seam editors → all build OK
11. Browser-verified with agent-browser: scene 1 + Next→scene 2 load, narration,
    controls; spawns tuned (01 out of tree, 02 clear of pillar); PCFSoft→PCF fix
12. Production v2 assets: 12 Blender envs (HDRI moods + PBR + bevel), 12 Cycles
    keyframes, 12 Draco GLBs (29MB, lazy per-scene), vendor/ CC0 manifest

## How to run
- `cd storyworld`
- `node tools/validate-content/validate.mjs`
- `cd apps/web; npm install; npm run dev` → http://localhost:5173
- Controls: auto-zoom per scene, Prev/Next, Pause (Space), Narrate (Web Speech TTS), subtitles in narration panel

## Known limits (phase 2)
- Art is procedural placeholders; Illustration/Neural agents to author per-scene paintings honoring the 50%-center-portal contract
- Audio is planned + runtime TTS; Audio Agent to produce ambience/narration stems
- Renderer is Canvas 2D; Runtime Graphics Agent path: WebGL/Three.js scenes per world_bible renderMode, then WebGPU progressive enhancement
- Editors (world/seam) not yet built; schemas + package spec already support them

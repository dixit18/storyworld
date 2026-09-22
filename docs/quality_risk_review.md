# Quality + Risk Review (Sprint 1)

## Checklists
- Content pipeline: intake/bible/scene-graph/world-bible/asset-audio-transition/manifests — DONE, validator green
- Art quality: focal portal per scene, palette=emotion (gold=lineage, river-blue=memory, fire=vengeance/vow), loop closure matched on fire — placeholders only, NEEDS authored pass
- Runtime readiness: manifest-driven load, entry scene, pause/resume/nav, subtitles/narration (TTS), Canvas DPR-aware, mobile panel collapse — DONE at proof tier; perf/a11y audit still open
- Release criteria: NOT FOR RELEASE — proof build only

## Risks
1. Placeholder art may be mistaken for final direction → mitigated: labeled v0 + replacement contract in world_bible
2. TTS narration quality varies by browser → phase 2 recorded stems
3. SVG-as-texture path will change under Three.js → assetIds stable; paths versioned (`procedural-v0` → authored `v1`)
4. `storyworld/` currently nested in starter kit → split to own repo at M7

## Next sprint
Authored keyframes for adi-01/adi-03/adi-12 first (loop anchors), Three.js scene for adi-03 river + adi-12 morph, recorded narration, world/seam editor stubs.

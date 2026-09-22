# Decision Log

| Date | Decision | Rationale | Status |
|---|---|---|---|
| 2026-09-21 | Canvas 2D zoom renderer for MVP, Three.js later | Reference research: contract first, renderer second; 88-image r=0.5 model works in Canvas | Accepted |
| 2026-09-21 | 12-scene Adi Parva breakdown | Covers Naimisha → snake sacrifice → Bharata line → Bhishma vow → births → rivalry → Lakshagriha → Hidimba → Swayamvara → Indraprastha; fits 10–16 required | Accepted |
| 2026-09-21 | Procedural SVG placeholders, no binary art in v0 | Unblocks runtime + packaging; Neural/Illustration agents replace per-scene in phase 2 | Accepted |
| 2026-09-21 | storyworld/ lives inside starter kit folder | Keeps kit + implementation together for first sprint; split to own repo at M7 | Accepted |
| 2026-09-21 | Deterministic seed = hash(storyId/chapterId/sceneId) | Reproducible procedural visuals, per stack guidance | Accepted |
| 2026-09-22 | Sprint 2: workspace packages + editors + keyframe v1 + tests | Real @storyworld/* packages, world/seam editors, layered SVG keyframes, node:test suites | Accepted |
| 2026-09-22 | Sprint 3: asset pipeline completion — synth WAVs, optimize/LOD/report, textures+shader+particles, poster-first player, Studio dashboard | No binary deps; deterministic synth; poster LOD for instant paint; shader honestly flagged raw | Accepted |
| 2026-09-22 | R&D: mcp-for-blender not invocable here (no MCP transport); replicated its value via Poly Haven REST + bpy | Keep deterministic versioned pipeline instead of prompt-driven modeling | Accepted |
| 2026-09-22 | Prod render v2: CC0 HDRI moods + 1K PBR (diff+rough, normals dropped for GLB weight) + bevel pass + metallic fixes | Verified per-pixel HDRI choice after qwantani gray-wash; night scenes keep art-directed gradient | Accepted |
| 2026-09-22 | Jev (TypeSafe System One) integrated as QA gate: fidelity Score + contradiction Noul per scene, calibrated gate, report to qa_jev_report.json | Text/JSON state only (no vision) so it judges words not renders; runs `npm run qa:jev`, skips without TYPESAFE_API_KEY | Accepted |

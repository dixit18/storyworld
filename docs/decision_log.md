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
| 2026-09-22 | Night-sky fix: Blender 5.2 world Generated coords don't drive ColorRamp as 4.x docs imply (verified: links intact, ramp dark, sky still bright); night scenes use flat dark Background colors | Proven by binary search (flat-dark test rendered correct night); stars/moon meshes carry sky interest | Accepted |
| 2026-09-22 | Removed OutlineEffect: silently drops sky-dome/background materials in r186 (proven by red/green sky test); toon read now from MeshToonMaterial + emissive floor only | Sky domes (canvas-gradient texture, zero custom GLSL) + per-scene exposure + shorter/higher dolly | Accepted |
| 2026-09-23 | Blob-canopy forest pass (tools/blender/blob_canopy.py): cone canopies swapped for displaced icosphere blobs sharing one mesh per blend; 156 canopies in adi-01 alone | Cones read as triangles; Chhota Bheem reference = round foliage masses; shared mesh keeps GLB weight flat (still 29MB total) | Accepted |
| 2026-09-23 | Speaker connection: bubble depthTest false + renderOrder 999, camera attention eases to speaker when user idle 4s+, speaker nods line; toonify special-cases flames to flat orange; radial-gradient sprite for embers/fireflies | User QA: bubbles occluded, characters feel static/disconnected, flame blew out white, sparks read as hexagons | Accepted |
| 2026-09-23 | Night readability: hemi 0.4-0.5 -> 0.65-0.7 + exposure 1.2-1.25 on 01/02/08/09; MCP repos (blender.org lab + ahujasid) mined for patterns but not wired (no MCP transport here); Rodin AI-gen deferred (style/rig risk, no current need) | Night scenes were muddy; open-source value replicated as versioned bpy scripts per 09-22 precedent | Accepted |

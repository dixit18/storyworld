# Master Workplan — Storyworld MVP (Mahabharata Ch.01 Adi Parva)

## Goal
Reusable story-to-world-to-platform pipeline + playable Chapter 01 proof.
Source kit: `01_START_HERE/` → `10_OUTPUT_TEMPLATES/`. Reference renderer research: `08_REFERENCE_INPUTS/` (Zoomquilt infinite-zoom contract).

## Execution order (per 04_EXECUTION_PLAN)
1. Story intake → 2. Research → 3. Narrative decomposition → 4. Scene graph → 5. World design → 6. Asset planning → 7. Asset build (procedural placeholders first) → 8. Chapter package → 9. Runtime player → 10. Tooling → 11. Optimization/QA

## Milestones
- M1 Foundation: repo scaffold, schemas, validator (THIS SPRINT)
- M2 Story Intelligence: intake + bible + chapter index (THIS SPRINT)
- M3 World Design: scene graph + world bible + transitions (THIS SPRINT)
- M4 Asset Pipeline: asset plan + procedural placeholders + manifests (THIS SPRINT)
- M5 First Story Run: complete chapter-01 package (THIS SPRINT)
- M6 Runtime Proof: Canvas infinite-zoom player loading the package (THIS SPRINT)
- M7 Internal Tools: validate-content + package-build CLIs
- M8 Product Polish: art QA, a11y, perf (Three.js/WebGPU upgrade path)

## Key decisions
- Runtime first proves the **illustration↔software contract** (nested frames, r=0.5, ≤4 images live, log-zoom), NOT Three.js. Canvas 2D MVP → Three.js/WebGL later, WebGPU progressive. Matches reference research conclusion.
- All Chapter 01 art is **procedural SVG/Canvas placeholders** under `content/.../assets/images/` + runtime procedural fallback. Offline AI art (Neural Rendering Agent) is phase 2.
- Runtime never invents story: loads `package_manifest.json` → `scene_graph.json` → assets → renders entry scene, pause/resume/nav.
- Deterministic seeds for all procedural visuals (`seed_policy`: storyId-chapterId-sceneId hash).
- 12 scenes for Adi Parva (within required 10–16).

## Dependency graph
schemas → intake → bible → scene_graph → world_bible → assets_manifest → package_manifest → runtime → QA

## Paths
- Package: `content/stories/mahabharata/chapter-01-adi-parva/`
- Schemas: `packages/story-schema/schemas/` (copied from `06_SCHEMAS/`)
- Validator: `tools/validate-content/validate.mjs`
- Player: `apps/web/` (Vite + TS, zero-dep Canvas zoom renderer)
- This plan: `docs/master_workplan.md`, decisions: `docs/decision_log.md`

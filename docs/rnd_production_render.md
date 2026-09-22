# R&D: Production-Ready Render Pipeline (2026-09-22)

## What was investigated
1. `ahujasid/mcp-for-blender` (29k stars): MCP server + Blender addon (socket :9876).
   Verdict: **cannot run it from here** — this environment has no MCP-client transport
   (tools available: shell/file/web only; the README's OpenCode config targets the
   OpenCode IDE product, not this API toolset). No code changes needed on their side;
   it is simply not invocable from my toolset.
2. Installed skills: `blender-web-pipeline`, `blender-modeling`, `blender-materials`
   (incl. full SKILL.md + references). Directly applicable; no MCP needed.
3. Poly Haven public API: reachable (HTTP 200, no key, CC0). Confirmed usable.
4. EEVEE draft speed on this machine (RTX 3080 Ti): full scene at 50% in ~11s.

## Why current renders look "triangly" (root causes, verified against outputs)
1. Unbeveled low-seg primitives (cones 8-seg, cylinders 10-seg), flat facets.
2. Single-color Principled materials, metallic in the forbidden 0.2–0.8 middle
   (our gold uses 0.4–0.8) → plasticky look.
3. Gradient sky → no real light variation, reflections, or ambient color.
4. Floating objects, empty ground planes, no contact/AO grounding.
5. 96 samples, no texture detail, thin distant compositions.

## Tools that remove each limitation (all open-source / free, terminal-driven)
| Limitation | Tool / source | Key needed | Status |
|---|---|---|---|
| Flat lighting/reflections | Poly Haven HDRIs (CC0, REST, no key) | none | API verified 200 |
| Plastic materials | Poly Haven PBR textures 1K (bark/stone/marble/wood/water) | none | ready |
| Extra set dressing | Poly Haven models / Poly Pizza low-poly (CC0 filter) | none / free key | ready / optional |
| Faceted geometry | bevel+subsurf per modeling skill (already in lib pattern) | none | ready |
| Slow iteration | EEVEE 50% drafts ~11s, Cycles finals | none | measured |
| AI 3D (Hyper3D/Hunyuan) | needs paid API keys | MISSING | rejected for now |
| Local Stable Diffusion | multi-GB downloads, non-deterministic, **images can't be roamed in 3D** | none | rejected for now |

## Neural rendering verdict
Skip it. Our requirement is *roamable* 3D, and neural outputs are (a) flat images
or (b) API-gated meshes with no art direction. Deterministic procedural Blender +
CC0 PBR assets give consistent style, real geometry, and Draco GLBs. Revisit only
for 2D concept keyframes if ever needed.

## Proposed production pipeline (per scene)
1. HDRI mood light (dawn / day / dusk / night interior) + sun match.
2. Bevel + higher-seg primitives, smooth shade, grounded placement.
3. PBR textures on hero surfaces (1K cap), procedural grain/marble elsewhere.
4. Scatter detail (grass/rocks/reeds), background silhouettes.
5. EEVEE draft for framing (~11s) → Cycles final 160–256sp OptiX.
6. Draco GLB re-export (proven: 17MB → 3.2MB), JPG keyframes, manifest bump.

## Recommended next step
Pilot **one** scene to the v2 quality bar (suggest adi-01 Naimisha: night + fire
shows HDRI + emission + texture payoff best), review the still, then batch the
other 11 with the locked formula.

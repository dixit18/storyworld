# HANDOFF — state of the build (2026-09-22, end of session)

## What this is
Reusable story→world→platform pipeline. Proof content: Mahabharata Chapter 01
(Adi Parva), 12 scenes. Player is a **continuous 3D journey** (no scene buttons):
the camera dollies through Blender-built GLB environments while toon-shaded
characters speak the scene's dialogue (TTS), with pause / 0.5× / 1× / 2× pacing.

## Where things stand
- DONE: content package (48/48 validate, 15/15 tests), 12 Blender envs + 12 Cycles
  keyframes + 12 Draco GLBs (29MB), 4 toon character archetypes (sage/warrior/
  princess/king, Bheem-bar verified in cast_preview.png), dialogue.json (20 voices),
  journey player (flight + dialogue + toon + outlines + tour pacing + ambience),
  studio dashboard, world/seam editors. Browser-verified (agent-browser screenshots).
- Production v2 look: CC0 HDRI moods, 1K PBR (diffuse+rough), bevel pass, metallic
  fixes, lacquer coat. Night scenes use gradient skies (audited: night HDRIs wash).
- Pushed to: https://github.com/dixit18/storyworld (public).

## Open threads / next up (in order)
1. Journey soak test: watch a full 12-scene flight in the browser; tune per-scene
   dolly vectors and line timing; fix any camera-in-geometry moments.
2. Character variety: accessory variants (Krishna peacock feather, Bhima mace in
   hand) so same-archetype speakers differ; then walk/idle bob animation.
3. Animated water + flame geometry in GLBs (currently static + light flicker).
4. Chapter 02 (Sabha Parva) pipeline run using the same machine.
5. Competitor watch (Zoomquilt-likes, AI story-world startups) — see session log.

## Key files
- Player: `apps/web/src/main.ts` (journey+dialogue+toon), `engine.ts`, `world.ts` (fallback).
- Blender: `tools/blender/scene_adi_*.py`, `chars_kit.py`, `upgrade_all.py`, `lib.py`.
- Content: `content/stories/mahabharata/chapter-01-adi-parva/` (+ `dialogue.json`).
- Vendor CC0: `tools/blender/vendor/` + manifest.json.
- Thinking: `docs/decision_log.md`, `docs/rnd_production_render.md`, this file.

## Session log (condensed)
- S1 scaffold + 12-scene pipeline + Canvas zoom player (superseded).
- S2 packages + editors + keyframe v1 + tests.
- S3 asset pipeline completion (WAV synth, LOD, Studio).
- S4 Blender 5.2 install, pilot adi-03 (fixed: Y-up confusion, sky API, dead delete-all,
  framing via frame_check), batch 12, Draco (17→3MB), GLB Three.js player.
- S5 R&D (MCP not invocable here; Poly Haven REST instead), v2 look pass on all 12,
  normal-map weight cut (52→29MB), browser-verified with agent-browser.
- S6 journey player (no Next), toon cast + dialogue, repo created + first push.
- S7 competitor watch (Outerbook/3DStoryteller closest; our moat = roamable 3D +
  paced journey + deterministic pipeline); journey soak test (1→2→3 advance OK,
  dolly shortened 0.38→0.25 after shrine collision); repo: dixit18/storyworld.
- S8 sky domes (canvas gradient, per-scene moods) after proving OutlineEffect
  silently eats background materials; per-scene exposure; dolly 0.18/+2.0;
  speed keys 1/2/3; agent-browser discipline (wait --text/--fn, single batch).
- S9 feel pass from user QA (still triangular envs, occluded bubbles, static
  cast): blob_canopy.py on all outdoor blends (156 canopies in adi-01; GLBs
  still 29MB); bubbles always-on-top + speaker focus + nod; toon flames flat
  orange; soft-glow particle sprites; night hemi/exposure lift; official
  Blender MCP page + ahujasid repo mined (Poly Haven/Poly Pizza/Rodin patterns
  noted, Rodin deferred); rebuilt + browser-verified scene 01.
- S10 reference study (Shining/Lusion/Oat the Goat) at user's push + cozy
  story-circle pilot on adi-01: tight ring, tree wall, close camera, Sauti
  1.25x; browser-verified clean (hard-reload needed: preview caches GLBs).
- S11 faces (billboard eyes/brows/talking mouth + blink), fill light, slim
  flame, cache-busting ?cb, ?freeze=1 staging hook, midpoint focus; fixed the
  vanishing-speaker bug (nod overwrote lookAt Euler .x -> PI-flip burial).
- S12 user rejected robots+stickers outright: built own-kit toon Rishi
  (chars_sage.py, 4.2k tris, Idle+blink) for all sage cast + VARIETY tints;
  closer adi-01 spawn; verified three distinct faced sages in player.
- S14 full cast kit (chars_kit.py): king/warrior/strongman/princess with
  Idle+blink, Arjuna->warrior, VARIETY skin slot + 20 rows, OWN_KIT wiring;
  journey-verified scenes 1-2, zero console errors. NEXT: restage scenes
  2-12 (adi-02 poles overexposed + center-framed) + env dressing pass.

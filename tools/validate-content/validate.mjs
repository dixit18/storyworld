// Minimal structural validator for Chapter 01 package (no external deps).
// Usage: node tools/validate-content/validate.mjs
import { readFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const ch = join(root, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva');
const fail = [];
const ok = [];
const need = (cond, msg) => (cond ? ok.push(msg) : fail.push(msg));
const load = (f) => JSON.parse(readFileSync(join(ch, f), 'utf8'));

try {
  const intake = load('story_intake.json');
  need(intake.storyId && intake.title && intake.sourceType && intake.genre && intake.scope, 'story_intake: required fields present');
  const bible = load('story_bible.json');
  need(bible.storyId && bible.logline && Array.isArray(bible.majorCharacters), 'story_bible: required fields present');
  const sg = load('scene_graph.json');
  need(Array.isArray(sg.scenes) && sg.scenes.length >= 10 && sg.scenes.length <= 16, `scene_graph: ${sg.scenes?.length} scenes (need 10-16)`);
  const ids = new Set(sg.scenes.map((s) => s.sceneId));
  need(ids.size === sg.scenes.length, 'scene_graph: sceneIds unique');
  need(sg.scenes.every((s) => s.sceneId && s.title && s.narrativeBeat && s.location), 'scene_graph: per-scene required fields');
  const wb = load('world_bible.json');
  need(wb.visualTheme?.palette?.length >= 3, 'world_bible: palette present');
  need(wb.scenes.length === sg.scenes.length, 'world_bible: covers all scenes');
  need(wb.scenes.every((s) => ['illustrated', '2.5d', '3d', 'hybrid', 'procedural'].includes(s.renderMode)), 'world_bible: renderModes valid');
  const am = load('assets_manifest.json');
  need(am.assets.length >= sg.scenes.length, 'assets_manifest: >=1 asset per scene');
  for (const a of am.assets) {
    const p = join(ch, a.path);
    need(existsSync(p), `asset exists: ${a.assetId} -> ${a.path}`);
  }
  const pm = load('package_manifest.json');
  need(pm.entrySceneId && ids.has(pm.entrySceneId), 'package_manifest: entrySceneId valid');
  for (const f of [pm.sceneGraphPath, pm.worldBiblePath, pm.assetsManifestPath, pm.audioManifestPath, pm.transitionsPath]) {
    need(existsSync(join(ch, f)), `package file exists: ${f}`);
  }
  const tr = load('transitions.json');
  need(tr.nestingRatio === 0.5 && tr.maxLiveImages <= 4, 'transitions: r=0.5, maxLive<=4');
  need(tr.transitions.length === sg.scenes.length, 'transitions: one outgoing edge per scene (loop closed)');
  const last = tr.transitions[tr.transitions.length - 1];
  need(last.loopClosure === true && last.to === sg.scenes[0].sceneId, 'transitions: loop closure back to entry');
  const nar = load('narration.json');
  need(nar.blocks.length === sg.scenes.length, 'narration: block per scene');
  const au = load('audio_manifest.json');
  for (const t of au.tracks) {
    if (t.file) need(existsSync(join(ch, t.file)), `audio file exists: ${t.trackId}`);
  }
  const generated = au.tracks.filter((t) => t.status === 'generated').length;
  need(generated >= 4, `audio: ${generated} generated stems (need >=4)`);
  const lod = load('lod_manifest.json');
  need(sg.scenes.every((s) => lod.levels[`${s.sceneId}-bg`]?.poster), 'lod: poster per scene');
  const pp = JSON.parse(readFileSync(join(ch, 'assets', 'particles', 'portal-particles.json'), 'utf8'));
  need(sg.scenes.every((s) => pp.portalByScene[s.sceneId] && pp.emitters[pp.portalByScene[s.sceneId]]), 'particles: emitter per scene');
  const rep = load('assets_report.json');
  need(rep.assets.every((a) => a.status === 'pass'), 'assets_report: all within gzip budget');
  need(existsSync(join(ch, 'build_log.md')), 'build_log.md exists');
} catch (e) {
  fail.push('exception: ' + e.message);
}

console.log(`PASS ${ok.length}:`);
for (const m of ok) console.log('  ok - ' + m);
if (fail.length) {
  console.log(`FAIL ${fail.length}:`);
  for (const m of fail) console.log('  FAIL - ' + m);
  process.exit(1);
} else {
  console.log('All content checks passed.');
}

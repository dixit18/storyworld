// Contract tests over the built Chapter 01 package (no TS needed).
import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ch = join(
  dirname(fileURLToPath(import.meta.url)),
  '..', 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva',
);
const load = (f) => JSON.parse(readFileSync(join(ch, f), 'utf8'));

const sg = load('scene_graph.json');
const wb = load('world_bible.json');
const tr = load('transitions.json');
const nar = load('narration.json');
const am = load('assets_manifest.json');
const pm = load('package_manifest.json');

describe('chapter package contract', () => {
  it('has 10-16 scenes with unique ids', () => {
    assert.ok(sg.scenes.length >= 10 && sg.scenes.length <= 16);
    assert.equal(new Set(sg.scenes.map((s) => s.sceneId)).size, sg.scenes.length);
  });
  it('entry scene exists', () => {
    assert.ok(sg.scenes.some((s) => s.sceneId === pm.entrySceneId));
  });
  it('zoom contract: r=0.5, <=4 live, loop closed', () => {
    assert.equal(tr.nestingRatio, 0.5);
    assert.ok(tr.maxLiveImages <= 4);
    assert.equal(tr.transitions.length, sg.scenes.length);
    const last = tr.transitions[tr.transitions.length - 1];
    assert.equal(last.loopClosure, true);
    assert.equal(last.to, sg.scenes[0].sceneId);
  });
  it('every scene has narration, world entry, and an asset file', () => {
    const narrIds = new Set(nar.blocks.map((b) => b.sceneId));
    const worldIds = new Set(wb.scenes.map((s) => s.sceneId));
    for (const s of sg.scenes) {
      assert.ok(narrIds.has(s.sceneId), `narration missing: ${s.sceneId}`);
      assert.ok(worldIds.has(s.sceneId), `world entry missing: ${s.sceneId}`);
    }
    for (const a of am.assets) {
      assert.ok(existsSync(join(ch, a.path)), `asset missing: ${a.path}`);
      // phase-2 stubs (e.g. WebGL shaders) may stay raw; everything else ships optimized
      const expect = a.type === 'shader' ? ['optimized', 'raw'] : ['optimized'];
      assert.ok(expect.includes(a.optimizationStatus), `status wrong: ${a.assetId}`);
    }
  });
  it('render modes are valid', () => {
    for (const s of wb.scenes) {
      assert.ok(['illustrated', '2.5d', '3d', 'hybrid', 'procedural'].includes(s.renderMode));
    }
  });
  it('asset pipeline outputs are complete', () => {
    const au = load('audio_manifest.json');
    for (const t of au.tracks) {
      if (t.file) assert.ok(existsSync(join(ch, t.file)), `audio missing: ${t.file}`);
    }
    assert.ok(au.tracks.filter((t) => t.status === 'generated').length >= 4);
    const lod = load('lod_manifest.json');
    for (const s of sg.scenes) {
      assert.ok(lod.levels[`${s.sceneId}-bg`]?.poster, `poster missing: ${s.sceneId}`);
    }
    const pp = load('assets/particles/portal-particles.json');
    for (const s of sg.scenes) {
      assert.ok(pp.emitters[pp.portalByScene[s.sceneId]], `emitter missing: ${s.sceneId}`);
    }
    const rep = load('assets_report.json');
    assert.ok(rep.assets.every((a) => a.status === 'pass'));
    assert.ok(existsSync(join(ch, 'build_log.md')));
  });
});

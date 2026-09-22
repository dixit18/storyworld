// Studio dashboard: full asset pipeline visible in the browser.
import { loadChapterPackage } from '@storyworld/narrative-runtime';

const elStages = document.getElementById('stages')!;
const elAssets = document.getElementById('assets')!;
const elQa = document.getElementById('qa')!;
const elLog = document.getElementById('buildlog')!;
const elPkg = document.getElementById('pkgline')!;

async function getJSON<T>(p: string): Promise<T> {
  const r = await fetch(p);
  if (!r.ok) throw new Error(`${p}: ${r.status}`);
  return r.json() as Promise<T>;
}
async function getText(p: string): Promise<string> {
  const r = await fetch(p);
  return r.ok ? r.text() : '(missing)';
}
const kb = (n: number) => `${(n / 1024).toFixed(1)}KB`;

async function main() {
  const pkg = await loadChapterPackage('./package');
  const [am, rep, tr, audio, lod] = await Promise.all([
    getJSON<{ assets: { assetId: string; type: string; path: string; source: string; version: string; optimizationStatus: string; tags: string[] }[] }>('./package/assets_manifest.json'),
    getJSON<{ assets: { assetId: string; bytes: number; gzipBytes: number; status: string }[]; totalGzipBytes: number }>('./package/assets_report.json'),
    getJSON<{ nestingRatio: number; maxLiveImages: number; transitions: unknown[] }>('./package/transitions.json'),
    getJSON<{ tracks: { trackId: string; file?: string; status: string }[] }>('./package/audio_manifest.json'),
    getJSON<{ levels: Record<string, { poster?: string; full?: string; fallback?: string }> }>('./package/lod_manifest.json'),
  ]);
  elLog.textContent = await getText('./package/build_log.md');

  elPkg.textContent =
    `${pkg.manifest.packageId} · v${pkg.manifest.version} · ${pkg.scenes.length} scenes · entry ${pkg.manifest.entrySceneId}`;

  const repById = new Map(rep.assets.map((a) => [a.assetId, a]));
  const byType = (t: string) => am.assets.filter((a) => a.type === t);

  const stages: { name: string; detail: string; done: boolean }[] = [
    { name: '1 · Story intake', detail: 'story_intake.json — mahabharata / chapter-01-adi-parva', done: true },
    { name: '2 · Story bible', detail: `${pkg.scenes.length} beats · thesis: inheritance & cost of certainty`, done: true },
    { name: '3 · Narrative', detail: `scene_graph + narration (${pkg.narrationById.size}/${pkg.scenes.length}) + subtitles`, done: pkg.narrationById.size === pkg.scenes.length },
    { name: '4 · World design', detail: `world_bible + transitions (r=${tr.nestingRatio}, loop closed)`, done: tr.nestingRatio === 0.5 },
    { name: '5 · Asset production', detail: `${byType('image').length} keyframes · ${byType('audio').length} ambience · ${byType('texture').length} textures · shader + particles`, done: true },
    { name: '6 · Asset build', detail: `gzip ${(rep.totalGzipBytes / 1024).toFixed(1)}KB keyframes · LOD ${Object.keys(lod.levels).length} levels · posters + procedural fallback`, done: true },
    { name: '7 · Package', detail: `${pkg.manifest.packageId} · entry ${pkg.manifest.entrySceneId}`, done: true },
    { name: '8 · Runtime', detail: 'player + world/seam editors (links above)', done: true },
  ];
  for (const s of stages) {
    const d = document.createElement('div');
    d.className = 'stage' + (s.done ? ' done' : '');
    d.innerHTML = `<h3>${s.name}</h3><div>${s.detail}</div>`;
    const b = document.createElement('span');
    b.className = 'badge';
    b.textContent = s.done ? 'done' : 'open';
    d.appendChild(b);
    elStages.appendChild(d);
  }

  for (const a of am.assets) {
    const card = document.createElement('div');
    card.className = 'card';
    const r = repById.get(a.assetId);
    const head = document.createElement('div');
    head.innerHTML = `<strong>${a.assetId}</strong> `;
    const tb = document.createElement('span');
    tb.className = 'badge type';
    tb.textContent = a.type;
    head.appendChild(tb);
    card.appendChild(head);
    if (a.type === 'image') {
      const img = document.createElement('img');
      img.src = `./package/${a.path}`;
      img.alt = a.assetId;
      img.loading = 'lazy';
      card.appendChild(img);
    } else if (a.type === 'audio') {
      const au = document.createElement('audio');
      au.controls = true;
      au.loop = true;
      au.preload = 'none';
      au.src = `./package/${a.path}`;
      card.appendChild(au);
    } else {
      const code = document.createElement('code');
      code.textContent = a.path;
      card.appendChild(code);
    }
    const meta = document.createElement('div');
    const size = r ? ` · ${kb(r.bytes)} (gzip ${kb(r.gzipBytes)})` : '';
    meta.textContent = `${a.source} ${a.version} · ${a.optimizationStatus}${size}`;
    card.appendChild(meta);
    const st = document.createElement('span');
    const ok = a.optimizationStatus === 'optimized' && (!r || r.status === 'pass');
    st.className = 'badge' + (ok ? '' : ' warn');
    st.textContent = ok ? 'qc pass' : 'qc review';
    card.appendChild(st);
    elAssets.appendChild(card);
  }

  const checks: [string, boolean][] = [
    [`${pkg.scenes.length} scenes (need 10–16)`, pkg.scenes.length >= 10 && pkg.scenes.length <= 16],
    ['narration covers all scenes', pkg.narrationById.size === pkg.scenes.length],
    ['posters cover all scenes', pkg.posterByScene.size === pkg.scenes.length],
    ['particle emitters for all scenes', pkg.emitterByScene.size === pkg.scenes.length],
    ['ambience files for all scenes', pkg.audioFileByScene.size === pkg.scenes.length],
    ['audio tracks generated', audio.tracks.filter((t) => t.status === 'generated').length >= 4],
    ['keyframe gzip within budget', rep.assets.every((a) => a.status === 'pass')],
  ];
  for (const [label, ok] of checks) {
    const li = document.createElement('li');
    li.className = ok ? 'pass' : 'fail';
    li.textContent = `${ok ? 'PASS' : 'FAIL'} — ${label}`;
    elQa.appendChild(li);
  }
}

main().catch((e: unknown) => {
  elPkg.textContent = e instanceof Error ? e.message : String(e);
});

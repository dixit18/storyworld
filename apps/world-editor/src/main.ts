// World editor stub: inspect + tweak world_bible.json per scene, export the result.
import { loadChapterPackage } from '@storyworld/narrative-runtime';

const list = document.getElementById('list')!;
const editor = document.getElementById('editor')!;

async function getJSON<T>(p: string): Promise<T> {
  const r = await fetch(p);
  if (!r.ok) throw new Error(`${p}: ${r.status}`);
  return r.json() as Promise<T>;
}

type WorldScene = {
  sceneId: string;
  renderMode: string;
  cameraMode: string;
  assetNeeds: string[];
  proceduralRules: string[];
  transitionDesign: string;
};

const MODES = ['illustrated', '2.5d', '3d', 'hybrid', 'procedural'];

async function main() {
  const pkg = await loadChapterPackage('./package');
  const wb = await getJSON<{ visualTheme: { palette: string[] }; scenes: WorldScene[] }>(
    './package/world_bible.json',
  );
  const byId = new Map(wb.scenes.map((s) => [s.sceneId, structuredClone(s)]));
  let current = pkg.scenes[0].sceneId;

  function renderList() {
    list.innerHTML = '';
    for (const s of pkg.scenes) {
      const b = document.createElement('button');
      b.textContent = s.title;
      b.className = s.sceneId === current ? 'active' : '';
      b.onclick = () => { current = s.sceneId; renderList(); renderEditor(); };
      list.appendChild(b);
    }
  }

  function renderEditor() {
    const s = pkg.scenes.find((x) => x.sceneId === current)!;
    const w = byId.get(current)!;
    editor.innerHTML = '';
    const h = document.createElement('h2');
    h.textContent = s.title;
    editor.appendChild(h);

    const pal = document.createElement('div');
    pal.innerHTML = '<strong>Palette:</strong> ';
    for (const c of wb.visualTheme.palette) {
      const sw = document.createElement('span');
      sw.className = 'swatch';
      sw.style.background = c;
      sw.title = c;
      pal.appendChild(sw);
    }
    editor.appendChild(pal);

    const mk = (label: string, el: HTMLElement) => {
      const l = document.createElement('label');
      l.textContent = label;
      editor.appendChild(l);
      editor.appendChild(el);
    };

    const mode = document.createElement('select');
    for (const m of MODES) {
      const o = document.createElement('option');
      o.value = m; o.textContent = m;
      if (m === w.renderMode) o.selected = true;
      mode.appendChild(o);
    }
    mode.onchange = () => { w.renderMode = mode.value; };
    mk('Render mode', mode);

    const cam = document.createElement('input');
    cam.value = w.cameraMode;
    cam.onchange = () => { w.cameraMode = cam.value; };
    mk('Camera mode', cam);

    const assets = document.createElement('textarea');
    assets.value = w.assetNeeds.join('\n');
    assets.onchange = () => { w.assetNeeds = assets.value.split('\n').map((x) => x.trim()).filter(Boolean); };
    mk('Asset needs (one per line)', assets);

    const rules = document.createElement('textarea');
    rules.value = w.proceduralRules.join('\n');
    rules.onchange = () => { w.proceduralRules = rules.value.split('\n').map((x) => x.trim()).filter(Boolean); };
    mk('Procedural rules (one per line)', rules);

    const trans = document.createElement('textarea');
    trans.value = w.transitionDesign;
    trans.onchange = () => { w.transitionDesign = trans.value; };
    mk('Transition design', trans);

    const img = document.createElement('img');
    img.className = 'preview';
    img.alt = `Keyframe preview for ${s.title}`;
    img.src = pkg.assetPathById.get(s.sceneId) ?? '';
    editor.appendChild(img);

    const actions = document.createElement('div');
    actions.id = 'actions';
    const exp = document.createElement('button');
    exp.className = 'primary';
    exp.textContent = 'Export world_bible.json';
    exp.onclick = () => {
      const out = JSON.stringify(
        { storyId: pkg.manifest.storyId, chapterId: pkg.manifest.chapterId, visualTheme: wb.visualTheme, scenes: [...byId.values()] },
        null, 2,
      );
      const a = document.createElement('a');
      a.href = URL.createObjectURL(new Blob([out], { type: 'application/json' }));
      a.download = 'world_bible.json';
      a.click();
      URL.revokeObjectURL(a.href);
    };
    actions.appendChild(exp);
    editor.appendChild(actions);
  }

  renderList();
  renderEditor();
}

main().catch((e: unknown) => {
  editor.textContent = e instanceof Error ? e.message : String(e);
});

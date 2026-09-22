// Seam editor stub: tweak transitions.json durations/types with loop validation.
import { loadChapterPackage } from '@storyworld/narrative-runtime';

type Transition = {
  from: string;
  to: string;
  type: string;
  durationSec: number;
  loopClosure?: boolean;
};

const rows = document.getElementById('rows')!;
const status = document.getElementById('status')!;
const btnExport = document.getElementById('export') as HTMLButtonElement;

async function getJSON<T>(p: string): Promise<T> {
  const r = await fetch(p);
  if (!r.ok) throw new Error(`${p}: ${r.status}`);
  return r.json() as Promise<T>;
}

async function main() {
  const pkg = await loadChapterPackage('./package');
  const tr = await getJSON<{
    nestingRatio: number;
    maxLiveImages: number;
    zoomSecondsPerScene: number;
    transitions: Transition[];
  }>('./package/transitions.json');
  const ids = new Set(pkg.scenes.map((s) => s.sceneId));

  function validate() {
    const problems: string[] = [];
    if (tr.nestingRatio !== 0.5) problems.push('nestingRatio must be 0.5');
    if (tr.maxLiveImages > 4) problems.push('maxLiveImages must be <= 4');
    for (const t of tr.transitions) {
      if (!ids.has(t.from)) problems.push(`unknown from: ${t.from}`);
      if (!ids.has(t.to)) problems.push(`unknown to: ${t.to}`);
      if (!(t.durationSec > 0 && t.durationSec <= 10)) problems.push(`bad duration ${t.from}→${t.to}`);
    }
    const last = tr.transitions[tr.transitions.length - 1];
    if (!(last.loopClosure && last.to === pkg.scenes[0].sceneId)) {
      problems.push('loop must close back to entry scene');
    }
    if (problems.length) {
      status.className = 'bad';
      status.textContent = 'Invalid: ' + problems.join('; ');
    } else {
      status.className = 'good';
      const total = tr.transitions.reduce((a, t) => a + t.durationSec, 0);
      status.textContent = `Valid — ${tr.transitions.length} seams, ${total.toFixed(1)}s transition time, loop closed.`;
    }
  }

  function render() {
    rows.innerHTML = '';
    for (const t of tr.transitions) {
      const trEl = document.createElement('tr');
      const from = document.createElement('td'); from.textContent = t.from;
      const to = document.createElement('td'); to.textContent = t.to;
      const typeTd = document.createElement('td');
      const type = document.createElement('input');
      type.value = t.type;
      type.setAttribute('aria-label', `Transition type ${t.from} to ${t.to}`);
      type.onchange = () => { t.type = type.value; validate(); };
      typeTd.appendChild(type);
      const durTd = document.createElement('td');
      const dur = document.createElement('input');
      dur.type = 'number'; dur.min = '0.5'; dur.max = '10'; dur.step = '0.5';
      dur.value = String(t.durationSec);
      dur.setAttribute('aria-label', `Duration ${t.from} to ${t.to}`);
      dur.onchange = () => { t.durationSec = Number(dur.value); validate(); };
      durTd.appendChild(dur);
      const loop = document.createElement('td');
      loop.textContent = t.loopClosure ? 'loop ↩' : '';
      trEl.append(from, to, typeTd, durTd, loop);
      rows.appendChild(trEl);
    }
    validate();
  }

  btnExport.onclick = () => {
    const out = JSON.stringify(
      { storyId: pkg.manifest.storyId, chapterId: pkg.manifest.chapterId, ...tr },
      null, 2,
    );
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([out], { type: 'application/json' }));
    a.download = 'transitions.json';
    a.click();
    URL.revokeObjectURL(a.href);
  };

  render();
}

main().catch((e: unknown) => {
  status.className = 'bad';
  status.textContent = e instanceof Error ? e.message : String(e);
});

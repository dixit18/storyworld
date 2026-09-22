// Storyworld journey player: one continuous flight through Adi Parva.
// No scene buttons — the story moves; the user sets pace (pause / 0.5x / 1x / 2x),
// looks around freely, and hears each scene's dialogue on its characters.
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';
import { Engine, type EnvResult } from './engine';
import { BUILDERS } from './world';
import {
  loadChapterPackage,
  type ChapterPackage,
} from '@storyworld/narrative-runtime';
import {
  ambienceForScene,
  playSceneAmbience,
  stopSpeech,
} from '@storyworld/audio-engine';

interface SceneStyle {
  bg: number;
  fog: [number, number];
  spawn: { pos: [number, number, number]; target: [number, number, number] };
  hemi: { sky: number; ground: number; i: number };
  sun: { color: number; i: number; pos: [number, number, number] };
  fires: { color: number; i: number; pos: [number, number, number] }[];
  extras: 'embers' | 'fireflies' | null;
}

// (Unchanged environment art direction — spawns double as journey waypoints.)
const STYLE: Record<string, SceneStyle> = {
  'adi-01-naimisha': { bg: 0x070d0a, fog: [25, 130], spawn: { pos: [8, 3.0, -11], target: [0, 1.6, 2] },
    hemi: { sky: 0x2a3a4a, ground: 0x0a0f0a, i: 0.5 }, sun: { color: 0x8fa8c8, i: 0.5, pos: [-30, 40, 30] },
    fires: [{ color: 0xff8c3a, i: 90, pos: [0, 2.5, 0] }], extras: 'embers' },
  'adi-02-snake-sacrifice': { bg: 0x120606, fog: [20, 110], spawn: { pos: [10, 4, -13], target: [0, 3, 2] },
    hemi: { sky: 0x3a1a12, ground: 0x0a0605, i: 0.4 }, sun: { color: 0xff6a3a, i: 0.6, pos: [-20, 30, 10] },
    fires: [{ color: 0xff6a3a, i: 160, pos: [0, 3, 0] }], extras: 'embers' },
  'adi-03-ganga': { bg: 0x3a4a5e, fog: [35, 180], spawn: { pos: [2, 7.5, -40], target: [6, 0.5, 14] },
    hemi: { sky: 0x9db8d8, ground: 0x2a3a2a, i: 0.7 }, sun: { color: 0xffe0b0, i: 1.6, pos: [40, 30, -30] },
    fires: [], extras: null },
  'adi-04-bhishma-vow': { bg: 0x171006, fog: [15, 90], spawn: { pos: [11, 3.4, -12], target: [0, 3.5, 13] },
    hemi: { sky: 0x5a4a30, ground: 0x14100a, i: 0.5 }, sun: { color: 0xffd88a, i: 1.2, pos: [10, 24, 14] },
    fires: [{ color: 0xffb35a, i: 30, pos: [-8, 3.5, -2] }, { color: 0xffb35a, i: 30, pos: [8, 3.5, -2] }], extras: null },
  'adi-05-vyasa-line': { bg: 0x0d0d14, fog: [12, 65], spawn: { pos: [8, 2.8, -11], target: [0, 1.4, 6] },
    hemi: { sky: 0x3a3450, ground: 0x0a0a10, i: 0.45 }, sun: { color: 0x8a7aa8, i: 0.5, pos: [0, 20, -10] },
    fires: [{ color: 0xff9a3a, i: 25, pos: [5, 2.2, -4] }], extras: null },
  'adi-06-births': { bg: 0x87a6c4, fog: [45, 200], spawn: { pos: [2, 3.5, 6], target: [-10, 1, -18] },
    hemi: { sky: 0xbdd4e8, ground: 0x3a5a3a, i: 0.8 }, sun: { color: 0xfff2d8, i: 2.0, pos: [40, 50, 20] },
    fires: [], extras: null },
  'adi-07-drona': { bg: 0xb8a888, fog: [45, 200], spawn: { pos: [0, 4, -24], target: [0, 2.5, 16] },
    hemi: { sky: 0xcfd8e0, ground: 0x6a5638, i: 0.7 }, sun: { color: 0xffe8c0, i: 2.0, pos: [30, 44, 18] },
    fires: [], extras: null },
  'adi-08-lakshagriha': { bg: 0x0d0505, fog: [22, 120], spawn: { pos: [26, 10, -34], target: [0, 5, 8] },
    hemi: { sky: 0x3a1a10, ground: 0x0a0605, i: 0.4 }, sun: { color: 0xff8c3a, i: 0.6, pos: [-24, 26, 12] },
    fires: [{ color: 0xff8c3a, i: 110, pos: [-9, 2.5, -8] }, { color: 0xff8c3a, i: 90, pos: [9, 2.5, -8] }], extras: 'embers' },
  'adi-09-hidimba': { bg: 0x040806, fog: [10, 60], spawn: { pos: [0, 2.8, -14], target: [0, 3, 12] },
    hemi: { sky: 0x1a2a24, ground: 0x050805, i: 0.4 }, sun: { color: 0x4a6a5a, i: 0.4, pos: [10, 24, -8] },
    fires: [{ color: 0x3a7a4a, i: 30, pos: [0, 3, -10] }], extras: 'fireflies' },
  'adi-10-swayamvara': { bg: 0x8a7358, fog: [30, 150], spawn: { pos: [-16, 5, -20], target: [2, 2.5, 6] },
    hemi: { sky: 0xd8c8a8, ground: 0x5a4a38, i: 0.65 }, sun: { color: 0xfff2d8, i: 1.8, pos: [30, 44, 20] },
    fires: [], extras: null },
  'adi-11-division': { bg: 0x4a3a52, fog: [28, 140], spawn: { pos: [0, 6, -28], target: [0, 2.5, 6] },
    hemi: { sky: 0x7a5a7a, ground: 0x2a2030, i: 0.55 }, sun: { color: 0xffb37a, i: 1.2, pos: [-30, 22, 20] },
    fires: [], extras: null },
  'adi-12-indraprastha': { bg: 0xd9a05a, fog: [40, 180], spawn: { pos: [38, 14, -48], target: [4, 9, 12] },
    hemi: { sky: 0xe8d0a8, ground: 0x4a5a42, i: 0.7 }, sun: { color: 0xffd8a0, i: 2.2, pos: [-40, 26, 30] },
    fires: [{ color: 0xff8c3a, i: 50, pos: [18, 1.5, 48] }], extras: 'embers' },
};

interface CastMember { arch: string; char: string; x: number; z: number; s: number }
// Cast placed near each scene's story heart; they turn to face the arriving camera.
const CAST: Record<string, CastMember[]> = {
  'adi-01-naimisha': [{ arch: 'sage', char: 'Sauti', x: -4, z: 6.5, s: 1 }, { arch: 'sage', char: 'Shaunaka', x: 4, z: 7, s: 0.95 }],
  'adi-02-snake-sacrifice': [{ arch: 'king', char: 'Janamejaya', x: -2.5, z: 5.5, s: 1.05 }, { arch: 'sage', char: 'Astika', x: 2.5, z: 6, s: 1 }],
  'adi-03-ganga': [{ arch: 'king', char: 'Shantanu', x: 3, z: 10, s: 1 }, { arch: 'princess', char: 'Ganga', x: 8.5, z: 11, s: 1 }],
  'adi-04-bhishma-vow': [{ arch: 'warrior', char: 'Bhishma', x: -2, z: 10, s: 1.15 }, { arch: 'king', char: 'Shantanu', x: 2.5, z: 10.5, s: 1 }],
  'adi-05-vyasa-line': [{ arch: 'sage', char: 'Vyasa', x: -1.5, z: 0, s: 1.1 }, { arch: 'princess', char: 'Satyavati', x: 2, z: 0.5, s: 1 }],
  'adi-06-births': [{ arch: 'princess', char: 'Kunti', x: -6, z: -10, s: 1 }, { arch: 'sage', char: 'Durvasa', x: -2.5, z: -9, s: 1 }],
  'adi-07-drona': [{ arch: 'sage', char: 'Drona', x: 3, z: 6, s: 1.05 }, { arch: 'warrior', char: 'Arjuna', x: -1, z: 7, s: 1 }],
  'adi-08-lakshagriha': [{ arch: 'warrior', char: 'Yudhishthira', x: -2, z: 2, s: 0.95 }, { arch: 'sage', char: 'Vidura', x: 2, z: 2.5, s: 1 }],
  'adi-09-hidimba': [{ arch: 'strongman', char: 'Bhima', x: -2, z: 4, s: 1.25 }, { arch: 'princess', char: 'Hidimbi', x: 2, z: 4.5, s: 1 }],
  'adi-10-swayamvara': [{ arch: 'princess', char: 'Draupadi', x: 0, z: 0, s: 1.05 }, { arch: 'warrior', char: 'Arjuna', x: 3.5, z: 0.5, s: 1 }],
  'adi-11-division': [{ arch: 'king', char: 'Dhritarashtra', x: -3, z: 0, s: 1.1 }, { arch: 'warrior', char: 'Yudhishthira', x: 3, z: 0.5, s: 1 }],
  'adi-12-indraprastha': [{ arch: 'warrior', char: 'Krishna', x: 0, z: 4, s: 1 }, { arch: 'warrior', char: 'Arjuna', x: 3, z: 4.5, s: 0.95 }],
};

interface Line { char: string; arch: string; line: string }

const SEG_SECONDS = 26; // journey seconds per scene at 1x

const canvas = document.getElementById('world') as HTMLCanvasElement;
const elTitle = document.getElementById('sceneTitle')!;
const elNarr = document.getElementById('narration')!;
const elProg = document.getElementById('progress')!;
const elBar = document.getElementById('journeybar') as HTMLElement;
const elInfo = document.getElementById('information')!;
const btnPause = document.getElementById('pause') as HTMLButtonElement;
const btnVoice = document.getElementById('voice') as HTMLButtonElement;
const btnSpeed = document.getElementById('speedcycle') as HTMLButtonElement;
const loader = document.getElementById('loader')!;
const poster = document.getElementById('poster') as HTMLImageElement;
const loadMsg = document.getElementById('loadmsg')!;

// UI rests invisible; any activity wakes it briefly. The journey never waits.
let awakeTimer: number | null = null;
function wakeUI() {
  elInfo.classList.add('awake');
  if (awakeTimer) window.clearTimeout(awakeTimer);
  awakeTimer = window.setTimeout(() => elInfo.classList.remove('awake'), 3500);
}
window.addEventListener('pointermove', wakeUI, { passive: true });
window.addEventListener('pointerdown', wakeUI);
window.addEventListener('keydown', wakeUI);

const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// 4-step toon gradient shared by every character.
const gradientMap = (() => {
  const data = new Uint8Array([110, 160, 210, 255]);
  const tex = new THREE.DataTexture(data, data.length, 1, THREE.RedFormat);
  tex.minFilter = THREE.NearestFilter;
  tex.magFilter = THREE.NearestFilter;
  tex.needsUpdate = true;
  return tex;
})();

function toonify(root: THREE.Object3D) {
  root.traverse((o) => {
    const mesh = o as THREE.Mesh;
    if (!mesh.isMesh) return;
    const old = mesh.material as THREE.MeshStandardMaterial | THREE.MeshStandardMaterial[];
    const first = Array.isArray(old) ? old[0] : old;
    const c = (first as THREE.MeshStandardMaterial)?.color ?? new THREE.Color(0xffffff);
    mesh.material = new THREE.MeshToonMaterial({
      color: c.clone(),
      emissive: c.clone().multiplyScalar(0.38),
      gradientMap,
    });
  });
}

function buildLights(group: THREE.Group, st: SceneStyle): THREE.PointLight[] {
  group.add(new THREE.HemisphereLight(st.hemi.sky, st.hemi.ground, st.hemi.i));
  const sun = new THREE.DirectionalLight(st.sun.color, st.sun.i);
  sun.position.set(...st.sun.pos);
  sun.castShadow = true;
  sun.shadow.mapSize.set(1024, 1024);
  sun.shadow.camera.left = -45; sun.shadow.camera.right = 45;
  sun.shadow.camera.top = 45; sun.shadow.camera.bottom = -45;
  sun.shadow.camera.far = 200;
  group.add(sun);
  const flickers: THREE.PointLight[] = [];
  for (const f of st.fires) {
    const p = new THREE.PointLight(f.color, f.i, 34, 1.8);
    p.position.set(...f.pos);
    group.add(p);
    flickers.push(p);
  }
  return flickers;
}

function addExtras(group: THREE.Group, st: SceneStyle, sceneId: string): (t: number, dt: number) => void {
  if (!st.extras || reducedMotion) return () => {};
  let seed = 0;
  for (const c of sceneId) seed = (seed * 31 + c.charCodeAt(0)) >>> 0;
  const rand = (() => { let a = seed; return () => { a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; })();
  const isFire = st.extras === 'embers';
  const n = isFire ? 60 : 80;
  const color = isFire ? 0xffb347 : 0x9adf6a;
  const cx = st.fires[0]?.pos[0] ?? 0;
  const cz = st.fires[0]?.pos[2] ?? 0;
  const spread = isFire ? 3 : 35;
  const pos = new Float32Array(n * 3);
  const spd = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    pos[i * 3] = cx + (rand() - 0.5) * spread * 2;
    pos[i * 3 + 1] = rand() * (isFire ? 5 : 6);
    pos[i * 3 + 2] = cz + (rand() - 0.5) * spread * 2;
    spd[i] = 0.6 + rand() * 1.4;
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const pts = new THREE.Points(geo, new THREE.PointsMaterial({
    color, size: isFire ? 0.16 : 0.14, transparent: true, opacity: 0.9,
  }));
  group.add(pts);
  return (t, dt) => {
    const p = geo.attributes.position as THREE.BufferAttribute;
    for (let i = 0; i < n; i++) {
      if (isFire) {
        let y = p.getY(i) + spd[i] * dt;
        if (y > 6) y = 0.3;
        p.setY(i, y);
        p.setX(i, p.getX(i) + Math.sin(y * 3 + i) * dt * 0.3);
      } else {
        p.setX(i, p.getX(i) + Math.sin(t * 0.8 + i * 2.1) * dt * 0.7);
        p.setY(i, p.getY(i) + Math.cos(t * 0.6 + i) * dt * 0.4);
      }
    }
    p.needsUpdate = true;
  };
}

// In-world speech bubble: one rounded card floating over the speaker.
const bubble = (() => {
  const cv = document.createElement('canvas');
  cv.width = 512; cv.height = 256;
  const g = cv.getContext('2d')!;
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  const mat = new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: true });
  const sprite = new THREE.Sprite(mat);
  sprite.scale.set(5.2, 2.6, 1);
  sprite.visible = false;
  function wrap(text: string, max: number): string[] {
    const words = text.split(' ');
    const out: string[] = [];
    let cur = '';
    for (const w of words) {
      if ((cur + ' ' + w).trim().length > max && cur) { out.push(cur); cur = w; }
      else cur = (cur + ' ' + w).trim();
    }
    if (cur) out.push(cur);
    return out.slice(0, 4);
  }
  return {
    sprite,
    show(speaker: string, line: string) {
      g.clearRect(0, 0, 512, 256);
      g.fillStyle = 'rgba(10,12,18,0.88)';
      g.strokeStyle = '#c9a227';
      g.lineWidth = 4;
      g.beginPath();
      (g as CanvasRenderingContext2D).roundRect(8, 8, 496, 200, 26);
      g.fill(); g.stroke();
      // tail
      g.beginPath();
      g.moveTo(226, 208); g.lineTo(286, 208); g.lineTo(256, 248); g.closePath();
      g.fillStyle = 'rgba(10,12,18,0.88)';
      g.fill();
      g.fillStyle = '#c9a227';
      g.font = '600 30px Georgia, serif';
      g.fillText(speaker.toUpperCase().slice(0, 24), 36, 58);
      g.fillStyle = '#f5f0e1';
      g.font = 'italic 34px Georgia, serif';
      wrap(line, 30).forEach((ln, i) => g.fillText(ln, 36, 108 + i * 38));
      tex.needsUpdate = true;
      mat.opacity = 1;
      sprite.visible = true;
    },
    hide() { sprite.visible = false; },
  };
})();

function speakLine(text: string, voice?: { pitch: number; rate: number }, enabled = true) {
  try {
    speechSynthesis.cancel();
    if (!enabled) return;
    const u = new SpeechSynthesisUtterance(text);
    if (voice) {
      u.pitch = voice.pitch;
      u.rate = voice.rate;
    }
    speechSynthesis.speak(u);
  } catch { /* TTS unavailable */ }
}

async function main() {
  const pkg: ChapterPackage = await loadChapterPackage('./package');
  const scenes = pkg.scenes;
  const dlg = await (await fetch('./package/dialogue.json')).json() as {
    voices: Record<string, { pitch: number; rate: number }>;
    scenes: Record<string, Line[]>;
  };
  const engine = new Engine(canvas);

  const draco = new DRACOLoader();
  draco.setDecoderPath('./draco/');
  const gltf = new GLTFLoader();
  gltf.setDRACOLoader(draco);

  // Character archetype cache: load once, clone per placement.
  const charCache = new Map<string, THREE.Group>();
  async function getChar(arch: string): Promise<THREE.Group | null> {
    if (!charCache.has(arch)) {
      try {
        const loaded = await gltf.loadAsync(`./package/assets/models/characters/${arch}.glb`);
        const g = loaded.scene as THREE.Group;
        toonify(g);
        charCache.set(arch, g);
      } catch (e) {
        console.warn('character missing:', arch, e);
        return null;
      }
    }
    const tpl = charCache.get(arch);
    return tpl ? tpl.clone() as THREE.Group : null;
  }

  let index = 0; // journey order = scene order
  let paused = false;
  let speed = reducedMotion ? 0 : 1;
  let voiceOn = true;
  let segElapsed = 0; // seconds into current scene segment (at 1x scale)
  let lineIdx = -1;
  let journeyDone = false;

  const segLen = () => SEG_SECONDS;
  const totalLen = () => SEG_SECONDS * scenes.length;

  const SPEEDS = [1, 2, 0.5];
  function setSpeed(s: number) {
    speed = s;
    btnSpeed.textContent = s === 0 ? 'Stopped' : `${s}×`;
    btnSpeed.classList.toggle('on', s !== 1);
    engine.idleAutoRotate = !paused && speed === 0;
  }

  // Speaking character groups, for bubble anchoring.
  const speakers = new Map<string, THREE.Group>();

  async function enterScene(i: number) {
    index = i;
    const s = scenes[index];
    const sceneId = s.sceneId;
    const st = STYLE[sceneId];
    elTitle.textContent = `${index + 1}. ${s.title}`;
    elNarr.textContent = pkg.narrationById.get(sceneId) ?? s.narrativeBeat;
    elProg.textContent = `${sceneId} · ${s.location} · ${s.emotion}`;
    stopSpeech();
    void playSceneAmbience(pkg.audioFileByScene.get(sceneId), ambienceForScene(sceneId));

    loader.classList.add('visible');
    poster.src = `./package/assets/renders/${sceneId}.jpg`;
    loadMsg.textContent = `Entering ${s.title}…`;

    const group = new THREE.Group();
    const flickers = buildLights(group, st);
    let update: (t: number, dt: number) => void = () => {};
    try {
      const loaded = await gltf.loadAsync(`./package/assets/models/${sceneId}.glb`);
      group.add(loaded.scene);
    } catch (e) {
      console.warn('GLB failed, primitive fallback:', sceneId, e);
      const fallback = BUILDERS[sceneId]();
      group.add(fallback.env.group);
      update = fallback.env.update;
    }
    // Cast: toon characters placed around the story heart, facing the arrival.
    const camArrive = new THREE.Vector3(...st.spawn.pos);
    speakers.clear();
    for (const c of CAST[sceneId] ?? []) {
      const ch = await getChar(c.arch);
      if (!ch) continue;
      ch.position.set(c.x, 0.45, c.z);
      ch.scale.setScalar(c.s);
      ch.lookAt(camArrive.x, 0.45, camArrive.z);
      ch.rotateY(Math.PI); // models face -Z; turn them toward camera
      group.add(ch);
      speakers.set(c.char, ch);
    }
    group.add(bubble.sprite);
    bubble.hide();
    const extraUpdate = addExtras(group, st, sceneId);
    const seedF = st.fires.map((f) => f.i);
    engine.setEnvironment({
      group,
      spawn: st.spawn,
      update: (t, dt) => {
        flickers.forEach((l, k) => {
          l.intensity = seedF[k] * (0.86 + 0.14 * Math.sin(t * 12 + k * 2.4) * Math.sin(t * 5.3 + k));
        });
        update(t, dt);
        extraUpdate(t, dt);
        // Journey flight: drift camera + target forward along the dolly vector.
        if (speed > 0 && !paused && !journeyDone) {
          const seg = flightSeg(sceneId);
          const step = seg.dir.clone().multiplyScalar((seg.len / segLen()) * dt * speed);
          engine.camera.position.add(step);
          engine.controls.target.add(step);
          segElapsed += dt * speed;
          if (segElapsed >= segLen()) {
            segElapsed = 0;
            void advance();
          }
        }
        updateJourneyUI();
      },
    }, st.bg, st.fog[0], st.fog[1]);
    segElapsed = 0;
    lineIdx = -1;
    setTimeout(() => loader.classList.remove('visible'), 450);
  }

  // Straight dolly per scene: from spawn toward the story heart, 38% of the way + lift.
  const segCache = new Map<string, { dir: THREE.Vector3; len: number }>();
  function flightSeg(sceneId: string) {
    let seg = segCache.get(sceneId);
    if (!seg) {
      const st = STYLE[sceneId];
      const a = new THREE.Vector3(...st.spawn.pos);
      const b = a.clone().lerp(new THREE.Vector3(...st.spawn.target), 0.25);
      b.y += 1.5;
      const dir = b.clone().sub(a);
      seg = { dir: dir.clone().normalize(), len: dir.length() };
      segCache.set(sceneId, seg);
    }
    return seg;
  }

  function lines(): Line[] {
    return dlg.scenes[scenes[index].sceneId] ?? [];
  }

  function updateJourneyUI() {
    const ls = lines();
    const per = ls.length ? segLen() / ls.length : segLen();
    const li = Math.min(ls.length - 1, Math.floor(segElapsed / per));
    if (li !== lineIdx && ls[li]) {
      lineIdx = li;
      const who = speakers.get(ls[li].char);
      if (who) {
        bubble.sprite.position.copy(who.position);
        bubble.sprite.position.y += 2.9 * who.scale.x;
        bubble.show(ls[li].char, ls[li].line);
      } else {
        bubble.hide();
      }
      const v = dlg.voices[ls[li].char];
      speakLine(ls[li].line, v, voiceOn && !paused);
    }
    const done = scenes.slice(0, index).length * segLen() + Math.min(segElapsed, segLen());
    elBar.style.width = `${(done / totalLen()) * 100}%`;
  }

  async function advance() {
    if (index + 1 >= scenes.length) {
      journeyDone = true;
      setSpeed(0);
      bubble.hide();
      return;
    }
    loader.classList.add('visible');
    await enterScene(index + 1);
  }

  btnPause.onclick = () => {
    paused = !paused;
    btnPause.textContent = paused ? 'Play' : 'Pause';
    if (paused) { stopSpeech(); bubble.hide(); }
    else { lineIdx = -1; wakeUI(); }
    engine.idleAutoRotate = !paused && speed === 0;
  };
  btnVoice.onclick = () => {
    voiceOn = !voiceOn;
    btnVoice.textContent = voiceOn ? 'Voice: on' : 'Voice: off';
    if (!voiceOn) stopSpeech();
  };
  btnSpeed.onclick = () => {
    const next = SPEEDS[(SPEEDS.indexOf(speed) + 1) % SPEEDS.length];
    setSpeed(next);
    if (paused && next > 0) btnPause.click();
    wakeUI();
  };
  window.addEventListener('keydown', (e) => {
    if (e.code === 'Space' && (e.target as HTMLElement)?.tagName !== 'BUTTON') {
      e.preventDefault();
      btnPause.click();
    }
  });

  const unlock = () => {
    const s = scenes[index];
    void playSceneAmbience(pkg.audioFileByScene.get(s.sceneId), ambienceForScene(s.sceneId));
    window.removeEventListener('pointerdown', unlock);
    window.removeEventListener('keydown', unlock);
  };
  window.addEventListener('pointerdown', unlock);
  window.addEventListener('keydown', unlock);

  setSpeed(reducedMotion ? 0 : 1);
  await enterScene(pkg.entryIndex);
  index = pkg.entryIndex;
}

main().catch((e: unknown) => {
  elTitle.textContent = 'Failed to load chapter package';
  elNarr.textContent = e instanceof Error ? e.message : String(e);
  loader.classList.remove('visible');
});

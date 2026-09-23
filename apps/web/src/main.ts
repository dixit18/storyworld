// Storyworld journey player: one continuous flight through Adi Parva.
// No scene buttons — the story moves; the user sets pace (pause / 0.5x / 1x / 2x),
// looks around freely, and hears each scene's dialogue on its characters.
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';
import { clone as skeletonClone } from 'three/examples/jsm/utils/SkeletonUtils.js';
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
  sky: [number, number]; // top, horizon
  exposure: number;
  spawn: { pos: [number, number, number]; target: [number, number, number] };
  hemi: { sky: number; ground: number; i: number };
  sun: { color: number; i: number; pos: [number, number, number] };
  fires: { color: number; i: number; pos: [number, number, number] }[];
  extras: 'embers' | 'fireflies' | null;
}

// (Unchanged environment art direction — spawns double as journey waypoints.)
const STYLE: Record<string, SceneStyle> = {
  'adi-01-naimisha': { bg: 0x070d0a, fog: [14, 85], sky: [0x02040a, 0x0d1a24], exposure: 1.2, spawn: { pos: [5.0, 2.0, -4.5], target: [0, 1.4, 0] },
    hemi: { sky: 0x2a3a4a, ground: 0x0a0f0a, i: 0.7 }, sun: { color: 0x8fa8c8, i: 0.5, pos: [-30, 40, 30] },
    fires: [{ color: 0xff8c3a, i: 90, pos: [0, 2.5, 0] }], extras: 'embers' },
  'adi-02-snake-sacrifice': { bg: 0x120606, fog: [20, 110], sky: [0x0a0505, 0x2a0d0a], exposure: 1.2, spawn: { pos: [10, 4, -13], target: [0, 3, 2] },
    hemi: { sky: 0x3a1a12, ground: 0x0a0605, i: 0.65 }, sun: { color: 0xff6a3a, i: 0.6, pos: [-20, 30, 10] },
    fires: [{ color: 0xff6a3a, i: 160, pos: [0, 3, 0] }], extras: 'embers' },
  'adi-03-ganga': { bg: 0x3a4a5e, fog: [35, 180], sky: [0x4a6a9a, 0xe8a06a], exposure: 1.5, spawn: { pos: [2, 7.5, -40], target: [6, 0.5, 14] },
    hemi: { sky: 0x9db8d8, ground: 0x2a3a2a, i: 0.7 }, sun: { color: 0xffe0b0, i: 1.6, pos: [40, 30, -30] },
    fires: [], extras: null },
  'adi-04-bhishma-vow': { bg: 0x171006, fog: [15, 90], sky: [0x171006, 0x3a2a18], exposure: 1.2, spawn: { pos: [11, 3.4, -12], target: [0, 3.5, 13] },
    hemi: { sky: 0x5a4a30, ground: 0x14100a, i: 0.5 }, sun: { color: 0xffd88a, i: 1.2, pos: [10, 24, 14] },
    fires: [{ color: 0xffb35a, i: 30, pos: [-8, 3.5, -2] }, { color: 0xffb35a, i: 30, pos: [8, 3.5, -2] }], extras: null },
  'adi-05-vyasa-line': { bg: 0x0d0d14, fog: [12, 65], sky: [0x0d0d14, 0x2a2438], exposure: 1.15, spawn: { pos: [8, 2.8, -11], target: [0, 1.4, 6] },
    hemi: { sky: 0x3a3450, ground: 0x0a0a10, i: 0.45 }, sun: { color: 0x8a7aa8, i: 0.5, pos: [0, 20, -10] },
    fires: [{ color: 0xff9a3a, i: 25, pos: [5, 2.2, -4] }], extras: null },
  'adi-06-births': { bg: 0x87a6c4, fog: [45, 200], sky: [0x3a6ab8, 0xbcd4e8], exposure: 1.5, spawn: { pos: [2, 3.5, 6], target: [-10, 1, -18] },
    hemi: { sky: 0xbdd4e8, ground: 0x3a5a3a, i: 0.8 }, sun: { color: 0xfff2d8, i: 2.0, pos: [40, 50, 20] },
    fires: [], extras: null },
  'adi-07-drona': { bg: 0xb8a888, fog: [45, 200], sky: [0x5a7a9e, 0xd8bd93], exposure: 1.5, spawn: { pos: [0, 4, -24], target: [0, 2.5, 16] },
    hemi: { sky: 0xcfd8e0, ground: 0x6a5638, i: 0.7 }, sun: { color: 0xffe8c0, i: 2.0, pos: [30, 44, 18] },
    fires: [], extras: null },
  'adi-08-lakshagriha': { bg: 0x0d0505, fog: [22, 120], sky: [0x0d0505, 0x3a140c], exposure: 1.2, spawn: { pos: [26, 10, -34], target: [0, 5, 8] },
    hemi: { sky: 0x3a1a10, ground: 0x0a0605, i: 0.65 }, sun: { color: 0xff8c3a, i: 0.6, pos: [-24, 26, 12] },
    fires: [{ color: 0xff8c3a, i: 110, pos: [-9, 2.5, -8] }, { color: 0xff8c3a, i: 90, pos: [9, 2.5, -8] }], extras: 'embers' },
  'adi-09-hidimba': { bg: 0x040806, fog: [10, 60], sky: [0x020604, 0x0d1f18], exposure: 1.25, spawn: { pos: [0, 2.8, -14], target: [0, 3, 12] },
    hemi: { sky: 0x1a2a24, ground: 0x050805, i: 0.7 }, sun: { color: 0x4a6a5a, i: 0.4, pos: [10, 24, -8] },
    fires: [{ color: 0x3a7a4a, i: 30, pos: [0, 3, -10] }], extras: 'fireflies' },
  'adi-10-swayamvara': { bg: 0x8a7358, fog: [30, 150], sky: [0x6a7a9e, 0xd8b078], exposure: 1.4, spawn: { pos: [-16, 5, -20], target: [2, 2.5, 6] },
    hemi: { sky: 0xd8c8a8, ground: 0x5a4a38, i: 0.65 }, sun: { color: 0xfff2d8, i: 1.8, pos: [30, 44, 20] },
    fires: [], extras: null },
  'adi-11-division': { bg: 0x4a3a52, fog: [28, 140], sky: [0x2a2440, 0xc0705a], exposure: 1.3, spawn: { pos: [0, 6, -28], target: [0, 2.5, 6] },
    hemi: { sky: 0x7a5a7a, ground: 0x2a2030, i: 0.55 }, sun: { color: 0xffb37a, i: 1.2, pos: [-30, 22, 20] },
    fires: [], extras: null },
  'adi-12-indraprastha': { bg: 0xd9a05a, fog: [40, 180], sky: [0x5a7ab0, 0xf0a05a], exposure: 1.5, spawn: { pos: [38, 14, -48], target: [4, 9, 12] },
    hemi: { sky: 0xe8d0a8, ground: 0x4a5a42, i: 0.7 }, sun: { color: 0xffd8a0, i: 2.2, pos: [-40, 26, 30] },
    fires: [{ color: 0xff8c3a, i: 50, pos: [18, 1.5, 48] }], extras: 'embers' },
};

interface CastMember { arch: string; char: string; x: number; z: number; s: number }
// Per-character cloth tints so same-archetype cast never reads as clones.
// Colors are linear-space RGB triplets for MeshStandardMaterial.color.
const VARIETY: Record<string, { dhoti?: [number, number, number]; shawl?: [number, number, number]; beard?: [number, number, number] }> = {
  Sauti: { dhoti: [0.93, 0.88, 0.76], shawl: [0.78, 0.34, 0.12], beard: [0.82, 0.82, 0.80] },
  Rishi: { dhoti: [0.95, 0.62, 0.22], shawl: [0.60, 0.26, 0.10], beard: [0.45, 0.43, 0.40] },
  Shaunaka: { dhoti: [0.88, 0.82, 0.70], shawl: [0.55, 0.15, 0.08], beard: [0.90, 0.89, 0.86] },
  Astika: { dhoti: [0.90, 0.85, 0.72], shawl: [0.30, 0.42, 0.22], beard: [0.82, 0.82, 0.80] },
  Vyasa: { dhoti: [0.93, 0.88, 0.76], shawl: [0.72, 0.58, 0.20], beard: [0.55, 0.53, 0.50] },
};
// Cast placed near each scene's story heart; they turn to face the arriving camera.
const CAST: Record<string, CastMember[]> = {
  'adi-01-naimisha': [{ arch: 'sage', char: 'Sauti', x: 3.0, z: 2.0, s: 1.25 }, { arch: 'sage', char: 'Rishi', x: 3.93, z: 3.17, s: 1.0 }, { arch: 'sage', char: 'Shaunaka', x: -3.0, z: -2.0, s: 1.1 }],
  'adi-02-snake-sacrifice': [{ arch: 'king', char: 'Janamejaya', x: -2.5, z: 5.5, s: 1.05 }, { arch: 'sage', char: 'Astika', x: 2.5, z: 6, s: 1 }],
  'adi-03-ganga': [{ arch: 'king', char: 'Shantanu', x: 3, z: 10, s: 1 }, { arch: 'princess', char: 'Ganga', x: 8.5, z: 11, s: 1 }],
  'adi-04-bhishma-vow': [{ arch: 'warrior', char: 'Bhishma', x: -2, z: 10, s: 1.15 }, { arch: 'king', char: 'Shantanu', x: 2.5, z: 10.5, s: 1 }],
  'adi-05-vyasa-line': [{ arch: 'sage', char: 'Vyasa', x: -1.5, z: 0, s: 1.1 }, { arch: 'princess', char: 'Satyavati', x: 2, z: 0.5, s: 1 }],
  'adi-06-births': [{ arch: 'princess', char: 'Kunti', x: -6, z: -10, s: 1 }, { arch: 'sage', char: 'Durvasa', x: -2.5, z: -9, s: 1 }],
  'adi-07-drona': [{ arch: 'sage', char: 'Drona', x: 3, z: 6, s: 1.05 }, { arch: 'ranger', char: 'Arjuna', x: -1, z: 7, s: 1 }],
  'adi-08-lakshagriha': [{ arch: 'warrior', char: 'Yudhishthira', x: -2, z: 2, s: 0.95 }, { arch: 'sage', char: 'Vidura', x: 2, z: 2.5, s: 1 }],
  'adi-09-hidimba': [{ arch: 'strongman', char: 'Bhima', x: -2, z: 4, s: 1.25 }, { arch: 'princess', char: 'Hidimbi', x: 2, z: 4.5, s: 1 }],
  'adi-10-swayamvara': [{ arch: 'princess', char: 'Draupadi', x: 0, z: 0, s: 1.05 }, { arch: 'ranger', char: 'Arjuna', x: 3.5, z: 0.5, s: 1 }],
  'adi-11-division': [{ arch: 'king', char: 'Dhritarashtra', x: -3, z: 0, s: 1.1 }, { arch: 'warrior', char: 'Yudhishthira', x: 3, z: 0.5, s: 1 }],
  'adi-12-indraprastha': [{ arch: 'warrior', char: 'Krishna', x: 0, z: 4, s: 1 }, { arch: 'ranger', char: 'Arjuna', x: 3, z: 4.5, s: 0.95 }],
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
// ?freeze=1 pins spawn framing for staging shots (no wake/pan/flight/TTS).
const FREEZE = new URLSearchParams(location.search).has('freeze');
let awakeTimer: number | null = null;
function wakeUI() {
  elInfo.classList.add('awake');
  if (awakeTimer) window.clearTimeout(awakeTimer);
  awakeTimer = window.setTimeout(() => elInfo.classList.remove('awake'), 3500);
}
if (!FREEZE) {
  window.addEventListener('pointermove', wakeUI, { passive: true });
  window.addEventListener('pointerdown', wakeUI);
  window.addEventListener('keydown', wakeUI);
}

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
    if (/flame/i.test(mesh.name)) {
      // Toon fire: flat warm orange, never blown-out white.
      mesh.material = new THREE.MeshBasicMaterial({ color: 0xff8c1a });
      return;
    }
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

function makeSkyDome(top: number, horizon: number): THREE.Mesh {
  const cv = document.createElement('canvas');
  cv.width = 4; cv.height = 256;
  const g = cv.getContext('2d')!;
  const cTop = `#${top.toString(16).padStart(6, '0')}`;
  const cHor = `#${horizon.toString(16).padStart(6, '0')}`;
  const grad = g.createLinearGradient(0, 0, 0, 256);
  grad.addColorStop(0.0, cTop);
  grad.addColorStop(0.46, cTop);
  grad.addColorStop(0.52, cHor);
  grad.addColorStop(0.58, cHor);
  grad.addColorStop(1.0, '#050505');
  g.fillStyle = grad;
  g.fillRect(0, 0, 4, 256);
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  const mat = new THREE.MeshBasicMaterial({ map: tex, side: THREE.BackSide, fog: false, depthWrite: false });
  const dome = new THREE.Mesh(new THREE.SphereGeometry(420, 24, 16), mat);
  dome.frustumCulled = false;
  dome.renderOrder = -10;
  return dome;
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
  // Fill from the arrival side so faces never go pitch black when backlit.
  const fill = new THREE.DirectionalLight(0xffe0b8, 0.55);
  fill.position.set(st.spawn.pos[0], st.spawn.pos[1] + 4, st.spawn.pos[2]);
  fill.target.position.set(0, 1, 0);
  group.add(fill, fill.target);
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
  // Soft round sprite so sparks/fireflies read as glow, not hexagons.
  const dotTex = (() => {
    const cv = document.createElement('canvas');
    cv.width = 64; cv.height = 64;
    const g = cv.getContext('2d')!;
    const grad = g.createRadialGradient(32, 32, 2, 32, 32, 30);
    grad.addColorStop(0, 'rgba(255,255,255,1)');
    grad.addColorStop(0.45, 'rgba(255,255,255,0.7)');
    grad.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = grad;
    g.fillRect(0, 0, 64, 64);
    return new THREE.CanvasTexture(cv);
  })();
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
    color, size: isFire ? 0.16 : 0.14, map: dotTex, transparent: true,
    opacity: 0.9, depthWrite: false,
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
  const mat = new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: false });
  const sprite = new THREE.Sprite(mat);
  sprite.scale.set(6, 3, 1);
  sprite.renderOrder = 999;
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

// Cartoon faces: a billboard sprite per character — big eyes, brows, mouth —
// with random blinks and a talking mouth while their line plays.
const _X_AXIS = new THREE.Vector3(1, 0, 0);
const _nodQ = new THREE.Quaternion();
function makeFace(stern: boolean): {
  sprite: THREE.Sprite;
  update: (t: number, dt: number, talking: boolean) => void;
} {
  const cv = document.createElement('canvas');
  cv.width = 128; cv.height = 128;
  const g = cv.getContext('2d')!;
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, transparent: true }));
  let nextBlink = 1.5 + Math.random() * 2.5;
  let blinkLeft = -1;
  let mouthPhase = 0;
  let mouthOpen = false;
  function draw(talking: boolean) {
    g.clearRect(0, 0, 128, 128);
    const closed = blinkLeft >= 0;
    for (const ex of [42, 86]) {
      if (closed) {
        g.strokeStyle = '#1a1210'; g.lineWidth = 5; g.lineCap = 'round';
        g.beginPath(); g.moveTo(ex - 13, 54); g.lineTo(ex + 13, 54); g.stroke();
      } else {
        g.fillStyle = '#fff';
        g.beginPath(); g.ellipse(ex, 50, 14, 17, 0, 0, Math.PI * 2); g.fill();
        g.fillStyle = '#1a1210';
        g.beginPath(); g.arc(ex, 53, 6.5, 0, Math.PI * 2); g.fill();
        g.fillStyle = '#fff';
        g.beginPath(); g.arc(ex - 2, 50, 2.2, 0, Math.PI * 2); g.fill();
      }
    }
    g.strokeStyle = '#1a1210'; g.lineWidth = 6; g.lineCap = 'round';
    g.beginPath(); g.moveTo(28, 28); g.lineTo(56, stern ? 21 : 28); g.stroke();
    g.beginPath(); g.moveTo(72, stern ? 21 : 28); g.lineTo(100, 28); g.stroke();
    if (talking) {
      const open = 5 + 6 * (0.5 + 0.5 * Math.sin(mouthPhase));
      g.fillStyle = '#401410';
      g.beginPath(); g.ellipse(64, 98, 10, open, 0, 0, Math.PI * 2); g.fill();
    } else {
      g.strokeStyle = '#1a1210'; g.lineWidth = 5;
      g.beginPath(); g.arc(64, 88, 10, 0.15 * Math.PI, 0.85 * Math.PI); g.stroke();
    }
    tex.needsUpdate = true;
  }
  draw(false);
  return {
    sprite,
    update(t, dt, talking) {
      if (blinkLeft >= 0) {
        blinkLeft -= dt;
        if (blinkLeft < 0) { nextBlink = t + 2 + Math.random() * 2.5; draw(talking); }
      } else if (t > nextBlink) { blinkLeft = 0.12; draw(talking); }
      if (talking) { mouthPhase += dt * 14; mouthOpen = true; draw(true); }
      else if (mouthOpen) { mouthOpen = false; mouthPhase = 0; draw(false); }
    },
  };
}

async function main() {
  // Bump when art changes so browsers stop serving stale GLBs/posters.
  const CB = 'cb5';
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

  // Character archetype cache: Quaternius CC0 heroes (rigged + idle) for males,
  // our toon princess for female roles. Templates are shared; placements clone.
  const charCache = new Map<string, { group: THREE.Group; clips: THREE.AnimationClip[] }>();
  async function getChar(arch: string): Promise<{ group: THREE.Group; clips: THREE.AnimationClip[] } | null> {
    if (!charCache.has(arch)) {
      try {
        const url = arch === 'princess'
          ? `./package/assets/models/characters/princess.glb?${CB}`
          : `./package/assets/models/cast/${arch}.glb?${CB}`;
        const loaded = await gltf.loadAsync(url);
        const g = loaded.scene as THREE.Group;
        if (arch === 'princess') toonify(g);
        engine.markShared(g);
        charCache.set(arch, { group: g, clips: loaded.animations ?? [] });
      } catch (e) {
        console.warn('character missing:', arch, e);
        return null;
      }
    }
    return charCache.get(arch) ?? null;
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

  // Speaking character groups + bubble heights, for bubble anchoring.
  const speakers = new Map<string, { g: THREE.Group; h: number }>();
  const faces = new Map<string, { sprite: THREE.Sprite; update: (t: number, dt: number, talking: boolean) => void }>();
  let talkingChar: string | null = null;
  let focusPoint: THREE.Vector3 | null = null;
  let nod: { g: THREE.Group; start: number } | null = null;

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
    poster.src = `./package/assets/renders/${sceneId}.jpg?${CB}`;
    loadMsg.textContent = `Entering ${s.title}…`;

    const group = new THREE.Group();
    group.add(makeSkyDome(st.sky[0], st.sky[1]));
    const flickers = buildLights(group, st);
    let update: (t: number, dt: number) => void = () => {};
    try {
      const loaded = await gltf.loadAsync(`./package/assets/models/${sceneId}.glb?${CB}`);
      loaded.scene.traverse((o) => {
        const mesh = o as THREE.Mesh;
        if (!mesh.isMesh) return;
        if (/flame/i.test(mesh.name)) {
          // Toon fire: flat warm orange, never blown-out white.
          mesh.material = new THREE.MeshBasicMaterial({ color: 0xff8c1a });
        } else if (/firefly/i.test(mesh.name)) {
          // Baked glow-dots: small, pale green, unlit, so they read as fireflies.
          mesh.material = new THREE.MeshBasicMaterial({ color: 0x9adf6a });
          mesh.scale.multiplyScalar(0.55);
        }
      });
      group.add(loaded.scene);
    } catch (e) {
      console.warn('GLB failed, primitive fallback:', sceneId, e);
      const fallback = BUILDERS[sceneId]();
      group.add(fallback.env.group);
      update = fallback.env.update;
    }
    // Cast: rigged heroes placed around the story heart, facing the arrival,
    // idle animation running.
    const camArrive = new THREE.Vector3(...st.spawn.pos);
    speakers.clear();
    faces.clear();
    talkingChar = null;
    const mixers: THREE.AnimationMixer[] = [];
    for (const c of CAST[sceneId] ?? []) {
      const tpl = await getChar(c.arch);
      if (!tpl) continue;
      const ch = skeletonClone(tpl.group) as THREE.Group;
      ch.position.set(c.x, 0, c.z);
      ch.scale.setScalar(c.s);
      ch.lookAt(camArrive.x, 0, camArrive.z);
      // Own-kit models are authored facing Blender +Y (= three -Z after Yup
      // export); Quaternius face +Z. Flip ours so all face the arrival.
      if (c.arch === 'sage') ch.rotateY(Math.PI);
      ch.userData.baseQuat = ch.quaternion.clone();
      ch.traverse((o) => { o.frustumCulled = false; });
      const idle = tpl.clips.find((a) => /idle/i.test(a.name)) ?? tpl.clips[0];
      if (idle) {
        const mixer = new THREE.AnimationMixer(ch);
        mixer.clipAction(idle.clone()).play();
        mixers.push(mixer);
      }
      group.add(ch);
      speakers.set(c.char, { g: ch, h: c.arch === 'princess' ? 2.9 : 2.5 });
      // Variety: per-character dhoti/shawl/beard tints (materials cloned per
      // placement so the cached template stays pristine).
      const vary = VARIETY[c.char];
      if (vary) {
        ch.traverse((o) => {
          const mesh = o as THREE.Mesh;
          if (!mesh.isMesh) return;
          const m = mesh.material as THREE.MeshStandardMaterial;
          const n = (m.name || '').toLowerCase();
          const tint = n.includes('dhoti') ? vary.dhoti : n.includes('shawl') ? vary.shawl
            : (n.includes('beard') || n.includes('mustache')) ? vary.beard : null;
          if (tint) {
            const cp = m.clone();
            cp.color.setRGB(...tint);
            mesh.material = cp;
          }
        });
      }
      // Face: billboard features on the head, front (+Z after lookAt).
      // Skipped for our own sage (modeled face + bone-blink in its Idle).
      if (c.arch !== 'sage') {
        const face = makeFace(/warrior|king|bhishma|drona/i.test(`${c.arch} ${c.char}`));
        const fy = (c.arch === 'princess' ? 1.9 : 1.62) * c.s;
        face.sprite.scale.set(0.8 * c.s, 0.8 * c.s, 1);
        face.sprite.position.set(0, fy, 0.26 * c.s);
        ch.add(face.sprite);
        faces.set(c.char, face);
      }
    }
    group.add(bubble.sprite);
    bubble.hide();
    const extraUpdate = addExtras(group, st, sceneId);
    const seedF = st.fires.map((f) => f.i);
    engine.renderer.toneMappingExposure = st.exposure;
    engine.setEnvironment({
      group,
      spawn: st.spawn,
      update: (t, dt) => {
        flickers.forEach((l, k) => {
          l.intensity = seedF[k] * (0.86 + 0.14 * Math.sin(t * 12 + k * 2.4) * Math.sin(t * 5.3 + k));
        });
        update(t, dt);
        extraUpdate(t, dt);
        for (const m of mixers) m.update(dt);
        for (const [name, f] of faces) f.update(t, dt, !paused && talkingChar === name);
        // Speaker connection: attention eases toward the speaker (unless the
        // user recently took the camera), who nods their line.
        if (focusPoint && !paused && !FREEZE && engine.idleSeconds() > 4) {
          engine.controls.target.lerp(focusPoint, 1 - Math.exp(-1.6 * dt));
        }
        if (nod) {
          const k = (performance.now() / 1000 - nod.start) / 0.9;
          if (k >= 1) { nod.g.quaternion.copy(nod.g.userData.baseQuat); nod = null; }
          else {
            _nodQ.setFromAxisAngle(_X_AXIS, -0.13 * Math.sin(k * Math.PI));
            nod.g.quaternion.copy(nod.g.userData.baseQuat).multiply(_nodQ);
          }
        }
        // Journey flight: drift camera + target forward along the dolly vector.
        if (speed > 0 && !paused && !journeyDone && !FREEZE) {
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
    focusPoint = null;
    nod = null;
    setTimeout(() => loader.classList.remove('visible'), 450);
  }

  // Straight dolly per scene: from spawn toward the story heart, 38% of the way + lift.
  const segCache = new Map<string, { dir: THREE.Vector3; len: number }>();
  function flightSeg(sceneId: string) {
    let seg = segCache.get(sceneId);
    if (!seg) {
      const st = STYLE[sceneId];
      const a = new THREE.Vector3(...st.spawn.pos);
      const b = a.clone().lerp(new THREE.Vector3(...st.spawn.target), 0.18);
      b.y += 2.0;
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
        bubble.sprite.position.copy(who.g.position);
        bubble.sprite.position.y += (who.h + 0.9) * who.g.scale.x;
        bubble.show(ls[li].char, ls[li].line);
        talkingChar = ls[li].char;
        // Lean in: attention glides between speaker and story heart so the
        // pair composition holds instead of centering one head.
        const heart = new THREE.Vector3(...STYLE[scenes[index].sceneId].spawn.target);
        focusPoint = who.g.position.clone().lerp(heart, 0.45).add(new THREE.Vector3(0, 1.0 * who.g.scale.x, 0));
        nod = { g: who.g, start: performance.now() / 1000 };
      } else {
        bubble.hide();
        talkingChar = null;
      }
      const v = dlg.voices[ls[li].char];
      speakLine(ls[li].line, v, voiceOn && !paused && !FREEZE);
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
    if (e.key === '1') setSpeed(0.5);
    if (e.key === '2') setSpeed(1);
    if (e.key === '3') setSpeed(2);
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

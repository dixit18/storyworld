// 12 explorable Adi Parva environments. Every builder returns { group, update, spawn }.
// Placement is deterministic: prng(seedFor(storyId, chapterId, sceneId)).
import * as THREE from 'three';
import { seedFor, prng } from '@storyworld/world-runtime';
import type { EnvResult } from './engine';

const SID = 'mahabharata';
const CH = 'chapter-01-adi-parva';
type Rand = () => number;
type Anim = (t: number, dt: number) => void;

// ---------- shared helpers ----------
const M = (color: number, o: THREE.MeshStandardMaterialParameters = {}) =>
  new THREE.MeshStandardMaterial({ color, roughness: 0.85, metalness: 0.05, ...o });
const E = (color: number, emissive: number, i = 1.6) =>
  new THREE.MeshStandardMaterial({ color, emissive, emissiveIntensity: i, roughness: 0.6 });

function solid(geo: THREE.BufferGeometry, mat: THREE.Material, x = 0, y = 0, z = 0): THREE.Mesh {
  const m = new THREE.Mesh(geo, mat);
  m.position.set(x, y, z);
  m.castShadow = true;
  return m;
}
function ground(w: number, d: number, color: number, y = 0): THREE.Mesh {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, d), M(color));
  m.rotation.x = -Math.PI / 2;
  m.position.y = y;
  m.receiveShadow = true;
  return m;
}
function rig(g: THREE.Group, sky: number, sunColor: number, sunI: number, sunPos: [number, number, number], hemiI = 0.5) {
  g.add(new THREE.HemisphereLight(sky, 0x1a1410, hemiI));
  const sun = new THREE.DirectionalLight(sunColor, sunI);
  sun.position.set(...sunPos);
  sun.castShadow = true;
  sun.shadow.mapSize.set(1024, 1024);
  sun.shadow.camera.left = -45; sun.shadow.camera.right = 45;
  sun.shadow.camera.top = 45; sun.shadow.camera.bottom = -45;
  sun.shadow.camera.far = 160;
  g.add(sun);
}
function tree(r: Rand, x: number, z: number, s: number, leaf = 0x1f4d2e, trunkC = 0x4a3421): THREE.Group {
  const g = new THREE.Group();
  const trunk = solid(new THREE.CylinderGeometry(0.22 * s, 0.34 * s, 2.2 * s, 7), M(trunkC), 0, 1.1 * s, 0);
  g.add(trunk);
  const lm = M(leaf, { roughness: 0.95 });
  const c1 = solid(new THREE.ConeGeometry(1.7 * s, 3.2 * s, 8), lm, 0, 3.4 * s, 0);
  const c2 = solid(new THREE.ConeGeometry(1.2 * s, 2.4 * s, 8), lm, 0, 5 * s, 0);
  g.add(c1, c2);
  g.position.set(x, 0, z);
  g.rotation.y = r() * Math.PI * 2;
  return g;
}
function scatterTrees(g: THREE.Group, r: Rand, n: number, minR: number, maxR: number, sMin: number, sMax: number, leaf?: number) {
  for (let i = 0; i < n; i++) {
    const a = r() * Math.PI * 2;
    const d = minR + r() * (maxR - minR);
    g.add(tree(r, Math.cos(a) * d, Math.sin(a) * d, sMin + r() * (sMax - sMin), leaf));
  }
}
function rocks(g: THREE.Group, r: Rand, n: number, area: number, c = 0x5a5a5a) {
  for (let i = 0; i < n; i++) {
    const s = 0.3 + r() * 1.1;
    const m = solid(new THREE.DodecahedronGeometry(s, 0), M(c), (r() - 0.5) * area, s * 0.4, (r() - 0.5) * area);
    m.rotation.set(r() * 3, r() * 3, r() * 3);
    g.add(m);
  }
}
function pillar(h: number, rad: number, c: number, trim = 0xc9a227): THREE.Group {
  const g = new THREE.Group();
  g.add(solid(new THREE.BoxGeometry(rad * 3, 0.5, rad * 3), M(trim), 0, 0.25, 0));
  g.add(solid(new THREE.CylinderGeometry(rad, rad * 1.15, h, 10), M(c), 0, h / 2 + 0.5, 0));
  g.add(solid(new THREE.BoxGeometry(rad * 3.2, 0.6, rad * 3.2), M(trim), 0, h + 0.8, 0));
  return g;
}
/** Campfire / fire pit. Returns flames to flicker + registers embers. */
function firePit(g: THREE.Group, anims: Anim[], x: number, z: number, s: number, lightI = 60): THREE.PointLight {
  const base = new THREE.Group();
  base.position.set(x, 0, z);
  for (let i = 0; i < 8; i++) {
    const a = (i / 8) * Math.PI * 2;
    base.add(solid(new THREE.DodecahedronGeometry(0.32 * s, 0), M(0x6a6a6a), Math.cos(a) * 1.3 * s, 0.2, Math.sin(a) * 1.3 * s));
  }
  for (let i = 0; i < 4; i++) {
    const a = (i / 4) * Math.PI * 2 + 0.4;
    const log = solid(new THREE.CylinderGeometry(0.16 * s, 0.16 * s, 2.2 * s, 6), M(0x3a2415), Math.cos(a) * 0.5 * s, 0.35 * s, Math.sin(a) * 0.5 * s);
    log.rotation.z = Math.PI / 2;
    log.rotation.y = -a;
    base.add(log);
  }
  const flames: THREE.Mesh[] = [];
  const fm = (c: number, e: number) => E(c, e, 2.4);
  const f1 = solid(new THREE.ConeGeometry(0.75 * s, 2.4 * s, 8), fm(0xe07b2a, 0xe25822), 0, 1.4 * s, 0);
  const f2 = solid(new THREE.ConeGeometry(0.45 * s, 1.6 * s, 8), fm(0xf5d76e, 0xf5a623), 0, 1.3 * s, 0);
  flames.push(f1, f2);
  base.add(f1, f2);
  const light = new THREE.PointLight(0xff8c3a, lightI, 30 * s, 1.8);
  light.position.set(x, 2.4 * s, z);
  g.add(light);
  g.add(base);
  const seed = x * 13.7 + z * 7.1;
  anims.push((t) => {
    f1.scale.set(1 + 0.16 * Math.sin(t * 11 + seed), 1 + 0.22 * Math.sin(t * 13 + seed * 2), 1 + 0.16 * Math.cos(t * 9 + seed));
    f2.scale.set(1 + 0.2 * Math.cos(t * 15 + seed), 1 + 0.28 * Math.sin(t * 17 + seed), 1);
    light.intensity = lightI * (0.86 + 0.14 * Math.sin(t * 12 + seed) * Math.sin(t * 5.3 + seed));
  });
  // embers
  const n = 40;
  const pos = new Float32Array(n * 3);
  const spd = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    pos[i * 3] = x + (Math.random() - 0.5) * 1.4 * s;
    pos[i * 3 + 1] = Math.random() * 4 * s;
    pos[i * 3 + 2] = z + (Math.random() - 0.5) * 1.4 * s;
    spd[i] = 0.8 + Math.random() * 1.6;
  }
  const pg = new THREE.BufferGeometry();
  pg.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const pts = new THREE.Points(pg, new THREE.PointsMaterial({ color: 0xffb347, size: 0.14 * s, transparent: true, opacity: 0.9 }));
  g.add(pts);
  anims.push((_, dt) => {
    const p = pg.attributes.position as THREE.BufferAttribute;
    for (let i = 0; i < n; i++) {
      let y = p.getY(i) + spd[i] * dt * s;
      if (y > 5.5 * s) y = 0.3;
      p.setY(i, y);
      p.setX(i, p.getX(i) + Math.sin(y * 3 + i) * dt * 0.3);
    }
    p.needsUpdate = true;
  });
  return light;
}
function stars(g: THREE.Group, r: Rand, n: number, spread: number, y = 90) {
  const pos = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) {
    pos[i * 3] = (r() - 0.5) * spread;
    pos[i * 3 + 1] = y * (0.35 + r() * 0.65);
    pos[i * 3 + 2] = (r() - 0.5) * spread;
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  g.add(new THREE.Points(geo, new THREE.PointsMaterial({ color: 0xf5f0e1, size: 0.7, sizeAttenuation: false })));
}
function moon(g: THREE.Group, x: number, y: number, z: number, s = 4) {
  const m = new THREE.Mesh(new THREE.SphereGeometry(s, 16, 16), E(0xf5f0e1, 0xf5f0e1, 1.2));
  m.position.set(x, y, z);
  g.add(m);
}
function water(g: THREE.Group, anims: Anim[], w: number, d: number, x: number, y: number, z: number, color = 0x1e4e79): THREE.Mesh {
  const geo = new THREE.PlaneGeometry(w, d, 42, 26);
  const base = (geo.attributes.position as THREE.BufferAttribute).array.slice();
  const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color, roughness: 0.3, metalness: 0.35, transparent: true, opacity: 0.94 }));
  m.rotation.x = -Math.PI / 2;
  m.position.set(x, y, z);
  m.receiveShadow = true;
  g.add(m);
  const seed = x + z;
  anims.push((t) => {
    const p = geo.attributes.position as THREE.BufferAttribute;
    for (let i = 0; i < p.count; i++) {
      const bx = base[i * 3];
      const by = base[i * 3 + 1];
      p.setZ(i, 0.35 * Math.sin(bx * 0.35 + t * 1.6 + seed) * Math.cos(by * 0.4 + t * 1.1));
    }
    p.needsUpdate = true;
    geo.computeVertexNormals();
  });
  return m;
}
function figure(c: number, x: number, z: number, s = 1, ry = 0): THREE.Group {
  const g = new THREE.Group();
  g.add(solid(new THREE.CylinderGeometry(0.32 * s, 0.5 * s, 1.5 * s, 8), M(c), 0, 0.75 * s, 0));
  g.add(solid(new THREE.SphereGeometry(0.24 * s, 10, 8), M(0x8a6b4a), 0, 1.7 * s, 0));
  g.position.set(x, 0, z);
  g.rotation.y = ry;
  return g;
}
function banner(g: THREE.Group, anims: Anim[], x: number, y: number, z: number, c: number, w = 2.2, h = 5) {
  const pole = solid(new THREE.CylinderGeometry(0.09, 0.09, h + 2.4, 6), M(0x3a2a18), x, (h + 2.4) / 2, z);
  g.add(pole);
  const geo = new THREE.PlaneGeometry(w, h, 6, 1);
  const cloth = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: c, side: THREE.DoubleSide, roughness: 0.9 }));
  cloth.position.set(x + w / 2 + 0.1, y, z);
  cloth.castShadow = true;
  g.add(cloth);
  const base = (geo.attributes.position as THREE.BufferAttribute).array.slice();
  anims.push((t) => {
    const p = geo.attributes.position as THREE.BufferAttribute;
    for (let i = 0; i < p.count; i++) {
      const bx = base[i * 3];
      p.setZ(i, 0.3 * Math.sin(bx * 2.2 + t * 3 + x) * (bx / w + 0.5));
    }
    p.needsUpdate = true;
    geo.computeVertexNormals();
  });
}
function lampBowl(g: THREE.Group, x: number, z: number, h = 1.1): THREE.PointLight {
  const g2 = new THREE.Group();
  g2.add(solid(new THREE.CylinderGeometry(0.12, 0.2, h, 8), M(0x2a2018), 0, h / 2, 0));
  g2.add(solid(new THREE.CylinderGeometry(0.42, 0.3, 0.3, 10), M(0x6b4a22), 0, h + 0.1, 0));
  const flame = solid(new THREE.SphereGeometry(0.16, 8, 8), E(0xffc861, 0xff9a2a, 2.6), 0, h + 0.42, 0);
  g2.add(flame);
  g2.position.set(x, 0, z);
  g.add(g2);
  const l = new THREE.PointLight(0xffb35a, 14, 16, 1.9);
  l.position.set(x, h + 1, z);
  g.add(l);
  return l;
}

interface Cfg { bg: number; fog: [number, number]; spawn: EnvResult['spawn'] }
function ctx(sceneId: string): { r: Rand; g: THREE.Group; anims: Anim[] } {
  return { r: prng(seedFor(SID, CH, sceneId)), g: new THREE.Group(), anims: [] };
}
function done(c: Cfg, g: THREE.Group, anims: Anim[], spawn: EnvResult['spawn'], extra?: (t: number, dt: number) => void): { env: EnvResult; cfg: Cfg } {
  return {
    env: { group: g, spawn, update: (t, dt) => { for (const a of anims) a(t, dt); extra?.(t, dt); } },
    cfg: { ...c, spawn },
  };
}

// ---------- the 12 worlds ----------
function b01(): { env: EnvResult; cfg: Cfg } {
  const { r, g, anims } = ctx('adi-01-naimisha');
  rig(g, 0x0a1410, 0x8fa8c8, 0.35, [30, 40, 20], 0.35);
  g.add(ground(150, 150, 0x0e2016));
  scatterTrees(g, r, 70, 11, 68, 0.9, 1.9);
  rocks(g, r, 14, 90);
  firePit(g, anims, 0, 0, 1.1);
  for (let i = 0; i < 8; i++) { // log seats for the listening sages
    const a = (i / 8) * Math.PI * 2 + 0.2;
    const seat = solid(new THREE.CylinderGeometry(0.35, 0.35, 2.2, 8), M(0x4a3421), Math.cos(a) * 4.2, 0.35, Math.sin(a) * 4.2);
    seat.rotation.z = Math.PI / 2; seat.rotation.y = -a;
    g.add(seat);
    g.add(figure([0xd8cfae, 0xb08d4a, 0x8a6b4a][i % 3], Math.cos(a) * 4.2, Math.sin(a) * 4.2, 1, -a + Math.PI / 2));
  }
  stars(g, r, 420, 320);
  moon(g, -70, 80, -90, 5);
  return done({ bg: 0x070d0a, fog: [22, 130], spawn: { pos: [0, 0, 0], target: [0, 0, 0] } }, g, anims,
    { pos: [11, 3.4, 13], target: [0, 1.6, 0] });
}

function b02(): { env: EnvResult; cfg: Cfg } {
  const { r, g, anims } = ctx('adi-02-snake-sacrifice');
  rig(g, 0x1a0a08, 0xff6a3a, 0.5, [-20, 30, 10], 0.25);
  g.add(ground(120, 120, 0x17100c));
  const floor = solid(new THREE.BoxGeometry(46, 0.6, 46), M(0x2a2018), 0, 0.3, 0);
  floor.receiveShadow = true;
  g.add(floor);
  for (let i = 0; i < 12; i++) {
    const a = (i / 12) * Math.PI * 2;
    const p = pillar(9, 0.7, 0x3a2a20);
    p.position.set(Math.cos(a) * 19, 0.6, Math.sin(a) * 19);
    g.add(p);
  }
  const back = solid(new THREE.BoxGeometry(46, 12, 1.5), M(0x241812), 0, 6, -22.5);
  g.add(back);
  firePit(g, anims, 0, 0, 1.9, 90);
  // serpents rising from the flames
  for (let i = 0; i < 7; i++) {
    const a = (i / 7) * Math.PI * 2 + r() * 0.5;
    const pts = [
      new THREE.Vector3(Math.cos(a) * 2, 0.5, Math.sin(a) * 2),
      new THREE.Vector3(Math.cos(a + 0.7) * 2.6, 3.4, Math.sin(a + 0.7) * 2.6),
      new THREE.Vector3(Math.cos(a + 1.4) * 1.8, 6.4, Math.sin(a + 1.4) * 1.8),
      new THREE.Vector3(Math.cos(a + 2) * 2.4, 9.2, Math.sin(a + 2) * 2.4),
    ];
    const tube = solid(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 32, 0.34, 8),
      new THREE.MeshStandardMaterial({ color: 0x5c1f14, emissive: 0xd84818, emissiveIntensity: 0.55, roughness: 0.5 }), 0, 0, 0);
    g.add(tube);
    const head = solid(new THREE.SphereGeometry(0.55, 10, 8), E(0xff7a2a, 0xff5a1a, 1.8),
      pts[3].x, pts[3].y + 0.3, pts[3].z);
    g.add(head);
  }
  for (let i = 0; i < 6; i++) { // priests ringing the rite
    const a = (i / 6) * Math.PI * 2 + 0.5;
    g.add(figure(0x4a1f14, Math.cos(a) * 8.5, Math.sin(a) * 8.5, 1.15, -a + Math.PI / 2));
  }
  lampBowl(g, 12, 12); lampBowl(g, -12, 12); lampBowl(g, 12, -12); lampBowl(g, -12, -12);
  return done({ bg: 0x120606, fog: [18, 105], spawn: { pos: [0, 0, 0], target: [0, 0, 0] } }, g, anims,
    { pos: [13, 4.5, 15], target: [0, 2.5, 0] });
}

function b03(): { env: EnvResult; cfg: Cfg } {
  const { r, g, anims } = ctx('adi-03-ganga');
  rig(g, 0x8fa8c8, 0xffe0b0, 0.9, [40, 30, -30], 0.6);
  water(g, anims, 170, 90, 0, 0, -10);
  // banks
  const bL = solid(new THREE.BoxGeometry(170, 2, 26), M(0x2a4a2e), 0, 0.4, 26);
  const bR = solid(new THREE.BoxGeometry(170, 2, 26), M(0x2a4a2e), 0, 0.4, -46);
  bL.receiveShadow = bR.receiveShadow = true;
  g.add(bL, bR);
  // ghat steps into the river
  for (let i = 0; i < 6; i++) {
    g.add(solid(new THREE.BoxGeometry(14, 0.5, 1.6), M(0x9a8a6a), -20, 1.2 - i * 0.35, 14 - i * 1.7));
  }
  // shrine
  for (const dx of [-4.4, 4.4]) {
    const p = pillar(6, 0.5, 0xd8cfae);
    p.position.set(24 + dx, 1.4, 24);
    g.add(p);
  }
  const roof = solid(new THREE.ConeGeometry(7, 3, 4), M(0x8B2E1F), 24, 9.6, 24);
  roof.rotation.y = Math.PI / 4;
  g.add(roof);
  // reeds + rocks + palace silhouette
  for (let i = 0; i < 40; i++) {
    const x = (r() - 0.5) * 150;
    const z = r() > 0.5 ? 13.5 + r() * 2 : -33 - r() * 2;
    g.add(solid(new THREE.CylinderGeometry(0.05, 0.08, 2 + r() * 1.5, 5), M(0x3a5a34), x, 1.8, z));
  }
  rocks(g, r, 10, 120, 0x6a6a62);
  const pal = M(0x2a3444, { roughness: 1 });
  g.add(solid(new THREE.BoxGeometry(30, 14, 8), pal, -48, 7, -52));
  g.add(solid(new THREE.BoxGeometry(18, 22, 8), pal, -30, 11, -52));
  g.add(solid(new THREE.ConeGeometry(5, 6, 4), M(0xc9a227), -30, 25, -52));
  // basket with the kept child, bobbing
  const basket = new THREE.Group();
  basket.add(solid(new THREE.CylinderGeometry(0.9, 0.7, 0.7, 10), M(0x6b4a22), 0, 0.2, 0));
  basket.add(solid(new THREE.SphereGeometry(0.32, 10, 8), M(0xd8a67a), 0, 0.65, 0));
  basket.position.set(6, 0.25, -8);
  g.add(basket);
  anims.push((t) => {
    basket.position.y = 0.25 + 0.16 * Math.sin(t * 1.4);
    basket.rotation.z = 0.08 * Math.sin(t * 0.9);
    basket.position.x = 6 + 1.2 * Math.sin(t * 0.12);
  });
  stars(g, r, 120, 300);
  return done({ bg: 0x27394f, fog: [30, 170], spawn: { pos: [0, 0, 0], target: [0, 0, 0] } }, g, anims,
    { pos: [16, 4.5, 22], target: [-4, 1, -10] });
}

function b04(): { env: EnvResult; cfg: Cfg } {
  const { r, g, anims } = ctx('adi-04-bhishma-vow');
  rig(g, 0x2a2014, 0xffd88a, 1.0, [10, 24, 14], 0.5);
  const floor = solid(new THREE.BoxGeometry(52, 0.6, 52), M(0xd8cfae, { roughness: 0.4, metalness: 0.15 }), 0, 0.3, 0);
  floor.receiveShadow = true;
  g.add(floor);
  for (const [x, z] of [[-18, -18], [18, -18], [-18, 18], [18, 18], [-18, 0], [18, 0], [0, -18]] as [number, number][]) {
    const p = pillar(11, 0.8, 0xe8dcc0);
    p.position.set(x, 0.6, z);
    g.add(p);
  }
  g.add(solid(new THREE.BoxGeometry(52, 14, 1.5), M(0x3a2c1c), 0, 7, -25));
  g.add(solid(new THREE.BoxGeometry(52, 3, 54), M(0x241a10), 0, 15.5, 0)); // roof slab
  // empty throne on a dais + oath sword
  for (let i = 0; i < 3; i++) g.add(solid(new THREE.BoxGeometry(10 - i * 2, 0.5, 8 - i * 1.4), M(0xb08d4a), 0, 0.85 + i * 0.5, -14));
  g.add(solid(new THREE.BoxGeometry(3.4, 3.2, 1.2), M(0x8a6a2a, { metalness: 0.5, roughness: 0.4 }), 0, 4, -14.5));
  g.add(solid(new THREE.BoxGeometry(4.2, 1.1, 1.6), M(0x8a6a2a, { metalness: 0.5, roughness: 0.4 }), 0, 5.6, -14.5));
  const blade = solid(new THREE.BoxGeometry(0.16, 3.4, 0.4), M(0xd8d8e0, { metalness: 0.9, roughness: 0.2 }), 2.8, 3.4, -12.5);
  blade.rotation.z = 0.5;
  g.add(blade);
  g.add(solid(new THREE.BoxGeometry(0.5, 0.9, 0.5), M(0x3a2a18), 2.1, 1.6, -12.5));
  const beam = solid(new THREE.BoxGeometry(0.1, 9, 3.2), E(0xffe8b0, 0xffd88a, 1.4), 0, 6, -14); // oath light
  g.add(beam);
  banner(g, anims, -14, 9, -24, 0x8B2E1F);
  banner(g, anims, 14, 9, -24, 0x8B2E1F);
  lampBowl(g, -8, 2); lampBowl(g, 8, 2); lampBowl(g, -8, -8); lampBowl(g, 8, -8);
  void r;
  return done({ bg: 0x171006, fog: [14, 85], spawn: { pos: [0, 0, 0], target: [0, 0, 0] } }, g, anims,
    { pos: [11, 3.2, 10], target: [0, 3, -13] });
}

function b05(): { env: EnvResult; cfg: Cfg } {
  const { r, g, anims } = ctx('adi-05-vyasa-line');
  rig(g, 0x14141c, 0x8a7aa8, 0.4, [0, 20, 10], 0.3);
  const floor = solid(new THREE.BoxGeometry(34, 0.6, 34), M(0x23232f), 0, 0.3, 0);
  floor.receiveShadow = true;
  g.add(floor);
  g.add(solid(new THREE.BoxGeometry(34, 10, 1.2), M(0x1a1a24), 0, 5, -16.5));
  g.add(solid(new THREE.BoxGeometry(1.2, 10, 34), M(0x1a1a24), -16.5, 5, 0));
  // three cradles: one covered (blindness), one pale, one plain
  const cradles: [number, number][] = [[-7, -4], [0, -4], [7, -4]];
  cradles.forEach(([x, z], i) => {
    const c = new THREE.Group();
    c.add(solid(new THREE.BoxGeometry(2.6, 1, 1.4), M(0x5a4028), 0, 1, 0));
    for (const dx of [-1, 1]) {
      const rocker = solid(new THREE.TorusGeometry(1.1, 0.12, 6, 12, Math.PI), M(0x5a4028), dx * 0.8, 0.5, 0);
      rocker.rotation.y = Math.PI / 2;
      rocker.rotation.z = Math.PI;
      c.add(rocker);
    }
    if (i === 0) c.add(solid(new THREE.BoxGeometry(2.7, 0.9, 1.5), M(0x0c0c12), 0, 1.7, 0)); // covered
    else c.add(solid(new THREE.SphereGeometry(0.3, 10, 8), M(i === 1 ? 0xd8c8b8 : 0xc8a67a), 0, 1.5, 0));
    c.position.set(x, 0.6, z);
    g.add(c);
  });
  // Vyasa silhouette in the doorway
  const sage = figure(0x0a0a0e, 0, -12, 1.7, 0);
  g.add(sage);
  g.add(solid(new THREE.BoxGeometry(4, 7, 0.6), E(0x4a3a5c, 0x2a1f3d, 0.8), 0, 4, -16.4)); // lit doorway
  lampBowl(g, 5, 4);
  const drape = new THREE.Mesh(new THREE.PlaneGeometry(8, 9), M(0x3d2a4a, { side: THREE.DoubleSide }));
  drape.position.set(-10, 5, -15.8);
  g.add(drape);
  void r;
  return done({ bg: 0x0d0d14, fog: [10, 60], spawn: { pos: [0, 0, 0], target: [0, 0, 0] } }, g, anims,
    { pos: [8, 2.6, 9], target: [0, 1.4, -5] });
}

function b06(): { env: EnvResult; cfg: Cfg } {
  const { r, g, anims } = ctx('adi-06-births');
  rig(g, 0x9db8d8, 0xfff2d8, 1.3, [40, 50, 20], 0.75);
  g.add(ground(150, 150, 0x3a6a3a));
  // flower rows
  for (let row = 0; row < 5; row++) {
    for (let i = 0; i < 12; i++) {
      const x = -22 + i * 4 + (r() - 0.5);
      const z = 2 + row * 3 + (r() - 0.5);
      g.add(solid(new THREE.CylinderGeometry(0.05, 0.05, 0.9, 5), M(0x2a5a2a), x, 0.45, z));
      const f = new THREE.Mesh(new THREE.SphereGeometry(0.22, 8, 6), E([0xd84a6a, 0xf5d76e, 0xf5f0e1][(i + row) % 3], 0xffffff, 0.5));
      f.position.set(x, 1, z);
      g.add(f);
    }
  }
  // palace wall behind
  g.add(solid(new THREE.BoxGeometry(90, 10, 3), M(0xd8cfae), 0, 5, -24));
  for (let i = -4; i <= 4; i++) {
    const t = solid(new THREE.CylinderGeometry(1.6, 1.6, 14, 10), M(0xc8bb9a), i * 10, 7, -24);
    g.add(t);
    g.add(solid(new THREE.ConeGeometry(2.2, 3, 10), M(0x8B2E1F), i * 10, 15.5, -24));
  }
  // river strip + drifting basket
  water(g, anims, 150, 16, 0, 0.05, 22);
  const basket = new THREE.Group();
  basket.add(solid(new THREE.CylinderGeometry(0.9, 0.7, 0.7, 10), M(0x6b4a22), 0, 0.2, 0));
  basket.add(solid(new THREE.SphereGeometry(0.32, 10, 8), M(0xd8a67a), 0, 0.65, 0));
  g.add(basket);
  anims.push((t) => {
    basket.position.set(-60 + ((t * 1.5) % 130), 0.3 + 0.12 * Math.sin(t * 1.6), 22);
  });
  for (let i = 0; i < 8; i++) lampBowl(g, -28 + i * 8, -8);
  scatterTrees(g, r, 24, 34, 70, 0.8, 1.5, 0x2a5a34);
  return done({ bg: 0x87a6c4, fog: [40, 190], spawn: { pos: [0, 0, 0], target: [0, 0, 0] } }, g, anims,
    { pos: [14, 4, 16], target: [-6, 1.5, -10] });
}

function b07(): { env: EnvResult; cfg: Cfg } {
  const { r, g, anims } = ctx('adi-07-drona');
  rig(g, 0x9db8cc, 0xffe8c0, 1.25, [30, 44, 18], 0.7);
  g.add(ground(160, 160, 0x8a6b42));
  // range markers
  for (let i = 0; i < 8; i++) {
    g.add(solid(new THREE.BoxGeometry(0.5, 0.5, 30), M(0xf5f0e1, { roughness: 1 }), -21 + i * 6, 0.25, -6));
  }
  // targets at staggered ranges
  const tz = [-14, -20, -26, -32, -38];
  tz.forEach((z, i) => {
    const x = -16 + i * 8;
    const stand = solid(new THREE.CylinderGeometry(0.18, 0.24, 3.4, 8), M(0x4a3421), x, 1.7, z);
    g.add(stand);
    const rings: [number, number][] = [[1.5, 0xd84a3a], [1.05, 0xf5f0e1], [0.6, 0xd84a3a]];
    rings.forEach(([rad, c]) => {
      const ring = solid(new THREE.TorusGeometry(rad, 0.14, 8, 24), M(c), x, 4.4, z + 0.1);
      g.add(ring);
    });
    g.add(solid(new THREE.SphereGeometry(0.22, 8, 8), M(0xd84a3a), x, 4.4, z + 0.1));
  });
  // arrow rack + stuck arrows
  const rack = solid(new THREE.BoxGeometry(3, 1.2, 1), M(0x4a3421), 8, 0.6, 6);
  g.add(rack);
  for (let i = 0; i < 9; i++) {
    const a = solid(new THREE.CylinderGeometry(0.04, 0.04, 2.6, 5), M(0xd8c8a8), 7 + (i % 3) * 0.9, 2.2, 5.7 + Math.floor(i / 3) * 0.35);
    a.rotation.x = 0.25;
    g.add(a);
  }
  for (let i = 0; i < 5; i++) { // arrows in the ground near the line
    const a = solid(new THREE.CylinderGeometry(0.04, 0.04, 1.8, 5), M(0xd8c8a8), -8 + r() * 16, 0.8, 2 + r() * 5);
    a.rotation.x = 0.5 + r() * 0.3;
    g.add(a);
  }
  // Ekalavya shrine: stone + offering bowl
  g.add(solid(new THREE.DodecahedronGeometry(1.6, 0), M(0x6a6a62), -14, 1, 10));
  g.add(solid(new THREE.CylinderGeometry(0.7, 0.45, 0.5, 10), M(0x8a6a2a, { metalness: 0.6, roughness: 0.35 }), -14, 2.4, 10));
  g.add(figure(0x3a5a6a, 6, -2, 1.1, 2.6)); // Drona watching
  g.add(figure(0x8a2a2a, 2, 0, 1, 2.6));   // Arjuna at the line
  // dust motes
  const n = 90;
  const pos = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) {
    pos[i * 3] = (r() - 0.5) * 60; pos[i * 3 + 1] = r() * 7; pos[i * 3 + 2] = (r() - 0.5) * 60;
  }
  const pg = new THREE.BufferGeometry();
  pg.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const dust = new THREE.Points(pg, new THREE.PointsMaterial({ color: 0xe8d8b0, size: 0.12, transparent: true, opacity: 0.6 }));
  g.add(dust);
  anims.push((t) => { dust.rotation.y = t * 0.014; });
  scatterTrees(g, r, 18, 45, 75, 0.9, 1.6);
  return done({ bg: 0x9db8cc, fog: [45, 200], spawn: { pos: [0, 0, 0], target: [0, 0, 0] } }, g, anims,
    { pos: [0, 3.2, 18], target: [0, 2.5, -16] });
}

function b08(): { env: EnvResult; cfg: Cfg } {
  const { r, g, anims } = ctx('adi-08-lakshagriha');
  rig(g, 0x14100e, 0xff8c3a, 0.55, [-24, 26, 12], 0.3);
  g.add(ground(140, 140, 0x1c1410));
  // ornate lacquer palace
  const wallM = M(0x5c2a14, { roughness: 0.55 });
  const trimM = M(0xc9a227, { metalness: 0.5, roughness: 0.4 });
  g.add(solid(new THREE.BoxGeometry(24, 10, 16), wallM, 0, 5, -6));
  g.add(solid(new THREE.BoxGeometry(26, 1, 18), trimM, 0, 10.2, -6));
  const roof = solid(new THREE.ConeGeometry(17, 7, 4), M(0x2a140a), 0, 14, -6);
  roof.rotation.y = Math.PI / 4;
  g.add(roof);
  for (let i = 0; i < 5; i++) { // burning windows
    const w = solid(new THREE.BoxGeometry(1.8, 2.6, 0.3), E(0xff9a2a, 0xe25822, 2.2), -9.6 + i * 4.8, 5.4, 2.1);
    g.add(w);
  }
  g.add(solid(new THREE.BoxGeometry(3, 5, 0.5), M(0x0a0605), 0, 2.5, 2.1)); // dark door
  firePit(g, anims, -9, 8, 1.2, 70);
  firePit(g, anims, 9, 8, 1.0, 60);
  firePit(g, anims, 0, 12, 0.8, 50);
  // escape tunnel: dark ramp + mound behind the house
  const ramp = solid(new THREE.BoxGeometry(4, 0.5, 12), M(0x0a0806), 0, 0.4, -20);
  ramp.rotation.x = 0.12;
  g.add(ramp);
  g.add(solid(new THREE.SphereGeometry(4, 10, 8), M(0x2a2018), 0, 0.5, -28));
  // smoke columns
  const smokeM = new THREE.MeshBasicMaterial({ color: 0x4a4a4a, transparent: true, opacity: 0.35 });
  const smokes: THREE.Mesh[] = [];
  for (let i = 0; i < 5; i++) {
    const s = new THREE.Mesh(new THREE.PlaneGeometry(6, 16), smokeM);
    s.position.set(-8 + i * 4 + r() * 2, 18, -6 + r() * 3);
    g.add(s);
    smokes.push(s);
  }
  anims.push((t) => {
    smokes.forEach((s, i) => {
      s.position.y = 16 + ((t * (0.8 + i * 0.14)) % 10);
      s.rotation.y = t * 0.2 + i;
    });
  });
  stars(g, r, 200, 300);
  return done({ bg: 0x0d0505, fog: [20, 115], spawn: { pos: [0, 0, 0], target: [0, 0, 0] } }, g, anims,
    { pos: [16, 4.5, 18], target: [0, 4, -6] });
}

function b09(): { env: EnvResult; cfg: Cfg } {
  const { r, g, anims } = ctx('adi-09-hidimba');
  rig(g, 0x0a1410, 0x4a6a5a, 0.3, [10, 24, 8], 0.3);
  g.add(ground(130, 130, 0x0a140e));
  scatterTrees(g, r, 95, 8, 60, 1.1, 2.3, 0x0d1f16);
  rocks(g, r, 12, 70, 0x3a3a3a);
  const fallen = solid(new THREE.CylinderGeometry(0.5, 0.6, 9, 8), M(0x2a1e14), 4, 0.5, 6);
  fallen.rotation.z = Math.PI / 2;
  fallen.rotation.y = 0.5;
  g.add(fallen);
  // Bhima's mace leaning on a rock
  g.add(solid(new THREE.DodecahedronGeometry(1.4, 0), M(0x5a5a5a), -5, 0.8, 2));
  const handle = solid(new THREE.CylinderGeometry(0.16, 0.2, 5, 8), M(0x4a3421), -4.2, 2.6, 2);
  handle.rotation.z = 0.5;
  g.add(handle);
  g.add(solid(new THREE.SphereGeometry(0.7, 10, 8), M(0x6a6a6a, { metalness: 0.6, roughness: 0.4 }), -3, 4.6, 2));
  // watching eyes in the dark
  const eyePairs: THREE.Mesh[] = [];
  const spots: [number, number, number][] = [[-12, 4.5, -14], [10, 3.4, -18], [-4, 6, -26], [16, 5, -8], [-18, 3, -4]];
  for (const [x, y, z] of spots) {
    for (const dx of [-0.5, 0.5]) {
      const e = new THREE.Mesh(new THREE.SphereGeometry(0.32, 10, 8), E(0xffd84a, 0xcc9214, 2.2));
      e.position.set(x + dx, y, z);
      g.add(e);
      eyePairs.push(e);
    }
  }
  anims.push((t) => {
    const blink = (Math.sin(t * 0.7) > 0.985) ? 0.12 : 1; // occasional blink
    eyePairs.forEach((e) => { e.scale.y = blink; });
  });
  const glow = new THREE.PointLight(0x3a7a4a, 10, 26, 1.9);
  glow.position.set(0, 3, -10);
  g.add(glow);
  // fireflies
  const n = 70;
  const pos = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) {
    pos[i * 3] = (r() - 0.5) * 70; pos[i * 3 + 1] = 0.5 + r() * 5; pos[i * 3 + 2] = (r() - 0.5) * 70;
  }
  const fg = new THREE.BufferGeometry();
  fg.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const flies = new THREE.Points(fg, new THREE.PointsMaterial({ color: 0x9adf6a, size: 0.16, transparent: true, opacity: 0.85 }));
  g.add(flies);
  anims.push((t, dt) => {
    const p = fg.attributes.position as THREE.BufferAttribute;
    for (let i = 0; i < n; i++) {
      p.setX(i, p.getX(i) + Math.sin(t * 0.8 + i * 2.1) * dt * 0.7);
      p.setY(i, p.getY(i) + Math.cos(t * 0.6 + i) * dt * 0.4);
    }
    p.needsUpdate = true;
  });
  return done({ bg: 0x040806, fog: [8, 58], spawn: { pos: [0, 0, 0], target: [0, 0, 0] } }, g, anims,
    { pos: [0, 2.6, 14], target: [0, 3, -12] });
}

function b10(): { env: EnvResult; cfg: Cfg } {
  const { r, g, anims } = ctx('adi-10-swayamvara');
  rig(g, 0xd8b878, 0xfff2d8, 1.2, [30, 44, 20], 0.65);
  const floor = solid(new THREE.BoxGeometry(64, 0.6, 44), M(0xc8b088, { roughness: 0.5 }), 0, 0.3, 0);
  floor.receiveShadow = true;
  g.add(floor);
  for (let i = 0; i < 8; i++) { // pavilion columns
    for (const z of [-19, 19]) {
      const p = pillar(12, 0.7, 0xe8dcc0);
      p.position.set(-28 + i * 8, 0.6, z);
      g.add(p);
    }
  }
  g.add(solid(new THREE.BoxGeometry(66, 1.2, 46), M(0x8B2E1F), 0, 13.4, 0)); // canopy
  // pool with the reflected target
  const pool = solid(new THREE.CylinderGeometry(5, 5, 0.5, 24), new THREE.MeshStandardMaterial({ color: 0x1e4e79, roughness: 0.15, metalness: 0.5 }), 0, 0.7, -4);
  pool.receiveShadow = true;
  g.add(pool);
  const rings: [number, number][] = [[3.4, 0xf5f0e1], [2.2, 0xc9a227], [1.1, 0xf5f0e1]];
  rings.forEach(([rad, c]) => {
    const ring = solid(new THREE.TorusGeometry(rad, 0.16, 8, 32), M(c, { metalness: 0.4, roughness: 0.4 }), 0, 7.5, -4);
    ring.rotation.x = Math.PI / 2;
    g.add(ring);
  });
  const fish = solid(new THREE.ConeGeometry(0.5, 1.6, 8), M(0xc9a227, { metalness: 0.6, roughness: 0.3 }), 0, 7.5, -4);
  fish.rotation.x = Math.PI;
  g.add(fish);
  anims.push((t) => { fish.rotation.y = t * 0.8; });
  // the great bow on its stand
  const bow = solid(new THREE.TorusGeometry(2.6, 0.22, 8, 24, Math.PI * 1.2), M(0x4a2c14), -12, 3, -4);
  bow.rotation.z = Math.PI * 0.9;
  g.add(bow);
  g.add(solid(new THREE.BoxGeometry(1.6, 1, 1.6), M(0x3a2a18), -12, 0.8, -4));
  // garland of five knots
  for (let i = 0; i < 5; i++) {
    const k = solid(new THREE.TorusGeometry(0.5, 0.16, 8, 16), E([0xd84a6a, 0xf5d76e, 0xf5f0e1, 0xd84a6a, 0xf5d76e][i], 0xffffff, 0.4), 8 + i * 1.3, 2.2, -4);
    g.add(k);
  }
  // thrones + witnessing crowd
  for (let i = 0; i < 5; i++) {
    g.add(solid(new THREE.BoxGeometry(2, 2.4, 1.2), M(0x8a6a2a, { metalness: 0.4, roughness: 0.5 }), -8 + i * 4, 1.5, 12));
  }
  const crowdC = [0x8B2E1F, 0x1e4e79, 0xc9a227, 0x4a5a3a, 0x6a3a5a];
  for (let i = 0; i < 22; i++) {
    const a = (i / 22) * Math.PI * 2;
    g.add(figure(crowdC[i % crowdC.length], Math.cos(a) * (13 + r() * 4), -4 + Math.sin(a) * (9 + r() * 3), 0.95, -a + Math.PI / 2));
  }
  banner(g, anims, -24, 9, -18, 0xc9a227);
  banner(g, anims, 24, 9, -18, 0xc9a227);
  return done({ bg: 0x8a7358, fog: [30, 150], spawn: { pos: [0, 0, 0], target: [0, 0, 0] } }, g, anims,
    { pos: [14, 4.5, 16], target: [-2, 3, -5] });
}

function b11(): { env: EnvResult; cfg: Cfg } {
  const { r, g, anims } = ctx('adi-11-division');
  rig(g, 0x6a5a7a, 0xffb37a, 0.85, [-30, 22, 20], 0.55);
  // two halves of the kingdom split by water
  const west = solid(new THREE.BoxGeometry(34, 3, 60), M(0x3a4a34), -19, 0.5, 0);
  const east = solid(new THREE.BoxGeometry(34, 3, 60), M(0x4a3a2e), 19, 0.5, 0);
  west.receiveShadow = east.receiveShadow = true;
  g.add(west, east);
  water(g, anims, 8, 70, 0, 0.4, 0, 0x2a3a5a);
  // broken bridge planks
  for (let i = 0; i < 6; i++) {
    const p = solid(new THREE.BoxGeometry(3.4, 0.3, 1.4), M(0x4a3421), -2.5 + (i >= 3 ? 5 + r() : 0), 2.1 - Math.abs(i - 2.5) * 0.35, -12 + i * 4.4);
    p.rotation.z = (r() - 0.5) * 0.5;
    p.rotation.y = (r() - 0.5) * 0.4;
    g.add(p);
  }
  // half crown on a pedestal (west) + empty pedestal (east)
  g.add(solid(new THREE.BoxGeometry(3, 2, 3), M(0x8a8578), -19, 3, -10));
  const half = solid(new THREE.CylinderGeometry(1.3, 1.5, 1.1, 12, 1, false, 0, Math.PI), M(0xc9a227, { metalness: 0.7, roughness: 0.3 }), -19, 4.6, -10);
  g.add(half);
  for (let i = 0; i < 4; i++) {
    const a = (i / 4) * Math.PI;
    g.add(solid(new THREE.ConeGeometry(0.22, 0.9, 6), M(0xc9a227, { metalness: 0.7, roughness: 0.3 }), -19 + Math.cos(a) * 1.3, 5.5, -10 + Math.sin(a) * 1.3));
  }
  g.add(solid(new THREE.BoxGeometry(3, 2, 3), M(0x8a8578), 19, 3, -10));
  // rival banners, torn angles
  banner(g, anims, -30, 8, 8, 0x8B2E1F);
  banner(g, anims, 30, 8, 8, 0x1e4e79);
  g.add(figure(0xd8cfae, -8, 6, 1.1, 1.8));
  g.add(figure(0x5c1f14, 8, 6, 1.1, -1.8));
  scatterTrees(g, r, 16, 30, 60, 0.8, 1.4);
  return done({ bg: 0x4a3a52, fog: [26, 140], spawn: { pos: [0, 0, 0], target: [0, 0, 0] } }, g, anims,
    { pos: [0, 6, 26], target: [0, 2.5, -4] });
}

function b12(): { env: EnvResult; cfg: Cfg } {
  const { r, g, anims } = ctx('adi-12-indraprastha');
  rig(g, 0xd8b088, 0xffd8a0, 1.5, [-40, 26, 30], 0.7);
  g.add(ground(170, 170, 0x4a6a42));
  // white palace rising
  const plat = solid(new THREE.BoxGeometry(44, 2, 36), M(0xe8e2cc), 0, 1, -14);
  plat.receiveShadow = true;
  g.add(plat);
  const tower = (x: number, z: number, h: number, rad: number) => {
    g.add(solid(new THREE.CylinderGeometry(rad, rad * 1.15, h, 12), M(0xf5f0e1), x, 2 + h / 2, z));
    g.add(solid(new THREE.SphereGeometry(rad * 1.02, 14, 10, 0, Math.PI * 2, 0, Math.PI / 2), M(0xc9a227, { metalness: 0.65, roughness: 0.3 }), x, 2 + h, z));
    g.add(solid(new THREE.SphereGeometry(rad * 0.2, 8, 8), E(0xffe8b0, 0xffd88a, 1.5), x, 2 + h + rad * 1.15, z));
  };
  tower(0, -18, 22, 4.4);
  tower(-14, -12, 14, 3);
  tower(14, -12, 14, 3);
  g.add(solid(new THREE.BoxGeometry(30, 8, 10), M(0xf5f0e1), 0, 6, -14));
  g.add(solid(new THREE.BoxGeometry(34, 1, 12), M(0xc9a227, { metalness: 0.5, roughness: 0.4 }), 0, 10.4, -14));
  for (let i = 0; i < 7; i++) g.add(solid(new THREE.BoxGeometry(16 - i * 1.6, 0.6, 4), M(0xe8e2cc), 0, 0.6 + i * 0.6, 6 - i * 1.1)); // steps
  // gardens
  for (let i = 0; i < 24; i++) {
    const x = -30 + (i % 12) * 5.5;
    const z = 12 + Math.floor(i / 12) * 6;
    g.add(solid(new THREE.CylinderGeometry(0.05, 0.05, 0.9, 5), M(0x2a5a2a), x, 0.45, z));
    const f = new THREE.Mesh(new THREE.SphereGeometry(0.24, 8, 6), E(i % 2 ? 0xf5d76e : 0xf5f0e1, 0xffffff, 0.5));
    f.position.set(x, 1, z);
    g.add(f);
  }
  // burnt Khandava edge: charred trunks + last smoke
  for (let i = 0; i < 16; i++) {
    const x = 34 + r() * 30;
    const z = -30 + r() * 55;
    g.add(solid(new THREE.CylinderGeometry(0.3, 0.45, 4 + r() * 4, 7), M(0x14100c), x, 2.5, z));
  }
  const ember = firePit(g, anims, 44, 0, 0.9, 40);
  void ember;
  // rising sun
  const sun = new THREE.Mesh(new THREE.SphereGeometry(7, 18, 18), E(0xffd8a0, 0xffb060, 1.6));
  sun.position.set(-90, 26, -120);
  g.add(sun);
  // circling birds
  const birds = new THREE.Group();
  for (let i = 0; i < 7; i++) {
    const b = new THREE.Mesh(new THREE.ConeGeometry(0.3, 1.4, 4), M(0x2a2a2a));
    b.position.set((r() - 0.5) * 40, 24 + r() * 10, -40 + (r() - 0.5) * 40);
    b.rotation.z = Math.PI / 2;
    birds.add(b);
  }
  g.add(birds);
  anims.push((t) => { birds.rotation.y = t * 0.05; });
  return done({ bg: 0xd9a05a, fog: [38, 180], spawn: { pos: [0, 0, 0], target: [0, 0, 0] } }, g, anims,
    { pos: [20, 6, 24], target: [-2, 6, -16] });
}

export const BUILDERS: Record<string, () => { env: EnvResult; cfg: Cfg }> = {
  'adi-01-naimisha': b01,
  'adi-02-snake-sacrifice': b02,
  'adi-03-ganga': b03,
  'adi-04-bhishma-vow': b04,
  'adi-05-vyasa-line': b05,
  'adi-06-births': b06,
  'adi-07-drona': b07,
  'adi-08-lakshagriha': b08,
  'adi-09-hidimba': b09,
  'adi-10-swayamvara': b10,
  'adi-11-division': b11,
  'adi-12-indraprastha': b12,
};

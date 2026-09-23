// 3D engine: WebGL renderer, roamable camera (orbit + WASD), fog, lighting rig.
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { OutlineEffect } from 'three/examples/jsm/effects/OutlineEffect.js';

export interface EnvResult {
  group: THREE.Group;
  /** Per-frame animation hook. */
  update: (t: number, dt: number) => void;
  /** Where the camera starts. */
  spawn: { pos: [number, number, number]; target: [number, number, number] };
}

export class Engine {
  renderer: THREE.WebGLRenderer;
  effect: OutlineEffect;
  scene: THREE.Scene;
  camera: THREE.PerspectiveCamera;
  controls: OrbitControls;
  private keys = new Set<string>();
  private current: THREE.Group | null = null;
  private updater: (t: number, dt: number) => void = () => {};
  private shared = new WeakSet<object>();
  private last = performance.now();
  idleAutoRotate = true;
  private lastInteract = performance.now();

  constructor(canvas: HTMLCanvasElement) {
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFShadowMap;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.05;
    this.effect = new OutlineEffect(this.renderer, { defaultThickness: 0.0025 });

    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(58, 1, 0.1, 600);
    this.controls = new OrbitControls(this.camera, canvas);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.06;
    this.controls.maxPolarAngle = 1.53; // stay above ground
    this.controls.minDistance = 2.5;
    this.controls.maxDistance = 55;
    this.controls.autoRotateSpeed = 0.5;

    window.addEventListener('resize', () => this.resize());
    this.resize();
    window.addEventListener('keydown', (e) => this.keys.add(e.code));
    window.addEventListener('keyup', (e) => this.keys.delete(e.code));
    canvas.addEventListener('pointerdown', () => { this.lastInteract = performance.now(); });
    canvas.addEventListener('wheel', () => { this.lastInteract = performance.now(); }, { passive: true });

    const loop = (now: number) => {
      requestAnimationFrame(loop);
      const dt = Math.min(0.05, (now - this.last) / 1000);
      this.last = now;
      this.roam(dt);
      this.updater(now / 1000, dt);
      this.controls.autoRotate = this.idleAutoRotate && now - this.lastInteract > 9000;
      this.controls.update();
      this.effect.render(this.scene, this.camera);
    };
    requestAnimationFrame(loop);
  }

  resize() {
    const w = window.innerWidth;
    const h = window.innerHeight;
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(w, h);
  }

  /** WASD / arrows glide the camera and its orbit target across the ground plane. */
  private roam(dt: number) {
    const fwd = new THREE.Vector3();
    this.camera.getWorldDirection(fwd);
    fwd.y = 0;
    fwd.normalize();
    const right = new THREE.Vector3().crossVectors(fwd, new THREE.Vector3(0, 1, 0)).negate();
    const move = new THREE.Vector3();
    if (this.keys.has('KeyW') || this.keys.has('ArrowUp')) move.add(fwd);
    if (this.keys.has('KeyS') || this.keys.has('ArrowDown')) move.sub(fwd);
    if (this.keys.has('KeyA') || this.keys.has('ArrowLeft')) move.add(right);
    if (this.keys.has('KeyD') || this.keys.has('ArrowRight')) move.sub(right);
    if (move.lengthSq() === 0) return;
    move.normalize().multiplyScalar(11 * dt);
    const t = this.controls.target.clone().add(move);
    // Keep the visitor inside the world.
    const r = Math.hypot(t.x, t.z);
    if (r > 58) {
      t.x *= 58 / r;
      t.z *= 58 / r;
    }
    const shift = t.clone().sub(this.controls.target);
    this.controls.target.copy(t);
    this.camera.position.add(shift);
    this.camera.position.y = Math.max(1.2, this.camera.position.y);
    this.lastInteract = performance.now();
  }

  /** Mark a reusable template (cached characters) so disposal skips its GPU assets. */
  markShared(root: THREE.Object3D) {
    root.traverse((o) => {
      const mesh = o as THREE.Mesh;
      if (!mesh.isMesh) return;
      this.shared.add(mesh.geometry);
      const m = mesh.material as THREE.Material | THREE.Material[];
      (Array.isArray(m) ? m : [m]).forEach((x) => this.shared.add(x));
    });
  }

  setEnvironment(env: EnvResult, bg: number, fogNear: number, fogFar: number) {
    if (this.current) {
      this.scene.remove(this.current);
      this.current.traverse((o) => {
        const mesh = o as THREE.Mesh;
        if (mesh.isMesh || (o as THREE.Points).isPoints) {
          const geo = mesh.geometry as THREE.BufferGeometry;
          if (!this.shared.has(geo)) {
            geo.dispose();
          }
          const m = (mesh.material as THREE.Material | THREE.Material[]);
          (Array.isArray(m) ? m : [m]).forEach((x) => {
            if (!this.shared.has(x)) x.dispose();
          });
        }
      });
    }
    this.scene.background = new THREE.Color(bg);
    this.scene.fog = new THREE.Fog(bg, fogNear, fogFar);
    this.current = env.group;
    this.updater = env.update;
    this.scene.add(env.group);
    this.camera.position.set(...env.spawn.pos);
    this.controls.target.set(...env.spawn.target);
    this.controls.update();
  }
}

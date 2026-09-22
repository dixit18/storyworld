// @storyworld/narrative-runtime — manifest-driven story loading. Never invents story.
export interface Scene {
  sceneId: string;
  title: string;
  narrativeBeat: string;
  purpose: string;
  transitionIn: string;
  transitionOut: string;
  visualAnchor: string;
  portalType: string;
  characters: string[];
  location: string;
  emotion: string;
}

export interface PackageManifest {
  packageId: string;
  storyId: string;
  chapterId: string;
  version: string;
  entrySceneId: string;
  sceneGraphPath: string;
  worldBiblePath: string;
  assetsManifestPath: string;
  audioManifestPath: string;
  transitionsPath: string;
}

export interface ChapterPackage {
  manifest: PackageManifest;
  scenes: Scene[];
  narrationById: Map<string, string>;
  subtitlesById: Map<string, string>;
  assetPathById: Map<string, string>;
  /** sceneId -> ambient audio file URL (from audio_manifest). */
  audioFileByScene: Map<string, string>;
  /** sceneId -> poster data-URI for instant paint (from lod_manifest). */
  posterByScene: Map<string, string>;
  /** sceneId -> particle emitter name (from portal-particles). */
  emitterByScene: Map<string, string>;
  /** emitter name -> config (from portal-particles). */
  emitterConfigs: Map<string, ParticleEmitter>;
  zoomSecondsPerScene: number;
  entryIndex: number;
}

export interface ParticleEmitter {
  count: number;
  color: string;
  size: [number, number];
  rise: number;
  drift: number;
  alpha: number;
}

async function getJSON<T>(base: string, file: string): Promise<T> {
  const r = await fetch(`${base}/${file}`);
  if (!r.ok) throw new Error(`chapter package fetch failed: ${file} (${r.status})`);
  return (await r.json()) as T;
}

/** Load and cross-link a full chapter package from a base URL. Throws on structural errors. */
export async function loadChapterPackage(base: string): Promise<ChapterPackage> {
  const manifest = await getJSON<PackageManifest>(base, 'package_manifest.json');
  const [sg, nar, sub, am, tr, audio, lod, particles] = await Promise.all([
    getJSON<{ storyId: string; chapterId: string; scenes: Scene[] }>(base, manifest.sceneGraphPath),
    getJSON<{ blocks: { sceneId: string; text: string }[] }>(base, 'narration.json'),
    getJSON<{ cues: { sceneId: string; text: string }[] }>(base, 'subtitles.json').catch(() => ({ cues: [] })),
    getJSON<{ assets: { assetId: string; path: string }[] }>(base, manifest.assetsManifestPath),
    getJSON<{ zoomSecondsPerScene: number }>(base, manifest.transitionsPath),
    getJSON<{ tracks: { trackId: string; kind: string; scenes: string[]; file?: string }[] }>(base, manifest.audioManifestPath).catch(() => ({ tracks: [] })),
    getJSON<{ levels: Record<string, { poster?: string }> }>(base, 'lod_manifest.json').catch(
      (): { levels: Record<string, { poster?: string }> } => ({ levels: {} }),
    ),
    getJSON<{ emitters: Record<string, ParticleEmitter>; portalByScene: Record<string, string> }>(base, 'assets/particles/portal-particles.json').catch(() => ({ emitters: {}, portalByScene: {} })),
  ]);

  if (!Array.isArray(sg.scenes) || sg.scenes.length === 0) throw new Error('scene graph has no scenes');
  const ids = new Set(sg.scenes.map((s) => s.sceneId));
  if (ids.size !== sg.scenes.length) throw new Error('duplicate sceneIds in scene graph');

  const entryIndex = Math.max(
    0,
    sg.scenes.findIndex((s) => s.sceneId === manifest.entrySceneId),
  );

  // Convention: assets/images/<sceneId>.svg, verified against the assets manifest.
  const manifestPaths = new Set(am.assets.map((a) => a.path));
  const assetPathById = new Map<string, string>();
  for (const s of sg.scenes) {
    const conventional = `assets/images/${s.sceneId}.svg`;
    const hit = am.assets.find(
      (a) => a.path === conventional || a.assetId === s.sceneId || a.assetId === `${s.sceneId}-bg`,
    );
    const chosen = hit?.path ?? (manifestPaths.has(conventional) ? conventional : null);
    if (chosen) assetPathById.set(s.sceneId, `${base}/${chosen}`);
  }

  const audioFileByScene = new Map<string, string>();
  for (const t of audio.tracks) {
    if (t.kind !== 'ambience' || !t.file) continue;
    for (const sid of t.scenes) {
      if (sid === 'all') {
        for (const s of sg.scenes) audioFileByScene.set(s.sceneId, `${base}/${t.file}`);
      } else if (ids.has(sid)) {
        audioFileByScene.set(sid, `${base}/${t.file}`);
      }
    }
  }

  const posterByScene = new Map<string, string>();
  for (const s of sg.scenes) {
    const poster = lod.levels[`${s.sceneId}-bg`]?.poster ?? lod.levels[s.sceneId]?.poster;
    if (poster) posterByScene.set(s.sceneId, poster);
  }

  return {
    manifest,
    scenes: sg.scenes,
    narrationById: new Map(nar.blocks.map((b) => [b.sceneId, b.text])),
    subtitlesById: new Map(sub.cues.map((c) => [c.sceneId, c.text])),
    assetPathById,
    audioFileByScene,
    posterByScene,
    emitterByScene: new Map(Object.entries(particles.portalByScene)),
    emitterConfigs: new Map(Object.entries(particles.emitters)),
    zoomSecondsPerScene: tr.zoomSecondsPerScene || 14,
    entryIndex,
  };
}

/** Ordered scene navigation with wrap-around (loop closure). */
export function stepIndex(current: number, delta: number, total: number): number {
  return (((current + delta) % total) + total) % total;
}

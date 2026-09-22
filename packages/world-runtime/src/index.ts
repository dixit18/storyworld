// @storyworld/world-runtime — infinite-zoom math (Zoomquilt contract).
// Nesting ratio r=0.5: each successor occupies 50% linear size at the center.
// Zoom phase p in [0,1): current frame scales 1x->2x, nested successor 0.5x->1x.

/** Nesting ratio: successor linear size relative to its parent frame. */
export const NESTING_RATIO = 0.5;

/** Max simultaneously drawn images (Baumgarten's Zoomquilt-2 budget: 4). */
export const MAX_LIVE_IMAGES = 4;

/** Continuous zoom scale for phase p in [0, 1]. */
export function zoomScale(phase: number): number {
  const p = Math.min(1, Math.max(0, phase));
  return Math.pow(1 / NESTING_RATIO, p);
}

/** Nested successor size as a fraction of the current frame at phase p. */
export function nestedFraction(phase: number): number {
  return NESTING_RATIO * zoomScale(phase);
}

/** Fade-in alpha for the nested successor so the seam reads as emergence, not a cut. */
export function nestedAlpha(phase: number): number {
  const p = Math.min(1, Math.max(0, phase));
  return 0.25 + 0.75 * p;
}

/** Deterministic 32-bit seed from story/chapter/scene ids (seed_policy). */
export function seedFor(storyId: string, chapterId: string, sceneId: string): number {
  const s = `${storyId}/${chapterId}/${sceneId}`;
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

/** Mulberry32 PRNG for reproducible procedural visuals. */
export function prng(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

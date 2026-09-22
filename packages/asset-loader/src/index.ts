// @storyworld/asset-loader — bounded-concurrency preloading with graceful fallback.

function loadOne(src: string): Promise<HTMLImageElement | null> {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () => resolve(null); // caller falls back to procedural render
    img.src = src;
  });
}

/** Load a single image URL (posters, overlays). Resolves null on failure. */
export function loadImageURL(src: string): Promise<HTMLImageElement | null> {
  return loadOne(src);
}

/** Preload scene images with bounded concurrency. Never rejects; missing -> null. */
export async function preloadImages(
  sceneIds: string[],
  urlFor: (sceneId: string) => string | undefined,
  concurrency = 4,
): Promise<Map<string, HTMLImageElement | null>> {
  const out = new Map<string, HTMLImageElement | null>();
  let cursor = 0;
  async function worker() {
    while (cursor < sceneIds.length) {
      const id = sceneIds[cursor++];
      const url = urlFor(id);
      out.set(id, url ? await loadOne(url) : null);
    }
  }
  await Promise.all(Array.from({ length: Math.min(concurrency, sceneIds.length) }, worker));
  return out;
}

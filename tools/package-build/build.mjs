// Copies chapter package JSON + SVG assets into app public/package dirs.
// Usage: node tools/package-build/build.mjs [appDir...] (default: apps/web)
import { cpSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const src = join(root, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva');
const targets = process.argv.slice(2);
const apps = targets.length ? targets : ['apps/web'];
for (const app of apps) {
  const dest = join(root, app, 'public', 'package');
  mkdirSync(dest, { recursive: true });
  cpSync(src, dest, { recursive: true });
  console.log(`packaged chapter-01 -> ${app}/public/package`);
}

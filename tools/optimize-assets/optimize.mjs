// Asset Build: minify SVGs, measure gzip, emit posters + LOD manifest + report + build log.
// Usage: node tools/optimize-assets/optimize.mjs
import { readFileSync, writeFileSync, readdirSync, statSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { gzipSync } from 'node:zlib';

const root = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const ch = join(root, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva');
const imgDir = join(ch, 'assets', 'images');

// accent per scene (matches keyframe generator)
const ACCENTS = {
  'adi-01-naimisha': ['#0d1f16', '#C9A227'], 'adi-02-snake-sacrifice': ['#1a0d0d', '#F5F0E1'],
  'adi-03-ganga': ['#0e2438', '#F5F0E1'], 'adi-04-bhishma-vow': ['#241d10', '#C9A227'],
  'adi-05-vyasa-line': ['#191926', '#F5F0E1'], 'adi-06-births': ['#0e2438', '#C9A227'],
  'adi-07-drona': ['#2a1a0d', '#F5F0E1'], 'adi-08-lakshagriha': ['#1a0d0d', '#C9A227'],
  'adi-09-hidimba': ['#070f0c', '#C9A227'], 'adi-10-swayamvara': ['#241d10', '#F5F0E1'],
  'adi-11-division': ['#191926', '#C9A227'], 'adi-12-indraprastha': ['#0e2438', '#F5F0E1'],
};

const minify = (svg) =>
  svg
    .replace(/<!--[\s\S]*?-->/g, '')
    .replace(/>\s+</g, '><')
    .replace(/\s{2,}/g, ' ')
    .trim();

const report = [];
const levels = {};
for (const f of readdirSync(imgDir).filter((f) => f.endsWith('.svg')).sort()) {
  const p = join(imgDir, f);
  const orig = readFileSync(p, 'utf8');
  const origBytes = statSync(p).size;
  const min = minify(orig);
  writeFileSync(p, min);
  const bytes = Buffer.byteLength(min);
  const gz = gzipSync(Buffer.from(min)).length;
  const sceneId = f.replace(/\.svg$/, '');
  const [bg, fg] = ACCENTS[sceneId] ?? ['#0c0f14', '#C9A227'];
  const poster = `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="24" viewBox="0 0 32 24"><rect width="32" height="24" fill="${bg}"/><circle cx="16" cy="12" r="5" fill="${fg}"/></svg>`;
  const assetId = `${sceneId}-bg`;
  levels[assetId] = {
    full: `assets/images/${f}`,
    poster: `data:image/svg+xml,${encodeURIComponent(poster)}`,
    fallback: 'procedural',
  };
  report.push({ assetId, path: `assets/images/${f}`, bytes, gzipBytes: gz, savedBytes: origBytes - bytes, width: 1024, height: 768, status: gz < 20000 ? 'pass' : 'review' });
  console.log(`${assetId}: ${origBytes} -> ${bytes} bytes (gzip ${gz})`);
}

const totalGz = report.reduce((a, r) => a + r.gzipBytes, 0);
writeFileSync(join(ch, 'lod_manifest.json'), JSON.stringify({
  storyId: 'mahabharata', chapterId: 'chapter-01-adi-parva', levels,
}, null, 2));
writeFileSync(join(ch, 'assets_report.json'), JSON.stringify({
  storyId: 'mahabharata', chapterId: 'chapter-01-adi-parva',
  generatedAt: new Date().toISOString().split('T')[0],
  assets: report,
  totalGzipBytes: totalGz,
  budgets: { perAssetGzipBytes: 20000 },
}, null, 2));

const audioFiles = readdirSync(join(ch, 'assets', 'audio')).sort();
let log = `# Build log — mahabharata chapter-01-adi-parva\n\n`;
log += `Date: ${new Date().toISOString().split('T')[0]} · generator storyworld-0.2.0 · assetVersion keyframe-v1\n\n`;
log += `## Steps\n1. synth-audio: ${audioFiles.length} WAV loops (${audioFiles.join(', ')})\n`;
log += `2. optimize: minified ${report.length} keyframe SVGs, total gzip ${(totalGz / 1024).toFixed(1)}KB\n`;
log += `3. lod: full + poster (inline) + procedural fallback per asset -> lod_manifest.json\n`;
log += `4. report: assets_report.json (budgets: per-asset gzip < 20KB)\n`;
const fails = report.filter((r) => r.status !== 'pass');
log += fails.length ? `5. WARNINGS: ${fails.map((r) => r.assetId).join(', ')} over gzip budget\n` : `5. all assets within budget\n`;
writeFileSync(join(ch, 'build_log.md'), log);
console.log(`total keyframe gzip: ${(totalGz / 1024).toFixed(1)}KB`);

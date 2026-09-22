// Deterministic procedural ambience: 4 seamless-loop WAVs (22050 Hz mono 16-bit).
// Usage: node tools/optimize-assets/synth-audio.mjs
import { writeFileSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const SR = 22050;
const SECS = 6;
const N = SR * SECS;

function mulberry(seed) {
  let a = seed >>> 0;
  return () => {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const lp = (fc) => 1 - Math.exp((-2 * Math.PI * fc) / SR);
function lowpass(x, a) {
  const y = new Float64Array(x.length);
  let s = 0;
  for (let i = 0; i < x.length; i++) { s += a * (x[i] - s); y[i] = s; }
  return y;
}
function highpass(x, a) {
  const y = new Float64Array(x.length);
  let s = 0; let prev = 0;
  for (let i = 0; i < x.length; i++) { s = a * (s + x[i] - prev); prev = x[i]; y[i] = s; }
  return y;
}
const norm = (x, peak = 0.85) => {
  let m = 0;
  for (const v of x) m = Math.max(m, Math.abs(v));
  const g = m > 0 ? peak / m : 1;
  return Float64Array.from(x, (v) => v * g);
};
// Blend the tail into the head so the loop is seamless.
function loopBlend(x, secs = 1) {
  const X = Math.floor(SR * secs);
  const out = Float64Array.from(x);
  for (let i = 0; i < X; i++) {
    const t = i / X;
    out[N - X + i] = x[N - X + i] * t + x[i] * (1 - t);
  }
  return out;
}
const lfo = (k, phase = 0) => Float64Array.from({ length: N }, (_, i) => 0.5 + 0.5 * Math.sin((2 * Math.PI * k * i) / N + phase));

function fire(rand) {
  const white = Float64Array.from({ length: N }, () => rand() * 2 - 1);
  let bed = lowpass(white, lp(380));
  const e = lfo(3);
  for (let i = 0; i < N; i++) bed[i] *= 0.55 + 0.45 * e[i];
  // crackle pops
  const hp = highpass(white, 0.92);
  for (let c = 0; c < 46; c++) {
    const at = Math.floor(rand() * (N - 900));
    const amp = 0.25 + rand() * 0.75;
    const decay = 60 + rand() * 500;
    for (let i = 0; i < 900 && at + i < N; i++) bed[at + i] += hp[at + i] * amp * Math.exp(-i / decay);
  }
  return norm(loopBlend(bed));
}
function river(rand) {
  const white = Float64Array.from({ length: N }, () => rand() * 2 - 1);
  const hiss = highpass(white, 0.55);
  const body = lowpass(white, lp(240));
  const e = lfo(2, 1.1);
  const out = new Float64Array(N);
  for (let i = 0; i < N; i++) out[i] = hiss[i] * (0.5 + 0.5 * e[i]) * 0.7 + body[i] * 0.5;
  return norm(loopBlend(out));
}
function forest(rand) {
  const white = Float64Array.from({ length: N }, () => rand() * 2 - 1);
  let bed = highpass(lowpass(white, lp(1100)), 0.35);
  for (let i = 0; i < N; i++) bed[i] *= 0.35;
  // bird chirps: sine glides with Hamming envelope
  for (let c = 0; c < 9; c++) {
    const at = Math.floor(rand() * (N - 7000));
    const len = 4000 + Math.floor(rand() * 3000);
    const f0 = 2200 + rand() * 800;
    const f1 = f0 + 400 + rand() * 900;
    for (let i = 0; i < len && at + i < N; i++) {
      const t = i / len;
      const f = f0 + (f1 - f0) * t;
      const env = 0.54 - 0.46 * Math.cos((2 * Math.PI * i) / len);
      bed[at + i] += 0.5 * env * Math.sin(2 * Math.PI * f * (at + i) / SR);
    }
  }
  return norm(loopBlend(bed), 0.8);
}
function court(rand) {
  const white = Float64Array.from({ length: N }, () => rand() * 2 - 1);
  const bed = lowpass(white, lp(160));
  const out = new Float64Array(N);
  for (let i = 0; i < N; i++) {
    out[i] = bed[i] * 0.5
      + 0.06 * Math.sin((2 * Math.PI * 110 * i) / SR)
      + 0.025 * Math.sin((2 * Math.PI * 220 * i) / SR + 0.7);
  }
  return norm(loopBlend(out), 0.7);
}

function wav(samples) {
  const buf = Buffer.alloc(44 + samples.length * 2);
  buf.write('RIFF', 0); buf.writeUInt32LE(36 + samples.length * 2, 4); buf.write('WAVE', 8);
  buf.write('fmt ', 12); buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20);
  buf.writeUInt16LE(1, 22); buf.writeUInt32LE(SR, 24);
  buf.writeUInt32LE(SR * 2, 28); buf.writeUInt16LE(2, 32); buf.writeUInt16LE(16, 34);
  buf.write('data', 36); buf.writeUInt32LE(samples.length * 2, 40);
  for (let i = 0; i < samples.length; i++) {
    const v = Math.max(-1, Math.min(1, samples[i]));
    buf.writeInt16LE(Math.round(v * 32767), 44 + i * 2);
  }
  return buf;
}

const root = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const outDir = join(root, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva', 'assets', 'audio');
mkdirSync(outDir, { recursive: true });
const kinds = { forest: [forest, 101], fire: [fire, 202], river: [river, 303], court: [court, 404] };
for (const [name, [fn, seed]] of Object.entries(kinds)) {
  const samples = fn(mulberry(seed));
  const path = join(outDir, `amb-${name}.wav`);
  writeFileSync(path, wav(samples));
  console.log(`amb-${name}.wav ${(samples.length / SR).toFixed(1)}s ${(Buffer.byteLength(wav(samples)) / 1024).toFixed(0)}KB`);
}

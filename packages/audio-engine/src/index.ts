// @storyworld/audio-engine — narration (SpeechSynthesis) + procedural WebAudio ambience.
// No audio assets required in v0; recorded stems replace these in phase 2.

export type AmbienceKind = 'forest' | 'fire' | 'river' | 'court';

export function ambienceForScene(sceneId: string): AmbienceKind {
  if (/naimisha|hidimba/.test(sceneId)) return 'forest';
  if (/snake|lakshagriha|indraprastha/.test(sceneId)) return 'fire';
  if (/ganga|births/.test(sceneId)) return 'river';
  return 'court';
}

let audioCtx: AudioContext | null = null;
let ambNodes: { stop: () => void } | null = null;

function noiseBuffer(ctx: AudioContext, seconds = 2): AudioBuffer {
  const buf = ctx.createBuffer(1, ctx.sampleRate * seconds, ctx.sampleRate);
  const d = buf.getChannelData(0);
  for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
  return buf;
}

/** Start looped, filtered-noise ambience for a kind. Returns a stop handle. Idempotent. */
export function startAmbience(kind: AmbienceKind): () => void {
  stopAmbience();
  try {
    audioCtx ??= new AudioContext();
    const ctx = audioCtx;
    if (ctx.state === 'suspended') void ctx.resume();
    const src = ctx.createBufferSource();
    src.buffer = noiseBuffer(ctx);
    src.loop = true;
    const filter = ctx.createBiquadFilter();
    const gain = ctx.createGain();
    const table = {
      forest: { type: 'bandpass', freq: 900, q: 0.6, gain: 0.05 },
      fire: { type: 'lowpass', freq: 420, q: 0.4, gain: 0.09 },
      river: { type: 'highpass', freq: 1400, q: 0.5, gain: 0.05 },
      court: { type: 'bandpass', freq: 420, q: 0.8, gain: 0.035 },
    } as const;
    const cfg = table[kind];
    filter.type = cfg.type as BiquadFilterType;
    filter.frequency.value = cfg.freq;
    filter.Q.value = cfg.q;
    gain.gain.value = cfg.gain;
    src.connect(filter).connect(gain).connect(ctx.destination);
    src.start();
    const stop = () => {
      try { src.stop(); } catch { /* already stopped */ }
      src.disconnect();
    };
    ambNodes = { stop };
    return stopAmbience;
  } catch {
    return () => {};
  }
}

export function stopAmbience(): void {
  try { ambNodes?.stop(); } catch { /* noop */ }
  ambNodes = null;
}

let fileAudio: HTMLAudioElement | null = null;

/** Play a generated ambience file on loop. Resolves false if it cannot play. */
export async function playFileLoop(url: string, volume = 0.8): Promise<boolean> {
  stopFileLoop();
  stopAmbience();
  try {
    const el = new Audio(url);
    el.loop = true;
    el.volume = volume;
    fileAudio = el;
    await el.play();
    return true;
  } catch {
    fileAudio = null;
    return false;
  }
}

export function stopFileLoop(): void {
  try {
    fileAudio?.pause();
    fileAudio = null;
  } catch { /* noop */ }
}

/** Scene ambience: generated file first, procedural WebAudio fallback. */
export async function playSceneAmbience(fileUrl: string | undefined, fallback: AmbienceKind): Promise<void> {
  if (fileUrl) {
    if (await playFileLoop(fileUrl)) return;
  }
  stopFileLoop();
  startAmbience(fallback);
}
export function speak(text: string): void {
  try {
    speechSynthesis.cancel();
    speechSynthesis.speak(new SpeechSynthesisUtterance(text));
  } catch { /* TTS unavailable */ }
}

export function stopSpeech(): void {
  try { speechSynthesis.cancel(); } catch { /* noop */ }
}

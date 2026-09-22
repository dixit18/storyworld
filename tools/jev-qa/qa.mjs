// Jev QA gate: calibrated story-fidelity checks over the Chapter 01 text package.
// Needs TYPESAFE_API_KEY (direct, waitlist) — skips cleanly without it.
// Usage: node tools/jev-qa/qa.mjs [--scene adi-01-naimisha]
import { readFileSync, writeFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { TypeSafeClient, noul, score } from '@typesafe-ai/sdk';

const root = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const ch = join(root, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva');
const load = (f) => JSON.parse(readFileSync(join(ch, f), 'utf8'));

if (!process.env.TYPESAFE_API_KEY) {
  console.log('SKIP: TYPESAFE_API_KEY not set. Get one at typesafe.ai (waitlist) or use Vercel AI Gateway.');
  process.exit(0);
}

const only = process.argv[2] === '--scene' ? process.argv[3] : null;
const bible = load('story_bible.json');
const sg = load('scene_graph.json');
const nar = load('narration.json');
const dlg = load('dialogue.json');
const narrById = new Map(nar.blocks.map((b) => [b.sceneId, b.text]));

const client = new TypeSafeClient();
const thesis = `${bible.logline} Themes: ${bible.themes.join(', ')}.`;
const results = [];
let fail = 0;

for (const s of sg.scenes) {
  if (only && s.sceneId !== only) continue;
  const lines = (dlg.scenes[s.sceneId] ?? []).map((d) => `${d.char}: ${d.line}`).join('\n');
  const state = {
    thesis,
    scene: { id: s.sceneId, title: s.title, beat: s.narrativeBeat, emotion: s.emotion },
    narration: narrById.get(s.sceneId) ?? '',
    dialogue: lines,
  };
  const res = await client.systemOne({
    state,
    questions: {
      fidelity: score(
        'How faithfully do the narration and dialogue serve the scene beat and the epic thesis?',
        ['Off-beat or off-thesis', 'Loosely related', 'On beat', 'On beat and on thesis', 'Exemplary'],
      ),
      contradicts: noul(
        'Any narration or dialogue line contradicts the epic thesis (e.g. purely good-vs-evil framing, victories without cost)',
        { true: 'Contains a contradiction', false: 'No contradiction' },
      ),
    },
  });
  const fid = res.answers.fidelity;
  const con = res.answers.contradicts;
  const bad = (con.noul > 0.7 && con.confidence > 0.6) || (fid.score < 2 && fid.confidence > 0.6);
  if (bad) fail++;
  results.push({
    sceneId: s.sceneId,
    fidelity: { score: fid.score, confidence: fid.confidence },
    contradicts: { p: con.noul, confidence: con.confidence },
    pass: !bad,
  });
  console.log(`${bad ? 'FAIL' : 'PASS'} ${s.sceneId} fidelity=${fid.score} (c=${fid.confidence.toFixed(2)}) contra=${con.noul.toFixed(2)} (c=${con.confidence.toFixed(2)})`);
}

writeFileSync(join(ch, 'qa_jev_report.json'),
  JSON.stringify({ generatedAt: new Date().toISOString().split('T')[0], results }, null, 2));
console.log(`report -> qa_jev_report.json (${results.length} scenes, ${fail} failures)`);
process.exit(fail ? 1 : 0);

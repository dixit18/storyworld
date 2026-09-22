// Jev QA gate: calibrated story-fidelity checks over the Chapter 01 text package.
// Routes (in order): Vercel AI Gateway (AI_GATEWAY_API_KEY, no waitlist) ->
// direct TypeSafe API (TYPESAFE_API_KEY, waitlist). Skips cleanly with neither.
// Usage: node tools/jev-qa/qa.mjs [--scene adi-01-naimisha]
import { readFileSync, writeFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const ch = join(root, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva');
const load = (f) => JSON.parse(readFileSync(join(ch, f), 'utf8'));

const useGateway = !!process.env.AI_GATEWAY_API_KEY;
const useDirect = !!process.env.TYPESAFE_API_KEY;
if (!useGateway && !useDirect) {
  console.log('SKIP: set AI_GATEWAY_API_KEY (Vercel, no waitlist) or TYPESAFE_API_KEY (typesafe.ai).');
  process.exit(0);
}

const only = process.argv[2] === '--scene' ? process.argv[3] : null;
const bible = load('story_bible.json');
const sg = load('scene_graph.json');
const nar = load('narration.json');
const dlg = load('dialogue.json');
const narrById = new Map(nar.blocks.map((b) => [b.sceneId, b.text]));
const thesis = `${bible.logline} Themes: ${bible.themes.join(', ')}.`;

let ask;
if (useGateway) {
  const { experimental_evaluate } = await import('ai');
  ask = (state, questions) =>
    experimental_evaluate({ model: 'typesafe-ai/jev', state, questions });
} else {
  const { TypeSafeClient, score, noul } = await import('@typesafe-ai/sdk');
  const client = new TypeSafeClient();
  ask = (state, questions) => client.systemOne({ state, questions });
  var qScore = score;
  var qNoul = noul;
}

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
  const questions = useGateway
    ? {
        fidelity: {
          type: 'score',
          instructions: 'How faithfully do the narration and dialogue serve the scene beat and the epic thesis?',
          criteria: ['Off-beat or off-thesis', 'Loosely related', 'On beat', 'On beat and on thesis', 'Exemplary'],
        },
        contradicts: {
          type: 'boolean',
          instructions: 'Any narration or dialogue line contradicts the epic thesis (e.g. purely good-vs-evil framing, victories without cost)',
          criteria: { true: 'Contains a contradiction', false: 'No contradiction' },
        },
      }
    : {
        fidelity: qScore(
          'How faithfully do the narration and dialogue serve the scene beat and the epic thesis?',
          ['Off-beat or off-thesis', 'Loosely related', 'On beat', 'On beat and on thesis', 'Exemplary'],
        ),
        contradicts: qNoul(
          'Any narration or dialogue line contradicts the epic thesis (e.g. purely good-vs-evil framing, victories without cost)',
          { true: 'Contains a contradiction', false: 'No contradiction' },
        ),
      };
  const res = await ask(state, questions);

  const fid = res.answers.fidelity;
  const con = res.answers.contradicts;
  const fidScore = fid.score ?? 0;
  const fidConf = fid.confidence ?? res.providerMetadata?.typesafe?.confidence?.fidelity ?? 0;
  const conP = con.noul ?? con.boolean ?? 0;
  const conConf = con.confidence ?? res.providerMetadata?.typesafe?.confidence?.contradicts ?? 0;
  const bad = (conP > 0.7 && conConf > 0.6) || (fidScore < 2 && fidConf > 0.6);
  if (bad) fail++;
  results.push({
    sceneId: s.sceneId,
    fidelity: { score: fidScore, confidence: fidConf },
    contradicts: { p: conP, confidence: conConf },
    pass: !bad,
  });
  console.log(`${bad ? 'FAIL' : 'PASS'} ${s.sceneId} fidelity=${fidScore} contra=${Number(conP).toFixed(2)}`);
}

writeFileSync(join(ch, 'qa_jev_report.json'),
  JSON.stringify({ generatedAt: new Date().toISOString().split('T')[0], results }, null, 2));
console.log(`report -> qa_jev_report.json (${results.length} scenes, ${fail} failures)`);
process.exit(fail ? 1 : 0);

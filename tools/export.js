// Export what the deck builder needs from the app: simulator stages, scenarios, the LIVE block and the Riya case discussion.
const C = require(require('path').join(__dirname, 'load.js'))(process.argv[2]);
const { CASES, SIM_SCEN, LIVE, SCENARIOS } = C.__exp;
const out = { stages: {}, scen: {}, LIVE };
for (const c of CASES) if (c.scen) out.stages[c.id] = { id: c.id, scen: c.scen, stage: c.stage, t: c.t, title: c.title, illus: c.illus || null, story: c.story, event: c.event || '', dx: c.dx || '', live: c.live || null, debrief: c.debrief || null, eyebrow: c.eyebrow };
for (const z of SIM_SCEN) out.scen[z.id] = { title: z.title, setting: z.setting, blurb: z.blurb, eyebrow: z.eyebrow, stages: z.stages };
// Riya (case discussion sc-ltv): stage i becomes ry<i>, its orders become the live orders
const ltv = SCENARIOS.find(z => z.id === 'sc-ltv');
ltv.stages.forEach((t, i) => { if (t.opts) out.stages['ry' + i] = { id: 'ry' + i, story: t.story, event: t.teach || '', live: { q: t.q, opts: t.opts }, illus: null }; });
require('fs').writeFileSync(process.argv[3], JSON.stringify(out));

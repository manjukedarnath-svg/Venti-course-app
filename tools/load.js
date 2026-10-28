// Load the app's top-level constants (everything before `class Component`) into a Node context.
const fs = require('fs'), vm = require('vm');
module.exports = function load(file) {
  const s = fs.readFileSync(file, 'utf8');
  const a0 = s.indexOf('<script type="text/x-dc"'), a = s.indexOf('>', a0), b = s.indexOf('class Component extends DCLogic');
  let code = s.slice(a + 1, b);
  code = code.replace(/^const |\nconst /g, m => m.replace('const', 'var')).replace(/\nfunction /g, '\nvar __f; function ');
  const ctx = { console, Math, JSON, Object, Array, String, Number, window: {}, document: {}, location: { hash: '' } };
  vm.createContext(ctx);
  vm.runInContext(code + '\n;this.__exp = { CASES, PATIENTS, SIM_SCEN, SIM_STAGES, model, vmodeOf, LIVE, SCENARIOS, MODULES };', ctx, { filename: 'app.js' });
  return ctx;
};

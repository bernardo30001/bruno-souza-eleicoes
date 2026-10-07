const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const controls = new Map();
for (const selector of ['#app', '#year', '#office', '#territory', '#drill', '#clear']) {
  controls.set(selector, { innerHTML: '', addEventListener(type, fn) { this[type] = fn; } });
}
const routes = ['overview', 'state', 'neighborhoods', 'compare', 'scenarios'].map(route => ({ dataset: { route } }));
const context = vm.createContext({
  window: { scrollTo() {} }, console,
  document: { activeElement: null, querySelector: s => controls.get(s) || null,
    querySelectorAll: s => s === '[data-route]' ? routes : [] }
});
vm.runInContext(fs.readFileSync('dist/data.js', 'utf8'), context);
vm.runInContext(fs.readFileSync('dist/app.js', 'utf8'), context);
const run = expression => vm.runInContext(expression, context);
const change = (id, value) => controls.get(id).change({ target: { value } });
const route = name => routes.find(r => r.dataset.route === name).onclick();
function reset() { controls.get('#clear').click(); route('overview'); }
function checkState(year) {
  assert.equal(run('rowsFor().length'), 295, `${year}: todos os municípios devem aparecer`);
  assert.equal(run("(mapSvg(election()).match(/data-map-level=\"municipalities\"/g)||[]).length"), 295);
  assert.equal(run('totalOf(rowsFor()).votes'), run('election().totals.votes'));
  assert.match(controls.get('#app').innerHTML, /295 registros/);
}
for (const year of [2018, 2022, 2026]) {
  reset(); change('#year', 2012); change('#year', year); checkState(year);
  reset(); run('selectYear(2016)'); run(`selectYear(${year})`); checkState(year);
  reset(); change('#year', year); route('neighborhoods'); route('state'); checkState(year);
  reset(); change('#year', year); controls.get('#drill').click(); route('overview'); checkState(year);
}
reset(); change('#office', '13'); change('#office', '7'); checkState(2026);
change('#office', '6'); checkState(2022);
reset(); change('#territory', 'GF'); route('neighborhoods'); route('overview');
assert.equal(run('rowsFor().length'), 9, 'um filtro regional escolhido explicitamente deve ser preservado');
change('#year', 2012);
assert.equal(run('rowsFor().length'), 1);
assert.equal(run('totalOf(rowsFor()).votes'), 1491);
change('#year', 2022);
assert.equal(run('rowsFor().length'), 9);
change('#territory', '81795'); // Joinville: uma escolha explícita continua válida entre pleitos estaduais.
assert.equal(run('rowsFor().length'), 1);
change('#year', 2012);
assert.equal(run('rowsFor()[0].id'), '81051');
route('scenarios');
assert.equal(run('scenarioValue(S.scenarios[1])'), 1491);
route('overview'); change('#year', 2026);
assert.equal(run('rowsFor()[0].id'), '81795');
route('state'); checkState(2026);
route('compare'); run('S.compareA=2012; S.compareB=2026; render()');
assert.equal(run('comparisonRows().length'), 1);
run('S.compareA=2018; render()');
assert.equal(run('comparisonRows().length'), 295);
console.log('Navegação validada: anos, cargos, bairros, mapa, filtros explícitos, cenários e comparações.');

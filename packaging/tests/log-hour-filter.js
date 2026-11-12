const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const path = require('path');
const view = fs.readFileSync(path.join(__dirname, '../../opncell/src/opnsense/mvc/app/views/OPNsense/OPNCell/log.volt'), 'utf8');
let timeframe = 'hour', prefilter;
let refreshed = 0, allLabel;
const element = {prepend() {}, text() { return this; }, val() { return timeframe; },
    find(selector) { return {length: 0, text(value) { if (selector === 'option[value="all"]') { allLabel = value; } return this; }}; }, data() { return {}; },
    selectpicker(action) { if (action === 'refresh') { refreshed++; } }
};
const $ = arg => { if (typeof arg === 'function') { arg(); return; } return element; };
let gridSettings;
$.fn = {UIBootgrid: function (settings) { gridSettings = settings; return this; }};
$.ajaxPrefilter = fn => { prefilter = fn; };
const script = view.match(/<script>([\s\S]*?)<\/script>/)[1].replace(/{{.*?}}/g, value => value.includes("'All'") ? 'All' : 'Last hour');
vm.runInNewContext(script, {$, URLSearchParams, Date: {now: () => 1800000000000}});
$.fn.UIBootgrid.call({is: selector => selector === '#grid-log'}, {search:'/api/diagnostics/log/opncell/Last hour', options:{}});
assert.deepEqual(Array.from(gridSettings.options.rowCount), [50, 100, 200, 500, 1000, 5000, -1]);
$.fn.UIBootgrid.call({is: () => false}, {search:'/other', options:{rowCount:[25]}});
assert.deepEqual(gridSettings.options.rowCount, [25]);
const options = {url:'/api/diagnostics/log/opncell/mme', data:'severity=Informational&searchPhrase=IMSI&current=2'};
prefilter(options);
assert.equal(allLabel, 'All');
assert.equal(refreshed, 1, 'Initialized picker must refresh after adding the option');
let params = new URLSearchParams(options.data);
assert.equal(params.get('validFrom'), '1799996400');
assert.equal(params.get('searchPhrase'), 'IMSI');
assert.equal(params.get('severity'), 'Informational');
assert.equal(params.get('current'), '2');
assert.equal(options.url, '/api/opncell/log/query/mme');
timeframe = 'day';
const day = {url:'/api/diagnostics/log/opncell/mme', data:'validFrom=1799913600'};
prefilter(day);
assert.equal(day.data, 'validFrom=1799913600');
timeframe = 'hour';
for (const count of [100, 5000, -1]) {
    const original = {rowCount:count,current:3,severity:['Informational'],searchPhrase:'UE',sort:{timestamp:'desc'}};
    const json = {url:'/api/diagnostics/log/opncell/amf',contentType:'application/json',data:JSON.stringify(original)};
    prefilter(json);
    const result = JSON.parse(json.data);
    assert.deepEqual(result, {...original,validFrom:1799996400});
    assert.equal(json.url, '/api/opncell/log/query/amf');
}
console.log('SUCCESS: JSON and form hour requests preserve page size, All, page, search and severity');

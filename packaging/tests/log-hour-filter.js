const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const path = require('path');
const view = fs.readFileSync(path.join(__dirname, '../../opncell/src/opnsense/mvc/app/views/OPNsense/OPNCell/log.volt'), 'utf8');
let timeframe = 'hour', prefilter;
let refreshed = 0;
const element = {prepend() {}, text() { return this; }, val() { return timeframe; },
    find() { return {length: 0}; }, data() { return {}; },
    selectpicker(action) { if (action === 'refresh') { refreshed++; } }
};
const $ = arg => { if (typeof arg === 'function') { arg(); return; } return element; };
$.ajaxPrefilter = fn => { prefilter = fn; };
const script = view.match(/<script>([\s\S]*?)<\/script>/)[1].replace(/{{.*?}}/g, 'Last hour');
vm.runInNewContext(script, {$, URLSearchParams, Date: {now: () => 1800000000000}});
const options = {url:'/api/diagnostics/log/opncell/mme', data:'severity=Informational&searchPhrase=IMSI&current=2'};
prefilter(options);
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
console.log('SUCCESS: hour cutoff, existing filters, routing and day cutoff preserved');

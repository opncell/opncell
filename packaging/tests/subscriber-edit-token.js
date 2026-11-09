// Pass the path to the BSON module bundled with opncell-mongosh.
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const {EJSON} = require(process.argv[2]);
const source = fs.readFileSync(path.join(__dirname, '../../opncell/src/opnsense/scripts/opncell/updateSubscriberProfiles.py'), 'utf8');
const normalize = vm.runInNewContext(source.slice(source.indexOf('function sortedSnapshot'), source.indexOf('const canonicalToken')) + '\nsortedSnapshot');
const fixture = fs.readFileSync(path.join(__dirname, 'fixtures/subscriber-edit-token.ejson'), 'utf8');
const expected = fs.readFileSync(path.join(__dirname, 'fixtures/subscriber-edit-token.sha256'), 'utf8').trim();
for (const relaxed of [false, true]) {
    const document = EJSON.parse(fixture, {relaxed});
    const token = require('crypto').createHash('sha256').update(JSON.stringify(normalize(EJSON.serialize(document, {relaxed:false})))).digest('hex');
    if (token !== expected) throw new Error('BSON numeric promotion changed the edit token');
}
console.log('SUCCESS: BSON doubles and Int64 edit tokens match before and after numeric promotion');

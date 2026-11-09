import csv
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[2] / 'opncell/src/opnsense/scripts/opncell'
sys.path.insert(0, str(SCRIPTS))
import export_subscribers as exporter
import saveUsers as writer


def plain(value):
    if isinstance(value, dict):
        if set(value) == {'$numberInt'}:
            return int(value['$numberInt'])
        return {key: plain(item) for key, item in value.items()}
    if isinstance(value, list):
        return [plain(item) for item in value]
    return value


class SubscriberExportTests(unittest.TestCase):
    def test_csv_roundtrip_preserves_new_provisioning_fields(self):
        profile = {'sst': '1', 'sd': '000001', 'session_type': '3', 'lbo_roaming_allowed': '1',
                   'apn': 'internet', 'dl': '100', 'ul': '50', 'QoS': '9',
                   'arp_priority': '8', 'arp_capability': '1', 'arp_vulnerability': '2'}
        fields = {'imsi': '001010000000001', 'ki': '11'*16, 'opc': '22'*16, 'amf': '8000',
                  'msisdn': '12345,67890', 'ue_ambr_downlink': '123', 'ue_ambr_downlink_unit': '2',
                  'ue_ambr_uplink': '45', 'ue_ambr_uplink_unit': '2', 'subscriber_status': '1',
                  'operator_determined_barring': '8', 'default_slice': '1:000001',
                  'session_addresses': '{"1:000001/internet":{"ue":{"ipv4":"10.0.0.5","ipv6":"2001:db8::5"}}}'}
        original = plain(writer.build_subscriber({'count': 1, '1': {**fields, **profile}}))
        original['security']['sqn'] = 12345
        exported = exporter.export_row(original)
        stream = io.StringIO()
        csv_writer = csv.DictWriter(stream, exporter.FIELDS)
        csv_writer.writeheader()
        csv_writer.writerow(exported)
        stream.seek(0)
        row = next(csv.DictReader(stream))
        self.assertEqual(json.loads(row['profiles']), ['1:000001/internet'])
        restored = plain(writer.build_subscriber({'count': 1, '1': {**row, **profile}}))
        original['security'].pop('sqn')
        self.assertEqual(original, restored)
        self.assertNotIn('sqn', exported)
        self.assertEqual(row['imsi'], fields['imsi'])

    def test_legacy_integral_doubles_use_integer_form_values(self):
        doc = {'imsi': '001010000000001', 'subscriber_status': 0.0,
               'operator_determined_barring': 0.0,
               'ambr': {'downlink': {'value': 1000000000.0, 'unit': 0.0},
                        'uplink': {'value': 1000000000.0, 'unit': 0.0}},
               'slice': [{'sst': 1.0, 'default_indicator': True, 'session': [{'name': 'internet'}]}]}
        row = exporter.export_row(doc)
        self.assertEqual(row['subscriber_status'], '0')
        self.assertEqual(row['operator_determined_barring'], '0')
        self.assertEqual(row['ue_ambr_downlink'], '1000000000')
        self.assertEqual(row['ue_ambr_downlink_unit'], '0')
        self.assertEqual(row['default_slice'], '1')
        self.assertEqual(json.loads(row['profiles']), ['1/internet'])
        from subscriber_identity import policy_fields
        self.assertEqual(policy_fields(row)['subscriber_status'], 0)
        self.assertEqual(doc['subscriber_status'], 0.0)
        self.assertIsInstance(doc['subscriber_status'], float)

    def test_fractional_policy_value_is_not_rounded(self):
        from subscriber_identity import policy_fields
        row = exporter.export_row({'imsi': '001010000000001', 'subscriber_status': 0.5})
        with self.assertRaises(ValueError): policy_fields(row)
        self.assertEqual(exporter.provisioning_rules({'qos': {'index': 9.0, 'bad': 1.5}}),
                         {'qos': {'index': 9, 'bad': 1.5}})

    def test_nested_ids_not_exported_as_pcc_inputs(self):
        self.assertEqual(exporter.provisioning_rules([{'_id': object(), 'qos': {'_id': object(), 'index': 9}}]),
                         [{'qos': {'index': 9}}])

    def test_database_failure_does_not_export_empty_success(self):
        def unavailable(*args, **kwargs):
            raise RuntimeError('unavailable')
        with self.assertRaises(RuntimeError):
            exporter.fetch_export(unavailable)


if __name__ == '__main__':
    unittest.main()

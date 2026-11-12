#!/usr/local/bin/python3.13
"""Use the platform parser with exact filtered counts and consistent pagination."""
import argparse
from datetime import datetime
import json
import sys
from log_source import resolve_log


def matching_time(record, since):
    if not since:
        return True
    try:
        return datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00')).timestamp() >= since
    except (KeyError, TypeError, ValueError, AttributeError):
        return False


def page_records(records, limit, offset, since=0, emit=None):
    rows, total = [], 0
    for record in records:
        # The platform generator yields its first older record before stopping.
        # Exclude that boundary record before counting or paginating matches.
        if not matching_time(record, since):
            continue
        index = total
        total += 1
        if index >= offset and (limit == 0 or index < offset + limit):
            if emit is None:
                rows.append(record)
            else:
                emit(record)
    return rows, total


def main():
    if len(sys.argv) == 3 and sys.argv[1] == '--source':
        print(json.dumps({'path': str(resolve_log(sys.argv[2]))}))
        return
    sys.path.insert(0, '/usr/local/opnsense/scripts/syslog')
    from log_matcher import LogMatcher
    original = LogMatcher.fetch_log_filenames

    def filenames(filename, module):
        return [str(resolve_log(filename))] if module == 'opncell' else original(filename, module)

    LogMatcher.fetch_log_filenames = staticmethod(filenames)
    parser = argparse.ArgumentParser()
    for name, default in (('output', 'json'), ('filter', ''), ('limit', '0'),
                          ('offset', '0'), ('filename', ''), ('module', 'opncell'),
                          ('severity', ''), ('valid_from', '0')):
        parser.add_argument('--' + name, default=default)
    args = parser.parse_args()
    limit, offset, since = max(0, int(args.limit)), max(0, int(args.offset)), float(args.valid_from)
    matcher = LogMatcher(args.filter, args.filename, args.module, args.severity)
    emit = None if args.output == 'json' else lambda record: print(
        '%(timestamp)s\t%(severity)s\t%(process_name)s\t%(line)s' % record)
    rows, total = page_records(matcher.match_records(since), limit, offset, since, emit)
    if args.output == 'json':
        print(json.dumps({'filters': args.filter, 'rows': rows, 'total_rows': total, 'origin': args.filename}))


if __name__ == '__main__':
    main()

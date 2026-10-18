"""Check the complete hosted-owner interface at the candidate boundary.

The row-time/digest contract follows the guard identified in PR1959
(Josie Elliston), PR2301 (Aaron Wang), and its PR2309 continuation.
The immutable predecessor is unchanged; this check covers our emitted data.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

FIELDS = ('child', 'copy', 'family', 'helper', 'offset', 'owner_replica',
          'port', 'replica', 'stage', 'time', 'width')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows_by_key(rows):
    require(isinstance(rows, list), 'Owner rows must be a list')
    result = {}
    for row in rows:
        require(isinstance(row, dict) and set(row) == set(FIELDS),
                'Hosted owner row must contain exactly all 11 interface fields')
        require(all(type(value) is int for value in row.values()),
                'Hosted owner fields must be integers')
        key = (row['stage'], row['replica'], row['helper'])
        require(key not in result, 'Duplicate hosted owner key')
        result[key] = row
    return result


def validate_payload(template, owners, owner_sha256):
    hosting = template['hosting']
    require(hosting['owner_map_sha256'] == owner_sha256,
            'Hosted owner-map digest differs from the actual OWNERS gzip bytes')
    actual, expected = rows_by_key(hosting['pooled_slots']), rows_by_key(owners)
    require(actual == expected,
            'Hosted owner rows differ from OWNERS, including row time')
    digest = hashlib.sha256()
    for key in sorted(expected):
        digest.update(json.dumps(expected[key], sort_keys=True,
                                 separators=(',', ':')).encode() + b'\n')
    return {'status': 'PASS_HOSTED_OWNER_ROWS_AND_DIGEST',
            'rows': len(expected), 'fields': list(FIELDS),
            'owner_map_sha256': owner_sha256,
            'canonical_sorted_owner_rows_sha256': digest.hexdigest()}


def validate_hosted_owner_map(template_path, owners_path):
    result = validate_payload(read(template_path), read(owners_path), sha(owners_path))
    result['emitted_template_sha256'] = sha(template_path)
    return result


def mutation_controls(template_path, owners_path):
    template, owners = read(template_path), read(owners_path)
    digest = sha(owners_path)
    honest = validate_payload(template, owners, digest)
    rejected = []
    row = template['hosting']['pooled_slots'][0]
    row['time'] += 1
    try:
        validate_payload(template, owners, digest)
    except ValueError:
        rejected.append('corrupt-hosted-row-time')
    else:
        raise ValueError('Corrupt hosted time was accepted')
    finally:
        row['time'] -= 1
    original = template['hosting']['owner_map_sha256']
    template['hosting']['owner_map_sha256'] = '0'*64
    try:
        validate_payload(template, owners, digest)
    except ValueError:
        rejected.append('wrong-hosted-owner-map-digest')
    else:
        raise ValueError('Wrong hosted owner-map digest was accepted')
    finally:
        template['hosting']['owner_map_sha256'] = original
    return {'status': 'PASS_HOSTED_OWNER_BINDING_MUTATION_CONTROLS',
            'honest': honest, 'rejected': rejected,
            'emitted_template_sha256': sha(template_path)}


def main():
    if not __debug__:
        raise RuntimeError('Assertions must be enabled for the complete replay')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--template', type=Path, required=True)
    parser.add_argument('--owners', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--mutation-controls', action='store_true')
    args = parser.parse_args()
    check = mutation_controls if args.mutation_controls else validate_hosted_owner_map
    result = check(args.template, args.owners)
    args.out.write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'])


if __name__ == '__main__':
    main()

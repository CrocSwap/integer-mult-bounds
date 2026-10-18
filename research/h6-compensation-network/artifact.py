"""Readable receipts with canonical, losslessly compressed proof data.

Mathematical binding uses canonical decompressed JSON, never gzip headers.
"""
from pathlib import Path
import gzip
import hashlib
import json
import tempfile


def need(ok, message):
    if not ok:
        raise ValueError(message)


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        need(key not in value, 'duplicate JSON proof field: '+key)
        value[key] = item
    return value


def parse(raw):
    return json.loads(raw, object_pairs_hook=unique_object)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=True, allow_nan=False)+'\n').encode()


def canonical_sha256(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def write_gzip_json(path, value):
    path = Path(path)
    raw = canonical(value)
    path.write_bytes(gzip.compress(raw, mtime=0))
    return hashlib.sha256(raw).hexdigest()


def load_gzip_json(path):
    return parse(gzip.decompress(Path(path).read_bytes()))


def write_receipt(path, result, fields):
    path = Path(path)
    need('proof_data' not in result and len(fields) == len(set(fields)),
         'invalid proof-data split')
    data = {key: result[key] for key in sorted(fields)}
    summary = {key: value for key, value in result.items() if key not in data}
    data_path = path.with_name(path.stem+'-DATA.json.gz')
    summary['proof_data'] = dict(format='canonical-json-gzip-v1', file=data_path.name,
        fields=sorted(fields), canonical_sha256=write_gzip_json(data_path, data))
    path.write_text(json.dumps(summary, sort_keys=True, indent=2)+'\n')


def load_receipt(path):
    path = Path(path)
    summary = parse(path.read_bytes())
    descriptor = summary.pop('proof_data', None)
    if descriptor is None:
        return summary
    need(descriptor['format'] == 'canonical-json-gzip-v1', 'proof-data format')
    name = descriptor['file']
    need(Path(name).name == name and name.endswith('.json.gz'), 'proof-data path')
    data = load_gzip_json(path.with_name(name))
    need(isinstance(data, dict) and sorted(data) == descriptor['fields'],
         'proof-data field inventory')
    need(not set(data).intersection(summary), 'proof data overrides summary')
    need(canonical_sha256(data) == descriptor['canonical_sha256'],
         'canonical proof-data binding')
    return dict(summary, **data)


def main():
    with tempfile.TemporaryDirectory(prefix='h6-artifact-control-') as directory:
        path = Path(directory)/'RESULT.json'
        original = dict(status='fixture', coefficients=[[1, -5], [5, -1]], labels=[3, 7])
        write_receipt(path, original, ['coefficients', 'labels'])
        need(load_receipt(path) == original, 'split receipt round trip')
        descriptor = parse(path.read_bytes())['proof_data']
        data_path = path.with_name(descriptor['file'])
        raw = gzip.decompress(data_path.read_bytes())
        data_path.write_bytes(gzip.compress(raw, mtime=123456789))
        need(load_receipt(path) == original, 'gzip metadata must not affect mathematics')
        changed = parse(raw)
        changed['coefficients'][0][0] = 2
        write_gzip_json(data_path, changed)
        try:
            load_receipt(path)
        except ValueError as exc:
            need('canonical proof-data binding' in str(exc), 'payload mutation reason')
        else:
            raise ValueError('Changed proof data was accepted')
        try:
            parse('{"labels":[],"labels":[1]}')
        except ValueError as exc:
            need('duplicate JSON proof field' in str(exc), 'duplicate field reason')
        else:
            raise ValueError('Duplicate proof field was accepted')
    package = Path(__file__).resolve().parent
    manifest = parse((package/'PACKAGING.json').read_bytes())
    for entry in manifest['artifacts']:
        if 'summary' in entry:
            value = load_receipt(package/entry['summary'])
            data = {key: value[key] for key in entry['fields']}
        else:
            data = load_gzip_json(package/entry['gzip_artifact'])
        need(canonical_sha256(data) == entry['canonical_sha256'],
             'proof data changed from submitted baseline: '+entry['original_artifact'])
    print('PASS_CANONICAL_COMPRESSED_PROOF_DATA_AND_MUTATION_CONTROLS', flush=True)


if __name__ == '__main__':
    main()

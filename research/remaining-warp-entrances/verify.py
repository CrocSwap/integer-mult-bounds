"""Regenerate the new later-warp census; no predecessor verifier is run.

Produced by Nick Petalas. Apache-2.0.
"""
import ast
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path, limit=4 * 1024 * 1024):
    need(path.is_file() and path.stat().st_size <= limit, 'file size/type: ' + str(path))
    data = path.read_bytes()
    need(len(data) <= limit, 'file grew: ' + str(path))
    return data


def load_module(name, path):
    module = ModuleType(name)
    module.__file__ = str(path)
    exec(compile(read(path), str(path), 'exec', optimize=0), module.__dict__)
    return module


def validate_binding(data, entry):
    digest = hashlib.sha256(data).hexdigest()
    need(digest == entry['sha256'], 'source hash: ' + entry['path'])
    blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    need(blob == entry['git_blob'], 'source blob: ' + entry['path'])
    return digest


def authenticate():
    manifest = json.loads(read(HERE / 'SOURCES.json'))
    hashes = {}
    for entry in manifest['files']:
        if entry['usage'] == 'input':
            hashes[entry['path']] = validate_binding(read(ROOT / entry['path']), entry)
    return hashes


def source_word():
    path = ROOT / 'research/transported-warp-frames/inputs/BASE-WORD.json.gz'
    with gzip.open(path, 'rb') as stream:
        data = stream.read(4 * 1024 * 1024 + 1)
    need(len(data) <= 4 * 1024 * 1024, 'expanded source capacity')
    word = json.loads(data)
    need(len(word['warps']) == 72, 'source geometry')
    return word


def signature(word, model, scales=()):
    omitted = {p for p, _r in scales}
    seq = []
    for kind, k in model.events(word):
        if kind == 'warp':
            rec = word['warps'][k]
            seq.append(('warp', k, rec[1], tuple(rec[2])))
        elif kind != 'B' or k not in omitted:
            seq.append((kind, tuple(word[kind][k][:-1])))
    return seq


def changed_word_checks(source, got, scales, model, audit, original_inventory):
    need(signature(source, model) == signature(got, model, scales), 'ordered operator changed')
    for name in source:
        if name not in {'B', 'warps', 'restore', 'cleanup'}:
            need(source[name] == got[name], 'caller field changed: ' + name)
    for section in ('B', 'restore'):
        old = source[section]
        new = [g for k, g in enumerate(got[section])
               if section != 'B' or k not in {p for p, _r in scales}]
        need(len(old) == len(new), 'scalar count changed')
        for g, h in zip(old, new):
            need(g[:-1] == h[:-1], 'scalar operator changed')
            need(model.span(g[-1]) & ~model.span(h[-1]) == 0, 'original floor lost')
    need(got['restore'][191] == source['restore'][191], 'centre restore changed')
    need([g for g in got['cleanup'] if g[0] != 'scale' or g[2] != g[3]] ==
         [g for g in source['cleanup'] if g[0] != 'scale' or g[2] != g[3]],
         'nonidentity cleanup changed')
    audit.hygiene(got)
    profile, inventory, chain, _start, _end = audit.frame_bill(got, lagrangian=True)
    need(inventory == original_inventory, 'productive helper inventory changed')
    terminal = Counter(e[1] for entries in chain.values() for e in entries
                       if e[0] == ('end',) and e[1])
    return profile, dict(sorted(terminal.items()))


def census(word, model, audit):
    sequence = model.events(word)
    maps = [model.images(rec[2]) for rec in word['warps']]
    capacities = model.capacities(word, sequence, maps)
    dual = model.dual_capacities(word, sequence)
    later = [k for kind, k in sequence[sequence.index(('warp', 13)) + 1:] if kind == 'warp']
    baseline, inventory, _chain, _start, _end = audit.frame_bill(word)
    need(baseline == {1: 2440, 2: 725, 3: 224, 4: 102, 5: 20, 8: 8}, 'base invoice')
    rows = []
    for k in later:
        rec, cap = word['warps'][k], capacities[k]
        need(cap == dual[k], 'point-set/annihilator capacity disagreement')
        gap = len(model.basis(cap)) - len(rec[3])
        need(gap in (0, 1), 'unclassified capacity gap')
        row = {'warp': k, 'position': rec[0], 'lender': rec[1],
               'original_basis': rec[3], 'capacity_basis': model.basis(cap),
               'legal_entrance_count': 1 + gap}
        if gap:
            assigned = model.closure(word, sequence, maps, k, cap)
            got, scales = model.compile_word(word, assigned, maps, audit)
            need(scales == [(rec[0], rec[1])], 'unexpected entrance climbs')
            profile, end = changed_word_checks(word, got, scales, model, audit, inventory)
            change = model.delta(profile, baseline)
            need(sum(r * n for r, n in change.items()) == 0, 'rank mass changed')
            row.update(profile=profile, delta=change, sign_class=model.power_class(change),
                       terminal_climbs=end, inserted_climbs=scales,
                       changed_warp_boundaries=sum(model.span(a[3]) != model.span(b[3])
                                                  for a, b in zip(word['warps'], got['warps'])))
        rows.append(row)
    return rows


def reject(function, args):
    try:
        function(*args)
    except ValueError:
        return
    raise ValueError('rejection control accepted')


def controls(word, model, audit):
    for bad in ([-1], [512], [True], list(range(19))):
        reject(model.span, (bad,))
    for bad in (0, 2, 11, model.FULL + 1):
        reject(model.basis, (bad,))
    reject(model.images, ([0] * 9,))
    reject(model.power_class, ({1: -2, 2: 1},))
    reject(model.power_class, ({1: 5, 5: -1},))
    sequence = model.events(word)
    maps = [model.images(rec[2]) for rec in word['warps']]
    caps = model.capacities(word, sequence, maps)
    rec = word['warps'][15]
    reject(model.closure, (word, sequence, maps, 15, model.ZERO))
    outside = next(p for p in range(512) if not caps[15] >> p & 1)
    reject(model.closure, (word, sequence, maps, 15, model.join(caps[15], model.span([outside]))))
    assigned = model.closure(word, sequence, maps, 15, caps[15])
    got, scales = model.compile_word(word, assigned, maps, audit)
    need(len(scales) == 1, 'control climb')
    bad = json.loads(json.dumps(got))
    bad['warps'][15][4] = rec[4]
    try:
        audit.frame_bill(bad)
    except audit.AuditFailure:
        pass
    else:
        raise ValueError('wrong exit accepted')
    bad = json.loads(json.dumps(got))
    del bad['B'][scales[0][0]]
    for item in bad['warps']:
        if item[0] > scales[0][0]:
            item[0] -= 1
    try:
        audit.frame_bill(bad)
    except audit.AuditFailure:
        pass
    else:
        raise ValueError('missing paid climb accepted')
    manifest = json.loads(read(HERE / 'SOURCES.json'))
    bindings = [e for e in manifest['files'] if e['usage'] == 'input']
    for entry in bindings:
        data = read(ROOT / entry['path'])
        reject(validate_binding, (data + b'changed', entry))
    return 15 + len(bindings)


def summary(rows):
    enlarged = [r for r in rows if r['legal_entrance_count'] == 2]
    equal = [r['warp'] for r in enlarged if r['sign_class'] == 'equal']
    rigid = [r['warp'] for r in rows if r['legal_entrance_count'] == 1]
    need(len(rows) == 62 and len(enlarged) == 52 and len(rigid) == 10, 'census cardinality')
    need(equal == [31, 40], 'neutral cases')
    need(all(len(r['capacity_basis']) == 5 for r in rows), 'capacity dimension')
    classes = Counter(r['sign_class'] for r in enlarged)
    patterns = Counter(tuple(sorted(r['delta'].items())) for r in enlarged)
    return {'events': 62, 'rigid': rigid, 'enlargements': 52,
            'equal': equal, 'strict_power_losses': 50, 'classes': dict(sorted(classes.items())),
            'histogram_patterns': [{'delta': dict(k), 'count': v} for k, v in sorted(patterns.items())]}


def main():
    before = authenticate()
    model = load_module('remaining_model', HERE / 'model.py')
    audit = load_module('retained_frame_bill', ROOT / 'research/transported-warp-frames/vendor/audit_core.py')
    word = source_word()
    centers = set(word['centers'])
    need(all(not centers.intersection(model.touched(g)) for g in word['B']), 'B touches centre')
    need([k for k, g in enumerate(word['restore']) if centers.intersection(model.touched(g))]
         == [191], 'centre restore inventory')
    rows = census(word, model, audit)
    result = summary(rows)
    result['rejection_controls'] = controls(word, model, audit)
    need(before == authenticate(), 'source changed during replay')
    files = sorted(p for p in HERE.iterdir() if p.is_file())
    need(len(files) <= 10, 'package file capacity')
    for p in files:
        if p.suffix == '.py':
            ast.parse(read(p))
    result.update(status='PASS_REMAINING_WARP_ENTRANCES', rows=rows,
                  source_sha256=before,
                  package_sha256={p.name: hashlib.sha256(read(p)).hexdigest() for p in files})
    print(json.dumps(result, sort_keys=True))
    print('PASS_REMAINING_WARP_ENTRANCES no_new_kappa')


if __name__ == '__main__':
    main()

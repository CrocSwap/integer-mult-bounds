#!/usr/bin/env python3
"""Source-bound PR2101 Windows-role audit; constructed relocation, no supplier run.

AAAmirinu with substantial OpenAI Codex assistance. Apache-2.0.
Fixture bindings follow Adam Gall's PR2101 and Josie Elliston's PR1824.
"""
import argparse
import copy
import gzip
import itertools
import json
import os
from pathlib import Path, PurePosixPath
import sys
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import compare_roles as adapter

old = adapter.predecessor
require = adapter.require
A1094 = 'research/community-frontier1094-audit/'
A1042 = 'research/community-frontier1042-audit/'
OWNER = 'research/complex-t16-rare-pattern-exchanges/data/OWNERS.json.gz'
REF_WORK = '/private/tmp/batch1099-selected/candidate'
REF_LOCAL = '/private/tmp/batch1047-selected/slots/local'


def authenticate():
    rows = json.loads((HERE / 'SOURCES.json').read_bytes())['files']
    inputs = [r for r in rows if r['usage'] == 'input']
    for row in inputs:
        adapter.check_bytes((ROOT / row['path']).read_bytes(), row['sha256'], row['path'])
    return len(inputs)


def archive_files(path, prefix=''):
    result = {}
    with tarfile.open(path) as archive:
        for member in archive:
            if member.isdir() or not member.name.startswith(prefix):
                continue
            name = member.name[len(prefix):]
            part = PurePosixPath(name)
            require(member.isfile() and name and part.as_posix() == name
                    and not part.is_absolute() and '..' not in part.parts
                    and '\\' not in name and name not in result, 'unsafe archive member')
            result[name] = archive.extractfile(member).read()
    return result


def fixture():
    local = archive_files(ROOT / (A1042 + 'selected-replay.tar.gz'), 'slots/local/')
    receipt1042 = json.loads((ROOT / (A1042 + 'RESULT.json')).read_bytes())
    bound = {n.removeprefix('slots/local/'): h for n, h in receipt1042['artifacts'].items()
             if n.startswith('slots/local/')}
    require(len(bound) == 10 and {n: old.digest(b) for n, b in local.items()} == bound,
            'local input binding differs')
    archived = archive_files(ROOT / (A1094 + 'selected-replay.tar.gz'))
    require(archived['RESULT.json'] == (ROOT / (A1094 + 'RESULT.json')).read_bytes(),
            'selected result binding differs')
    for name in ('ASSEMBLY.json', 'REPLAY.json'):
        require(archived['candidate/strict/' + name] == (ROOT / (A1094 + name)).read_bytes(),
                'selected certificate/receipt binding differs')
    result = json.loads(archived['RESULT.json'])
    require(result['baseline_receipt_sha256'] == old.digest((ROOT / (A1042 + 'RESULT.json')).read_bytes())
            and result['assembly_sha256'] == old.digest(archived['candidate/strict/ASSEMBLY.json']),
            'selected lineage binding differs')
    files = {n.removeprefix('candidate/strict/'): b for n, b in archived.items()
             if n.startswith('candidate/strict/')}
    context = {'work': {'style': 'posix', 'path': REF_WORK},
               'local': {'style': 'posix', 'path': REF_LOCAL},
               'external': {'local-word': local['CANONICAL-WORD.json.gz'],
                            'local-replay': local['INDEPENDENT-LOCAL-REPLAY.json'],
                            'owners': (ROOT / OWNER).read_bytes()}}
    old.outer_log(archived['rare-pattern-exchanges.log'], files)
    return files, context, archived['rare-pattern-exchanges.log']


def encoded(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=True) + '\n').encode('ascii')


def mutate(files, name, operation):
    raw = files[name]
    value = json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw)
    operation(value)
    raw = encoded(value)
    if name.endswith('.gz'):
        raw = gzip.compress(raw, mtime=0)
    return dict(files, **{name: raw})


def relocated(files, original, work, local, style):
    """Independent exact fixture spelling oracle: explicit separators, not adapter joins."""
    context = {'work': {'style': style, 'path': work},
               'local': {'style': style, 'path': local}, 'external': original['external']}
    keymap = {}
    for role in old.POLICY['input_roles']:
        previous = original[role['root']]['path'] + '/' + role['suffix']
        prefix = context[role['root']]['path']
        keymap[previous] = (prefix + '\\' + role['suffix'].replace('/', '\\')
                            if style == 'windows-drive' else prefix + '/' + role['suffix'])
    updated = mutate(files, 'INDEPENDENT-T16.json', lambda v: v.__setitem__(
        'input_sha256', {keymap[k]: digest for k, digest in v['input_sha256'].items()}))
    return updated, context


def run():
    source_count = authenticate()
    reference, refctx, reference_log = fixture()
    positives, negatives = [], []

    def rejects(label, call):
        try:
            report = call()
        except (ValueError, TypeError, KeyError):
            negatives.append(label)
            return
        require(type(report) is dict and report.get('equivalent') is False,
                'negative control accepted: ' + label)
        negatives.append(label)

    def accepts(label, files, context, against=reference, leftctx=refctx):
        report = adapter.compare(against, files, leftctx, context)
        require(report['equivalent'] and report['checked_files'] == 105
                and report['authenticated_raw_edges_per_side'] == 30, 'positive rejected: ' + label)
        positives.append(label)

    accepts('unchanged-posix-reference', reference, refctx)
    win, winctx = relocated(reference, refctx, r'C:\proof runs\候補', r'D:\local inputs\供給', 'windows-drive')
    untyped = {**winctx, 'work': winctx['work']['path'], 'local': winctx['local']['path']}
    try:
        old.prepare(win, untyped)
    except ValueError as exc:
        require(str(exc) == 'root must be an absolute POSIX path', 'unexpected predecessor rejection')
        old_failure = str(exc)
    else:
        raise ValueError('pinned predecessor unexpectedly accepts Windows roots')
    accepts('windows-drive-japanese-spaces', win, winctx)
    posix, posctx = relocated(reference, refctx, '/tmp/literal\\backslash', '/tmp/local', 'posix')
    accepts('posix-literal-backslash-retained', posix, posctx)
    accepts('windows-identical-side-still-authenticated', win, winctx, win, winctx)
    if os.name == 'nt':
        for role in old.POLICY['input_roles']:
            require(str(Path(winctx[role['root']]['path']).joinpath(*role['suffix'].split('/')))
                    == adapter.role_path(winctx[role['root']], role['suffix']), 'native Windows spelling differs')

    keys = list(json.loads(win['INDEPENDENT-T16.json'])['input_sha256'])
    for key in keys:
        for label, op in (
            ('stale-digest', lambda v, key=key: v['input_sha256'].__setitem__(key, '0' * 64)),
            ('missing-role', lambda v, key=key: v['input_sha256'].pop(key)),
            ('separator-alias', lambda v, key=key: v['input_sha256'].__setitem__(key.replace('\\', '/'), v['input_sha256'].pop(key))),
            ('case-alias', lambda v, key=key: v['input_sha256'].__setitem__(key.lower(), v['input_sha256'].pop(key))),
        ):
            bad = mutate(win, 'INDEPENDENT-T16.json', op)
            rejects(label + ':' + key, lambda bad=bad: adapter.compare(reference, bad, refctx, winctx))
    digests = json.loads(win['INDEPENDENT-T16.json'])['input_sha256']
    require(len(set(digests.values())) == 6, 'swap controls require distinct role hashes')
    for first, second in itertools.combinations(keys, 2):
        def swap(v, first=first, second=second):
            d = v['input_sha256']; d[first], d[second] = d[second], d[first]
        bad = mutate(win, 'INDEPENDENT-T16.json', swap)
        rejects('role-swap:' + first + ':' + second,
                lambda bad=bad: adapter.compare(reference, bad, refctx, winctx))
    for name in sorted(win):
        bad = dict(win); del bad[name]
        rejects('missing-output:' + name, lambda bad=bad: adapter.compare(reference, bad, refctx, winctx))
    rejects('extra-output', lambda: adapter.compare(reference, dict(win, **{'EXTRA.json': b'{}'}), refctx, winctx))

    malformed = [r'C:relative', r'\rooted', 'C:/mixed', r'C:\double\\separator',
                 r'C:\dot\.\part', r'C:\parent\..\part', 'C:\\trailing\\',
                 r'C:\space ', r'C:\dot.', r'C:\CON', r'C:\name:stream',
                 r'\\server\share\work', r'\\?\C:\work', r'\\.\C:\work']
    for path in malformed:
        # Exercise root validation itself; unchanged receipt keys would reject
        # later as stale even if the canonical-root guard were accidentally lost.
        rejects('unsupported-root:' + path, lambda path=path: adapter.role_path(
            {'style': 'windows-drive', 'path': path}, 'CANONICAL-WORD.json.gz'))
    collision_ctx = {'work': {'style': 'windows-drive', 'path': r'C:\root'},
                     'local': {'style': 'windows-drive', 'path': r'c:\ROOT\STRICT\GLOBAL8\BASE\SPLIT-CENTRES'},
                     'external': refctx['external']}
    collision_keys = {}
    for role in old.POLICY['input_roles']:
        before = refctx[role['root']]['path'] + '/' + role['suffix']
        collision_keys[before] = collision_ctx[role['root']]['path'] + '\\' + role['suffix'].replace('/', '\\')
    collision = mutate(reference, 'INDEPENDENT-T16.json', lambda v: v.__setitem__(
        'input_sha256', {collision_keys[k]: digest for k, digest in v['input_sha256'].items()}))
    require(len(set(collision_keys.values())) == 6 and
            len({k.casefold() for k in collision_keys.values()}) == 5,
            'collision control must have six literal keys and five Windows identities')
    rejects('case-insensitive-role-collision', lambda: adapter.compare(reference, collision, refctx, collision_ctx))
    ctx = copy.deepcopy(winctx); ctx['work']['style'] = 'automatic'
    rejects('untyped-style', lambda: adapter.compare(reference, win, refctx, ctx))
    for name, op in (
        ('INDEPENDENT-T16.json', lambda v: v.__setitem__('live', True)),
        ('ASSEMBLY.json', lambda v: v.__setitem__('kappa', '1/2')),
        ('INDEPENDENT-T16.json', lambda v: v.__setitem__('unknown_path', r'C:\proof runs\候補')),
        ('INDEPENDENT-T16.json', lambda v: v['input_sha256'].__setitem__('work:fake', '0' * 64)),
        ('ADMISSION-CONTROLS.json', lambda v: v['input_sha256'].__setitem__('fresh_invoice', '0' * 64)),
        ('REPLAY.json', lambda v: v['stages'][0].__setitem__('log_sha256', '0' * 64)),
    ):
        bad = mutate(win, name, op)
        rejects('scientific-or-binding:' + name + ':' + str(len(negatives)),
                lambda bad=bad: adapter.compare(reference, bad, refctx, winctx))
    # Even path-like strings present on BOTH sides remain literal outside the six keys.
    left = mutate(reference, 'INDEPENDENT-T16.json', lambda v: v.__setitem__('note', REF_WORK + '/literal'))
    right = mutate(win, 'INDEPENDENT-T16.json', lambda v: v.__setitem__('note', winctx['work']['path'] + r'\literal'))
    rejects('unlisted-path-string-is-not-relocated', lambda: adapter.compare(left, right, refctx, winctx))
    bad = dict(win); bad['INDEPENDENT-T16.json'] = b'{"live":0,"live":1,' + win['INDEPENDENT-T16.json'].lstrip()[1:]
    rejects('duplicate-json-key', lambda: adapter.compare(reference, bad, refctx, winctx))
    # An identically corrupted pair must reject, not pass a byte-equality fast path.
    bad = mutate(win, 'INDEPENDENT-T16.json', lambda v: v['input_sha256'].__setitem__(keys[0], '0' * 64))
    rejects('identically-stale-native-roles', lambda: adapter.compare(bad, bad, winctx, winctx))

    # Composition with the predecessor's declared invoice and timing quotients.
    composed = dict(win)
    invoice = old.invoice.INVOICE
    composed[invoice] = encoded(json.loads(win[invoice]))
    require(composed[invoice] != win[invoice], 'invoice positive must change bytes')
    for name in old.invoice.CONSUMERS:
        composed = mutate(composed, name, lambda v: v['input_sha256'].__setitem__('fresh_invoice', old.digest(composed[invoice])))
    for name in ('REPLAY.json', 'STAGES.json'):
        def retime(v, name=name):
            for i, row in enumerate(v if name == 'STAGES.json' else v['stages']):
                row['seconds'] = 100 + i
        composed = mutate(composed, name, retime)
    accepts('windows-composed-invoice-and-22-times', composed, winctx)
    log = ('\n'.join(['PASS ' + n + ' ' + str(100 + i) for i, n in enumerate(old.STAGES)]
                     + reference_log.decode().splitlines()[11:]) + '\n').encode()
    require(old.outer_log(log, composed) == old.outer_log(reference_log, reference), 'composed outer log differs')
    positives.append('coupled-outer-log-retained')
    rejects('uncoupled-outer-log', lambda: old.outer_log(log.replace(b'100\n', b'101\n', 1), composed))
    for row in json.loads((HERE / 'SOURCES.json').read_bytes())['vendored_sources']:
        rejects('vendor-source-drift:' + row['path'], lambda row=row: adapter.check_bytes(
            (HERE / row['path']).read_bytes() + b'\0', row['sha256'], row['path']))
    return {'status': 'PASS_SELECTED_WINDOWS_ROLE_ADAPTER', 'source_inputs': source_count,
            'predecessor_rejection': old_failure, 'output_files': 105, 'roles': 6,
            'authenticated_edges_per_side': 30, 'fresh_supplier_run': False,
            'positive_controls': positives, 'negative_controls': negatives,
            'positive_count': len(positives), 'negative_count': len(negatives),
            'scope': 'Constructed Windows-drive/POSIX role relocation on authenticated reviewed outputs; no native supplier replay or new kappa.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    result = run()
    if args.write:
        (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2, ensure_ascii=True) + '\n', encoding='utf8', newline='\n')
    else:
        require(result == json.loads((HERE / 'RESULT.json').read_bytes()), 'deterministic result differs')
    print(result['status'], 'files=105 roles=6 positives=' + str(result['positive_count']),
          'negatives=' + str(result['negative_count']), 'no_supplier_run no_new_kappa')


if __name__ == '__main__':
    main()

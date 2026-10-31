"""Additional finite inventory controls; run only through admitted parent guard.

Instrumentation deliberately wraps fixed trusted sha/Path.read_bytes bindings.
It is a fixture for operation counts, not production callback-domain support.
"""
import hashlib
from pathlib import Path
import shutil
import stat


ORDER = (
    'counts-valid', 'counts-list-pins', 'counts-wrong-digest-prefix',
    'malformed-pin-before-sha', 'nonlist-pin-not-coerced',
    'sorted-first-failure', 'empty-pin-undeclared-before-read',
    'incomplete-after-traversal', 'counts-nonexact-extra', 'fresh-copy',
    'copy-byte-mutation', 'source-still-valid-after-copy-mutation',
    'fresh-mode-change-and-boundary-rejection', 'fresh-byte-mutation',
    'fresh-repin-current-bytes', 'fresh-restored',
)


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def typed(value):
    """Ordered exact primitive representation, independent from target helpers."""
    kind = type(value)
    if kind is dict:
        return ['dict', [[typed(key), typed(item)] for key, item in value.items()]]
    if kind is list or kind is tuple:
        return [kind.__name__, [typed(item) for item in value]]
    if kind in (str, int, bool, type(None)):
        return [kind.__name__, value]
    raise TypeError('Unsupported control value: ' + kind.__name__)


def observe(module, root, pins, exact=True):
    """Count actual reads/hash bytes while retaining exact outcomes; serial only."""
    original_sha, original_read = module.sha, Path.read_bytes
    hashes, reads = [], []

    def counted_sha(raw):
        hashes.append(len(raw))
        return original_sha(raw)

    def counted_read(path):
        raw = original_read(path)
        reads.append([str(path.relative_to(root)), len(raw)])
        return raw

    module.sha, Path.read_bytes = counted_sha, counted_read
    try:
        try:
            outcome = ('value', module.inventory(root, pins, exact=exact))
        except Exception as error:
            outcome = ('error', type(error), str(error))
    finally:
        module.sha, Path.read_bytes = original_sha, original_read
    need(module.sha is original_sha and Path.read_bytes is original_read,
         'Control instrumentation did not restore original bindings')
    return outcome, {'hash_calls': len(hashes), 'hash_bytes': sum(hashes),
                     'hash_lengths': hashes, 'reads': reads,
                     'read_calls': len(reads), 'read_bytes': sum(row[1] for row in reads)}


def outcome_typed(outcome):
    if outcome[0] == 'error':
        return ['error', outcome[1].__module__, outcome[1].__qualname__, outcome[2]]
    return ['value', typed(outcome[1])]


def run_controls(reference, candidate, scratch):
    scratch = Path(scratch)
    need(not scratch.exists(), 'Fresh digest fixture directory required')
    root = scratch / 'root'
    root.mkdir(parents=True)
    (root / 'nested').mkdir()
    payloads = {'alpha.txt': b'alpha\n', 'nested/beta.bin': b'\x00\xff\x7f'}
    for name, raw in payloads.items():
        (root / name).write_bytes(raw)
        (root / name).chmod(0o644)
    pins = {name: hashlib.sha256(raw).hexdigest() for name, raw in payloads.items()}
    expected = {name: {'sha256': pins[name], 'mode': 0o644, 'bytes': len(raw)}
                for name, raw in payloads.items()}
    rows = []

    def pair(tag, selected=pins, selected_root=root, exact=True, expected_value=None,
             error=None, reads=(6, 3), ref_hashes=(6, 6, 3, 3), cand_hashes=(6, 3)):
        left, left_counts = observe(reference, selected_root, selected, exact)
        right, right_counts = observe(candidate, selected_root, selected, exact)
        need(outcome_typed(left) == outcome_typed(right), 'Typed outcome differs: ' + tag)
        for label, counts, hash_lengths in (
                ('reference', left_counts, ref_hashes), ('candidate', right_counts, cand_hashes)):
            need(counts['hash_lengths'] == list(hash_lengths), 'Hash order/count differs: ' + tag + ':' + label)
            need([row[1] for row in counts['reads']] == list(reads), 'Read order/count differs: ' + tag + ':' + label)
            need([row[0] for row in counts['reads']] == list(payloads)[:len(reads)],
                 'Read pathname order differs: ' + tag + ':' + label)
        if error is not None:
            need(left[0] == 'error' and left[1] is error[0] and left[2] == error[1],
                 'Exact error differs: ' + tag)
        else:
            need(left[0] == 'value' and typed(left[1]) == typed(expected_value),
                 'Independent exact result differs: ' + tag)
        rows.append({'case': tag, 'outcome': outcome_typed(left),
                     'reference': left_counts, 'candidate': right_counts})
        return left

    pair('counts-valid', expected_value=expected)
    pair('counts-list-pins', {name: [digest, 0o644] for name, digest in pins.items()}, expected_value=expected)
    wrong = dict(pins, **{'alpha.txt': '0' * 64})
    prefix_error = (RuntimeError, 'Frozen input digest changed: alpha.txt')
    pair('counts-wrong-digest-prefix', wrong, error=prefix_error, reads=(6,), ref_hashes=(6,), cand_hashes=(6,))
    malformed = dict(pins, **{'alpha.txt': []})
    pair('malformed-pin-before-sha', malformed, error=(IndexError, 'list index out of range'),
         reads=(6,), ref_hashes=(), cand_hashes=())
    tuple_pin = dict(pins, **{'alpha.txt': (pins['alpha.txt'], 0o644)})
    pair('nonlist-pin-not-coerced', tuple_pin, error=prefix_error, reads=(6,), ref_hashes=(6,), cand_hashes=(6,))
    both_bad = {name: '0' * 64 for name in reversed(pins)}
    pair('sorted-first-failure', both_bad, error=prefix_error, reads=(6,), ref_hashes=(6,), cand_hashes=(6,))
    pair('empty-pin-undeclared-before-read', {}, error=(RuntimeError, 'Undeclared frozen input: alpha.txt'),
         reads=(), ref_hashes=(), cand_hashes=())
    missing = dict(pins, missing='1' * 64)
    pair('incomplete-after-traversal', missing, error=(RuntimeError, 'Frozen input inventory incomplete'))
    (root / 'extra').write_bytes(b'ignored')
    pair('counts-nonexact-extra', exact=False, expected_value=expected)
    (root / 'extra').unlink()
    copied = scratch / 'copied'
    shutil.copytree(root, copied)
    pair('fresh-copy', selected_root=copied, expected_value=expected)
    (copied / 'alpha.txt').write_bytes(b'changed')
    pair('copy-byte-mutation', selected_root=copied, error=prefix_error,
         reads=(7,), ref_hashes=(7,), cand_hashes=(7,))
    pair('source-still-valid-after-copy-mutation', expected_value=expected)
    (root / 'alpha.txt').chmod(0o600)
    mode_expected = {name: dict(info) for name, info in expected.items()}
    mode_expected['alpha.txt']['mode'] = 0o600
    changed = pair('fresh-mode-change-and-boundary-rejection', expected_value=mode_expected)
    # This reproduces the original caller's independent before/after equality.
    try:
        need(changed[1] == expected, 'Immutable source bytes/modes changed')
    except RuntimeError as error:
        need(str(error) == 'Immutable source bytes/modes changed', 'Boundary error changed')
    else:
        raise RuntimeError('Boundary comparison accepted returned mode drift')
    (root / 'alpha.txt').chmod(0o644)
    (root / 'alpha.txt').write_bytes(b'changed')
    pair('fresh-byte-mutation', error=prefix_error, reads=(7,), ref_hashes=(7,), cand_hashes=(7,))
    repinned = dict(pins, **{'alpha.txt': hashlib.sha256(b'changed').hexdigest()})
    current_expected = {name: dict(info) for name, info in expected.items()}
    current_expected['alpha.txt'].update(sha256=repinned['alpha.txt'], bytes=7)
    pair('fresh-repin-current-bytes', repinned, expected_value=current_expected,
         reads=(7, 3), ref_hashes=(7, 7, 3, 3), cand_hashes=(7, 3))
    (root / 'alpha.txt').write_bytes(payloads['alpha.txt'])
    pair('fresh-restored', expected_value=expected)
    need([row['case'] for row in rows] == list(ORDER), 'Additional control order changed')
    return {'status': 'DIGEST_COUNT_FRESHNESS_TYPED_CONTROLS_PASS', 'cases': rows,
            'case_count': len(rows), 'production_instrumentation': False,
            'scope': 'Finite trusted inventory inputs; no arbitrary callback or concurrent mutation equivalence'}

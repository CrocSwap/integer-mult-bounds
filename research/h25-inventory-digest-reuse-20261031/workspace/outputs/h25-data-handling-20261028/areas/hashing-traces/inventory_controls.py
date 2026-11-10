"""Actual original/candidate inventory-function controls for the parent queue."""
import hashlib
from pathlib import Path


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def capture(function, root, pins, exact=True):
    try:
        value = function(root, pins, exact=exact)
    except Exception as error:
        return ('error', type(error).__name__, str(error))
    return ('value', value)


def run_controls(reference_inventory, candidate_inventory, scratch):
    """Supply authenticated functions from independent original/new drivers."""
    scratch = Path(scratch)
    need(not scratch.exists(), 'Fresh inventory fixture directory required')
    root = scratch / 'root'
    root.mkdir(parents=True)
    (root / 'nested').mkdir()
    payloads = {'alpha.txt': b'alpha\n', 'nested/beta.bin': b'\x00\xff\x7f'}
    for name, raw in payloads.items():
        (root / name).write_bytes(raw)
        (root / name).chmod(0o644)
    pins = {name: hashlib.sha256(raw).hexdigest() for name, raw in payloads.items()}
    results = []

    def compare(tag, selected=pins, exact=True, selected_root=root):
        original = capture(reference_inventory, selected_root, selected, exact)
        candidate = capture(candidate_inventory, selected_root, selected, exact)
        need(original == candidate, 'Inventory behavior differs: ' + tag)
        results.append((tag, original[0]))
        return original

    initial = compare('valid')
    need(initial[0] == 'value', 'Initial inventory unexpectedly rejected')
    compare('list-pins', {name: [digest, 0o644] for name, digest in pins.items()})
    wrong = dict(pins)
    wrong['alpha.txt'] = '0' * 64
    need(compare('wrong-digest', wrong)[0] == 'error', 'Wrong digest accepted')
    missing = dict(pins)
    missing['missing'] = '1' * 64
    need(compare('missing', missing)[0] == 'error', 'Missing input accepted')
    (root / 'extra').write_bytes(b'extra')
    need(compare('extra')[0] == 'error', 'Exact extra file accepted')
    need(compare('extra-nonexact', exact=False)[0] == 'value', 'Nonexact census changed')
    (root / 'extra').unlink()
    link = root / 'link'
    link.symlink_to('alpha.txt')
    need(compare('symlink')[0] == 'error', 'Input symlink accepted')
    link.unlink()
    root_link = scratch / 'root-link'
    root_link.symlink_to(root, target_is_directory=True)
    need(compare('root-symlink', selected_root=root_link)[0] == 'error', 'Root symlink accepted')
    root_link.unlink()
    (root / 'alpha.txt').chmod(0o600)
    changed_mode = compare('changed-mode')
    need(changed_mode[0] == 'value' and changed_mode != initial, 'Mode drift vanished from inventory')
    (root / 'alpha.txt').chmod(0o644)
    (root / 'alpha.txt').write_bytes(b'changed')
    need(compare('fresh-call-after-mutation')[0] == 'error', 'Cross-call byte mutation accepted')
    (root / 'alpha.txt').write_bytes(payloads['alpha.txt'])
    need(compare('restored') == initial, 'Restored inventory differs')
    return {'status': 'INVENTORY_DIFFERENTIAL_CONTROLS_PASS', 'cases': results,
            'mode_drift_is_returned_for_boundary_comparison': True,
            'publication_wrapper_independent_manifest_controls_still_required': True}

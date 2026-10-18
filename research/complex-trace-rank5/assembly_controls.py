"""Admission-gate negative controls for the exact two-supplier assembly.

Prepared with OpenAI Codex assistance; Apache-2.0. These use the fresh owner
and invoice receipts, never repeat the physical replay or change its artifacts.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path

from assemble import assemble

assert __debug__, 'Assertions required'
P = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
digest = lambda x: hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def verify(owner_path, invoice_path):
    owner = json.loads(owner_path.read_text())
    invoice = json.loads(invoice_path.read_text())
    baseline = assemble(owner, invoice, sha(owner_path), sha(invoice_path))

    def empty_maps(o, i):
        i['strict_checks'] = {}
        i['local'] = {}

    def missing_backward(o, i):
        del i['local']['backward']

    def failed_status_zero_sweeps(o, i):
        i['status'] = 'FAIL'
        i['complete_invocation_sweeps'] = i['bridge_sweeps'] = 0

    def understated_stock(o, i):
        # Keep the two receipts mutually consistent, but remove a required role.
        o['physical'] -= 1
        i['physical'] -= 1
        i['physical_stock_identity']['coefficient_work'] -= 1

    def changed_profile(o, i):
        # Keep the rank mass and deficit unchanged; pricing must bind the word.
        o['paid_profile']['1'] += 2
        o['paid_profile']['2'] -= 1

    controls = [
        ('empty_certification_maps', empty_maps),
        ('missing_backward_orientation', missing_backward),
        ('failed_status_zero_sweeps', failed_status_zero_sweeps),
        ('nonboolean_precision_check', lambda o, i: i['strict_checks'].__setitem__('precision', 'true')),
        ('wrong_owner_role_count', lambda o, i: o.__setitem__('actual_helper_owner_charts', 36287)),
        ('understated_physical_stock', understated_stock),
        ('changed_profile_same_rank_mass', changed_profile),
        ('insufficient_finite_C0', lambda o, i: i['finite'].__setitem__('required_C0_bits', 210001)),
        ('unpaid_scalar_primitive', lambda o, i: i['local']['forward'].__setitem__('real_component_primitives', 168228)),
        ('wrong_local_artifact_binding', lambda o, i: i.__setitem__('local_programs_sha256', '0' * 64)),
        ('false_dirty_restoration', lambda o, i: i['local']['backward'].__setitem__('all_dirty_helper_columns_restored', False)),
        ('missing_finite_check', lambda o, i: i['strict_checks'].pop('halving')),
    ]
    rejected = []
    for name, mutate in controls:
        o, i = copy.deepcopy(owner), copy.deepcopy(invoice)
        mutate(o, i)
        # Rebind each mutated owner to its mutated invoice so tests of roles and
        # profiles cannot pass merely by tripping an unrelated stale-file hash.
        oh = digest(o)
        i['owner_audit_sha256'] = oh
        try:
            assemble(o, i, oh, digest(i))
        except (AssertionError, KeyError):
            rejected.append(name)
        else:
            raise AssertionError('Invalid admission receipt accepted: ' + name)
    try:
        assemble(owner, invoice, '0' * 64, sha(invoice_path))
    except AssertionError:
        rejected.append('wrong_owner_receipt_hash')
    else:
        raise AssertionError('Wrong owner digest accepted')
    assert len(rejected) == 13
    assert baseline['controls'] == ['next_grid', 'zero_eta', 'zero_beta', 'unit_beta']
    return dict(
        status='PASS_EXACT_ASSEMBLY_ADMISSION_NEGATIVE_CONTROLS',
        valid_receipt_kappa=baseline['kappa'],
        input_sha256=baseline['input_sha256'],
        assembler_sha256=sha(P / 'assemble.py'),
        rejected_controls=rejected,
        exact_outer_controls=baseline['controls'],
        scope='Mutation controls for receipt completeness, both orientations, literal work/stock, profile and hash binding. Does not replace the fresh physical replay.',
    )


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--owner', type=Path, required=True)
    ap.add_argument('--invoice', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    assert not a.out.exists()
    result = verify(a.owner, a.invoice)
    a.out.write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'], len(result['rejected_controls']))

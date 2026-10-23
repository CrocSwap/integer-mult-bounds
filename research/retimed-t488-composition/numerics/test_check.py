# SPDX-License-Identifier: Apache-2.0
"""Meaningful rejection controls for bounded arithmetic and source binding."""
from pathlib import Path
import argparse, importlib.util, json, shutil, tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('retimed_t488_check', HERE / 'check.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    data = m.derive_inputs()
    profile = data['derived']
    controls = []
    def reject(name, action):
        try:
            action()
        except ValueError as exc:
            controls.append({'name': name, 'status': 'REJECTED', 'reason': str(exc)})
        else:
            raise AssertionError('bad candidate accepted: ' + name)
    reject('unretimed_complete_profile', lambda: m.check(data['old']))
    missing_idle = dict(profile); del missing_idle[48]
    reject('omitted_nonlocal_rank48_idle_calls', lambda: m.check(missing_idle))
    same_mass = dict(profile); same_mass[1] -= 2; same_mass[2] += 1
    assert sum(r*n for r,n in same_mass.items()) == sum(r*n for r,n in profile.items())
    reject('mass_preserving_wrong_histogram', lambda: m.check(same_mass))
    wrong_calls = {r: data['old'].get(r,0) + 4770*data['delta'].get(r,0)
                   for r in data['old'].keys() | data['delta'].keys()}
    reject('wrong_T530_call_multiplicity', lambda: m.check(wrong_calls))
    negative = dict(profile); negative[48] = -1
    reject('negative_count', lambda: m.check(negative))
    decimal = dict(profile); decimal[1] = float(decimal[1])
    reject('floating_count', lambda: m.check(decimal))
    boolean = dict(profile); boolean[1] = True
    reject('boolean_count', lambda: m.check(boolean))
    duplicate = dict(profile); duplicate['1'] = duplicate[1]
    reject('duplicate_integer_string_rank', lambda: m.check(duplicate))
    wrong_parent = dict(profile); wrong_parent[73] = 1
    reject('paid_rank_equals_parent', lambda: m.check(wrong_parent))
    original_lower, original_upper = m.ROOT_LOWER, m.ROOT_UPPER
    try:
        m.ROOT_LOWER = original_upper
        m.ROOT_UPPER = original_upper + m.Q(1,10**24)
        reject('next_grid_endpoint_claimed_feasible', lambda: m.check(profile))
    finally:
        m.ROOT_LOWER, m.ROOT_UPPER = original_lower, original_upper
    # Corrupt one authenticated source in an isolated test copy. Never edit inputs.
    scratch = Path(tempfile.mkdtemp(prefix='tampered-input-control-', dir=args.out.parent))
    shutil.copytree(HERE/'inputs',scratch/'inputs')
    shutil.copytree(HERE/'vendor',scratch/'vendor')
    shutil.copy2(HERE/'PROVENANCE.json',scratch/'PROVENANCE.json')
    claim = scratch/'inputs/PR3642-CLAIM.json'
    raw = json.loads(claim.read_text());raw['kappa'] = '0';claim.write_text(json.dumps(raw))
    try:
        m.HERE = scratch
        reject('comparator_claim_byte_mutation',lambda:m.check(profile))
    finally:
        m.HERE = HERE
        shutil.rmtree(scratch)
    receipt = m.check(profile)
    result = {'status':'PASS_VALID_PROFILE_AND_ELEVEN_REJECTION_CONTROLS',
              'positive_status':receipt['status'], 'controls':controls,
              'source_provenance_sha256':m.sha(HERE/'PROVENANCE.json'),
              'scope':m.SCOPE}
    assert len(controls)==11
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'])

if __name__=='__main__':main()

# SPDX-License-Identifier: Apache-2.0
"""Fresh bounded modern outer arithmetic using unchanged authenticated engines."""
from pathlib import Path
from fractions import Fraction as Q
import hashlib, importlib.util, json, os, subprocess, sys
HERE = Path(__file__).resolve().parent

def check_outer(moment, out):
    """Run the two outer engines into a fresh directory and return their receipt.

    moment must be a receipt freshly returned by check.check(profile). The caller
    runs profile arithmetic first. All inherited outer hypotheses remain assumed.
    """
    spec=importlib.util.spec_from_file_location('retimed_input_checker',HERE/'check.py')
    checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    checker.authenticate()
    if moment['status']!='PASS_SOURCE_BOUND_TWO_ENGINE_RETIMED_T488_ARITHMETIC':
        raise ValueError('successful arithmetic receipt required')
    if moment['source_provenance_sha256']!=checker.sha(HERE/'PROVENANCE.json'):
        raise ValueError('moment provenance mismatch')
    verified = checker.check(moment['new_profile'])
    for field in ('root_interval', 'conditional_modern_kappa', 'authenticated_PR3642_modern_kappa', 'live', 'replicas'):
        if moment[field] != verified[field]:
            raise ValueError('outer input differs from freshly checked moment: ' + field)
    out=Path(out)
    if out.exists():raise ValueError('fresh outer output directory required')
    out.mkdir(parents=True);(out/'outer').mkdir();(out/'new').mkdir()
    C=Q(moment['root_interval'][0]);K=Q(moment['conditional_modern_kappa']);prior=Q(moment['authenticated_PR3642_modern_kappa'])
    if K!=C-Q(1,10**46)-Q(1,10**70) or K<=prior:
        raise ValueError('candidate transfer expression or comparator mismatch')
    def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
    save(out/'new/SPEC.json',dict(geometry=dict(dimension=73,replicas=moment['replicas']),
         expected=dict(complex_lower=str(C),kappa=str(prior),global_profile=moment['new_profile'],live=moment['live']),
         outer_refinement=dict(endpoint_digits=24)))
    save(out/'CLAIM.json',dict(kappa=str(K),scope=checker.SCOPE))
    save(out/'outer/B.json',dict(b=str(C-Q(1,10**104)),b_above_endpoint=moment['root_interval'][1],profile=moment['new_profile'],live=moment['live']))
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0')
    for name in ('check_ledger.py','independent_check.py'):
        raw=(HERE/'vendor'/name).read_bytes();(out/'outer'/name).write_bytes(raw)
        with (out/(name+'.log')).open('w') as f:
            subprocess.run([sys.executable,'-B',str((out/'outer'/name).resolve())],env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
    ledger=json.loads((out/'outer/LEDGER.json').read_bytes());row=ledger['rows']['struct_boundary_radix_union'];controls=ledger['rejecting_controls']['struct_boundary_radix_union']
    if Q(row['kappa']['rational'])!=K:raise ValueError('ledger does not derive candidate kappa')
    checks=row['strict_checks']
    if len(checks)!=63 or not all(Q(x['rational'])>0 for x in checks.values()):raise ValueError('63 positive outer inequalities required')
    if len(controls)!=17 or not all(x and all(Q(v['rational'])<=0 for v in x.values())for x in controls.values()):raise ValueError('17 original outer rejecting controls required')
    independent=json.loads((out/'outer/INDEPENDENT.json').read_bytes())
    if Q(independent['rows']['struct_boundary_radix_union']['kappa'])!=K:raise ValueError('independent outer kappa mismatch')
    result=dict(status='PASS_SOURCE_BOUND_RETIMED_T488_MODERN_OUTER_ARITHMETIC',kappa=str(K),kappa_decimal=checker.dec(K),
                strict_inequalities=63,rejected_controls=17,independent_status=independent['status'],
                exact_strict_margins=checks,exact_rejection_margins=controls,
                ledger_sha256=checker.sha(out/'outer/LEDGER.json'),independent_sha256=checker.sha(out/'outer/INDEPENDENT.json'),
                checker_sha256=checker.sha(HERE/'vendor/check_ledger.py'),independent_checker_sha256=checker.sha(HERE/'vendor/independent_check.py'),
                scope='Source-bound exact modern outer arithmetic only. All inherited analytic and supplier hypotheses remain conditional; no native/controller/full scientific admission is run or inferred.')
    save(out/'RESULT.json',result)
    return result

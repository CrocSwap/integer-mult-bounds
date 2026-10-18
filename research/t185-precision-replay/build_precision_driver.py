#!/usr/bin/env python3
"""Generate an explicitly parameterized derivative of PR2863's admission driver.

Only a fresh output directory is written. Frozen source and cache inputs remain
unchanged. Source hashes and each single exact preimage are required. No retained
mathematical predicate is deleted; the discovery generator adds a fine endpoint
that the original coarse and both original fine moment checkers must certify.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

DRIVER_SHA='1d4b8b9df01e42f5f2450b5837132861c5aa8cd3a011e6a6fa35e53463417346'
HELPER_SHA='1039fddb7fd63e5bd0f8aca53494a64c7eb5814fbf2b584ca24cd64e2125755a'
BASELINE_HEAD='34328b1d5e5bebac62d5cabec993dfbfd7b2123f'
BASELINE_SHA='eebaf5fc6d4721ba99418bdd0bbcbb933c5bf4f351025065f39a11120680f0f9'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--package',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--digits',type=int,default=40)
    a=ap.parse_args()
    assert __debug__ and 26<=a.digits<=70
    package=a.package.resolve();out=a.out.resolve()
    driver=package/'tools/admit2857.py';helper=Path(__file__).with_name('endpoint_refiner.py')
    baseline=package/'CLAIM.json'
    assert sha(driver)==DRIVER_SHA and sha(helper)==HELPER_SHA and sha(baseline)==BASELINE_SHA
    claim=json.loads(baseline.read_text())
    assert claim['display']=='0.001720100805416885927944 - 10^-46 - 10^-70'
    assert not out.exists() and not out.is_relative_to(package)
    original=driver.read_text();body=original;changes=[]
    def replace(old,new,why):
        nonlocal body
        assert body.count(old)==1,(why,body.count(old))
        body=body.replace(old,new)
        changes.append(dict(preimage=old,replacement=new,reason=why))
    replace('PRECISION = dict(endpoint_digits=24, grid_digits=18, margin_digits=28, bootstrap_steps=12)',
            f'PRECISION = dict(endpoint_digits={a.digits}, grid_digits=18, margin_digits=28, bootstrap_steps=12)',
            'Only the supplier bracket precision changes; ordinary bootstrap grid, margins and depth remain intact.')
    entry=f"    'pr2863': dict(pr=2863, head='{BASELINE_HEAD}', sha256='{sha(baseline)}', field='kappa'),\n"
    replace('COMPARISONS = {\n','COMPARISONS = {\n'+entry,'Bind exact comparison to the frozen full PR2863 headline, not an older supplier.')
    old="    external_hashes = {str(p): sha(p) for p in helper_paths + [a.fill.resolve(), a.order.resolve(), a.dispatch.resolve(), a.comparison_claim.resolve(), a.blocknorm_checker.resolve()]}"
    new=f"    precision_helper = Path(__file__).with_name('endpoint_refiner.py')\n    need(sha(precision_helper) == '{HELPER_SHA}', 'exact precision generator source')\n"+old.replace('helper_paths + [','helper_paths + [precision_helper, ')
    replace(old,new,'Authenticate the new discovery-only helper as an external input before and after complete admission.')
    old_discovery=" if DISCOVER:b=Q(M.certify(H,73,owner['live'],False)['lower']);conservative_b=Q(M.certify(H,73,owner['live'],True)['lower'])"
    new_discovery=" if DISCOVER:\n  from endpoint_refiner import refine as _precision_refine\n  _coarse_b=Q(M.certify(H,73,owner['live'],False)['lower']);_coarse_conservative=Q(M.certify(H,73,owner['live'],True)['lower'])\n  b=_precision_refine(H,73,owner['live'],_coarse_b,False,SPEC['outer_refinement']['endpoint_digits'])\n  conservative_b=_precision_refine(H,73,owner['live'],_coarse_conservative,True,SPEC['outer_refinement']['endpoint_digits'])"
    addition="    # New discovery input only: retained coarse and BOTH fine checkers below\n    # still certify both native and conservative endpoints in strict admission.\n    shutil.copy2(precision_helper, package / 'code/endpoint_refiner.py')\n    need(sha(package / 'code/endpoint_refiner.py') == external_hashes[str(precision_helper)], 'precision helper copied exactly')\n    patch('code/assemble.py', [("+repr(old_discovery)+", "+repr(new_discovery)+")])\n\n"
    replace("    # PR2530's already checked correction:",addition+"    # PR2530's already checked correction:",'Derive both fine endpoints from their already-certified coarse brackets; all subsequent moment, admission and control predicates are unchanged.')
    replace("    write(package / 'outer/B.json', dict(b=str(C-Q(1,10**104)), b_above_endpoint=str(C+Q(1,10**24)),",
            "    DIG = PRECISION['endpoint_digits']\n    write(package / 'outer/B.json', dict(b=str(C-Q(1,10**(DIG+80))), b_above_endpoint=str(C+Q(1,10**DIG)),",
            'The same strict free gap and upper rejection endpoint are derived from the declared bracket precision.')
    replace('kappa == C-Q(1,10**70)-Q(1,10**46) and kappa > previous',
            'kappa == C-Q(1,10**(DIG+46))-Q(1,10**(DIG+22)) and kappa > previous',
            'Preserve exact fixed-grid-maximum equality with the unchanged ledger formulas at DIG; retain strict pinned-baseline improvement.')
    replace("b='certified complex_lower - 1e-104 (outer/B.json)'",
            "b=f'certified complex_lower - 1e-{DIG+80} (outer/B.json)'",'Update provenance text to the actual derived free gap.')
    replace("retuned_slacks='Endpoint precision24; free gaps follow outer/check_ledger.py from the frozen SPEC.'",
            "retuned_slacks=f'Endpoint precision{DIG}; free gaps follow outer/check_ledger.py from the frozen SPEC.'",'Keep explanation synchronized with parameters.')
    replace("fixed_grid_maximum='kappa=C-10^-70-10^-46 exactly; same fixed-grid-maximum proof at precision24.'",
            "fixed_grid_maximum=f'kappa=C-10^-{DIG+46}-10^-{DIG+22} exactly; same fixed-grid-maximum proof at precision{DIG}.'",'Keep exact claimed formula synchronized with parameters.')
    ast.parse(body)
    # Core gates must survive verbatim. Parameterized equality above is separately
    # pinned in the semantic diff and derives from unchanged outer ledger formulas.
    retained=["run('release', package / 'verify_release.py'", "receipt['status'] == 'PASS_RELEASE'", "receipt['manifest_sha256'] == sha(package / 'MANIFEST.json')", "tree(source, ('MANIFEST.json',)) == source_files", "tree(cache) == native_receipt['cache_files']", "run('discovery', runtime / 'replay.py'", "for name in ('check_ledger.py', 'independent_check.py'):"]
    assert all(x in original and x in body for x in retained)
    out.mkdir(parents=True)
    target=out/'admit_precision.py';target.write_text(body)
    shutil.copyfile(helper,out/'endpoint_refiner.py')
    (out/'driver.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),body.splitlines(True),fromfile='PR2863/tools/admit2857.py',tofile='admit_precision.py')))
    receipt=dict(status='GENERATED_NOT_EXECUTED',baseline_head=BASELINE_HEAD,baseline_claim_sha256=sha(baseline),digits=a.digits,source_driver_sha256=sha(driver),generated_driver_sha256=sha(target),endpoint_helper_sha256=sha(helper),changes=changes,retained_gates=retained,scope='Parameter-only derivative. Run only after repaired pinned baseline completes. A complete strict release, independent result comparison, source/manifest checks and current frontier refresh remain mandatory. No native circuit, fill, profile, invoice or verifier predicate is relaxed.')
    (out/'DERIVATION.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:receipt[k] for k in ('status','digits','generated_driver_sha256','baseline_claim_sha256')}))

if __name__=='__main__':main()

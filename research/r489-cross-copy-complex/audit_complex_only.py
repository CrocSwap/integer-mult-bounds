"""Independent audit of the cross-copy hosted complex template (no code shared with the generator).
usage: audit_complex_only.py UPSTREAM442_CHANGED COMPLEX_DIR OUT.json"""
import copy, gzip, hashlib, json, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_split import audit_complex
def main():
    chg, cd, outp = map(Path, sys.argv[1:4]); tpl = lambda p: json.loads(gzip.decompress(Path(p).read_bytes()))
    pct = tpl(chg / 'split-centres/GLOBAL-TEMPLATE.json.gz'); ct = tpl(cd / 'GLOBAL-TEMPLATE.json.gz'); ch = json.loads((cd / 'HOSTED.json').read_text())
    assert hashlib.sha256(gzip.decompress((cd / 'GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest() == ch['template_sha256']
    lc = json.loads((chg / 'split-centres/LOCAL-CHECKS.json').read_text())
    cp, chh, cs = audit_complex(ct, pct, lc); assert cp == Counter({int(k): v for k, v in ch['global_profile'].items()})
    controls = []
    def reject(name, fn):
        q = copy.deepcopy(ct); fn(q)
        try: audit_complex(q, pct, lc)
        except (AssertionError, KeyError, IndexError, StopIteration, ValueError, TypeError): controls.append(name)
        else: raise AssertionError('mutation accepted: ' + name)
    def first_split(q): return next(pc for pc in q['hosting']['pieces'] if len(pc[3]) == 2)
    def outside(q):
        pc = q['hosting']['pieces'][0]; pc[0] = next(s for s in range(9) if s not in q['hosting']['windows'][str(pc[2])][2])
    reject('complex: hosted residual outside its window', outside)
    reject('complex: split piece widths do not sum to nine', lambda q: first_split(q)[3][0].__setitem__(2, first_split(q)[3][0][2] + 1))
    reject('complex: split pieces on two different children', lambda q: first_split(q).__setitem__(2, (first_split(q)[2] + 1) % 20))
    reject('complex: remainder child understated', lambda q: q['idle_children'][0].__setitem__('rank', q['idle_children'][0]['rank'] - 1))
    reject('complex: dropped bank', lambda q: q.__setitem__('live', q['live'] - 1))
    reject('complex: duplicated hosted residual', lambda q: q['hosting']['pieces'].append(list(q['hosting']['pieces'][0])))
    reject('complex: changed local program', lambda q: q['local_programs']['forward'].pop())
    res = dict(status='PASS_INDEPENDENT_CROSS_COPY_COMPLEX_AUDIT', complex_template_sha256=ch['template_sha256'],
               complex_profile={str(k): v for k, v in sorted(cp.items())}, complex_live=ct['live'], complex_hosted_residuals=chh,
               complex_split_residuals=cs, complex_maxchild=max(cp), mutations_rejected=controls)
    outp.write_text(json.dumps(res, indent=2) + '\n'); print(json.dumps({k: v for k, v in res.items() if 'profile' not in k}))
if __name__ == '__main__': main()

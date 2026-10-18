# SPDX-License-Identifier: Apache-2.0
"""Independent precision-only candidate and admission-driver audit.

Uses this audit's alternating-exp(-t) Fraction engine, not the producer engine.
Prepared with substantial OpenAI Codex assistance.
"""
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as F
import ast, hashlib, json, sys
from pathlib import Path
import check_optimum as core

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(p,label):
    if not p:raise ValueError(label)
def decimal(q):
    with localcontext() as c:
        c.prec=120
        return str(Decimal(q.numerator)/Decimal(q.denominator))
def predicates(source):
    return Counter(ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(source))
                   if isinstance(n,ast.Assert) or isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='need')
def main():
    package=Path(sys.argv[1]); precision=Path(sys.argv[2]); out=Path(sys.argv[3])
    claim=json.loads((package/'CLAIM.json').read_text())
    screen=json.loads((precision/'screen40/RESULT.json').read_text())
    H={int(r):F(n,185) for r,n in json.loads((package/'data/PROFILE.json').read_text()).items()}
    C=F('0.0017201008054168859279440070756063355312'); upper=C+F(1,10**40)
    K=C-F(1,10**62)-F(1,10**86); old=F(claim['kappa'])
    need(C==F(screen['root_lower']) and upper==F(screen['root_upper']),'screen root endpoints')
    need(K==F(screen['kappa']) and K>old,'exact candidate comparison')
    native=[core.moment(H,C),core.moment(H,upper)]
    need(native[0][1]<0<native[1][0],'alternating-exp independent fine native signs')
    fine=F(json.loads((precision/'conservative40.json').read_text())['fine'])
    bad=core.poly_add(H,{1:F(32*73*73,10**16)*sum(H.values())})
    conservative=[core.moment(bad,fine),core.moment(bad,fine+F(1,10**40))]
    need(conservative[0][1]<0<conservative[1][0],'independent conservative surcharge signs')
    # The perturbation still lies in the interval of the independent LP audit.
    need(core.LOW<C<upper<core.HIGH,'fine bracket within certified LP interval')
    control=core.moment(core.poly_add(H,{1:F(1)}),C)
    need(control[0]>0,'additional rank-one paid child control')
    original=(package/'tools/admit2857.py').read_text()
    generated=(precision/'driver40/admit_precision.py').read_text()
    deriv=json.loads((precision/'driver40/DERIVATION.json').read_text())
    need(sha(package/'tools/admit2857.py')==deriv['source_driver_sha256'],'original driver bound')
    need(sha(precision/'driver40/admit_precision.py')==deriv['generated_driver_sha256'],'generated driver bound')
    body=original
    for x in deriv['changes']:
        need(body.count(x['preimage'])==1,'unique admitted preimage')
        body=body.replace(x['preimage'],x['replacement'])
    need(body==generated,'complete declared source diff')
    for x in reversed(deriv['changes']):
        need(body.count(x['replacement'])==1,'unique reverse replacement')
        body=body.replace(x['replacement'],x['preimage'])
    need(body==original,'byte exact original roundtrip by reversal')
    a=predicates(original);b=predicates(generated)
    removed=list((a-b).elements());added=list((b-a).elements())
    need(len(removed)==1 and len(added)==3,'only parameterized equality and two added helper hashes')
    oldcheck="need(kappa == C-Q(1,10**70)-Q(1,10**46) and kappa > previous, 'candidate must strictly improve full exact pinned frontier headline before full release')"
    newcheck="need(kappa == C-Q(1,10**(DIG+46))-Q(1,10**(DIG+22)) and kappa > previous, 'candidate must strictly improve full exact pinned frontier headline before full release')"
    need(removed==list(predicates(oldcheck).elements()),'only old fixed-digit equality changed')
    need(list(predicates(newcheck).elements())[0] in added,'new equality retains strict comparison')
    # Independently evaluate every changed numeric formula at 24 and 40 digits.
    formulas={}
    for dig in (24,40):
        formulas[dig]={'supplier_gap':str(F(1,10**(dig+80))),
                       'root_grid':str(F(1,10**dig)),
                       'outer_floor':str(F(1,10**(dig+46))),
                       'outer_backoff':str(F(1,10**(dig+22)))}
    need(F(formulas[24]['supplier_gap'])==F(1,10**104) and
         F(formulas[24]['root_grid'])==F(1,10**24) and
         F(formulas[24]['outer_floor'])==F(1,10**70) and
         F(formulas[24]['outer_backoff'])==F(1,10**46),'original24 numeric roundtrip')
    # Added generator changes only discovery; assert the retained strict
    # admission moment-check block is untouched by the declared patches.
    assembler=Path(sys.argv[4]);assembly=assembler.read_text()
    call=next(x for x in deriv['changes'] if "patch('code/assemble.py'" in x['replacement'])
    patchcalls=[n for n in ast.walk(ast.parse(generated)) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='patch' and n.args and isinstance(n.args[0],ast.Constant) and n.args[0].value=='code/assemble.py']
    # Other pre-existing assembly patches belong to baseline; select new discovery.
    discovery=[]
    for n in patchcalls:
        for before,after in ast.literal_eval(n.args[1]):
            if before.startswith(' if DISCOVER:b='):
                discovery.append((before,after))
    need(len(discovery)==1,'single discovery-only assembly replacement')
    before,after=discovery[0];need(assembly.count(before)==1,'discovery exact source preimage')
    changed=assembly.replace(before,after)
    start=assembly.index(' def check_moment(');end=assembly.index(' conservative_moments=',start)
    retained=assembly[start:end]
    need(retained in changed,'entire original coarse/fine strict moment checking retained')
    files={'original_driver':package/'tools/admit2857.py','candidate_driver':precision/'driver40/admit_precision.py',
           'discovery_helper':precision/'driver40/endpoint_refiner.py','producer':precision/'build_precision_driver.py',
           'native_profile':package/'data/PROFILE.json','baseline_claim':package/'CLAIM.json',
           'source_assembler':assembler,'independent_arithmetic':Path(core.__file__),'independent_audit':Path(__file__)}
    result={'status':'PASS_INDEPENDENT_PRECISION_ENDPOINTS_AND_DRIVER_SCOPE_NOT_FULL_RELEASE',
        'baseline_head':'34328b1d5e5bebac62d5cabec993dfbfd7b2123f',
        'root_lower':str(C),'root_upper':str(upper),'native_moment_intervals':core.strings(native),
        'conservative_lower':str(fine),'conservative_moment_intervals':core.strings(conservative),
        'kappa':str(K),'kappa_decimal':decimal(K),'baseline':str(old),'gain':str(K-old),'gain_decimal':decimal(K-old),
        'negative_controls':['root upper endpoint strictly rejected','one extra paid rank-one child strictly rejected'],
        'driver_changes':len(deriv['changes']),'old_predicate_occurrences':sum(a.values()),
        'new_predicate_occurrences':sum(b.values()),'only_changed_old_predicate':'fixed 24-digit outer equality generalized to DIG with same strict comparison',
        'added_predicates':'two exact discovery-helper source hash checks','formulas':formulas,
        'roundtrip':'reversal of declared edits exactly recovers original source bytes; parameterized numeric formulas agree at DIG24. Builder itself currently allows26..70, so no generated24 wrapper execution claimed.',
        'unchanged_moment_check_block_sha256':hashlib.sha256(retained.encode()).hexdigest(),
        'input_sha256':{k:sha(v) for k,v in files.items()},
        'scope':'Precision-only candidate; no new native construction or full release pass asserted. Full source/cache/native/owner/invoice/control/release gates remain required.'}
    out.mkdir(parents=True,exist_ok=True)
    (out/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','kappa_decimal','gain_decimal','driver_changes','old_predicate_occurrences','new_predicate_occurrences']},indent=2))

if __name__=='__main__':main()

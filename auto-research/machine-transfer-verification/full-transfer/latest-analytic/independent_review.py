#!/usr/bin/env python3
"""Independent exact audit of the literal PR73 Lean witnesses and source pin.

Imports neither the witness generator nor the package's checker. It uses
Fraction arithmetic and a Horner polynomial evaluator, not real floats.
Does not compile Lean or replay physical words/CRT.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
PIN = '253ecc88faeed55a950c76026d1fe67a7f690123'
SOURCE_PATH = 'research/round6-pr71/parameter-certificate.json'
SOURCE_SHA = 'f391f7cee5377ab148f3cecc223fd8111c3075578b1ee327610e4dd3e3468fb0'

def exp_partial(x, terms):
    # Horner form of 1+x+x^2/2!+...+x^(terms-1)/(terms-1)!.
    result = Q(1)
    for i in range(terms-1, 0, -1):
        result = 1+x*result/i
    return result

def exp_remainder_bound(x, terms):
    term = Q(1)
    for i in range(1, terms+1):
        term *= x/i
    return term*Q(terms+1, terms)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repository', type=Path, required=True)
    args = ap.parse_args()
    raw = (HERE/'pr73-candidate.json').read_bytes()
    blob = subprocess.check_output(['git','-C',str(args.repository),'show',PIN+':'+SOURCE_PATH])
    assert raw == blob and sha256(raw).hexdigest() == SOURCE_SHA
    c = json.loads(raw)
    p = c['bit']
    assert (p['m'],p['W'],p['total_rank'],p['deficit'],p['maxchild']) == (575,135075665,77666660475,1846900,529)
    a = Q(12854322426487,250000000000000000)
    assert a == Q(c['bit_saving']) and 0 < a < 1
    lean = (HERE/'Pr73ProfileCertificate.lean').read_text()
    def nat(name):
        return int(re.search(r'^def '+name+r' : ℕ := (\d+)$',lean,re.M)[1])
    def rat(name):
        match = re.search(r'^def '+name+r' : ℚ := \((\d+) / (\d+) : ℚ\)$',lean,re.M)
        return Q(int(match[1]),int(match[2]))
    assert nat('m') == p['m'] and nat('W') == p['W'] and rat('saving') == a
    L2 = rat('logTwoUpper')
    assert L2 >= 0 and exp_partial(L2,24) >= 2
    rows = re.findall(r'⟨(\d+), (\d+), (\d+), \((\d+) / (\d+) : ℚ\), \((\d+) / (\d+) : ℚ\)⟩',lean)
    assert len(rows) == 26
    literals, moment, audits = {}, Q(0), []
    for t,n,k,ln,ld,un,ud in rows:
        t,n,k = int(t),int(n),int(k)
        assert t not in literals and 0 < t < p['m'] and n > 0
        literals[str(t)] = n
        L,U = Q(int(ln),int(ld)),Q(int(un),int(ud))
        ratio = Q(p['m'], t*2**k)
        assert 1 <= ratio <= 2 and L >= 0
        log_gap = exp_partial(L,24)-ratio
        assert log_gap >= 0
        x = a*(k*L2+L)
        assert 0 <= x <= 1
        exp_gap = U-exp_partial(x,8)-exp_remainder_bound(x,8)
        assert exp_gap >= 0
        moment += Q(n*t,p['m']*p['W'])*U
        audits.append(dict(width=t,multiplicity=n,scale=k,logSmall=str(L),expUpper=str(U),
                           lower_exp_certificate_gap=str(log_gap),argument=str(x),
                           upper_exp_certificate_gap=str(exp_gap)))
    assert literals == p['child_multiplicities']
    assert sum(int(t)*n for t,n in literals.items()) == p['total_rank']
    assert p['m']*p['W']-p['total_rank'] == p['deficit']
    assert 1-moment == Q(699597017858129667,4221114531250000000000000000000000000) > 0
    witnesses = json.loads((HERE/'pr73-witnesses.json').read_text())
    assert witnesses['source_sha256'] == SOURCE_SHA
    assert (witnesses['m'],witnesses['W']) == (p['m'],p['W'])
    assert Q(witnesses['saving']) == a and Q(witnesses['log_two_upper']) == L2
    assert (witnesses['log_terms'],witnesses['exp_terms']) == (24,8)
    assert Q(witnesses['rational_moment_upper']) == moment
    assert Q(witnesses['rational_gap']) == 1-moment
    assert witnesses['rows'] == [{k:r[k] for k in ('width','multiplicity','scale','logSmall','expUpper')} for r in audits]
    manifest = json.loads((HERE/'theorem-manifest.json').read_text())
    build = json.loads((HERE/'verification/axiom-audit.json').read_text())
    hashes = {}
    for name,item in manifest['files'].items():
        digest = sha256((HERE/name).read_bytes()).hexdigest()
        assert digest == item['sha256'] == build['files'][name]['sha256']
        assert set(item['theorems']) == set(build['files'][name]['theorems'])
        assert all(set(ax) <= {'propext','Quot.sound','Classical.choice'} for ax in build['files'][name]['theorems'].values())
        hashes[name] = digest
    assert build['new_theorem_count'] == 14 and build['dependency_theorem_count'] == 52
    dependency_count = 0
    for folder,key in [(HERE.parents[1]/'next-proof/analytic','analytic_dependency_manifest_sha256'),
                       (HERE.parents[1]/'transfer-proof/recurrence','recurrence_dependency_manifest_sha256')]:
        manifest_raw = (folder/'theorem-manifest.json').read_bytes()
        assert sha256(manifest_raw).hexdigest() == manifest[key]
        dep = json.loads(manifest_raw)
        for name,item in dep['files'].items():
            assert sha256((folder/name).read_bytes()).hexdigest() == item['sha256'] == build['files'][name]['sha256']
            assert set(item['theorems']) == set(build['files'][name]['theorems'])
            assert all(set(ax) <= {'propext','Quot.sound','Classical.choice'} for ax in build['files'][name]['theorems'].values())
            dependency_count += len(item['theorems'])
    assert dependency_count == 52
    result = dict(status='PASS independent pinned-source/literal/Fraction audit',pin=PIN,
                  candidate_sha256=SOURCE_SHA,m=p['m'],W=p['W'],saving=str(a),
                  row_count=26,rank_mass=p['total_rank'],deficit=p['deficit'],maxchild=p['maxchild'],
                  rational_moment_upper=str(moment),rational_gap=str(1-moment),
                  new_lean_theorem_count=14,dependency_theorem_count=52,
                  final_source_sha256=hashes,rows=audits,
                  scope='Actual finite characteristic certified; state-cost theorem still requires its explicit physical child/base/recurrence hypotheses')
    (HERE/'independent-review.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS literal26rows, pinned Gitblob, every rational witness inequality, exact gap and final14+52 Lean receipt')

if __name__ == '__main__':
    main()

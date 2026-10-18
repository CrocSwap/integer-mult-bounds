#!/usr/bin/env python3
"""Optional HiGHS nomination, adapted from navinor's retained gen_duals.py.
Solver outputs are proposals; acceptance rechecks all columns exactly.
Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
"""
import gzip, json, sys, hashlib
from fractions import Fraction as F
from pathlib import Path
import highspy
import numpy as np
import scipy
import scipy.sparse as sp
import scipy.sparse.linalg as spla
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import model as M
RANKS=range(1,10)
A=F(21,20)*F(1690054109089,10**15)

def solve(rows, rhs, cols, gamma):
    nr, nc = len(rows), len(cols)
    start, index, value = [0], [], []
    cost = []
    for _, c, entries in cols:
        cost.append(sum(c[d] * gamma[d] for d in range(len(c))))
        for i, a in sorted(entries):
            index.append(i)
            value.append(float(a))
        start.append(len(index))
    lp = highspy.HighsLp()
    lp.num_col_, lp.num_row_ = nc, nr
    lp.col_cost_ = np.array(cost)
    lp.col_lower_ = np.zeros(nc)
    lp.col_upper_ = np.full(nc, highspy.kHighsInf)
    lp.row_lower_ = np.array(rhs, dtype=float)
    lp.row_upper_ = np.array(rhs, dtype=float)
    lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise
    lp.a_matrix_.start_ = np.array(start, dtype=np.int32)
    lp.a_matrix_.index_ = np.array(index, dtype=np.int32)
    lp.a_matrix_.value_ = np.array(value)
    h = highspy.Highs()
    h.setOptionValue('output_flag', False)
    h.setOptionValue('presolve', 'on')
    h.setOptionValue('threads', 1)
    h.setOptionValue('solver', 'simplex')
    h.passModel(lp)
    h.run()
    assert h.getModelStatus() == highspy.HighsModelStatus.kOptimal, h.modelStatusToString(h.getModelStatus())
    basis = h.getBasis()
    sol = h.getSolution()
    return h.getInfo().objective_function_value, basis, list(sol.col_value)


def symbolic_duals(rows, cols, basis):
    # pybind's vector properties return fresh lists: fetch each exactly once.
    column_status, row_status = basis.col_status, basis.row_status
    basic_cols = [j for j,status in enumerate(column_status) if status == highspy.HighsBasisStatus.kBasic]
    active_rows = [i for i,status in enumerate(row_status) if status != highspy.HighsBasisStatus.kBasic]
    assert len(basic_cols) == len(active_rows), (len(basic_cols), len(active_rows))
    rpos = {i: k for k, i in enumerate(active_rows)}
    data, ri, ci = [], [], []
    for kc, j in enumerate(basic_cols):
        for i, a in cols[j][2]:
            if i in rpos:
                # transpose: row = basic column, column = active row
                ri.append(kc)
                ci.append(rpos[i])
                data.append(float(a))
    At = sp.csc_matrix((data, (ri, ci)), shape=(len(basic_cols), len(active_rows)))
    lu = spla.splu(At)
    q = {}
    for d in RANKS:
        rhs_d = np.array([float(cols[j][1][d]) for j in basic_cols])
        sol = lu.solve(rhs_d)
        for k, i in enumerate(active_rows):
            x = F(float(sol[k])).limit_denominator(1 << 20)
            if x:
                q.setdefault(i, {})[d] = x
    # exact check on the basic columns: A_B^T q == c_B coordinate-wise
    for j in basic_cols:
        key, c, entries = cols[j]
        for d in RANKS:
            s = sum((a * q.get(i, {}).get(d, 0) for i, a in entries), F(0))
            assert s == c[d], ('rationalised dual is not exact on a basic column', key, d, s, c[d])
    return q


def main():
    raw=gzip.decompress((HERE/'references/WORD.json.gz').read_bytes())
    word=json.loads(raw); model=M.Model(word); a=float(A)
    gamma=[0.0]+[d*((73/d)**a-(73/51)**a)/a for d in RANKS]
    out={'schema':'selected-k8-unrestricted-end-duals-v1','nomination_a':str(A),
         'word_sha256':hashlib.sha256(raw).hexdigest(),'components':[]}
    report={'versions':{'python':sys.version.split()[0],'highspy':highspy.Highs().version(),'numpy':np.__version__,'scipy':scipy.__version__},'solver_options':{'presolve':'on','threads':1,'solver':'simplex'},'components':[]}
    candidate={}; total=[F(0)]*10
    for index,comp in enumerate(model.components()):
        print('ASSEMBLE',index,len(comp),flush=True)
        labels,unary,pairs=model.component_problem(comp)
        rows,rhs,cols=M.lp(labels,unary,pairs)
        print('SOLVE',index,len(rows),len(cols),flush=True)
        obj,basis,x=solve(rows,rhs,cols,gamma)
        print('LP_FINISHED',index,obj,flush=True)
        q=symbolic_duals(rows,cols,basis)
        print('SYMBOLIC_FINISHED',index,len(q),flush=True)
        objective={d:sum((rhs[i]*vec.get(d,0) for i,vec in q.items()),F(0)) for d in RANKS}
        for d in RANKS:total[d]+=objective[d]
        fractional=sum(1 for value in x if 1e-8<value<1-1e-8)
        chosen_by_node={node:[] for node in comp}
        for j,(key,c,entries) in enumerate(cols):
            if key[0]=='x' and x[j]>1-1e-8:
                chosen_by_node[key[1]].append(key[2])
        for node,chosen in chosen_by_node.items():
            if len(chosen)==1:candidate[node]=chosen[0]
        report['components'].append({'first':comp[0],'nodes':len(comp),'rows':len(rows),'columns':len(cols),'fractional_columns':fractional,'numeric_objective':obj})
        out['components'].append({'first':json.dumps(comp[0]),'nodes':len(comp),'duals':{json.dumps(rows[i]):{str(d):str(z) for d,z in sorted(vec.items())} for i,vec in sorted(q.items())}})
        if index%20==0 or fractional:print(index,len(comp),len(cols),'fractional',fractional,flush=True)
    full=len(candidate)==len(model.domain)
    report['complete_integral_candidate']=full
    report['symbolic_component_objective']={str(d):str(total[d]) for d in RANKS}
    if full:
        profile=model.profile(candidate)
        report['candidate_profile']=profile
        report['changed_endpoints']=[n[1] for n in candidate if n[0]=='E' and candidate[n]!=model.original_caps[n[1]]]
        report['changed_gate_frames']=sum(n[0]=='G' and candidate[n]!=model.given[n[1]] for n in candidate)
        primal={'assignment':{json.dumps(n):list(fr) for n,fr in sorted(candidate.items())},'profile':profile}
        (HERE/'PRIMAL.json.gz').write_bytes(gzip.compress(json.dumps(primal,sort_keys=True,separators=(',',':')).encode(),mtime=0))
    data=json.dumps(out,sort_keys=True,separators=(',',':')).encode()
    (HERE/'DUALS.json.gz').write_bytes(gzip.compress(data,mtime=0))
    report['canonical_duals_sha256']=hashlib.sha256(data).hexdigest()
    (HERE/'DISCOVERY.json').write_text(json.dumps(report,indent=2)+'\n')
    print('NOMINATED_NOT_CERTIFIED',len(out['components']),full,report.get('candidate_profile'),report.get('changed_endpoints'),flush=True)

if __name__=='__main__':main()

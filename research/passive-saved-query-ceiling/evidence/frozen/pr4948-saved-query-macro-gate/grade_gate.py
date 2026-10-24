#!/usr/bin/env python3
"""Fixed-source necessary grade gate for the nine passive macro cuts.

No native physical word is emitted. An exact one-column grade census is
combined with a written sufficiently-large-width pure-word argument.
"""
import contextlib
import hashlib
import io
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent
with contextlib.redirect_stdout(io.StringIO()): env=runpy.run_path(str(HERE/'bank_span.py'))
a,need,obs=env['a'],env['need'],env['obs']
up=env['env'];ce,N,W,Q=up['ce'],up['N'],up['word'],up['Q']
Ks=[W(r['K_word']) for r in N['ports']]
inverses=[K.adjoint() for K in Ks]
D=ce.fourier(9,range(1,9));qi=Q.adjoint();full=ce.fourier(9)
grade=up['grade'];M=[[F(up['F'][j][i]) for j in range(112)] for i in range(112)]
for K in Ks:
    need(grade(K)==0,'Source K is monomial')
    kr,rk=K.then(full),full.then(K)
    need(kr.tab==rk.tab and kr.zero_state()==rk.zero_state(),
         'Source K commutes full Gaussian including absolute phase')

# The row variables refer to original inputs before the scalar right
# boundary, so target/source ownership is not inferred from a later chart.
allowed={((),(0,0)),((-1,),(0,0)),((2,-1),(0,0)),((-1,2),(1,0))}
trace=[]
for label,row in obs:
    column=row[0]
    need(set(column).issubset(allowed),'No hidden D3 or extra-query source0 path')
    trace.append({'observation':label,'original_input0_terms':up['serial'](column)})
need(set(k for _,row in obs for k in row[0])==allowed,'All four stated source-path types occur')

unselected=[j for j in range(112) if M[j][j]==0]
selected=[j for j in range(112) if M[j][j]!=0]
need(len(unselected)==104 and len(selected)==8,'Actual zero/nonzero diagonal split')
need(set(M[j][j] for j in selected)=={F(12)},'Selected source diagonal12')
hist=Counter();per_source=[];all_words=[]
for j in unselected:
    local=Counter();support=[]
    for i in range(112):
        if not M[i][j]:continue
        T=Ks[j].then(inverses[i]) # K_i^-1 K_j.
        op=D.then(T).then(qi)    # Q^-1 K_i^-1 K_j D.
        r=grade(op)
        need(r==7,'All unselected late-source pure words have grade7')
        local[r]+=1;hist[r]+=1;support.append(i)
        all_words.append({'destination_port':i,'source_port':j,
                          'coefficient':str(M[i][j]),'grade':r})
    need(len(support)==52,'Actual unselected column support52')
    per_source.append({'source_port':j,'support':support,'grades':dict(local)})

# Earlier I,Q^-1,C1Q^-1 paths have grades0/1 because every K_i^-1 K_j
# is monomial. The target for original bank0 is D Q^-1, grade9.
need(grade(ce.ident(9))==0 and grade(qi)==1,'Earlier original source grades')
target=qi.then(D)
need(grade(target)==9,'Required first negative target grade9')
selected_controls=[]
for j in selected:
    op=D.then(Ks[j]).then(inverses[j]).then(qi)
    need(grade(op)==9,'Nonzero diagonal control exposes grade9')
    selected_controls.append({'source_port':j,'coefficient':str(M[j][j]),'grade':grade(op)})
need(grade(qi.then(D))==9,'Uncoded identity-code control exposes grade9')

out={
 'status':'STOP_NINE_PASSIVE_CUTS_FINITE_CODE_LEFT_DECODER',
 'declared_cuts':env['cuts'],'observed_bank_fields':len(obs),
 'original_input0_dependency_trace':trace,
 'actual_source_zero_diagonal_ports':unselected,
 'post_FULL_unselected_word_grade_histogram':dict(hist),
 'per_source':per_source,'all_supported_words':all_words,
 'earlier_word_grades':[0,1],'target_grade':9,
 'selected_diagonal_controls':selected_controls,
 'all_width_implication':'The finite pure-word support has grades<=7 for these104 inputs, even after any allowed left monomial/code expansion. Projectively distinct one-column operators have independent tensor powers at sufficiently large f. Hence an all-positive-width target identity is impossible in this passive-observation grammar. No width1 matrix-independence inference is used.',
 'left_control_grammar':'Passive observations only; scalar owner operations and finite actual C1/C3 words length<=3. Each code entry is a finite scalar sum of monomial Clifford maps, including phases. No new Q, native internal prefix, or feedback changing later paid-gate inputs.',
 'copy_inventory':env['out']['copy_upper_ledger'],
 'cleanup':'Not reached: even granting every owned COPY/CLEAR, storage, finite code evaluation and precision cost for free does not supply the missing target grade.',
 'scope_limits':['No obstruction to active feedback into a future paid gate, which changes the frozen chronological word.',
   'No obstruction to native internal prefix observations, additional Gaussian calls, or a different incoming/outgoing placement.',
   'No claim that the104 remaining directions fail at every small f; the theorem rejects an identity required at all positive widths.'],
 'physical_emission':False,'new_kappa':None,
 'dependency_sha256':{'bank_span.py':hashlib.sha256((HERE/'bank_span.py').read_bytes()).hexdigest(),
                      'mixed_check.py':env['need_hash']},
 'source_pins':up['result']['source_pins'],
}
print(json.dumps(out,indent=2,sort_keys=True))

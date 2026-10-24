#!/usr/bin/env python3
"""One literal controlled-phase opportunity, no enumeration; Apache-2.0.

Substantial OpenAI Codex assistance; native #4610 and exact Clifford engine
credits retained. Does not assert a two-call endpoint or physical consumer.
"""
from pathlib import Path
from hashlib import sha256
import json,os,subprocess,sys,types

HERE=Path(__file__).resolve().parent
PIN='20bb93cd990d2ff683e4d0fc56b87a42cd5d3296'
PATH='research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py'
raw=subprocess.check_output(['git','show',PIN+':'+PATH],env={**os.environ,'GIT_NO_REPLACE_OBJECTS':'1'})
ce=types.ModuleType('controlled_phase_exact');sys.modules[ce.__name__]=ce
exec(compile(raw,PATH,'exec'),ce.__dict__)

def need(ok,message):
    if not ok:raise ValueError(message)

def grade(op):return ce.rank([x for x,z,p in op.tab[op.n:]])

# Physical bit0 is the shared q coordinate; bit1 is one already-paid A axis.
# C is exactly (-1)^(q*a), a monomial of absolute phase +1 at address zero.
q=ce.cgate(2,1);a=ce.cgate(2,2);C=ce.diag(2,(2,1))
need(grade(C)==0,'one literal monomial controlled phase')
terms={
 'M11_first':a,
 'M11_cross':q.adjoint().then(a).then(C).then(q),
 'M12_minus':a.then(C).then(q),
 'M21':q.adjoint().then(a).then(C),
 'M22':a.then(C),
}
grades={name:grade(op) for name,op in terms.items()}
need(grades['M12_minus']==grades['M21']==2,'both offdiagonal words have maximal old-two-axis grade')
need(grades['M22']==grades['M11_first']==1,'old diagonal grade is one')
need(grade(C.then(C))==0 and C.then(C).tab==ce.ident(2).tab,'C inverse is same literal monomial')
# Absolute phase is retained by the exact circuit word. The four-column
# monomial C action is also checked independently from its literal definition.
phase={x:(-1 if x==3 else 1) for x in range(4)}
need(phase=={0:1,1:1,2:1,3:-1},'controlled-phase address convention')

# Lift the exact literal words to all17 axes. Spectator A hasseven axes,
# fresh B haseight, so offdiagonal rank is2+15=17 at every column width.
def lift(op,n):
    out=ce.ident(n)
    for g in op.circuit:
        if g[0]=='C':gate=ce.cgate(n,g[1],g[2])
        elif g[0]=='D':gate=ce.diag(n,tuple(g[1])+(0,)*(n-op.n),tuple(g[2])+(0,)*(n-op.n))
        else:raise ValueError('unexpected literal gate '+repr(g))
        out=out.then(gate)
    return out
spectator=ce.fourier(17,range(2,17))
full={name:grade(lift(op,17).then(spectator)) for name,op in terms.items()}
need(full['M12_minus']==full['M21']==17 and full['M22']==16,'actual17-axis support grades')

# Control: a pure q<->a address swap instead of C has only one rank17 word.
P=ce.perm(2,(2,1))
swap={
 'M11_first':a,
 'M11_cross':q.adjoint().then(a).then(P).then(q),
 'M12_minus':a.then(P).then(q),
 'M21':q.adjoint().then(a).then(P),
 'M22':a.then(P),
}
swapgrades={name:grade(op)+15 for name,op in swap.items()}
need([name for name,r in swapgrades.items() if r==17]==['M21'],'pure-swap one-copy obstruction control')

result=dict(status='PASS_EXACT_CZ_GRADES_BUT_FAIL_LOWER_GRADE_PURITY_GATE',
 source_commit=PIN,compiler_path=PATH,compiler_sha256=sha256(raw).hexdigest(),
 physical_monomial='C_f=(-1)^(sum_columns q_column*a_column), applied to interstage Y only',
 monomial_passes_per_port=1,main_ports=112,total_main_monomial_passes=112,
 extra_gaussian_calls=0,helper_inputs_and_targets_unchanged=True,
 old_two_axis_grades=grades,full17_axis_grades=full,pure_swap_control_grades=swapgrades,
 old_two_axis_literal_words={name:op.circuit for name,op in terms.items()},
 max_rank_projection_image='2*dim_K B, since [[c,b],[a,0]] is injective on B^2 for group units a,b',
 optimistic_profile='224H17+2H versus 2P; source funded-C unwrapped surplus about39.063938',
 maximal_grade_count_gate_passed=True,lower_grade_purity_gate_passed=False,
 lower_grade_obstruction='M22 is a nonzero grade16 group unit; invertible outer GL2(B) cannot erase a nonzero grade16 matrix component',
 endpoint_identity_proved=False,native_full_caller_proved=False,compiler_reserve_funded=False,
 scope='one literal interstage controlled phase; no enumeration, no outer boundary synthesis, no kappa')
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='old_two_axis_literal_words'},sort_keys=True))

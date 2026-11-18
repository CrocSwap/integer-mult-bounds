if not __debug__:
    raise RuntimeError("Run verification without -O; assertions are required")
import sys, json, hashlib, random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from reversible_linear import compile_linear,clear,selftest
r=selftest(); controls=[]
for a,d,w,x,t in [([1],2,3,[1],0),([2],1,3,[3],-2),([1,-1],1,4,[3,1],3)]:
 c,o,s=compile_linear(a,d,w); target,_,invalid=clear(c,o,x,t,w)
 assert target or invalid
 controls.append({'coefficients':a,'D':d,'width':w,'input':x,'target':t,'target_output':target,'invalid_output':invalid,'illegal_erasure_blocked':True})
r['adversarial_controls']=controls
rng=random.Random(89208)
for _ in range(100):
 w=rng.randrange(1,11);a=[rng.randrange(-12,13) for _ in range(rng.randrange(1,5))];d=rng.randrange(1,17)
 c,o,s=compile_linear(a,d,w)
 x=[rng.randrange(-(1<<(w-1)),1<<(w-1)) for _ in a];t=rng.randrange(-(1<<(w-1)),1<<(w-1))
 target,_,invalid=clear(c,o,x,t,w)
 assert (not target and not invalid)==(sum(k*v for k,v in zip(a,x))==d*t)
r['additional_random_contracts_all_zero_iff_exact_integer_relation']=100
r['script_sha256']=hashlib.sha256(Path(__file__).with_name('reversible_linear.py').read_bytes()).hexdigest()
c,o,stats=compile_linear([1]*4+[-1]*4,2,1076)
x=[1,3,-2,2,4,-1,5,-4]; n=sum(x[:4])-sum(x[4:])
target,_,invalid=clear(c,o,x,n//2,1076)
assert not target and not invalid
r['fullwidth_network']={'width':1076,'stats':stats,'executed':True}

# Independent-review edge cases, now permanent reproducible regressions.
A=1<<1075; M=A-1
edge_cases=[
 ('positive_max_exact',[M,M,0,0,0,0,0,0],M,0),
 ('negative_min_exact',[-A,-A,0,0,0,0,0,0],-A,0),
 ('fraction',[1,0,0,0,0,0,0,0],0,1),
 ('positive_overflow',[M,M,2,0,0,0,0,0],-A,1)]
r['fullwidth_edges']=[]
for label,x,target,expected_flag in edge_cases:
 after,_,flag=clear(c,o,x,target,1076)
 assert after==0 and flag==expected_flag
 r['fullwidth_edges'].append({'case':label,'inputs':[str(t) for t in x],'target':str(target),'target_output':after,'invalid_output':flag})
# Full reversible-network roundtrips from arbitrary bitstrings verify gate
# bijectivity; these are NOT zero-ancilla clean-computation claims.
from reversible_linear import apply
small,outputs,_=compile_linear([1,-2],3,3)
rng_inverse=random.Random(7680)
for _ in range(100):
 state=[rng_inverse.randrange(2) for _ in range(small.next+4)]
 initial=list(state)
 gates=small.gates+[('CX',b,small.next+i) for i,b in enumerate(outputs)]+[('CX',small.invalid,small.next+3)]+list(reversed(small.gates))
 apply(state,gates);apply(state,reversed(gates));assert state==initial
r['arbitrary_initial_state_gate_inverse_roundtrips']=100

r['example_cost_table']=[]
for width in (4,1076,1108):
 circuit,output,cost=compile_linear([1]*4+[-1]*4,2,width)
 r['example_cost_table'].append({'width':width,**cost})
from public_source_binding import verify as verify_public
r['public_source_binding']=verify_public()
Path(__file__).with_name('EXAMPLE-PROVENANCE.json').write_text(json.dumps(r['public_source_binding'],indent=2)+'\n',encoding='utf-8',newline='\n')
Path(__file__).with_name('RESULT.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(r))
print("PASS_CLEAN_REVERSIBLE_WITNESS")

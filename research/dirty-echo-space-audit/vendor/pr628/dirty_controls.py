"""Corrupt instruction order, restoration, phase indexing and scratch handling."""
from pathlib import Path
import json,types,argparse,importlib.util
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('dirty',P/'dirty.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d);c=d.c;F=d.F
source=(P/'dirty.py').read_text()

def case(module):
    x=[(F(1,2),F(1,4)),c.ONE,(F(-1,4),F(1,2))];x0=x[:]
    y=[(F(7),F(-2)),(F(3),F(9)),(F(-4),F(1))];y0=y[:]
    scratch=[[(F(3+j+i),F(2*j-i))for i in range(3)]for j in range(2)];s0=[z[:]for z in scratch]
    phases=[c.ONE,(F(3,5),F(4,5)),(F(0),F(1))]
    fs=[(True,(F(1,4),F(1,8)),F(3)),(False,(F(1,4),F(-1,8)),F(1)),(True,(F(1,8),F(1,4)),F(1))]
    expected=d.exact_operator(x0,fs,phases,1)
    module.compose(x,y,fs,scratch,phases,F(1,2),256,1)
    c.need(x==x0 and scratch==s0,'dirty restoration')
    c.need(all(c.norm2(c.sub(c.sub(v,t),e))<=F(1,1<<128)for v,t,e in zip(y,y0,expected)),'dense error')
    module.compose(x,y,fs,scratch,phases,F(1,2),256,1,-1)
    c.need(x==x0 and scratch==s0 and y==y0,'inverse instruction word')

case(d);controls=[]
mutations=[
 ('undo_in_forward_order','for i in ordered(n,-d):','for i in ordered(n,d):'),
 ('wrong_inner_phase','conj(phases[(i+d)%n])','conj(phases[i])'),
 ('omit_inner_shift','lambda i:(i-d)%n','lambda i:i'),
 ('negative_word_not_reversed','for src,dst,fs,sgn in reversed(operations)','for src,dst,fs,sgn in operations'),
 ('omit_last_commutator_term','(x,z,B,-1),(z,y,A,-1)','(x,z,B,-1)'),
 ('omit_scratch_restoration','(x,z,B,-1),(z,y,A,-1)','(z,y,A,-1)'),
 ('overwrite_dirty_scratch','z=scratch[0];rest=scratch[1:]','z=scratch[0];z[:]=[c.ZERO]*len(z);rest=scratch[1:]'),
 ('insufficient_rounding','n=len(x);c.need(x is not y','bits=8;n=len(x);c.need(x is not y'),
]
for name,old,new in mutations:
    c.need(source.count(old)==1,'unambiguous mutation '+name)
    m=types.ModuleType('mutant_'+name);m.__file__=str(P/'dirty.py');exec(compile(source.replace(old,new),m.__file__,'exec'),m.__dict__)
    try:case(m)
    except ValueError as error:controls.append(dict(name=name,rejected=str(error)))
    else:raise ValueError('accepted mutation '+name)
a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);args=a.parse_args();args.out.write_text(json.dumps(dict(status='passed',positive=1,controls=controls),indent=2)+'\n');print('PASS positive and',len(controls),'instruction mutations')

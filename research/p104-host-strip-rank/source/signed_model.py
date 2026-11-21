"""Load the pinned independent Laurent model without its physical main."""
from pathlib import Path
from types import ModuleType
import sys

root=Path(__file__).resolve().parent
p=root/"candidate_gate.py"
text=p.read_text()
body=text[text.index("def module("):text.index("def precision(")]
exec(compile(body,str(p),"exec"))
def ceil_log2(q):
    a,b=q.numerator,q.denominator
    k=a.bit_length()-b.bit_length()
    assert k>=0
    return k+(a>b<<k)

def signed_model():
    code=(root/"independent.py").read_text()
    m=independent(root)
    # Recompile only the Laurent caller after the pinned signed-op edit.
    # The 8+8 rechart can produce masses above IEEE double range.
    base=code[code.index("def caller("):code.index("def invoices(")]
    base=base.replace("elif event[1]=='IDLE_ONE':degree.update(event[3])",
                      "elif event[1] in ('IDLE_ONE','IDLE_ODD'):degree.update(event[3])")
    base=base.replace("elif op=='IDLE_ONE':rows[r]=pscale(rows[r],m=sum(1<<(8*(s-1)) for s in e[3]))",
                      "elif op in ('IDLE_ONE','IDLE_ODD'):rows[r]=pscale(rows[r],q=e[4] if op=='IDLE_ODD' else 0,m=sum(1<<(8*(s-1)) for s in e[3]))")
    assert base.count("math.ceil(math.log2(maxmass))")==1
    base=base.replace("math.ceil(math.log2(maxmass))","ceil_log2(maxmass)")
    m.ceil_log2=ceil_log2
    exec(compile(base,str(root/"independent.py"),"exec"),m.__dict__)
    return m

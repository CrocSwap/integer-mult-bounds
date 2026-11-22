"""Run both literal scaled copies on independent nonzero Gaussian product states."""
from argparse import ArgumentParser
from pathlib import Path
from functools import cache
import sys
p=ArgumentParser()
p.add_argument("runtime",type=Path)
args=p.parse_args()
sys.path.insert(0,str(args.runtime.resolve()))
from upstream import HERE,install
_,_,_,source=install()
from raw48 import ComplexRaw
from periodic import Job
from retimed_supplier import Raw
from grades import SCALES, SPLITS
from band_product import production_supplier
from check_nonzero_eight import Field, Axes, WitnessRaw, addresses, basis, diagonal, final_ray, rot

class RayField(Field):
    def blank(self):
        return RayField(self.stock)

    def phase(self,fn,suffix):
        if self.data is None:
            return
        z,rays=self.data
        n=len(rays)
        base=fn(0)%4
        z=rot(z,base)
        # The source opcodes I, S and CZ apply the same phase polynomial in
        # each of the n physical columns. Evaluate that polynomial on all 512
        # assignments of the first column. Check additional physical addresses
        # in every column as well as two mixed whole-register assignments.
        single=tuple((fn(x)-base)%4 for x in addresses(0,n))
        after=[]
        totals=[base,base]
        probes=[0,0]
        for i,v in enumerate(rays):
            indices=((71*i+93)%512,(11*i+7)%512)
            locations=addresses(i,n)
            for sample,j in enumerate(indices):
                assert (fn(locations[j])-base)%4==single[j]
                totals[sample]+=single[j]
                probes[sample]|=locations[j]
            v2,phase=diagonal(v,single)
            after.append(v2)
            z=rot(z,phase)
        assert all(fn(a)%4==q%4 for a,q in zip(probes,totals))
        self.data=z,tuple(after)

def check():
    assert SCALES==(1,79) and SPLITS==1008
    producer=production_supplier(1024,10**18)
    a,w=producer.physical,producer.word
    sizes, paid = producer.recipe.targets, producer.recipe.paid
    assert producer.recipe.ambient==153*79
    stock=[0,0]
    fields={i:RayField(stock) for i in range(len(sizes))}
    jobs=[Job(i,range(2*k)) for i,k in enumerate(sizes)]
    clock,call=next((i,row[1]) for i,row in enumerate(a.instructions()) if row[0]=="NATIVE")
    key=("helper",clock,call,1544)
    pawn=next(i for i,p in enumerate(w.targets) if p.tag==key)
    assert w.targets[pawn].rank==8
    exp={}
    widths=tuple(2*s for s in SCALES)
    for copy,cols in enumerate(widths):
        owner=pawn+copy*len(w.targets)
        origins=tuple((37*i+11+17*copy)%512 for i in range(cols))
        initial=((3 if not copy else -7)<<2048,(5 if not copy else 2)<<2048)
        fields[owner].data=initial,tuple(basis(i) for i in origins)
        exact=tuple(final_ray(i) for i in origins)
        z=rot(initial,sum(p for _,p in exact))
        assert all(x % (16**cols)==0 for x in z)
        exp[owner]=(z[0]//16**cols,z[1]//16**cols),tuple(v for v,_ in exact)
    raw=WitnessRaw(a,fields,Axes(),low=0,bundle=1,slots=2*producer.recipe.ambient)
    it=Raw(w,raw).native(jobs,2)
    completed=0
    nonzero={width:0 for width in widths}
    for grade in paid:
        job=next(it)
        field=fields[job.owner]
        completed+=1
        assert len(job.axes)==2*grade
        if field.data is not None:
            nonzero[len(field.data[1])]+=1
            for axis in job.axes:
                field.paid(axis)
    assert next(it,None) is None
    assert set(fields)==set(range(len(sizes))) and all(f.live and f.writes>0 for f in fields.values())
    assert {i:f.data for i,f in fields.items() if f.data is not None}==exp
    assert all(nonzero.values())
    writes=sum(f.writes for f in fields.values())
    for f in fields.values():
        f.retire()
    assert stock[0]==0
    print("physical columns",widths,"nonzero cut counts",nonzero,"all paid",completed)
    print("owners",len(fields),"owner writes",writes,"sum output axes",2*sum(sizes),"peak handles",stock[1])
    print("exact nonzero output Hilbert log2 dimensions",tuple(9*x for x in widths))
    print("PASS_SCALED_POSITIVE_RAW")

if __name__=="__main__":
    check()

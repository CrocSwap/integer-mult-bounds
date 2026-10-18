"""Check the finite interfaces used by the written recursive induction."""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from importlib.util import spec_from_file_location,module_from_spec
from math import lcm

from expressions import Expression,BoundExpression,FrozenFields
from provider import need,fixture_header,prepare_fallback,build_weights,canonical
from recursive_plan import caller,residual_plan,depth
from fallback_program import shape,child_descriptor


def moments(catalogue,root):
    directory=root/"research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r740-replica32/code/engines"
    modules=[]
    for name in ("moment","base_two_moment"):
        spec=spec_from_file_location("retained_"+name,directory/(name+".py"))
        module=module_from_spec(spec);spec.loader.exec_module(module);modules.append(module)
    first,second=modules;c=F(17,10000);h=catalogue.profile;w=28416
    fallback=32*64**2*sum(h.values())
    one=(sum(F(r*n,64*w) for r,n in h.items())+F(fallback,10**16*64*w))
    a=first.moment(h,64,w,c,True)
    b=second.moment(64,w,list(h.items()),c)
    bad=second.moment(64,w,[(1,fallback)],c)
    b=tuple(x+y/10**16 for x,y in zip(b,bad))
    need(max(a[0],b[0])<=min(a[1],b[1]),"retained rational moment enclosures intersect")
    need(one<F(199,200) and max(a[1],b[1])<F(9999,10000),"coarse strict moment margins")
    return {"coarse_saving":str(c),"fallback_envelope":fallback,
            "linear_moment":str(one),"linear_upper":"199/200",
            "fractional_upper":"9999/10000",
            "first_upper_decimal":first.decimal(a[1]),
            "second_upper_decimal":first.decimal(b[1]),
            "ordinary_saving":str(c*(1-c)),
            "scope":"Existing rational engines, fixed coarse point; no new supplier root search."}


def stock():
    w,p=28416,28425;m=lcm(w,p)
    need((m,m//w,m//p)==(269241600,9475,9472),"live/physical compatibility reserve")
    widths=list(range(257))+[10**j+k for j in range(3,31) for k in (0,1,63)]
    checks=0
    for n in widths:
        d=depth(n)
        if n>=64:
            f=n//64
            for child in [r*f for r in range(1,43)]+[f//2]:
                if child:
                    need(depth(child)<=d-1,"fresh stock exponent sufficient")
                    need(0<child<n,"proper child")
                    checks+=1
        need(d<=2*(max(2,n)-1).bit_length(),"integer logarithmic depth envelope")
        f,delta=divmod(n,64)
        need(0<=delta<64 and 64*f+delta==n,"suffix-head peel")
        for i in range(delta):
            need(n-1-(64*f+i)==delta-1-i,"peeled head/tail pairing")
    return {"W":w,"P":p,"M":m,"M_over_W":m//w,"M_over_P":m//p,
            "width_cases":len(widths),"proper_child_checks":checks,
            "stock":"K^D(n), K=M*|GL64(F_q)|*q^(4096*(w-1))",
            "packet_volume_denominator":"W*|GL64(F_q)|"}


def plans(catalogue):
    counts=Counter();digest=sha256();pair_checks=0
    for rank in (1,7,42):
        request=next(r for r in catalogue.requests if r.base.rank==rank)
        root=Expression(3,2,141)
        for bad in (False,True):
            headers=[fixture_header(catalogue,request,3,2,bad=bad,high=t) for t in (0,1,2)]
            need(len({h.raw.low for h in headers})==1,"complete low-class plan domain")
            plan=residual_plan(root,request,headers[0].raw.low,catalogue)
            need(plan.branch==("fallback" if bad else "good"),"branch uses current low matrix")
            need(all(residual_plan(root,request,h.raw.low,catalogue)==plan for h in headers),
                 "one symbolic macroplan across high values")
            counts[plan.branch+"_plans"]+=1;counts[plan.branch+"_children"]+=len(plan.children)
            digest.update(canonical([(ch.kind,ch.first,ch.second,ch.expression.size)
                                     for ch in plan.children]).encode())
            if bad:
                incoming=BoundExpression(root,catalogue,FrozenFields(()))
                for h in headers:
                    prepared=prepare_fallback(incoming,h)
                    need(shape(prepared.operations)==plan.operations,"low plan equals full-ring operation shape")
                    pair_ops={op.target:op for op in prepared.operations
                              if op.kind=="swap" and op.coefficient.kind=="pair"}
                    for ch in plan.children:
                        if ch.kind!="pair" or ch.expression.path[-1].field not in (1,64,126):
                            continue
                        bound=BoundExpression(ch.expression,catalogue,FrozenFields.from_headers((h,)))
                        actual=build_weights(bound)[0]
                        expected=child_descriptor(prepared,pair_ops[ch.expression.path[-1].field])
                        need([actual.value(j) for j in range(actual.size)]==
                             [expected.value(j) for j in range(expected.size)],"symbolic fallback child binding")
                        pair_checks+=1
    return {"counts":dict(counts),"child_shape_sha256":digest.hexdigest(),
            "full_ring_pair_bindings":pair_checks,"high_field_recursive_splits":0}


def run(catalogue,root):
    return {"status":"PASS_RECURSIVE_INTERFACE_CHECKS",
            "caller":caller(catalogue),"plans":plans(catalogue),
            "stock":stock(),"moments":moments(catalogue,root)}

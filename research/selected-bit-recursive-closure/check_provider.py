"""Actual-label preparation, source guards and complete operator checks."""
from dataclasses import replace
from hashlib import sha256
import json

import descriptor as d
import ring_algebra as ring
from controlled_normalizer import schedule,coefficient as good_coefficient,child_weights
from fallback_program import reconstruct as fallback_reconstruct
from provider import (need,WeightRecipe,RawHeader,GeneralHeader,Chart,Base,
    fixture_header,raw_header,prepare_good,prepare_fallback,build_weights)
from expressions import Expression,BoundExpression,FrozenFields


def good_operator(form,column):
    m,f,modulus=form.n,form.f,form.modulus
    rows=ring.eye(2*m);before,after=schedule(m,form.rank,f)
    def apply(slots):
        for slot in slots:
            if slot[4]!=column:continue
            target,source=slot[1]//f,slot[2]//f
            c=good_coefficient(form,slot)
            if c:rows[target]=[(x+c*y)%modulus for x,y in zip(rows[target],rows[source])]
    apply(before)
    for k,pivot in enumerate(form.pivots):
        i,j=k,2*m-1-k;unit=form.weights[k*f+column]*pivot%modulus
        a,b=rows[i],rows[j]
        rows[i]=[unit*x%modulus for x in b]
        inverse=pow(unit,-1,modulus);rows[j]=[inverse*x%modulus for x in a]
    apply(after)
    return rows


def incoming_recipe(catalogue,q,width):
    copy=next(r for r in catalogue.requests if r.kind=="COPY" and r.old_frame==510)
    header=fixture_header(catalogue,copy,q,width,high=1)
    expression=Expression(q,width,2048).append("good",copy,header.raw.low,0)
    need(expression.size==224,"actual rank-seven incoming descriptor")
    return BoundExpression(expression,catalogue,FrozenFields.from_headers((header,)))


def check_all_bases(catalogue):
    cases=0
    for q,width in ((3,2),(5,2)):
        modulus=q**width
        for base in catalogue.bases.values():
            basis=base.basis(q,width)
            diagonal=[[int(i==j and i<base.rank) for j in range(64)] for i in range(64)]
            recovered=ring.conjugate(diagonal,basis,ring.inverse(basis,q,modulus),modulus)
            need(recovered==[list(row) for row in base.matrix(modulus)],"actual-label control basis")
            cases+=1
    chart_cases=0
    for chart in catalogue.charts:
        matrix=catalogue.chart_matrix(chart)
        need(all(x.denominator&(x.denominator-1)==0 for row in matrix for x in row),"dyadic selected owner chart")
        reduced=ring.reduce_matrix(matrix,9)
        need(ring.multiply(reduced,ring.transpose(reduced),9)==ring.eye(64),"assembled chart remains a unit")
        chart_cases+=1
    return {"full_64_coordinate_basis_cases":cases,"assembled_owner_charts":chart_cases}


def check_operators(catalogue):
    chosen=[]
    for rank in (1,2,3,4,5,6,7,42):
        chosen.append(next(r for r in catalogue.requests if r.base.rank==rank and
                           (r.kind=="IDLE" if rank==42 else r.kind=="MOVE")))
    chosen+= [next(r for r in catalogue.requests if r.kind=="COPY" and r.old_frame==frame)
              for frame in range(510,519)]
    chosen+= [next(r for r in catalogue.requests if r.kind=="MOVE" and r.chart.kind=="data" and r.stage==8),
              next(r for r in catalogue.requests if r.kind=="MOVE" and r.chart.kind=="host" and r.chart.port>=0),
              next(r for r in catalogue.requests if r.kind=="MOVE" and r.chart.kind=="host" and r.chart.port<0)]
    q,width=3,2;recipe=incoming_recipe(catalogue,q,width)
    weights,_=build_weights(recipe);f=weights.size//64
    digest=sha256();cases=0;good_slots=set()
    for request in chosen:
        for bad in (False,True):
            header=fixture_header(catalogue,request,q,width,bad=bad,high=1)
            direct=d.residual(header.direct_projector(),q**width)
            if bad:
                form=prepare_fallback(recipe,header)
                get=lambda j:fallback_reconstruct(form,j)
            else:
                form=prepare_good(recipe,header)
                before,after=schedule(64,request.base.rank,f)
                expected=2*(request.base.rank*(127-request.base.rank)+4096)*f
                need(len(before)+len(after)==expected and
                     all(slot[1]>slot[2] for slot in before+after),"one child and only ordered good ADDs")
                good_slots.add((request.base.rank,expected))
                get=lambda j:good_operator(form,j)
            for j in range(f):
                incoming=[weights.value(i*f+j) for i in range(64)]
                expected=d.weighted_residual(direct,incoming,q**width)
                actual=get(j)
                need(actual==expected,"full selected-label weighted operator")
                digest.update(json.dumps(actual,separators=(",",":")).encode())
                cases+=1
    return {"actual_requests":len(chosen),"atom_columns":f,
            "full_128_coordinate_operators":cases,"operator_sha256":digest.hexdigest(),
            "ordered_good_ADD_counts":[list(x) for x in sorted(good_slots)],
            "good_children_per_residual":1,"good_body_ordinary_calls":0}


def check_header_controls(catalogue):
    copy=next(r for r in catalogue.requests if r.kind=="COPY" and r.old_frame==510)
    header=fixture_header(catalogue,copy,3,2)
    correct=header.direct_projector()
    # A source already aligned to d must not receive its old owner chart again.
    doubled=replace(header,request=replace(copy,chart=copy.source_chart))
    wrong=doubled.direct_projector()
    need(wrong!=correct and sum(wrong[i][i] for i in range(64))%9==7,"double-owner-chart semantic witness")
    original=d.residual(correct,9);changed=d.residual(wrong,9)
    double_column=next(j for j in range(128) if any(original[i][j]!=changed[i][j] for i in range(128)))
    other=next(r for r in catalogue.requests if r.kind=="COPY" and r.old_frame==511)
    same_rank=replace(header,request=replace(copy,base=other.base))
    wrong_frame=d.residual(same_rank.direct_projector(),9)
    frame_column=next(j for j in range(128) if any(original[i][j]!=wrong_frame[i][j] for i in range(128)))
    try:
        bad=replace(header,raw=replace(header.raw,space="owner"))
        prepare_good(WeightRecipe(3,2,64),bad)
    except ValueError as error:
        need(str(error)=="owner/common header convention","header-space guard")
    else:
        raise ValueError("mislabelled private header accepted")
    equivalences=0
    for kind in ("data","host"):
        request=next(r for r in catalogue.requests if r.kind=="MOVE" and r.chart.kind==kind and
                     (r.stage>0 if kind=="data" else True))
        owner=fixture_header(catalogue,request,5,2)
        matrix=owner.raw.full(type("Counter",(),{"prefix_cells":0})())
        sigma=ring.reduce_matrix(catalogue.chart_matrix(request.chart),25)
        common=ring.multiply(matrix,sigma,25)
        alternate=replace(request,chart=Chart("identity"),header_space="common")
        view=GeneralHeader(raw_header(5,2,common,"common"),alternate,catalogue)
        need(owner.direct_projector()==view.direct_projector(),"owner and common formulations agree")
        equivalences+=1
    return {"double_owner_chart_witness_column":double_column,
            "same_rank_wrong_frame_witness_column":frame_column,
            "wrong_header_space":"REJECT","owner_common_equivalences":equivalences}


def run(catalogue):
    return {"status":"PASS_ACTUAL_SELECTED_RESIDUAL_PROVIDER","binding":catalogue.receipt(),
            "bases_and_charts":check_all_bases(catalogue),
            "operators":check_operators(catalogue),"controls":check_header_controls(catalogue)}

"""Actual selected labels drive completed physical leaf operations."""
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
import json

from provider import Catalogue,fixture_header,build_weights,need
from expressions import Expression,BoundExpression,FrozenFields
from leaf import execute_leaf,direct_leaf
from physical_stream import Layout


def labelled_recipes(catalogue,q,width):
    request=next(r for r in catalogue.requests if r.kind=="COPY" and r.old_frame==510)
    headers=[fixture_header(catalogue,request,q,width,high=t) for t in range(q**(width-1))]
    need(len({h.raw.low for h in headers})==1,"one actual-label low class")
    expression=Expression(q,width,512).append("good",request,headers[0].raw.low,0)
    need(expression.size==56,"rank-seven generated leaf extent")
    return tuple(BoundExpression(expression,catalogue,FrozenFields.from_headers((h,))) for h in headers)


def raw_records(layout,parents):
    records=parents*layout.unused*layout.rows
    need(records<2**layout.payload,"unique opaque leaf record labels")
    return [(i>>bit)&1 for i in range(records) for bit in range(layout.payload)]


def leaf_case(recipes,count,offset,unused,gap,payload,controls=False):
    q,width=recipes[0].q,recipes[0].width
    layout=Layout(count,1,q**width,unused,gap,payload)
    raw=raw_records(layout,len(recipes))
    actual,meter,_=execute_leaf(raw,recipes,count,offset,unused,gap,payload)
    expected=direct_leaf(raw,recipes,layout,offset)
    need(actual==expected,"full completed weighted leaf endpoint")
    rejected=[]
    if controls:
        for key in ("wrong_inverse","low_ancestors","omit_digit"):
            wrong,_,_=execute_leaf(raw,recipes,count,offset,unused,gap,payload,**{key:True})
            need(wrong!=expected,"weighted leaf control: "+key)
            rejected.append(key)
    movement=meter.movement
    return {"q":q,"width":width,"leaf_atoms":count,"weight_offset":offset,
        "parent_prefixes":len(recipes),"unused_classes":unused,"gap_classes":gap,
        "payload_bits":len(raw),"ordinary_atom_swaps":meter.ordinary_atom_swaps,
        "elementary_digit_swaps":meter.digit_swaps,"ordered_shifts":meter.ordered_shifts,
        "fixed_signs":meter.fixed_signs,"opaque_child_calls":meter.opaque_child_calls,
        "fixed_bucket_tapes":meter.max_bucket_tapes,
        "payload_reads":movement.payload_reads,"payload_writes":movement.payload_writes,
        "head_moves":movement.head_moves,"scratch_erases":movement.scratch_erases,
        "output_sha256":sha256(bytes(actual)).hexdigest(),"controls":rejected}


def mixed_recipe(catalogue,q=5,width=2,good_high=1):
    request=next(r for r in catalogue.requests if r.kind=="IDLE" and r.stage==6 and r.role==213)
    good=fixture_header(catalogue,request,q,width,high=good_high)
    bad=fixture_header(catalogue,request,q,width,bad=True,high=0)
    root=Expression(q,width,6400)
    first=root.append("good",request,good.raw.low,0)
    second=first.append("pair",request,bad.raw.low,1,field=1)
    need((first.size,second.size)==(4200,65),"mixed descriptor widths")
    return BoundExpression(second,catalogue,FrozenFields.from_headers((good,bad)))


def expression_controls(catalogue):
    recipes=labelled_recipes(catalogue,3,2)
    values=[]
    for recipe in recipes:
        weights,_=build_weights(recipe)
        values.append([weights.value(7),weights.value(8)])
        need(set(recipe.fields.reads)=={0},"only frozen ancestor field zero was read")
    need(values==[[1,1],[4,1],[7,1]],"same symbolic expression over varying high fields")
    mixed=[mixed_recipe(catalogue,good_high=t) for t in (1,2)]
    need(mixed[0].expression==mixed[1].expression,"one mixed expression over varying ancestors")
    mixed_values=[build_weights(r)[0].value(0) for r in mixed]
    need(mixed_values==[21,16],"mixed leaf retains the good ancestor")
    recipe=recipes[1]
    bad_node=replace(recipe.expression.path[0],high_slot=1)
    bad=replace(recipe,expression=replace(recipe.expression,path=(bad_node,)))
    try:
        build_weights(bad)
    except ValueError as error:
        need(str(error)=="causal ancestor field order","fresh-field rejection reason")
    else:
        raise ValueError("incoming weight read the current fresh matrix")
    two=mixed[0]
    early=replace(two.expression.path[0],high_slot=1)
    bad=replace(two,expression=replace(two.expression,path=(early,two.expression.path[1])))
    try:
        build_weights(bad)
    except ValueError as error:
        need(str(error)=="causal ancestor field order","later ancestor capture rejection")
    else:
        raise ValueError("an earlier ancestor read a later ancestor")
    low=[list(row) for row in two.expression.path[0].low_matrix]
    low[0][0]=(low[0][0]+1)%two.q
    early=replace(two.expression.path[0],low_matrix=tuple(map(tuple,low)))
    bad=replace(two,expression=replace(two.expression,path=(early,two.expression.path[1])))
    try:
        build_weights(bad)
    except ValueError as error:
        need(str(error)=="frozen header source binding","low-header provenance rejection")
    else:
        raise ValueError("ancestor low residue changed without its field binding")
    return {"one_expression_high_values":values,"mixed_expression_values":mixed_values,
            "fresh_field_control":"REJECT",
            "later_ancestor_capture_control":"REJECT","frozen_low_header_control":"REJECT",
            "unused_stock_accesses":0}


def run(catalogue):
    recipes=labelled_recipes(catalogue,3,2)
    empty=(BoundExpression(Expression(3,1,0),catalogue,FrozenFields(())),)
    roots=(BoundExpression(Expression(3,1,3,2),catalogue,FrozenFields(())),)
    return {"status":"PASS_COMPLETED_WEIGHTED_LEAVES",
        "symbolic_prefixes":expression_controls(catalogue),
        "cases":[leaf_case(empty,0,0,3,2,3),
                 leaf_case(roots,3,0,1,1,10),
                 leaf_case(recipes,2,7,2,2,17),
                 leaf_case((recipes[1],),1,0,2,3,11,True),
                 leaf_case((mixed_recipe(catalogue),),1,0,2,3,13,True)]}


if __name__=="__main__":
    print(json.dumps(run(Catalogue(Path.cwd())),indent=2))

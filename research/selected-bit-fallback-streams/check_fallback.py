"""Complete toy payload programs and selected mixed fallback operator checks."""
from collections import Counter
from dataclasses import replace
from hashlib import sha256
from itertools import product
import json
from math import gcd

from descriptor import identity, multiply, weighted_residual, require
from fallback_program import (Header, Ancestor, Prefix, prepare, coefficient,
    physical_atom, logical_column, shape, reconstruct, paid_children, annotated_reductions)
from controlled_stream import Tape, Meter, controlled_add
from physical_stream import Layout, execute, sign_pass, Execution


def header(q, width, matrix, axes):
    modulus = q**width
    return Header(q,width,
        tuple(tuple(x%modulus%q for x in row) for row in matrix),
        tuple(tuple((x%modulus)//q for x in row) for row in matrix),tuple(axes))


def small_prefix(q=3, width=2, columns=1, high=0, tail_parent=False):
    good = header(q,width,[[1,0,0],[0,1,1],[0,1,2]],(0,1))
    bad = header(q,width,[[q,q-1,0],[1,1,0],[0,0,1]],(0,))
    current = header(q,width,[[q,q-1],[1,1+q*high]],(0,))
    return Prefix(9*columns,1,
        (Ancestor("good",good),Ancestor("pair",bad,4 if tail_parent else 1,tail_parent)),current)


def selected_chart(blocks):
    h = identity(64)
    for i,j,a,b,c,d in blocks:
        h[i][i],h[i][j],h[j][i],h[j][j] = a,b,c,d
    order = list(range(22,64))+list(range(22))
    g = [[0]*64 for _ in range(64)]
    for i in range(64):
        for j, original in enumerate(order):
            g[i][original] = h[i][j]
    return g


def selected_prefix(q=5, width=2, mixed=False, high=0):
    axes = tuple(range(22,64))
    good = header(q,width,selected_chart([
        (0,43,1,1,q,1+q),(1,42,1,1,2*q,1+2*q),
        (25,44,1,1,3*q,1+3*q)]),axes)
    bad = header(q,width,selected_chart([(0,43,q,q-1,1,1),(1,42,1,0,1,1)]),axes)
    current = header(q,width,selected_chart([
        (0,43,q,q-1,1,1+q*high),(1,42,1,0,1,1)]),axes)
    ancestors = (Ancestor("good",good),)
    if mixed:
        ancestors += (Ancestor("pair",bad,1,False),)
    return Prefix(64*(100 if mixed else 5),1,ancestors,current)


def direct_matrix(form, column):
    weights = [form.weights.value(i*form.columns+column) for i in range(form.dimension)]
    return weighted_residual(form.matrix, weights, form.modulus)


def raw_payload(layout, parents):
    records = parents*layout.unused*layout.rows
    require(records < 2**layout.payload, "unique opaque record labels")
    return [(index>>bit)&1 for index in range(records) for bit in range(layout.payload)]


def direct_payload(raw, controls, layout):
    """One dense address-matrix action, independent of elimination instructions."""
    out = [None]*len(raw);m,f=layout.dimension,layout.columns
    for h, control in enumerate(controls):
        form = prepare(control)
        matrices = [direct_matrix(form,j) for j in range(f)]
        for stock,row in product(range(layout.unused),range(layout.rows)):
            values = layout.decode(row);destination=values[:]
            for j, matrix in enumerate(matrices):
                logical = [values[layout.axis(physical_atom(i,j,m,f))] for i in range(2*m)]
                transformed = [sum(a*x for a,x in zip(line,logical))%layout.modulus for line in matrix]
                for i,x in enumerate(transformed):
                    destination[layout.axis(physical_atom(i,j,m,f))] = x
            new_row=layout.encode(destination)
            src=((h*layout.unused+stock)*layout.rows+row)*layout.payload
            dst=((h*layout.unused+stock)*layout.rows+new_row)*layout.payload
            require(out[dst] is None,"direct payload oracle bijection")
            out[dst:dst+layout.payload]=raw[src:src+layout.payload]
    require(all(x is not None for x in out),"direct payload oracle coverage")
    return out


def physical_program(q,width,f,parents,gap,unused,payload,conversion_control=False):
    controls=tuple(small_prefix(q,width,f,t) for t in range(parents))
    layout=Layout(2,f,q**width,unused,gap,payload)
    raw=raw_payload(layout,parents)
    expected=direct_payload(raw,controls,layout)
    actual,execution=execute(raw,controls,layout)
    require(actual==expected,"complete mixed fallback physical program")
    require(actual!=raw,"nontrivial complete residual")
    if conversion_control:
        wrong,_=execute(raw,controls,layout,omit_reversal=True)
        require(wrong!=expected,"omitted physical orientation conversion")
    form=prepare(controls[0]);n=2*form.dimension
    classes=Counter()
    for op in form.operations:
        if op.kind=="lower":
            for j in range(f):
                c=coefficient(form,op.coefficient,j)
                classes["zero" if c==0 else "unit" if gcd(c,q)==1 else "nonunit"]+=1
    require(classes["zero"]>0 and classes["unit"]>0,"physical zero and unit slots")
    if width>1:
        require(classes["nonunit"]>0,"physical nonzero nonunit slot")
    require(len(execution.child_calls)<=6*n*(n-1)+3*n+6*(n-1),"retained fallback allowance")
    require(all(x["volume"]==len(raw) for x in execution.child_calls),"full-volume completed child calls")
    meter=execution.meter
    return {"q":q,"width":width,"atom_columns":f,"parent_headers":parents,
        "complete_address_rows_per_header":layout.rows,"unused_classes":unused,"gap_classes":gap,
        "payload_bits":len(raw),"input_weights":[form.weights.value(i) for i in range(form.weights.size)],
        "ordered_ADD_passes":execution.ordered_add_passes,"fixed_sign_passes":execution.fixed_sign_passes,
        "first_header_ADD_coefficient_classes":dict(sorted(classes.items())),
        "completed_child_calls":len(execution.child_calls),
        "child_width_histogram":dict(sorted(Counter(x["width"] for x in execution.child_calls).items())),
        "child_logical_volume":len(raw),"matrix_preparations":execution.matrix_preparations,
        "adapter_payload_reads":meter.payload_reads,"adapter_payload_writes":meter.payload_writes,
        "adapter_head_moves":meter.head_moves,"scratch_erases":meter.scratch_erases,
        "output_sha256":sha256(bytes(actual)).hexdigest(),
        "conversion_control":"REJECT" if conversion_control else "not applicable at f=1",
        "callee_scope":"Exact charged F_a oracles; sequential ADD/sign adapters are physical, child implementations remain a premise."}


def selected_operators():
    records=[];columns=0
    for q,width,mixed in ((3,2,False),(5,2,False),(5,2,True),(7,2,True)):
        prefix=selected_prefix(q,width,mixed)
        form=prepare(prefix);modulus=form.modulus
        require(form.matrix[0][0]%q==1,"bad projector gives residual entry I-P")
        require(multiply(form.matrix,form.matrix,modulus)==identity(128),"selected residual involution")
        digests=[]
        for j in range(form.columns):
            actual=reconstruct(form,j)
            require(actual==direct_matrix(form,j),"all selected mixed operator coefficients")
            digests.append(sha256(json.dumps(actual,separators=(",",":")).encode()).hexdigest())
            columns+=1
        widths=paid_children(form)
        require(max(widths)<=form.columns and len(widths)<=98682<131072,"selected fallback child allowance")
        require(sum(op.kind=="lower" for op in form.operations)==128*127,"retained zero/nonunit ADD slots")
        require(shape(form.operations)==shape(prepare(selected_prefix(q,width,mixed,1)).operations),
                "schedule independent of high lift")
        records.append({"q":q,"width":width,"mixed_ancestor":mixed,"columns":form.columns,
            "incoming_atoms":form.weights.size,"peeled_atoms":form.weights.size-64*form.columns,
            "shear_slots":16256,"weighted_swap_slots":sum(x.kind=="swap" for x in form.operations),
            "paid_children":len(widths),"operator_sha256":digests})
    return {"fixtures":records,"full_128_coordinate_operators":columns,
            "retained_fallback_allowance":98682,"selected_charged_allowance":131072}


def semantic_controls():
    form=prepare(small_prefix())
    require([form.weights.value(i) for i in range(2)]==[1,5],"actual mixed small weights")
    first=next(op for op in form.operations if op.kind=="lower" and op.coefficient.reduction_index==0)
    correct=-coefficient(form,first.coefficient,0)%9
    wrong=-coefficient(form,first.coefficient,0,True)%9
    require((correct,wrong)==(2,4),"intermediate-permutation coefficient witness")
    matrix=direct_matrix(form,0)
    require((matrix[1][0]+correct*matrix[0][0])%9==0 and
            (matrix[1][0]+wrong*matrix[0][0])%9==5,"wrong final permutation leaves uncleared entry")
    require(reconstruct(form,0,True)!=matrix,"wrong final permutation changes full residual")
    tail=prepare(small_prefix(tail_parent=True))
    require([tail.weights.value(i) for i in range(2)]==[2,1],"mixed tail ancestor orientation")

    selected=prepare(selected_prefix())
    slot=next(op for op in selected.operations if op.kind=="lower" and
              op.coefficient.reduction_index==16088)
    require((slot.target,slot.source,slot.coefficient.first,slot.coefficient.second)==(126,42,42,126),
            "selected upper shear physical lowering")
    logical=[coefficient(selected,slot.coefficient,j) for j in range(3)]
    physical=[coefficient(selected,slot.coefficient,logical_column(slot.target,t,64,3)) for t in range(3)]
    require(logical==[21,21,16] and physical==[16,21,21],"selected middle-lower orientation witness")
    prefix=selected_prefix();unused,middle,payload,modulus=2,2,13,25
    raw=[(i>>bit)&1 for i in range(unused*modulus*middle*modulus) for bit in range(payload)]
    def evaluate(control,wrong_orientation=False):
        current=prepare(control)
        current_slot=next(x for x in current.operations if x.kind=="lower" and x.coefficient.reduction_index==16088)
        field=current_slot.coefficient.first if wrong_orientation else current_slot.target
        c=coefficient(current,current_slot.coefficient,logical_column(field,0,64,3))
        return c,current.arithmetic
    actual=controlled_add(Tape(Meter(),raw),(prefix,),unused,modulus,middle,payload,evaluate)
    bad=controlled_add(Tape(Meter(),raw),(prefix,),unused,modulus,middle,payload,
                       lambda p:evaluate(p,True))
    expected=[None]*len(raw)
    for stock,x,z,y in product(range(unused),range(25),range(middle),range(25)):
        src=(((stock*25+x)*middle+z)*25+y)*payload
        dst=(((stock*25+x)*middle+z)*25+(y+16*x)%25)*payload
        expected[dst:dst+payload]=raw[src:src+payload]
    require(actual.bits==expected and bad.bits!=expected,"physical selected upper-shear orientation control")

    mixed_prefix=selected_prefix(mixed=True);mixed=prepare(mixed_prefix)
    low=prepare(mixed_prefix,low_only_ancestors=True)
    index=next(i for i,x in enumerate(mixed.operations) if x.kind=="lower" and
               coefficient(mixed,x.coefficient,0)!=coefficient(low,low.operations[i].coefficient,0))
    coefficients=[coefficient(p,p.operations[index].coefficient,0) for p in (mixed,low)]
    require(reconstruct(mixed,0)!=reconstruct(low,0),"low-only mixed ancestry changes full residual")
    require(index==381 and coefficients==[9,24],"selected mixed physical coefficient")
    def mixed_evaluate(control,low_only=False):
        current=prepare(control,low_only_ancestors=low_only)
        c=coefficient(current,current.operations[index].coefficient,0)
        return c,current.arithmetic
    mixed_actual=controlled_add(Tape(Meter(),raw),(mixed_prefix,),unused,modulus,middle,payload,mixed_evaluate)
    mixed_bad=controlled_add(Tape(Meter(),raw),(mixed_prefix,),unused,modulus,middle,payload,
                             lambda p:mixed_evaluate(p,True))
    # The two ancestor substitutions give A[43]=-1/11=9; low-only gives-1=24.
    for stock,x,z,y in product(range(unused),range(25),range(middle),range(25)):
        src=(((stock*25+x)*middle+z)*25+y)*payload
        dst=(((stock*25+x)*middle+z)*25+(y+9*x)%25)*payload
        expected[dst:dst+payload]=raw[src:src+payload]
    require(mixed_actual.bits==expected and mixed_bad.bits!=expected,
            "full mixed descriptor drives physical controlled ADD")
    return {"final_permutation_control":{"correct_first_coefficient":2,"wrong":4,"uncleared_entry":5},
        "small_mixed_weights":[1,5],"tail_parent_weights":[2,1],
        "selected_upper_shear":{"elimination_slot":16088,"logical":logical,"physical":physical,
                                "payload_bits":len(raw),"wrong_orientation":"REJECT"},
        "low_only_mixed_ancestry":{"instruction":index,"correct_and_wrong":coefficients,
                                   "physical_payload_bits":len(raw),"status":"REJECT"}}


def fixed_sign_check():
    layout=Layout(2,1,9,2,3,17);raw=raw_payload(layout,1)
    execution=Execution();axis=layout.axis(3)
    actual=sign_pass(Tape(execution.meter,raw),layout,axis,execution)
    expected=[None]*len(raw)
    for stock,row in product(range(layout.unused),range(layout.rows)):
        values=layout.decode(row);values[axis]=-values[axis]%9
        src=(stock*layout.rows+row)*layout.payload
        dst=(stock*layout.rows+layout.encode(values))*layout.payload
        expected[dst:dst+layout.payload]=raw[src:src+layout.payload]
    require(actual.bits==expected and actual.head==0,"fixed sign physical adapter")
    return {"payload_bits":len(raw),"passes":execution.fixed_sign_passes,"completed_children":0}


def build_result():
    return {"status":"PASS_SELECTED_MIXED_FALLBACK_STREAMS",
        "selected_operators":selected_operators(),"semantic_controls":semantic_controls(),
        "full_payload_programs":[physical_program(3,2,1,3,2,2,17),
                                 physical_program(3,1,2,1,1,1,13,True)],
        "fixed_sign":fixed_sign_check(),
        "scope":"Full mixed fallback descriptors and sequential adapters, with charged completed-child oracles; no full selected supplier or exponent admission."}


if __name__=="__main__":
    print(json.dumps(build_result(),indent=2))

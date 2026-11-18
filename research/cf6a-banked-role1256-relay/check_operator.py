#!/usr/bin/env python3
"""Replay every raw and banked normalized operator and CLEAR relation."""

import argparse
from dataclasses import replace
from fractions import Fraction
from functools import cache
import importlib.util
import json
from math import lcm
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("cf6a_relay_constructor", HERE / "construct.py")
source = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = source
spec.loader.exec_module(source)


def same_row(left, left_grid, right, right_grid):
    return left.keys() == right.keys() and all(
        value * right_grid == right[role] * left_grid for role,value in left.items())


def add_row(result, donor, factor):
    numerator, denominator = factor.numerator, factor.denominator
    if denominator == 1:
        for role,value in donor.items():
            total = result.get(role,0) + numerator*value
            if total:
                result[role] = total
            else:
                result.pop(role,None)
    else:
        for role,value in donor.items():
            term,remainder = divmod(numerator*value,denominator)
            if remainder:
                raise ValueError("exact integer pre-product division")
            total = result.get(role,0) + term
            if total:
                result[role] = total
            else:
                result.pop(role,None)


def exact_grid(graph, order):
    grids = {~r:1 for r in range(len(graph.initial))}
    for key in order:
        grids[key] = lcm(*(grids[donor]*factor.denominator for donor,factor in graph.forms[key].items()))
    return lcm(*grids.values())


def evaluate(graph, required=None):
    order = graph.schedule()
    if required is not None:
        relevant = set(required)
        for key in reversed(order):
            if key in relevant:
                relevant.update(graph.forms[key])
        order = [key for key in order if key in relevant]
    grid = exact_grid(graph,order)
    values = {~r:{r:grid} for r in range(len(graph.initial))}
    products = 0
    for key in order:
        result = {}
        for donor,factor in sorted(graph.forms[key].items()):
            add_row(result,values[donor],factor)
            products += len(values[donor])
        values[key] = result
    return grid,values,products


def weighted(row, values, common):
    denominator = lcm(*(value.denominator for value in row.values()))
    result = {}
    for token,weight in row.items():
        add_row(result,values[token],weight*denominator)
    return result,common*denominator


def smooth(value):
    value = abs(value)
    for prime in (2,3,5):
        while value % prime == 0:
            value //= prime
    return value == 1


@cache
def guarded_literal(literal, op):
    factor = source.rational(literal)
    nb, db = abs(factor.numerator).bit_length(),factor.denominator.bit_length()
    source.need(max(nb,db) <= 24 and smooth(factor.denominator)
                and (op != "SCALE" or smooth(factor.numerator)),
                "source bounded 2/3/5-smooth scalar literal")
    return factor,nb,db


def chronological_replay(word, certificates, banked_rows, banked_grid, monitors):
    """Direct chronological integer evaluation, without executing the folded forms."""
    grid = 225 << 14
    n = word["public"]
    fields = [{r:grid} for r in range(n)] + [None]*word["owned_fields"]
    charts = word["initial"][:] + [None]*word["owned_fields"]
    clear_rows = {entry.clock:entry for entry in monitors}
    products = clear_count = zero_count = moves = literals = 0
    max_num = max_den = 0
    for clock,event in enumerate(word["program"]):
        op,r,*args = event
        if op == "INIT":
            source.need(fields[r] is None and charts[r] is None and r >= n, "direct fresh private owner")
            charts[r],fields[r] = args[0],{}
            continue
        stored = fields[r]
        source.need(stored is not None, "direct active field")
        if op == "MOVE":
            a,b,owned = args
            source.need(charts[r] == a and owned == (r >= n)
                        and same_row(stored,grid,banked_rows[clock],banked_grid), f"raw paid observation {clock}")
            charts[r] = b
            moves += 1
            continue
        source.need(charts[r] == args[-1], "direct local operand chart")
        if op == "CLEAR":
            proof = clear_rows[clock]
            weights = {int(label):source.rational(value) for label,value in certificates[str(clock)].items()}
            source.need(r == proof.role and charts[r] == proof.chart
                        and all(label != r and fields[label] is not None for label in weights),
                        f"other live direct CLEAR witness at {clock}")
            rhs,rhs_unit = weighted(weights,fields,grid)
            source.need(same_row(stored,grid,rhs,rhs_unit),f"direct CLEAR equality at {clock}")
            lhs,lhs_unit = weighted(proof.left,banked_rows,banked_grid)
            source.need(same_row(stored,grid,lhs,lhs_unit),f"direct-bank CLEAR binding at {clock}")
            clear_count += 1
            zero_count += not stored
            charts[r],fields[r] = None,None
            continue
        if op == "SCALE":
            factor,nb,db = guarded_literal(args[0],op)
            result = {}
            add_row(result,stored,factor)
            products += len(stored)
            fields[r] = result
        else:
            donor,literal,_ = args
            source.need(op == "ADD" and donor != r and fields[donor] is not None
                        and charts[donor] == charts[r], "direct other cocharted ADD")
            factor,nb,db = guarded_literal(literal,op)
            add_row(stored,fields[donor],factor)
            products += len(fields[donor])
        literals += 1
        max_num,max_den = max(max_num,nb),max(max_den,db)
    source.need(moves == 6144 and clear_count == 235 and zero_count == 42 and literals == 148154,
                "direct raw operation and CLEAR denominator")
    source.need(charts[:n] == word["final"] and all(row is None for row in fields[n:]), "all public and private exits")
    first = len(word["program"])
    source.need(all(same_row(fields[r],grid,banked_rows[first+r],banked_grid) for r in range(n)),
                "direct and banked public operator equality")
    return {"grid":grid,"paid_move_observations":moves,"public_rows":n,"clear_relations":clear_count,
            "zero_clear_rows":zero_count,"nonzero_clear_rows":clear_count-zero_count,
            "literal_scalar_events":literals,"literal_bits":[max_num,max_den],"scalar_products":products}


def public_formula(word, grid):
    """The declared 400 main block ports and one own-input return for each helper."""
    values = [{r:grid} for r in range(word["public"])]
    hosted = word["hosted"]
    d_ports = set(hosted["Dports"])
    main = set(word["live"]) | {r+112 for r in word["live"]} | set(hosted["X2"]) | set(hosted["Y2"])
    source.need(len(main) == 400 and source.ROLE not in main and grid % 2 == 0,"all protected main slots")
    for ordinal,x in enumerate(word["live"]):
        y = x+112
        if ordinal in d_ports:
            values[y][x] = grid
        else:
            values[x][y] = -grid
            values[y] = {x:grid//2,y:grid//2}
    for x,y in zip(hosted["X2"],hosted["Y2"],strict=True):
        values[x][y] = -grid
    return values


def source_transpose(graph, forward, grid, reverse, reverse_grid):
    keys = range(graph.first,graph.first+len(graph.final))
    for key in keys:
        for coordinate,numerator in forward[key].items():
            source.need(numerator*reverse_grid ==
                        reverse[graph.first+coordinate].get(key-graph.first,0)*grid,
                        "computed dual equals exact public matrix transpose")
    source.need(sum(len(forward[k]) for k in keys) == sum(len(reverse[k]) for k in keys),
                "full transpose support")


def verify_clears(monitors, old, old_grid, new, new_grid):
    zero_count = 0
    observed = []
    for clear in monitors:
        old_left,lhs_grid = weighted(clear.left,old,old_grid)
        old_right,rhs_grid = weighted(clear.right,old,old_grid)
        new_left,cn_lgrid = weighted(clear.left,new,new_grid)
        new_right,cn_rgrid = weighted(clear.right,new,new_grid)
        source.need(same_row(old_left,lhs_grid,old_right,rhs_grid)
                    and same_row(new_left,cn_lgrid,new_right,cn_rgrid)
                    and same_row(old_left,lhs_grid,new_left,cn_lgrid),f"paired CLEAR relation {clear.clock}")
        zero_count += not old_left
        observed.append([clear.clock,clear.role,clear.chart,clear.born,clear.sources,
                         sorted((r,str(Fraction(v,lhs_grid))) for r,v in old_left.items())])
    source.need(len(observed) == 235 and zero_count == 42,"235 paired CLEAR relations with 42 exact zeros")
    return {"total":len(observed),"zero":zero_count,"nonzero":len(observed)-zero_count,
            "all_observation_sha256":source.digest(source.canonical(observed))}


def controls(word, certs, child, grid, rows, monitors):
    key = source.KEEP
    invalid_forms = {**child.forms,key:{token:-value for token,value in child.forms[key].items()}}
    bad = source.Graph(child.first,child.initial,child.final,child.moves,invalid_forms)
    bad_grid,bad_values,_ = evaluate(bad,required={key})
    source.need(not same_row(rows[key],grid,bad_values[key],bad_grid),"same-price wrong sign control")
    invalid_moves = {**child.moves,key:(source.RELAY,source.END)}
    try:
        source.Graph(child.first,child.initial,child.final,invalid_moves,child.forms).schedule()
    except ValueError as exc:
        source.need("same ordered chart" in str(exc),"wrong-source rejection reason")
    else:
        raise ValueError("wrong donor chart accepted")
    first = monitors[0]
    changed = {**certs,str(first.clock):{str(first.role):"1"}}
    try:
        source.raw_fold(word,changed)
    except ValueError as exc:
        source.need(str(exc) == f"other live CLEAR witness source at {first.clock}","self-reference rejection reason")
    else:
        raise ValueError("self-referencing CLEAR accepted")
    dirty = next(entry for entry in monitors if weighted(entry.left,rows,grid)[0])
    missing_relation = [replace(entry,right={}) if entry is dirty else entry for entry in monitors]
    try:
        verify_clears(missing_relation,rows,grid,rows,grid)
    except ValueError as exc:
        source.need(str(exc) == f"paired CLEAR relation {dirty.clock}","dirty erase rejection reason")
    else:
        raise ValueError("dirty CLEAR without its witness accepted")
    try:
        guarded_literal("1/7","ADD")
    except ValueError as exc:
        source.need(str(exc) == "source bounded 2/3/5-smooth scalar literal","raw grid control reason")
    else:
        raise ValueError("non-smooth raw literal accepted")
    return {"same_price_wrong_sign":"rejected","wrong_source_chart":"rejected",
            "self_clear":"rejected","dirty_clear_erasure":"rejected","denominator_7_raw_literal":"rejected"}


def check():
    word,certs,parent,child,monitors,mark,graphs = source.rebuild()
    base_grid,base_forward,base_work = evaluate(parent)
    base_dual_grid,base_dual,base_dual_work = evaluate(parent.transpose())
    grid,forward,work = evaluate(child)
    dual_grid,dual,dual_work = evaluate(child.transpose())
    source.need(len(parent.moves) == 6144 and len(child.moves) == 6143 and len(child.forms) == 7644,
                "literal learned paid and public denominators")
    for key in child.forms:
        source.need(same_row(base_forward[key],base_grid,forward[key],grid),f"forward stable row {key}")
        source.need(same_row(base_dual[key],base_dual_grid,dual[key],dual_grid),f"adjoint stable row {key}")
    expected = public_formula(word,grid)
    source.need(all(forward[child.first+r] == row for r,row in enumerate(expected)),"complete public block")
    source_transpose(parent,base_forward,base_grid,base_dual,base_dual_grid)
    source_transpose(child,forward,grid,dual,dual_grid)
    raw = chronological_replay(word,certs,base_forward,base_grid,monitors)
    clear = verify_clears(monitors,base_forward,base_grid,forward,grid)
    negative = controls(word,certs,child,grid,forward,monitors)
    return {
        "status":"PASS_CF6A_ROLE1256_EXACT_OPERATOR_CLEAR",
        "source_pr":7700,"source_head":source.SOURCE_HEAD,"source_word_sha256":source.WORD,
        "source_certs_sha256":source.CERTS,"caller_sha256":source.CALLER,"relay":mark,
        "decoded_graph_sha256":{name:source.digest(data) for name,data in graphs.items()},
        "raw_direct_replay":raw,"clear_replay":clear,"controls":negative,
        "exact_normalized_rows":{"paid_matched":len(child.moves),"public_matched":len(child.final),
                                 "both_orientations":True,"protected_main_ports":400},
        "banked_integer_grids":{"parent_forward":base_grid,"parent_adjoint":base_dual_grid,
                                "candidate_forward":grid,"candidate_adjoint":dual_grid},
        "banked_preproduct_counts":{"parent_forward":base_work,"parent_adjoint":base_dual_work,
                                    "candidate_forward":work,"candidate_adjoint":dual_work},
        "qualification_scope":"Raw normalized operator, banked forward and adjoint operator, and recorded 235 CLEAR relations",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path)
    args = parser.parse_args()
    result = check()
    if args.out:
        with args.out.open("xb") as stream:
            stream.write(source.canonical(result)+b"\n")
    print(result["status"],source.CHILD,flush=True)


if __name__=="__main__":
    main()

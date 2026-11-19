#!/usr/bin/env python3
"""Portable chronological replay of the paid #7781 GF(2) quotients."""
import argparse
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path


CONTACT = "0cfae4f0a7a47628f7ce45b5c11bcacbb2957592f5be511230434d7b7e8f0d37"
CANDIDATE = "c38f1881fa87f9b9e4a27e6ba8f4ce1a608a6d6ab014648bbe758d3c48a353d9"
ROOTED = "d3aa4426fa8fe7dc167270d01f2515184f2bff6a82744a14e941c5dd3afca27d"


def check(condition, message):
    if not condition:
        raise ValueError(message)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def mask(items):
    return sum(1 << i for i in items)


def transpose(edge, start, final, moves, rows):
    reverse = dict.fromkeys(rows, 0)
    for k, row in rows.items():
        for j in edge.indices(row):
            reverse[~j if j in start else j] ^= 1 << (~k if k < 0 else k)
    return final, start, {k:(b,a) for k,(a,b) in moves.items()}, reverse


def measure(edge, graph):
    start, _, _, rows = graph
    values = {r: 1 << r for r in start}
    for packet in edge.schedule(*graph):
        values[packet] = edge.combine(rows[packet], values)
    return values


def project(edge, graph, owners, replacements, bridge, redirected=None):
    start, final, moves, rows = graph
    old = measure(edge, graph)
    cut = mask(owners)
    removed = mask(replacements)
    for k, row in replacements.items():
        check(k in moves and not row & (cut|removed), "the replacement uses retained same-chart donors")
        check(not (old[k] ^ edge.combine(row,old)) & ~cut, "exact local projected identity")
    after = {k:(row & ~(cut|removed)) ^ edge.combine(row & removed,replacements)
             for k,row in rows.items() if k not in replacements and ~k not in owners}
    new_moves = {k:leg for k,leg in moves.items() if k not in replacements}
    for r, k in zip(owners,bridge,strict=True):
        check(k not in moves and r >= 222,"bridge reinstates one independent helper")
        new_moves[k] = start[r],final[r]
        after[k],after[~r] = 1 << r,1 << k
    for k,(route,source) in (redirected or {}).items():
        new_moves[k] = route
        after[k] = source
    result = start,final,new_moves,after
    forward = transpose(edge,*result)
    order = edge.schedule(*forward)
    edge.basis(forward[0],forward[2],forward[3],order)
    return result


def root_feedback(edge, source, witness, literal=None):
    check(edge.digest(source) == CANDIDATE and witness["program_sha256"] == ROOTED,
          "exact source and child for owner 411")
    trace = witness["trace"]
    init, final, legs, rows, clocks = edge.extract(source)
    graph = transpose(edge,init,final,legs,rows)
    _,_,moves,original = graph
    for key, item in trace["retire"].items():
        k = int(key)
        check(moves[k] == tuple(item["charts"]) and clocks[k] == item["clock"],"literal owner-411 retirement slot")
    bridge = trace["owner_bridge"]["label"]
    check(graph[0][411] == 1 and graph[1][411] == 509,"independent owner 411 return charts")
    mapping = {3298:1<<2329,2946:0}
    try:
        project(edge,graph,(411,),mapping,(bridge,))
    except ValueError as error:
        check(str(error)=="causal binary packet schedule","unrooted feedback fails the causal gate")
    else:
        raise ValueError("unrooted feedback control passed")
    replacements = {int(k):(tuple(v["after"]),mask(v["row"])) for k,v in trace["tree"].items()}
    check(len(replacements) == 3 and replacements ==
          {2329:((0,509),original[3298] & ~((1<<411)|(1<<2946))),
           2590:((509,390),1<<2329),2944:((390,517),1<<2590)},"rooted paid tree source equations")
    result = project(edge,graph,(411,),mapping,(bridge,),replacements)
    forward = transpose(edge,*result)
    word = edge.emit_word(source,*forward,edge.schedule(*forward))
    check(edge.digest(word) == ROOTED,"all repaired word bytes")
    if literal is None:
        return word, None

    root_row = replacements[2329][1]
    stack = list(edge.indices(root_row))
    ancestors = set()
    while stack:
        donor = stack.pop()
        if donor in ancestors:
            continue
        ancestors.add(donor)
        if donor in moves:
            stack.extend(edge.indices(original[donor]))
    check(not ancestors.intersection({2329,2590,2944,2946,3298}), "old producer has exterior ancestry")
    old_values, new_values = measure(edge, graph), measure(edge, result)
    restriction = 1 << 411
    check(old_values[3298] ^ old_values[2329] == old_values[2946] == restriction,
          "exact alias and pure owner coefficients")
    check(new_values[bridge] == restriction and all(new_values[k] == (old_values[k] & ~restriction)
          for k in result[2] if k != bridge), "every retained projected paid row")
    charts = literal.Charts(word["frames"])
    tree = (2329,2590,2944)
    tree_grades = [charts.leg(*result[2][k]) for k in tree]
    bridge_grade = charts.leg(*result[2][bridge])
    check(tree_grades == [4,2,1] and bridge_grade == 4, "nested tree and owner's bridge grades")
    old_grades = [charts.leg(*moves[k]) for k in (*tree,2946,3298)]
    from collections import Counter

    delta = Counter(old_grades)
    delta.subtract(tree_grades + [bridge_grade])
    credit = {grade: count for grade, count in delta.items() if count}
    check(credit == {1:1,3:1,4:-1}, "entire owner-411 signed rank delta")
    removed_donor = 3303
    check(root_row & (1 << removed_donor), "held-out original root donor")
    damaged_rows = result[3] | {2329:root_row ^ (1 << removed_donor)}
    damaged = transpose(edge, *result[:3], damaged_rows)
    try:
        edge.basis(damaged[0], damaged[2], damaged[3], edge.schedule(*damaged))
    except ValueError as error:
        check(str(error) == "complete binary public transfer", "omitting the root donor fails the full transfer")
    else:
        raise ValueError("root donor omission control passed")
    for adjoint in (False, True):
        rows_read, tape, _ = literal.tape(word, charts, adjoint=adjoint)
        check(rows_read == literal.expected_rows(word["public"], adjoint)
              and tape["erase_dirty"] == word["owned_fields"], "full operator and dirty retirement")
    return word, dict(parent_sha256=CANDIDATE, word_sha256=ROOTED, owner=411, old_alias_chart=509,
                      pure_packet=2946, tree_charts=[0,509,390,517], exact_tree_ranks=tree_grades,
                      grade_of_independent_owner_bridge=bridge_grade, strict_nested_tree=True,
                      old_exterior_producer_direct_terms=root_row.bit_count(),
                      old_exterior_producer_transitive_ancestors=len(ancestors), retained_paid_rows=len(result[2])-1,
                      arbitrary_coefficients_each_direction=word["public"]**2,
                      dirty_owned_erasures_each_direction=word["owned_fields"], signed_delta_by_rank=credit,
                      unrooted_control="causal binary packet schedule", omitted_old_producer_donor_rejected=removed_donor)


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--contact",type=Path,required=True,help="the eight-birth 680-owner contact word")
    cli.add_argument("--withdrawals",type=Path,required=True,help="the exact parallel-births-replay.json")
    cli.add_argument("--edge",type=Path,required=True,help="pinned bit_native.py from #7776")
    cli.add_argument("--literal",type=Path,help="independent binary literal replay inherited from #7781")
    cli.add_argument("--tree411",type=Path,help="optional rooted tree411-replay.json")
    cli.add_argument("--root-control-out",type=Path,help="rooted tree control receipt")
    cli.add_argument("--out",type=Path,required=True)
    args = cli.parse_args()
    check(sha256(args.edge.read_bytes()).hexdigest() ==
          "4368c62a5d42f81189d6776b8dba8c85a311b6a199b816244b545c6bb7d3dc1e", "native extractor identity")
    edge = load(args.edge,"native_edge")
    source = json.loads(gzip.decompress(args.contact.read_bytes()))
    check(edge.digest(source) == CONTACT, "exact contact predecessor")
    receipt = json.loads(args.withdrawals.read_bytes())
    check(receipt["program_sha256"] == CANDIDATE, "expected final word")
    trace = receipt["trace"]
    graph = transpose(edge,*edge.extract(source)[:4])
    graph = project(edge,graph,(432,),{int(k):mask(v) for k,v in trace["earlier_432_retirement"].items()},
                    (trace["earlier_432_paid_slot"],))
    graph = project(edge,graph,tuple(trace["selected"]),{int(k):mask(row["row"]) for k,row in trace["removed"].items()},
                    (row["label"] for row in trace["added"]))
    forward = transpose(edge,*graph)
    word = edge.emit_word(source,*forward,edge.schedule(*forward))
    check(edge.digest(word) == CANDIDATE, "canonical emitted word readout")
    literal = load(args.literal,"independent_literal") if args.literal else None
    if args.tree411:
        word, control = root_feedback(edge,word,json.loads(args.tree411.read_bytes()),literal)
        if args.root_control_out:
            check(control is not None, "root controls require the independent literal interpreter")
            args.root_control_out.write_text(json.dumps(control,sort_keys=True,indent=2)+"\n")
    elif literal is not None:
        frame = literal.Charts(word["frames"])
        for adjoint in (False,True):
            rows, _, _ = literal.tape(word,frame,adjoint=adjoint)
            check(rows == literal.expected_rows(word["public"],adjoint), "independent native endpoint and lifetimes")
    args.out.write_bytes(gzip.compress((json.dumps(word,separators=(",",":"))+"\n").encode(),mtime=0))
    print("PASS",edge.digest(word),word["public"])

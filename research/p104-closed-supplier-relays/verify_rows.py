#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Compare two serialized P104 native graphs by independent exact replay."""

import argparse
from collections import Counter
from dataclasses import dataclass, replace
from fractions import Fraction
from hashlib import sha256
from itertools import chain
from math import gcd, lcm
from pathlib import Path
from typing import NamedTuple
import gzip
import json


PARENT = "f30aece9bbf9da00a428e61bc489dde0278f604b7cfd9fb3b1d2707990af2647"
LAYOUT = "f1d44a8d0ff3578359892c2277161ace9f79fe6155a276bf461d4b33980fd347"
OWNERS = 1264
AXES = 4


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def encoded(value):
    return json.dumps(value,sort_keys=True,separators=(",", ":")).encode()


def read(path):
    raw = path.read_bytes()
    value = json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)
    return value, {"file":path.name, "bytes_sha256":sha256(raw).hexdigest(),
                   "content_sha256":sha256(encoded(value)).hexdigest()}


def chart_span(frame):
    span = {0}
    for axis in frame:
        require(type(axis) is int and 0 < axis < 512 and axis not in span,
                "Independent frame axes in the nine-dimensional ambient space")
        span.update({value ^ axis for value in span})
    return span


@dataclass(frozen=True)
class Graph:
    frames: list
    initial: tuple
    final: tuple
    first: int
    moves: dict
    forms: dict
    schedule: tuple

    @property
    def terminals(self):
        return range(self.first,self.first+len(self.initial))

    def source_chart(self, node):
        return self.moves[node][0] if node in self.moves else self.final[node-self.first]

    @classmethod
    def parse(cls, value):
        frames = value["frames"]
        initial,final = tuple(value["initial"]),tuple(value["final"])
        first = value["first_output"]
        require(len(initial) == len(final) == OWNERS and type(first) is int and first > 0,
                "Exact 1,264-owner public inventory")
        def valid_chart(index):
            return type(index) is int and 0 <= index < len(frames)

        require(all(map(valid_chart,chain(initial,final))), "Public chart IDs")
        moves = {}
        for key,a,b in value["moves"]:
            require(type(key) is int and 0 <= key < first and key not in moves and valid_chart(a) and valid_chart(b),
                    "Unique paid key and real chart IDs")
            moves[key] = a,b
        forms = {}
        for node,literals in value["forms"]:
            require(type(node) is int and node not in forms, "Unique form key")
            row = {}
            for donor,literal in literals:
                require(type(donor) is int and donor not in row and type(literal) is str, "Unique rational donor")
                q = Fraction(literal)
                require(q != 0, "No zero coefficient in sparse form")
                row[donor] = q
            forms[node] = tuple(row.items())
        schedule = tuple(value["schedule"])
        require(forms.keys() == (moves.keys() | set(range(first,first+OWNERS))), "Exact paid and terminal form inventory")
        require(len(schedule) == len(forms) and all(type(i) is int for i in schedule)
                and set(schedule) == forms.keys(), "Complete schedule with every form once")
        result = cls(frames,initial,final,first,moves,forms,schedule)
        result.check_order()
        return result

    def check_order(self):
        charts = {~i:c for i,c in enumerate(self.initial)}
        for node in self.schedule:
            source = self.source_chart(node)
            for donor,_ in self.forms[node]:
                require(donor in charts, f"Read before return at form {node}, donor {donor}")
                require(charts[donor] == source, f"Wrong donor chart at form {node}, donor {donor}")
            if node in self.moves:
                require(node not in charts, "Repeated paid return")
                charts[node] = self.moves[node][1]


def public_operator(graph, layout, spans):
    roles = layout["live"]
    h = layout["hosted"]
    hosted = set(h["Dports"])
    required = [{i:Fraction(1)} for i in range(OWNERS)]
    mains = set()
    require(layout["frames"] == graph.frames and len(roles) == len(layout["ports"]) == 104
            and len(set(layout["ports"])) == 104, "Public chart table and 104 distinct real ports")
    require(len(hosted) == 96 and hosted <= set(range(len(roles))), "96 A ports and eight B ports")
    require(len(h["X2"]) == len(h["Y2"]) == len(hosted), "All secondary pairs")
    for i,(x,axis) in enumerate(zip(roles,layout["ports"],strict=True)):
        y = x+112
        mains.update((x,y))
        require(spans[graph.initial[x]] == {0,axis} and spans[graph.initial[y]] == {0}
                and len(spans[graph.final[x]]) == 512
                and spans[graph.final[y]] == {v for v in range(512) if (v & axis).bit_count()%2 == 0},
                f"Complete primary chart boundary for port {i}")
        if i in hosted:
            required[y][x] = Fraction(1)
        else:
            required[x][y] = Fraction(-1)
            required[y] = {x:Fraction(1,2),y:Fraction(1,2)}
    for i,x,y in zip(h["Dports"],h["X2"],h["Y2"],strict=True):
        mains.update((x,y))
        u = roles[i]
        require(all(boundary[a] == boundary[b] for a,b in ((x,u),(y,u+112))
                    for boundary in (graph.initial,graph.final)), "Complete secondary chart boundary")
        required[x][y] = Fraction(-1)
    require(len(mains) == 400 and mains <= set(range(OWNERS)), "400 distinct mains and 864 independent helpers")
    return required,mains


def charge_inventory(graph, mains, spans):
    paid = Counter()
    for a,b in graph.moves.values():
        require(spans[a] < spans[b] or spans[b] < spans[a], "Strictly nested paid transfer charts")
        paid[abs(len(graph.frames[a])-len(graph.frames[b]))] += 1
    targets = Counter()
    for r,(a,b) in enumerate(zip(graph.initial,graph.final,strict=True)):
        if r not in mains:
            require(spans[a] < spans[b], f"Positive same-owner helper at role {r}")
            targets[len(graph.frames[b])-len(graph.frames[a])] += 1
    return dict(paid),dict(targets)


def combine(terms):
    """Sum rational vectors with one exact integer denominator per stored row."""
    scaled = [(row, coefficient.numerator, denominator*coefficient.denominator)
              for (denominator,row),coefficient in terms if row]
    denominator = lcm(*(d for _,_,d in scaled))
    total = {}
    for row,n,d in scaled:
        weight = n*(denominator//d)
        for key,num in row.items():
            total[key] = total.get(key,0)+weight*num
    result = {k:v for k,v in total.items() if v}
    common = gcd(denominator,*result.values())
    if common > 1:
        return denominator//common,{k:v//common for k,v in result.items()}
    return denominator,result


def unpack(row):
    denominator,coefficients = row
    return {k:Fraction(v,denominator) for k,v in coefficients.items()}


def forward(graph, watch=()):
    current = {~i:(1,{i:1}) for i in range(OWNERS)}
    outputs = [None] * OWNERS
    for node in graph.schedule:
        out = combine((current[donor],q) for donor,q in graph.forms[node])
        if node in graph.moves:
            current[node] = out
        else:
            outputs[node-graph.first] = unpack(out)
    return outputs,{node:unpack(current[node]) for node in watch}


def backward(graph, watch=()):
    """Reverse-accumulate independent terminal covectors directly on the edge list."""
    pending = {node:[((1,{i:1}),Fraction(1))] for i,node in enumerate(graph.terminals)}
    watched = {}
    for node in reversed(graph.schedule):
        dependency = combine(pending.pop(node,()))
        if node in watch:
            watched[node] = unpack(dependency)
        if dependency[1]:
            for donor,q in graph.forms[node]:
                pending.setdefault(donor,[]).append((dependency,q))
    return [unpack(combine(pending.get(~i,()))) for i in range(OWNERS)],watched


def matrix_transpose(rows):
    ans = [{} for _ in rows]
    for i,row in enumerate(rows):
        for j,coef in row.items():
            ans[j][i] = coef
    return ans


def endpoint_digest(rows):
    return sha256(encoded([[[j,str(q)] for j,q in sorted(row.items())] for row in rows])).hexdigest()


class Payload(NamedTuple):
    owner: object
    chart: int | None
    cells: tuple


BLANK = Payload(None,None,(0,)*AXES)


class Bank:
    """Guarded numerical homes with an explicit, value-independent extent clear."""

    def __init__(self, homes):
        self.slots = [Payload(None,None,tuple((i+1)*(j+2) for j in range(AXES))) for i in range(homes)]
        self.head = None
        self.guards = (object(),object())
        self.original_guards = self.guards
        self.cleared = 0

    def select(self, slot):
        require(self.head is None and type(slot) is int and 0 <= slot < len(self.slots), "Guarded home access")
        self.head = slot

    def clear(self, slot, extent=AXES):
        self.select(slot)
        try:
            require(0 <= extent <= AXES, "CLEAR within the addressed extent")
            old = self.slots[slot]
            self.slots[slot] = Payload(None,None,tuple(0 if k<extent else cell for k,cell in enumerate(old.cells)))
            self.cleared += extent
        finally:
            self.head = None

    def install(self, slot, payload):
        self.select(slot)
        try:
            require(self.slots[slot] == BLANK, "Write into a dirty or occupied home")
            require(len(payload.cells) == AXES, "A complete staged payload")
            self.slots[slot] = payload
        finally:
            self.head = None

    def load(self, slot, owner, chart):
        self.select(slot)
        try:
            held = self.slots[slot]
            require(held.owner == owner and held.chart == chart, "Exact owner and chart from held home")
            return held.cells
        finally:
            self.head = None

    def retired(self):
        return self.head is None and self.guards is self.original_guards and all(cell == BLANK for cell in self.slots)


def controls_reject(action, reason):
    try:
        action()
    except ValueError as exc:
        require(str(exc).startswith(reason), f"Mutation rejected by unrelated check: {exc}")
        return True
    raise ValueError(f"Counterfactual accepted: {reason}")


def dirty_extent_control():
    bank = Bank(2)
    neighbor = bank.slots[1]
    bank.clear(0,AXES-1)
    require(bank.slots[0].cells[:-1] == (0,)*(AXES-1) and bank.slots[0].cells[-1], "Dirty last addressed cell")
    replacement = Payload("fresh",0,(1,)*AXES)
    rejected = controls_reject(lambda:bank.install(0,replacement), "Write into a dirty or occupied home")
    bank.clear(0)
    bank.install(0,replacement)
    require(bank.load(0,"fresh",0) == (1,)*AXES and bank.slots[1] == neighbor and bank.head is None,
            "Full clear admits replacement and preserves neighbor and head")
    return {"partial_clear_rejected":rejected,"neighbor_unchanged":True,"guarded_head_restored":True}


def held_replay(graph, target):
    """Hold old public inputs, complete each return, and explicitly retire every home."""
    k = len(graph.moves)
    arrivals = {node:OWNERS+i for i,node in enumerate(sorted(graph.moves))}
    sender = 2*OWNERS+k
    scratch = range(sender+1,sender+5)
    accumulator,donor_home,product_home,quotient_home = scratch
    bank = Bank(sender+5)
    old_public = tuple(tuple((-1)**(r+j)*(7*r+3*j+1) for j in range(AXES)) for r in range(OWNERS))
    public = list(old_public)
    for slot in range(sender+5):
        bank.clear(slot)
    for role,cells in enumerate(public):
        bank.install(role,Payload(~role,graph.initial[role],cells))
    parked_rejected = False

    for node in graph.schedule:
        source = graph.source_chart(node)
        sums = (0,)*AXES
        for donor,q in graph.forms[node]:
            home = ~donor if donor < 0 else arrivals[donor]
            cells = bank.load(home,donor,source)
            bank.install(donor_home,Payload(node,source,cells))
            products = tuple(q.numerator*x for x in bank.load(donor_home,node,source))
            bank.install(product_home,Payload(node,source,products))
            quotients = tuple(Fraction(x,q.denominator) for x in bank.load(product_home,node,source))
            bank.install(quotient_home,Payload(node,source,quotients))
            sums = tuple(a+b for a,b in zip(sums,bank.load(quotient_home,node,source),strict=True))
            for slot in (donor_home,product_home,quotient_home):
                bank.clear(slot)
        bank.install(accumulator,Payload(node,source,sums))
        held_sum = bank.load(accumulator,node,source)
        if node in graph.moves:
            bank.install(sender,Payload(node,source,held_sum))
            if not parked_rejected:
                counterfactual = Payload(node+1,source,held_sum)
                parked_rejected = controls_reject(lambda:bank.install(sender,counterfactual),
                                                   "Write into a dirty or occupied home")
                require(bank.slots[arrivals[node]] == BLANK, "No returned value before completion")
            returned = bank.load(sender,node,source)
            bank.install(arrivals[node],Payload(node,graph.moves[node][1],returned))
            bank.clear(sender)
        else:
            stage = OWNERS + k + node-graph.first
            bank.install(stage,Payload(node,source,held_sum))
        bank.clear(accumulator)

    require(tuple(public) == old_public and all(
        bank.load(role,~role,graph.initial[role]) == cells for role,cells in enumerate(old_public)),
        "Original public values and immutable homes preserved until final install")
    for role,row in enumerate(target):
        node = graph.first+role
        staged = bank.load(OWNERS+k+role,node,graph.final[role])
        expected = tuple(sum(q*old_public[i][j] for i,q in row.items()) for j in range(AXES))
        require(staged == expected, f"Same-owner held output at role {role}")
        public[role] = staged
    for slot in range(sender+5):
        bank.clear(slot)
    require(parked_rejected and bank.retired(), "Retired complete homes, guards and live sender")
    count = AXES*(2*(sender+5)+k+len(graph.schedule)+3*sum(map(len,graph.forms.values())))
    require(bank.cleared == count, "All scheduled extent addresses were overwritten")
    return {"homes":sender+5,"cells_per_home":AXES,"addressed_cells_cleared":bank.cleared,
            "same_owner_installs":len(public),"guards_and_homes_restored":True,
            "parked_sender_alias_rejected":True,"public_preserved_until_install":True}


def mutated_form(graph, node, row):
    return replace(graph, forms={**graph.forms,node:row})


def cycle_control(graph):
    by_pair = {pair:node for node,pair in graph.moves.items()}
    pair = next(((node,by_pair[b,a]) for node,(a,b) in graph.moves.items() if (b,a) in by_pair),None)
    require(pair is not None, "Available counterfactual same-chart two-cycle")
    a,b = pair
    cycle = replace(graph,forms={**graph.forms,a:((b,Fraction(1)),),b:((a,Fraction(1)),)})
    return {"nodes":pair,"cycle_rejected":controls_reject(cycle.check_order,"Read before return")}


def changed_paid_control(graph, paid_changed, entry, exit_, target, target_t):
    node = next((k for k in paid_changed if entry[k] and exit_[k]),None)
    require(node is not None, "A changed paid form with nonzero entrance and terminal influence")
    changed = mutated_form(graph,node,tuple((donor,-q) for donor,q in graph.forms[node]))
    changed.check_order()
    forward_fault,_ = forward(changed)
    backward_fault,_ = backward(changed)
    diff = [r for r,(a,b) in enumerate(zip(forward_fault,target,strict=True)) if a != b]
    diff_t = [r for r,(a,b) in enumerate(zip(backward_fault,target_t,strict=True)) if a != b]
    require(diff and diff_t and matrix_transpose(forward_fault) == backward_fault,
            "Both independently computed orientations reject changed paid sign")
    return {"paid_node":node,"changed_terminal_rows":diff,"changed_transposed_rows":diff_t}


def summary(graph, pin, mains, spans, outputs, adjoints, target):
    paid,productive = charge_inventory(graph,mains,spans)
    return {**pin, "public":OWNERS,"mains":len(mains),"helpers":OWNERS-len(mains),"paid_moves":len(graph.moves),
            "recorded_acyclic_schedule":True,"forms":len(graph.forms),"terms":sum(map(len,graph.forms.values())),
            "paid_ranks":paid,"productive_ranks":productive,"forward_rows":len(outputs),
            "transposed_rows":len(adjoints),"forward_sha256":endpoint_digest(outputs),
            "transpose_sha256":endpoint_digest(adjoints),"held_clear":held_replay(graph,target)}


def verify(parent_path, candidate_path, layout_path, candidate_pin):
    parent_raw,parent_id = read(parent_path)
    candidate_raw,candidate_id = read(candidate_path)
    layout,layout_id = read(layout_path)
    require(parent_id["content_sha256"] == PARENT and candidate_id["content_sha256"] == candidate_pin
            and layout_id["content_sha256"] == LAYOUT, "Canonical parent, candidate and layout pins")
    parent,candidate = Graph.parse(parent_raw),Graph.parse(candidate_raw)
    require((parent.frames,parent.initial,parent.final,parent.first) ==
            (candidate.frames,candidate.initial,candidate.final,candidate.first), "Identical public charts, order and namespace")
    require(len(parent.moves) == 5720, "Published f30 paid transfer inventory")
    spans = [chart_span(f) for f in parent.frames]
    expected,mains = public_operator(parent,layout,spans)
    expected_t = matrix_transpose(expected)
    watched = sorted(k for k in candidate.moves if candidate.moves[k] != parent.moves.get(k)
                     or candidate.forms[k] != parent.forms.get(k))

    left,_ = forward(parent)
    left_t,_ = backward(parent)
    right,inputs = forward(candidate,watched)
    right_t,outputs = backward(candidate,set(watched))
    require(left == right == expected, "Both graph forward maps equal the fixed arbitrary-owner operator")
    require(left_t == right_t == expected_t, "Both graph reverse maps equal the fixed transposed operator")
    parent_report = summary(parent,parent_id,mains,spans,left,left_t,expected)
    candidate_report = summary(candidate,candidate_id,mains,spans,right,right_t,expected)
    require(parent_report["productive_ranks"] == candidate_report["productive_ranks"], "Productive rank histogram conserved")
    return {"schema":"p104-independent-native-rows/1","parent":parent_report,"candidate":candidate_report,
            "checker_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
            "layout":layout_id,"same_complete_endpoint_operators":True,
            "recorded_paid_changes":{"removed":sorted(parent.moves.keys()-candidate.moves.keys()),
                                    "used_changed_forms":watched},
            "fault_controls":{"paid_coefficient_sign":changed_paid_control(candidate,watched,inputs,outputs,
                                                                            expected,expected_t),
                              "causal_cycle":cycle_control(candidate),"dirty_tail_clear":dirty_extent_control()},
            "scope":"Exact normalized rational endpoint operators, chart/owner causality, and finite held-CLEAR fixture."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parent",type=Path)
    parser.add_argument("candidate",type=Path)
    parser.add_argument("layout",type=Path)
    parser.add_argument("--candidate-sha256",required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    report = verify(args.parent,args.candidate,args.layout,args.candidate_sha256)
    args.output.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print(json.dumps({k:report[k]["content_sha256"] for k in ("parent","candidate")}))


if __name__ == "__main__":
    main()

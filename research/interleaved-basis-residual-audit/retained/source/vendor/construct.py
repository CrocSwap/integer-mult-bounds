#!/usr/bin/env python3
"""Rebuild the exact banked #7700 graph and its role-1256 relay contraction."""

import argparse
from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from graphlib import TopologicalSorter
import gzip
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
SOURCE_HEAD = "7d84799a447867d36137d12ef7ca5646154d763c"
WORD = "ae62d5d8bef6f7146454b4b3643e487a58380c606a16c5baef7bf0dcf9df1472"
CERTS = "39ef28b708cd8bf1166b111d656809407b370dd11cd81a8e43820779f995aca3"
CALLER = "62d94fb992acab0a71c3d12f22be4ce63f4f65e5cbe3f420b93aa1393ffa8dcf"
DONOR_HEAD = "28b2af322a1fab01b3734365988930920f9dda48"
PARENT = "72705b094d83d2ba24006661bbb031786a691b776bedb94515b1321e1535105f"
CHILD = "8e7b755bd2d2d387bc3d3adfe48100985adf74775ca5acbb143170a3d16b5ccf"
PINS = {
    "WORD.json.gz": ("50c1facfc5626c060560e2f354b71bd92d0bb1c1e853b2aad72abcbaaa5328a5", WORD),
    "CERTS.json": (CERTS, CERTS),
    "CALLER.json.gz": ("d889996a337f648087208ab51c98eaf052705d4fca88b5d01b6e9257a829897a", CALLER),
    "PARENT-GRAPH.json.gz": ("c86288cddb4b80af3c8128c9a0d2f7a1e82bae64c5152a0d96a19d166afaab1d", PARENT),
    "CANDIDATE-GRAPH.json.gz": ("0177c25371181e3b1f2c13325eb8434fbf6384a9ab99a612849efd5d0f6ab2cc", CHILD),
}
REMOVE = 95828
KEEP = 104442
ROLE = 1256
START, RELAY, END = (476, 878, 127)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(raw):
    return sha256(raw).hexdigest()


def read(name):
    path = DATA / name
    packed = path.read_bytes()
    packed_sha, raw_sha = PINS[name]
    need(digest(packed) == packed_sha, f"transport hash of {name}")
    raw = gzip.decompress(packed) if path.suffix == ".gz" else packed
    need(digest(raw) == raw_sha, f"decoded hash of {name}")
    return raw


@cache
def rational(literal):
    number = Fraction(literal)
    need(number and str(number) == literal, "reduced nonzero rational literal")
    return number


def accumulate(row, source, factor):
    for token, value in source.items():
        total = row.get(token, 0) + factor * value
        if total:
            row[token] = total
        else:
            row.pop(token, None)


@dataclass
class Graph:
    """Every paid result is a distinct stable token. Terminals are never donors."""

    first: int
    initial: list
    final: list
    moves: dict
    forms: dict

    def schedule(self):
        terminals = set(range(self.first, self.first + len(self.final)))
        need(self.forms.keys() == terminals | self.moves.keys(), "complete paid and public forms")
        dependencies = {}
        for key in sorted(self.forms):
            source = self.moves[key][0] if key in self.moves else self.final[key - self.first]
            dependencies[key] = []
            for donor in sorted(self.forms[key]):
                if donor >= 0:
                    need(donor in self.moves and self.moves[donor][1] == source,
                         f"same ordered chart for paid donor at {key}")
                    dependencies[key].append(donor)
                else:
                    role = ~donor
                    need(0 <= role < len(self.initial) and self.initial[role] == source,
                         f"same ordered chart for input donor at {key}")
        return list(TopologicalSorter(dependencies).static_order())

    def transpose(self):
        def reverse(node):
            if node < 0:
                return self.first + ~node
            if node >= self.first:
                return ~(node - self.first)
            return node

        rows = {key: {} for key in self.moves}
        rows.update({self.first + r: {} for r in range(len(self.initial))})
        for key, row in self.forms.items():
            for donor, weight in row.items():
                rows[reverse(donor)][reverse(key)] = weight
        return Graph(self.first, self.final, self.initial,
                     {key: (b, a) for key, (a, b) in self.moves.items()}, rows)


@dataclass
class Clear:
    clock: int
    role: int
    chart: int
    born: int
    left: dict
    right: dict
    sources: list


def raw_fold(word, certificates):
    """Apply the attributed #7674 folding rule and capture both CLEAR sides."""
    n = word["public"]
    start, end, program = word["initial"], word["final"], word["program"]
    first = len(program)
    capacity = n + word["owned_fields"]
    need(n == len(start) == len(end) == 1501 and first == 154768 and capacity == 1569,
         "exact raw denominator")
    rows = [{~r: Fraction(1)} for r in range(n)] + [None] * word["owned_fields"]
    charts = start[:] + [None] * word["owned_fields"]
    active, moves, forms, raw_moves = {}, {}, {}, {}
    witnesses = []
    peak = 0
    for clock, event in enumerate(program):
        op, role, *args = event
        need(type(role) is int and 0 <= role < capacity, "literal raw owner label")
        if op == "INIT":
            need(n <= role and role not in active and rows[role] is None, "new private owner")
            need(0 <= args[0] < len(word["frames"]), "valid INIT chart")
            charts[role] = args[0]
            rows[role] = {}
            active[role] = clock
            peak = max(peak, len(active))
            continue
        row = rows[role]
        need(row is not None, "current live field")
        if op == "MOVE":
            a, b, owned = args
            need(type(owned) is bool and owned == (role >= n) and a == charts[role]
                 and 0 <= b < len(word["frames"]), "literal owner and MOVE charts")
            moves[clock], forms[clock] = (a, b), row
            raw_moves[clock] = [role, a, b, owned, active.get(role)]
            charts[role], rows[role] = b, {clock: Fraction(1)}
            continue
        need(charts[role] == args[-1], "literal scalar chart")
        if op == "CLEAR":
            need(role in active and str(clock) in certificates, f"certified private retirement {clock}")
            relation = {}
            sources = []
            for label, literal in sorted(certificates[str(clock)].items(), key=lambda item: int(item[0])):
                field = int(label)
                need(0 <= field < capacity and field != role and rows[field] is not None,
                     f"other live CLEAR witness source at {clock}")
                factor = rational(literal)
                accumulate(relation, rows[field], factor)
                sources.append([field, charts[field], str(factor)])
            witnesses.append(Clear(clock, role, charts[role], active.pop(role), row, relation, sources))
            charts[role], rows[role] = None, None
        elif op == "SCALE":
            factor = rational(args[0])
            rows[role] = {token: coefficient * factor for token, coefficient in row.items()}
        else:
            donor, literal, _ = args
            need(op == "ADD" and 0 <= donor < capacity and donor != role
                 and rows[donor] is not None and charts[donor] == charts[role], "other cocharted ADD")
            accumulate(row, rows[donor], rational(literal))
    need(charts[:n] == end and all(value is None for value in charts[n:]) and not active,
         "same public exit and complete private retirement")
    need(peak == 51 and len(moves) == 6144 and len(witnesses) == len(certificates) == 235,
         "complete native MOVE and CLEAR custody")
    forms.update({first + r: rows[r] for r in range(n)})
    return Graph(first, start, end, moves, forms), witnesses, raw_moves


def span(basis):
    values = {0}
    for axis in basis:
        need(type(axis) is int and 0 < axis < 512 and axis not in values,
             "independent binary ordered chart")
        values |= {axis ^ value for value in values}
    return values


def contract(source, atlas, witnesses, raw_moves):
    a, c, b = START, RELAY, END
    need(raw_moves[REMOVE] == [ROLE,a,c,False,None] and raw_moves[KEEP] == [ROLE,c,b,False,None],
         "literal route anchors and owner")
    need(source.moves[REMOVE] == (a,c) and source.moves[KEEP] == (c,b)
         and source.forms[KEEP] == {REMOVE: Fraction(1)}, "pure relay at the anchored paid reader")
    readers = [key for key,row in source.forms.items() if REMOVE in row]
    need(readers == [KEEP] and all(REMOVE not in clear.left and REMOVE not in clear.right for clear in witnesses),
         "sole reader and no original CLEAR incidence")
    basis_a,basis_c,basis_b = (atlas[x] for x in (a,c,b))
    need(span(basis_a) < span(basis_c) < span(basis_b)
         and tuple(map(len,(basis_a,basis_c,basis_b))) == (3,6,9), "positive 3+3→6 chart nesting")
    marks = {
        "remove":REMOVE,"keep":KEEP,"charts":[a,c,b],"ranks":[3,3,6],"scale":"1",
        "removed_raw_move":raw_moves[REMOVE],"surviving_raw_move_before":raw_moves[KEEP],
        "direct_pair_already_paid":(a,b) in source.moves.values(),
        "all_readers_of_removed":readers,"raw_clear_use_of_removed":False,
    }
    forms,moves = dict(source.forms),dict(source.moves)
    forms[KEEP] = forms.pop(REMOVE)
    del moves[REMOVE]
    moves[KEEP] = (a,b)
    return Graph(source.first,source.initial,source.final,moves,forms),marks


def serialized(graph, frames, kind, **extra):
    metadata = {
        "schema":"p104-exact-banked-dag/v1","kind":kind,"source_pr":7700,"source_pr_head":SOURCE_HEAD,
        "source_word_sha256":WORD,"caller_sha256":CALLER,
        "source_clear_certificates_sha256":CERTS,"reference_bank_head":DONOR_HEAD,**extra,
    }
    return canonical({
        "metadata":metadata,"frames":frames,"initial":graph.initial,"final":graph.final,
        "first_output":graph.first,"moves":[[key,*route] for key,route in sorted(graph.moves.items())],
        "forms":[[key,[[token,str(value)] for token,value in sorted(row.items())]]
                 for key,row in sorted(graph.forms.items())],
        "schedule":graph.schedule(),
    })


def rebuild():
    word = json.loads(read("WORD.json.gz"))
    certs = json.loads(read("CERTS.json"))
    caller = json.loads(read("CALLER.json.gz"))
    need(certs["candidate_canonical_sha256"] == WORD and caller["stages"] == 16
         and caller["ambient_rank"] == 137, "literal source and signed caller binding")
    certificates = certs["clear_event_index"]
    parent,witnesses,raw_moves = raw_fold(word,certificates)
    child,mark = contract(parent,word["frames"],witnesses,raw_moves)
    graphs = {
        "PARENT-GRAPH.json.gz":serialized(parent,word["frames"],"parent"),
        "CANDIDATE-GRAPH.json.gz":serialized(child,word["frames"],"candidate",
                                source_banked_graph_sha256=PARENT,paid_relay=mark),
    }
    for name,raw in graphs.items():
        need(raw == read(name), f"deterministic reconstruction of decoded {name}")
    return word,certificates,parent,child,witnesses,mark,graphs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, help="Optional directory for regenerated gzip artifacts")
    args = parser.parse_args()
    *_,graphs = rebuild()
    if args.out_dir:
        for name,raw in graphs.items():
            with (args.out_dir/name).open("xb") as stream:
                stream.write(gzip.compress(raw,mtime=0))
    print("PASS_CF6A_REBUILD", PARENT, CHILD)


if __name__=="__main__":
    main()

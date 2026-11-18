"""Check the fixed helper restrictions with exact forward basis vectors."""
from collections import Counter
from fractions import Fraction
from functools import reduce
from graphlib import TopologicalSorter
from hashlib import sha256
from math import gcd, lcm
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
PARENT = "db10e4ca7154b454f86bf404bc34b3a16d02de6cc008d5227e4eef2654cb0778"
CHILD = "16e99893a2c669467ce74f214e8eb5150402f0267aaa8d67aad5d870aa4d5c18"


def require(ok, text):
    if not ok:
        raise ValueError(text)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sparse(entries):
    row = {k: Fraction(v) for k, v in entries}
    require(entries == [[k, str(row[k])] for k in sorted(row)] and all(row.values()),
            "noncanonical sparse row")
    return row


class Graph:
    def __init__(self, initial, final, moves, forms, first):
        self.initial, self.final = list(initial), list(final)
        self.moves, self.forms, self.first = moves, forms, first

    def order(self):
        n = len(self.initial)
        require(len(self.final) == n, "public dimensions")
        require(set(self.forms) == set(self.moves) | set(range(self.first, self.first + n)),
                "node inventory")
        successors = {k: [] for k in self.forms}
        degree = {}
        for key in sorted(self.forms):
            chart = self.moves[key][0] if key in self.moves else self.final[key - self.first]
            degree[key] = 0
            for donor in sorted(self.forms[key]):
                require(self.forms[key][donor] != 0, "zero edge")
                if donor < 0:
                    require(0 <= ~donor < n, "input range")
                    location = self.initial[~donor]
                else:
                    require(donor in self.moves, "missing paid donor")
                    location = self.moves[donor][1]
                    degree[key] += 1
                    successors[donor].append(key)
                require(chart == location, "nonlocal edge")
        ready = sorted(k for k, d in degree.items() if d == 0)
        result = []
        while ready:
            result.extend(ready)
            following = []
            for key in ready:
                for user in successors[key]:
                    degree[user] -= 1
                    if degree[user] == 0:
                        following.append(user)
            ready = following
        require(len(result) == len(self.forms), "dependency cycle")
        return result

    def transpose(self):
        def opposite(k):
            if k < 0:
                return self.first + ~k
            return ~(k - self.first) if k >= self.first else k
        forms = {k: {} for k in self.forms}
        for row, donors in self.forms.items():
            for donor, value in donors.items():
                forms[opposite(donor)][opposite(row)] = value
        return Graph(self.final, self.initial, {k: (b, a) for k, (a, b) in self.moves.items()},
                     forms, self.first)


def vector_sum(terms):
    """Keep one integer denominator per vector; no float enters the calculation."""
    terms = list(terms)
    denominator = lcm(*(d * q.denominator for q, (d, row) in terms))
    result = {}
    for q, (d, row) in terms:
        factor = q.numerator * (denominator // (d * q.denominator))
        for i, v in row.items():
            result[i] = result.get(i, 0) + factor * v
    result = {i: v for i, v in result.items() if v}
    common = reduce(gcd, result.values(), denominator)
    return denominator // common, {i: v // common for i, v in result.items()}


def basis(graph, wanted):
    order = graph.order()
    closure, pending = set(), list(wanted)
    while pending:
        key = pending.pop()
        if key < 0 or key in closure:
            continue
        require(key in graph.forms, "basis target")
        closure.add(key)
        pending.extend(graph.forms[key])
    values = {~i: (1, {i: 1}) for i in range(len(graph.initial))}
    products = 0
    for key in order:
        if key in closure:
            terms = [(q, values[d]) for d, q in graph.forms[key].items()]
            products += sum(len(v[1]) for q, v in terms)
            values[key] = vector_sum(terms)
    return {k: values[k] for k in wanted}, products, len(closure)


def replace(forms, pivot, relation):
    require(relation.get(pivot), "zero pivot")
    replacement = {k: -v / relation[pivot] for k, v in relation.items() if k != pivot}
    result = {}
    for key, row in forms.items():
        if key == pivot:
            continue
        new = {k: v for k, v in row.items() if k != pivot}
        if pivot in row:
            for donor, weight in replacement.items():
                new[donor] = new.get(donor, 0) + row[pivot] * weight
        result[key] = {k: v for k, v in new.items() if v}
    return result


def rank(frames, a, b):
    return abs(len(frames[a]) - len(frames[b]))


def reject(function, label):
    try:
        function()
    except ValueError:
        return label
    raise ValueError("control accepted: " + label)


def debit(saved, lost):
    require(lost > 0 and len(saved) >= 2 and all(d > 0 for d in saved) and sum(saved) == lost,
            "complete rank debit")


def validate_edit(graph, edit, mains, retired):
    r = edit["role"]
    require(0 <= r < len(graph.initial) and r not in mains | retired, "helper pivot")
    require(graph.initial[r] != graph.final[r], "zero target")
    entrance = {~k: v for k, v in sparse(edit["entrance"]).items()}
    require(entrance.get(~r), "missing entrance pivot")
    require(all(0 <= ~k < len(graph.initial) and ~k not in retired and
                graph.initial[~k] == graph.initial[r] for k in entrance), "entrance chart")
    banks = []
    for bank in edit["banks"]:
        pivot, chart = bank["remove"], bank["chart"]
        relation = sparse(bank["relation"])
        require(pivot in graph.moves and graph.moves[pivot][1] == chart and relation.get(pivot),
                "receiver pivot")
        for k in relation:
            require((k < 0 and 0 <= ~k < len(graph.initial)) or k in graph.moves,
                    "receiver donor")
            location = graph.initial[~k] if k < 0 else graph.moves[k][1]
            require(location == chart, "receiver chart")
        banks.append((pivot, chart, relation))
    require(len(banks) >= 2 and len({c for k, c, r in banks}) == len(banks), "receiver charts")
    return entrance, banks


def layouts(graph, frames):
    # The source hash uses this standard-library order. Basis evaluation uses Graph.order.
    canonical_order = list(TopologicalSorter({k: sorted(d for d in graph.forms[k] if d >= 0)
                                             for k in sorted(graph.forms)}).static_order())
    return dict(initial=graph.initial, final=graph.final, first_output=graph.first,
                frames=frames, moves=[[k, *graph.moves[k]] for k in sorted(graph.moves)],
                forms=[[k, [[d, str(q)] for d, q in sorted(graph.forms[k].items())]]
                       for k in sorted(graph.forms)], schedule=canonical_order)


def histogram(graph, frames, mains):
    spans = []
    for frame in frames:
        span = {0}
        for v in frame:
            require(0 < v < 512 and v not in span, "frame basis")
            span |= {v ^ w for w in span}
        spans.append(span)
    paid, targets = Counter(), Counter()
    for a, b in graph.moves.values():
        require(spans[a] < spans[b] or spans[b] < spans[a], "nested transfer")
        paid[rank(frames, a, b)] += 1
    for r, (a, b) in enumerate(zip(graph.initial, graph.final)):
        if r not in mains:
            require(spans[a] < spans[b], "positive helper")
            targets[rank(frames, a, b)] += 1
    return paid, targets


def run():
    for pin in json.loads((HERE / "SOURCE-PINS.json").read_text())["files"]:
        require(sha256((HERE / pin["path"]).read_bytes()).hexdigest() == pin["sha256"],
                "input identity: " + pin["path"])
    raw = gzip.decompress((HERE / "parent.json.gz").read_bytes())
    require(sha256(raw).hexdigest() == PARENT, "parent graph identity")
    source = json.loads(raw)
    interface = json.loads((HERE / "interface.json").read_text())
    edits = json.loads((HERE / "QUOTIENTS.json").read_text())
    frames = source["frames"]
    net = Graph(source["initial"], source["final"], {k: (a, b) for k, a, b in source["moves"]},
                {k: sparse(row) for k, row in source["forms"]}, source["first_output"])
    net.order()
    positions = {k: i for i, k in enumerate(source["schedule"])}
    require(len(positions) == len(source["schedule"]) == len(net.forms) and
            positions.keys() == net.forms.keys() and
            all(d < 0 or positions[d] < positions[k] for k, row in net.forms.items() for d in row),
            "source schedule")
    mains = set(interface["main_roles"])
    require(len(mains) == 400 and interface["public"] == len(net.initial) == 1501, "main interface")
    require(mains == set(interface["live"]) | {x + 112 for x in interface["live"]} |
            set(interface["hosted"]["X2"]) | set(interface["hosted"]["Y2"]), "main labels")
    before_hist = histogram(net, frames, mains)
    outputs = list(range(net.first, net.first + len(net.initial)))
    endpoint, parent_products, _ = basis(net, outputs)
    for r in range(len(net.initial)):
        row = endpoint[net.first + r]
        require(row[1].keys() <= mains if r in mains else row == (1, {r: 1}), "parent endpoint split")
    records, controls, retired = [], [], set()
    relation_products = 0
    paid_debit, target_debit = Counter(), Counter()
    for step, edit in enumerate(edits, 1):
        direction = edit["direction"]
        require(direction in ("forward", "transpose"), "direction")
        work = net.transpose() if direction == "transpose" else net
        entrance, banks = validate_edit(work, edit, mains, retired)
        wanted = {k for pivot, chart, row in banks for k in row}
        values, products, nodes = basis(work, wanted)
        relation_products += products
        target = vector_sum((q, (1, {~k: 1})) for k, q in entrance.items())
        for pivot, chart, row in banks:
            actual = vector_sum((q, values[k]) for k, q in row.items())
            require(actual == target, f"receiver relation at step {step}, key {pivot}")
            donor = next(k for k in row if values[k][1])
            altered = dict(row)
            altered[donor] += 1
            require(vector_sum((q, values[k]) for k, q in altered.items()) != target,
                    "altered receiver coefficient accepted")
            controls.append([step, pivot, "receiver coefficient +1 rejected", donor])
        altered_entrance = dict(entrance)
        altered_entrance[~edit["role"]] += 1
        require(vector_sum((q, (1, {~k: 1})) for k, q in altered_entrance.items()) != target,
                "altered entrance coefficient accepted")
        if step == 13:
            controls.append(reject(lambda: validate_edit(net, edit, mains, retired),
                                   "role 559 in forward orientation rejected"))
        saved = [rank(frames, *work.moves[pivot]) for pivot, chart, row in banks]
        lost = rank(frames, work.initial[edit["role"]], work.final[edit["role"]])
        debit(saved, lost)
        reject(lambda: debit(saved, 0), "omitted productive debit")
        paid_debit.update(saved)
        target_debit[lost] += 1
        forms = replace(work.forms, ~edit["role"], entrance)
        moves = dict(work.moves)
        for pivot, chart, row in banks:
            forms = replace(forms, pivot, row)
            del moves[pivot]
        final = list(work.final)
        final[edit["role"]] = work.initial[edit["role"]]
        forms[work.first + edit["role"]] = {~edit["role"]: Fraction(1)}
        work = Graph(work.initial, final, moves, forms, work.first)
        work.order()
        net = work.transpose() if direction == "transpose" else work
        net.order()
        retired.add(edit["role"])
        records.append(dict(step=step, role=edit["role"], direction=direction, saved=saved,
                            lost=lost, entrance_terms=len(entrance), ancestor_nodes=nodes,
                            coefficient_products=products))
    keep = [r for r in range(len(net.initial)) if r not in retired]
    remap = {r: i for i, r in enumerate(keep)}
    require(mains <= remap.keys() and all(remap[x + 112] == remap[x] + 112 for x in interface["live"]),
            "main compact interface")
    for r in retired:
        require(net.initial[r] == net.final[r] and net.forms[net.first + r] == {~r: 1},
                "retired identity")
    forms = {}
    for k, row in net.forms.items():
        if k >= net.first and k - net.first in retired:
            continue
        require(all(d >= 0 or ~d in remap for d in row), "retired entrance reader")
        key = net.first + remap[k - net.first] if k >= net.first else k
        forms[key] = {d if d >= 0 else ~remap[~d]: q for d, q in row.items()}
    net = Graph([net.initial[r] for r in keep], [net.final[r] for r in keep],
                net.moves, forms, net.first)
    digest = sha256(encoded(layouts(net, frames))).hexdigest()
    require(digest == CHILD, "compact graph identity")
    desired = {net.first + remap[r]: (d, {remap[i]: v for i, v in row.items()})
               for r in keep for d, row in [endpoint[net.first + r]]}
    actual, forward_products, _ = basis(net, desired)
    require(actual == desired, "compact forward endpoint")
    transposed = {net.first + i: {} for i in range(len(keep))}
    for k, (d, row) in desired.items():
        for i, v in row.items():
            transposed[net.first + i][k - net.first] = Fraction(v, d)
    desired_reverse = {k: vector_sum((q, (1, {i: 1})) for i, q in row.items())
                       for k, row in transposed.items()}
    actual_reverse, reverse_products, _ = basis(net.transpose(), desired_reverse)
    require(actual_reverse == desired_reverse, "compact transpose endpoint")
    after_hist = histogram(net, frames, {remap[r] for r in mains})
    require(before_hist[0] == after_hist[0] + paid_debit and
            before_hist[1] == after_hist[1] + target_debit, "aggregate rank debits")
    for label, histogram_value in (("paid", paid_debit), ("targets", target_debit)):
        require(sum(k * v for k, v in histogram_value.items()) == 200, label + " rank mass")
    invoices = []
    fixed = None
    for name, hist in (("parent-application.json", before_hist), ("application.json", after_hist)):
        published = json.loads((HERE / name).read_text())
        caller = published["caller"]
        require(caller["calls"] == 16, "caller multiplicity")
        now = [caller["fixed_caller_paid"], caller["fixed_root_targets"]]
        require(fixed is None or fixed == now, "fixed caller changed")
        fixed = now
        invoice = {}
        for label, native, base in zip(("paid", "targets"), hist, fixed):
            total = Counter({int(k): v for k, v in base.items()})
            total.update({k: 16 * v for k, v in native.items()})
            require({str(k): v for k, v in total.items()} == published["invoice"][label],
                    "published invoice " + label)
            invoice[label] = dict(jobs=sum(total.values()), mass=sum(k*v for k,v in total.items()))
        invoices.append(invoice)
    return dict(status="PASS_HELPER_QUOTIENT_BASIS_AUDIT", parent_sha256=PARENT,
                compact_sha256=digest, steps=records, relations=sum(len(r["saved"]) for r in records),
                directions=dict(Counter(r["direction"] for r in records)),
                public=[1501, len(keep)], main=len(mains), helpers=[1101, len(keep) - len(mains)],
                paid=[sum(before_hist[0].values()), sum(after_hist[0].values())],
                native_histograms={"parent":before_hist, "candidate":after_hist},
                full_invoices=invoices,
                native_debits={"paid":paid_debit, "targets":target_debit},
                sixteen_call_debits={"paid":{k:16*v for k,v in paid_debit.items()},
                                    "targets":{k:16*v for k,v in target_debit.items()},
                                    "paid_rank_mass":3200, "target_rank_mass":3200},
                basis_coefficient_products={"parent":parent_products, "relations":relation_products,
                                            "candidate_forward":forward_products, "candidate_transpose":reverse_products},
                controls=controls, altered_entrance_controls=len(records), omitted_debit_controls=len(records),
                retained_labels_sha256=sha256(encoded(keep)).hexdigest())


if __name__ == "__main__":
    result = json.loads(json.dumps(run()))
    expected = HERE / "RESULT.json"
    if expected.exists():
        require(result == json.loads(expected.read_text()), "receipt mismatch")
        print(result["status"], result["relations"], len(result["steps"]), result["public"][1])
    else:
        print(json.dumps(result, indent=2, sort_keys=True))

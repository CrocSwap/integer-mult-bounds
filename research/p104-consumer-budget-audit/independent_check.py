"""Independent literal-word and rational-budget audit; standard library only.

No primary checker, producer, Clifford interpreter or older audit is imported.
The forward program is reconstructed from its original witness and two literal
insertions. Binary spans and sparse rational rows are replayed from scratch.
This checks logical inverse-transpose compatibility, not the native physical
operators or admission of the conditional consumer's ownership/coverage model.

Predecessor construction and native correctness remain credited to PR2458,
PR2712, PR2725 and their retained lineage. Written with OpenAI Codex assistance;
this is a separate implementation, not independent human or formal review.
"""

from collections import Counter
from copy import deepcopy
from fractions import Fraction
from functools import lru_cache
from hashlib import sha1, sha256
import json
from pathlib import Path


P = Path(__file__).resolve().parent
ROOT = P.parents[1]
F = Fraction
KAPPA = F(836330098538459, 500000000000000000)
PROFILES = {
    "forward": (1216, 74, 86, 104, 48, 42, 68, 8),
    "2712": (1498, 60, 74, 92, 58, 56, 92, 8),
    "2725": (1502, 58, 74, 93, 57, 56, 91, 9),
}
DISCOUNTED = {
    "2712": (10408, 610, 726, 888, 472, 434, 708, 72),
    "2725": (10424, 602, 726, 892, 468, 434, 704, 76),
}
LOWER_BOUNDS = {
    "2712": F(7594999831115139259129, 7592000000000000000000),
    "2725": F(7595006521755927566801, 7592000000000000000000),
}


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def literal_json(raw):
    """Reject duplicate keys rather than letting a later value replace one."""
    def object_pairs(pairs):
        out = {}
        for key, value in pairs:
            need(key not in out, "duplicate JSON key")
            out[key] = value
        return out
    return json.loads(raw, object_pairs_hook=object_pairs)


def authenticated_json(base, records, field, name):
    matches = [r for r in records if r.get(field) == name]
    need(len(matches) == 1, "unique source pin: " + name)
    relative = Path(name)
    need(not relative.is_absolute() and ".." not in relative.parts,
         "relative source path")
    path = ((P / "inputs/SELECTED-AT-BASE.json")
            if base == ROOT and name == "certificates/selected-result.json"
            else base / relative).resolve()
    need(path.is_relative_to(base.resolve()), "source path containment")
    raw = path.read_bytes()
    pin = matches[0]
    need(sha256(raw).hexdigest() == pin["sha256"], "source SHA256: " + name)
    blob = b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
    need(sha1(blob).hexdigest() == pin["git_blob"], "source Git blob: " + name)
    return literal_json(raw), raw


def inputs():
    sources = literal_json((P / "SOURCES.json").read_bytes())["files"]
    predecessors = literal_json((P / "PREDECESSORS.json").read_bytes())["files"]
    witness, witness_raw = authenticated_json(
        ROOT, sources, "path", "research/p104-native-channel/inputs/LOWRANK-WITNESS.json")
    selected, _ = authenticated_json(ROOT, sources, "path", "certificates/selected-result.json")
    assembly, _ = authenticated_json(
        ROOT, sources, "path", "research/community-frontier1094-audit/ASSEMBLY.json")
    need(F(selected["kappa"]) == F(assembly["kappa"]) == KAPPA,
         "selected kappa binding")
    circuit, _ = authenticated_json(P, predecessors, "local", "inputs/PR2458-CIRCUIT.json")
    duals = {}
    for label in ("2712", "2725"):
        duals[label], _ = authenticated_json(
            P, predecessors, "local", "inputs/PR" + label + "-WORD.json")
    need(circuit["source_witness_sha256"] == sha256(witness_raw).hexdigest(),
         "forward witness binding")
    need(circuit["targets"] == [0, 1], "two corrected forward targets")
    insertions = circuit["insertions"]
    need(len(witness["program"]) == 4058 and len(insertions) == 2,
         "literal forward reconstruction sizes")
    need([x["completed_cut"] for x in insertions] == [0, 4058],
         "literal forward insertion cuts")
    need(set(witness["initial_frames"]).isdisjoint(circuit["initial_frames"]),
         "fresh correction dirt")
    forward = {
        "initial_frames": witness["initial_frames"] | circuit["initial_frames"],
        "final_frames": witness["final_frames"] | circuit["final_frames"],
        "program": insertions[0]["events"] + witness["program"] + insertions[1]["events"],
    }
    return forward, duals, F(assembly["complex_lower"])


@lru_cache(maxsize=None)
def span_tuple(vectors):
    values = {0}
    for vector in vectors:
        values.update(vector ^ old for old in tuple(values))
    need(len(values) == 1 << len(vectors), "independent frame basis")
    return frozenset(values)


def span(vectors):
    need(type(vectors) is list and len(vectors) <= 9
         and all(type(v) is int and 0 < v < 512 for v in vectors),
         "nine-bit frame domain")
    return span_tuple(tuple(vectors))


def replay(word, forward):
    initial, final = word["initial_frames"], word["final_frames"]
    names = sorted(initial)
    need(len(names) == 358 and set(final) == set(names), "persistent inventory")
    need(Counter(n[0] for n in names) == Counter(X=104, Y=104, D=32, G=32, Q=8, N=78),
         "persistent role inventory")
    frames = {n: span(initial[n]) for n in names}
    rows = {n: {n: F(1)} for n in names}
    counts, paid = Counter(), Counter()
    descending = 0
    private = None
    lifetimes = []
    for index, event in enumerate(word["program"]):
        need(type(event) is list and event and type(event[0]) is str, "literal event")
        tag = event[0]
        counts[tag] += 1
        if tag == "transport":
            need(len(event) == 5, "transport arity")
            _, name, old, new, rank = event
            old_span, new_span = span(old), span(new)
            need(name in frames and frames[name] == old_span, "transport entry chart")
            need(old_span <= new_span or new_span <= old_span, "nested transport")
            need(type(rank) is int and rank == abs(len(old) - len(new)) and rank > 0,
                 "transport rank charge")
            frames[name] = new_span
            paid[rank] += 1
            descending += len(old) > len(new)
        elif tag == "add":
            need(len(event) == 5, "ADD arity")
            _, target, source, coefficient, common = event
            need(target != source and target in frames and source in frames
                 and frames[target] == frames[source] == span(common), "common ADD chart")
            need(type(coefficient) in (int, str), "literal rational ADD coefficient")
            coefficient = F(coefficient)
            for name, value in rows[source].items():
                updated = rows[target].get(name, F(0)) + coefficient * value
                if updated:
                    rows[target][name] = updated
                else:
                    rows[target].pop(name, None)
        elif tag == "sign":
            need(len(event) == 4 and not forward, "dual sign arity")
            _, name, coefficient, common = event
            need(coefficient == "-1" and name in frames and frames[name] == span(common),
                 "sign coefficient and chart")
            rows[name] = {n: -v for n, v in rows[name].items()}
        elif tag == "zero":
            need(len(event) == 3, "zero arity")
            _, name, common = event
            need(name == "C" and name not in frames and private is None, "fresh owned zero")
            frames[name], rows[name] = span(common), {}
            private = {"start": index, "copied_from": None}
        elif tag == "copy":
            need(len(event) == 4 and forward, "forward COPY contract")
            _, name, source, common = event
            need(private is not None and name == "C" and source in rows
                 and private["copied_from"] is None and not rows[name], "zero COPY destination")
            need(frames[name] == frames[source] == span(common), "common COPY chart")
            rows[name] = dict(rows[source])
            private["copied_from"] = source
        elif tag == "erase":
            need(len(event) == 3, "erase arity")
            _, name, common = event
            need(private is not None and name == "C" and name in frames
                 and frames[name] == span(common), "owned erase chart")
            if forward:
                need(private["copied_from"] is not None and len(rows[name]) == 53,
                     "forward owned live-discard contract")
            else:
                need(private["copied_from"] is None and not rows[name], "dual zero erase")
            lifetimes.append((private["start"], index, private["copied_from"], len(rows[name])))
            del frames[name], rows[name]
            private = None
        else:
            raise ValueError("unknown event tag: " + tag)
    need(private is None and set(frames) == set(rows) == set(names), "private lifetime closure")
    need(frames == {n: span(final[n]) for n in names}, "complete final frames")
    need(len(lifetimes) == 8, "eight private lifetimes")
    if forward:
        need([x[2] for x in lifetimes] == ["Q" + str(i) for i in range(8)],
             "forward copied-source order")
    dirty = [n for n in names if n[0] not in "XY"]
    need(len(dirty) == 150 and all(rows[n] == {n: F(1)} for n in dirty),
         "arbitrary dirty-helper restoration")
    # This is endpoint dimension progress, not a certificate of owner credit.
    progress = Counter((n[0], len(initial[n]), len(final[n])) for n in names)
    expected_progress = Counter({("X", 1, 9): 104, ("Y", 0, 8): 104,
                                 ("D", 0, 9): 32, ("G", 0, 9): 32,
                                 ("Q", 0, 9): 8, ("N", 0, 9): 78})
    need(progress == expected_progress, "persistent endpoint progression")
    net = sum(len(final[n]) - len(initial[n]) for n in names)
    need(net == 104 * 8 + 104 * 8 + 150 * 9 == 3014, "endpoint progress sum")
    return {"rows": rows, "profile": paid, "counts": counts,
            "lifetimes": lifetimes, "descending": descending, "progress": net}


def check_forward_form(replayed):
    rows = replayed["rows"]
    for name, row in rows.items():
        if name.startswith("Y"):
            need(row.get(name) == 1 and all(n == name or n.startswith("X") for n in row),
                 "forward triangular form")
        else:
            need(row == {name: F(1)}, "forward restored source or helper")
    for target in (0, 1):
        need(rows["Y" + str(target)] == {"Y" + str(target): F(1), "X" + str(target): F(1)},
             "two corrected forward rows")


def check_inverse_transpose(forward, dual):
    """For F=[[I,0],[A,I]], F^-T=[[I,-A^T],[0,I]].

    The triangular form is checked separately. All persistent helpers carry
    identity blocks. Explicitly compare every coefficient, including zeros.
    """
    frows, drows = forward["rows"], dual["rows"]
    need(set(frows) == set(drows), "forward/dual persistent names")
    checked = 0
    for name in frows:
        expected = {name: F(1)}
        if name.startswith("X"):
            for target in range(104):
                y = "Y" + str(target)
                value = frows[y].get(name, F(0))
                if value:
                    expected[y] = -value
        for column in frows:
            need(drows[name].get(column, F(0)) == expected.get(column, F(0)),
                 "inverse-transpose boundary coefficient")
            checked += 1
    need(checked == 128164, "all boundary coefficients compared")
    return checked


def check_ledger(label, replayed):
    paid = replayed["profile"]
    need(tuple(paid[r] for r in range(1, 9)) == PROFILES[label]
         and set(paid) == set(range(1, 9)), "complete expected transport profile")
    if label == "forward":
        expected = Counter(add=3064, transport=1646, zero=8, copy=8, erase=8)
        mass, descending = 3070, 8
    else:
        expected = Counter(add=3104, transport=1938 if label == "2712" else 1940,
                           zero=8, erase=8, sign=208)
        mass, descending = 3542, 216
    need(replayed["counts"] == expected and replayed["descending"] == descending,
         "literal operation ledger")
    need(sum(r * count for r, count in paid.items()) == mass, "complete paid rank mass")


def elementary_log_bounds():
    # In e=sum 1/n!, the n>=5 tail is below (1/120)/(1-1/6).
    # Thus e < 1631/600 < 11/4, so e^4<73 and e^2<73/8.
    factorial, partial = 1, F(1)
    for n in range(1, 5):
        factorial *= n
        partial += F(1, factorial)
    upper = partial + F(1, 120) / (1 - F(1, 6))
    need(upper == F(1631, 600) and upper < F(11, 4), "elementary exponential bound")
    need(F(11, 4) ** 4 < 73 and F(11, 4) ** 2 < F(73, 8),
         "strict logarithm lower bounds")


def budget(label, forward, dual):
    need(0 < KAPPA < 1, "selected saving domain")
    m, families, stages, forgiveness = 73, 832, 9, 416
    progress = forward["progress"]
    need(progress == dual["progress"] == 3014, "equal endpoint progression")
    idle = (m - 1) * families - stages * progress
    need(idle == 32778, "conditional idle coverage")
    raw = Counter({r: 5 * forward["profile"][r] + 4 * dual["profile"][r]
                   for r in range(1, 9)})
    need(F(sum(r * n for r, n in raw.items()) + idle, m * families) == F(599, 584),
         "raw mass obstruction")
    discounted = raw.copy()
    discounted[1] -= 4 * forgiveness
    need(discounted[1] >= 0 and tuple(discounted[r] for r in range(1, 9)) == DISCOUNTED[label],
         "endpoint-forgiven profile")
    mass = sum(r * n for r, n in discounted.items())
    need(mass == 27854 and mass + idle == m * families - 104,
         "discounted mass and slack")
    # For 0<p<1, each integer increment j^p-(j-1)^p is <=1.
    # Therefore removing <=416 integer ranks per dual saves <=416 H1.
    # This does not cover arbitrary regrouping of the remaining children.
    # Idle children of rank<=m cost at least idle/m; grant this relaxation.
    # (r/m)^(1-a) = (r/m)*exp(a*log(m/r)), exp(x)>=1+x.
    # log(73)>4 for r=1; log(73/r)>2 for 2<=r<=8.
    slope = 4 * discounted[1] + 2 * sum(r * discounted[r] for r in range(2, 9))
    need(slope == (76524 if label == "2712" else 76556), "elementary moment slope")
    lower = 1 + (slope * KAPPA - 104) / (m * families)
    need(lower == LOWER_BOUNDS[label] and lower > 1, "selected rational obstruction")
    # A fully paid bank adds the same m to mass and denominator. Its presence
    # divides this positive excess by a larger positive capacity, never flips it.
    need(slope * KAPPA - 104 > 0, "fully paid bank excess sign")
    return lower


def regrouping_scope_witness(primitive_saving):
    """A histogram counterexample to a mass-only extension, not a new word.

    Independent logarithm upper bounds use e>65/24 and integer powers, not
    direct Taylor evaluations of exp(9/2) or exp(17/8).
    """
    need(primitive_saving == F(67018507072324140917, 40000000000000000000000),
         "selected primitive saving binding")
    lower_e = sum((F(1), F(1), F(1, 2), F(1, 6), F(1, 24)))
    need(lower_e == F(65, 24) and lower_e ** 9 > 73 ** 2
         and lower_e ** 17 > F(73, 9) ** 8, "scope witness logarithm upper bounds")
    # Thus log(73)<9/2 and log(73/9)<17/8. For 0<=x<1,
    # exp(x)<=sum x^n=1/(1-x), by termwise comparison of the series.
    x1, x9 = primitive_saving * F(9, 2), primitive_saving * F(17, 8)
    need(0 < x1 < 1 and 0 < x9 < 1, "scope witness geometric-series domain")
    need(17 + 3093 * 9 == 27854, "scope witness equal rank mass")
    upper = (F(17) / (1 - x1) + F(3093 * 9) / (1 - x9) + 32778) / (73 * 832)
    need(upper == F(768756558943453721588036545458749049905049480382613,
                   768812344366283572579075775027782729118100104964256)
         and upper < 1, "scope witness favorable abstract histogram")
    # Both reciprocal terms increase with a while their denominators stay
    # positive. Checking the endpoint therefore covers 0<=a<=1/580.
    endpoint = F(1, 580)
    end_x1, end_x9 = endpoint * F(9, 2), endpoint * F(17, 8)
    need(0 < primitive_saving < endpoint and 0 < end_x1 < 1 and 0 < end_x9 < 1,
         "uniform scope witness interval domain")
    endpoint_upper = (F(17) / (1 - end_x1) + F(3093 * 9) / (1 - end_x9)
                      + 32778) / (73 * 832)
    need(upper < endpoint_upper == F(53862115339, 53863448288) < 1,
         "uniform scope witness interval endpoint")


def rejects(label, expected, function):
    try:
        function()
    except ValueError as error:
        need(expected in str(error), "control rejected for unrelated reason: " + label)
        return
    raise ValueError("control unexpectedly accepted: " + label)


def controls(forward_word, dual_word, forward_result):
    bad = deepcopy(dual_word)
    event = next(e for e in bad["program"] if e[0] == "add" and e[4])
    event[4] = []
    rejects("stale ADD chart", "common ADD chart", lambda: replay(bad, False))

    bad = deepcopy(forward_word)
    index = next(i for i, e in enumerate(bad["program"]) if e[0] == "copy")
    _, target, source, common = bad["program"][index]
    bad["program"].insert(index, ["add", target, source, "1", common])
    rejects("dirty COPY destination", "zero COPY destination", lambda: replay(bad, True))

    bad = deepcopy(dual_word)
    event = next(e for e in reversed(bad["program"])
                 if e[0] == "add" and e[1].startswith("X"))
    event[3] = "0"
    rejects("lost dual coefficient", "inverse-transpose boundary coefficient",
            lambda: check_inverse_transpose(forward_result, replay(bad, False)))

    bad = deepcopy(dual_word)
    event = next(e for e in bad["program"] if e[0] == "transport" and e[4] > 1)
    event[4] -= 1
    rejects("undercharged transport", "transport rank charge", lambda: replay(bad, False))

    bad = deepcopy(forward_word)
    need(bad["program"][0][0] == "add", "forward compensation control location")
    bad["program"][0][3] = "0"
    rejects("lost forward dirty compensation", "forward triangular form",
            lambda: check_forward_form(replay(bad, True)))

    bad = deepcopy(dual_word)
    cut = next(i for i, e in enumerate(bad["program"]) if e[0] == "erase")
    event = next(e for e in reversed(bad["program"][:cut]) if e[0] == "add" and e[1] == "C")
    event[3] = "0"
    rejects("lost dual private cleanup", "dual zero erase", lambda: replay(bad, False))
    return 6


def main():
    forward_word, dual_words, primitive_saving = inputs()
    forward = replay(forward_word, True)
    check_forward_form(forward)
    check_ledger("forward", forward)
    elementary_log_bounds()
    regrouping_scope_witness(primitive_saving)
    coefficients = 0
    for label, word in dual_words.items():
        dual = replay(word, False)
        check_ledger(label, dual)
        coefficients += check_inverse_transpose(forward, dual)
        budget(label, forward, dual)
    count = controls(forward_word, dual_words["2725"], forward)
    print("PASS_INDEPENDENT_P104_CONSUMER_BUDGET"
          f" words=3 coefficients={coefficients} dirty_helpers=150_per_word"
          " forward_live_discards=8 dual_zero_erases=8_per_word"
          " progress=3014_per_word slopes=76524,76556 abstract_scope_witness=1"
          f" controls={count} conditional_coverage_only no_native_or_owner_admission")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Authenticate and reconstruct the exact owned-rise adapter/lifetime evidence.

The finite evidence is not an execution of a recursive or fixed-tape child.
The all-width and chronological-contract implication is proved in PROOF.md.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from hashlib import sha1, sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    inventory = json.loads((HERE / "RETAINED.json").read_text())["files"]
    for record in inventory:
        path = HERE / record["path"]
        need(not path.is_symlink(), "source symlink")
        data = path.read_bytes()
        need(len(data) == record["bytes"], "source byte length")
        need(sha256(data).hexdigest() == record["sha256"], "source SHA256")
        blob = sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        need(blob == record["git_blob"], "source Git blob")
    return len(inventory)


def space(basis):
    result = {0}
    for vector in basis:
        need(isinstance(vector, int) and 0 < vector < 512, "nine-axis frame basis")
        need(vector not in result, "independent frame basis")
        result |= {x ^ vector for x in result}
    return result


def scan(word, descending_only=False):
    """Exact current-frame and symbolic owned-lifetime scan of the literal word."""
    public = len(word["initial"])
    total = public + word["owned_fields"]
    spaces = [space(frame) for frame in word["frames"]]
    dims = [len(frame) for frame in word["frames"]]
    current = word["initial"][:] + [None] * word["owned_fields"]
    rows = [{r: Fraction(1)} for r in range(public)] + [{} for _ in range(word["owned_fields"])]
    active = {}
    lives = []
    rises = []
    paid = Counter()
    dirty_clears = peak = 0
    strict_rejections = []
    second_targets = set(word["hosted"]["Y2"])
    owned_reads_y2 = []
    for index, event in enumerate(word["program"]):
        op, role = event[:2]
        need(isinstance(role, int) and 0 <= role < total, "actual physical role")
        if op == "INIT":
            frame = event[2]
            need(public <= role and current[role] is None and role not in active, "exclusive owned birth")
            need(0 <= frame < len(spaces), "birth chart exists")
            current[role] = frame
            rows[role] = {}
            life = dict(role=role, begin=index, birth_frame=frame, rises=[], reads=[], writes=[], moves=[])
            active[role] = life
            lives.append(life)
            peak = max(peak, len(active))
        elif op == "CLEAR":
            need(role in active and current[role] == event[2], "owned clear at the actual current chart")
            life = active.pop(role)
            life.update(end=index, death_frame=event[2], dirty=bool(rows[role]))
            dirty_clears += bool(rows[role])
            current[role] = None
            rows[role] = {}
        elif op == "MOVE":
            _, role, start, end, private = event
            need(current[role] == start and bool(private) == (role in active), "paid move owns its current field")
            rising = spaces[start] < spaces[end]
            falling = spaces[end] < spaces[start]
            need(rising or falling, "strict nested move")
            need(private or rising, "public source rule remains ascending")
            rank = abs(dims[start] - dims[end])
            paid[rank] += 1
            if private:
                active[role]["moves"].append(index)
                if rising:
                    active[role]["rises"].append(index)
                    rises.append(dict(event=index, role=role, start=start, end=end, rank=rank))
                    if descending_only:
                        strict_rejections.append(index)
            current[role] = end
        else:
            need(op in ("ADD", "COPY", "SCALE"), "literal scalar alphabet")
            frame = event[-1]
            need(current[role] is not None and current[role] == frame, "scalar destination current chart")
            value = Fraction(event[2] if op == "SCALE" else event[3])
            need(value and value.denominator & (value.denominator - 1) == 0, "nonzero dyadic scalar")
            if role in active:
                active[role]["writes"].append(index)
            if op == "SCALE":
                need(abs(value.numerator) & (abs(value.numerator) - 1) == 0, "unit dyadic SCALE")
                rows[role] = {key: coefficient * value for key, coefficient in rows[role].items()}
            else:
                source = event[2]
                need(0 <= source < total and source != role and current[source] == frame, "scalar source same chart and distinct field")
                if op == "COPY":
                    need(role in active and not rows[role], "ideal COPY into owned zero; numerical semantics is ADD")
                if source in active:
                    active[source]["reads"].append(index)
                if role in active and source in second_targets:
                    owned_reads_y2.append(index)
                for key, coefficient in rows[source].items():
                    updated = rows[role].get(key, Fraction(0)) + value * coefficient
                    if updated:
                        rows[role][key] = updated
                    else:
                        rows[role].pop(key, None)
    need(not active and all(x is None for x in current[public:]), "every owned lifetime closes")
    need(current[:public] == word["final"], "literal public final charts")
    need(all(not row for row in rows[public:]), "ideal owned return has no independent data")
    histogram = Counter(item["rank"] for item in rises)
    before = [life["begin"] for life in lives if life["rises"] and any(j < life["rises"][0] for j in life["reads"])]
    between = [life["begin"] for life in lives if len(life["rises"]) > 1 and
               any(life["rises"][0] < j < life["rises"][-1] for j in life["writes"] + life["reads"])]
    result = dict(events=len(word["program"]), public=public, owned_roles=word["owned_fields"],
                  lifetimes=len(lives), owned_peak=peak, dirty_clears=dirty_clears,
                  paid=dict(sorted(paid.items())), paid_mass=sum(rank * count for rank, count in paid.items()),
                  owned_rises=len(rises), ascent_histogram=dict(sorted(histogram.items())),
                  ascent_mass=sum(item["rank"] for item in rises),
                  read_before_first_rise_lifetimes=before, contacts_between_rises_lifetimes=between,
                  owned_reads_Y2=owned_reads_y2, strict_rejected_events=strict_rejections)
    return rises, lives, result


def record_list(monomial):
    """Uniform-in-f nine-axis record realization, with every phase retained."""
    matrix = monomial["matrix_rows"]
    phase = monomial["phase"]
    alpha = monomial["linear_Z4"]
    quadratic = monomial["quadratic_rows"]
    need(len(matrix) == len(alpha) == len(quadratic) == 9, "complete nine-axis monomial")
    need(0 <= monomial["offset"] < 512 and 0 <= phase < 4, "monomial displacement/absolute phase")
    records = []
    for i, value in enumerate(alpha):
        need(0 <= value < 4 and value % 2 == (quadratic[i] >> i) & 1, "unit quadratic phase convention")
        records.extend([["S", i]] * value)
    for i in range(9):
        for j in range(i + 1, 9):
            need(((quadratic[i] >> j) & 1) == ((quadratic[j] >> i) & 1), "symmetric quadratic phase")
            if (quadratic[i] >> j) & 1:
                records.append(["CZ", i, j])
    reduced = list(matrix)
    eliminate = []
    for column in range(9):
        pivot = next((row for row in range(column, 9) if (reduced[row] >> column) & 1), None)
        need(pivot is not None, "invertible monomial address map")
        if pivot != column:
            reduced[pivot], reduced[column] = reduced[column], reduced[pivot]
            eliminate.extend([["XROW", column, pivot], ["XROW", pivot, column], ["XROW", column, pivot]])
        for row in range(9):
            if row != column and (reduced[row] >> column) & 1:
                reduced[row] ^= reduced[column]
                eliminate.append(["XROW", row, column])
    need(reduced == [1 << i for i in range(9)], "monomial eliminated exactly")
    records.extend(reversed(eliminate))
    records.extend(["NOT", i] for i in range(9) if (monomial["offset"] >> i) & 1)
    records.extend([["I"]] * phase)
    need(len(records) <= 171, "retained fixed monomial record bound")
    return records


def load_clifford():
    spec = spec_from_file_location("owned_ascent_retained_clifford", HERE / "retained/clifford_exact.py")
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build():
    sources = authenticate()
    word = json.load(gzip.open(HERE / "retained/native-word.json.gz", "rt"))
    rises, lives, census = scan(word, descending_only=True)
    need(len(rises) == 23 and census["ascent_mass"] == 56, "literal ascent census")
    need(census["strict_rejected_events"] == [item["event"] for item in rises], "exact old-rule rejection boundary")
    compiler = load_clifford()
    frames = {}

    def chart(index):
        if index not in frames:
            frames[index] = compiler.canonical_frame(9, tuple(word["frames"][index]))
        return frames[index]

    recipes = []
    for item in rises:
        operator = chart(item["start"]).adjoint().then(chart(item["end"]))
        recipe, compiled = compiler.lower_child(operator)
        need(recipe["rank"] == item["rank"], "compiled rise is one canonical child of exactly its rank")
        need(compiled.tab == operator.tab and compiled.zero_state() == operator.zero_state(), "phase-bearing compiler equality")
        entry = dict(item, left=recipe["left"], right=recipe["right"])
        entry["left_records"] = record_list(entry["left"])
        entry["right_records"] = record_list(entry["right"])
        recipes.append(entry)
    pairs = [len(item["left_records"]) + len(item["right_records"]) for item in recipes]
    need(all(count <= 342 < 1000 for count in pairs), "every rise adapter pair fits its already charged route allowance")
    controls = {}
    import copy
    first_birth = next(j for j, event in enumerate(word["program"]) if event[0] == "INIT")
    for name, mutate in (
        ("public_alias", lambda mutant: mutant["program"][first_birth].__setitem__(1, 0)),
        ("missing_clear", lambda mutant: mutant["program"].pop(next(j for j, event in enumerate(mutant["program"]) if event[0] == "CLEAR"))),
        ("zero_rank_move", lambda mutant: mutant["program"][rises[0]["event"]].__setitem__(3, rises[0]["start"])),
    ):
        mutant = copy.deepcopy(word)
        mutate(mutant)
        try:
            scan(mutant)
        except ValueError:
            controls[name] = True
        else:
            controls[name] = False
    need(all(controls.values()), "ownership/frame controls reject")
    result = dict(source_files=sources, census=census, adapter_pairs=len(recipes),
                  max_monomial_records=max(len(item[key]) for item in recipes for key in ("left_records", "right_records")),
                  max_pair_records=max(pairs), total_pair_records=sum(pairs),
                  existing_rise_route_allowance=1000 * len(recipes), added_paid_jobs=0,
                  added_productive_credits=0, added_physical_banks=0, controls=controls)
    return recipes, lives, result


def run():
    recipes, lives, result = build()
    need(json.loads(json.dumps(recipes)) == json.loads((HERE / "RECIPES.json").read_text()), "complete frozen phase-bearing recipes")
    need(lives == json.loads((HERE / "LIFETIMES.json").read_text()), "complete frozen chronological lifetimes")
    need(json.loads(json.dumps(result)) == json.loads((HERE / "RESULT.json").read_text())["primary"], "frozen exact result")
    print(json.dumps(result, sort_keys=True))
    print("PASS_OWNED_ASCENT_CONTRACT")


if __name__ == "__main__":
    try:
        run()
    except Exception as error:
        print("FAIL_OWNED_ASCENT_CONTRACT:", error, file=sys.stderr)
        raise SystemExit(1) from error

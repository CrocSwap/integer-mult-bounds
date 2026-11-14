#!/usr/bin/env python3
"""Independent exact replay cross-check of the 16 detailed full-L samples."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys


PACKAGE = Path(__file__).resolve().parents[1]
WORD_PATH = PACKAGE / "inputs/WORD.json.gz"
WORD_SHA = "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9"


def need(ok, message):
    if not ok:
        raise AssertionError(message)


def add(dst, src, factor=Q(1)):
    for coordinate, value in src.items():
        result = dst.get(coordinate, Q(0)) + factor * value
        if result:
            dst[coordinate] = result
        else:
            dst.pop(coordinate, None)


def reduce_row(row, basis):
    result = row.copy()
    for pivot in sorted(basis):
        if result.get(pivot):
            add(result, basis[pivot], -result[pivot])
    return result


def insert(basis, row):
    result = reduce_row(row, basis)
    if not result:
        return False
    pivot = min(result)
    scale = result[pivot]
    basis[pivot] = {h: value / scale for h, value in result.items()}
    return True


def image_and_kernel(rows, mains, helpers):
    image = {}
    lifts = {}
    kernel = {}
    for original in rows:
        projected = {h: value for h, value in original.items() if h in mains}
        lift = original.copy()
        for pivot in sorted(image):
            coefficient = projected.get(pivot)
            if coefficient:
                add(projected, image[pivot], -coefficient)
                add(lift, lifts[pivot], -coefficient)
        if projected:
            pivot = min(projected)
            scale = projected[pivot]
            image[pivot] = {h: value/scale for h, value in projected.items()}
            lifts[pivot] = {h: value/scale for h, value in lift.items()}
        else:
            need(set(lift) <= helpers, "prior projection kernel is helper-only")
            insert(kernel, lift)
    return image, lifts, kernel


def span_key(frame):
    values = {0}
    for vector in frame:
        values |= {x ^ vector for x in tuple(values)}
    need(len(values) == 1 << len(frame), "original frame independence")
    return frozenset(values)


def as_row(row):
    return {int(h): Q(value) for h, value in row.items()}


def load_price():
    path = PACKAGE / "verifier/integer_prices.py"
    spec = importlib.util.spec_from_file_location("wave52_crosscheck_prices", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def check(sample, paired):
    raw = WORD_PATH.read_bytes()
    need(sha256(raw).hexdigest() == WORD_SHA, "exact #7481 source bytes")
    word = json.loads(gzip.decompress(raw))
    need(sample["source_sha256"] == paired["source_sha256"] == WORD_SHA,
         "both result sets bind same pinned source")
    sample_by_event = {x["event"]: x for x in sample["candidate_relations"]}
    paired_by_event = {x["event"]: x for x in paired["records"]}
    sample_events = set(sample_by_event)
    need(len(sample_events) == 16 and sample_events <= set(paired_by_event),
         "all 16 sampled events present in exhaustive paired replay")

    frames = word["frames"]
    spans = [span_key(frame) for frame in frames]
    dimensions = list(map(len, frames))
    public = word["public"]
    mains = (set(word["live"]) | {h + 112 for h in word["live"]} |
             set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"]))
    helpers = set(range(public)) - mains
    target_ranks = {h: abs(dimensions[word["initial"][h]] -
                           dimensions[word["final"][h]]) for h in helpers}
    selected_keys = {spans[sample_by_event[event]["destination"]]
                     for event in sample_events}
    histories = {key: {} for key in selected_keys}
    rows = [{h: Q(1)} for h in range(public)] + [None] * word["owned_fields"]
    charts = list(word["initial"]) + [None] * word["owned_fields"]
    for owner, frame in enumerate(word["initial"]):
        key = spans[frame]
        if key in histories:
            insert(histories[key], {owner: Q(1)})

    checked = []
    price = load_price()
    for event, instruction in enumerate(word["program"]):
        opcode, owner = instruction[:2]
        if opcode == "MOVE":
            source, destination = instruction[2:4]
            need(rows[owner] is not None and charts[owner] == source,
                 "native source chart during direct sample replay")
            target = rows[owner].copy()
            key = spans[destination]
            if event in sample_events:
                record = sample_by_event[event]
                paired_record = paired_by_event[event]
                need(not instruction[4], "sampled target is public")
                need((owner, source, destination) ==
                     (record["owner"], record["source"], record["destination"]),
                     "sampled owner/endpoints match source")
                P = histories[key]
                rank = abs(dimensions[source] - dimensions[destination])
                need(rank == record["target_rank"] == paired_record["target_rank"],
                     "target movement rank agrees")
                target_main = {h: value for h, value in target.items() if h in mains}
                main_P = {}
                for prior in P.values():
                    projection = {h: value for h, value in prior.items() if h in mains}
                    if projection:
                        insert(main_P, projection)
                need(target_main and not reduce_row(target_main, main_P),
                     "strict prior main history contains target projection")
                need(bool(reduce_row(target, P)),
                     "target misses strict full native history")
                need({str(h): str(v) for h, v in sorted(target.items())} == record["target"],
                     "full source replay reproduces sample target")

                image, lifts, K = image_and_kernel(list(P.values()), mains, helpers)
                projected = target_main.copy()
                residual = target.copy()
                for pivot in sorted(image):
                    coefficient = projected.get(pivot)
                    if coefficient:
                        add(projected, image[pivot], -coefficient)
                        add(residual, lifts[pivot], -coefficient)
                need(not projected and set(residual) <= helpers,
                     "paired reduction yields helper residual")
                need(bool(reduce_row(residual, K)),
                     "paired residual is outside prior helper kernel")
                expected_kernel_dimension = len(K)
                need(record["prior_helper_history_dimension"] == expected_kernel_dimension,
                     "sample kernel dimension matches independent paired replay")
                need(record["L_dimension"] == expected_kernel_dimension + 1,
                     "L_E dimension follows independent quotient rank one")

                # L_E = K + span(residual). Its support is the union of K and
                # the residual, so this independent minimum must match the
                # full-L echelon witness's minimum coordinate tariff.
                support = set().union(*(set(row) for row in K.values())) | set(residual)
                minimum_rank = min(target_ranks[h] for h in support)
                need(minimum_rank == record["minimum_enabling_relation_rank"] ==
                     paired_record["minimum_enabling_relation_rank"],
                     "minimum one-relation debit agrees with independent paired replay")

                relation = as_row(record["minimum_enabling_relation"])
                need(set(relation) <= helpers and bool(relation), "witness helper-only")
                history_coefficients = record["relation_history_basis_coefficients"]
                check_row = relation.copy()
                prior_rows = list(P.values())
                for index, coefficient in history_coefficients.items():
                    add(check_row, prior_rows[int(index)], Q(coefficient))
                need(check_row == target,
                     "exact witness identity target = relation + prior history rows")
                need(bool(reduce_row(relation, K)),
                     "witness supplies a new helper relation outside K")
                need(min(target_ranks[h] for h in relation) == minimum_rank,
                     "full-L witness attains independently computed minimum price")

                profile = Counter({rank: 1})
                profile[minimum_rank] -= 1
                profile = {r: count for r, count in profile.items() if count}
                exact_saving = price.display(price.moment(profile))
                need(exact_saving["exact"] == record["optimistic_single_cache_saving_0038"]["exact"],
                     "full-L saved saving class/interval matches exact price engine")
                sample_class = record["optimistic_single_cache_saving_classification"]
                paired_class = paired_record["saving_0038"]["classification"]
                classes_agree = (sample_class == paired_class or
                                 (sample_class == "interval_overlap" and
                                  paired_class == "zero_or_interval_overlap"))
                need(classes_agree,
                     "sample and exhaustive paired saving classes agree")
                checked.append({"event": event, "target_rank": rank,
                    "minimum_enabling_relation_rank": minimum_rank,
                    "L_dimension": record["L_dimension"],
                    "prior_helper_history_dimension": expected_kernel_dimension,
                    "full_history_miss": True,
                    "saving_class": paired_record["saving_0038"]["classification"]})
            if key in histories:
                insert(histories[key], target)
            rows[owner] = target
            charts[owner] = destination
        elif opcode == "INIT":
            need(owner >= public and charts[owner] is None and rows[owner] is None,
                 "owned INIT lifecycle")
            charts[owner], rows[owner] = instruction[2], {}
        elif opcode == "CLEAR":
            need(owner >= public and charts[owner] == instruction[2] and rows[owner] is not None,
                 "owned CLEAR lifecycle")
            charts[owner], rows[owner] = None, None
        elif opcode == "SCALE":
            need(charts[owner] == instruction[3] and rows[owner] is not None,
                 "coframed SCALE")
            factor = Q(instruction[2])
            need(factor, "nonzero SCALE")
            rows[owner] = {h: factor * value for h, value in rows[owner].items()
                           if factor * value}
        elif opcode in ("ADD", "COPY"):
            donor = instruction[2]
            need(owner != donor and charts[owner] == charts[donor] == instruction[4],
                 "coframed scalar contact")
            if opcode == "COPY":
                need(owner >= public and not rows[owner], "zero owned COPY destination")
            add(rows[owner], rows[donor], Q(instruction[3]))
        else:
            raise AssertionError(f"unknown opcode: {opcode}")

    need(len(checked) == 16, "all 16 detailed candidates cross-checked")
    # Equal rank means f(r)-f(r)=0 exactly. This catches dict-collision or
    # signed-interval mistakes in the rank-price aggregation.
    for item in checked:
        if item["target_rank"] == item["minimum_enabling_relation_rank"]:
            source_record = paired_by_event[item["event"]]
            need(source_record["saving_0038"]["exact"] == ["0", "0"] and
                 source_record["saving_0038"]["classification"] == "zero_or_interval_overlap",
                 "equal-rank profile is exactly zero (cancellation control)")
    control_profile = Counter({5: 1})
    control_profile[5] -= 1
    control_profile = {rank: count for rank, count in control_profile.items() if count}
    control_saving = price.moment(control_profile)
    need(control_saving == (Q(0), Q(0)),
         "equal-rank f(5)-f(5) control cancels exactly")
    collapsed_dict_mutant = price.moment({5: -1})
    need(collapsed_dict_mutant != control_saving,
         "negative control detects a dict-collision implementation mutant")
    return {"status": "PASS", "source_sha256": WORD_SHA,
            "crosschecked_sample_count": len(checked), "sampled_events": checked,
            "equal_rank_cancellation_control": {
                "status": "PASS", "profile": control_profile,
                "exact_interval": [str(x) for x in control_saving],
                "dict_collision_mutant_rejected": True},
            "method": "Fresh exact full source replay of the 16 selected histories; paired image/lift/kernel computation independently checks L_E dimension and minimum support rank, while each published helper witness is verified by its exact prior-history row identity.",
            "scope": "Checks only the 16 full-L samples against the exhaustive paired price engine; the all-1,066 candidate screen is separately recorded in ALL-ONE-RELATION-PRICES.json."}


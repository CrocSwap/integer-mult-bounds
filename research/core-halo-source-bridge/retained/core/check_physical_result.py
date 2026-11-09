"""Independent numerical/source review of the complete physical I1 receipt.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
This reads externally observed words. It never supplies a physical payload or
claims the I1 execution verifies a nonidentity interior. Source Q is regenerated
from authenticated Reference entries, not accepted from the producer's pages.
"""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

from independent_numerics import (
    bandwidth, budget, canonical_json, ceil_log2, decode_pairs, five_factors, identity, need,
    pow2, row_norm, squared_norm,
)
from stage_observer import KINDS, check_stages
from check_source_join import dense_replay
from staged_oracle import first_inverse, supplied_action


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main():
    parser = ArgumentParser()
    parser.add_argument("--source-package", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    package = args.source_package.resolve()
    path = args.receipt or package / "PHYSICAL-RESULT.json"
    raw = path.read_bytes()
    receipt = json.loads(raw)
    need(receipt["status"] == "PASS_COMPLETE_PHYSICAL_NARROW_CORE", "completed physical receipt")
    plan, source = receipt["allocation"], receipt["source"]
    need(plan["labels"] == plan["g"] == 1 and plan["side"] == 2,
         "this observed physical fixture is exactly K1 g1 L2")
    join = load("_physical_observer_join_sources", package / "join_sources.py")
    with join.numerical() as runtime:
        reference = runtime.reference.Reference(runtime.raw, *source["parameters"])
        need(reference.description_hash == source["reference_sha256"], "same immutable actual Reference")
        origin, side = source["origin"], plan["side"]
        q = tuple(tuple(reference.entry("narrow", origin + i, origin + j).value
                        for j in range(side)) for i in range(side))
        reported = tuple(tuple(Q(x) for x in row) for row in source["Q"][0][0])
        need(q == reported and q != identity(side), "regenerated original nonidentity Q")
        factors = five_factors(q, source["interior"])
        need(factors["A"] == ((Q(1),),), "physical fixture has identity scalar interior only")
        norm_bound = max(max(row_norm(m), row_norm(tuple(zip(*m)))) for m in factors["factors"])
        need(norm_bound <= plan["h"], "independent actual row/column source norm certificate")
        recomputed = budget(plan["n"], plan["g"], plan["h"], plan["target"], plan["P"],
                            plan["R0"].bit_length() - 1)
        for name in ("H", "R0", "R2", "Rstar", "stage_target", "local_target", "V2"):
            need(recomputed[name] == plan[name], "independent complete allocation: " + name)
        P, width, rb = plan["P"], plan["width"], plan["radius_bits"]
        need(squared_norm(decode_pairs(receipt["initial"], P)) <= plan["R0"] ** 2,
             "actual input satisfies the initial whole-field radius promise")
        need(width >= P + rb + 2, "completed dense output fits common carrier despite internal Wd")
        window_source = load("_physical_observer_window", join.INVERSE / "source_window.py")
        band = max(1, bandwidth(q))
        sufficient = window_source.sufficient_allocation(reference, band=band,
            radius=plan["Rstar"], target=plan["local_target"], incoming=P,
            largest_descriptor=reference.target_size)
        window = window_source.make_window(reference, origin=origin, length=side,
            interior_blocks=(tuple(source["interior"]),), band=band, cap=1,
            block=sufficient["block"], precision=P, width=width,
            radius=plan["Rstar"], target=plan["local_target"])
        upper = tuple(tuple(factors["factors"][3][i][j] for j in window.E) for i in window.E)
        s = max(sum(bool(x) for x in row) for row in upper)
        forward_error = Q(s * plan["Rstar"] + 6, 1 << P)
        need(forward_error <= pow2(-plan["local_target"]), "actual upper-action precision")
        need(max(Q(1), row_norm(upper)) * plan["Rstar"] < 1 << (width - P - 1),
             "actual upper-action signed carrier range")
        adapter = load("_physical_observer_admitted_context", package / "admitted_context.py")
        partition = adapter.AdmittedPartition(runtime, reference, "narrow", origin,
            side, len(source["interior"]), (tuple(source["interior"]),))
        regenerated_programs = [adapter.prepare(runtime, ((partition,),), direction,
            target=plan["stage_target"], radius_bits=rb, incoming=P, fractional_bits=P)
            for direction in (True, False)]
        programs = receipt["dense_programs"]
        need(len(programs) == 2, "the two actual stored dense directions")
        for actual, program in zip(regenerated_programs, programs):
            need(canonical_json(actual.record()) == canonical_json(program),
                 "actual authenticated source preparation reproduces the complete dense certificate")
            need(program["labels"] == program["axes"] == 1 and program["side"] == side
                 and program["records"] == 2 and program["global_grid"] == program["incoming_bits"] == P,
                 "same complete dense geometry and common grid")
            need(program["target_bits"] == plan["stage_target"]
                 and program["radius_bits"] == rb
                 and Q(program["total_error"]) < pow2(-plan["stage_target"]),
                 "actual dense numerical certificate")
        need(programs[0]["directions"] == [[True]] and programs[1]["directions"] == [[False]],
             "actual inverse and forward source directions")
        allowances = (regenerated_programs[0].total_error, plan["V2"] * window.total_error,
                      regenerated_programs[1].total_error, plan["V2"] * forward_error,
                      regenerated_programs[0].total_error)
        names = ("D_Ainv_1", "T1", "D_A", "T2", "D_Ainv_2")
        observations = []
        for kind, name in zip(KINDS, names):
            row = receipt["observations"][name]
            observations.append(dict(kind=kind, input=row["input"], output=row["output"],
                input_precision=P, output_precision=P, input_width=width, output_width=width,
                input_radius=plan["R2"]))
        checked = check_stages(((q,),), ((tuple(source["interior"]),),), receipt["initial"], P,
                              observations, allowances, plan["target"], common_precision=P)
        interpreted_dense = []
        for stage, observed in enumerate(observations):
            before = tuple(tuple(value) for value in observed["input"])
            after = tuple(tuple(value) for value in observed["output"])
            if stage in (0, 2, 4):
                expected, counts = dense_replay(runtime, regenerated_programs[int(stage == 2)], before)
                interpreted_dense.append(counts)
            else:
                actual = list(decode_pairs(before, P))
                rows = tuple(actual[i] for i in window.E)
                if stage == 1:
                    result = first_inverse(window, rows)
                else:
                    lift = max(abs(2 * i - (2 * j + 1)) for i, row in enumerate(upper)
                               for j, value in enumerate(row) if value)
                    block = 1 << ceil_log2(max(2, lift))
                    result = supplied_action(upper, rows, block, P)
                for index, value in zip(window.E, result):
                    actual[index] = value
                expected = tuple(tuple(int(x * (1 << P)) for x in value) for value in actual)
                need(decode_pairs(expected, P) == tuple(actual), "staged interpreter returns the common grid")
            need(expected == after, "every physical word equals independent staged semantics: " + names[stage])
        need(receipt["returned"] == receipt["observations"][names[-1]]["output"],
             "protected physical return equals actual final stage")
        need(receipt["complete_dense_calls"] == 3 and receipt["complete_dense_events"] ==
             2 * programs[0]["stages"] + programs[1]["stages"], "complete physical dense count")
        need(all(s["stages"] == s["global_H_calls"] + s["global_diagonal_calls"] for s in programs),
             "actual source H and diagonal event cardinalities")
        checked.update(physical_receipt_sha256=sha256(raw).hexdigest(),
            reviewed_physical_execution=True, reviewer_replayed_physical_execution=False,
            regenerated_reference=True, regenerated_dense_certificates=True,
            identity_interior_limitation=True,
            complete_dense_events=receipt["complete_dense_events"],
            staged_bitwise_agreement=True, independently_interpreted_dense=interpreted_dense,
            source_reference_sha256=reference.description_hash)
        print(canonical_json(checked))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Pinned physical run, original-matrix checks and executed negative controls.
Prepared for @CubeJerry with OpenAI Codex assistance. Apache-2.0.
Host containers/decoders in this verifier are external fixtures and oracles.
"""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
from time import perf_counter
from types import ModuleType

PACKAGE = Path(__file__).resolve().parent


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


S = load("fine_gap_sources", PACKAGE / "sources.py")
C = load("fine_gap_coefficients", PACKAGE / "coefficients.py")
CC = load("fine_gap_coefficient_checks", PACKAGE / "coefficient_checks.py")
O = load("fine_gap_original_oracle", PACKAGE / "original_matrix_oracle.py")
R = load("fine_gap_rounded_oracle", PACKAGE / "rounded_oracle.py")
H = load("fine_gap_cleanup_check", PACKAGE / "cleanup_check.py")


def rejected(name, operation, message=None):
    try:
        operation()
    except ValueError as error:
        need(message is None or str(error) == message, name + ": unexpected failure: " + str(error))
        return name
    raise ValueError(name + ": negative control escaped")


def snapshot(tapes):
    return tuple((bytes(t.cells), t.head) for t in tapes)


def unique(tapes):
    return tuple({id(t): t for t in tapes}.values())


def actions(tapes):
    return sum(t.meter.reads + t.meter.writes + t.meter.moves for t in unique(tapes))


def owned_blank(owner):
    from words import BLANK
    for tape in unique(owner.forbidden()):
        need(tape.head == 1 and all(cell == BLANK for cell in tape.cells), "all fixed owned roles erased at origin")
    owner.idle()


def main():
    need(sys.argv[1:] in ([], ["--long"]), "only optional --long replay flag")
    extended = bool(sys.argv[1:])
    raw = S.authenticated_inputs()
    factory = lambda parameters: S.make_reference(raw, parameters)
    coefficient_receipt = CC.run(C, factory)
    O.selfcheck()
    reference = factory((61, 3, 1, 4, 8, 80))
    receipts, controls = [], []
    with S.physical_runtime():
        from cardinal_counts import Count
        from check_support import no_decode
        from records import Tape
        from router_metadata import owned
        from run_consumer import RunInverse
        from run_pages import EncodedPages, emit_stream
        from session import borrowed_count, erase_marker, initialize_marker, sealed_constructors
        from words import BLANK
        cleanup_receipt = H.run(Tape, BLANK)

        tape_for = emit_stream

        def decoded_output(output, length, width):
            bits = []
            for _ in range(length * width):
                bit = output.read()
                need(bit in (0, 1), "complete physical output bit")
                bits.append(bit); output.step(1)
            need(output.read() == BLANK, "exact physical output extent")
            return O.decode_twos_complement_bits(bits, width)

        owner = RunInverse()
        fixed_roles = len(unique(owner.forbidden()))
        owned_blank(owner)
        for length in ((20, 2, 1) if extended else (8, 2, 1)):
            pages = C.prepare(reference, 11, length, 1, 8)
            p = pages.plan
            words = tuple(((-1 if i % 2 else 1) * (i+1) * (1 << p.f)) // (2*length+1) for i in range(length))
            need(max(map(abs, words)) <= 1 << p.f, "funded physical input radius")
            with EncodedPages(pages) as encoded:
                counts = encoded.counts
                tapes = (tape_for(words, counts[2]), *encoded.streams)
                all_ports = tapes + tuple(v.tape for v in counts)
                before = snapshot(all_ports)
                all_tapes = unique((*owner.forbidden(), *all_ports))
                before_actions = actions(all_tapes)
                before_scalar = dict(owner.scalar_word.calls)
                before_packed = dict(owner.convolution.word.calls)
                before_blocks = owner.blocks
                start = perf_counter()
                with no_decode():
                    output = owner.run(*tapes, *counts)
                seconds = perf_counter() - start
                measured_actions = actions(all_tapes) - before_actions
                need(before == snapshot(all_ports), "all eleven borrowed bodies and origins restored")
                actual = decoded_output(output, p.n, p.W)
                need(actual == R.action(words, pages), "exact rounded-stage physical equality")
                output.clear(); erase_marker(output)
                owned_blank(owner)
                retained_cells = sum(len(t.cells) for t in unique(owner.forbidden()))
                need(len(unique(owner.forbidden())) == fixed_roles, "unchanged fixed role inventory")
                blocks = (p.n + p.L - 1) // p.L
                expected_scalar = 0 if p.n == 1 else 9*p.n + 2*p.L*(blocks-1)
                expected_packed = 0 if p.n == 1 else 8*blocks
                scalar = {key: owner.scalar_word.calls[key] - before_scalar[key] for key in before_scalar}
                packed = {key: owner.convolution.word.calls[key] - before_packed[key] for key in before_packed}
                need(sum(scalar.values()) == expected_scalar and sum(packed.values()) == expected_packed,
                     "exact complete multiplication invoice")
                need(owner.blocks - before_blocks == (0 if p.n == 1 else 2*blocks), "both residual orientations")
                matrix, provenance = O.original_reference_matrix(reference, p.start, p.n)
                check = O.check_output(matrix, words, actual, p.f, p.total_error)
                if length > 2:
                    need(p.L < p.n and p.n % p.L, "overlap and short final block exercised")
                    need(R.action(words, pages, reverse_f=True) != actual, "original F-index mutation changes exact words")
                    transposed = tuple(tuple(matrix[j][i] for j in range(p.n)) for i in range(p.n))
                    controls.extend((
                        rejected("transpose_original_matrix", lambda: O.check_output(transposed, words, actual, p.f, p.total_error), "original-reference action error"),
                        rejected("reverse_return_order", lambda: O.check_output(matrix, words, actual[::-1], p.f, p.total_error), "original-reference action error"),
                        rejected("changed_return_unit", lambda: O.check_output(matrix, words, (actual[0] + (1 << p.f), *actual[1:]), p.f, p.total_error), "original-reference action error"),
                        "original_F_index_bit_control"))
                if length == 1:
                    controls.append(rejected("aliased_descriptors", lambda: owner.run(*tapes, counts[0], counts[0], counts[2], counts[3]), "pairwise disjoint run and descriptor ports"))
                    controls.append(rejected("aliased_streams", lambda: owner.run(tapes[0], tapes[0], *tapes[2:], *counts), "pairwise disjoint run and descriptor ports"))
                    bad_count = borrowed_count(counts[0])
                    bad_count.tape = owner.scalar_word.product.twiddles.pool.tapes[0]
                    controls.append(rejected("inactive_descendant_alias", lambda: owner.run(*tapes, bad_count, *counts[1:]), "external run ports"))
                    truncated = tape_for(pages.streams["residual_plus"][:-1], counts[2])
                    try:
                        controls.append(rejected("truncated_residual_page", lambda: owner.run(*tapes[:-1], truncated, *counts), "complete fixed-width binary key"))
                        owned_blank(owner)
                    finally:
                        truncated.clear(); erase_marker(truncated)
                    need(before == snapshot(all_ports), "rejected controls preserve borrowed state")
                receipts.append(dict(n=p.n, L=p.L, W=p.W, f=p.f, seconds=seconds,
                    physical_actions=measured_actions, scalar_products=scalar, packed_products=packed,
                    fixed_roles=fixed_roles, outer_pool_peak=owner.pool.peak,
                    retained_owned_cells=retained_cells,
                    page_bits=sum(map(len, pages.streams.values())) * p.W,
                    maximum_error=float(check["maximum_error"]), residual=float(check["residual_norm"]),
                    allowance=float(p.total_error), source=provenance,
                    words_sha256=sha256(json.dumps(actual).encode()).hexdigest(),
                    pages_sha256=pages.receipt()["stream_sha256"]))
                tapes[0].clear(); erase_marker(tapes[0])

        def recurrence_probe(engine):
            with owned(Count.literal(2), Count.literal(8), Count.literal(2)) as (n, width, precision):
                source = tape_for((1, 1), width)
                mu = tape_for((0, 1), width)
                destination = Tape()
                for tape in engine.pool.tapes:
                    initialize_marker(tape)
                try:
                    with no_decode(), sealed_constructors(), engine.scope.installed():
                        engine.recurrence(source, mu, destination, n, width, precision)
                        engine.pool.empty()
                    result = decoded_output(destination, 2, 8)
                finally:
                    for tape in engine.pool.tapes:
                        erase_marker(tape)
                    for tape in (source, mu, destination):
                        tape.clear(); erase_marker(tape)
                owned_blank(engine)
                return result

        need(recurrence_probe(owner) == (1, 0), "completed difference before truncation")
        original = (PACKAGE / "run_consumer.py").read_text()
        correct = "with owned(difference(wide_rhs, product)) as (residual,):\n                                following = truncate(residual, precision)"
        wrong = "with owned(truncate(product, precision)) as (wrong_product,):\n                                following = difference(rhs, wrong_product)"
        need(original.count(correct) == 1, "unique literal recurrence mutation")
        mutant = ModuleType("fine_gap_product_first_mutation")
        exec(compile(original.replace(correct, wrong), "<intentional product-first mutation>", "exec"), mutant.__dict__)
        need(recurrence_probe(mutant.RunInverse()) == (1, 1), "executed premature-product-rounding counterexample")
        controls.append("literal_product_first_rounding_mutation")
        owned_blank(owner)

    print("PASS_PHYSICAL_FINE_GAP_RUN", flush=True)
    print(json.dumps(dict(extended=extended, fixtures=receipts, controls=controls,
                         coefficient_checks=coefficient_receipt, cleanup_checks=cleanup_receipt,
                         source_files={p.name: sha256(p.read_bytes()).hexdigest() for p in
                         (PACKAGE / "run_consumer.py", PACKAGE / "coefficients.py", PACKAGE / "original_matrix_oracle.py")}),
                     sort_keys=True), flush=True)


if __name__ == "__main__":
    main()

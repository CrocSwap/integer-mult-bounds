"""Generated four-family GL2(F3) caller, including private and global operations."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import sys
from time import monotonic
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader
loader.activate()
from cardinal_counts import Count
from check_headers import residual_address
from check_runtime import destination
from check_support import no_decode
from controller import finite_word
from directory import Context
from forms import fallback_form, good_form
from macro_code import Residual, compile_node
from macro_machine import Machine
from matrices import Matrices
import model
from numeric import Page
import oracle
from plan import compile_plan
from records import RECORD_END, Tape, read_finite, read_word
import scheduler
from trace import execute
from words import Arena, BLANK, Ring, need


def body(tape):
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def request_key(request):
    return (request.kind, request.reference, request.reverse_adapter, request.child_kind,
            request.field, request.reverse, request.negative_inverse, request.half)


class Binding:
    """Only the fixed w1/n2/weights(2,1) model may use these compiled scalars."""
    cutoff, stock_multiple, child_mode = 2, 1, 0

    def __init__(self, catalogue, definitions, projectors):
        self.catalogue, self.codes = catalogue, catalogue.codes
        self.definitions, self.projectors = definitions, projectors

    def residual(self, identifier, common, low, mode):
        need(mode == 0, "one first-range fixture program")
        return self.definitions[(identifier, common, low)]

    def incoming(self, runtime):
        def coefficient(prefix, request):
            need(prefix.read() == BLANK and request.kind == "incoming", "fixture frozen-only root")
            value = (2, 1)[finite_word(request.coordinate, 2)]
            if request.negative_inverse:
                value = (-pow(value, -1, 3)) % 3
            return runtime.arena.literal(value)
        return SimpleNamespace(coefficient=coefficient)

    def validate_residual(self, runtime, definition, first):
        two = runtime.indices.literal(2)
        try:
            need(runtime.depth.zero() and runtime.context.raw.compare(runtime.context.cap, runtime.context.ring.one) == 0
                 and runtime.indices is runtime.size.arena and
                 runtime.context.q == 3 and runtime.context.dimension == 2 and
                 runtime.context.ring.raw.arena is runtime.arena,
                 "first-range fixture domain")
            from words import Unsigned
            need(Unsigned(runtime.indices).compare(runtime.size, two) == 0, "fixture f equals one")
        finally:
            runtime.indices.free(two)

    def coefficient(self, runtime, definition, prefix, request):
        need(request.coordinate.zero(), "fixture coefficient coordinate zero")
        prefix.rewind()
        need(read_finite(prefix, self.codes.bits) == definition.code, "exact fixture request and view code")
        for _ in range(4):
            word = read_word(prefix, runtime.arena)
            try:
                need(word.zero(), "complete w1 high field is zero")
            finally:
                runtime.arena.free(word)
        need(prefix.read() == RECORD_END, "fixture current field terminator")
        prefix.step(1)
        need(prefix.read() == BLANK, "fixture current field is last")
        prefix.rewind()
        return runtime.arena.literal(definition.constants[request_key(request)])

    def child_program(self, *_args):
        raise ValueError("first-range fixture has no internal child")

    def check_stock(self, runtime):
        expected = Count.literal(1)
        try:
            need(expected.equals(runtime.count("unused")), "fixture unused row quotient")
        finally:
            expected.close()


def compile_binding(catalogue, context, indices):
    ring, matrices = context.ring, Matrices(context.ring)
    incoming = model.Incoming(context, indices, (2, 1))
    definitions, projectors, cache = {}, {}, {}
    try:
        for identifier, request in enumerate(catalogue.requests):
            common = request.kind != "IDLE"
            basis = model.I if request.base == 0 else model.S
            chart = model.I if common else request.chart
            preparation = tuple(tuple(sum(chart[i][k] * basis[k][j] for k in range(2))
                                      for j in range(2)) for i in range(2))
            for low in catalogue.low_classes():
                header = oracle.multiply(low, oracle.reduce_rational(preparation, 3), 3)
                projector = tuple(map(tuple, oracle.multiply([[row[0]] for row in header], oracle.inverse(header, 3)[:1], 3)))
                if projector not in cache:
                    plan = compile_plan(projector, 1, 3, projector[0][0] != 0)
                    encoded = matrices.constants(projector)
                    form = good_form(encoded, 1, ring) if plan.good else fallback_form(encoded, ring)
                    columns, depth = indices.literal(1), indices.zero()
                    page = Page(plan, form, ring, indices, columns, incoming.weight, depth, 0, object())
                    constants = {}
                    for event in execute(page):
                        if event.request is None:
                            continue
                        need(event.request.coordinate.zero(), "compile only fixture coordinate zero")
                        value = page.evaluate(event.request)
                        key, scalar = request_key(event.request), value.inspect()
                        need(key not in constants or constants[key] == scalar, "one finite fixture coefficient per key")
                        constants[key] = scalar
                        ring.arena.free(value)
                    page.close()
                    matrices.free(encoded)
                    indices.free_many(columns, depth)
                    cache[projector] = plan, constants
                plan, constants = cache[projector]
                code = catalogue.codes.encode(identifier, common, low)
                definitions[(identifier, common, low)] = Residual(code, plan, identifier, common, low, constants=constants)
                projectors[code] = projector
    finally:
        incoming.close()
    need(len(definitions) == 672 and len(cache) == 12, "complete fixed fixture binding compilation")
    return Binding(catalogue, definitions, projectors)


def run(gap_size=2):
    started = monotonic()
    catalogue = model.Catalogue()
    topology = model.Topology(catalogue)
    arena, indices = Arena(3), Arena(8)
    modulus = arena.input(3)
    ring = Ring(modulus)
    context = Context(ring, catalogue.codes)
    binding = compile_binding(catalogue, context, indices)
    code = compile_node(topology, binding)
    context.close()
    ring.close()
    size, depth = indices.input(2), indices.zero()
    source, directory, program = Tape(), Tape(), Tape()
    fibre_size, length = 81 * gap_size, 192 * 81 * gap_size
    for i in range(length):
        source.append(((i * 13) ^ (i >> 3) ^ (i >> 7) ^ 0x53) & 1)
    source.rewind()
    original = body(source)
    counts = [Count.literal(value) for value in (1, 192, 1, gap_size, 1)]
    residuals, checkpoints = Counter(), []
    private = {}
    copy_checks = 0
    def observe(machine, kind, *labels):
        nonlocal copy_checks
        if kind == "copy_source":
            src, dst = labels
            need(not private, "one private-copy checker scope")
            private.update(source=src, copied=body(machine.tape(src)))
            need(body(machine.tape(dst)) == private["copied"], "complete private source clone")
        elif kind == "residual_begin":
            definition, role = labels
            request = catalogue.requests[definition.identifier]
            residuals[request.kind] += 1
            if request.kind == "COPY":
                need(private and body(machine.tape(role)) == private["copied"], "COPY enters its retained dirty source")
        elif kind == "residual_end":
            definition, role = labels
            if catalogue.requests[definition.identifier].kind == "COPY":
                expected = bytearray(fibre_size)
                for address in range(fibre_size):
                    target = residual_address(address, binding.projectors[definition.code], (2, 1), 3, gap_size)
                    expected[target] = private["copied"][address]
                need(body(machine.tape(role)) == expected and
                     body(machine.tape(private["source"])) == private["copied"],
                     "independent dirty COPY endpoint and unchanged source before cancelling XORs")
                private.clear()
                copy_checks += 1
        elif kind == "local_cover_sweep" and labels[0] in (0, 1):
            stage = labels[0]
            family = body(machine.tape(("family", 0)))
            for low in range(48):
                for address in range(fibre_size):
                    target = destination(address, 2, 3, (2, 1), gap_size) if stage == 0 else address
                    need(family[low * fibre_size + target] == original[low * fibre_size + address],
                         "independent intermediate family endpoint before sweep cancellation")
            checkpoints.append(stage)
    machine = Machine(binding, topology, (code,), Arena(3, 512), Arena(8, 512), observe)
    print("compiled local model", len(code.operations), "instructions", file=sys.stderr, flush=True)
    def reject_invocation(*_args, **_kwargs):
        raise ValueError("source recursive Invocation reached the physical controller")
    with no_decode(), patch.object(scheduler.Invocation, "__init__", reject_invocation):
        output = machine.run(source, directory, program, modulus, size, depth, *counts)
    actual = body(output)
    expected = bytearray(length)
    for row in range(192):
        for address in range(fibre_size):
            target = destination(address, 2, 3, (2, 1), gap_size)
            expected[row * fibre_size + target] = original[row * fibre_size + address]
    need(actual == expected and body(source) == original and not body(directory) and not body(program),
         "complete four-family caller endpoint and borrowed input preservation")
    need(checkpoints == [0, 1] and copy_checks == 96 and not private and
         residuals == {"MOVE": 192, "COPY": 96, "IDLE": 384}, "complete chronological fixture coverage")
    need(machine.closed and not machine.arena.live and not machine.indices.live and
         machine.numerical.machine.tapes == [{}, {}] and
         all(all(symbol == BLANK for symbol in tape.cells)
             for tape in (*machine.roles.values(), *machine.handoff.values(), *machine.pool.tapes)),
         "complete first-range fixed workspace cleanup")
    result = dict(domain="q3 w1 n2 four-family fixture with weights(2,1)", addresses=length,
                  gap=gap_size, instructions=len(code.operations), counts=machine.counts,
                  residuals=dict(residuals), private_copy_oracles=copy_checks,
                  intermediate_sweeps=checkpoints, payload_sha256=sha256(actual).hexdigest(),
                  peak_scratch_leases=machine.pool.peak, scratch_capacity=len(machine.pool.tapes),
                  numerical_slots=[len(machine.arena.words), len(machine.indices.words)])
    source.clear()
    directory.clear()
    program.clear()
    output.clear()
    for count in counts:
        count.close()
    arena.free(modulus)
    indices.free_many(size, depth)
    need(not arena.live and not indices.live, "closed local fixture input banks")
    print("generated local controller completed in", round(monotonic() - started, 2), "seconds", file=sys.stderr)
    return result


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2, sort_keys=True))

"""Separate selected generated coefficients from the reduced GL2 fixture."""
from types import SimpleNamespace

import loader
loader.activate()
from children import extend
from controller import Callback
from macro_code import Residual
from numeric import selected_coefficient
import oracle
from plan import Plan, Request
from records import Fields, Program, append_finite
from words import need


def view(cls, runtime, tape):
    result = object.__new__(cls)
    result.index_arena, result.residue_arena = runtime.indices, runtime.arena
    result.code_bits = runtime.binding.codes.bits
    result.tape = tape
    return result


class SelectedBinding:
    cutoff, stock_multiple, child_mode = 64, 9475, 0

    def __init__(self, specifications):
        self.specifications = specifications
        self.catalogue = specifications.catalogue
        self.codes = self.catalogue.codes
        self.ambient = specifications.bind(0, True, tuple(map(tuple, oracle.eye(64)))).code

    def residual(self, identifier, common, low, mode):
        need(mode == 0, "one selected source program")
        request = self.catalogue.requests[identifier]
        need(common == (request.kind != "IDLE"), "selected common/native source view")
        spec = self.specifications.bind(identifier, common, low)
        return Residual(spec.code, self.specifications.plan(spec.code), identifier, common, low)

    def incoming(self, runtime):
        def coefficient(prefix, request):
            need(request.kind == "incoming", "incoming coefficient grammar")
            fields = view(Fields, runtime, prefix)
            frame = Callback(runtime.context.ring, runtime.indices, runtime.program, fields,
                             self.specifications, self.ambient, allow_fallback=True, leaf=True)
            try:
                raw = frame.raw
                need(raw.compare(frame.final_size, runtime.size) == 0 and
                     raw.compare(frame.depth, runtime.depth) == 0, "incoming frame width and depth")
                value = frame.weight(request.coordinate)
                if request.negative_inverse:
                    inverse = runtime.context.ring.inverse(value)
                    need(inverse is not None, "incoming unit inverse")
                    following = runtime.context.ring.negate(inverse)
                    runtime.arena.free_many(value, inverse)
                    value = following
                frame.close()
                return value
            except BaseException:
                frame.abort()
                raise
        return SimpleNamespace(coefficient=coefficient)

    def validate_residual(self, runtime, definition, first):
        frame = Callback(runtime.context.ring, runtime.indices, runtime.program,
                         view(Fields, runtime, first), self.specifications,
                         definition.code, allow_fallback=True)
        try:
            need(frame.raw.compare(frame.final_size, runtime.size) == 0 and
                 frame.raw.compare(frame.depth, runtime.depth) == 0, "current residual frame binding")
            frame.close()
        except BaseException:
            frame.abort()
            raise

    def coefficient(self, runtime, definition, prefix, request):
        return selected_coefficient(definition.plan, runtime.context.ring, runtime.indices,
                                    runtime.program, view(Fields, runtime, prefix),
                                    self.specifications, definition.code, request)

    def child_program(self, runtime, definition, event, first):
        callback = Callback(runtime.context.ring, runtime.indices, runtime.program,
                            view(Fields, runtime, first), self.specifications,
                            definition.code, allow_fallback=True)
        zero = runtime.indices.zero()
        try:
            result = extend(callback, Request("child", zero, child_kind=event.child_kind,
                                             field=event.field, reverse=event.reverse, half=event.half))
            callback.close()
            return result.tape
        except BaseException:
            callback.abort()
            raise
        finally:
            runtime.indices.free(zero)

    def check_stock(self, runtime):
        pass


class ToyBinding:
    """Fixture-only q2/dimension2 grammar; production uses SelectedBinding."""
    cutoff, stock_multiple, child_mode = 2, 1, 0

    def __init__(self, catalogue, plans):
        self.catalogue, self.codes, self.plans = catalogue, catalogue.codes, plans

    def residual(self, identifier, common, low, mode):
        need(common and identifier in (0, 1) and mode in (0, 1), "toy MOVE binding")
        plan, constants = self.plans[(identifier, low)]
        code = self.codes.encode(identifier, common, low)
        if mode:
            return Residual(code, Plan(2, 1, True, ()), identifier, common, low,
                            axis=identifier, constants=constants)
        return Residual(code, plan, identifier, common, low, constants=constants)

    def incoming(self, runtime):
        return SimpleNamespace(coefficient=lambda _prefix, _request:
                               runtime.arena.copy(runtime.context.ring.one))

    def validate_residual(self, runtime, definition, first):
        pass

    def coefficient(self, runtime, definition, prefix, request):
        if request.kind == "child":
            return runtime.arena.copy(runtime.context.ring.one)
        return runtime.arena.literal(definition.constants[(request.reference, request.reverse_adapter)])

    def child_program(self, runtime, definition, event, first):
        # The retained toy grammar uses only Program identity. Carry a finite
        # source-label record as extra inert data to exercise descriptor parking.
        result = runtime.pool.acquire()
        from directory import append_tape
        append_tape(runtime.program.tape, result)
        append_finite(result, definition.code, self.codes.bits)
        result.rewind()
        return result

    def check_stock(self, runtime):
        from cardinal_counts import Count
        expected = Count.literal(6 if runtime.root else 1)
        try:
            need(expected.equals(runtime.count("unused")), "toy exact independent fresh stock")
        finally:
            expected.close()

"""Focused coefficient admission checks; preparation only, no physical consumer replay.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0."""
from dataclasses import replace

def rejected(C, name, operation, text):
    try:
        operation()
    except ValueError as error:
        C.need(str(error) == text, name + ': different rejection: ' + str(error))
        return name
    raise ValueError(name + ': escaped rejection')

def run(C, make_reference):
    ref = make_reference((61, 3, 1, 4, 8, 80))
    before = tuple(map(len, (ref.entries, ref.weights, ref.kernel)))

    def forbidden(*args, **kwargs):
        raise RuntimeError('producer queried a global Reference entry')
    ref.entry = forbidden
    pages = C.prepare(ref, 11, 20, 1, 8)
    strong = C.prepare(ref, 11, 20, 1, 48)
    single = C.prepare(ref, 11, 1, 1, 16)
    C.need(before == tuple(map(len, (ref.entries, ref.weights, ref.kernel))) == (0, 0, 0), 'no global coefficient or full-run weight materialized')
    C.need(single.plan.L == 1, 'singleton residual cap')
    unit = 1 << single.plan.f
    C.need(single.streams == {'Finv': (unit,), 'F': (unit,), 'mu_minus': (0,), 'mu_plus': (0,), 'residual_minus': (unit, unit, unit), 'residual_plus': (unit, unit, unit)}, 'singleton exact identity pages')
    producer = C.Producer(ref, pages.plan)
    grid = 1 << producer.bits - pages.plan.f
    box = producer.Interval(3 * grid + grid // 2, 4 * grid + grid // 2 - 1, producer.bits)
    rounded = producer.quantize(box)
    C.need(rounded == 3 and box.hi - rounded * grid > grid, 'one-ulp counterfactual actually fails')
    controls = [rejected(C, 'mixed_phase', lambda: C.prepare(ref, 11, 21, 1, 8), 'one original phase interval'), rejected(C, 'wrap_interval', lambda: C.prepare(ref, 51, 20, 1, 8), 'ordinary nonwrapping source interval'), rejected(C, 'underfunded_reference', lambda: C.prepare(ref, 11, 20, 1, 80), 'fixed Reference error exceeds run allocation'), rejected(C, 'interval_too_wide', lambda: producer.quantize(producer.Interval(0, grid + 1, producer.bits)), 'coefficient interval below one data unit'), rejected(C, 'zero_reciprocal', lambda: producer.reciprocal(producer.Interval(0, 1, producer.bits)), 'positive reciprocal denominator')]
    weak = replace(strong.plan, interval_bits=strong.plan.f + 2 * C.ceil_log2(strong.plan.n + 1) + 16)
    controls.append(rejected(C, 'omitted_gauge_precision', lambda: C.Producer(ref, weak).build(), 'coefficient interval below one data unit'))
    production_ref = make_reference((65521, 15, 3, 4, 32, 256))
    plan = C.make_plan(production_ref, 2185, 4368, 1, 64)
    C.need(plan.L < plan.n and plan.interval_bits < production_ref.weight_precision, 'run metadata separates local and full-run precision')
    C.need(not production_ref.weights and (not production_ref.entries), 'large source metadata did not materialize data')
    return {'regular': {'L': pages.plan.L, 'W': pages.plan.W, 'f': pages.plan.f, 'sha256': pages.receipt()['stream_sha256']}, 'large_gauge': {'L': strong.plan.L, 'h': strong.plan.gauge_bits, 'f': strong.plan.f, 'Q': strong.plan.interval_bits}, 'singleton_identity': True, 'one_ulp_counterfactual_rejected': True, 'controls': controls, 'source_entries_materialized': 0, 'metadata_only': {'parameters': [65521, 15, 3, 4, 32, 256], 'start': plan.start, 'n': plan.n, 'L': plan.L, 'f': plan.f, 'W': plan.W, 'Q': plan.interval_bits, 'unused_global_weight_precision': production_ref.weight_precision}}

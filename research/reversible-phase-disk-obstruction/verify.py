#!/usr/bin/env python3
"""Authenticate sources, execute exact witnesses and compare a typed receipt."""
from fractions import Fraction as F
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from model import (need, load_source, norm2, disk, error25, phase_box,
                   refined_product, refined_inverse, lift, strict_json_equal)


def rejection(f, label):
    try:
        f()
    except ValueError:
        return
    raise ValueError('control accepted: ' + label)


def run():
    intervals, kernel = load_source()
    need(F(2, 5) > F(16, 4**3), 'exact obstruction threshold')
    need(F(4, 5) < F(16, 4**2), 'identity feasible at p=2')
    need(F(21, 20)**2 + F(9, 10)**2 == F(153, 80) < 4,
         'all-input shear bound')
    by_precision, total, refined_cases, lift_cases, oracle_cases = [], 0, 0, 0, 0
    for p in range(1, 7):
        s = 1 << p
        inputs = disk(p)
        box, inverse_box = phase_box(intervals, p), phase_box(intervals, p, -1)
        w, _ = intervals.inward_quantize(box, p)
        need(w == (3*s//5, 4*s//5), 'rational inward phase binding')
        images, refined_images, norm_loss = set(), set(), 0
        max_error25 = 0
        for x in inputs:
            y = kernel.phase_product(intervals, x, box, p)
            need(norm2(y) <= norm2(x), 'actual forward norm contract')
            e = error25(x, y)
            need(e < 400, 'actual forward four-h error')
            kernel.rect_error(x, y, box, p)
            max_error25 = max(max_error25, e)
            norm_loss += norm2(y) < norm2(x)
            images.add(y)
            back = kernel.phase_product(intervals, y, inverse_box, p)
            need(norm2(back) <= norm2(y) and error25(y, back, -1) < 400,
                 'actual conjugate call remains legal')
            # Same multiplier, doubled denominator, no final product rounding.
            z = refined_product(x, w)
            refined_images.add(z)
            need(refined_inverse(z, w) == x, 'refined exact image inverse')
            need(norm2(z) <= s*s*norm2(x), 'refined physical norm')
            er = 5*z[0] - s*(3*x[0]-4*x[1])
            ei = 5*z[1] - s*(4*x[0]+3*x[1])
            need(er*er + ei*ei < 400*s*s, 'refined four-h error')
            refined_cases += 1
            lifted = lift(x)
            need(lift(lifted, True) == x and lift(lift(x, True)) == x,
                 'lift two-sided exact inverse')
            need(80*error25(x, lifted) <= 25*153, 'lift uniform error')
            lift_cases += 1
            # Retain x: recomputation undoes a dirty accumulator despite collisions.
            dirty = (7-2*x[0], -11+3*x[1])
            accumulated = tuple(a+b for a, b in zip(dirty, y))
            restored = tuple(a-b for a, b in zip(accumulated,
                             kernel.phase_product(intervals, x, box, p)))
            need(restored == dirty, 'out-of-place dirty-output return')
            oracle_cases += 1
            if p <= 2:
                need(error25(x, x) < 400, 'identity boundary positive')
        need(len(refined_images) == len(inputs), 'refined injection')
        need(len(images) < len(inputs), 'actual kernel is not injective')
        by_precision.append(dict(p=p, inputs=len(inputs), distinct_outputs=len(images),
                                 strict_norm_decreases=norm_loss,
                                 max_error_squared_times25_in_grid_units=max_error25))
        total += len(inputs)
    for p in range(1, 129):
        box = phase_box(intervals, p)
        zero = kernel.phase_product(intervals, (0, 0), box, p)
        tiny = kernel.phase_product(intervals, (1, 0), box, p)
        need(zero == tiny == (0, 0), 'actual collision precision instance')
    box, inverse_box = phase_box(intervals, 3), phase_box(intervals, 3, -1)
    forward = kernel.phase_product(intervals, (8, 0), box, 3)
    back = kernel.phase_product(intervals, forward, inverse_box, 3)
    need(forward == (4, 6) and back == (6, 0), 'exact source roundtrip witness')
    outward = lift((0, 8))
    need(outward == (-7, 5) and norm2(outward) == 74, 'outward slack witness')
    controls = []
    def reject_claim(label, condition):
        rejection(lambda: need(condition, label), label)
        controls.append(label)
    reject_claim('injective_actual_kernel', (0, 0) !=
                 kernel.phase_product(intervals, (1, 0), box, 3))
    reject_claim('conjugate_is_exact_inverse', back == (8, 0))
    reject_claim('lift_preserves_closed_disk', norm2(outward) <= 64)
    clipped = (0, 0) if norm2(outward) > 64 else outward
    reject_claim('clipping_preserves_lift_inverse', lift(clipped, True) == (0, 8))
    fine = refined_product((8, 0), (4, 6))
    reject_claim('refined_output_has_same_denominator', norm2(fine) <= 64)
    reject_claim('nonincrease_alone_preserves_shells', norm2((0, 0)) == norm2((8, 0)))
    rejection(lambda: kernel.phase_product(intervals, (9, 0), box, 3), 'input outside disk')
    controls.append('source_rejects_outside_input')
    rejection(lambda: refined_inverse((1, 0), (4, 6)), 'outside refined image')
    controls.append('refined_inverse_requires_image')
    gaussian = 0
    for p in range(1, 7):
        for x in disk(p):
            y = x
            for _ in range(4):
                need(norm2(y) == norm2(x), 'Gaussian unit shell')
                y = (-y[1], y[0])
            need(y == x, 'Gaussian unit exact return')
            gaussian += 4
    return dict(status='PASS_REVERSIBLE_PHASE_DISK_BOUNDARY', source_disk_inputs=total,
                source_calls_per_input=3, by_precision=by_precision,
                collision_precisions_checked=128, refined_grid_cases=refined_cases,
                lifted_inverse_cases=lift_cases, retained_input_oracle_cases=oracle_cases,
                gaussian_unit_cases=gaussian, semantic_controls=controls,
                p3_roundtrip_numerators=[[8, 0], list(forward), list(back)],
                p3_outward_lift_numerators=[[0, 8], list(outward)],
                obstruction='all p>=3; fixed (3+4i)/5, total injective D_p->D_p, nonincrease, error<4h',
                minimum_boundary_error_squared='2/5',
                lifted_uniform_squared_error_over_h_squared='153/80',
                limits='In-place fixed-helper-fiber only; no selected phase, cleanup, native cost or supplier claim.')


if __name__ == '__main__':
    result = run()
    args = sys.argv[1:]
    if args[:1] == ['--output'] and len(args) == 2:
        with Path(args[1]).open('x', encoding='utf-8') as out:
            json.dump(result, out, indent=2, sort_keys=True)
            out.write('\n')
    else:
        need(not args, 'unknown arguments')
        strict_json_equal(result, json.loads((HERE / 'RESULT.json').read_text()))
    print('PASS_REVERSIBLE_PHASE_DISK_BOUNDARY inputs={} refined={} controls={}'.format(
        result['source_disk_inputs'], result['refined_grid_cases'], len(result['semantic_controls'])))

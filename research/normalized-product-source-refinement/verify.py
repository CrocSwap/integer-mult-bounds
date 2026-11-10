#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent symbolic source certificates, with semantic source mutants."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from algebra import need
from flow_certificate import (fft_loop_certificate, lift_layout_certificate, pointwise_stream_certificate,
                              recovery_certificate, stage_body_certificate, whole_run_certificate)
from source_certificate import butterfly_certificate, plan_certificate, signed_helper_certificate
from twiddle_certificate import (interval_helpers, taylor_transfer_certificate,
                                 twiddle_direction_certificate, twiddle_plan_certificate,
                                 twiddle_value_certificate)


def sources():
    result = {}
    pins = json.loads((HERE/'SOURCES.json').read_bytes())
    for row in pins['files']:
        if row['usage'] != 'input':
            continue
        path = ROOT/row['path']
        need(not path.is_symlink(), 'regular source input')
        data = path.read_bytes()
        need(hashlib.sha256(data).hexdigest() == row['sha256'], 'source SHA256 '+row['path'])
        blob = b'blob '+str(len(data)).encode()+b'\0'+data
        need(hashlib.sha1(blob).hexdigest() == row['git_blob'], 'source Git blob '+row['path'])
        result[path.name] = data.decode('utf-8')
    return result


def audit(source):
    words, arithmetic, plan, twiddles, engine = (source[name] for name in (
        'ring_words.py', 'fft_arithmetic.py', 'product_plan.py', 'twiddle_setup.py', 'ring_engine.py'))
    result = {}
    # Source contracts precede installation of their symbolic summaries.
    result['signed_helpers'] = signed_helper_certificate(words, arithmetic)
    result['directed_interval_helpers'] = interval_helpers(words, arithmetic, twiddles)
    result['twiddle_parameters'] = twiddle_plan_certificate(words, arithmetic, twiddles)
    result['taylor_loop_transfer'] = taylor_transfer_certificate(words, arithmetic, twiddles)
    result['twiddle_index_and_endpoint_join'] = twiddle_value_certificate(words, arithmetic, twiddles)
    result['twiddle_direction'] = twiddle_direction_certificate(words, arithmetic, twiddles)
    result['product_parameters'] = plan_certificate(words, arithmetic, plan)
    result['butterfly_dags'] = butterfly_certificate(words, arithmetic)
    result['lift_and_zero_padding'] = lift_layout_certificate(engine)
    result['complete_stage_stream'] = stage_body_certificate(words, arithmetic, engine)
    result['fft_loop'] = fft_loop_certificate(words, arithmetic, engine)
    result['pointwise_stream'] = pointwise_stream_certificate(words, arithmetic, engine)
    result['integer_recovery'] = recovery_certificate(words, arithmetic, engine)
    result['complete_run'] = whole_run_certificate(words, arithmetic, plan, engine)
    return result


def replace_once(source, filename, before, after):
    result = dict(source)
    need(before != after and result[filename].count(before) == 1, 'one precise source mutation: '+before)
    result[filename] = result[filename].replace(before, after, 1)
    return result


def mutants(source):
    cases = [
        ('unknown_AST_while', 'fft_arithmetic.py', 'def dif(self, a, b, c, d, u, v, plan):',
         'def dif(self, a, b, c, d, u, v, plan):\n        while False:\n            pass'),
        ('unknown_service_in_exception', 'fft_arithmetic.py', '            real.close()\n            raise',
         '            unproved_service()\n            real.close()\n            raise'),
        ('early_butterfly_truncation', 'fft_arithmetic.py', 'self.complex_product(dr, di, u, v, plan.word_width)',
         'self.complex_product(truncate(dr, plan.Q), di, u, v, plan.word_width)'),
        ('wrong_DIT_normalization', 'fft_arithmetic.py',
         'return tuple(truncate(value, plan.half_shift) for value in values)',
         'return tuple(truncate(value, plan.Q) for value in values)'),
        ('complex_product_wrong_imaginary_sign', 'fft_arithmetic.py',
         'imaginary = add(ad, bc)', 'imaginary = difference(ad, bc)'),
        ('scalar_word_return_width', 'fft_arithmetic.py', 'size.multiply_small(2)', 'size.multiply_small(1)'),
        ('scalar_product_sign', 'fft_arithmetic.py', 'left.negative != right.negative', 'left.negative == right.negative'),
        ('unsigned_subtract_direction', 'ring_words.py',
         'Signed(subtract(left.magnitude, right.magnitude), left.negative)',
         'Signed(subtract(right.magnitude, left.magnitude), left.negative)'),
        ('wrong_Q_double_precision', 'product_plan.py', 'self.Q.multiply_small(2)', 'self.Q.multiply_small(1)'),
        ('wrong_final_product_scale', 'product_plan.py', 'self.product_shift.add(self.ell)', 'self.product_shift.add(self.m)'),
        ('wrong_directed_quotient', 'twiddle_setup.py', 'if upward and not remainder.zero():', 'if upward:'),
        ('negative_interval_wrong_endpoint', 'twiddle_setup.py',
         'return difference(lower, hi), difference(upper, lo)', 'return difference(lower, lo), difference(upper, hi)'),
        ('outward_positive_choice', 'twiddle_setup.py', 'return Signed(right_shift(lower.magnitude, shift))',
         'return Signed(right_shift(upper.magnitude, shift))'),
        ('Taylor_ceil_replaced_by_floor', 'twiddle_setup.py',
         'next_hi = quotient(high_product, denominator, True)', 'next_hi = quotient(high_product, denominator, False)'),
        ('Taylor_wrong_degree_increment', 'twiddle_setup.py', '                        degree.increment()',
         '                        degree.increment()\n                        degree.increment()'),
        ('Taylor_wrong_padding', 'twiddle_setup.py', 'self.padding.multiply_small(24)', 'self.padding.multiply_small(23)'),
        ('twiddle_wrong_conjugation', 'twiddle_setup.py',
         'imaginary.negative = not imaginary.negative and not imaginary.magnitude.zero()',
         'imaginary.negative = imaginary.negative and not imaginary.magnitude.zero()'),
        ('twiddle_wrong_table_extent', 'twiddle_setup.py', 'for index in indices(plan.half):', 'for index in indices(plan.length):'),
        ('FFT_missing_stage_count', 'ring_engine.py', 'for _ in indices(plan.m):', 'for _ in indices(plan.ell):'),
        ('FFT_wrong_length_growth', 'ring_engine.py', 'length.multiply_small(2)', 'length.multiply_small(4)'),
        ('FFT_wrong_group_division', 'ring_engine.py', 'groups.divide_small(2)', 'groups.divide_small(4)'),
        ('FFT_reversed_group_halves', 'ring_engine.py',
         'append_bits(top, output)\n                        append_bits(bottom, output)',
         'append_bits(bottom, output)\n                        append_bits(top, output)'),
        ('FFT_wrong_inner_extent', 'ring_engine.py', 'for _ in indices(half):', 'for _ in indices(plan.N):'),
        ('omitted_opposite_transform', 'ring_engine.py',
         'self.current = self.fft(self.current, plan, True)', 'self.current = self.current'),
        ('wrong_opposite_transform_sign', 'ring_engine.py',
         'self.current = self.fft(self.current, plan, True)', 'self.current = self.fft(self.current, plan, False)'),
        ('wrong_negacyclic_subtraction', 'ring_engine.py', 'difference(lower, upper)', 'difference(upper, lower)'),
        ('premature_recovery_truncation', 'ring_engine.py', 'nearest(value, plan.recovery_shift)) as (upper,)',
         'nearest(truncate(value, plan.product_shift), plan.recovery_shift)) as (upper,)'),
        ('wrong_zero_padding_count', 'ring_engine.py', 'zeros.multiply_small(2)', 'zeros.multiply_small(1)'),
        ('stage_returns_consumed_source', 'ring_engine.py',
         'self.calls["stages"] += 1\n            return output',
         'self.calls["stages"] += 1\n            return source'),
        ('stage_cleanup_erases_output', 'ring_engine.py',
         'for buffer in (left, top, bottom):\n                buffer.clear()',
         'for buffer in (left, top, output):\n                buffer.clear()'),
        ('FFT_clears_current_before_return', 'ring_engine.py',
         'table.clear()\n                if opposite:', 'current.clear()\n                if opposite:'),
        ('wrong_final_coefficient_index', 'ring_engine.py',
         'with owned(Count.literal(1)) as (one,):', 'with owned(Count.literal(2)) as (one,):'),
        ('symbolic_Taylor_zero_branch', 'twiddle_setup.py',
         '                while not remaining.finished:\n',
         '                while not remaining.finished:\n'
         '                    if lo.zero():\n'
         '                        return (Signed(Count.literal(0)), Signed(Count.literal(0)), '
         'Signed(Count.literal(0)), Signed(Count.literal(0)))\n'),
        ('broadened_plan_boundary', 'product_plan.py',
         'compare(self.ell, self.p) < 0', 'compare(self.ell, self.p) <= 0'),
        ('upward_twiddle_angle', 'twiddle_setup.py',
         'angle = quotient(numerator, self.half)', 'angle = quotient(numerator, self.half, True)'),
        ('wrong_special_twiddle_branch', 'twiddle_setup.py',
         'if compare(twice, self.half) == 0:', 'if compare(twice, self.half) < 0:'),
        ('reversed_twiddle_components', 'twiddle_setup.py',
         'return inward(endpoints[0], endpoints[1], self.shift), inward(endpoints[2], endpoints[3], self.shift)',
         'return inward(endpoints[2], endpoints[3], self.shift), inward(endpoints[0], endpoints[1], self.shift)'),
        ('reversed_twiddle_stream', 'twiddle_setup.py',
         'write_signed(real, self.output, plan.width)\n                            write_signed(imaginary, self.output, plan.width)',
         'write_signed(imaginary, self.output, plan.width)\n                            write_signed(real, self.output, plan.width)'),
        ('wrong_table_precision', 'ring_engine.py',
         'self.twiddles.run(borrowed_count(plan.Q), borrowed_count(length), opposite)',
         'self.twiddles.run(borrowed_count(plan.p), borrowed_count(length), opposite)'),
        ('caller_cleanup_erases_output', 'ring_engine.py',
         'self.output.rewind()\n            if not succeeded:',
         'self.output.clear()\n            if not succeeded:'),
    ]
    # These were independently discovered false-acceptance probes. Each
    # changes real equal-sign or zero inputs while formal atoms alone do not
    # decide its runtime predicate. The correct action is rejection, never
    # treating distinct symbolic representations as unequal runtime values.
    for name, condition in (
            ('sign_equality', 'a.negative == c.negative'),
            ('sign_identity', 'a.negative is c.negative'),
            ('bool_coercion', 'not bool(a.negative)'),
            ('isinstance_signed', 'isinstance(a, Signed)'),
            ('type_signed', 'type(a) is Signed'),
            ('zero_equals_true', 'a.magnitude.zero() == True'),
            ('sign_membership', 'a.negative in (True, False)'),
            ('sign_dictionary_collision', '{a.negative: False, c.negative: True}[a.negative]')):
        head = '    def dif(self, a, b, c, d, u, v, plan):\n'
        cases.append(('unresolved_symbolic_'+name, 'fft_arithmetic.py', head,
                      head+'        if '+condition+':\n'
                      '            return (a.copy(), b.copy(), c.copy(), d.copy())\n'))
    result = []
    def reject(name, candidate):
        try:
            audit(candidate)
        except (ValueError, KeyError, IndexError, StopIteration, TypeError) as error:
            result.append(dict(name=name, result='rejected', reason=type(error).__name__+': '+str(error)))
        else:
            raise ValueError('semantic source mutant accepted: '+name)
    for name, filename, before, after in cases:
        reject(name, replace_once(source, filename, before, after))
    for name, candidate in flow_mutants(source):
        reject(name, candidate)
    return result


def flow_mutants(source):
    """Cross-review attacks on successful-region attachment and normal exits.

    They reach the semantic audit after source-hash checking is bypassed in
    memory. The unchanged source must have passed its positive audit first.
    """
    cases = [('recover', 'unguarded_record'), ('recover', 'record_else'),
             ('stage', 'record_else'), ('stage', 'group_else'), ('stage', 'half_else'),
             ('lift_and_pad', 'record_else'), ('stage', 'dead_region'),
             ('pointwise', 'dead_region'), ('recover', 'dead_region'),
             ('twiddles', 'record_else'), ('twiddles', 'dead_conjugation'),
             ('run', 'false_success'), ('twiddles', 'entry_direction'),
             ('lift_and_pad', 'swapped_extents'), ('fft', 'cleared_initial')]
    for method, kind in cases:
        filename = 'twiddle_setup.py' if method == 'twiddles' else 'ring_engine.py'
        tree = ast.parse(source[filename])
        name = 'Twiddles' if method == 'twiddles' else 'RingProduct'
        class_ = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == name)
        function = next(node for node in class_.body if isinstance(node, ast.FunctionDef)
                        and node.name == ('run' if method == 'twiddles' else method))
        if kind == 'cleared_initial':
            original = function.body[1].value
            function.body[1].value = ast.Subscript(
                value=ast.Tuple(elts=[ast.Call(func=ast.Attribute(value=ast.Name(id='current', ctx=ast.Load()),
                                          attr='clear', ctx=ast.Load()), args=[], keywords=[]), original], ctx=ast.Load()),
                slice=ast.Constant(value=1), ctx=ast.Load())
        elif kind == 'swapped_extents':
            record = function.body[-1].body[0]
            record.iter, record.body[0].iter = record.body[0].iter, record.iter
        elif kind == 'false_success':
            assignments = [node for node in ast.walk(function) if isinstance(node, ast.Assign)
                           and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                           and node.targets[0].id == 'succeeded' and isinstance(node.value, ast.Constant)
                           and node.value.value is True]
            need(len(assignments) == 1, 'one final success flag mutation')
            assignments[0].value = ast.Constant(value=False)
        elif method == 'twiddles':
            loop = next(node for node in ast.walk(function) if isinstance(node, ast.For)
                        and ast.unparse(node.iter) == 'indices(plan.half)')
            if kind == 'record_else':
                loop.orelse = ast.parse('self.output.clear()').body
            elif kind == 'entry_direction':
                function.body[0] = ast.parse('opposite = True').body[0]
            else:
                emitted = loop.body[1]
                emitted.body[0] = ast.If(test=ast.Constant(value=False), body=[emitted.body[0]], orelse=[])
        elif kind == 'unguarded_record':
            loop = next(node for node in ast.walk(function) if isinstance(node, ast.For)
                        and ast.unparse(node.iter) == 'indices(plan.records)')
            loop.body[3] = ast.parse('output.clear()').body[0]
        elif kind == 'dead_region':
            region = function.body[-1]
            container = region.body if method != 'recover' else region.body[0].body[0].body
            container[0] = ast.If(test=ast.Constant(value=False), body=[container[0]], orelse=[])
        else:
            expression = {'record_else': 'indices(plan.records)', 'group_else': 'indices(groups)',
                          'half_else': 'indices(half)'}[kind]
            loop = next(node for node in ast.walk(function) if isinstance(node, ast.For)
                        and ast.unparse(node.iter) == expression)
            loop.orelse = ast.parse('output.clear()').body
        candidate = dict(source)
        candidate[filename] = ast.unparse(ast.fix_missing_locations(tree))+'\n'
        yield 'outline_'+method+'_'+kind, candidate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    source = sources()
    certificate = audit(source)
    controls = mutants(source)
    result = dict(schema_version=1, result='PASS_NORMALIZED_PRODUCT_SOURCE_REFINEMENT',
                  base_commit='7c49fe32c55de02c2c873655c804b16e4c3fef0a', kappa_changed=False,
                  certificates=certificate, rejecting_controls=controls,
                  primitive_premises=['Canonical exact nonnegative Count arithmetic and encoded loops',
                                      'Exact unsigned scalar WordProduct return at the declared width',
                                      'Retained successful-input tape ownership, codecs and packet ABI'],
                  written_refinements=['Unbounded binary shift and nearest-integer loops',
                                       'Machin/Taylor enclosure and reachable Taylor guard',
                                       'Dyadic stage-index/DIF-DIT order induction',
                                       'Disk error propagation, N squared scaling and exact integer recovery'],
                  formal_kernel_claim=False, physical_supplier_admission=False)
    path = HERE/'RESULT.json'
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        need(json.loads(path.read_bytes()) == result, 'exact registered symbolic receipt')
    print('PASS_NORMALIZED_PRODUCT_SOURCE_REFINEMENT '+json.dumps(dict(
        kappa_changed=False, certificates=len(certificate), rejecting_controls=len(controls)), sort_keys=True))


if __name__ == '__main__':
    main()

"""Source, denominator, spectator, signed-arithmetic and scope controls."""
from copy import deepcopy
from fractions import Fraction

from common import require, same_typed
import controller_certificate
import geometry
import inputs
import quantized
import scalar_certificate


def run(data, geometry_result, scalar_result, controller_result):
    out = {}

    def reject(name, function, reason=None):
        try:
            function()
        except ValueError as error:
            if reason is not None:
                require(reason in str(error), 'wrong rejection boundary: '+name)
            out[name] = str(error)
        else:
            raise ValueError('accepted negative control: '+name)

    def word_mutant(name, change, reason=None):
        word = deepcopy(data['word'])
        change(word)
        reject(name, lambda: scalar_certificate.certify(word, data['result']), reason)

    word_mutant('odd_exterior_denominator', lambda w: w['program'][1].__setitem__(-2, '1/3'), 'dyadic')
    word_mutant('stale_common_chart', lambda w: w['program'][1].__setitem__(-1, 4), 'destination chart')
    word_mutant('boolean_role', lambda w: w['program'][0].__setitem__(1, True), 'target role')
    word_mutant('missing_source_cut', lambda w: w['program'].pop(100), 'complete source chronology')
    word_mutant('unrecognized_rounding_opcode', lambda w: w['program'][1].__setitem__(0, 'ROUND_ADD'), 'opcode')
    word_mutant('copy_into_public_role', lambda w: w['program'].__setitem__(1, ['COPY', 205, 572, '1/2', 3]), 'COPY into owned zero')
    move_index = next(i for i, e in enumerate(data['word']['program']) if e[0] == 'MOVE')
    word_mutant('wrong_native_ownership', lambda w: w['program'][move_index].__setitem__(4, True), 'ownership')
    reject('three_bit_coefficient_certificate',
           lambda: scalar_certificate.certify(data['word'], data['result'], 3), '8745')

    def controller_mutant(name, change):
        controller = deepcopy(data['controller'])
        change(controller)
        reject(name, lambda: controller_certificate.certify(data['word'], controller, data['result'], data['dependency']))

    controller_mutant('missing_wrapper_translation', lambda c: c['physical_events'].pop(1))
    controller_mutant('dropped_exterior_swap_sign', lambda c: c['physical_events'][2].__setitem__(0, 'SWAP'))
    controller_mutant('nonintegral_global_boundary', lambda c: c['boundaries']['right_program'][0].__setitem__(-1, '1/2'))
    controller_mutant('aliased_global_add', lambda c: c['boundaries']['right_program'][0].__setitem__(2, c['boundaries']['right_program'][0][1]))

    keep = sum(1 << j for j in geometry_result['retained_axes'])
    omitted = next(j for j in range(265) if not keep >> j & 1)
    zero = geometry.phase(())
    target = geometry.phase(geometry.normalized([(1 << omitted, 1)]))
    reject('discarded_odd_spectator_phase', lambda: geometry.translation(zero, target, keep), 'translation')
    target2 = geometry.phase(geometry.normalized([(1 << omitted, 2)]))
    reject('omitted_spectator_translation', lambda: geometry.translation(zero, target2, keep), 'omitted spectators')
    coupled = geometry.phase(geometry.normalized([((1 << omitted) ^ 1, 1), (1 << omitted, -1), (1, -1)]))
    reject('discarded_spectator_mixed_phase', lambda: geometry.translation(zero, coupled, keep), 'mixed spectator')
    reject('truncated_raw_phase_vector', lambda: geometry.translation((zero[0][:145], zero[1]), zero, keep), 'all raw phase')

    native = deepcopy(data['native'])
    native['pairs'][0][2]['left']['phase'] = (native['pairs'][0][2]['left']['phase']+1) % 4
    reject('lost_absolute_native_phase', lambda: quantized.native_records(data['word'], native, data['result']), 'payload')
    native2 = deepcopy(data['native'])
    native2['pairs'].pop()
    reject('missing_native_or_helper_pair', lambda: quantized.native_records(data['word'], native2, data['result']), 'coverage')
    record = deepcopy(data['native']['pairs'][0][2]['left'])
    record['matrix_rows'][1] = record['matrix_rows'][0]
    reject('nonbijective_native_monomial', lambda: quantized.record_key(record), 'bijective')

    arithmetic = quantized.Arithmetic(16)
    reject('negative_inexact_exterior_product', lambda: arithmetic.product(-1, Fraction(1, 2)), 'exact division')
    constant = [(1, 0)]*512
    require(arithmetic.cstage(list(constant), 1) == constant, 'C pair complete numerator positive control')
    reject('separately_divided_C_summand', lambda: arithmetic.divide(1, 2, 'invalid_summand'), 'exact division')
    wrong_nearest = (quantized.nearest(1, 2)+quantized.nearest(1, 2),
                     quantized.nearest(1, 2)+quantized.nearest(-1, 2))
    wrong_truncation = (2*quantized.toward_zero(1, 2), 0)
    require(wrong_nearest != (1, 0) and wrong_truncation != (1, 0), 'termwise C rounding counterexample')
    sparse = [(0, 0)]*512
    sparse[0] = (1, 0)
    reject('arbitrary_fine_grid_native_input_is_not_reachable_contract', lambda: arithmetic.cstage(sparse, 1), 'exact division')
    reject('insufficient_signed_headroom', lambda: quantized.Arithmetic(8).stored(128), 'headroom')
    reject('boolean_quantizer_numerator', lambda: quantized.nearest(True, 2), 'integer domain')
    reject('boolean_tensor_width', lambda: quantized.widths(0, 0, True), 'column count')
    require([quantized.nearest(a, 2) for a in (-3, -1, 1, 3)] == [-1, 0, 1, 2], 'actual nearest upward ties')
    require([quantized.toward_zero(a, 2) for a in (-3, -1, 1, 3)] == [-1, 0, 0, 1], 'actual signed toward zero')
    require(quantized.turn((1, 0), 2) != quantized.turn((1, 0), 1), 'tensor phase differs from exterior phase')
    require(2*quantized.nearest(1, 2) != 1 and 2*quantized.toward_zero(1, 2) != 1,
            'unfunded final coarsening is not identity')
    for f in (1, 2, 17, 10**9+1):
        F, W = quantized.widths(3, 2, f)
        require(W == F+2+(145*f+2)//2+15, 'all parity width identity')
    for path, root, pins in [(next(iter(inputs.PINS)), inputs.ROOT, inputs.PINS),
                              ('vendor/a1/PROOF.md', inputs.HERE, inputs.VENDOR)]:
        raw = (root/path).read_bytes()
        reject('source_drift:'+path, lambda p=path, r=raw, m=pins: inputs.authenticate(p, r+b' ', m), 'source bytes')
    typed = deepcopy(controller_result)
    typed['reverse_interfaces'] = True
    reject('typed_receipt_corruption', lambda: require(same_typed(controller_result, typed), 'typed result receipt'), 'typed result')
    altered = deepcopy(scalar_result)
    altered['product_debt'] = 3
    reject('omitted_product_debt_receipt', lambda: require(same_typed(scalar_result, altered), 'complete product receipt'), 'product receipt')
    return {'rejections': out, 'positive_kernel_controls': ['complete C numerator before division',
            'signed upward ties and toward zero', 'exterior versus tensor absolute phase',
            'two policies fail unfunded final downcast', 'width identity at both parities and large f'],
            'termwise_nearest_C_wrong_output': list(wrong_nearest),
            'termwise_toward_zero_C_wrong_output': list(wrong_truncation),
            'scope': 'three-bit rejection concerns this coefficient certificate, not sharp physical format necessity'}

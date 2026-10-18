#!/usr/bin/env python3
"""Independent semantic corruption controls on a relocated H6 successor."""
from pathlib import Path
from fractions import Fraction as F
import copy
import gzip
import hashlib
import importlib.util
import json
import sys
import numpy as np

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
from artifact import load_gzip_json


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, PACKAGE / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main():
    c = load('gate_compensation', 'construction/network.py')
    k = load('gate_k_encoder', 'k_encoder/network.py')
    b = load('gate_independent_bucket', 'independent/bucketed.py')
    p = load('gate_physical', 'physical_compiler/compile.py')
    h = load('gate_horner', 'coefficient_horner.py')
    roots, _, ports, profiles = c.geometry.construct_shell()
    ports = ports[(profiles & 4) == 0, :16]
    _, addresses, _ = c.geometry.binary_labels(roots, ports)
    checks = []

    def reject(name, function, reason):
        try:
            function()
        except ValueError as exc:
            need(reason in str(exc), name + ' failed for unrelated reason: ' + str(exc))
            checks.append(dict(name=name, status='DETECTED', reason=str(exc)))
        else:
            raise ValueError('Negative control accepted: ' + name)

    fixture = load_gzip_json(PACKAGE / 'construction/fixture-8-compensation.json.gz')
    c.run_fixture(fixture)
    for name, phase, action, reason in [
        ('missing_dirty_prefix', 'dirt_prefix', 'remove', 'forward all-basis'),
        ('missing_dirty_cleanup', 'FULL_cleanup', 'remove', 'forward all-basis'),
        ('wrong_compensation_edge_coefficient', 'target_cap_scatter', 'double', 'forward all-basis')]:
        mutant = copy.deepcopy(fixture)
        index = next(i for i, event in enumerate(mutant['events']) if event['phase'] == phase and event['op'] == 'add')
        if action == 'remove':
            del mutant['events'][index]
        else:
            mutant['events'][index]['q'] = str(2 * F(mutant['events'][index]['q']))
        reject(name, lambda f=mutant: c.run_fixture(f), reason)
    mutant = copy.deepcopy(fixture)
    index = next(i for i, event in enumerate(mutant['events']) if event['phase'] == 'FULL_cleanup')
    register = mutant['events'][index]['dst']
    mutant['events'].insert(index, c.climb(register, (), 'gate_illegal_descent'))
    reject('illegal_ordinary_frame_descent', lambda: c.run_fixture(mutant), 'nonnested ordinary transition')
    mutant = copy.deepcopy(fixture)
    index = next(i for i, event in enumerate(mutant['events']) if event['phase'] == 'source_line_gather' and event['op'] == 'climb')
    del mutant['events'][index]
    reject('noncommon_current_frame', lambda: c.run_fixture(mutant), 'unequal current frames')

    # Metadata and actual incidence are independently bound; a copied label
    # cannot redefine which actual target ports belong to a bucket.
    with gzip.open(PACKAGE / 'independent/fixture-8-forward.json.gz', 'rt') as stream:
        bucket = json.load(stream)

    def bucket_bindings(word):
        for lane in word['lanes']:
            source = word['indices'][lane['source_position']]
            need(source == lane['source_port'], 'bucket source port binding')
            for target_position in lane['targets']:
                target = word['indices'][target_position]
                need(int(addresses[target]) == lane['target_label'], 'actual target bucket label')
                t = int(ports[target] @ ports[source]) // 4
                wanted = F(int(target == source)) - F(t**3-4*t, 48)
                need(F(lane['coefficients'][str(target_position)]) == wanted, 'actual bucket edge coefficient')
                need((int(addresses[source]) & lane['target_label']).bit_count() % 2 == 0,
                     'actual orthogonal bucket incidence')

    bucket_bindings(bucket)
    b.interpret(bucket, addresses)
    mutant = copy.deepcopy(bucket)
    mutant['lanes'][0]['target_label'] ^= 1
    reject('wrong_target_bucket_label', lambda: bucket_bindings(mutant), 'actual target bucket label')
    with gzip.open(PACKAGE / 'k_encoder/fixture-8-forward.json.gz', 'rt') as stream:
        kword = json.load(stream)
    k.replay(kword)
    mutant = copy.deepcopy(kword)
    index = next(i for i, event in enumerate(mutant['events']) if event['op'] == 'private_transition')
    mutant['events'][index]['rank'] = 16
    reject('wrong_private_copy_rank', lambda: k.replay(mutant), 'K exact check')

    price = json.loads((PACKAGE / 'pricing/RESULT.json').read_text())

    def invoice_bindings(receipt):
        for model in receipt['models']:
            compensation = model['compensation_helpers']['count']
            centers = sum(int(width) * count for width, count in model['histogram'].items())
            for row in model['rows']:
                L = row['stages']
                m = 16 * L + 1
                q, pad = divmod(m, 17)
                stock = F((L-1)*30960) + F(L*(compensation+816), q)
                deficit = (L-1)*30960 - L*centers
                need(F(row['stock_per_template']) == stock, 'complete helper stock')
                need(row['helper_pad'] == pad and row['replicated_pad_rank_mass'] == L*(compensation+816)*pad,
                     'complete helper pad')
                need(row['center_private_copy_bill'] == centers, 'private center C bill')
                need(F(row['complete_rank_mass_per_template']) == m*stock-deficit, 'complete rank mass')
                need(F(row['replicated_stock']) == q*stock, 'integral replicated stock')

    invoice_bindings(price)
    for name, field, value, reason in [
        ('wrong_helper_stock', 'stock_per_template', str(F(price['models'][0]['rows'][0]['stock_per_template'])+1), 'complete helper stock'),
        ('omitted_helper_pad', 'helper_pad', 0, 'complete helper pad'),
        ('wrong_private_center_C', 'center_private_copy_bill', 13871, 'private center C bill')]:
        mutant = copy.deepcopy(price)
        mutant['models'][0]['rows'][0][field] = value
        reject(name, lambda r=mutant: invoice_bindings(r), reason)

    kres = json.loads((PACKAGE / 'k_encoder/RESULT.json').read_text())
    def primitive(q):
        q = abs(F(q)); a, d = q.numerator, q.denominator
        need(a > 0 and d & (d-1) == 0, 'dyadic scalar coefficient')
        return 3 + a.bit_length()-1 + a.bit_count() + d.bit_length()-1

    def scalar_binding(receipt):
        total = sum(count*primitive(q) for q, count in receipt['gather_coefficients'].items())
        total += sum(count*primitive(q) for q, count in receipt['scatter_coefficients'].items())
        need(receipt['K_forward_primitive_bound'] == 2*total+3*816 and
             receipt['K_dual_primitive_bound'] == 2*total+6*816, 'scalar encoding charge')
    scalar_binding(kres)
    coefficients = {F(q) for field in ('gather_coefficients', 'scatter_coefficients') for q in kres[field]}
    coefficients.update(F(q) for q in ('1', '-1', '1/16', '-1/16', '5/16', '-5/16'))
    coefficients |= {-q for q in coefficients}
    for coefficient in coefficients:
        code = h.compile_add(coefficient)
        need(h.execute(code) == [coefficient, 1], 'Every supplied dyadic Horner coefficient')
        need(len(code) == primitive(coefficient), 'Independent Horner primitive count')
    code = list(h.compile_add(F(5, 16)))
    code.insert(code.index(('double',)), ('double',))
    reject('double_Horner_doubling', lambda: need(h.execute(code) == [F(5,16), 1], 'Horner weighted coefficient'),
           'Horner weighted coefficient')
    code = list(h.compile_add(F(5, 16)))
    code.remove(('half',))
    reject('missing_Horner_halving', lambda: need(h.execute(code) == [F(5,16), 1], 'Horner weighted coefficient'),
           'Horner weighted coefficient')
    reject('missing_Horner_temporary_erase', lambda: h.execute(h.compile_add(F(5,16))[:-1]), 'stream remains live')
    mutant = copy.deepcopy(kres)
    mutant['K_forward_primitive_bound'] *= 2
    reject('double_primitive_encoding', lambda: scalar_binding(mutant), 'scalar encoding charge')
    bank = json.loads((PACKAGE / 'bank_physical/RESULT.json').read_text())

    def movement_bound(receipt):
        adapter = receipt['adapter_bound']
        need(adapter['maximum_address_movements_per_adapter_per_coordinate'] == 1, 'movement-inclusive bound')
        need(adapter['conservative_combined_phase_and_movement_actions_per_adapter_per_coordinate'] >=
             adapter['maximum_scalar_unit_phase_actions_per_adapter_per_coordinate'] +
             adapter['maximum_address_movements_per_adapter_per_coordinate'], 'movement-inclusive bound')
    movement_bound(bank)
    mutant = copy.deepcopy(bank)
    mutant['adapter_bound']['maximum_address_movements_per_adapter_per_coordinate'] = 0
    reject('missing_address_movement_charge', lambda: movement_bound(mutant), 'movement-inclusive bound')

    recipes = json.loads((PACKAGE / 'physical_compiler/RECIPES.json').read_text())
    original = recipes['recipes'][0]
    baseline = p.decode(original, recipes['h'])
    mutant = copy.deepcopy(original)
    mutant['left']['phase'] = (mutant['left']['phase']+1) % 4
    phased = p.decode(mutant, recipes['h'])
    need(phased.tab == baseline.tab, 'Global phase control preserves every signed Pauli generator')
    need(not p.equal_exact(phased, baseline), 'Physical global phase mutation must be detected')
    checks.append(dict(name='physical_global_phase', status='DETECTED', signed_tableau_unchanged=True))
    mutant = copy.deepcopy(original)
    mutant['rank'] += 1
    need(not p.equal_exact(p.decode(mutant, recipes['h']), baseline), 'Physical Fourier rank mutation must be detected')
    checks.append(dict(name='physical_fourier_rank', status='DETECTED'))
    result = dict(status='PASS_INDEPENDENT_SUCCESSOR_CORRUPTION_CONTROLS', checks=checks,
                  python=sys.version, optimized_python=sys.flags.optimize,
                  generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  independently_checked_signed_dyadic_coefficients=len(coefficients),
                  scope='Mathematical source/circuit/resource mutations, finite all-column words and exact physical operator controls. No billion-event or selected supplier replay.')
    (HERE / 'CONTROLS.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(result['status'], len(checks))


if __name__ == '__main__':
    main()

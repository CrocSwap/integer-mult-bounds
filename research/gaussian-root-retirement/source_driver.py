"""Check the complete conditional scaled-transport construction.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The native, mixed caller, price and compiler sources keep their original credit.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import gzip
import json
import sys

sys.dont_write_bytecode = True
from fusion_support import HERE, need, read, load, encode, source_context, reject, authenticate
from construct import construct

STATUS = 'PASS_SCALED_TRANSPORT_FUSION_KAPPA_003288299'


def delta(after, before):
    out = Counter(after)
    out.subtract(before)
    return {int(k): v for k, v in out.items() if v}


def run(write=False, build_only=False, services=None, extension=None):
    with source_context() as (package, retained, local_module):
        L = local_module if services is None else services(local_module.ROOT, local_module)
        source = read(package/'WORD.json.gz')
        source_result = read(package/'RESULT.json')
        source_verifier = load(package/'verify.py', 'fusion_source_constructor_check')
        # The retained build mode checks its full constructor chain and controls.
        source_verifier.run(retained.parent/'source-rebuild', build_only=True)
        word, construction = construct(source, read(HERE/'SPEC.json'))
        need(len(word['program']) == 18493 and construction['correction_count'] == 569
             and len(construction['changed_full_rows']) == 28, 'Exact construction inventory')
        need(all(word[k] == source[k] for k in word if k != 'program'), 'All public boundaries and native frames are unchanged')
        if write:
            payload = json.dumps(word, separators=(',', ':')).encode()
            (HERE/'WORD.json.gz').write_bytes(gzip.compress(payload, mtime=0))
            (HERE/'CONSTRUCTION.json').write_text(json.dumps(encode(construction), sort_keys=True, indent=2)+'\n')
        else:
            need(word == read(HERE/'WORD.json.gz'), 'Exact regenerated word')
            need(encode(construction) == read(HERE/'CONSTRUCTION.json'), 'Exact correction receipt')
        before, local = L.replay(source), L.replay(word)
        need(encode(before) == source_result['local'], 'Exact source local invoice')
        need(delta(local['paid'], before['paid']) == {1: -2, 4: -2, 5: 2}
             and local['helpers'] == before['helpers'], 'Complete local paid and productive changes')
        need(tuple(local[k] for k in ('public_inputs', 'owned_fields', 'owned_lifetimes',
                                      'peak_owned_fields', 'real_scalar_allowance', 'paid_rank_mass'))
             == (770, 29, 45, 13, 137218, 5925), 'Exact changed local inventory')
        zero_module = load(package/'zero_scratch.py', 'fusion_zero_scratch')
        obligations = [dict(field=782, frame=127, count=1)]
        zero = zero_module.verify(word, obligations)
        controls = {}
        for role, receiver, frame in [(368, 782, 243), (336, 781, 240)]:
            expected = ['ADD', receiver, role, '1', frame]
            locations = [i for i, event in enumerate(word['program']) if event == expected]
            need(len(locations) == 1, 'Unique new carrier injection')
            for kind in ('drop', 'double', 'wrong_frame'):
                bad = deepcopy(word)
                if kind == 'drop':
                    del bad['program'][locations[0]]
                elif kind == 'double':
                    bad['program'][locations[0]][3] = '2'
                else:
                    bad['program'][locations[0]][-1] = 127
                controls[str(role)+'_injection_'+kind] = reject(lambda bad=bad: L.replay(bad))
        for index in (0, -1):
            bad = deepcopy(word)
            del bad['program'][construction['raw_event_count'] if index == 0 else index]
            controls['correction_drop_'+str(index)] = reject(lambda bad=bad: L.replay(bad))
        bad = deepcopy(word)
        position = next(i for i, event in enumerate(bad['program']) if event[0] == 'SCALE' and event[1] == 368 and event[-1] == 243)
        bad['program'][position][-1] = 517
        controls['old_scale_frame'] = reject(lambda: L.replay(bad))
        pin = next(x for x in read(HERE/'SOURCE.json')['files'] if x['path'].endswith('p104-third-anchor-clean-mixed-root/WORD.json.gz'))
        raw = (package/'WORD.json.gz').read_bytes()
        controls['source_byte'] = reject(lambda: authenticate(bytes([raw[0]^1])+raw[1:], pin))
        need(construct(source, [])[0] == source, 'Empty-change source control')
        print('PASS exact source rebuild, changed scalar word, lifetimes, zero cache and construction controls', flush=True)
        if build_only:
            return
        tree = retained/'research/mixed-projector-query-root'
        load(tree/'algebra.py', 'algebra')
        controller = load(tree/'controller.py', 'controller')
        caller = controller.construct()
        need(encode(caller) == read(tree/'CONTROLLER.json'), 'Exact unchanged caller')
        controller.replay(caller)
        module = load(tree/'module_check.py', 'fusion_independent_module').run()
        controls.update(controller.controls(caller))
        columns = L.reverse_columns(word)
        need(columns['columns'] == 799 and columns['coefficients'] == 638401, 'All independent transpose columns')
        print('PASS all 799 columns and complete mixed caller', flush=True)
        native = L.native(word)
        need(native['helpers'] == local['helpers'] and native['main_adapters'] == 208
             and native['helper_normalizers'] == 1124, 'All native targets and adapters')
        physical = load(tree/'physical.py', 'fusion_physical').physical(caller, word, L)
        need(physical['physical_contacts'] == 7488, 'All physical mixed contacts')
        print('PASS native maps with absolute phases and all 7488 physical contacts', flush=True)
        adapter = read(HERE/'PRICING-EDITS.json')
        text = (package/'pricing.py').read_text()
        need(sha256(text.encode()).hexdigest() == adapter['source_sha256'], 'Exact price source')
        for before_text, after_text in adapter['edits']:
            need(text.count(before_text) == 1, 'Unique declared price edit')
            text = text.replace(before_text, after_text)
        need(text == (HERE/'pricing.py').read_text(), 'Only declared price changes')
        price_module = load(HERE/'pricing.py', 'fusion_price')
        price = price_module.run(local, native, caller, physical, L)
        T0, P0 = controller.formula_invoice(before)
        T1, P1 = controller.formula_invoice(local)
        need(T0 == T1 and delta(P1, P0) == {1: -36, 4: -36, 5: 36}, 'All eighteen native calls and target debits')
        E = L.load(L.ROOT/'research/higher-moment-strictification/verify.py', 'fusion_comparison_intervals')
        other = L.load(L.ROOT/'research/kappa-rebuild/architecture/mixed_target_probe.py', 'fusion_comparison_second')
        t0, p0 = E.moment(T0, 1-price_module.KAPPA), E.moment(P0, 1-price_module.KAPPA)
        tl, th = other.moment(T0, price_module.KAPPA)
        pl, ph = other.moment(P0, price_module.KAPPA)
        need(t0[1] < p0[0] and th < pl, 'Both engines reject the old source at the new claim')
        comparison = dict(previous='0.003287014', source_raw=source_result['complete_cost']['raw_root_interval'],
                          first=E.display((t0[0]-p0[1], t0[1]-p0[0])), second=E.display((tl-ph, th-pl)))
        print('PASS both exact prices, complete compiler and outer inequalities, and strict source comparison', flush=True)
        result = encode(dict(status=STATUS, conditional_kappa=str(price_module.KAPPA),
                           kappa_decimal='0.003288299', source_head=read(HERE/'SOURCE.json')['head'],
                           native_word_sha256=sha256((HERE/'WORD.json.gz').read_bytes()).hexdigest(),
                           local=local, construction=construction, columns=columns, native=native,
                           zero_cache=zero, caller_module=module, physical=physical,
                           complete_cost=price, comparison=comparison, controls=controls,
                           assumptions=['native_all_columns', 'owned_erasure', 'compiler', 'precision_tape', 'analytic_recovery'],
                           scope='Local conditional construction; no independent acceptance, materialized multiplier or selected-frontier change.'))
        need(result == read(HERE/'RESULT.json'), 'Every source result and control remains unchanged')
        if extension is None:
            return result
        return {'source':result,'candidate':extension.run(word, caller, local, native, L)}


if __name__ == '__main__':
    write = '--write-result' in sys.argv
    result = run(write=write, build_only='--build-only' in sys.argv)
    if result is not None:
        if write:
            (HERE/'RESULT.json').write_text(json.dumps(result, sort_keys=True, indent=2)+'\n')
        else:
            need(result == read(HERE/'RESULT.json'), 'Exact complete receipt')
        print(STATUS, flush=True)

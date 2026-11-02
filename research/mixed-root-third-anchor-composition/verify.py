"""Compose the fixed mixed root with the PR6375 native word plus a third group-1091 anchor.

Prepared by the Claude Sonnet 5.5 main session (Claude Code) with orchestrated subagent
assistance, for Erwan L. Apache-2.0. Adapted from the mixed-root contact composition verifier
(Ali Romman with OpenAI Codex); every change is marked CANDIDATE CHANGE. The source
constructors and proof engines retain their original notices.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha1, sha256
from pathlib import Path, PurePosixPath
import gzip
import importlib.util
import json
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREVIOUS = ROOT/'research/mixed-root-source-composition'
CONTACT = 'research/p104-contact-block-contraction/'
LIFT = 'research/p104-shared-carrier-lifts/'
STATUS = 'PASS_MIXED_ROOT_THIRD_ANCHOR_KAPPA_00328637739144124222748802'  # CANDIDATE CHANGE


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_bytes())


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def authenticate(data, pin):
    need(sha256(data).hexdigest() == pin['sha256'], 'Exact source SHA256: '+pin['path'])
    need(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == pin['git_blob'],
         'Exact source Git blob: '+pin['path'])


def reject(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError('Invalid control accepted')


def delta(after, before):
    result = Counter(after)
    result.subtract(before)
    return {r: n for r, n in result.items() if n}


def retained_source(root, manifest_name, archive_name, count):
    manifest = read(HERE/manifest_name)
    archive = HERE/archive_name
    need(sha256(archive.read_bytes()).hexdigest() == manifest['archive_sha256'], 'Exact retained source archive')
    pins = {p['path']: p for p in manifest['files']}
    need(len(pins) == len(manifest['files']) == count, 'Exact retained source inventory')
    with tarfile.open(archive, 'r:') as tar:
        members = tar.getmembers()
        need(len(members) == count and {m.name for m in members} == set(pins), 'Every retained source file')
        for member in members:
            path = PurePosixPath(member.name)
            need(member.isfile() and not path.is_absolute() and '..' not in path.parts, 'Regular relative retained path')
            data = tar.extractfile(member).read()
            authenticate(data, pins[member.name])
            target = root/member.name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    return manifest


def run(build_only=False):  # CANDIDATE CHANGE: cheap build-only mode
    live = read(HERE/'SOURCES.json')['files']
    for pin in live:
        if pin['usage'] == 'input':
            authenticate((ROOT/pin['path']).read_bytes(), pin)
    previous = load(PREVIOUS/'verify.py', 'prior_mixed_composition')
    for filename, edits in [('pricing.py', 'PRICING-EDITS.json'), ('ceiling.py', 'CEILING-EDITS.json')]:
        text = (PREVIOUS/filename).read_text()
        for before, after in read(HERE/edits):
            need(text.count(before) == 1, 'One occurrence of each declared '+filename+' edit')
            text = text.replace(before, after)
        need(text == (HERE/filename).read_text(), 'Exact declared '+filename+' adapter')
    with previous.sources() as (root, old_manifest):
        manifest = retained_source(root, 'CONTACT-INPUTS.json', 'contact-source.tar', 8)
        lift_manifest = retained_source(root, 'LIFT-INPUTS.json', 'lift-source.tar', 7)
        original = root/previous.ROOT_SOURCE
        joint = root/previous.CONTRACT_SOURCE
        new = root/CONTACT
        load(original/'algebra.py', 'algebra')
        controller = load(original/'controller.py', 'controller')
        physical = load(original/'physical.py', 'contact_root_physical')
        module = load(original/'module_check.py', 'contact_root_module')
        binary = load(root/'research/balanced-query-tree/module_check.py', 'contact_root_binary')
        support = load(joint/'support.py', 'support')
        legacy = load(joint/'construct.py', 'legacy_basis')
        third = load(HERE/'construct3.py', 'third_constructor')  # CANDIDATE CHANGE: k-anchor constructor (uses the loaded legacy basis)
        constructor = load(new/'construct.py', 'contact_root_constructor')
        need((joint/'construct.py').read_bytes() == (new/'inputs/pr6353-construct.py').read_bytes(),
             'The exact retained PR6353 basis constructor')
        need((joint/'WORD.json.gz').read_bytes() == (new/'inputs/pr6353-WORD.json.gz').read_bytes(),
             'The exact retained PR6353 native word')
        old_word = json.loads(gzip.decompress((joint/'WORD.json.gz').read_bytes()))
        native_word, witness = constructor.construct(old_word)
        need(native_word == json.loads(gzip.decompress((new/'WORD.json.gz').read_bytes())), 'Every rebuilt PR6372 native word field')
        need(legacy.encode(witness) == read(new/'BASIS.json'), 'Every new rational basis witness')
        need(all(native_word[k] == value for k, value in old_word.items() if k not in ('program', 'final')),
             'Unchanged native interface, inputs and frames')
        need({r: native_word['final'][r] for r in range(770) if native_word['final'][r] != old_word['final'][r]}
             == {224: 245, 227: 245}, 'Only the two declared helper outputs change')
        contact_word = native_word
        lifted = root/LIFT
        need((new/'WORD.json.gz').read_bytes() == (lifted/'inputs/pr6372-WORD.json.gz').read_bytes(),
             'Exact retained input to the shared-carrier constructor')
        lifts = load(lifted/'construct.py', 'mixed_shared_carrier_constructor')
        native_word = lifts.construct(contact_word, read(lifted/'LIFTS.json'))
        need(native_word == json.loads(gzip.decompress((lifted/'WORD.json.gz').read_bytes())),
             'Every reconstructed PR6375 native word field')
        need(all(native_word[k] == value for k, value in contact_word.items() if k not in ('program', 'initial')),
             'Unchanged lifted interface, frames and final outputs')
        need({r: native_word['initial'][r] for r in range(770)
              if native_word['initial'][r] != contact_word['initial'][r]}
             == {520: 106, 655: 106, 544: 105, 671: 105, 472: 105, 624: 105},
             'Exactly six changed input frames')
        # CANDIDATE CHANGE: `native_word` was the PR6375 word; it is kept as `predecessor_word`. The word used
        # below is the third-anchor word: PR6353 -> three anchors (word3) -> the same PR6375 lift rounds.
        predecessor_word = native_word
        need(third.construct(old_word, None)[0] == contact_word, 'spec=None reproduces the PR6372 word exactly')
        word3, _ = third.construct(old_word, third.load_spec(read(HERE/'SPEC.json')))
        native_word = lifts.construct(word3, read(lifted/'LIFTS.json'))
        need(native_word == json.loads(gzip.decompress((HERE/'WORD.json.gz').read_bytes())),
             'Every rebuilt third-anchor native word field')
        need(all(native_word[k] == predecessor_word[k] for k in native_word if k not in ('program', 'final'))
             and {r for r in range(770) if native_word['final'][r] != predecessor_word['final'][r]} == {234}
             and native_word['final'][234] == 246 and predecessor_word['final'][234] == 127,
             'Only the third anchor output frame differs from the PR6375 word')
        caller = controller.construct()
        need(caller == read(original/'CONTROLLER.json'), 'Every unchanged mixed caller event')
        root_result, binary_result = module.run(), binary.run()
        caller_result = controller.replay(caller)
        controls = controller.controls(caller)
        price = load(HERE/'pricing.py', 'contact_root_price')
        ceiling = load(HERE/'ceiling.py', 'contact_root_ceiling')
        optimality = load(HERE/'optimality.py', 'contact_root_optimality')
        print('PASS exact source reconstruction, root, normalization and complete caller', flush=True)
        with support.checkers() as (L, frozen):
            old, contact, local = L.replay(old_word), L.replay(contact_word), L.replay(native_word)
            pred, pre = L.replay(predecessor_word), L.replay(word3)  # CANDIDATE CHANGE: PR6375 word and word3
            need(price.encode(contact) == read(new/'RESULT.json')['local'], 'Published PR6372 local receipt')
            need(price.encode(pred) == read(lifted/'RESULT.json')['local'], 'Published PR6375 local receipt')  # CANDIDATE CHANGE: predecessor
            need(price.encode(old) == read(PREVIOUS/'RESULT.json')['local'], 'Prior complete composition source')
            pd, td = delta(local['paid'], old['paid']), delta(local['helpers'], old['helpers'])
            need(delta(contact['paid'], old['paid']) == {4: 2, 5: -2}
                 and delta(contact['helpers'], old['helpers']) == {8: 2, 9: -2}, 'Exact contact changes')
            # CANDIDATE CHANGE: lifts are measured against word3; the third anchor against the PR6372 word and the PR6375 word
            lift_pd, lift_td = delta(local['paid'], pre['paid']), delta(local['helpers'], pre['helpers'])
            need(lift_pd == {1: 6, 3: -3, 4: 3, 5: -3} and lift_td == {8: 6, 9: -6},
                 'Exact signed shared-carrier changes')
            third_pd, third_td = delta(pre['paid'], contact['paid']), delta(pre['helpers'], contact['helpers'])
            need(third_pd == {4: 1, 5: -1} and third_td == {8: 1, 9: -1}, 'Exact third-anchor change')
            need(delta(local['paid'], pred['paid']) == {4: 1, 5: -1}
                 and delta(local['helpers'], pred['helpers']) == {8: 1, 9: -1}, 'Exact change against the PR6375 word')
            need((local['public_inputs'], local['owned_fields'], local['owned_lifetimes'], local['peak_owned_fields'])
                 == (770, 29, 44, 13), 'All inputs and all three new owned lifetimes')
            need((local['real_scalar_allowance'], local['paid_rank_mass']) == (131052, 5925), 'Exact scalar allowance and paid mass')
            for label, index in witness['control_indices'].items():
                bad = deepcopy(contact_word)
                del bad['program'][index]
                controls['missing_'+label] = reject(lambda: L.replay(bad))
            for role in (224, 227):
                bad = deepcopy(native_word)
                bad['final'][role] = old_word['final'][role]
                controls['missing_target_'+str(role)] = reject(lambda: L.replay(bad))
            for role in (520, 655, 544, 671, 472, 624):
                bad = deepcopy(native_word)
                bad['initial'][role] = contact_word['initial'][role]
                controls['old_entrance_'+str(role)] = reject(lambda: L.replay(bad))
            source_events = {tuple(e) for e in word3['program']}  # CANDIDATE CHANGE: lift controls relative to word3
            new_adds = [i for i, e in enumerate(native_word['program'])
                        if e[0] == 'ADD' and tuple(e) not in source_events]
            for label, index in [('first_lift_delivery', new_adds[0]), ('last_lift_restore', new_adds[-1])]:
                bad = deepcopy(native_word)
                del bad['program'][index]
                controls[label] = reject(lambda: L.replay(bad))
            bad = deepcopy(native_word)
            bad['program'][new_adds[0]][3] = str(-Q(bad['program'][new_adds[0]][3]))
            controls['lift_response_sign'] = reject(lambda: L.replay(bad))
            # CANDIDATE CHANGE: controls specific to the third anchor 234
            events75 = {tuple(e) for e in predecessor_word['program']}
            P3 = native_word['program']
            third_new = [i for i, e in enumerate(P3) if tuple(e) not in events75]
            t_moves = [i for i in third_new if P3[i][0] == 'MOVE']
            t_246 = [i for i in third_new if P3[i][0] == 'ADD' and P3[i][-1] == 246]
            t_in = [i for i in third_new if P3[i][0] == 'ADD' and P3[i][-1] == 3]
            t_out = [i for i in third_new if P3[i][0] == 'ADD' and P3[i][-1] == 127]
            need(t_moves and t_246 and t_in and t_out, 'Third-anchor events present')
            for label, frame in [('wrong_entrance_245', 245), ('entrance_reverted', 127)]:
                bad = deepcopy(native_word)
                bad['final'][234] = frame
                controls['third_anchor_' + label] = reject(lambda: L.replay(bad))
            for label, index in [('move_dropped', t_moves[0]), ('response_dropped', t_246[0]),
                                 ('input_correction_dropped', t_in[0]), ('dyadic_restore_dropped', t_out[-1])]:
                bad = deepcopy(native_word)
                del bad['program'][index]
                controls['third_anchor_' + label] = reject(lambda: L.replay(bad))
            bad = deepcopy(native_word)
            bad['program'][t_246[0]][3] = str(2*Q(bad['program'][t_246[0]][3]))
            controls['third_anchor_response_doubled'] = reject(lambda: L.replay(bad))
            if build_only:  # CANDIDATE CHANGE: stop after the rebuild, local deltas and word controls
                print('PASS third-anchor rebuild, local deltas, inventory and word controls', flush=True)
                return None
            columns = L.reverse_columns(native_word)
            need(columns['columns'] == 799 and columns['coefficients'] == 638401, 'All independent native columns')
            native = L.native(native_word)
            maps = physical.physical(caller, native_word, L)
            need(maps['full_calls'] == 18 and maps['physical_contacts'] == 7488, 'All physical caller contacts')
            print('PASS source inputs, dense transpose, native phases, physical caller and owned controls', flush=True)
            bound = price.run(local, native, caller, maps, L)
            old_targets, old_paid = controller.formula_invoice(old)
            need(delta({int(r): n for r, n in bound['paid'].items()}, old_paid) == {r: 18*n for r, n in pd.items()},
                 'All eighteen paid changes')
            need(delta({int(r): n for r, n in bound['targets'].items()}, old_targets) == {r: 18*n for r, n in td.items()},
                 'All eighteen productive target debits')
            E = load(frozen/'research/higher-moment-strictification/verify.py', 'contact_root_comparison')
            fixed_ceiling = ceiling.run(local, E, read(original/'ROOT.json'))
            optimum = optimality.run(local, E, read(original/'ROOT.json'), bound, fixed_ceiling)
            old_margin = E.moment(old_targets, 1-price.KAPPA)[1]-E.moment(old_paid, 1-price.KAPPA)[0]
            need(old_margin < 0, 'The previous source fails at the new complete claim')
            contact_targets, contact_paid = controller.formula_invoice(contact)
            contact_margin = E.moment(contact_targets, 1-price.KAPPA)[1]-E.moment(contact_paid, 1-price.KAPPA)[0]
            need(contact_margin < 0, 'The immediate PR6372 composition fails at the new complete claim')
            pred_targets, pred_paid = controller.formula_invoice(pred)  # CANDIDATE CHANGE
            pred_margin = E.moment(pred_targets, 1-price.KAPPA)[1]-E.moment(pred_paid, 1-price.KAPPA)[0]
            need(pred_margin < 0, 'The PR6375 word with this same mixed caller fails the new claim')
            bad = deepcopy(local); bad['paid'][4] -= 1
            controls['unpaid_native_move'] = reject(lambda: price.assemble(bad, native, caller, maps))
            bad = deepcopy(local); bad['helpers'][9] += 1; bad['helpers'][8] -= 1
            controls['missing_productive_debit'] = reject(lambda: price.assemble(bad, native, caller, maps))
            for pin in manifest['files']+lift_manifest['files']:
                data = (root/pin['path']).read_bytes()
                controls['damaged_'+pin['path']] = reject(lambda data=data, pin=pin: authenticate(bytes([data[0]^1])+data[1:], pin))
            print('PASS both prices, complete compiler and outer ledger, source controls and exact raw family limit', flush=True)
        return price.encode({'status': STATUS, 'source_head': lift_manifest['source_head'],
            'contact_source_head': manifest['source_head'],
            'root_source': old_manifest['root_head'], 'native_events': len(native_word['program']),
            'root': root_result, 'binary': binary_result, 'caller': caller_result,
            'local': local, 'paid_delta': pd, 'target_delta': td, 'columns': columns,
            'lift_paid_delta': lift_pd, 'lift_target_delta': lift_td,
            'native': native, 'physical': maps, 'price': bound, 'fixed_root_ceiling': fixed_ceiling,
            'raw_optimality': optimum,
            'prior_source_margin_upper': old_margin, 'controls': controls,
            'immediate_source_margin_upper': contact_margin, 'pr6375_word_margin_upper': pred_margin,
            'third_paid_delta': third_pd, 'third_target_delta': third_td, 'pr6375_local': pred, 'word3_local': pre,  # CANDIDATE CHANGE
            'gain_over_pr6398': price.KAPPA-Q('.00328621476572836015146308'),
            'gain_over_pr6375': price.KAPPA-Q('.00315120'),
            'relative_gain_over_pr6375_percent': 100*(price.KAPPA/Q('.00315120')-1),
            'assumptions': ['native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery'],
            'selected_frontier_changed': False})


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    with tempfile.TemporaryDirectory(prefix='mixed-contact-cache-') as cache:
        sys.pycache_prefix = cache
        result = run('--build-only' in sys.argv)
    if result is None:
        print(STATUS + '_BUILD', flush=True)
        sys.exit(0)
    if sys.argv[1:] == ['--write-result']:
        (HERE/'RESULT.json').write_text(json.dumps(result, sort_keys=True, indent=2)+'\n')
    else:
        need(not sys.argv[1:], 'Only --write-result is supported')
        need(result == read(HERE/'RESULT.json'), 'Exact complete scientific receipt')
    print(STATUS, flush=True)

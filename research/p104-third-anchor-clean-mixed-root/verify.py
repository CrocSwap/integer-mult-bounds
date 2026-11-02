"""Complete portable conditional composition: PR6417's clean native merge and mixed root, with a third group-1091 anchor.

Prepared by the Claude Sonnet 5.5 main session (Claude Code) with orchestrated subagent assistance, for Erwan L.
Apache-2.0. Adapted from the PR6417 verifier (Rohan Arun with substantial OpenAI Codex assistance); every change
is marked '# CANDIDATE CHANGE'. No check of the PR6417 verifier is removed; checks that compared against the
published single-word receipts are replaced by differential checks against those receipts, as marked.
"""
from collections import Counter
from contextlib import ExitStack
from copy import deepcopy
from fractions import Fraction as Q  # CANDIDATE CHANGE
from hashlib import sha256
from pathlib import Path
import json
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from support import ROOT, read, load, need, encode, inputs, reject

STATUS = 'PASS_THIRD_ANCHOR_CLEAN_MIXED_ROOT_COMPOSITION_KAPPA_003287014'  # CANDIDATE CHANGE: new status


def delta(after, before):  # CANDIDATE CHANGE: helper for the differential local checks
    out = Counter(after)
    out.subtract(before)
    return {int(r): n for r, n in out.items() if n}


def run(retained, build_only=False):  # CANDIDATE CHANGE: cheap build-only mode
    inputs(retained)
    clean = retained/'research/p104-clean-piggyback'
    tree = retained/'research/mixed-projector-query-root'
    contact = retained/'research/p104-contact-block-contraction'  # CANDIDATE CHANGE
    lift = retained/'research/p104-shared-carrier-lifts'  # CANDIDATE CHANGE
    controls = {}  # CANDIDATE CHANGE: collected before the caller controls
    # CANDIDATE CHANGE: rebuild chain. PR6353 word -> (spec=None regression == PR6372 word) -> third-anchor word word3
    # -> the PR6375 lift rounds (rebuilt PR6375 word == the retained one) -> parametrized PR6399 merge, cache label 782.
    # The PR6399 constructor itself is not executed: merge_construct.py is our parametrized copy, regression-checked
    # below against the retained published PR6399 word (cache label 781).
    merger = load(HERE/'merge_construct.py','third_clean_merge')
    w75 = read(clean/'inputs/pr6375-WORD.json.gz')
    need(read(lift/'WORD.json.gz') == w75, 'The retained PR6375 word is the clean merge input')
    clean_word = read(clean/'WORD.json.gz')
    need(merger.construct(w75, cache=781) == clean_word, 'The parametrized merge reproduces the published PR6399 word')
    load(contact/'inputs/pr6353-construct.py','legacy_basis')
    third = load(HERE/'construct3.py','third_constructor')
    s53 = read(contact/'inputs/pr6353-WORD.json.gz')
    need(third.construct(s53, None)[0] == read(contact/'WORD.json.gz'), 'spec=None reproduces the PR6372 word exactly')
    lifts = load(lift/'construct.py','stack_lifts')
    lift_rounds = read(lift/'LIFTS.json')
    need(lifts.construct(read(contact/'WORD.json.gz'), lift_rounds) == w75, 'The PR6375 lifts reproduce the PR6375 word')
    spec = read(HERE/'SPEC.json')
    word3 = third.construct(s53, third.load_spec(spec))[0]
    lifted = lifts.construct(word3, lift_rounds)
    word = merger.construct(lifted, cache=782)
    need(word == read(HERE/'WORD.json.gz'), 'Every regenerated native word field')  # CANDIDATE CHANGE: our shipped word
    need(all(word[k] == clean_word[k] for k in word if k not in ('program','final'))
         and {r for r in range(770) if word['final'][r] != clean_word['final'][r]} == {234}
         and word['final'][234] == 246 and clean_word['final'][234] == 127,
         'Only the third anchor output frame differs from the PR6399 word')  # CANDIDATE CHANGE
    load(tree/'algebra.py','algebra')
    controller = load(tree/'controller.py','controller')
    old_price = retained/'research/mixed-root-contact-composition/pricing.py'
    text = old_price.read_text()
    adapter = read(HERE/'PRICING-EDITS.json')
    need(sha256(text.encode()).hexdigest() == adapter['source_sha256'], 'Exact price source')
    for before,after in adapter['edits']:
        need(text.count(before) == 1, 'Unique declared price edit')
        text = text.replace(before,after)
    need(text == (HERE/'pricing.py').read_text(), 'Only declared price changes')
    source = load(ROOT/'research/p104-root-relay-descent-2/sources.py','mixed_clean_archive_source')
    with ExitStack() as stack:
        parent = stack.enter_context(source.sources())
        cursor = stack.enter_context(source.load(parent/'sources.py','mixed_archive_top').sources())
        for depth in range(7):
            cursor,root = stack.enter_context(source.load(cursor/'sources.py','mixed_archive_'+str(depth)).sources())
        L = source.load(parent/'local.py','mixed_clean_local')
        L.ROOT = root
        local = L.replay(word)
        clean_local = L.replay(clean_word)  # CANDIDATE CHANGE: the published PR6399 word, replayed
        need(encode(clean_local) == read(clean/'RESULT.json')['local'], 'Exact retained clean native invoice')  # CANDIDATE CHANGE: now checks the PR6399 word it describes
        # CANDIDATE CHANGE: differential local checks of the stacked word against the published clean word
        need(delta(local['paid'], clean_local['paid']) == {4: 1, 5: -1}
             and delta(local['helpers'], clean_local['helpers']) == {8: 1, 9: -1},
             'Exact third-anchor change against the PR6399 word')
        need(tuple(local[k] for k in ('public_inputs','owned_fields','owned_lifetimes','peak_owned_fields',
                                      'real_scalar_allowance','paid_rank_mass','endpoint_coefficients'))
             == (770, 29, 45, 13, 131560, 5925, 638401), 'Exact stacked local inventory')
        need(clean_local['owned_lifetimes'] == 44 and clean_local['real_scalar_allowance'] == 130178,
             'The published clean word inventory')
        # CANDIDATE CHANGE: lifts and the third anchor measured on the intermediate words
        pre_local, w3_local = L.replay(lifted), L.replay(word3)
        need(delta(pre_local['paid'], w3_local['paid']) == {1: 6, 3: -3, 4: 3, 5: -3}
             and delta(pre_local['helpers'], w3_local['helpers']) == {8: 6, 9: -6}
             and pre_local['owned_lifetimes'] == w3_local['owned_lifetimes'] == 44
             and pre_local['real_scalar_allowance'] == 131052, 'Exact lift changes and no added lifetime on the third-anchor word')
        zero_module = load(HERE/'zero_scratch.py','third_clean_zero_scratch')  # CANDIDATE CHANGE: own implementation, not the retained PR6399 file
        obligations = [dict(field=782,frame=127,count=1)]  # CANDIDATE CHANGE: cache label 782 (label 781 is a third-anchor shadow row)
        zero = zero_module.verify(word,obligations)
        # CANDIDATE CHANGE: controls specific to the third anchor and to the stacked pieces
        events_clean = {tuple(e) for e in clean_word['program']}
        P3 = word['program']
        third_new = [i for i,e in enumerate(P3) if tuple(e) not in events_clean and 782 not in (e[1], e[2] if len(e) > 3 else -1)]
        t_moves = [i for i in third_new if P3[i][0] == 'MOVE']
        t_246 = [i for i in third_new if P3[i][0] == 'ADD' and P3[i][-1] == 246]
        t_in = [i for i in third_new if P3[i][0] == 'ADD' and P3[i][-1] == 3]
        t_out = [i for i in third_new if P3[i][0] == 'ADD' and P3[i][-1] == 127]
        need(t_moves and t_246 and t_in and t_out, 'Third-anchor events present')
        for label,frame in [('wrong_entrance_245',245),('entrance_reverted',127)]:
            bad = deepcopy(word)
            bad['final'][234] = frame
            controls['third_anchor_'+label] = reject(lambda bad=bad: L.replay(bad))
        for label,index in [('move_dropped',t_moves[0]),('response_dropped',t_246[0]),
                            ('input_correction_dropped',t_in[0]),('dyadic_restore_dropped',t_out[-1])]:
            bad = deepcopy(word)
            del bad['program'][index]
            controls['third_anchor_'+label] = reject(lambda bad=bad: L.replay(bad))
        bad = deepcopy(word)
        bad['program'][t_246[0]][3] = str(2*Q(bad['program'][t_246[0]][3]))
        controls['third_anchor_response_doubled'] = reject(lambda: L.replay(bad))
        controls['merge_label_collision'] = reject(lambda: merger.construct(lifted, cache=781))
        bad = deepcopy(word)
        del bad['program'][-3]
        controls['stacked_merge_cleanup_event_dropped'] = reject(lambda: zero_module.verify(bad,obligations))
        bad = deepcopy(spec)
        first_anchor = str(bad['anchors'][0])
        key = sorted(bad['dirs'][first_anchor])[0]
        bad['dirs'][first_anchor][key] = '1/3'
        controls['third_anchor_spec_corrupted'] = reject(lambda: third.construct(s53, third.load_spec(bad)))
        if build_only:  # CANDIDATE CHANGE
            print('PASS stacked rebuild, local deltas, inventory, zero scratch and third-anchor controls',flush=True)
            return None
        caller = controller.construct()
        need(encode(caller) == read(tree/'CONTROLLER.json'), 'Complete pinned mixed caller')
        controller.replay(caller)
        module = load(tree/'module_check.py','mixed_root_independent_module').run()
        controls.update(controller.controls(caller))
        columns = L.reverse_columns(word)
        need(columns['columns'] == 799 and columns['coefficients'] == 638401, 'All independent transpose columns')
        print('PASS regenerated native word, ownership, zero scratch and799columns',flush=True)
        native = L.native(word)
        clean_native = read(clean/'RESULT.json')['native']
        enc_native = encode(native)
        # CANDIDATE CHANGE: the published native receipt describes the PR6399 word; for the stacked word every field is
        # compared except the three that necessarily change (the new chart, the helper histogram, the recipe payload).
        need({k: v for k,v in enc_native.items() if k not in ('distinct_maps','helpers','recipe_payload_sha256')}
             == {k: v for k,v in clean_native.items() if k not in ('distinct_maps','helpers','recipe_payload_sha256')}
             and enc_native['distinct_maps'] == clean_native['distinct_maps']+1
             and enc_native['helpers'] == encode(local['helpers'])
             and enc_native['recipe_payload_sha256'] != clean_native['recipe_payload_sha256'],
             'Native maps and phases differ from the PR6399 receipt only by the third-anchor chart')
        physical = load(tree/'physical.py','mixed_clean_physical').physical(caller,word,L)
        need(physical['physical_contacts'] == 7488, 'All mixed physical contacts')
        print('PASS native absolute phases and7488physical mixed contacts',flush=True)
        price = load(HERE/'pricing.py','mixed_clean_price').run(local,native,caller,physical,L)
        bad = deepcopy(word)
        bad['program'].pop(-2)
        controls['missing_new_scratch_uncompute'] = reject(lambda:zero_module.verify(bad,obligations))
        # Corrupted actual retained bytes are rejected by the same binding guard.
        pin = read(HERE/'RETAINED-INPUTS.json')['native']['files'][0]
        data = (retained/pin['path']).read_bytes()
        from support import authenticate
        reject(lambda:authenticate(bytes([data[0]^1])+data[1:],pin))
        print('PASS both price engines, complete compiler/precision/outer and controls',flush=True)
    return encode(dict(status=STATUS,conditional_kappa='0.003287014',tested='0.003287019',  # CANDIDATE CHANGE: claim A (9 decimals, PR6417 style); constants from the exact raw bracket
        source_pr=6417,source_head='df683ace130c83ca8caaa301b027a247a46e4ea8',
        native_candidate_sha256=sha256((HERE/'WORD.json.gz').read_bytes()).hexdigest(),
        local=local,clean_local=clean_local,columns=columns,native=native,new_scratch_zero=zero,physical=physical,
        module=module,complete_cost=price,controls=controls,
        assumptions=['native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery'],
        goal_005_complete=False,
        scope='Complete locally verified source-bound conditional composition. Same-author separate arithmetic engines; no independent human/kernel acceptance, materialized multiplier or .005 claim.'))


def main():
    with tempfile.TemporaryDirectory(prefix='third-anchor-clean-mixed-root-') as directory:
        temp = Path(directory)
        old_temp = tempfile.tempdir
        tempfile.tempdir = directory
        sys.pycache_prefix = str(temp/'bytecode')
        try:
            result = run(temp/'retained', '--build-only' in sys.argv)  # CANDIDATE CHANGE
        finally:
            tempfile.tempdir = old_temp
    if result is None:  # CANDIDATE CHANGE
        print(STATUS+'_BUILD',flush=True)
        return
    if '--write-result' in sys.argv:  # CANDIDATE CHANGE: the PR6417 verifier has no write mode in this file
        (HERE/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:
        need(result == read(HERE/'RESULT.json'), 'Exact complete scientific receipt')
    print(STATUS,flush=True)


if __name__ == '__main__':
    main()

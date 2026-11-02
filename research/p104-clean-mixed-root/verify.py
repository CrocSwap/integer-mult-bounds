"""Complete portable clean-native / mixed-root conditional composition.
Rohan Arun with substantial OpenAI Codex assistance. Apache-2.0.
"""
from contextlib import ExitStack
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from support import ROOT, read, load, need, encode, inputs, reject

STATUS = 'PASS_COMPLETE_CONDITIONAL_CLEAN_MIXED_ROOT_COMPOSITION'


def run(retained):
    inputs(retained)
    clean = retained/'research/p104-clean-piggyback'
    tree = retained/'research/mixed-projector-query-root'
    builder = load(clean/'construct.py','mixed_clean_constructor')
    word = builder.construct(read(clean/'inputs/pr6375-WORD.json.gz'))
    need(word == read(clean/'WORD.json.gz'), 'Every regenerated native word field')
    load(tree/'algebra.py','algebra')
    controller = load(tree/'controller.py','controller')
    caller = controller.construct()
    need(encode(caller) == read(tree/'CONTROLLER.json'), 'Complete pinned mixed caller')
    controller.replay(caller)
    module = load(tree/'module_check.py','mixed_root_independent_module').run()
    controls = controller.controls(caller)
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
        need(encode(local) == read(clean/'RESULT.json')['local'], 'Exact retained clean native invoice')
        zero_module = load(clean/'owned_zero.py','mixed_clean_independent_zero')
        obligations = [dict(field=781,frame=127,count=1)]
        zero = zero_module.verify(word,obligations)
        columns = L.reverse_columns(word)
        need(columns['columns'] == 799 and columns['coefficients'] == 638401, 'All independent transpose columns')
        print('PASS regenerated native word, ownership, zero scratch and799columns',flush=True)
        native = L.native(word)
        need(encode(native) == read(clean/'RESULT.json')['native'], 'Exact retained native maps/phases')
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
    return encode(dict(status=STATUS,conditional_kappa='0.003286849',tested='0.003286854',
        source_pr=6398,source_head='dee2663ba0918be86993fd9d63c8d64b020f4c83',
        native_candidate_sha256=sha256((clean/'WORD.json.gz').read_bytes()).hexdigest(),
        local=local,columns=columns,native=native,new_scratch_zero=zero,physical=physical,
        module=module,complete_cost=price,controls=controls,
        assumptions=['native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery'],
        goal_005_complete=False,
        scope='Complete locally verified source-bound conditional composition. Same-author separate arithmetic engines; no independent human/kernel acceptance, materialized multiplier or .005 claim.'))


def main():
    with tempfile.TemporaryDirectory(prefix='clean-mixed-root-') as directory:
        temp = Path(directory)
        old_temp = tempfile.tempdir
        tempfile.tempdir = directory
        sys.pycache_prefix = str(temp/'bytecode')
        try:
            result = run(temp/'retained')
        finally:
            tempfile.tempdir = old_temp
    need(result == read(HERE/'RESULT.json'), 'Exact complete scientific receipt')
    print(STATUS,flush=True)


if __name__ == '__main__':
    main()

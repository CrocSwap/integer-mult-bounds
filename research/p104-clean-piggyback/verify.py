"""Portable full conditional admission for the clean P104 transport merge.
Rohan Arun with substantial OpenAI Codex assistance. Apache-2.0.
Retained archive/checkers/caller credits are preserved in NOTICE.
"""
from contextlib import ExitStack
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256, sha1
from pathlib import Path
import gzip
import importlib.util
import json
import os
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STATUS = 'PASS_P104_CLEAN_PIGGYBACK_CONDITIONAL_003151787'
sys.dont_write_bytecode = True


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def read(path):
    b = Path(path).read_bytes()
    return json.loads(gzip.decompress(b) if str(path).endswith('.gz') else b)


def encode(v):
    if isinstance(v, Q):
        return str(v)
    if isinstance(v, dict):
        return {str(k): encode(x) for k,x in v.items()}
    if isinstance(v, (tuple,list)):
        return [encode(x) for x in v]
    return v


def authenticate():
    for pin in read(HERE/'SOURCES.json')['files']:
        if pin['usage'] != 'input':
            continue
        b = (ROOT/pin['path']).read_bytes()
        need(sha256(b).hexdigest() == pin['sha256'], 'Source SHA256: '+pin['path'])
        need(sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest() == pin['git_blob'], 'Source Git blob')


def reject(action):
    try:
        action()
    except ValueError as ex:
        return str(ex)
    raise ValueError('Corruption accepted')


def run():
    authenticate()
    builder = load(HERE/'construct.py','clean_transport_construct')
    source = read(HERE/'inputs/pr6375-WORD.json.gz')
    word = builder.construct(source)
    need(word == read(HERE/'WORD.json.gz'), 'Every regenerated scientific word field')
    source_dir = ROOT/'research/p104-root-relay-descent-2'
    src = load(source_dir/'sources.py','clean_transport_sources')
    tree = ROOT/'research/balanced-query-tree'
    edits = read(HERE/'PRICING-EDITS.json')
    text = (tree/'pricing.py').read_text()
    need(sha256(text.encode()).hexdigest() == edits['source_sha256'], 'Price source')
    for a,b in edits['edits']:
        need(text.count(a) == 1, 'Unique price adapter anchor')
        text = text.replace(a,b)
    need(text == (HERE/'pricing.py').read_text(), 'Only declared price literal edits')
    controller = load(tree/'controller.py','controller')
    caller = controller.construct()
    need(encode(caller) == read(tree/'CONTROLLER.json'), 'Pinned complete caller')
    module = load(tree/'module_check.py','clean_transport_module').run()
    caller_check = controller.replay(caller)
    controls = controller.controls(caller)
    with ExitStack() as contexts:
        parent = contexts.enter_context(src.sources())
        cursor = contexts.enter_context(src.load(parent/'sources.py','clean_transport_top').sources())
        for depth in range(7):
            cursor,root = contexts.enter_context(src.load(cursor/'sources.py','clean_transport_archive_'+str(depth)).sources())
        L = src.load(parent/'local.py','clean_transport_local')
        L.ROOT = root
        baseline,local = L.replay(source),L.replay(word)
        need(local['helpers'] == baseline['helpers'], 'No productive target change')
        need(local['paid_rank_mass'] == baseline['paid_rank_mass'] == 5926, 'Linear bill retained')
        need(local['paid'][4] == baseline['paid'][4]-1 and local['paid'][1] == baseline['paid'][1]-1 and local['paid'][5] == baseline['paid'][5]+1, 'Exact 4+1 to5 paid merge')
        zero_module = load(HERE/'owned_zero.py','clean_transport_zero')
        obligations = [dict(field=781,frame=127,count=1)]
        zero = zero_module.verify(word,obligations)
        columns = L.reverse_columns(word)
        need(columns['columns'] == 799 and columns['coefficients'] == 638401, 'Every independent transpose column')
        print('PASS rebuilt word, exact ownership, zero-restored scratch and all799columns',flush=True)
        native = L.native(word)
        physical = load(tree/'physical.py','clean_transport_physical').physical(caller,word,L)
        need(native['distinct_maps'] == 2940 and physical['physical_contacts'] == 7904, 'Complete native/caller map inventory')
        print('PASS all native maps, absolute phases and7904physical contacts',flush=True)
        price = load(HERE/'pricing.py','clean_transport_price').run(local,native,caller,physical,L)
        need(price['raw_root_interval'] == ['315179488707/100000000000000','78794872177/25000000000000'], 'Exact two-engine root bracket')
        bad = deepcopy(word)
        bad['program'].pop(-2)
        controls['new_uncomputation_removed'] = reject(lambda:zero_module.verify(bad,obligations))
        bad2 = deepcopy(word)
        last = max(i for i,e in enumerate(bad2['program']) if e[0]=='ADD' and e[1]<bad2['public'])
        bad2['program'].pop(last)
        controls['public_correction_removed'] = reject(lambda:L.replay(bad2))
        print('PASS two price engines, compiler/precision/outer and corruption controls',flush=True)
    return encode(dict(status=STATUS,kappa='0.003151787',tested='0.003151792',
        source_head='247b5c319b9f58fe9ee61dbf80697f8a9a429831',
        source_word_sha256=sha256((HERE/'inputs/pr6375-WORD.json.gz').read_bytes()).hexdigest(),
        candidate_word_sha256=sha256((HERE/'WORD.json.gz').read_bytes()).hexdigest(),
        local=local,native=native,independent_transpose=columns,new_scratch_zero=zero,
        caller=caller_check,module=module,physical=physical,complete_cost=price,controls=controls,
        assumptions=['native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery'],
        limits=['Conditional source-bound construction, not an unconditional multiplication theorem.',
                'Same-author separate arithmetic checks; no independent human or formal-kernel acceptance.',
                'No materialized rounded multiplier; inherited owned erasure remains conditional.',
                'The selected frontier is unchanged; the .005 objective remains unmet.']))


def main():
    with tempfile.TemporaryDirectory(prefix='clean-piggyback-') as temp:
        old = tempfile.tempdir
        tempfile.tempdir = temp
        sys.pycache_prefix = str(Path(temp)/'bytecode')
        try:
            result = run()
        finally:
            tempfile.tempdir = old
    if '--write-result' in sys.argv:
        (HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        need(result == read(HERE/'RESULT.json'), 'Exact complete receipt')
    print(STATUS,flush=True)


if __name__ == '__main__':
    main()

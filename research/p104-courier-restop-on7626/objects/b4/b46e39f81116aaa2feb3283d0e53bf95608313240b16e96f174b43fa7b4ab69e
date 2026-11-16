"""Complete native and signed application for the timed helper757 update.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
Derived from Hao Yan/7604; retain his application and all source credit.
Retained engines credit ToikY, Rohan Arun, Clear1nsight, DreamingOfClouds,
dillona and their attributed predecessors. No retained file is modified.
"""
import argparse
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
RETAINED = HERE / 'retained/role902'
PEER = HERE / 'retained/pr7604'
NATIVE_MARKER = 'PASS_HELPER757_COMPLETE_NATIVE'
SIGNED_MARKER = 'PASS_HELPER757_COMPLETE_SIGNED_APPLICATION'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw)


def canonical(record):
    return json.dumps(record, sort_keys=True, separators=(',', ':')).encode()


def authenticate():
    for relative, pin in read(RETAINED / 'PINS.json').items():
        path = RETAINED / relative
        assert not path.is_symlink() and path.resolve().is_relative_to(RETAINED)
        assert digest(path.read_bytes()) == pin, relative
    assert digest((PEER / 'word.json.gz').read_bytes()) == 'aae5a85746db1abc5145b993e9a9408076f34c53c4bb8040a99b6a39f2685527'
    spec = importlib.util.spec_from_file_location('helper757_build', HERE / 'build.py')
    build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build)
    word = read(HERE / 'data/word.json.gz')
    assert word == build.build_word(), 'Independently reconstruct the unique helper757 splice'
    assert read(HERE / 'data/invoice-new.json') == build.invoice()
    return word


def adapt(source, patches, output):
    raw = source.read_text()
    record = {'source': str(source.relative_to(HERE)), 'source_sha256': digest(raw.encode()), 'edits': []}
    for before, after in patches:
        assert raw.count(before) == 1, (source.name, before)
        raw = raw.replace(before, after)
        record['edits'].append({'before': before, 'after': after, 'occurrences': 1})
    compile(raw, str(output), 'exec')
    output.write_text(raw)
    record['adapted_sha256'] = digest(raw.encode())
    return record


CHARTS = '''def charts(vendor,word):
    compiler=load('helper757_chart_compiler',vendor/'frozen/clifford_exact.py')
    interpreter=load('helper757_chart_interpreter',vendor/'frozen/native_verify.py')
    before=read(ROOT/'frozen-composition/7481-WORD.json.gz')
    need(sha256(canonical(before)).hexdigest()=='64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8','Exact #7481 physical comparator')
    routes=lambda w:{i:[tuple(e[2:4])for e in w['program']if e[0]=='MOVE'and e[1]==i]for i in range(w['public'])}
    old_routes,new_routes=routes(before),routes(word)
    changed=[i for i in old_routes if old_routes[i]!=new_routes[i]]
    affected={pair for i in changed for pair in old_routes[i]+new_routes[i]}
    need({(3,618),(716,807),(327,907),(618,913),(729,808),(3,603)}<=affected,'Every token-settled, two-contraction, helper315 and helper757 direct pair')
    report=[]
    for a,b in sorted(affected):
        ca,cb=(compiler.canonical_frame(9,tuple(word['frames'][f]))for f in(a,b))
        recipe,_=compiler.lower_child(ca.adjoint().then(cb))
        expected=interpreter.adjoint(interpreter.frame(word['frames'][a],9))+interpreter.frame(word['frames'][b],9)
        actual=interpreter.recipe(recipe)
        interpreter.equal(actual,expected,'Signed Pauli action and absolute phase')
        need(recipe['rank']==len(word['frames'][b])-len(word['frames'][a]),'Exact public ascent rank')
        for x,y in ((actual,expected),(interpreter.adjoint(actual),interpreter.adjoint(expected))):
            for column in range(512):need(interpreter.state(x,column)==interpreter.state(y,column),'Exact forward/adjoint Gaussian column')
        bad=deepcopy(recipe);bad['left']['phase']=(bad['left']['phase']+1)%4
        need(rejects(lambda:interpreter.equal(interpreter.recipe(bad),expected,'Wrong absolute phase')),'Reject wrong phase')
        report.append({'pair':[a,b],'rank':recipe['rank'],'columns':512,'adjoint_columns':512,'absolute_phase_verified':True})
    return {'all_affected_pairs':report,'changed_public_fields':changed,'wrong_phase_rejected':True}

'''


def native_adapter(root, word):
    source = RETAINED / 'engines/7544-native.py'
    original = source.read_text()
    old_charts = original[original.index('def charts('):original.index('def run():')]
    expected = digest(canonical(word))
    patches = [
        ("EXPECTED='2acc6bfd2807239fafdb3f9e09ff8ad34703df958496590ab657ef0b9ac93aef'", f"EXPECTED='{expected}'"),
        (old_charts, CHARTS),
        ("        need(new==read(ROOT/'frozen-composition/COMPOSED-WORD.json.gz'),'Literal composed word')", """        peer=read(ROOT/'frozen-composition/7604-WORD.json.gz')
        need(sha256((ROOT/'frozen-composition/7604-WORD.json.gz').read_bytes()).hexdigest()=='aae5a85746db1abc5145b993e9a9408076f34c53c4bb8040a99b6a39f2685527','Exact open #7604 comparator')
        program=peer['program']
        required={33517:['ADD',1143,757,'-1',3],38584:['MOVE',757,3,595,False],38585:['ADD',757,902,'-1',595],42714:['ADD',757,1557,'-2/3',595],42716:['MOVE',757,595,603,False],42717:['ADD',1255,757,'-1',603]}
        need(all(program[i]==e for i,e in required.items()),'Exact helper757 contacts')
        touches=[i for i in range(33518,42716)if 757 in(program[i][1:3]if program[i][0]in('ADD','COPY')else program[i][1:2])]
        need(touches==[38584,38585,42714],'No intervening read of helper757')
        emitted=[]
        for i,event in enumerate(program):
            if i==33518:emitted.append(['ADD',757,1255,'-1',3])
            if i==42716:emitted.extend([['MOVE',757,3,603,False],['ADD',757,1255,'1',603]])
            elif i not in(38584,38585,42714):emitted.append(event)
        need(new==dict(peer,program=emitted),'Exact timed helper757 word and unchanged metadata')"""),
        ("        oldN,N=map(I.native,(old,new))", """        oldN,peerN,N=map(I.native,(old,peer,new))
        need(all(N[k]==peerN[k]for k in('public','helpers','rises','owned_peak','lifetimes','bad_inputs')),'Fixed complete #7604 ownership and target contract')
        need(delta(N['paid'],peerN['paid'])=={1:-2,2:1},'Exact additional helper757 native saving')"""),
        ("=={1:-1,3:-1,4:-1,5:-1,6:1,7:1}", "=={1:-7,2:-5,4:1,6:1,7:1}"),
        ("len(old['program'])+19", "len(old['program'])+164"),
        ("        bad=deepcopy(new);i=bad['program'].index(['MOVE',485,3,724,False]);bad['program'][i][2]=721", """        bad=deepcopy(new);i=bad['program'].index(['MOVE',757,3,603,False]);bad['program'][i][2]=595
        controls['wrong_helper757_source']=rejects(lambda:I.native(bad))
        bad=deepcopy(new);bad['program'].remove(['MOVE',757,3,603,False])
        controls['missing_helper757_paid_move']=rejects(lambda:I.native(bad))
        bad=deepcopy(new);i=bad['program'].index(['MOVE',485,3,724,False]);bad['program'][i][2]=721"""),
        ('PASS_COMPOSED_7481_7542_COMPLETE_NATIVE', NATIVE_MARKER),
        ("subprocess.run([sys.executable,'-I','-B',str(command)",
         "subprocess.run([sys.executable,'-I','-B','-X','pycache_prefix='+str(ROOT/'isolated/pycache'),str(command)"),
    ]
    return adapt(source, patches, root / 'producer54/validation_native/run.py')


def signed_adapter(root, word):
    expected = digest(canonical(word))
    patches = [
        ("old_word=read(FROZEN/'7481-WORD.json.gz')", "old_word=read(FROZEN/'7546-WORD.json.gz')"),
        ("new_word==read(FROZEN/'COMPOSED-WORD.json.gz'),'Pinned literal composite word'", "new_word==read(FROZEN/'CANDIDATE-WORD.json.gz'),'Pinned literal helper757 word'"),
        ("=='2acc6bfd2807239fafdb3f9e09ff8ad34703df958496590ab657ef0b9ac93aef'", f"=='{expected}'"),
        ("FROZEN/'7481-NATIVE.json'", "FROZEN/'7546-NATIVE.json'"),
        ('PASS_COMPOSED_7481_7542_COMPLETE_NATIVE', NATIVE_MARKER),
        ("=='64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'", "=='bdecd5cc1cb9f164dc695ce07a07d5d44e9961996fcdfa4d77b4092fecbda745'"),
        ("FROZEN/'7481-SIGNED.json'", "FROZEN/'7546-SIGNED.json'"),
        ("Q('0.003647081039689')", "Q('0.003648411294790')"),
        ("{1:-34,5:-17,7:17}", "{1:-102,2:-51,3:17,4:17,5:17}"),
        ("==110485", "==110366"),
        ("Whole reconstructed #7481 invoice", "Whole reconstructed #7546 invoice"),
        ("Strictly higher than #7481 raw crossing", "Strictly higher than #7546 raw crossing"),
        ("Exact #7481 invoice rejects the new signed claim", "Exact #7546 invoice rejects the new signed claim"),
        ("  G=load('producer_signed_price_engine',bundle/'gate.py')", """  peer_word=read(FROZEN/'7604-WORD.json.gz')
  peer_native=ind.native(peer_word);assert not peer_native['bad_inputs']
  peer_invoice=ind.invoices(peer_word,C,peer_native)
  frozen_peer=read(FROZEN/'7604-INVOICE.json')
  assert normal(peer_invoice['P'])==frozen_peer['paid'] and normal(peer_invoice['T'])==frozen_peer['targets']
  assert peer_invoice['S']==1424 and not peer_invoice['empty_root_credits']
  ranks=set(peer_invoice['P'])|set(after['P'])
  assert {r:after['P'].get(r,0)-peer_invoice['P'].get(r,0)for r in ranks if after['P'].get(r,0)!=peer_invoice['P'].get(r,0)}=={1:-34,2:17}
  candidate_invoice=read(FROZEN/'CANDIDATE-INVOICE.json')
  assert normal(after['P'])==candidate_invoice['paid'] and normal(after['T'])==candidate_invoice['targets']
  G=load('producer_signed_price_engine',bundle/'gate.py')"""),
        ("  assert directed.moment(G.signed(native_invoice),Q(gate['claim']))[1]<0", """  assert directed.moment(G.signed(native_invoice),Q(gate['claim']))[1]<0
  assert directed.moment(G.signed(peer_invoice),Q(gate['claim']))[1]<0,'Exact open #7604 invoice rejects the new signed claim'
  assert Q(gate['claim'])>Q('0.0036502223358273'),'Strict improvement over latest #7604 crossing'
  assert Q(gate['claim'])>=Q('0.0036504442446'),'Conservative public claim is within the proved application'"""),
        ("  price_record=normal(dict(before=before,after=after,gate=gate,price=price,", """  public_claim=Q('0.0036504442446')
  public_gate=directed.gate(after,public_claim,public_claim+Q(7,10**14),*map(Q,gate['raw_bracket']),Q(gate['BIT_pin']))
  price_record=normal(dict(public_claim_gate=public_gate,before=before,after=after,gate=gate,price=price,"""),
        ('PASS_COMPOSED_7481_7542_COMPLETE_SIGNED_APPLICATION', SIGNED_MARKER),
        ("source_head='89eaa9d8cae37c1540de98f2d29a3abaabb96a2b'", "source_head='99438c43df7aac1e5dbcc43c1578fcd886c119ec',peer_head='ba2638c5a6e2b9a1c0c559a41811e5d41a591f41'"),
    ]
    return adapt(RETAINED / 'engines/7544-signed.py', patches, root / 'producer54/validation_signed/run.py')


def prepare(root, word):
    root.mkdir(parents=True, exist_ok=True)
    (root / 'isolated').mkdir(exist_ok=True)
    shutil.copytree(RETAINED / 'upstream/inputs', root / 'inputs')
    frozen = root / 'frozen-composition'
    frozen.mkdir()
    files = {
        '7481-WORD.json.gz': RETAINED / 'bench/7481-WORD.json.gz',
        '7546-WORD.json.gz': RETAINED / 'expected/role902-WORD.json.gz',
        '7546-NATIVE.json': RETAINED / 'expected/NATIVE.json',
        '7546-SIGNED.json': RETAINED / 'expected/SIGNED.json',
        '7604-WORD.json.gz': PEER / 'word.json.gz',
        '7604-INVOICE.json': PEER / 'invoice-new.json',
        'CANDIDATE-WORD.json.gz': HERE / 'data/word.json.gz',
        'CANDIDATE-INVOICE.json': HERE / 'data/invoice-new.json',
    }
    for name, path in files.items():
        shutil.copyfile(path, frozen / name)
    for name in ('reroute', 'validation_native', 'validation_signed'):
        (root / 'producer54' / name).mkdir(parents=True)
    shutil.copyfile(HERE / 'data/word.json.gz', root / 'producer54/reroute/WORD.json.gz')
    shutil.copyfile(RETAINED / 'engines/7481-EMISSION.json', root / 'producer54/reroute/RESULT.json')
    records = [native_adapter(root, word), signed_adapter(root, word)]
    (root / 'ADAPTERS.json').write_text(json.dumps(records, indent=2) + '\n')


def normalized_receipt(record):
    record = dict(record)
    record.pop('timings', None)
    record.pop('elapsed_seconds', None)
    return record


def final_application(root):
    native = read(root / 'producer54/validation_native/NATIVE-RESULT.json')
    signed = read(root / 'producer54/validation_signed/RESULT.json')
    old = read(RETAINED / 'expected/FINAL.json')
    assert native['status'] == NATIVE_MARKER and signed['status'] == SIGNED_MARKER
    assert native['word_canonical_sha256'] == digest(canonical(read(HERE / 'data/word.json.gz')))
    assert signed['price']['new_native'] == native['word_canonical_sha256']
    assert signed['caller_sha256'] == '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc'
    assert signed['assumptions'] == old['assumptions']
    assert native['native']['lifetimes'] == 74 and native['native']['owned_peak'] == 50
    assert native['derived_grid']['odd_scale'] == 1125 and native['derived_grid']['fractional_bits'] == 25
    assert native['controls'] and all(native['controls'].values())
    assert native['controls']['wrong_helper757_source'] and native['controls']['missing_helper757_paid_move']
    assert native['charts']['wrong_phase_rejected']
    pairs = {tuple(item['pair']): item for item in native['charts']['all_affected_pairs']}
    for pair, rank in (((3, 618), 3), ((716, 807), 3), ((327, 907), 5), ((618, 913), 4), ((729, 808), 2), ((3, 603), 2)):
        item = pairs[pair]
        assert item['rank'] == rank and item['columns'] == item['adjoint_columns'] == 512 and item['absolute_phase_verified']
    assert native['physical_checks'] == ['verify_host3_odd.py', 'physical.py']
    price = signed['price']
    invoice = price['after']
    target = read(HERE / 'data/invoice-new.json')
    assert invoice['P'] == target['paid'] and invoice['T'] == target['targets']
    assert invoice['S'] == 1424 and invoice['empty_root_credits'] == 0
    assert sum(invoice['P'].values()) == 110366 and sum(invoice['T'].values()) == 22461
    checks = signed['checks']
    partial = checks['ODD-ADMISSION-PARTIAL.json']
    assert partial['invoice'] == invoice and partial['compiler_outer'] == price['gate']
    for gate in (price['gate'], price['public_claim_gate']):
        outer = gate['outer']
        assert outer['strict_count'] == 54 and outer['functional_count'] == 4
        assert Q(outer['minimum_margin']) > 0 and outer['BIT_just_below_effective_rejected']
    assert Q(price['public_claim_gate']['claim']) == Q('0.0036504442446')
    assert Q(price['public_claim_gate']['tested']) == Q('0.00365044424467')
    ordinary = partial['ordinary']['conservative_total']
    assert ordinary < 10**9
    joined = checks['ODD-8X9-APPLICATION-CHECKS.json']
    assert joined['status'] == 'PASS_8X9_EXACT_COMPONENT_APPLICATION_CHECKS'
    assert joined['native_canonical_sha256'] == native['word_canonical_sha256']
    assert joined['caller_sha256'] == signed['caller_sha256']
    catalogue = signed['catalogue']
    maps = sum(item['checked_maps'] for item in catalogue)
    assert catalogue and all(item['catalogue_size'] == maps for item in catalogue)
    assert sum(item['main_boundary_pairs'] for item in catalogue) == 104
    tape = checks['ODD-FIXED-TAPE-COUNTS.json']
    precision = checks['ODD-PRECISION.json']
    assert tape['context_c'] == precision['context_c'] and tape['native_invocations'] == 17
    public_h = int(price['public_claim_gate']['H'])
    public_kstar = 1920 * 153**1920 * (public_h + 1)**2
    public_context_bits = (4096 * public_kstar).bit_length()
    assert precision['context_c'] <= 4096 and public_context_bits < public_h
    assert max(item['strict_power_of_two'] for item in precision['rounded_caller']['bounds'].values()) < public_h
    fields = ('native_invocations', 'monomial_map_slots', 'elementary_records_upper', 'scalar_services_upper')
    return dict(status='PASS_HELPER757_FINAL_APPLICATION', claim='0.0036504442446',
                framework_claim=signed['claim'], raw_crossing=price['gate']['raw_bracket'],
                candidate_canonical_sha256=native['word_canonical_sha256'], caller_sha256=signed['caller_sha256'],
                paid_calls=110366, productive_calls=22461, surplus=1424,
                ordinary_bound=ordinary, ordinary_change_over_7546=ordinary-old['ordinary_bound'],
                precision_c=precision['context_c'], tape={k: tape[k] for k in fields},
                public_context_bound_bits=public_context_bits, public_H=public_h,
                public_claim_derivation='Weakening the stronger complete framework claim; tape H inequalities also checked at the public gate.',
                tape_change_over_7546={k: tape[k]-old['tape'][k] for k in fields},
                outer=price['public_claim_gate']['outer'], signed_physical_map_count=maps,
                assumptions=signed['assumptions'])


def execute(stage, root, bootstrap):
    native = root / 'producer54/validation_native/NATIVE-RESULT.json'
    pinned = HERE / 'data/NATIVE.json'
    if stage == 'signed':
        assert pinned.exists(), 'Complete fresh native stage must be frozen before signed replay'
        shutil.copyfile(pinned, native)
    script = root / f'producer54/validation_{stage}/run.py'
    started = time.monotonic()
    cache = root / 'isolated/pycache'
    environment = dict(os.environ, TMPDIR=str(root / 'isolated'), PYTHONPYCACHEPREFIX=str(cache))
    with (root / f'{stage}.stdout').open('w') as stdout, (root / f'{stage}.stderr').open('w') as stderr:
        result = subprocess.run([sys.executable, '-I', '-B', '-X', f'pycache_prefix={cache}', str(script)], cwd=root,
                                env=environment, stdout=stdout, stderr=stderr, timeout=560)
    receipt = {'stage': stage, 'exit': result.returncode, 'seconds': time.monotonic()-started}
    (root / f'{stage}.receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print((root / f'{stage}.stdout').read_text(), end='')
    if result.returncode:
        sys.stderr.write((root / f'{stage}.stderr').read_text())
        raise SystemExit(result.returncode)
    record = native if stage == 'native' else root / 'producer54/validation_signed/RESULT.json'
    expected = HERE / ('data/NATIVE.json' if stage == 'native' else 'data/SIGNED.json')
    if not bootstrap:
        assert normalized_receipt(read(record)) == normalized_receipt(read(expected)), 'Fresh complete application receipt differs'
    if stage == 'signed':
        final = final_application(root)
        (root / 'FINAL.json').write_text(json.dumps(final, indent=2, sort_keys=True) + '\n')
        if not bootstrap:
            assert final == read(HERE / 'data/FINAL.json')
    print(json.dumps(receipt), flush=True)


def main():
    if sys.flags.optimize or sys.version_info[:2] != (3, 12):
        raise ValueError('Use Python 3.12 with assertions enabled')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=('native', 'signed'), required=True)
    parser.add_argument('--work', type=Path, help='Retain fresh receipts in a previously absent scratch directory')
    parser.add_argument('--bootstrap', action='store_true', help='Emit candidate receipts before committing their expected snapshots')
    args = parser.parse_args()
    word = authenticate()
    if args.work:
        assert not args.work.exists()
        root = args.work.resolve()
        prepare(root, word)
        execute(args.stage, root, args.bootstrap)
    else:
        with tempfile.TemporaryDirectory(prefix='helper757-application-') as work:
            root = Path(work).resolve()
            prepare(root, word)
            execute(args.stage, root, args.bootstrap)
    authenticate()


if __name__ == '__main__':
    main()

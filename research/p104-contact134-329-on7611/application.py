#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Counted retarget of #7605's complete application to the #7611 contact edit.

The retained #7605 application and engines remain unchanged.  This launcher
constructs their scripts in an isolated root and records each exact source
replacement.  Scientific execution requires the caller's external resource
lease; this launcher does not establish a cgroup itself.
"""
import argparse
from collections import defaultdict
from fractions import Fraction
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
P7605 = HERE / 'retained/pr7605'
P7608 = HERE / 'retained/pr7608'
P7611 = HERE / 'retained/pr7611'
BASE_CANON = 'e20f3f9240ac3f5fa4bbd7ab9b5550d660886901bb209f335409c329ac45d9cd'
PEER_CANON = '177b74c42ac633aaee21b0bbd5373441ccba8e5bad029d827877cf2d585fd0e3'
APP_SHA = 'b46e39f81116aaa2feb3283d0e53bf95608313240b16e96f174b43fa7b4ab69e'
NATIVE = 'PASS_HELPER757_COMPLETE_NATIVE'
SIGNED = 'PASS_HELPER757_COMPLETE_SIGNED_APPLICATION'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def patch_file(path, replacements):
    text = path.read_text()
    before_sha = sha(text.encode())
    edits = []
    for old, new in replacements:
        count = text.count(old)
        if count != 1:
            raise ValueError(f'{path.name}: expected one occurrence, found {count}: {old[:120]!r}')
        text = text.replace(old, new)
        edits.append({'before': old, 'after': new, 'occurrences': count})
    compile(text, str(path), 'exec')
    path.write_text(text)
    return {'file': str(path.name), 'source_sha256': before_sha,
            'adapted_sha256': sha(text.encode()), 'edits': edits}


def apply_edits(program, edit):
    assert len(program) == edit['base_events']
    deleted = {}
    for i, event in edit['delete']:
        assert i not in deleted and program[i] == event
        deleted[i] = event
    inserted = defaultdict(list)
    for i, events in edit['insert_before']:
        assert 0 <= i <= len(program)
        inserted[i].extend(events)
    result = []
    for i, event in enumerate(program):
        result.extend(inserted[i])
        if i not in deleted:
            result.append(event)
    result.extend(inserted[len(program)])
    return result + edit['append']


def authenticate_candidate(build):
    build.authenticate()
    assert sha((P7605 / 'application.py').read_bytes()) == APP_SHA
    base_mod = load('retained_7605_application', P7605 / 'application.py')
    base = base_mod.authenticate()
    assert sha(canonical(base)) == BASE_CANON
    w08 = read(P7608 / 'data/word.json.gz')
    assert read(P7608 / 'data/base-7605-word.json.gz') == base
    assert w08 == dict(base, program=apply_edits(base['program'], read(P7608 / 'data/edits.json')))
    w11 = read(P7611 / 'data/word.json.gz')
    assert sha(canonical(w11)) == PEER_CANON
    assert read(P7611 / 'data/base-7608-word.json.gz') == w08
    assert w11 == dict(w08, program=apply_edits(w08['program'], read(P7611 / 'data/edits.json')))
    candidate = build.build_word()
    p = w11['program']
    checks = {41073:['MOVE',134,3,618,False],41074:['MOVE',329,373,618,False],
              41075:['ADD',134,329,'-1/2',618],41166:['MOVE',329,618,733,False],
              42110:['MOVE',134,618,913,False]}
    assert all(p[i] == v for i,v in checks.items())
    assert [i for i in range(41073,42111) if 134 in (p[i][1:3] if p[i][0] in ('ADD','COPY') else p[i][1:2])] == [41073,41075,42110]
    assert [i for i in range(41074,41167) if 329 in (p[i][1:3] if p[i][0] in ('ADD','COPY') else p[i][1:2])] == [41074,41075,41166]
    changes = {41073:['MOVE',134,3,373,False],41075:['ADD',134,329,'-1/2',373],
               41166:['MOVE',329,373,733,False],42110:['MOVE',134,373,913,False]}
    expected = [changes.get(i,e) for i,e in enumerate(p) if i != 41074]
    assert candidate == dict(w11, program=expected)
    assert read(HERE / 'data/word.json.gz') == candidate
    assert read(HERE / 'data/invoice-new.json') == build.invoice()
    return base_mod, base, w11, candidate


def prepare(root, base_mod, base, candidate, price):
    # The retained prepare first generates the fully counted #7605 scripts.
    base_mod.prepare(root, base)
    frozen = root / 'frozen-composition'
    for dst, src in {
        '7605-WORD.json.gz': P7605/'data/word.json.gz',
        '7611-WORD.json.gz': P7611/'data/word.json.gz',
        '7611-INVOICE.json': P7611/'data/invoice-new.json',
        'CANDIDATE-WORD.json.gz': HERE/'data/word.json.gz',
        'CANDIDATE-INVOICE.json': HERE/'data/invoice-new.json',
    }.items():
        shutil.copyfile(src, frozen/dst)
    shutil.copyfile(HERE/'data/word.json.gz', root/'producer54/reroute/WORD.json.gz')
    npath = root/'producer54/validation_native/run.py'
    spath = root/'producer54/validation_signed/run.py'
    basehash = BASE_CANON
    newhash = sha(canonical(candidate))
    native_patches = [
        ("EXPECTED='"+basehash+"'", "EXPECTED='"+newhash+"'"),
        ("        need(new==dict(peer,program=emitted),'Exact timed helper757 word and unchanged metadata')",
         "        baseline=read(ROOT/'frozen-composition/7605-WORD.json.gz')\n"
         "        need(sha256(canonical(baseline)).hexdigest()=='"+basehash+"' and baseline==dict(peer,program=emitted),'Exact helper757 lineage')\n"
         "        immediate=read(ROOT/'frozen-composition/7611-WORD.json.gz')\n"
         "        need(sha256(canonical(immediate)).hexdigest()=='"+PEER_CANON+"','Exact immediate #7611 source')\n"
         "        p=immediate['program']; changes={41073:['MOVE',134,3,373,False],41075:['ADD',134,329,'-1/2',373],41166:['MOVE',329,373,733,False],42110:['MOVE',134,373,913,False]}\n"
         "        need(new==dict(immediate,program=[changes.get(i,e) for i,e in enumerate(p) if i!=41074]),'Exact occurrence-bound candidate and metadata')"),
        ("        oldN,peerN,N=map(I.native,(old,peer,new))\n        need(all(N[k]==peerN[k]for k in('public','helpers','rises','owned_peak','lifetimes','bad_inputs')),'Fixed complete #7604 ownership and target contract')\n        need(delta(N['paid'],peerN['paid'])=={1:-2,2:1},'Exact additional helper757 native saving')",
         "        oldN,peerN,baselineN,immediateN,N=map(I.native,(old,peer,baseline,immediate,new))\n"
         "        need(all(baselineN[k]==peerN[k] for k in ('public','helpers','rises','owned_peak','lifetimes','bad_inputs')),'Fixed #7604 ownership and targets')\n"
         "        need(delta(baselineN['paid'],peerN['paid'])=={1:-2,2:1},'Exact helper757 native saving')\n"
         "        need(all(N[k]==immediateN[k] for k in ('public','helpers','rises','owned_peak','lifetimes','bad_inputs')),'Fixed immediate ownership and targets')\n"
         "        need(delta(N['paid'],immediateN['paid'])=={1:-2,2:2,3:-1,4:-1,5:1},'Exact contact native paid delta')"),
        ("=={1:-7,2:-5,4:1,6:1,7:1}", "=={1:-13,2:-6,4:-1,5:2,6:2,7:1}"),
        ("len(old['program'])+164", "len(old['program'])+195"),
        ("        bad=deepcopy(new);i=bad['program'].index(['MOVE',485,3,724,False]);bad['program'][i][2]=721",
         "        bad=deepcopy(new);i=bad['program'].index(['MOVE',134,373,913,False]);bad['program'][i][2]=618\n"
         "        controls['wrong_contact_source']=rejects(lambda:I.native(bad))\n"
         "        bad=deepcopy(new);bad['program'].remove(['MOVE',329,373,733,False])\n"
         "        controls['missing_contact_paid_move']=rejects(lambda:I.native(bad))\n"
         "        bad=deepcopy(new);i=bad['program'].index(['MOVE',485,3,724,False]);bad['program'][i][2]=721"),
        ("need({(3,618),(716,807),(327,907),(618,913),(729,808),(3,603)}<=affected,",
         "need(len(affected)==66 and changed==[46,82,100,134,166,185,315,329,757,761,902,1077],'Exact affected-pair and role denominator')\n"
         "    need({(3,618),(716,807),(327,907),(618,913),(729,808),(3,603),(3,373),(373,733),(373,913),(401,922),(513,127),(740,1071)}<=affected,"),
        ("        for x,y in ((actual,expected),(interpreter.adjoint(actual),interpreter.adjoint(expected))):\n"
         "            for column in range(512):need(interpreter.state(x,column)==interpreter.state(y,column),'Exact forward/adjoint Gaussian column')",
         "        actual_h,expected_h=interpreter.adjoint(actual),interpreter.adjoint(expected)\n"
         "        interpreter.equal(actual_h,expected_h,'Adjoint signed Pauli action and absolute phase')\n"
         "        dense=(a,b) in {(3,373),(373,733),(373,913),(401,922),(513,127),(740,1071)}\n"
         "        if dense:\n"
         "            for x,y in ((actual,expected),(actual_h,expected_h)):\n"
         "                for column in range(512):need(interpreter.state(x,column)==interpreter.state(y,column),'Exact forward/adjoint Gaussian column')"),
        ("        report.append({'pair':[a,b],'rank':recipe['rank'],'columns':512,'adjoint_columns':512,'absolute_phase_verified':True})",
         "        coverage={'pair':[a,b],'rank':recipe['rank'],'forward_signed_pauli_generators':18,'adjoint_signed_pauli_generators':18,'forward_exact_phase_columns':1,'adjoint_exact_phase_columns':1,'operator_dimension':512,'full_operator_equality':'signed_pauli_and_exact_phase','absolute_phase_verified':True}\n"
         "        if dense:coverage.update(columns=512,adjoint_columns=512)\n"
         "        report.append(coverage)"),
        ("checkpoint('all affected Gaussian columns and absolute phase, finite physical replay and signed routes')",
         "checkpoint('all affected signed Pauli and exact phase, six dense forward/adjoint pairs, finite physical replay and signed routes')"),
    ]
    signed_patches = [
        ("=='"+basehash+"'", "=='"+newhash+"'"),
        ("{1:-102,2:-51,3:17,4:17,5:17}", "{1:-204,2:-68,3:17,4:-17,5:51,6:17}"),
        ("==110366", "==110264"),
        ("peer_word=read(FROZEN/'7604-WORD.json.gz')", "peer_word=read(FROZEN/'7611-WORD.json.gz')"),
        ("frozen_peer=read(FROZEN/'7604-INVOICE.json')", "frozen_peer=read(FROZEN/'7611-INVOICE.json')"),
        ("=={1:-34,2:17}", "=={1:-34,2:34,3:-17,4:-17,5:17}"),
        ("Q(gate['claim'])>Q('0.0036502223358273')", "Q(gate['claim'])>Q('"+str(price.TESTED)+"')"),
        ("Q(gate['claim'])>=Q('0.0036504442446')", "Q(gate['claim'])>=Q('"+str(price.CLAIM)+"')"),
        ("public_claim=Q('0.0036504442446')", "public_claim=Q('"+str(price.CLAIM)+"')"),
        ("public_claim+Q(7,10**14)", "Q('"+str(price.TESTED)+"')"),
    ]
    records = [patch_file(npath,native_patches), patch_file(spath,signed_patches)]
    (root/'CONTACT-ADAPTERS.json').write_text(json.dumps(records, indent=2, sort_keys=True)+'\n')
    return records


def validate_native(path, expected_word, expected_adapter):
    raw = Path(path).read_bytes()
    obj = json.loads(raw)
    assert obj['status'] == NATIVE
    assert obj['word_canonical_sha256'] == expected_word
    assert obj['controls'] and all(obj['controls'].values())
    assert obj['controls']['wrong_helper757_source'] and obj['controls']['missing_helper757_paid_move']
    assert obj['controls']['wrong_contact_source'] and obj['controls']['missing_contact_paid_move']
    assert obj['physical_checks'] == ['verify_host3_odd.py', 'physical.py']
    assert obj['native']['lifetimes'] == 74 and obj['native']['owned_peak'] == 50
    assert obj['derived_grid']['odd_scale'] == 1125 and obj['derived_grid']['fractional_bits'] == 25
    assert obj['charts']['wrong_phase_rejected']
    rows = obj['charts']['all_affected_pairs']
    pairs = {tuple(x['pair']):x for x in rows}
    assert len(rows)==len(pairs)==66
    assert obj['charts']['changed_public_fields']==[46,82,100,134,166,185,315,329,757,761,902,1077]
    dense = {(3,373):2,(373,733):2,(373,913):5,(401,922):5,(513,127):6,(740,1071):3}
    assert set(dense) <= set(pairs)
    for pair,x in pairs.items():
        assert x['forward_signed_pauli_generators']==x['adjoint_signed_pauli_generators']==18
        assert x['forward_exact_phase_columns']==x['adjoint_exact_phase_columns']==1
        assert x['operator_dimension']==512 and x['full_operator_equality']=='signed_pauli_and_exact_phase'
        assert x['absolute_phase_verified']
        if pair in dense:
            assert x['rank']==dense[pair] and x['columns']==x['adjoint_columns']==512
        else:
            assert 'columns' not in x and 'adjoint_columns' not in x
    assert expected_adapter, 'Adapter ledger must be authenticated by caller'
    return obj, sha(raw)


def main():
    assert __debug__ and sys.version_info[:2] == (3,12)
    parser=argparse.ArgumentParser()
    parser.add_argument('--stage', choices=('native','signed'), required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--native-result', type=Path)
    parser.add_argument('--native-adapters', type=Path)
    args=parser.parse_args()
    assert not args.work.exists()
    if args.stage == 'signed':
        assert args.native_result and args.native_adapters, 'fresh native receipt and adapter ledger required'
    else:
        assert not args.native_result and not args.native_adapters
    build=load('contact_build', HERE/'build.py')
    price=load('contact_price', HERE/'price.py')
    base_mod,base,peer,candidate=authenticate_candidate(build)
    root=args.work.resolve()
    records=prepare(root,base_mod,base,candidate,price)
    native_path=root/'producer54/validation_native/NATIVE-RESULT.json'
    candidate_hash=sha(canonical(candidate))
    if args.stage == 'signed':
        expected_records=json.loads(args.native_adapters.read_bytes())
        assert expected_records == records, 'native and signed counted adapter ledgers differ'
        assert not args.native_result.is_symlink() and not args.native_adapters.is_symlink()
        _, native_digest=validate_native(args.native_result,candidate_hash,expected_records)
        source_receipt=read(args.native_result.parent.parent.parent/'native.receipt.json')
        assert source_receipt['stage']=='native' and source_receipt['exit']==0
        assert source_receipt['candidate_canonical_sha256']==candidate_hash
        assert source_receipt['native_result_sha256']==native_digest
        assert source_receipt['adapter_sha256']==sha(args.native_adapters.read_bytes())
        assert source_receipt['launcher_sha256']==sha(Path(__file__).read_bytes())
        # Explicit negative control: an ancestor receipt must fail candidate binding.
        try:
            validate_native(P7605/'data/NATIVE.json',candidate_hash,expected_records)
        except (AssertionError, KeyError):
            pass
        else:
            raise AssertionError('stale #7605 native receipt accepted')
        shutil.copyfile(args.native_result,native_path)
        assert sha(native_path.read_bytes()) == native_digest
    script=root/f'producer54/validation_{args.stage}/run.py'
    start=time.monotonic()
    env=dict(os.environ,TMPDIR=str(root/'isolated'),PYTHONPYCACHEPREFIX=str(root/'isolated/pycache'))
    with (root/f'{args.stage}.stdout').open('x') as out, (root/f'{args.stage}.stderr').open('x') as err:
        result=subprocess.run([sys.executable,'-I','-B','-X',f'pycache_prefix={root}/isolated/pycache',str(script)],cwd=root,env=env,stdout=out,stderr=err,check=False)
    receipt={'stage':args.stage,'exit':result.returncode,'seconds':time.monotonic()-start,
             'candidate_canonical_sha256':candidate_hash,'adapter_sha256':sha((root/'CONTACT-ADAPTERS.json').read_bytes()),
             'launcher_sha256':sha(Path(__file__).read_bytes())}
    (root/f'{args.stage}.receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    assert result.returncode == 0, 'complete stage failed; inspect logs'
    if args.stage == 'native':
        _,native_digest=validate_native(native_path,candidate_hash,records)
        receipt['native_result_sha256']=native_digest
        (root/f'{args.stage}.receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    else:
        signed=read(root/'producer54/validation_signed/RESULT.json')
        assert signed['status']==SIGNED and signed['price']['new_native']==candidate_hash
        assert signed['caller_sha256']=='255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc'
        assert Fraction(signed['price']['gate']['claim']) >= Fraction(str(price.CLAIM))
        assert signed['assumptions']==['native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery']
        gate=signed['price']['public_claim_gate']['outer']
        assert gate['strict_count']==54 and gate['functional_count']==4 and Fraction(gate['minimum_margin'])>0 and gate['BIT_just_below_effective_rejected']
        assert signed['checks']['ODD-ADMISSION-PARTIAL.json']['invoice']==signed['price']['after']
        assert signed['checks']['ODD-ADMISSION-PARTIAL.json']['compiler_outer']==signed['price']['gate']
        assert sum(x['main_boundary_pairs'] for x in signed['catalogue'])==104
        assert signed['checks']['ODD-ADMISSION-PARTIAL.json']['ordinary']['conservative_total']<10**9
        tape=signed['checks']['ODD-FIXED-TAPE-COUNTS.json']
        precision=signed['checks']['ODD-PRECISION.json']
        assert tape['native_invocations']==17 and tape['context_c']==precision['context_c']
        h=int(signed['price']['public_claim_gate']['H'])
        kstar=1920 * 153**1920 * (h+1)**2
        assert precision['context_c'] <= 4096 and (4096*kstar).bit_length() < h
        assert max(x['strict_power_of_two'] for x in precision['rounded_caller']['bounds'].values()) < h
        joined=signed['checks']['ODD-8X9-APPLICATION-CHECKS.json']
        assert joined['status']=='PASS_8X9_EXACT_COMPONENT_APPLICATION_CHECKS'
        assert joined['native_canonical_sha256']==candidate_hash and joined['caller_sha256']==signed['caller_sha256']
        maps=sum(item['checked_maps'] for item in signed['catalogue'])
        assert maps and all(item['catalogue_size']==maps for item in signed['catalogue'])
        receipt['native_result_sha256']=native_digest
        receipt['stale_7605_rejected']=True
        (root/f'{args.stage}.receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(receipt,sort_keys=True),flush=True)


if __name__=='__main__':
    main()

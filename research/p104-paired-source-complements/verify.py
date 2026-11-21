#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Authenticate the exact predecessor, reprice the fixed supplier, replay the signed application."""
import argparse
from fractions import Fraction as F
from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path, PurePosixPath
import runpy
import sys
import tarfile
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from certificate import COVER, H, OLD_CAP, OLD_CLAIM, SEED, TICK, TRIAL, certify, require

PREDECESSOR = 'c3837013dd7e2c50f6c3065c8f99d52a33b617bb'
PAIRED = 'fb9b6a7b0d27da1cf98430893a3016bf811e2aa4'
PREVIOUS_REPLAY = '0fed060d852e6e37c1ff4ffe514d5765c9efdd6e0a3a24f6bc59cbbdcc7b0d79'
PREVIOUS_ACCEPT = '0b179d16461707f2ec6b0ea02149b1dfef0f667a051da475fa400713a01f6377'
PAIR_NAME = 'research/p104-paired-delayed-cover'


def read(path,digest=None):
    content=path.read_bytes()
    if digest:
        require(sha256(content).hexdigest()==digest, f'input SHA-256 {path.name}')
    return json.loads(content)


def write(path,data):
    with path.open('x') as handle:
        json.dump(data,handle,sort_keys=True,indent=2)
        handle.write('\n')


def module(id,path):
    spec=importlib.util.spec_from_file_location(id,path)
    loaded=importlib.util.module_from_spec(spec)
    sys.modules[id]=loaded
    spec.loader.exec_module(loaded)
    return loaded


def restore_tree(work):
    source=read(HERE/'SOURCES.json')['offline_predecessor']
    require(source['head']==PREDECESSOR and source['path']==PAIR_NAME, 'exact comparative head')
    archive=HERE/source['archive']
    require(sha256(archive.read_bytes()).hexdigest()==source['archive_sha256'],'comparative archive bytes')
    seen={}
    root=work/PAIR_NAME
    root.mkdir(parents=True)
    with tarfile.open(archive) as tar:
        for item in tar:
            name=item.name
            parts=PurePosixPath(name).parts
            require(parts and '/'.join(parts)==name and '\\' not in name and
                    all(part not in ('/', '.', '..') for part in parts) and name not in seen,
                    'unique confined source paths')
            require(item.isfile() and not item.linkname and set(('size','git_blob','sha256','mode'))==set(source['files'].get(name,{})),
                    'archive member is a registered regular file')
            pin=source['files'][name]
            require(item.size==pin['size'] and item.size<=4*1024*1024 and pin['mode'] in ('100644','100755'),
                    'expected size and Git mode')
            with tar.extractfile(item) as member:
                raw=member.read()
            git_blob=sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            require(len(raw)==item.size and git_blob==pin['git_blob'] and sha256(raw).hexdigest()==pin['sha256'],
                    f'byte-for-byte pinned source {name}')
            dest=root.joinpath(*parts)
            dest.parent.mkdir(parents=True,exist_ok=True)
            with dest.open('xb') as output:
                output.write(raw)
            seen[name]=(pin['mode'],git_blob)
    require(set(seen)==set(source['files']), 'complete comparative archive')
    require(tree_hash(seen)==source['tree'], 'exact predecessor package Git tree')
    return root


def tree_hash(files):
    directories={}
    entries=[]
    for name,(mode,hex_blob) in files.items():
        node,sep,rest=name.partition('/')
        if sep:
            directories.setdefault(node,{})[rest]=(mode,hex_blob)
        else:
            entries.append((node,mode,hex_blob))
    entries.extend((node,'40000',tree_hash(children)) for node,children in directories.items())
    entries.sort(key=lambda item:(item[0]+('/' if item[1]=='40000' else '')).encode())
    payload=b''.join(mode.encode()+b' '+name.encode()+b'\0'+bytes.fromhex(blob) for name,mode,blob in entries)
    return sha1(b'tree '+str(len(payload)).encode()+b'\0'+payload).hexdigest()


def repriced_bit(engine,orig,base,cert):
    native=base['binary_native']
    paid={int(k):v for k,v in native['paid_all'].items()}
    productive={int(k):v for k,v in native['productive_all'].items()}
    signed=engine.signed_profile(productive,paid)
    old=orig['peer_finite']
    require(old['raw_crossing']==base['binary_raw'] and old['finite_separation']['paid']==native['paid_all']
            and old['finite_separation']['targets']==native['productive_all'], 'source-bound 36-call signed inventory')
    margin=engine.moment(signed,TRIAL)
    bad=signed.copy()
    bad[1]-=1
    require(margin[0]>0>engine.moment(bad,TRIAL)[1], 'directed trial and one-added-BIT-call control')
    independent=engine.compiler(paid,productive,TRIAL)
    require((independent['H'],independent['product_exponent'],independent['cutoff'],independent['productive_floor'],
             independent['ambient_base'])==(H,768,15,16,134), 'independent rational finite compiler and fixed dimensions')
    require(F(orig['delayed_cover_debit'])==COVER and old['cover_prime_condition']==
            'odd q > 2^45*N^5 avoiding the frozen finite catalogue witnesses', 'original same-prime fallback and stock')
    require(F(cert['strict']['normalized_strict_gap'][0])>0 and
            F(old['tested_saving'])==F('.003890115276594'), 'revised separated strictness at the original word')
    cap, rows=engine.bootstrap(SEED,F(cert['covered']),[stage['admitted'] for stage in cert['stages']])
    require(cap==F(cert['cap']) and len(rows)==4, 'complete paid BIT cap')
    for original,candidate in zip(rows,cert['stages'],strict=True):
        edge=F(candidate['bound'])
        require(original['claim']==candidate['admitted'] and F(original['previous'])==F(candidate['previous']) and
                F(original['envelope'][0])<=edge<=F(original['envelope'][1]) and F(candidate['slack'])>0,
                'independent four-stage price and margins')
    return cap, {'independent_rational_compiler':independent,'new_margin':engine.decimal_interval(margin),
                 'bootstrap_stages':rows,'original_stock':old['stock'],'original_cutoff_prime':old['cover_prime_condition'],
                 'literal_word':base['binary_word'],'native':native}


def replay(work):
    previous=restore_tree(work/'predecessor')
    old_verify=module('p104_verified_predecessor',previous/'verify.py')
    old_verify.unpack(work/'peer-export')
    adapter=module('p104_verified_adapter',previous/'application/replay.py')
    require(adapter.HEAD==PAIRED,'paired immutable source head')
    old_primary=read(previous/'primary/PRICE.json',adapter.PRIMARY)
    old_independent=read(previous/'independent/PRICE.json',adapter.INDEPENDENT)
    old=read(previous/'weighted/moment/application/RESULT.json',PREVIOUS_REPLAY)
    old_accept=read(previous/'weighted/moment/independent/ACCEPT.json',PREVIOUS_ACCEPT)
    require(old_accept['replay_sha256']==PREVIOUS_REPLAY and old_accept['cap']==old['cap'] and
            F(old['cap'])==OLD_CAP and F(old['claim'])==OLD_CLAIM and old_accept['claim']==old['claim'],
            'sealed complete comparative application and independent check')
    peer=adapter.peer_copy(work/'peer-code',work/'peer-export')
    base=peer.read('APPLICATION.json')
    require(adapter.certify(old_primary,old_independent,base)==F('.003890115176583'),'predecessor cover control')
    native=base['binary_native']
    certificate=certify(native['paid_all'],native['productive_all'],base['binary_raw'],base['rational_raw'])
    print('PASS_SOURCE_COMPLEMENTS_AND_PAID_MOMENTS',certificate['terminal_debit_numerator'],certificate['cap'],flush=True)
    package=peer.source_tree(work,base)
    original=adapter.normalize(adapter.binary(peer,work,package,base,old_primary))
    cap,bit=repriced_bit(sys.modules['binary_price'],original,base,certificate)
    print('PASS_LITERAL_36_CALL_BIT_STOCK_AND_NEAR_CROSSING_TRIAL',certificate['C'],flush=True)
    old_app=dict(base,binary_ordinary=old['cap'],claim=old['claim'],outer=old['outer'])
    app=dict(base,binary_ordinary=certificate['cap'],claim=certificate['claim'])
    word,layout,physical=peer.rational_application(work,package,app,cap)
    physical=adapter.normalize(physical)
    invoice={'T':physical['application']['invoice']['targets'],'P':physical['application']['invoice']['paid']}
    require(invoice==old_accept['invoice'] and physical['caller']==old['caller'] and
            physical['caller_census']['calls']==base['rational_calls']==48 and
            old['source_archive']==base['source_archive'] and old['source_count']==base['source_count']==134,
            'unchanged signed rational invoice, route and source closure')
    outer=adapter.outer_prices(peer,work,old_app,app,physical)
    app.update(H=outer['H'],outer=outer['outer'])
    require(old['premises']==app['premises'] and len(app['premises'])==5, 'five named inherited contracts')
    peer.audit(work,package,app,cap,word,layout,physical)
    independent=runpy.run_path(str(previous/'weighted/independent/accept.py'))
    gate=independent['signed_gate'](work/'peer-export',base,invoice,old_app,app,physical)
    require(outer['outer']==gate and gate['BIT_just_below_effective_rejected'] and
            F(certificate['tested'])==F(app['claim'])+7*TICK<cap, 'complete signed application and separate guard replay')
    print('PASS_COMPLETE_SIGNED_APPLICATION',app['claim'],certificate['tested'],gate['strict_count'],gate['functional_count'],flush=True)
    return {'outcome':'PASS_FIXED_CARRIER_CONDITIONAL_GAIN', 'comparison':{'pr':8029,'head':PREDECESSOR},
            'paired_source':{'pr':8027,'head':PAIRED,'archive':base['source_archive'],'files':base['source_count']},
            'price':certificate,'binary':bit,'rational_invoice':invoice,'native_calls':{'BIT':36,'rational':48},
            'caller':physical['caller'],'rational_word':base['rational_word'],'rational_layout':base['rational_layout'],
            'rational_H':str(app['H']),'outer':gate,'premises':app['premises'],
            'rejected_controls':['terminal debit minus one','uniform per-source worst case at infinity',
                                 'one additional paid BIT rank one','one additional paid rational rank one',
                                 'supplied BIT cap equals signed tested point','BIT cap below effective requirement']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,help='write a new deterministic receipt to an unused path')
    args=parser.parse_args()
    require(sys.version_info[:2]==(3,12) and sys.implementation.name=='cpython' and __debug__,
            'CPython 3.12 with assertions is required')
    with TemporaryDirectory(prefix='p104-source-complement-') as temp:
        result=replay(Path(temp))
    sealed=HERE/'RESULT.json'
    if sealed.exists():
        require(read(sealed)==result,'deterministic receipt matches sealed complete replay')
    else:
        require(args.out is not None,'committed replay requires sealed RESULT.json')
    if args.out:
        write(args.out,result)
    print(result['outcome'],result['price']['claim'],result['price']['absolute_gain'],flush=True)


if __name__=='__main__':
    main()

#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Yiyang (@Lyy-iiis), with substantial OpenAI Codex and multi-agent assistance.
"""Read-only, bounded verifier for this exact conditional release's evidence.

This does not rerun the native scalar algebra or establish the inherited analytic
interfaces. It authenticates the executed proof artifacts, checks their exact
bindings and arithmetic, and independently replays the literal finite packing.
No packaged Python is imported or executed; tar members are never extracted.
"""
import argparse
from collections import Counter
import copy
from fractions import Fraction as Q
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import stat
import sys
import tarfile

sys.dont_write_bytecode = True
MANIFEST_PIN = 'ef7b8983700d51fce63869121cb0cad28f930bd0a8901ebfce57b1d714aee0fe'
SOURCE_PIN = 'c8ec4d1b7be08d2ad30730a07392ad9cb6d0222f2c35bef43c9a80a39b16e41f'
DERIVED_PIN = '54dc42f25c1d8b85adcf593c4bf6c0f83f7351388af857812790b8a0b4c3d869'
PLAN_PIN = '163431bf8d3bc0d9b894994b1a3cfa7947367b2243b3c0b3a97d740195a1cb08'
OLD_RECEIPT_PIN = 'a56d2fe28812e93c5526564ef77f7e5e8d1cbb111efeb6c3b0f53c9ec01ca2bc'
PR2848_PIN = 'aceb1394b3e8f3abcc9b1a0dc82756ab937ffbefc2f37305a229a00ccc5137e9'
PR2853_PIN = 'eb3260be191774b931cff6e562978a2af27bbc6ff666ca8c1d387a2b18dc86fa'
WORDS = {'base': '001b14314d8db873d4d80826d4af9c40a3e5a1fecde743e5a26391bdf673f458',
         'extra': 'bc5bfe51178f0c3312d28318412ec490463c896ceed0660b9c443fcb76496546'}
LOCAL = {'1':2394,'2':642,'3':266,'4':128,'5':26,'8':8}
WIDTHS = {4:26,5:2,7:62,8:84,9:234}
PROFILE = {'1':805860,'2':213786,'3':91775,'4':42624,'5':13098,'8':2664,'9':1,'48':13379}
IDLE = {'1':8658,'3':3197,'5':4440,'9':1,'48':13379}
C = Q(1720096628684832600972,10**24)
KAPPA = C-Q(1,10**46)-Q(1,10**70)
GAIN = Q(1438120379902596153,10**24)
E = 'evidence/full/'
AUDIT = E+'candidate/release/verify/strict/global/audit/'
COUNTS = {'admission':119,'bit':12,'controller':25,'independent_owner':8,'geometry':6,
          'modern_outer_rejections':17,'modern_outer_strict_inequalities':63,'supplier_outer_rows':47,
          'shared_kernel_base':8,'shared_kernel_extra':8,'base_native_mutants':46,'extra_native_mutants':46,
          'base_wrapper_mutants':25,'extra_wrapper_mutants':25,'base_warp_mutants':13,'extra_warp_mutants':13}
MAX_FILE = 16*1024*1024
MAX_TOTAL = 128*1024*1024

class Invalid(ValueError): pass

def need(ok, why):
    if not ok: raise Invalid(why)

def sha(b): return hashlib.sha256(b).hexdigest()

def safe_name(name):
    p = PurePosixPath(name)
    need(isinstance(name,str) and name and not p.is_absolute() and '\\' not in name
         and all(x not in ('','.', '..') for x in name.split('/')), 'unsafe relative path')
    return name

def read_file(root, name):
    safe_name(name)
    p=root
    for part in PurePosixPath(name).parts:
        p=p/part
        need(not p.is_symlink(), 'symlink input: '+name)
    s=p.stat()
    need(stat.S_ISREG(s.st_mode) and s.st_size<=MAX_FILE, 'input type/size: '+name)
    with p.open('rb') as f: b=f.read(MAX_FILE+1)
    need(len(b)==s.st_size and len(b)<=MAX_FILE, 'unstable/oversize input: '+name)
    return b

def unzip(b):
    with gzip.GzipFile(fileobj=io.BytesIO(b)) as f: result=f.read(MAX_FILE+1)
    need(len(result)<=MAX_FILE, 'expanded gzip size')
    return result

def unique_object(pairs):
    out={}
    for k,v in pairs:
        need(k not in out,'duplicate JSON key');out[k]=v
    return out

def decode(b):
    return json.loads(b,object_pairs_hook=unique_object,
                      parse_constant=lambda x: (_ for _ in ()).throw(Invalid('nonfinite JSON')))

def rational(x):
    if isinstance(x,dict):x=x['rational']
    need(isinstance(x,(str,int)) and not isinstance(x,bool) and len(str(x))<=10000,'bounded rational')
    return Q(x)

def canonical(x):return sha(json.dumps(x,sort_keys=True,separators=(',',':')).encode())

def load(package):
    root=package.resolve(strict=True)
    need(root.is_dir(),'package directory')
    raw={};docs={}
    def add(name):
        b=read_file(root,name);raw[name]=b
        if name.endswith('.json'):docs[name]=decode(b)
        elif name.endswith('.json.gz'):docs[name]=decode(unzip(b))
    add(E+'MANIFEST.json')
    need(sha(raw[E+'MANIFEST.json'])==MANIFEST_PIN,'frozen evidence manifest SHA256')
    manifest=docs[E+'MANIFEST.json']
    need(len(manifest)==167,'evidence inventory count')
    actual=[];entries=0
    for p in (root/E).rglob('*'):
        entries+=1;need(entries<=512,'bounded evidence directory entries')
        need(not p.is_symlink(),'symlink evidence entry')
        need(p.name!='__pycache__' and p.suffix not in ('.pyc','.pyo'),'stale bytecode evidence')
        if p.is_file():actual.append(p.relative_to(root/E).as_posix())
    need(set(actual)==set(manifest)|{'MANIFEST.json'},'exact evidence inventory')
    for name,digest in manifest.items():
        add(E+safe_name(name));need(sha(raw[E+name])==digest,'evidence file hash: '+name)
    names=['CLAIM.json','FILL.json.gz','ORDER.json','DISPATCH.json','PROFILE.json','PROVIDERS.json',
           'sources/PR2833-PLAN.json.gz','sources/PR2848-CLAIM.json','sources/PR2853-OUTER-CLAIM.json']
    names += ['words/WORD-'+tag+'.json.gz' for tag in WORDS]
    names += ['sources/PR2833-WORD-'+tag+'.json.gz' for tag in WORDS]
    names += ['reproduce.py','build_overlay.py','prepare_shared_native.py','admit_shared_replica.py','shared_kernel.py','review_four_groups.py']
    for name in names:add(name)
    for n in ['lift_parent.py','replica_parent.py','reconstruct_replica.py','blocknorm_certificate.py']:
        add('vendor/pr2839/'+n)
    archive=raw[E+'native/NATIVE-CACHE.tar.gz'];cache={};expanded=0
    with tarfile.open(fileobj=io.BytesIO(archive),mode='r|gz') as t:
        for i,m in enumerate(t):
            need(i<128 and m.isfile() and not m.issym() and not m.islnk(),'native archive member type/count')
            safe_name(m.name);need(m.name not in cache,'native archive duplicate')
            need(0<=m.size<=MAX_FILE,'native archive member size');expanded+=m.size
            need(expanded<=MAX_TOTAL,'native archive expanded size')
            with t.extractfile(m) as f:b=f.read(m.size+1)
            need(len(b)==m.size,'native archive member length');cache[m.name]=sha(b)
            raw['cache/'+m.name]=b
            if m.name.endswith('.json'):docs['cache/'+m.name]=decode(b)
    need(sum(map(len,raw.values()))<=MAX_TOTAL,'bounded total input bytes')
    return raw,docs,cache

def sources(raw,d):
    original=d[E+'source/PR2833-MANIFEST.json'];derived=d[E+'source/DERIVED-MANIFEST.json']
    need(sha(raw[E+'source/PR2833-MANIFEST.json'])==SOURCE_PIN and len(original)==541,'original source inventory')
    need(sha(raw[E+'source/DERIVED-MANIFEST.json'])==DERIVED_PIN and len(derived)==547,'derived source inventory')
    receipt=d[E+'wrapper/source-DERIVATION.json']
    delta={k:{'before_sha256':original.get(k),'after_sha256':derived.get(k)} for k in set(original)|set(derived) if original.get(k)!=derived.get(k)}
    need(len(delta)==11 and delta==receipt['changes'],'exact eleven source changes')
    need(receipt['upstream_manifest_sha256']==SOURCE_PIN and receipt['derived_manifest_sha256']==DERIVED_PIN,'source derivation manifest bindings')
    need(receipt['builder_sha256']==sha(raw['build_overlay.py']),'executed builder binding')
    for tag,wordhash in WORDS.items():
        old='sources/PR2833-WORD-'+tag+'.json.gz';new='words/WORD-'+tag+'.json.gz';wr=receipt['words'][tag]
        need(sha(raw[new])==wordhash==wr['candidate_word_sha256'],'changed word byte binding')
        need(sha(raw[old])==wr['source_word_sha256'],'original word binding')
        need(canonical(d[new])==wr['candidate_canonical_sha256'] and canonical(d[old])==wr['source_canonical_sha256'],'decoded word binding')
        need(wr['groups']==[478,460,462,480] and wr['ledger']['delta']=={'1':12,'2':-8},'four kernel local delta')
        need(d[new]['report']['local_profile']==LOCAL,'literal word local profile')
        need(derived['new/borrow/words/BORROW-WORD-43'+tag+'.json.gz']==wordhash,'derived word source binding')
    for file,shipped in [('reproduce.py','reproduce.py'),('build_overlay.py','build_overlay.py'),('prepare_shared_native.py','prepare_shared_native.py'),('admit_shared_replica.py','admit_shared_replica.py'),('shared_kernel.py','shared_kernel.py'),('shared_kernel_review.py','review_four_groups.py')]:
        need(raw[E+'scripts/'+file]==raw[shipped],'executed script exact copy: '+shipped)
    inputs=d[E+'wrapper/RESULT.json']['input_sha256']
    for k,v in inputs.items():
        suffix=PurePosixPath(k).name
        local=None
        if suffix in ['FILL.json.gz','ORDER.json','DISPATCH.json']:local=suffix
        elif suffix in ['WORD-base.json.gz','WORD-extra.json.gz']:local='words/'+suffix
        elif suffix in ['lift_parent.py','replica_parent.py','reconstruct_replica.py','blocknorm_certificate.py']:local='vendor/pr2839/'+suffix
        elif suffix in ['build_overlay.py','prepare_shared_native.py','admit_shared_replica.py','shared_kernel.py','review_four_groups.py']:local=suffix
        if local:need(sha(raw[local])==v,'wrapper actual input binding: '+local)
    need(sha(unzip(raw['sources/PR2833-PLAN.json.gz']))==PLAN_PIN,'authentic source T37 windows')

def native(raw,d,cache):
    nr=d[E+'native/NATIVE-RECEIPT.json']
    need(cache==nr['cache_files'] and len(cache)==63,'complete native archive tree')
    need(nr['manifest_sha256']==DERIVED_PIN,'native derived source binding')
    need(nr['fresh_current_provider_count']==2 and nr['fresh_retained_native_count']==0 and nr['fresh_retained_parent'] is False
         and nr['reused_retained_native_count']==2 and nr['reused_retained_parent'] is True,'fresh versus reused provenance')
    old=d[E+'reused-retained-input/NATIVE-RECEIPT.json']
    need(sha(raw[E+'reused-retained-input/NATIVE-RECEIPT.json'])==nr['retained_reuse_receipt_sha256']==OLD_RECEIPT_PIN,'retained source receipt')
    fresh=set(WORDS.values())
    for name,value in cache.items():
        if name.split('/')[0] not in fresh:need(old['cache_files'].get(name)==value,'unchanged retained cache member')
    parent=[n for n in cache if n.startswith('_receipts/') and n.endswith('/RECEIPT.json')]
    need(len(parent)==1 and cache[parent[0]]==nr['retained_parent_receipt_sha256'],'retained parent receipt')
    parent_stages=d['cache/'+parent[0].replace('RECEIPT.json','STAGES.json')]
    need(len(parent_stages)==16 and all(x['exit_code']==0 for x in parent_stages),'retained sixteen-stage parent')
    for tag,wordhash in WORDS.items():
        p=nr['providers'][tag];base='cache/'+wordhash+'/'
        need(p['word_sha256']==wordhash,'native current word hash')
        for name,digest in p['complete_native_files'].items():need(cache[wordhash+'/'+name]==digest,'complete current native file binding')
        need(raw[base+'local/FULL-WORD.json.gz']==raw['words/WORD-'+tag+'.json.gz'],'native consumes actual changed word')
        result=d[E+'native/fresh-'+tag+'/RESULT.json'];steps=result['steps']
        need([x['step'] for x in steps]==['native','ledgers','local-replay','wrappers','phases'] and all(x['exit_code']==0 for x in steps),'five fresh native stages')
        need(steps==d[base+'STEPS.json'] and result['word_sha256']==wordhash,'fresh result versus cached stages')
        derived=d[E+'source/DERIVED-MANIFEST.json']
        for name,digest in result['source_sha256'].items():need(derived.get('new/fastnative/vendor/'+name)==digest,'native executed source pin')
        scalar=d[E+'native/'+tag+'/SCALAR-FRAME-AUDIT.json']
        need(scalar['local_profile']==LOCAL and scalar['local_rank_mass']==5182 and scalar['helpers']==408
             and scalar['live_columns_each_orientation']==632 and scalar['zero_buffers']==72,'scalar endpoint and profile bill')
        pid='gauge44' if tag=='base' else 'extra'
        need(d['PROVIDERS.json'][pid]['widths']==scalar['widths'] and Counter(scalar['widths'])==WIDTHS,'ordered native provider widths')
        need(d['PROVIDERS.json'][pid]['actual_paid_profile']==LOCAL,'provider local profile')
        checks=d[E+'native/'+tag+'/LOCAL-CHECKS.json'];ind=d[E+'native/'+tag+'/INDEPENDENT-LOCAL-REPLAY.json']
        for orient in ('forward','backward'):
            c=checks[orient];a=ind['local'][orient]
            need(c['all_columns']==632 and c['paid_profile']==LOCAL and c['zero_buffers_returned_to_zero']==72
                 and c['private_centers_cleared'] is True and c['private_coefficient_stream_cleared_after_each_macro'] is True,'all-column native check')
            need(a['all_exact_columns']==632 and a['private_work_erased'] is True and a['zero_buffers_returned_to_zero']==72
                 and a['warp_columns_each_exact']==512 and ind['paid_profiles'][orient]==LOCAL,'independent native endpoint')
        for name in ['SCALAR-FRAME-AUDIT.json','LOCAL-CHECKS.json','INDEPENDENT-LOCAL-REPLAY.json','WRAPPER-CHECKS.json','WARP-RECIPE-CHECKS.json']:
            need(raw[E+'native/'+tag+'/'+name]==raw[base+'local/'+name],'published native receipt versus archive')

def packing(d):
    plan=d['sources/PR2833-PLAN.json.gz'];order=d['ORDER.json'];dispatch=d['DISPATCH.json'];fill=d['FILL.json.gz']
    need(order==plan['order'] and len(order)==333 and sorted(map(tuple,order))==[(s,r) for s in range(9) for r in range(37)],'authentic complete T37 order')
    need([x[:2] for x in dispatch]==order and Counter(x[2] for x in dispatch)=={'gauge44':125,'extra':208},'complete provider dispatch')
    need(fill['dispatch_overrides']==[] and len(fill['rows'])==135864,'complete literal roles')
    windows={tuple(map(int,k.split(','))):(cap,set(times)) for k,(cap,times) in plan['windows'].items()}
    masks={};helpers=[0]*333;families=[set() for _ in order]
    for row in fill['rows']:
        need(len(row)==6 and all(type(x) is int for x in row),'integer owner role')
        t,h,r,ch,port,off=row
        need(0<=t<333 and 0<=h<408 and 0<=r<37 and (r,ch) in windows and 0<=port<112 and 0<=off<=48,'owner role ranges')
        cap,times=windows[r,ch];need(t in times,'strict authenticated owner window')
        width=d['PROVIDERS.json'][dispatch[t][2]]['widths'][h]
        family=r*896+(2*plan['pairs'][str(ch)]+plan['sides'][str(ch)])*112+port
        need(family not in families[t],'per-call physical family collision');families[t].add(family)
        need(not (helpers[t]>>h)&1,'duplicate helper role');helpers[t]|=1<<h
        key=r,ch,port;bits=((1<<width)-1)<<off
        need(off+width<=cap and not masks.get(key,0)&bits,'owner bin capacity or overlap');masks[key]=masks.get(key,0)|bits
    need(all(h==(1<<408)-1 for h in helpers),'every helper present at every call')
    idle=Counter()
    for (r,ch),(cap,times) in windows.items():
        for port in range(112):
            mask=masks.get((r,ch,port),0);need(not mask&(mask+1),'internal owner hole')
            rem=cap-mask.bit_count()
            if rem:idle[str(rem)]+=1
    need(dict(idle)==IDLE,'literal idle remainder bill')
    profile=Counter(idle)
    for _,_,pid in dispatch:profile.update(d['PROVIDERS.json'][pid]['actual_paid_profile'])
    need(dict(profile)==PROFILE==d['PROFILE.json'],'literal whole profile')
    need(sum(int(r)*n for r,n in profile.items())==2408256,'whole rank mass')
    return {'roles':135864,'calls':333,'live':33152,'physical':33642,'rank_mass':2408256,'idle':IDLE}

def billing(raw,d):
    own=d[AUDIT+'OWNERS-AND-PROFILE.json'];inv=d[AUDIT+'PREFIX-AND-INVOICE.json'];b=inv['blocknorm']
    for key,value in [('live',33152),('physical',33642),('rank_mass',2408256),('hosted_residuals',135864),('banked_residuals',0),('deficit',11840)]:need(own[key]==value,'full owner receipt '+key)
    need(own['paid_profile']==PROFILE and own['all_live_owners_per_call_distinct'] is True,'strict owner profile')
    need(inv['owner_audit_sha256']==sha(raw[AUDIT+'OWNERS-AND-PROFILE.json']) and inv['controller_audit_sha256']==sha(raw[AUDIT+'ASYNC-AUDIT.json']),'invoice owner/controller binding')
    need(inv['live']==33152 and inv['physical']==33642 and inv['helpers']==408 and inv['centres']==8 and inv['private_zero_buffers']==72,'complete physical stock')
    need(sum(inv['physical_stock_identity'].values())==33642,'physical stock identity')
    need(inv['complete_invocation_sweeps']==333 and inv['bridge_sweeps']==333 and inv['global_prefix_bits']==1452 and inv['charged_prefix_bits']==2048,'actual sweep and prefix invoice')
    for key,value in [('replicas',37),('physical_families',33642),('live_families',33152),('active_calls_per_block',9),('bridges_per_block',9),('physical_stock_bits',2643),('stock_l2_bits',1322),('local_actual_prefix_bits',70),('actual_prefix_bits',1452),('required_reserve_bits',1510),('retained_payload_bits',2048)]:need(b[key]==value,'blocknorm '+key)
    need(b['actual_prefix_bits']<=b['required_reserve_bits']<b['retained_payload_bits'],'blocknorm reserve')
    for pid in ('gauge44','extra'):
        need(inv['providers'][pid]['widths']==d['PROVIDERS.json'][pid]['widths'],'invoice ordered widths')
        for orient in ('forward','backward'):
            a=b['endpoint_replay'][pid][orient]
            need(a['all_arbitrary_columns']==632 and a['helper_to_data_response_zero'] is True and a['centres_first_clear_and_terminal_zero']==8 and a['zero_buffers_allocated_and_cleared']==72,'blocknorm all-column hypotheses')
    assembly=d[E+'candidate/release/verify/strict/ASSEMBLY.json']
    rows=assembly['moments'];need(len(rows)==4,'four native moment endpoints')
    for row in rows:
        need(row['accept'] in (True,False),'moment accept flag')
        for engine in ['mercator','base_two']:
            lo,hi=map(rational,row[engine]);need(lo<=hi and (hi<0 if row['accept'] else lo>0),'strict independent moment sign')
    need([rational(x['endpoint']) for x in rows if x['side']=='complex']==[C,C+Q(1,10**24)],'complex endpoint bracket')
    need(rational(rows[0]['endpoint'])==Q(1733427039589844234749,10**24),'actual bit endpoint')

def controls(d):
    registry=d[E+'ACTUAL-CONTROLS.json']['counts'];need(set(registry)==set(COUNTS),'all control families')
    for label,count in COUNTS.items():
        item=registry[label];value=d[E+item['source']]
        for k in item['json_path']:value=value[k]
        need(isinstance(value,(dict,list)) and len(value)==item['count']==count,'actual control array: '+label)
        if isinstance(value,list) and value and isinstance(value[0],str):need(len(set(value))==count,'unique controls: '+label)
    review=d[E+'candidate/release/verify/shared-kernel-independent-review/FOUR-GROUP-INDEPENDENT-REVIEW.json']
    for tag in WORDS:
        v=review['variants'][tag]
        need(v['candidate_sha256']==WORDS[tag] and v['inserted_A_gates']==20 and v['compensation_removed']==28 and v['compensation_added']==28,'kernel review literal scope')
        need(v['all_four_operand_and_target_supports_disjoint'] is True and v['all_other_sections_unchanged'] is True,'kernel structural checks')
        names=[x['name'] for x in v['controls']];need(len(set(names))==8,'unique kernel controls')
        for x in v['controls']:
            need(bool(x['rejected_for']) and x['cleanup_rederived']==(x['name']!='stale_cleanup'),'meaningful semantic kernel controls')
    ledger=d[E+'candidate/outer/LEDGER.json']
    for v in ledger['rows']['struct_boundary_radix_union']['strict_checks'].values():need(rational(v)>0,'strict modern outer inequality')
    for values in ledger['rejecting_controls']['struct_boundary_radix_union'].values():
        need(values and any(rational(v)<=0 for v in values.values()),'modern outer rejection witness')
    for v in d[E+'candidate/release/verify/strict/ASSEMBLY.json']['outer'].values():need(rational(v)>0,'strict supplier outer row')

def claims(raw,d):
    claim=d['CLAIM.json'];wrapper=d[E+'wrapper/RESULT.json'];complete=d[E+'COMPLETE.json'];candidate=d[E+'candidate/RESULT.json']
    need(sha(raw['sources/PR2848-CLAIM.json'])==PR2848_PIN and sha(raw['sources/PR2853-OUTER-CLAIM.json'])==PR2853_PIN,'comparison source pins')
    prior=rational(d['sources/PR2848-CLAIM.json']['kappa']);latest=rational(d['sources/PR2853-OUTER-CLAIM.json']['kappa_rational'])
    need(KAPPA-prior==GAIN and KAPPA-latest>0,'exact improvement over both comparisons')
    for x in [claim,wrapper,complete,candidate]:need(rational(x['kappa'])==KAPPA and rational(x['gain'])==GAIN and rational(x['kappa_decimal'])==KAPPA,'exact headline and gain')
    for x in [claim,wrapper,complete]:
        s=x['secondary_comparison'];need(s['pr']==2853 and s['head']=='d01045dfb67428679618027dff552f1d032fa999' and s['claim_sha256']==PR2853_PIN and rational(s['gain'])==KAPPA-latest,'exact secondary comparison')
    need(claim['replicas']==37 and claim['calls']==333 and claim['helper_roles']==135864 and claim['local_profile']==LOCAL and claim['selected_frontier_changed'] is False,'scoped top-level claim')
    bindings={'native_receipt_sha256':'native/NATIVE-RECEIPT.json','derived_source_manifest_sha256':'source/DERIVED-MANIFEST.json','generated_package_manifest_sha256':'candidate/admitted-package/MANIFEST.json','release_receipt_sha256':'candidate/release/RELEASE-RECEIPT.json','wrapper_sha256':'scripts/reproduce.py'}
    for key,path in bindings.items():
        actual=sha(raw[E+path]);need(claim[key]==wrapper[key]==actual,'claim release chain '+key)
    need(claim['source_manifest_sha256']==SOURCE_PIN and wrapper['source_manifest_sha256']==SOURCE_PIN,'original source identity')
    need(wrapper['candidate_result_sha256']==sha(raw[E+'candidate/RESULT.json']),'wrapper candidate binding')
    need(complete['native_cache_archive_sha256']==sha(raw[E+'native/NATIVE-CACHE.tar.gz']),'published native archive hash')
    manifest=d[E+'candidate/admitted-package/MANIFEST.json']
    need(len(manifest)==551,'admitted generated file count')
    for name in ['FILL.json.gz','ORDER.json','DISPATCH.json']:
        need(sha(raw[name])==manifest['new/borrow-fill/'+name]==candidate[name.split('.')[0].lower()+'_sha256'],'actual owner payload admission binding')
    for tag,h in WORDS.items():need(manifest['new/borrow/words/BORROW-WORD-43'+tag+'.json.gz']==h,'admitted changed provider')
    for name in ['PROFILE.json']:
        need(d[E+'candidate/owners/'+name]==PROFILE and d[E+'candidate/admitted-package/new/'+name]==PROFILE,'admitted full profile')
    outer=d[E+'candidate/outer/OUTER-CLAIM.json'];ledger=d[E+'candidate/outer/LEDGER.json']
    need(rational(outer['kappa_rational'])==rational(outer['kappa'])==KAPPA and rational(outer['gain'])==GAIN,'outer exact headline')
    need(rational(ledger['rows']['struct_boundary_radix_union']['kappa'])==KAPPA and ledger['profile']==PROFILE and ledger['m']==73 and ledger['W']==33152,'modern outer actual profile denominator')
    need(rational(ledger['complex_lower_pinned'])==C and all(rational(x)<1 for x in ledger['native_moment']),'modern outer supplier endpoint')
    release=d[E+'candidate/release/RELEASE-RECEIPT.json'];need(release['manifest_sha256']==sha(raw[E+'candidate/admitted-package/MANIFEST.json']) and rational(release['kappa_decimal'])==KAPPA,'final release exact binding')
    stages=[('wrapper/STAGES.json','stage',['derive-source','fresh-current-native','complete-admission']),('candidate/STAGES.json','name',['owners','parent-lift','rebind','discovery','outer-check_ledger.py','outer-independent_check.py','release'])]
    for path,key,names in stages:
        v=d[E+path];need([x[key] for x in v]==names and all(x['exit_code']==0 for x in v),'successful complete stages '+path)
    v=d[E+'candidate/release/verify/STAGES.json'];need(len(v)==13 and len({x['name'] for x in v})==13 and all(x['exit_code']==0 for x in v),'all thirteen supplier release stages')
    need(any(x['name']=='shared-kernel-independent-review' for x in v) and any(x['name']=='geometry-controls' for x in v),'mandatory new proof and geometry stages')
    for label,item in d[E+'ACTUAL-CONTROLS.json']['counts'].items():need(item['source_sha256']==sha(raw[E+item['source']]),'control source binding '+label)
    ceiling=d[E+'CEILING-REALIZED.json'];need(rational(ceiling['fraction_of_local_profile_ceiling_lower'])==KAPPA/rational(ceiling['local_profile_ceiling_upper']),'exact ceiling realization')


def corruption_controls(raw,d,cache):
    results=[]
    def trial(name,fn,mutation,target,expected):
        changed=copy.deepcopy(target);mutation(changed)
        need(changed!=target,'nonvacuous evidence mutation '+name)
        try:fn(changed)
        except Invalid as ex:
            need(expected in str(ex),'wrong rejection reason '+name+': '+str(ex))
            results.append({'name':name,'rejected_for':str(ex)})
        else:raise Invalid('accepted corruption '+name)
    def change(key,field,value):return lambda z:z[key].__setitem__(field,value)
    trial('inflated_headline',lambda z:claims(raw,z),change('CLAIM.json','kappa',str(KAPPA+Q(1,10**9))),d,'exact headline')
    trial('false_secondary_gain',lambda z:claims(raw,z),lambda z:z['CLAIM.json']['secondary_comparison'].__setitem__('gain','0'),d,'secondary comparison')
    trial('source_manifest_substitution',lambda z:sources(raw,z),lambda z:z[E+'source/DERIVED-MANIFEST.json'].__setitem__('verify.py','0'*64),d,'eleven source changes')
    trial('missing_native_stage',lambda z:native(raw,z,cache),lambda z:z[E+'native/fresh-base/RESULT.json']['steps'].pop(),d,'five fresh native stages')
    trial('native_profile_undercharge',lambda z:native(raw,z,cache),lambda z:z[E+'native/base/SCALAR-FRAME-AUDIT.json']['local_profile'].__setitem__('1',2393),d,'scalar endpoint')
    trial('missing_native_cache_member',lambda z:native(raw,d,z),lambda z:z.pop(next(iter(z))),cache,'complete native archive')
    trial('stale_controller_count_15',controls,lambda z:z[AUDIT+'ASYNC-AUDIT.json']['mutations_rejected'].__delitem__(slice(15,None)),d,'actual control array: controller')
    trial('missing_shared_kernel_control',controls,lambda z:z[E+'candidate/release/verify/shared-kernel-independent-review/FOUR-GROUP-INDEPENDENT-REVIEW.json']['variants']['extra']['controls'].pop(),d,'actual control array: shared_kernel_extra')
    trial('non_strict_outer_margin',controls,lambda z:next(iter(z[E+'candidate/outer/LEDGER.json']['rows']['struct_boundary_radix_union']['strict_checks'].values())).__setitem__('rational','0'),d,'strict modern outer inequality')
    trial('omitted_private_buffers',lambda z:billing(raw,z),change(AUDIT+'PREFIX-AND-INVOICE.json','private_zero_buffers',0),d,'complete physical stock')
    trial('undercharged_geometry_sweep',lambda z:billing(raw,z),change(AUDIT+'PREFIX-AND-INVOICE.json','bridge_sweeps',332),d,'sweep and prefix invoice')
    trial('wrong_live_denominator',lambda z:claims(raw,z),change(E+'candidate/outer/LEDGER.json','W',33151),d,'actual profile denominator')
    trial('missing_owner_role',packing,lambda z:z['FILL.json.gz']['rows'].pop(),d,'complete literal roles')
    trial('overlapping_owner_role',packing,lambda z:z['FILL.json.gz']['rows'].__setitem__(1,list(z['FILL.json.gz']['rows'][0])),d,'physical family collision')
    trial('free_idle_remainder',packing,lambda z:z['PROFILE.json'].__setitem__('9',0),d,'literal whole profile')
    trial('changed_shipped_word',lambda z:sources(z,d),lambda z:z.__setitem__('words/WORD-base.json.gz',z['words/WORD-base.json.gz']+b'x'),raw,'changed word byte binding')
    for name in ['../escape','/absolute','a/../escape','a\\escape']:
        try:safe_name(name)
        except Invalid:results.append({'name':'unsafe_path_'+name,'rejected_for':'unsafe relative path'})
        else:raise Invalid('accepted unsafe path')
    return results

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--package',type=Path,required=True);ap.add_argument('--out',type=Path);ap.add_argument('--controls',action='store_true');a=ap.parse_args()
    root=a.package.resolve(strict=True)
    if a.out:
        out=a.out.absolute();need(not out.exists() and not out.is_symlink(),'fresh external output required')
        need(not out.resolve().is_relative_to(root),'output must be outside inspected package')
    raw,d,cache=load(root)
    sources(raw,d);native(raw,d,cache);owner=packing(d);billing(raw,d);controls(d);claims(raw,d)
    tests=corruption_controls(raw,d,cache) if a.controls else []
    receipt={'status':'PASS_BOUNDED_READ_ONLY_RELEASE_EVIDENCE','checker_sha256':sha(Path(__file__).read_bytes()),'evidence_manifest_sha256':MANIFEST_PIN,
             'package_claim_sha256':sha(raw['CLAIM.json']),'evidence_files':167,'native_archive_members':len(cache),'literal_owner':owner,
             'kappa':str(KAPPA),'gain_over_pr2848':str(GAIN),'secondary_comparison_claim_sha256':PR2853_PIN,'actual_controls':COUNTS,
             'fresh_current_native_chains':2,'reused_retained_native_chains':2,'reused_retained_parent_stages':16,
             'corruption_controls':tests,'scope':'Authenticates the executed full-release evidence and replays the literal finite owner bill; does not rerun the native scalar or outer engines. Two current chains were fresh in the recorded release; two unchanged retained chains and parent were reused. Inherited all-size/compiler/hosting/precision/tape/analytic obligations remain; no new Lean proof.'}
    # Re-read every consumed file to detect accidental changes; no package writes.
    for name,b in raw.items():
        if not name.startswith('cache/'):need(read_file(root,name)==b,'input changed during read-only verification')
    output=json.dumps(receipt,sort_keys=True,indent=2)+'\n'
    if a.out:
        with a.out.open('x',encoding='utf-8') as f:f.write(output)
    print(output,end='')
if __name__=='__main__':
    try:main()
    except (Invalid,KeyError,TypeError,ValueError,OSError) as exc:
        raise SystemExit('REJECT_RELEASE_EVIDENCE: '+str(exc))

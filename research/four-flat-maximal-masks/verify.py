#!/usr/bin/env python3
"""Exact controls and serial same-input differential benchmark. Stdlib only."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import os
import platform
import random
import re
import runpy
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent
build = runpy.run_path(str(ROOT / 'build.py'))
need, source, compile_c = (build[k] for k in ['need', 'source', 'compile_c'])
REPO = ROOT.parent.parent
PARENT = REPO / 'research/two-flat-cover-branching'
ENV_KEYS = ['FREES','NOSYM','ONLY','JMOD','JREM','NEWLO','PASS1','PAIRS','EXITCRACK','EXPORT_ONLY','EXPORT','PAIRLOG','DBG','TRACE','MASK_SETUP']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def run(exe, request):
    return subprocess.run([str(exe)], input=request, text=True, capture_output=True, timeout=180)


def controls(work):
    rng = random.Random(94)
    cases = [[i for i in range(16) if (family >> i) & 1] for family in range(1 << 16)]
    # Exercise all 128 positions, including cardinalities 0 and 128, and
    # incomparable equal-cardinality masks with nontrivial low/high words.
    for bit in range(128):
        cases.append(sorted({0, 1 << bit, (1 << 128)-1, ((1 << 128)-1) ^ (1 << bit)}))
    for _ in range(2000):
        base = rng.getrandbits(128)
        family = {rng.getrandbits(128) for _ in range(rng.randrange(1, 40))}
        family.update([0,base,base & rng.getrandbits(128),base | rng.getrandbits(128)])
        cases.append(sorted(family))
    request = ''.join(str(len(c))+'\n'+''.join(f'{x>>64:x} {x&((1<<64)-1):x}\n' for x in c) for c in cases)
    # Independent explicit sets, rather than C bit-mask containment or buckets.
    oracle=[]
    for c in cases:
        sets=[frozenset(i for i in range(128) if (v>>i)&1) for v in c]
        maxima=[v for j,v in enumerate(c) if not any(sets[j] < other for other in sets)]
        oracle.append(str(len(maxima))+''.join(f' {x:032x}' for x in maxima))
    expected='\n'.join(oracle)+'\n'
    for name,fast in [('reference',False),('accelerated',True)]:
        exe=compile_c(source(fast,kernel=True),work/name)
        p=run(exe,request)
        need(p.returncode==0 and p.stdout==expected,name+' differs from explicit-set oracle')
    fast_text=source(True,kernel=True)
    sanitized=compile_c(fast_text,work/'sanitized',('-fsanitize=undefined,bounds','-fsanitize-undefined-trap-on-error'))
    p=run(sanitized,request)
    need(p.returncode==0 and p.stdout==expected,'sanitized oracle comparison failed')
    mutations={
        'reverse_bucket_order': ('int weight = 128; weight >= 0; weight--','int weight = 0; weight <= 128; weight++'),
        'skip_larger_masks': ('int larger = kept;', 'int larger = 0;'),
        'reverse_containment': ('(mask & output[k]) == mask','(mask & output[k]) == output[k]'),
        'discard_high_word': ('(mask & output[k]) == mask','((u64)mask & (u64)output[k]) == (u64)mask'),
        'drop_last_maximum': ('return kept;','return kept ? kept-1 : 0;'),
        'omit_canonical_order': ('qsort(output, (size_t)kept, sizeof(u128), cmp128);','/* deliberately omit sort */'),
    }
    for name,(old,new) in mutations.items():
        need(old in fast_text,'missing mutant anchor')
        exe=compile_c(fast_text.replace(old,new),work/name)
        p=run(exe,request)
        need(p.returncode!=0 or p.stdout!=expected,'undetected mutant: '+name)
    for malformed in ['2\n0 1\n0 1\n','2\n0 2\n0 1\n','1\n0\n','-1\n','44001\n','no\n']:
        need(run(work/'accelerated',malformed).returncode!=0,'malformed kernel input accepted')
    try:
        build['once']('absent','required','replacement')
    except ValueError:
        pass
    else:
        raise ValueError('missing adapter anchor accepted')
    try:
        build['once']('twice twice','twice','replacement')
    except ValueError:
        pass
    else:
        raise ValueError('ambiguous adapter anchor accepted')
    # Authenticate the same declared inputs in a clean export, then alter one.
    export=work/'source-control';(export/'research').mkdir(parents=True)
    package=export/'research'/ROOT.name;shutil.copytree(ROOT,package,ignore=shutil.ignore_patterns('__pycache__'))
    for item in build['authenticate']()['inputs']:
        dst=export/item['path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(REPO/item['path'],dst)
    code='import runpy;runpy.run_path('+repr(str(package/'build.py'))+')["authenticate"]()'
    def authenticate_export():
        return subprocess.run([sys.executable,'-I','-B','-c',code],text=True,capture_output=True)
    need(authenticate_export().returncode==0,'clean source export rejected')
    target=export/'research/two-flat-cover-branching/vendor/s4z.c'
    target.write_bytes(target.read_bytes()+b'\n/* mutation */\n')
    p=authenticate_export();need(p.returncode!=0 and 'source mismatch' in p.stderr,'modified source accepted')
    good=[94,1,0,3,1,2,1,2]
    encode=lambda words:b''.join(x.to_bytes(16,'little') for x in words)
    need(inspect_setup(encode(good),94,1,2)=={'active_directions':1,'maximal_masks':2},'setup oracle failed')
    bad=[good[:-1],good+[0],good[:4]+[2]+good[5:],good[:-1]+[4],good[:-2]+[2,1],good[:1]+[0]+good[2:]]
    for words in bad:
        try:inspect_setup(encode(words),94,1,2)
        except ValueError:pass
        else:raise ValueError('malformed setup export accepted')
    return {'status':'PASS_MAXIMAL_MASK_CONTROLS','explicit_set_cases':len(cases),'all_four_point_families':65536,
            'seeded_wide_families':2000,'all_bit_position_cases':128,'oracle_sha256':sha(expected.encode()),
            'implementation_mutants':list(mutations),'invalid_inputs_rejected':6,'adapter_anchor_controls':2,'source_byte_control':'PASS','setup_export_controls':6}


def clean_env(**updates):
    env={k:v for k,v in os.environ.items() if k not in ENV_KEYS}
    env.update(updates)
    return env


def invoke(exe,work,args,env):
    start=time.perf_counter()
    p=subprocess.run([str(exe),*args],cwd=work,env=env,text=True,capture_output=True,timeout=300)
    elapsed=time.perf_counter()-start
    need(p.returncode==0,'engine failed: '+p.stderr[-3000:])
    return p,elapsed



def inspect_setup(data, expected_rep, expected_calls=None, expected_masks=None):
    need(len(data)%16==0,'partial setup word')
    pos=0
    def word():
        nonlocal pos
        need(pos+16<=len(data),'truncated setup')
        value=int.from_bytes(data[pos:pos+16],'little');pos+=16
        return value
    need(word()==expected_rep,'setup representative differs')
    count=word();total=0;previous_direction=-1
    need(0<=count<=18100,'invalid active count')
    for _ in range(count):
        direction,residual,cap,n=(word() for _ in range(4))
        need(previous_direction<direction<18100,'direction order/domain')
        previous_direction=direction
        need(residual.bit_length()<=112 and 0<n<=43435,'mask domain/count')
        previous=-1;maximum_weight=0
        for _ in range(n):
            mask=word()
            need(previous<mask and mask & residual==mask,'mask order/residual containment')
            previous=mask;maximum_weight=max(maximum_weight,mask.bit_count())
        need(cap==maximum_weight,'cap differs from complete list')
        total+=n
    need(pos==len(data),'trailing setup records')
    if expected_calls is not None:need(count==expected_calls,'missing active setup records')
    if expected_masks is not None:need(total==expected_masks,'missing maximal masks')
    return {'active_directions':count,'maximal_masks':total}


def full(work):
    raw=gzip.decompress((PARENT/'data/data88.txt.gz').read_bytes())
    (work/'data88.txt').write_bytes(raw)
    (work/'gens.txt').write_bytes((PARENT/'vendor/gens.txt').read_bytes())
    (work/'pairs.txt').write_bytes((PARENT/'data/pairs.txt').read_bytes())
    reports={};outputs={};setups={};requirements={};timing_pattern=r'MASK_TIMING rep (\d+) calls (\d+) inputs (\d+) outputs (\d+) filter ([\d.]+) setup ([\d.]+)'
    for name,fast in [('reference',False),('accelerated',True)]:
        exe=compile_c(source(fast),work/name)
        env=clean_env(ONLY='46,94',PAIRS=str(work/'pairs.txt'),PAIRLOG='1',EXPORT=str(work/name)+'-requirements',MASK_SETUP=str(work/name)+'-setup')
        p,elapsed=invoke(exe,work,['data88.txt','4','6','4','5','88','8','1','0'],env)
        (work/(name+'.stdout')).write_text(p.stdout);(work/(name+'.stderr')).write_text(p.stderr)
        need('pairs 12 surviving 11 leaves 5509 overflow 0 max span 2' in p.stdout,'incomplete full sample')
        outputs[name]=p.stdout
        requirements[name]={f.name.split('-requirements-')[1]:f.read_bytes() for f in work.glob(name+'-requirements-*.json')}
        setups[name]={f.name.split('-setup-')[1]:f.read_bytes() for f in work.glob(name+'-setup-*.bin')}
        rows=re.findall(timing_pattern,p.stderr)
        need([int(r[0]) for r in rows]==[46,94],'missing representative timing')
        reports[name]={'wall_seconds':elapsed,'representatives':[dict(rep=int(r[0]),calls=int(r[1]),input_masks=int(r[2]),maximal_masks=int(r[3]),filter_cpu_seconds=float(r[4]),setup_cpu_seconds=float(r[5])) for r in rows]}
    need(outputs['reference']==outputs['accelerated'],'full stdout differs')
    need(len(requirements['reference'])==11 and requirements['reference']==requirements['accelerated'],'all requirement records must agree')
    need(set(setups['reference'])=={'46.bin','94.bin'} and setups['reference']==setups['accelerated'],'complete setup state differs')
    setup_coverage={}
    for a,b in zip(reports['reference']['representatives'],reports['accelerated']['representatives']):
        need({k:v for k,v in a.items() if not k.endswith('seconds')}=={k:v for k,v in b.items() if not k.endswith('seconds')},'filter coverage differs')
        key=str(a['rep'])+'.bin'
        setup_coverage[key]=inspect_setup(setups['accelerated'][key],a['rep'],a['calls'],a['maximal_masks'])
    # The whole known positive wrapper reaches its exact span-five witness.
    (work/'positive-pair.txt').write_text('82 103676\n')
    positive=[]
    for name in ['reference','accelerated']:
        env=clean_env(ONLY='82',PAIRS=str(work/'positive-pair.txt'),EXITCRACK='1',MASK_SETUP=str(work/name)+'-positive')
        p,_=invoke(work/name,work,['data88.txt','6','6','4','0','88','5','1','0'],env)
        (work/(name+'-positive.stdout')).write_text(p.stdout)
        need('CRACK? target 5 span 5 rep 82 V2idx 103676' in p.stdout,'positive witness lost')
        positive.append(p.stdout)
    need(positive[0]==positive[1],'positive witness differs')
    need((work/'reference-positive-82.bin').read_bytes()==(work/'accelerated-positive-82.bin').read_bytes(),'positive setup differs')
    inspect_setup((work/'accelerated-positive-82.bin').read_bytes(),82)
    def total(name,key):return sum(r[key] for r in reports[name]['representatives'])
    return {'status':'PASS_MAXIMAL_MASK_FULL','benchmark':reports,
            'filter_speedup':total('reference','filter_cpu_seconds')/total('accelerated','filter_cpu_seconds'),
            'setup_speedup':total('reference','setup_cpu_seconds')/total('accelerated','setup_cpu_seconds'),
            'wall_speedup':reports['reference']['wall_seconds']/reports['accelerated']['wall_seconds'],
            'setup_state':{k:{'bytes':len(v),'sha256':sha(v),**setup_coverage[k]} for k,v in setups['accelerated'].items()},
            'requirements':{k:sha(v) for k,v in requirements['accelerated'].items()},
            'full_stdout_sha256':sha(outputs['accelerated'].encode()),'positive_stdout_sha256':sha(positive[0].encode()),
            'positive_setup_sha256':sha((work/'accelerated-positive-82.bin').read_bytes()),
            'pairs':12,'closure_leaves':5509,'positive_span_five':'PASS',
            'generated_c_sha256':{name:sha((work/(name+'.c')).read_bytes()) for name in ['reference','accelerated']}}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path);ap.add_argument('--controls-only',action='store_true');ap.add_argument('--full-only',action='store_true');args=ap.parse_args()
    need(not(args.controls_only and args.full_only),'conflicting modes');build['authenticate']()
    temporary=None
    if args.work:
        need(not args.work.exists(),'work directory must be fresh');args.work.mkdir(parents=True);work=args.work.resolve()
    else:
        temporary=tempfile.TemporaryDirectory(prefix='four-flat-masks-');work=Path(temporary.name)
    result={'python':sys.version,'platform':platform.platform(),'compiler':subprocess.check_output(['cc','--version'],text=True).splitlines()[0]}
    if not args.full_only:result['controls']=controls(work)
    if not args.controls_only:result['full']=full(work)
    (work/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
    if not args.full_only:print('PASS_MAXIMAL_MASK_CONTROLS')
    if not args.controls_only:print('PASS_MAXIMAL_MASK_FULL')
    if temporary:temporary.cleanup()

if __name__=='__main__':main()

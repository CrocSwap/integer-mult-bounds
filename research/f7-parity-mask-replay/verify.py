#!/usr/bin/env python3
"""Reproduce the complete same-domain census benchmark and failure controls.

Requires Python 3.12+ and cc with C11 and unsigned __int128 support.
Tekalign, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import hashlib
import json
import math
import platform
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = ROOT / 'research/f7-weight-parity-census-correction'
FLAGS = ['-O3', '-std=c11', '-Wall', '-Wextra', '-Werror']
CASES = [(20, 10, 8), (18, 9, 9), (20, 10, 7),
         (20, 9, 9), (20, 10, 9), (20, 10, 10)]
FIELDS = ['nodes', 'candidate_restored_leaves', 'all_restored_leaves', 'hits',
          'even_budget_prunes', 'odd_budget_prunes', 'aborted', 'complete']


def require(ok, detail):
    if not ok:
        raise RuntimeError(detail)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_text())


def pinned_sources():
    manifest = read(HERE / 'SOURCES.json')
    entries = [e for e in manifest['files'] if e['usage'] == 'input']
    require(len(entries) == 6, 'unexpected input inventory')
    for entry in entries:
        require(sha((ROOT / entry['path']).read_bytes()) == entry['sha256'], entry['path'])
    return (PARENT / 'engine/corrected_census.c').read_text()


def compile_c(source, target, n=7, length=20, extra=()):
    command = ['cc', *FLAGS, f'-DN={n}', f'-DL={length}', *extra,
               str(source), '-o', str(target)]
    subprocess.run(command, check=True, timeout=60, capture_output=True)
    return target


def census(binary, split, directory, extra=(), expected_exit=0):
    directory.mkdir()
    command = [str(binary), ','.join(map(str, split)), '--hits', str(directory/'hits'),
               '--json', str(directory/'result.json'), *map(str, extra)]
    started = time.perf_counter()
    p = subprocess.run(command, capture_output=True, text=True, timeout=480)
    elapsed = time.perf_counter() - started
    require(p.returncode == expected_exit, (command, p.returncode, p.stdout, p.stderr))
    data = read(directory/'result.json')
    return data, (directory/'hits').read_bytes(), elapsed


def exact(data):
    result = json.loads(json.dumps(data))
    for key in ('shards', 'total'):
        for record in result[key]:
            value = record.pop('seconds')
            require(isinstance(value, (int, float)) and math.isfinite(value) and value >= 0,
                    'invalid timing field')
    return result


def instrument(source):
    anchor = 'static void rec(int i) {'
    require(source.count(anchor) == 1, 'state-oracle anchor')
    return source.replace(anchor, (HERE/'state_oracle.c').read_text()+'\n'+anchor+'\n    check_state();')


def run_parent_check(name, source, out):
    # Execute authenticated source directly, avoiding any predecessor .pyc cache.
    loader = ("import sys; from pathlib import Path; "
              "p=Path(sys.argv.pop(1)); sys.path.insert(0,str(p.parent)); "
              "exec(compile(p.read_bytes(),str(p),'exec'),{'__name__':'__main__','__file__':str(p)})")
    command = [sys.executable, '-I', '-B', '-X', 'pycache_prefix='+str(out/'pycache'),
               '-c', loader, str(PARENT/'validation'/name),
               '--engine-source', str(source), '--output-dir', str(out)]
    subprocess.run(command, check=True, timeout=180)


def kernel_test(work):
    # All 448 basis/label pairs prove this finite linear permutation kernel;
    # composite masks additionally detect accidental nonlinear changes.
    harness = r'''
#define main census_entry
#include "fast.c"
#undef main
int main(void) {
    for(unsigned j=0;j<7;j++) {
        for(unsigned k=0;k<64;k++) {
            unsigned target=k^((1u<<j)>>1);
            if(step_translate(UINT64_C(1)<<k,j)!=(UINT64_C(1)<<target)) return 4;
        }
        uint64_t x=UINT64_C(0x123456789abcdef0), y=0;
        for(unsigned k=0;k<64;k++) if((x>>k)&1) y|=UINT64_C(1)<<(k^((1u<<j)>>1));
        if(step_translate(x,j)!=y || step_translate(step_translate(x,j),j)!=x) return 5;
    }
    return 0;
}
'''
    path = work/'kernel.c'
    path.write_text(harness)
    binary = compile_c(path, work/'kernel', extra=['-fsanitize=undefined,bounds',
                       '-fsanitize-undefined-trap-on-error'])
    subprocess.run([str(binary)], check=True, timeout=20)
    return 448


def controls(baseline, fast, work, adapter):
    (work/'fast.c').write_text(fast)
    state_source = work/'state.c'
    state_source.write_text(instrument(fast))
    run_parent_check('check_corrected_c.py', state_source, work/'small')
    run_parent_check('crosscheck_n7.py', state_source, work/'capped')
    checks = {'raw_product_comparisons': 164, 'inherited_failure_controls': 12,
              'independent_capped_comparisons': 36,
              'permutation_basis_cases': kernel_test(work)}
    base_source = work/'base.c'
    base_source.write_text(baseline)
    base = compile_c(base_source, work/'small-base', n=4, length=8)
    replacement = compile_c(state_source, work/'small-fast', n=4, length=8,
                            extra=['-fsanitize=undefined,bounds', '-fsanitize-undefined-trap-on-error'])
    comparisons = []
    for i, (split, args, exitcode) in enumerate([
        ((4,4), [], 0), ((4,4), ['--no-budgets'], 0),
        ((4,4), ['--no-even-budget'], 0), ((4,4), ['--no-odd-budget'], 0),
        ((4,4), ['00','01'], 0), ((4,4), ['00','01:10'], 2),
        ((4,4), ['--cap','1'], 2), ((3,3), [], 0)]):
        a,ah,_ = census(base, split, work/f'control-{i}-base', args, exitcode)
        b,bh,_ = census(replacement, split, work/f'control-{i}-fast', args, exitcode)
        require(exact(a) == exact(b) and ah == bh, ('small differential', i))
        comparisons.append({'case': i, 'exact': exact(b), 'ordered_hits_sha256': sha(bh)})
    # Original unsound-prune counterexample must appear among the actual hits.
    require(b'01021323\n' in (work/'control-0-fast/hits').read_bytes(), 'lost known universal word')
    checks['full_json_and_ordered_hit_comparisons'] = comparisons
    # Exercise reset/return and every label width, including the N=1 boundary.
    extra_cases = [(1,2,(1,1),[]), (1,20,(1,1),[]), (2,4,(2,2),[]),
                   (2,8,(2,2),['--no-budgets']), (3,10,(4,4),[]),
                   (5,10,(5,5),[]), (6,12,(6,6),[]), (7,20,(10,7),[])]
    extra_results=[]
    for i,(n,length,split,args) in enumerate(extra_cases):
        b0=compile_c(base_source,work/f'edge-base-{i}',n=n,length=length)
        b1=compile_c(state_source,work/f'edge-fast-{i}',n=n,length=length,
                     extra=['-fsanitize=undefined,bounds','-fsanitize-undefined-trap-on-error'])
        a,ah,_=census(b0,split,work/f'edge-base-run-{i}',args)
        b,bh,_=census(b1,split,work/f'edge-fast-run-{i}',args)
        require(exact(a)==exact(b) and ah==bh,('edge differential',n,length))
        extra_results.append({'n':n,'length':length,'split':split,'exact':exact(b),
                              'ordered_hits_sha256':sha(bh)})
    checks['all_dimension_state_and_sanitizer_checks']=extra_results
    mutants = [
        ('wrong_step', 'unsigned shift=1u<<(label-1);', 'unsigned shift=1u<<label;'),
        ('lost_return', 'epoints=old_epoints; opoints=old_opoints;',
         'epoints=old_epoints; opoints=old_opoints^1;'),
        ('wrong_new_point', 'opoints|=1;', 'opoints|=2;'),
        ('merged_cosets', 'pop(ee|oo|1)+pop(eo)', 'pop(ee|oo|eo|1)'),
    ]
    rejected = []
    for name, old, new in mutants:
        require(fast.count(old) == 1, ('mutant anchor', name))
        path = work/(name+'.c')
        changed = fast.replace(old, new)
        path.write_text(instrument(changed) if name != 'merged_cosets' else changed)
        binary = compile_c(path, work/name, n=4, length=8)
        directory = work/(name+'-out'); directory.mkdir()
        p = subprocess.run([str(binary),'4,4','--hits',str(directory/'hits'),
                            '--json',str(directory/'result.json')], capture_output=True, timeout=20)
        if name == 'merged_cosets':
            require(p.returncode == 0, (name,p.stderr))
            require((directory/'hits').read_bytes() != (work/'control-0-base/hits').read_bytes(), name)
        else:
            require(p.returncode == 3 and b'STATE_ORACLE_MISMATCH' in p.stderr, (name,p.returncode,p.stderr))
        rejected.append(name)
    bad = work/'corrupt.c'; bad.write_text(baseline+'\n')
    try:
        adapter['authenticate'](bad, sha(baseline.encode()))
    except ValueError:
        rejected.append('corrupt_source_pin')
    else:
        raise RuntimeError('corrupt source accepted')
    try:
        adapter['rewrite'](baseline.replace('mask_t add_same=0,add_cross=0;', '/* absent anchor */'))
    except ValueError:
        rejected.append('missing_adapter_anchor')
    else:
        raise RuntimeError('unknown source shape accepted')
    checks['new_rejecting_controls'] = rejected
    return checks


def benchmark(baseline, fast, work):
    expected = {r['case']: r for r in read(PARENT/'engine/SUMMARIES.json')['results']}
    require(len(expected) == 6, 'expected census inventory')
    sources = {'base': work/'baseline.c', 'fast': work/'accelerated.c'}
    sources['base'].write_text(baseline); sources['fast'].write_text(fast)
    binaries = {(mode,length): compile_c(path, work/f'{mode}-{length}', length=length)
                for mode,path in sources.items() for length in (18,20)}
    records = []
    for i, (length,s,t) in enumerate(CASES):
        key = f'n7_l{length}_{s}_{t}'
        results = {}
        # Alternate order; every run is from the empty prefix, without a cap.
        for mode in (('base','fast') if i%2==0 else ('fast','base')):
            data,hits,wall = census(binaries[mode,length], (s,t), work/f'{key}-{mode}')
            require(data['complete'] and not data['aborted'] and hits == b'', (key,mode))
            require(data['requested_shards']==data['completed_or_partial_shards']==1 and
                    data['shards'][0]['prefix']=='', (key, 'incomplete domain'))
            require(all(data['total'][0][f]==expected[key][f] for f in FIELDS), (key,mode,'count mismatch'))
            results[mode] = {'exact': exact(data), 'search_seconds': data['total'][0]['seconds'],
                             'wall_seconds': wall, 'ordered_hits_sha256': sha(hits)}
            print(key,mode,'nodes='+str(data['total'][0]['nodes']),f'wall={wall:.3f}s',flush=True)
        require(results['base']['exact']==results['fast']['exact'], key+' full JSON mismatch')
        records.append({'case':key,**results,'speedup':results['base']['wall_seconds']/results['fast']['wall_seconds']})
    a=sum(r['base']['wall_seconds'] for r in records)
    b=sum(r['fast']['wall_seconds'] for r in records)
    return {'cases':records,'baseline_wall_seconds':a,'accelerated_wall_seconds':b,
            'aggregate_speedup':a/b, 'total_nodes':sum(r['base']['exact']['total'][0]['nodes'] for r in records)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group()
    group.add_argument('--controls-only',action='store_true')
    group.add_argument('--benchmark-only',action='store_true')
    parser.add_argument('--work',type=Path)
    args=parser.parse_args()
    temporary=None
    if args.work:
        work=args.work.resolve(); work.mkdir(parents=True,exist_ok=False)
    else:
        temporary=tempfile.TemporaryDirectory(prefix='f7-mask-replay-'); work=Path(temporary.name)
    baseline=pinned_sources()
    adapter=runpy.run_path(str(HERE/'accelerate.py'))
    fast=adapter['rewrite'](baseline)
    result={'schema':1,'baseline_sha256':sha(baseline.encode()),'accelerated_sha256':sha(fast.encode()),
            'implementation_sha256':{name:sha((HERE/name).read_bytes())
                                     for name in ['accelerate.py','verify.py','state_oracle.c']},
            'python':sys.version,'platform':platform.platform(),'flags':FLAGS,
            'compiler':subprocess.check_output(['cc','--version'],text=True).splitlines()[0],
            'scope':'tooling; unchanged corrected L18/L20 census; no new kappa'}
    if not args.benchmark_only:
        result['controls']=controls(baseline,fast,work,adapter)
        print('PASS_F7_PARITY_MASK_CONTROLS',flush=True)
    if not args.controls_only:
        result['benchmark']=benchmark(baseline,fast,work)
        print('PASS_F7_PARITY_MASK_COMPLETE six_cases exact_traversal_and_ordered_hits',flush=True)
    (work/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print('receipt',work/'RESULT.json',flush=True)
    if temporary:
        print(json.dumps(result,sort_keys=True))
        temporary.cleanup()


if __name__=='__main__':
    main()

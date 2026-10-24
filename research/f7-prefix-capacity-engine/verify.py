#!/usr/bin/env python3
"""Check the actual census successor and its simple-path caller. Apache-2.0.

JoyboyBrian, with substantial OpenAI Codex assistance. The capacity theorem
is Ali Romman's PR5001 result, not a new theorem proved by this verifier.
"""
from collections import Counter
from pathlib import Path
import difflib
import hashlib
import json
import os
import platform
import runpy
import statistics
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DOMAINS = ((2, 4), (3, 6), (4, 8), (4, 10), (5, 12))


def require(value, message):
    if not value:
        raise ValueError(message)


def command(argv, **kwargs):
    result = subprocess.run(list(map(str, argv)), capture_output=True,
                            text=True, timeout=8, **kwargs)
    require(result.returncode == 0, f'command failed: {argv}: {result.stderr}')
    return result


def compile_c(source, output, n=None, length=None):
    definitions = [] if n is None else [f'-DN={n}', f'-DL={length}']
    command([os.environ.get('CC', 'cc'), '-O2', '-Wall', '-Wextra', '-Werror',
             '-std=c11', *definitions, source, '-o', output])


def leaf_instrument(source):
    marker = '        run.candidate_leaves++;'
    require(source.count(marker) == 1, 'census leaf boundary changed')
    return source.replace(marker, marker + '\n        fputs("LEAF ",stdout);\n'
                          '        for(int k=0;k<L;k++) fputc(\'0\'+word[k],stdout);\n'
                          '        fputc(\'\\n\',stdout);')


def run_census(binary, scratch, split, flags=()):
    hits, receipt = scratch/'hits.txt', scratch/'run.json'
    hits.unlink(missing_ok=True)
    receipt.unlink(missing_ok=True)
    result = command([binary, f'{split[0]},{split[1]}', '--hits', hits,
                      '--json', receipt, *flags])
    data = json.loads(receipt.read_text())
    require(data['complete'] and not data['aborted'], 'incomplete search')
    leaves = Counter(line[5:] for line in result.stdout.splitlines()
                     if line.startswith('LEAF '))
    return data, leaves, Counter(hits.read_text().splitlines())


def science(data):
    total = data['total'][0]
    return {key: total[key] for key in
            ('candidate_restored_leaves', 'all_restored_leaves', 'hits', 'aborted', 'complete')}


def independent_hits(words):
    result = Counter()
    for word, count in words.items():
        points, state = [], 0
        for letter in word:
            points.append(state)
            state ^= 1 << int(letter)
        n = 1 + max(map(int, word))
        require(state == 0 and len(set(points)) == len(word), 'nonsimple restored leaf')
        if len({a ^ b for a in points for b in points}) == 1 << n:
            result[word] = count
    return result


def vectors(n, length):
    """Unpruned direct descendant oracle, including cycles using fewer labels."""
    rows = []

    def descend(word, points, highest):
        actual = [set() for _ in range(n)]
        if len(points) == length:
            if points[-1].bit_count() == 1:
                for omitted in range(n):
                    mask = ((1 << n)-1) ^ (1 << omitted)
                    actual[omitted].add(sum((q & mask).bit_count() % 2 == 0 for q in points))
        else:
            for label in range(min(highest+1, n-1)+1):
                q = points[-1] ^ (1 << label)
                if q not in points:
                    child = descend(word+str(label), points+(q,), max(highest, label))
                    for omitted in range(n):
                        actual[omitted].update(child[omitted])
        if len(points) >= 2:
            for omitted in range(n):
                rows.append((word, points, omitted, actual[omitted]))
        return actual

    descend('', (0,), -1)
    return rows


def probe_source(source):
    return '#define main census_main\n' + source + '''
#undef main
int main(void) {
    char prefix[23]; int omitted;
    while(scanf("%22s %d",prefix,&omitted)==2) {
        int depth=(int)strlen(prefix); q=0; seen=1;
        for(int i=0;i<depth;i++) {
            word[i]=prefix[i]-'0'; q^=1<<word[i]; seen|=bit(q);
        }
        printf("%u\\n",capacity_splits(depth,omitted));
    }
    return 0;
}
'''


def probe(binary, rows):
    result = command([binary], input=''.join(f'{word} {omitted}\n'
                     for word, _, omitted, _ in rows))
    masks = list(map(int, result.stdout.splitlines()))
    require(len(masks) == len(rows), 'probe output truncated')
    return [{i for i in range(23) if mask & (1 << i)} for mask in masks]


def kernel_checks(source, scratch):
    oracle = runpy.run_path(str(ROOT/'research/f7-prefix-matching-capacity/verify.py'))['feasible_splits']
    checks, rejected = 0, {}
    rows = vectors(4, 8)
    fixture = ('010210', (0,1,3,2,6,4,5), 0, set())
    require(fixture in rows, 'first strict fixture absent')
    require(not oracle(fixture[1], 4, 8, 0), 'first strict fixture changed')
    src, binary = scratch/'probe.c', scratch/'probe'
    src.write_text(probe_source(source))
    compile_c(src, binary, 4, 8)
    original = probe(binary, rows)
    for (_, points, omitted, actual), result in zip(rows, original):
        expected = {s for s, _ in oracle(points, 4, 8, omitted)}
        require(result == expected, 'C capacity differs from PR5001 actual splits')
        require(actual <= result, 'actual completion rejected')
        checks += 1
    mutants = {
        'wrong_omitted_coordinate': ('mask=((1<<N)-1)^(1<<omitted)', 'mask=(1<<N)-1'),
        'omitted_closing_edge': ('high=crossing+r+1', 'high=crossing+r'),
        'fixed_half_split': ('if(x>available[0] || r-x>available[1]) continue;',
                             'if(x>available[0] || r-x>available[1] || size[0]+x!=L/2) continue;'),
    }
    for name, (old, new) in mutants.items():
        require(source.count(old) == 1, f'mutation boundary changed: {name}')
        src.write_text(probe_source(source.replace(old, new)))
        compile_c(src, binary, 4, 8)
        changed = probe(binary, rows)
        witnesses = [(word, omitted, sorted(actual-result))
                     for (word, _, omitted, actual), result in zip(rows, changed)
                     if not actual <= result]
        require(witnesses, f'no semantic rejection witness: {name}')
        rejected[name] = witnesses[0]
    # The final edge can preserve or cross the omitted-coordinate functional.
    src.write_text(probe_source(source))
    compile_c(src, binary, 2, 4)
    closures = [('010', (0,1,3,2), 0, {2}), ('101', (0,2,3,1), 0, {2})]
    require(probe(binary, closures) == [{2}, {2}], 'closing edge rejected')
    return {'exact_split_checks': checks, 'strict_fixture': '010210/omit0',
            'semantic_rejections': rejected, 'closing_controls': 2}


def evidence(scratch):
    source = (HERE/'census.c').read_text()
    predecessor = (HERE/'vendor/union_census.c').read_text()
    delta = ''.join(difflib.unified_diff(predecessor.splitlines(True), source.splitlines(True),
                    fromfile='vendor/union_census.c', tofile='census.c'))
    require(delta == (HERE/'DELTA.diff').read_text(), 'source delta differs')
    pins = json.loads((HERE/'SOURCES.json').read_text())
    for row in pins['files']:
        if row['usage'] == 'input':
            require(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'],
                    'external input bytes differ')
    for row in pins['retained_files']:
        require(hashlib.sha256((HERE/row['retained_path']).read_bytes()).hexdigest() == row['sha256'],
                'retained predecessor bytes differ')
    rows = []
    old_c, new_c = scratch/'old.c', scratch/'new.c'
    old_c.write_text(leaf_instrument(predecessor))
    new_c.write_text(leaf_instrument(source))
    oracle_c = scratch/'oracle.c'
    oracle_source = (HERE/'vendor/firing_census.c').read_text()
    oracle_source = oracle_source.replace('    closed++;', '''    int highest=-1;
    for(int i=0;i<L;i++) if(word[i]>highest) highest=word[i];
    if(highest==n-1) {
        fputs("LEAF ",stdout);
        for(int i=0;i<L;i++) fputc('0'+word[i],stdout);
        fputc('\\n',stdout);
    }
    closed++;''')
    oracle_c.write_text(oracle_source)
    oracle_binary = scratch/'oracle'
    compile_c(oracle_c, oracle_binary)
    for n, length in DOMAINS:
        old_binary, new_binary = scratch/'old', scratch/'new'
        compile_c(old_c, old_binary, n, length)
        compile_c(new_c, new_binary, n, length)
        oracle_run = command([oracle_binary, n, length])
        restored = Counter(line[5:] for line in oracle_run.stdout.splitlines() if line.startswith('LEAF '))
        hits = independent_hits(restored)
        modes = []
        for flags in (('--no-budgets',), ()):
            before, old_leaves, old_hits = run_census(old_binary, scratch, (length//2,)*2, flags)
            off, off_leaves, off_hits = run_census(new_binary, scratch, (length//2,)*2, flags)
            on, on_leaves, on_hits = run_census(new_binary, scratch, (length//2,)*2, (*flags, '--prefix-capacity'))
            require(old_leaves == off_leaves == on_leaves, 'complete leaf multiset changed')
            require(old_hits == off_hits == on_hits == hits, 'accepted leaf multiset changed')
            require(science(before) == science(off) == science(on), 'scientific report changed')
            clean_off = {key: value for key, value in off.items() if not key.startswith('prefix_capacity_')}
            for section in ('shards', 'total'):
                clean_off[section] = [{key: value for key, value in row.items()
                                       if key not in ('seconds','prefix_capacity_prunes')}
                                      for row in off[section]]
            clean_before = dict(before)
            for section in ('shards', 'total'):
                clean_before[section] = [{key: value for key, value in row.items() if key != 'seconds'}
                                         for row in before[section]]
            require(clean_before == clean_off, 'default-off engine report changed')
            require(not off['prefix_capacity_enabled'] and on['prefix_capacity_enabled'], 'opt-in gate failed')
            if flags:
                require(on_leaves == restored, 'independent restored-word oracle differs')
            modes.append({'budgets': not bool(flags), 'restored_leaves': sum(on_leaves.values()),
                          'hits': sum(on_hits.values()), 'nodes_before': before['total'][0]['nodes'],
                          'nodes_after': on['total'][0]['nodes'],
                          'capacity_prunes': on['total'][0]['prefix_capacity_prunes'],
                          'leaf_multiset_sha256': hashlib.sha256(json.dumps(sorted(on_leaves.items())).encode()).hexdigest()})
        rows.append({'n': n, 'length': length, 'modes': modes})
    # A repeat-capable weight split must bypass the simple-path-only predicate.
    compile_c(old_c, scratch/'old', 4, 8)
    compile_c(new_c, scratch/'new', 4, 8)
    a, al, ah = run_census(scratch/'old', scratch, (4,3), ('--no-budgets',))
    b, bl, bh = run_census(scratch/'new', scratch, (4,3), ('--no-budgets','--prefix-capacity'))
    require(al == bl and ah == bh and science(a) == science(b), 'unbalanced caller changed')
    require(b['prefix_capacity_requested'] and not b['prefix_capacity_enabled']
            and not b['total'][0]['prefix_capacity_prunes'], 'unsafe caller did not bypass capacity')
    return {'schema': 'f7-prefix-capacity-engine/v1', 'domains': rows,
            'unbalanced_weight_split_bypass': {'split': [4,3], 'restored_leaves': sum(bl.values())},
            'kernel': kernel_checks(source, scratch),
            'source_sha256': {str(path.relative_to(HERE)): hashlib.sha256(path.read_bytes()).hexdigest()
                              for path in sorted(HERE.rglob('*')) if path.is_file()
                              and path.name not in ('RESULT.json','TIMINGS.json')}}


def timings(scratch):
    source, binary = scratch/'timing.c', scratch/'timing'
    source.write_bytes((HERE/'census.c').read_bytes())
    rows = []
    for n, length in DOMAINS:
        compile_c(source, binary, n, length)
        row = {'n': n, 'length': length}
        for enabled in (False, True):
            samples = []
            for _ in range(5):
                start = time.perf_counter()
                run_census(binary, scratch, (length//2,)*2,
                           ('--no-budgets','--prefix-capacity') if enabled else ('--no-budgets',))
                samples.append(time.perf_counter()-start)
            row['on' if enabled else 'off'] = {'seconds': samples, 'median': statistics.median(samples)}
        row['median_ratio_on_over_off'] = row['on']['median']/row['off']['median']
        rows.append(row)
    return {'scope': 'Five process-inclusive wall-time samples per setting, compilation excluded; no leaf instrumentation.',
            'python': sys.version, 'platform': platform.platform(),
            'compiler': command([os.environ.get('CC','cc'),'--version']).stdout.splitlines()[0],
            'flags': '-O2 -Wall -Wextra -Werror -std=c11', 'rows': rows}


def main():
    with tempfile.TemporaryDirectory(prefix='f7-capacity-') as temporary:
        scratch = Path(temporary)
        if sys.argv[1:] == ['--timings']:
            result = timings(scratch)
        else:
            require(sys.argv[1:] in ([], ['--emit-receipt']), 'unexpected argument')
            result = evidence(scratch)
    encoded = json.dumps(result, indent=2, sort_keys=True)+'\n'
    if sys.argv[1:] in (['--emit-receipt'], ['--timings']):
        print(encoded, end='')
    else:
        require((HERE/'RESULT.json').read_text() == encoded, 'receipt differs')
        print('PASS_F7_PREFIX_CAPACITY_ENGINE')


if __name__ == '__main__':
    main()

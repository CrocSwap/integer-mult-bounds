"""Check incremental census state against pinned scan and independent splits.

Ali Romman, substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
import argparse
import difflib
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import runpy
import statistics
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = ROOT/'research/f7-prefix-capacity-engine/census.c'

def need(ok, message):
    if not ok:
        raise ValueError(message)

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)

def authenticate():
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            need(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'], 'source bytes')
    before, after = OLD.read_text(), (HERE/'census.c').read_text()
    delta = ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                       fromfile='pinned/census.c', tofile='census.c'))
    need(delta == (HERE/'DELTA.diff').read_text(), 'complete source delta')
    return before, after

def command(argv, **kwargs):
    return subprocess.run(list(map(str, argv)), capture_output=True, text=True, timeout=15, **kwargs)

def compile_c(text, path, n, length, sanitize=False):
    src = path.with_suffix('.c')
    src.write_text(text)
    extra = ['-fsanitize=undefined,bounds', '-fno-sanitize-recover=all'] if sanitize else []
    out = command([os.environ.get('CC', 'cc'), '-O2', '-Wall', '-Wextra', '-Werror', '-std=c11',
                   f'-DN={n}', f'-DL={length}', *extra, src, '-o', path])
    need(out.returncode == 0, 'compile: '+out.stderr)

def stable(value):
    if isinstance(value, dict):
        return {k: stable(v) for k, v in value.items() if k != 'seconds'}
    if isinstance(value, list):
        return [stable(v) for v in value]
    return value

def run_census(binary, directory, split, flags):
    with tempfile.TemporaryDirectory(dir=directory) as tmp:
        tmp = Path(tmp)
        start = time.perf_counter()
        out = command([binary, f'{split[0]},{split[1]}', '--hits', tmp/'hits', '--json', tmp/'run', *flags])
        seconds = time.perf_counter()-start
        need(out.returncode in (0, 2), 'census failed: '+out.stderr)
        data = json.loads((tmp/'run').read_text())
        need((out.returncode == 2) == data['aborted'] and data['complete'] != data['aborted'], 'cap status')
        leaves = Counter(line[5:] for line in out.stdout.splitlines() if line.startswith('LEAF '))
        hits = Counter((tmp/'hits').read_text().splitlines())
        return dict(report=stable(data), leaves=leaves, hits=hits), seconds

def instrument(source):
    old = '        run.candidate_leaves++;'
    need(source.count(old) == 1, 'leaf boundary')
    return source.replace(old, old+'''\n        fputs("LEAF ",stdout);
        for(int k=0;k<L;k++) fputc('0'+word[k],stdout);
        fputc('\\n',stdout);''')

def paths(n, length):
    rows = []
    def visit(word, points, highest):
        if word:
            for omitted in range(n):
                rows.append((word, points, omitted))
        if len(points) == length:
            return
        for label in range(min(n-1, highest+1)+1):
            q = points[-1] ^ (1 << label)
            if q not in points:
                visit(word+str(label), points+(q,), max(highest, label))
    visit('', (0,), -1)
    return rows

def probe_source(source):
    return '#define main census_main\n'+source+'''
#undef main
int main(void) {
    char prefix[23]; int omitted;
    while(scanf("%22s %d",prefix,&omitted)==2) {
        int depth=(int)strlen(prefix); q=0; seen=1;
        memset(capacity,0,sizeof capacity);
        for(int v=0;v<N;v++) capacity[0][v].size[0]=1;
        for(int i=0;i<depth;i++) {
            word[i]=prefix[i]-'0'; q^=1<<word[i];
            extend_capacity(i,q,word[i],seen); seen|=bit(q);
        }
        printf("%u\\n",capacity_splits(depth,omitted));
    }
    return 0;
}
'''

def kernel(after, tmp):
    rows = paths(4, 10)
    oracle = runpy.run_path(str(ROOT/'research/f7-prefix-matching-capacity/verify.py'))['feasible_splits']
    expected = [sum(1 << s for s, _ in oracle(points, 4, 10, omitted)) for _, points, omitted in rows]
    payload = ''.join(f'{word} {omitted}\n' for word, _, omitted in rows)
    def probe(source, sanitize=False):
        binary = tmp/'probe'
        compile_c(probe_source(source), binary, 4, 10, sanitize)
        out = command([binary], input=payload)
        need(out.returncode == 0, 'kernel process: '+out.stderr)
        return list(map(int, out.stdout.splitlines()))
    need(probe(after) == expected, 'independent split oracle')
    need(probe(after, True) == expected, 'sanitized split oracle')
    mutations = {
        'missing_occupied_pair': ('next->occupied_pairs[side]++;', 'next->occupied_pairs[side]+=0;'),
        'wrong_mate': ('old_seen&bit(point^(1<<omitted))', 'old_seen&bit(point)'),
        'lost_parent_state': ('*next=capacity[depth][omitted];', 'memset(next,0,sizeof *next);'),
        'lost_final_endpoint': ('int endpoints[2]={0,q};', 'int endpoints[2]={0,0};'),
    }
    rejected = {}
    for label, (old, new) in mutations.items():
        need(after.count(old) == 1, 'mutation boundary')
        changed = probe(after.replace(old, new))
        need(len(changed) == len(expected), 'probe output length')
        first = next((i for i, (a, b) in enumerate(zip(changed, expected)) if a != b), None)
        need(first is not None, 'mutation survived: '+label)
        rejected[label] = [rows[first][0], rows[first][2], expected[first], changed[first]]
    return dict(prefix_functionals=len(rows), mutations=rejected)

def evidence(before, after, tmp):
    rows = []
    for n, length in ((2, 4), (3, 6), (4, 8), (4, 10), (5, 12)):
        binaries = [tmp/'old', tmp/'new']
        for source, binary in zip((before, after), binaries):
            compile_c(instrument(source), binary, n, length)
        for flags in ([], ['--no-budgets'], ['--prefix-capacity'], ['--prefix-capacity', '--no-budgets']):
            left, _ = run_census(binaries[0], tmp, (length//2,)*2, flags)
            right, _ = run_census(binaries[1], tmp, (length//2,)*2, flags)
            need(left == right, 'complete search/report equivalence')
            rows.append(dict(n=n, length=length, flags=flags, report=left['report']['total'][0],
                             leaves_sha256=sha256(canonical(left['leaves']).encode()).hexdigest(),
                             hits_sha256=sha256(canonical(left['hits']).encode()).hexdigest()))
    # These use the last domain. Every run starts a fresh process and files.
    boundaries = []
    for split, flags in (((6, 5), ['--prefix-capacity', '--no-budgets']),
                         ((6, 6), ['--prefix-capacity', '--no-budgets', '010', '012']),
                         ((6, 6), ['--prefix-capacity', '--no-budgets', '--cap', '17'])):
        left, _ = run_census(binaries[0], tmp, split, flags)
        right, _ = run_census(binaries[1], tmp, split, flags)
        need(left == right, 'repeat/shard/cap boundary')
        boundaries.append(dict(split=split, flags=flags, report=left['report']))
    result = dict(status='PASS_INCREMENTAL_PREFIX_CAPACITY', complete_domain_modes=rows,
                  boundaries=boundaries, kernel=kernel(after, tmp),
                  census_sha256=sha256(after.encode()).hexdigest())
    return result

def timings(before, after, tmp):
    binaries = {'old': tmp/'old', 'new': tmp/'new'}
    for name, source in (('old', before), ('new', after)):
        compile_c(source, binaries[name], 6, 14)
    samples = {name: [] for name in ('old_on', 'new_on', 'new_off')}
    receipts = {}
    for turn in range(7):
        order = tuple(samples) if turn % 2 == 0 else tuple(reversed(samples))
        for label in order:
            name, mode = label.split('_')
            flags = ['--no-budgets']+(['--prefix-capacity'] if mode == 'on' else [])
            result, elapsed = run_census(binaries[name], tmp, (7, 7), flags)
            samples[label].append(elapsed)
            receipts.setdefault(label, result['report'])
            need(receipts[label] == result['report'], 'timing run changed report')
    need(receipts['old_on'] == receipts['new_on'], 'timing traversal changed')
    medians = {k: statistics.median(v) for k, v in samples.items()}
    return dict(domain=[6, 14], split=[7, 7], runs=7, seconds=samples, medians=medians,
                old_on_over_new_on=medians['old_on']/medians['new_on'],
                new_on_over_new_off=medians['new_on']/medians['new_off'], reports=receipts,
                compiler=command([os.environ.get('CC', 'cc'), '--version']).stdout,
                python=sys.version, platform=platform.platform(), machine=platform.machine(),
                definition='Serialized alternating process-inclusive runs; no compilation or leaf instrumentation in timings.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--emit', action='store_true')
    parser.add_argument('--timings', action='store_true')
    args = parser.parse_args()
    expected = None if args.emit or args.timings else json.loads((HERE/'RESULT.json').read_text())
    before, after = authenticate()
    with tempfile.TemporaryDirectory() as tmp:
        result = timings(before, after, Path(tmp)) if args.timings else evidence(before, after, Path(tmp))
    need(authenticate() == (before, after), 'sources changed during replay')
    if args.emit or args.timings:
        print(json.dumps(result, indent=2))
    else:
        need(canonical(result) == canonical(expected), 'complete typed receipt')
        print(result['status'])

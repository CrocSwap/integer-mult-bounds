#!/usr/bin/env python3
"""Exact target-matching certificate on the fixed PR694 basis, composed with PR681.

Prepared for Sagar Thakrar with substantial OpenAI Codex assistance, Apache-2.0.
Circuit mechanisms and the native/hosted drivers retain their predecessor credit.
"""
import argparse
from collections import Counter
import copy
import gzip
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BIT = ROOT / 'research/e8-bit-r420/data/bitE8mut-r420.json.gz'
CHECK = ROOT / 'research/e8-bit-r420/code/xcheck.py'
EXPORT = ROOT / 'research/e8-bit-carrier-skeleton/code/bit/export_records.py'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    data = Path(path).read_bytes()
    return json.loads(gzip.decompress(data) if str(path).endswith('.gz') else data)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def module(path):
    spec = importlib.util.spec_from_file_location('paired_' + path.stem, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def source_check():
    pins = read(HERE / 'SOURCES.json')
    for name, pin in pins['imported'].items():
        data = (HERE / name).read_bytes()
        need(hashlib.sha256(data).hexdigest() == pin['sha256'], 'import changed: ' + name)
        blob = b'blob ' + str(len(data)).encode() + b'\0' + data
        need(hashlib.sha1(blob).hexdigest() == pin['git_blob'], 'import Git blob: ' + name)
    for name, pin in pins['base_files'].items():
        data = (ROOT / name).read_bytes()
        if pin['representation'] == 'gzip-payload':
            data = gzip.decompress(data)
        else:
            need(pin['representation'] == 'file-bytes', 'unknown source representation')
        need(hashlib.sha256(data).hexdigest() == pin['sha256'], 'base source changed: ' + name)
    return pins


def cleanup(word):
    return [[1, d, list(ss)] for _, d, ss in reversed(word['A'] + word['B'])
            if not 120 <= d < 240]


def body(original):
    """Reconstruct PR681's A/B/C from its immutable, attributed recipes."""
    word = copy.deepcopy(original)
    q = read(HERE / 'vendor/pr691-quad.json')
    regs = q['registers']
    need(word['A'][q['start']:q['stop']] ==
         [[q['frame'], regs[d], [regs[s]]] for d, s in q['original']], 'quad input slice')
    word['A'][q['start']:q['stop']] = [[q['frame'], regs[d], [regs[s]]]
                                               for d, s in q['replacement']]
    b = read(HERE / 'vendor/pr674-block.json')
    word['B'][371:417] = [[547, d, [s]] for d, s in b['replacement_ops']]
    b = read(HERE / 'vendor/pr670-block.json')
    regs = b['registers']
    word['B'][263:313] = [[545, regs[d], [regs[s]]] for d, s in b['replacement_local_ops']]
    r = read(HERE / 'vendor/pr681-decoders.json')
    need(r['pairs'] == [r['source_pairs'][i] for i in r['selected_indices']], 'decoder recipe subset')
    tail = word['A'][-9:]
    need([g[1] for g in tail] == word['ret'] and all(g[0] == 1 for g in tail), 'decoder location')
    pre = [[1, a, [b]] for a, b in r['pairs']]
    transformed = []
    for frame, dst, sources in tail:
        row = set(sources)
        for a, b in r['pairs']:
            if a in row:
                row.symmetric_difference_update({b})
        transformed.append([frame, dst, sorted(row)])
    word['A'] = word['A'][:-9] + pre + transformed + copy.deepcopy(pre[::-1])
    word['C'] = cleanup(word)
    return word


def helper_matrix(original):
    rows = {d: set(sources) for frame, d, sources in original['D']}
    need(len(rows) == 120 and set(rows) == set(range(120, 240)), 'canonical D targets')
    prefix, used = [], set()
    for pair in read(HERE / 'vendor/pr694-recipe.json')['pairs']:
        a, b = pair['dst'], pair['src']
        need(type(a) is int and type(b) is int and 240 <= a < 660 and 240 <= b < 660
             and a != b and not ({a, b} & used), 'helper pair domain')
        used.update((a, b))
        before = sum(map(len, rows.values()))
        for row in rows.values():
            if a in row:
                row.symmetric_difference_update({b})
        need(before - sum(map(len, rows.values())) - 2 == pair['net_saved_additions'], 'helper price')
        prefix.append([0, a, [b]])
    need(len(prefix) == 201 and sum(map(len, rows.values())) == 12586, 'fixed helper matrix')
    return rows, prefix


def gain(rows, a, b):
    return len(rows[b]) - len(rows[a] ^ rows[b]) - 2


def matching_check(rows, pairs, prices):
    need(len(prices) == 120 and all(type(q) is int and q >= 0 for q in prices), 'dual domain')
    for a, b in itertools.combinations(range(120, 240), 2):
        weight = max(0, gain(rows, a, b), gain(rows, b, a))
        need(prices[a-120] + prices[b-120] >= 2*weight, 'dual edge inequality')
    used, saving = set(), 0
    for pair in pairs:
        need(len(pair) == 3 and all(type(x) is int for x in pair), 'matching integer triple')
        a, b, score = pair
        need(120 <= a < 240 and 120 <= b < 240 and a != b and not ({a, b} & used), 'matching overlap/domain')
        need(score == gain(rows, a, b) and score > 0, 'oriented matching price')
        used.update((a, b))
        saving += score
    need(2*saving == sum(prices), 'dual/primal objective gap')
    return {'unordered_edges': 7140, 'oriented_edges': 14280, 'pairs': len(pairs),
            'saving': saving, 'twice_dual_objective': sum(prices)}


def substitute(word, original, pairs):
    rows, helpers = helper_matrix(original)
    targets, used = [], set()
    for a, b, score in pairs:
        need(a in rows and b in rows and a != b and not ({a, b} & used), 'target matching domain')
        need(gain(rows, a, b) == score and score > 0, 'target gain')
        used.update((a, b))
        rows[b] ^= rows[a]
        targets.append([0, b, [a]])
    result = copy.deepcopy(word)
    result['D'] = helpers + targets + [[0, t, sorted(row)] for t, row in sorted(rows.items())]
    result['D'] += copy.deepcopy(targets[::-1] + helpers[::-1])
    return result


def d_operator(word):
    rows = [{i} for i in range(660)]
    for frame, dst, sources in word['D']:
        need(frame == 0 and word['frames'][frame] == [] and 120 <= dst < 660 and sources,
             'D frame/destination')
        need(len(set([dst] + sources)) == len(sources)+1 and all(120 <= s < 660 for s in sources), 'D operands')
        need(dst < 240 or all(s >= 240 for s in sources), 'target feeds helper')
        for source in sources:
            rows[dst].symmetric_difference_update(rows[source])
    return rows


def scalar_events(word):
    for phase in ('D', 'A', 'scatter', 'B', 'C'):
        if phase == 'scatter':
            for k, source in enumerate(word['ret']):
                yield ('copy', 660, source)
                for t, row in enumerate(word['scatter']):
                    if k in row:
                        yield ('add', 120+t, 660)
                yield ('erase', 660, source)
        else:
            for _, dst, sources in word[phase]:
                for source in sources:
                    yield ('add', dst, source)


def replay(events, reverse=False):
    """Separate set-valued 660-input replay plus integer positive row bounds."""
    rows = [{i} for i in range(660)] + [set()]
    bound = [1]*660 + [0]
    peak, opened, copies = 1, None, 0
    for kind, dst, src in reversed(events) if reverse else events:
        if reverse and kind != 'add':
            kind = 'copy' if kind == 'erase' else 'erase'
        if kind == 'add':
            need(0 <= dst < 660 and 0 <= src <= 660 and dst != src
                 and (src != 660 or opened is not None) and dst != opened, 'scalar ADD/lifecycle')
            rows[dst].symmetric_difference_update(rows[src])
            bound[dst] += bound[src]
            peak = max(peak, bound[dst])
        elif kind == 'copy':
            need(opened is None and dst == 660 and not rows[660], 'COPY lifecycle')
            rows[660] = set(rows[src]); bound[660] = bound[src]
            opened = src; copies += 1
        elif kind == 'erase':
            need(opened == src and dst == 660 and rows[660] == rows[src], 'ERASE lifecycle')
            rows[660] = set(); bound[660] = 0; opened = None
        else:
            raise ValueError('unknown event')
    expected = [{i} for i in range(660)] + [set()]
    for t in range(120):
        expected[120+t].add(t)
    need(rows == expected and opened is None and copies == 9, 'full arbitrary-input endpoint')
    return peak


def frame_paths(word, dimensions):
    paths = [[f] for f in word['start']]
    paid = Counter()
    for phase in ('D', 'A', 'scatter', 'B', 'C', 'final'):
        if phase == 'scatter':
            for r in word['ret']:
                paid[dimensions[paths[r][-1]]] += 1
            continue
        gates = [[f, r, []] for r, f in enumerate(word['final'])] if phase == 'final' else word[phase]
        for frame, dst, sources in gates:
            for r in [dst] + sources:
                old = paths[r][-1]
                if frame != old:
                    rank = dimensions[frame]-dimensions[old]
                    need(rank > 0 and set(word['frames'][old]) <= set(word['frames'][frame]), 'frame ascent')
                    paid[rank] += 1; paths[r].append(frame)
    return paths, {str(r): n for r, n in sorted(paid.items())}


def receipt(word, dimensions):
    events = list(scalar_events(word))
    f, b = replay(events), replay(events, True)
    payload = 64*f**3*b**2
    need(payload < 2**104, '104-bit payload cap')
    paths, paid = frame_paths(word, dimensions)
    return {'semantic_word_sha256': digest(word), 'scalar_stream_sha256': digest(events),
            'binary_additions': sum(e[0] == 'add' for e in events),
            'D_binary_additions': sum(len(g[2]) for g in word['D']), 'D_grouped_gates': len(word['D']),
            'forward_and_reverse': [{'copies': 9, 'columns': 660} for _ in range(2)],
            'forward_prefix': f, 'reverse_prefix': b, 'payload_prefix_upper': str(payload),
            'payload_prefix_bits': payload.bit_length(), 'paid_histogram': paid,
            'rank_mass': sum(int(r)*n for r, n in paid.items()), 'frame_paths_sha256': digest(paths)}


def export_check(word, result, out):
    word_path = out / 'word.json.gz'
    word_path.write_bytes(gzip.compress(canonical(word)+b'\n', mtime=0))
    subprocess.run([sys.executable, '-I', '-B', str(EXPORT), str(word_path), str(out/'records')],
                   check=True, stdout=subprocess.DEVNULL)
    data = (out/'records/249-records.bin').read_bytes()
    need(len(data) % 24 == 0, 'record alignment')
    events, paid = [], Counter()
    for op, a, b, c, d, e in struct.iter_unpack('<6i', data):
        if op == 0:
            paid[d] += 1
        elif op == 1:
            need(c == 1, 'ADD coefficient'); events.append(('add', a, b))
        elif op == 2:
            paid[e] += 1; events.append(('copy', b, a))
        elif op == 3:
            events.append(('erase', b, a))
        else:
            raise ValueError('unknown record')
    need(events == list(scalar_events(word)), 'exported scalar events differ')
    need({str(k): v for k, v in sorted(paid.items())} == result['paid_histogram'], 'exported paid profile')
    result.update(exported_records=len(data)//24, record_sha256=hashlib.sha256(data).hexdigest())


def controls(original, before, after, cert):
    names = []
    def reject(name, action):
        try:
            action()
        except ValueError:
            names.append(name)
        else:
            raise ValueError('control accepted: ' + name)
    expected = d_operator(original)
    for name, index in [('helper preparation', 0), ('target preparation', 201),
                        ('target restoration', -202), ('helper restoration', -1), ('middle read', 259)]:
        wrong = copy.deepcopy(after); del wrong['D'][index]
        reject('omit '+name, lambda w=wrong: need(d_operator(w) == expected, 'D endpoint'))
    wrong = copy.deepcopy(after); wrong['D'][0][0] = 1
    reject('D leaves frame zero', lambda: d_operator(wrong))
    rows, _ = helper_matrix(original)
    reject('zero vertex prices', lambda: matching_check(rows, cert['pairs'], [0]*120))
    wrong_pairs = copy.deepcopy(cert['pairs']); wrong_pairs.append(wrong_pairs[0])
    reject('overlapping target pairs', lambda: matching_check(rows, wrong_pairs, cert['doubled_vertex_prices']))
    wrong_prices = list(cert['doubled_vertex_prices'])
    wrong_prices[11] += 1
    reject('feasible but nontight dual', lambda: matching_check(rows, cert['pairs'], wrong_prices))
    wrong_pairs = copy.deepcopy(cert['pairs']); wrong_pairs[0][2] += 1
    reject('inflated pair saving', lambda: matching_check(rows, wrong_pairs, cert['doubled_vertex_prices']))
    # A pairing certificate for K cannot be substituted for the transformed KQ.
    stale = {d: set(ss) for _, d, ss in original['D']}
    reject('certificate on original K', lambda: matching_check(stale, cert['pairs'], cert['doubled_vertex_prices']))
    wrong = copy.deepcopy(after); wrong['C'].pop()
    reject('missing cleanup', lambda: replay(list(scalar_events(wrong))))
    neutral = copy.deepcopy(after)
    neutral['D'].extend([[0, 240, [241]], [0, 240, [241]]])
    need(d_operator(neutral) == expected, 'neutral pair endpoint')
    need(sum(e[0] == 'add' for e in scalar_events(neutral)) ==
         sum(e[0] == 'add' for e in scalar_events(after))+2, 'neutral operations uncharged')
    return names + ['neutral endpoint accepted and two ADDs charged']


def run(out):
    pins = source_check()
    original = read(BIT)
    cert = read(HERE / 'OPTIMUM.json')
    need(cert['assignment_seed'] == 11, 'assignment seed')
    rows, _ = helper_matrix(original)
    optimum = matching_check(rows, cert['pairs'], cert['doubled_vertex_prices'])
    need(optimum['saving'] == cert['gain'] == 1442, 'optimum value')
    integrated = body(original)
    old_pairs = read(HERE / 'vendor/pr681-targets.json')['pairs']
    before = substitute(integrated, original, old_pairs)
    after = substitute(integrated, original, cert['pairs'])
    pr733 = read(HERE/'vendor/pr733-targets.json')
    need(pr733['fixed_helper_recipe_sha256'] == hashlib.sha256(
         (HERE/'vendor/pr694-recipe.json').read_bytes()).hexdigest(), 'PR733 fixed helper recipe differs')
    same_body = substitute(integrated, original, pr733['target_pairs'])
    need(d_operator(before) == d_operator(after) == d_operator(original), 'semantic D substitution')
    checker = module(CHECK)
    checked, _, _, h, c, _ = checker.check(original)
    need(all(h.values()) and all(c.values()), 'original H1-H5')
    canonical_word = copy.copy(checked); canonical_word.w = integrated
    canonical_word.full()
    h, c, _ = canonical_word.interface()
    need(all(h.values()) and all(c.values()), 'canonical integrated H1-H5')
    for word in (before, after, same_body):
        obj = copy.copy(checked); obj.w = word; obj.full()
        h, c, _ = obj.interface()
        need(not h['H2_D_frame0_targets_from_helpers'] and not c['K_equals_D'], 'literal guard unexpectedly accepts')
        need(all(v for k, v in h.items() if k != 'H2_D_frame0_targets_from_helpers'), 'other H hypothesis')
    results = {}
    for name, word in [('baseline', before), ('replacement', after)]:
        folder = out/(name+'-export'); folder.mkdir()
        results[name] = receipt(word, checked.fdim)
        export_check(word, results[name], folder)
        (out/(name+'.json.gz')).write_bytes(gzip.compress(canonical(word)+b'\n', mtime=0))
    expected = read(HERE / 'vendor/pr681-expected.json')['bit']['replacement']
    need(results['baseline'] == expected, 'PR681 exact bit receipt differs')
    old, new = results['baseline'], results['replacement']
    need(old['binary_additions'] == 18378 and new['binary_additions'] == 18362, 'composed cost')
    for key in ('forward_prefix', 'reverse_prefix', 'paid_histogram', 'rank_mass', 'frame_paths_sha256'):
        need(old[key] == new[key], 'composed envelope/profile differs: ' + key)
    prior = receipt(same_body, checked.fdim)
    need(prior['binary_additions'] == 18370 and prior['D_binary_additions'] == 11554,
         'PR733 matching on the same PR681 body')
    for key in ('forward_prefix', 'reverse_prefix', 'paid_histogram', 'rank_mass', 'frame_paths_sha256'):
        need(prior[key] == new[key], 'same-body comparator differs: ' + key)
    result = {'status': 'PASS_R420_OPTIMAL_COMPOSED_PAIRS', 'base_commit': pins['base_commit'],
              **results, 'saved_additions': 16, 'selected_ADDs': 26916, 'saved_from_selected': 8554,
              'matching_optimum': optimum, 'controls': controls(original, before, after, cert),
              'PR733_matching_on_PR681_body': prior, 'saved_beyond_prior_matching_on_same_body': 8,
              'inherited_PR733_ADDs': 18548, 'same_optimum_on_PR733_body_ADDs': 18540,
              'literal_H2_claimed': False, 'semantic_D_columns': 660, 'no_new_kappa': True}
    (out/'LOCAL.json').write_text(json.dumps(result, indent=2)+'\n')
    return result


def deterministic(value):
    if isinstance(value, dict):
        return {k: deterministic(v) for k, v in value.items() if k != 'seconds'}
    if isinstance(value, list):
        return [deterministic(v) for v in value]
    return value


def native_controls(out, local, native):
    for name in ('baseline', 'replacement'):
        need(native[name]['legality']['common_frame_ADDs'] == local[name]['binary_additions'], 'native absolute cost')
        for stage in native[name]['stages'].values():
            need(stage['receipt']['local_scalar_additions'] == local[name]['binary_additions'], 'native stage cost')
    raw = (out/'replacement/cout/COHORT249-RECORDS.bin').read_bytes()
    rows = list(struct.iter_unpack('<6i', raw))
    index = max(i for i, e in enumerate(rows) if e[0] == 1 and e[5] == 1 and e[1] >= 240)
    mutant = out/'missing-helper-return.bin'
    mutant.write_bytes(b''.join(struct.pack('<6i', *e) for i, e in enumerate(rows) if i != index))
    for pairs in (2, 4, 5):
        rejected = subprocess.run([str(out/('bin/columns'+str(pairs))), str(mutant),
                                   str(out/('invalid'+str(pairs)+'.json'))], capture_output=True, text=True)
        need(rejected.returncode != 0 and 'local defining-decoder full formal column' in rejected.stderr,
             'native missing restoration was not rejected by the endpoint check')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, help='fresh output directory')
    p.add_argument('--native', action='store_true')
    p.add_argument('--hosted', action='store_true', help='includes native replay')
    p.add_argument('--record', type=Path, help='write a candidate receipt for review; not a certificate PASS')
    args = p.parse_args()
    if args.out:
        need(not args.out.exists(), 'output already exists')
        args.out.mkdir(parents=True)
        out = args.out
        temporary = None
    else:
        temporary = tempfile.TemporaryDirectory(prefix='r420-optimal-pairs-')
        out = Path(temporary.name)
    result = run(out)
    if args.record:
        need(not args.record.exists(), 'record destination already exists')
        args.record.write_text(json.dumps(result, indent=2)+'\n')
        print('RECORDED_CANDIDATE_RECEIPT', args.record)
    else:
        need(result == read(HERE/'CERTIFICATE.json'), 'committed certificate differs')
        if args.native or args.hosted:
            native = module(HERE/'native.py').run(ROOT, out)
            native_controls(out, result, native)
            need(deterministic(native) == read(HERE/'NATIVE.json'), 'native certificate differs')
            (out/'NATIVE.json').write_text(json.dumps(native, indent=2)+'\n')
        if args.hosted:
            hosted = module(HERE/'hosted.py').run(ROOT, out)
            need(deterministic(hosted) == read(HERE/'HOSTED.json'), 'hosted certificate differs')
            (out/'HOSTED.json').write_text(json.dumps(hosted, indent=2)+'\n')
        print('PASS_R420_OPTIMAL_COMPOSED_PAIRS optimum=1442 pairs=58 edges=7140 '
              'ADDs=18378->18362 payload_bits=104 columns=660 controls=13 no_new_kappa')
    if temporary:
        temporary.cleanup()


if __name__ == '__main__':
    main()

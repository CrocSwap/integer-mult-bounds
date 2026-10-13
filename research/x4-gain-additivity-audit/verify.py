#!/usr/bin/env python3
"""Exact arithmetic audit of the four PR799 paired read exchanges.

The frozen construction and arithmetic engines are imported only after their
source bytes have been checked against SOURCES.json. No cold replay is run.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
GROUPS = ((448, 472), (458, 592), (470, 604), (482, 614))
ARCHIVE = 'research/community-frontier741-audit/composed-replay-evidence.tar.gz'
RECIPE = 'research/gauge44-frames-x/construction/jx/RECIPE-X4.json'
BUILDER = 'research/gauge44-frames-x/construction/jx/build_jx.py'
PLAN = 'research/gauge44-frames-x/data/PLAN.json'
SPEC = 'research/gauge44-frames-x/data/SPEC.json'
ENGINES = 'research/complex-k492-owner-repair/vendor/multicold/engines/'


def require(ok, why):
    if not ok:
        raise ValueError(why)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_bytes())


def load(path, name):
    spec = importlib.util.spec_from_file_location('x4_gain_' + name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_sources(root, sources):
    required = {RECIPE, BUILDER, PLAN, SPEC,
                ENGINES + 'moment.py', ENGINES + 'base_two_moment.py'}
    files = sources['files']
    require(required <= set(files) and ARCHIVE not in files,
            'source manifest must pin each consumed source without pinning archive compression')
    for name, expected in files.items():
        require(digest((root / name).read_bytes()) == expected, 'source digest differs: ' + name)


def archive_word(root, sources):
    require(sources['baseline_archive'] == ARCHIVE, 'baseline archive path differs')
    path = root / sources['baseline_archive']
    member = sources['baseline_member']
    require(member == 'complex/sw4/FULL-WORD.json.gz', 'unexpected archive member')
    with tarfile.open(path, 'r:gz') as archive:
        names = [entry for entry in archive.getmembers() if entry.name == member]
        require(len(names) == 1 and names[0].isfile(), 'missing or repeated baseline member')
        stream = archive.extractfile(names[0])
        require(stream is not None, 'baseline member cannot be read')
        raw = gzip.decompress(stream.read())
    require(digest(raw) == sources['baseline_content_sha256'], 'baseline word digest differs')
    return json.loads(raw)


def subset_recipe(recipe, groups):
    selected = {h for group in groups for h in group}
    out = dict(recipe)
    out['edits'] = {kind: [entry for entry in recipe['edits'][kind] if entry['h'] in selected]
                    for kind in ('replace', 'delete', 'insert')}
    selected_replacements = {entry['i'] for entry in out['edits']['replace']}
    out['raises'] = [entry for entry in recipe['raises'] if entry[0] in selected_replacements]
    require(len(out['raises']) == 4*len(groups), 'raises do not match chosen edits')
    return out


def local_profile(word):
    return {int(r): n for r, n in word['report']['local_profile'].items()}


def helper_widths(word, builder):
    ranks = Counter()
    for r in range(224, 224 + word['report']['R']):
        start = builder.basis(word['start_extra'].get(str(r), []))
        final = builder.basis(word['helper_final'].get(str(r), builder.FULL))
        ranks[len(final)-len(start)] += 1
    return {str(r): n for r, n in sorted(ranks.items())}


def check_profile_family(profiles, selected_global, idle, calls):
    require(len(profiles) == 5 and calls == 72, 'profile family or call count differs')
    for j in range(5):
        expected_local = dict(profiles[0])
        expected_local[1] -= 2*j
        expected_local[2] += j
        require(profiles[j] == expected_local, 'local profile is not the paired delta at j=' + str(j))
    global_profiles = []
    for j, local in enumerate(profiles):
        result = Counter({r: calls*n for r, n in local.items()})
        result.update(idle)
        require(all(n > 0 for n in result.values()), 'nonpositive global profile')
        global_profiles.append(dict(sorted(result.items())))
    require(global_profiles[4] == selected_global, 'selected global profile differs')
    for j, profile in enumerate(global_profiles):
        require(sum(r*n for r, n in profile.items()) == 73*7168-2560,
                'rank mass differs at j=' + str(j))
    return global_profiles


def exact_brackets(profiles, sources, moment, base_two):
    brackets = sources['root_brackets']
    require(set(brackets) == {str(j) for j in range(5)}, 'root bracket set differs')
    result = []
    for j, profile in enumerate(profiles):
        require(all(type(r) is int and 0 < r < 73 and type(n) is int and n > 0
                    for r, n in profile.items()), 'moment input domain differs')
        lower, upper = map(Q, brackets[str(j)])
        # ln(73/r)<5, so each exponent argument is below 3/200 here.
        # This guard remains effective under python -O, unlike imported asserts.
        require(0 < lower < upper < Q(3, 1000) and upper-lower == Q(1, 10**24),
                'invalid root bracket')
        signs = []
        for endpoint, accept in ((lower, True), (upper, False)):
            a, b = moment.moment(profile, 73, 7168, endpoint, False)
            c, d = base_two.moment(73, 7168, list(profile.items()), endpoint)
            require((b < 1 and d < 1) if accept else (a > 1 and c > 1),
                    'root bracket sign fails at j=' + str(j))
            signs.append({'endpoint': str(endpoint), 'mercator': [str(a-1), str(b-1)],
                          'base_two': [str(c-1), str(d-1)]})
        result.append({'j': j, 'root': [str(lower), str(upper)], 'signs': signs})
    return result


def arithmetic_result(brackets):
    values = [(Q(row['root'][0]), Q(row['root'][1])) for row in brackets]
    k = [(lo/(1+lo), hi/(1+hi)) for lo, hi in values]
    seconds = []
    for j in range(1, 4):
        lo = k[j+1][0]-2*k[j][1]+k[j-1][0]
        hi = k[j+1][1]-2*k[j][0]+k[j-1][1]
        require(lo > 0, 'second difference is not proved positive')
        seconds.append({'center': j, 'interval': [str(lo), str(hi)]})
    lo = k[4][0]-4*k[1][1]+3*k[0][0]
    hi = k[4][1]-4*k[1][0]+3*k[0][1]
    require(lo > 0, 'four-exchange additivity residual is not proved positive')
    return {'ideal_kappa_intervals': [[str(a), str(b)] for a, b in k],
            'second_differences': seconds, 'four_vs_four_singles': [str(lo), str(hi)]}


def verify(root=ROOT, manifest=HERE / 'SOURCES.json'):
    sources = read_json(manifest)
    check_sources(root, sources)
    recipe = read_json(root / RECIPE)
    word = archive_word(root, sources)
    builder = load(root / BUILDER, 'build_jx')
    require(builder.csha(word) == recipe['input_content_sha256'], 'recipe baseline pin differs')
    plan, spec = read_json(root / PLAN), read_json(root / SPEC)
    require(plan['M'] == 73 and plan['live'] == 7168 and plan['deficit'] == 2560,
            'global pricing parameters differ')
    require(spec['data']['plan_sha256'] == digest((root / PLAN).read_bytes()), 'spec/plan binding differs')
    calls = len(spec['dispatch'])
    require(calls == len(plan['provider_calls']) == 72, 'call count differs')
    idle = {int(r): n for r, n in spec['expected']['idle_remainder_profile'].items()}
    require(idle == {1: 1, 3: 1, 44: 1, 48: 2396}, 'idle profile differs')
    require(word['report']['R'] == 504, 'helper count differs')
    widths = word['report']['width_inventory']
    require(widths == helper_widths(word, builder) == spec['providers']['gauge44']['inventory'] and
            sum(int(width)*count for width, count in widths.items()) > 0 and
            sum(widths.values()) == 504, 'helper width inventory differs')
    selected_global = {int(r): n for r, n in plan['profile'].items()}
    profiles_by_size = defaultdict(list)
    subset_rows = []
    endpoints = ('ports', 'centers', 'start_extra', 'helper_final')
    for mask in range(16):
        groups = [group for bit, group in enumerate(GROUPS) if mask & (1 << bit)]
        outcome = builder.build(word, subset_recipe(recipe, groups))
        require(all(outcome[name] == word[name] for name in endpoints) and
                outcome['report']['R'] == 504 and outcome['report']['width_inventory'] == widths and
                helper_widths(outcome, builder) == widths,
                'word endpoint or width data changed')
        require(builder.symstate([e[:-1] for e in outcome['B']]) ==
                builder.symstate([e[:-1] for e in word['B']]), 'B scalar map differs')
        local = local_profile(outcome)
        require(sum(local.values()) > 0, 'empty local profile')
        size = len(groups)
        profiles_by_size[size].append(local)
        subset_rows.append({'mask': mask, 'groups': [list(group) for group in groups],
                            'word_sha256': builder.csha(outcome),
                            'local_profile': {str(r): n for r, n in sorted(local.items())}})
    require(subset_rows[0]['word_sha256'] == recipe['frames_741_source']['frames_only_output_sha'],
            'PR741 baseline output pin differs')
    require(subset_rows[-1]['word_sha256'] == recipe['expected']['output_content_sha256'],
            'PR799 full output pin differs')
    profiles = []
    for j in range(5):
        require(len(profiles_by_size[j]) == (1, 4, 6, 4, 1)[j], 'subset count differs')
        require(all(row == profiles_by_size[j][0] for row in profiles_by_size[j]),
                'same-size subsets have different profiles')
        profiles.append(profiles_by_size[j][0])
    require(profiles[4] == {int(r): n for r, n in recipe['expected']['local_profile'].items()},
            'full local profile differs')
    global_profiles = check_profile_family(profiles, selected_global, idle, calls)
    moment = load(root / (ENGINES + 'moment.py'), 'moment')
    base_two = load(root / (ENGINES + 'base_two_moment.py'), 'base_two_moment')
    brackets = exact_brackets(global_profiles, sources, moment, base_two)
    arithmetic = arithmetic_result(brackets)
    return {'status': 'PASS_X4_PROFILE_ADDITIVE_IDEAL_KAPPA_NONADDITIVE',
            'scope': 'Finite 16-subset raw-word and exact unsurcharged ideal arithmetic audit; selected outer kappa unchanged.',
            'source_sha256': sources['files'], 'baseline_content_sha256': digest(json.dumps(word, sort_keys=True, separators=(',', ':')).encode()),
            'helper_width_inventory': widths,
            'subsets': subset_rows,
            'global_profiles': [{str(r): n for r, n in p.items()} for p in global_profiles],
            'root_brackets': brackets, **arithmetic}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', type=Path, default=HERE / 'SOURCES.json')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check', type=Path, help='Compare the regenerated receipt with a saved JSON receipt')
    args = parser.parse_args()
    result = verify(manifest=args.sources)
    payload = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.check:
        require(result == read_json(args.check), 'saved receipt differs from regenerated audit')
    if args.output:
        args.output.write_text(payload)
        print(result['status'], 'written to', args.output)
    elif args.check:
        print(result['status'], 'saved receipt matches')
    else:
        print(payload, end='')


if __name__ == '__main__':
    main()

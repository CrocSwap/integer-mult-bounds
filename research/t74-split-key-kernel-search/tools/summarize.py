"""Recompute RESULTS.json from the package data (and PR1957's A-section sample).  usage: summarize.py [--check]"""
import json, re, sys
from collections import Counter
from pathlib import Path
PKG = Path(__file__).resolve().parents[1]
PR1957 = PKG.parent / 't74-k554-local-exhaustion'
DATA = PKG / 'data'


def log_status():
    """CP status per job from the search logs (runs made before the tool wrote cp_status into its JSON)."""
    st = {}
    for f in sorted((DATA / 'logs').glob('*.txt')):
        cur = None
        for line in f.read_text().splitlines():
            m = re.match(r"dels \[\('([AB])', (\d+)\)\]", line)
            if m: cur = (f.name.split('-')[0], m.group(1) + m.group(2)); continue
            if line.startswith('stop ') and cur: st[cur] = line.split()[1]
            m = re.match(r"SUMMARY \[\('([AB])', (\d+)\)\] ddel (-?\d+) shape (\w+) nsol (\d+)", line)
            if m and cur:
                if m.group(4) == 'False': st[cur] = 'SHAPE_INFEASIBLE'
                st.setdefault(cur, 'SOLUTION_LIMIT')
    return st


def search_rows(kind, st):
    out = []
    for f in sorted((DATA / kind).glob('sk-*.json')):
        d = json.loads(f.read_text()); job = f.stem[3:]
        exact = [r for r in d['res'] if r.get('status') == 'ok']
        out.append(dict(job=job, ddel=d['ddel'], keys=len(d['keys']), candidates=d['ncand'], shape=d['shape'],
                        cp_status=d.get('cp_status') or st.get((kind, job)),
                        solutions=len(d['res']), exact_solutions=len(exact),
                        best_exact_delta=min((r['delta'] for r in exact), default=None),
                        exact_profit=[r['delta'] for r in exact if r['delta'] < 0]))
    return out


def main():
    rest = json.loads((DATA / 'relaxation-A-rest.json').read_text())
    samp = json.loads((PR1957 / 'data' / 'relaxation-A-sample.json').read_text())
    assert not set(rest) & set(samp)
    allr = {int(k): v for k, v in {**samp, **rest}.items()}
    assert sorted(allr) == list(range(len(allr))), 'A relaxation must cover every A gate exactly once'
    hist = Counter(v['delta'] for v in allr.values() if v.get('delta', 0) < 0)
    st = log_status()
    strict = search_rows('strict', st); diag = search_rows('diagnostic', st); ctl = search_rows('control', st)
    sampled = {int(k) for k in samp}
    r6763 = sorted(i for i, v in allr.items() if v.get('delta') == -6763)
    r8857 = sorted(i for i, v in allr.items() if v.get('delta') == -8857)
    res = dict(
        status='NO_SPLIT_KEY_KERNEL_FOUND_IN_SEARCHED_DOMAIN',
        words=dict(base='research/t74-k554-local-exhaustion/inputs/gauge44-word-566.json.gz',
                   control='research/t74-k554-local-exhaustion/inputs/step0-gauge44.json.gz'),
        a_section_relaxation=dict(
            gates=len(allr), new_in_this_package=len(rest), from_pr1957_sample=len(samp),
            statuses=dict(Counter(v.get('status', 'ok') for v in allr.values())),
            gain_histogram={str(k): hist[k] for k in sorted(hist)},
            cold_pivot_precancels_6763=dict(gates=r6763, searched_by_pr1957=sorted(set(r6763) & {1220, 1226, 1232, 1238, 1244}),
                                            first_priced_here=sorted(set(r6763) - sampled)),
            reads_8857=dict(gates=r8857, first_priced_here=sorted(set(r8857) - sampled))),
        strict_searches=dict(
            jobs=len(strict), proven_infeasible=sum(r['cp_status'] == 'INFEASIBLE' for r in strict),
            shape_infeasible=sum(r['cp_status'] == 'SHAPE_INFEASIBLE' for r in strict),
            other=[r['job'] for r in strict if r['cp_status'] not in ('INFEASIBLE', 'SHAPE_INFEASIBLE')],
            exact_profitable=[r for r in strict if r['exact_profit']], rows=strict),
        diagnostic_searches=diag,
        positive_control=ctl)
    out = json.dumps(res, indent=1) + '\n'
    if '--check' in sys.argv:
        assert (PKG / 'RESULTS.json').read_text() == out, 'RESULTS.json differs from the recomputed summary'
        print('PASS_RESULTS_RECOMPUTED')
    else:
        (PKG / 'RESULTS.json').write_text(out); print('wrote RESULTS.json')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Rebuild the positive-frame cloned skip-prefix producers and check them.

1. Build PR #53's skip-prefix DAG (research/skip-strips/skip_graph.py).
2. Envelope carriers (scripts/partial_swap/match_exported_dag.cpp) and PR #51's
   backward-positive labels (scripts/partial_swap/positive.py).
3. PR #51's paid whole-chain clone rounds (pr51/positive_clone_search.py,
   limit 4, policy 'late', seed 104729+1000003*round) with PR #51's rank-node
   matcher (mode 2) after each round, until no clone remains.
4. Assert the final DAG and label digests (pins.json).
5. Profile the pinned optimal matching (links-{h}.uses) in the fixed I+J basis
   with tools/cprof.cpp (c=1) and compare with profiles-{h}.json.
6. PR #51's independent compiler check_compiled_witness on the pinned matching.
Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
"""
import argparse, hashlib, importlib.util, json, os, struct, subprocess, sys, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT/'scripts')); sys.path.insert(0, str(HERE/'pr51'))
from partial_swap.graph import export
from partial_swap.positive import run as positive_labels
import positive_clone_search as PCS
from check_compiled_witness import check, read_dag, read_labels
_s = importlib.util.spec_from_file_location('pr53_skip_graph', ROOT/'research/skip-strips/skip_graph.py')
SG = importlib.util.module_from_spec(_s); _s.loader.exec_module(SG)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

def cc(src, out, inc=True):
    subprocess.run(['c++', '-O3', '-std=c++17', '-include', 'algorithm', '-I', str(ROOT/'scripts/partial_swap'), str(src), '-o', str(out)], check=True)

def match(mrn, dag, seed, out):
    r = json.loads(subprocess.run([str(mrn), str(dag), str(dag)+'.positive', str(seed), '2', str(out)], capture_output=True, text=True, check=True).stdout)
    r.update(dag_path=str(dag), witness_path=str(out), dag_sha256=PCS.digest(dag), positive_sha256=PCS.digest(str(dag)+'.positive'), witness_sha256=PCS.digest(out), schedule='rank-node')
    return r

def histogram(row, links, h):
    hh, v, n, q, args, core, cover, roots, kinds, active = read_dag(row['dag_path']); ranks, frames = read_labels(row['dag_path']+'.positive', h, n)
    deg = [0]*n
    for x in range(1, n):
        if active[x] and args[2*x]: deg[args[2*x]] += 1; deg[args[2*x+1]] += 1
    for r in roots: deg[r] += 1
    hist = [0]*(h+1)
    for x in range(1, n):
        if not active[x]: continue
        r = ranks[x]
        if args[2*x]:
            hist[r] += deg[x]-1; hist[h-r] += 1
            for y in (args[2*x], args[2*x+1]): hist[r-ranks[y]] += 1
        else: hist[1] += deg[x]
    for j in range(q):
        r = ranks[roots[j]]
        if kinds[j]: hist[r] += 1; hist[h] += 1
        else: hist[h-1-r] += 1; hist[1] += 1
    for d, u in links:
        t = roots[u & 0x7fffffff] if u >> 31 else u//2; val = t if u >> 31 else args[2*t+(u & 1)]
        ru, rv, rt = ranks[d], ranks[val], ranks[t]; hist[h-ru] -= 1; hist[rv] -= 1; hist[rt-rv] -= 1; hist[rt-ru] += 1
    return hist

def run(work):
    pins = json.loads((HERE/'pins.json').read_text())
    mexp, mrn, cprof = work/'mexp', work/'mrn', work/'cprof'
    cc(ROOT/'scripts/partial_swap/match_exported_dag.cpp', mexp); cc(HERE/'pr51/moment_match_rank_node.cpp', mrn); cc(HERE/'tools/cprof.cpp', cprof)
    receipt = {}
    for h in (23, 25):
        dag = work/f'h{h}.bin'; export(SG.graph(h), dag)
        subprocess.run([str(mexp), str(dag), str(dag)+'.links'], capture_output=True, text=True, check=True)
        positive_labels(str(dag))
        row = match(mrn, dag, 1, work/f'links{h}.json'); start_R = row['R']; rounds = []
        for i in range(8):
            jobs, diag, order, frames = PCS.opportunities(row, 4, 'late', 104729+1000003*i)
            if not jobs: break
            t = work/f'h{h}-clone-{i+1}'; d, _ = PCS.rewrite(row, jobs, order, frames, t)
            new = match(mrn, d, 104729+i, t/'selected-links.json'); rounds.append(dict(round=i+1, clones=len(jobs), R=new['R'])); row = new
        p = pins[str(h)]
        assert sha(row['dag_path']) == p['dag_sha256'] and sha(row['dag_path']+'.positive') == p['positive_sha256'], 'Final DAG/labels differ from pins'
        out = work/f'profile-{h}.json'
        subprocess.run([str(cprof), row['dag_path'], str(HERE/f'links-{h}.uses'), '1', '1', str(out)], check=True)
        assert json.loads(out.read_text()) == json.loads((HERE/f'profiles-{h}.json').read_text()), 'Profile differs from pin'
        raw = (HERE/f'links-{h}.uses').read_bytes(); n, k = struct.unpack_from('<2I', raw)
        links = [list(struct.unpack_from('<2I', raw, 8+8*i)) for i in range(k)]
        r2 = dict(row); r2['histogram'] = histogram(row, links, h); r2['matched'] = k; r2['R'] = r2['c']+r2['q']-k
        audit = check({'producer': r2, 'selected_links': {'links': links}}, False)
        print(f'PASS h={h} R {start_R} -> {r2["R"]} after {len(rounds)} clone rounds; digests, profile and PR #51 compiler check', flush=True)
        receipt[str(h)] = dict(start_R=start_R, rounds=rounds, final_R=r2['R'], matched=k, dag_sha256=p['dag_sha256'], positive_sha256=p['positive_sha256'],
                               compiler=audit.get('status'))
    return receipt

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--work-dir', type=Path); ap.add_argument('--output', type=Path); a = ap.parse_args()
    if a.work_dir: a.work_dir.mkdir(parents=True, exist_ok=True); r = run(a.work_dir)
    else:
        with tempfile.TemporaryDirectory(prefix='positive-skip-') as d: r = run(Path(d))
    if a.output: a.output.write_text(json.dumps(r, indent=2, sort_keys=True)+'\n')

#!/usr/bin/env python3
"""Parallel genetic search over paired-cube complex-word configurations, scored by the open generator.

Copyright 2026 Joel Pulikkan (GamingPuzzled). Apache-2.0. Prepared with Anthropic Claude assistance.

A configuration selects the restricted triple coordinates (tk), the all-but-one module (abo) and the output
merge.  Each one is built with PR161's graph and module code, compiled with open carrier matching, gauged by
PR161's selector and scored by generator.optimize, which runs PR161's physical checker.  Search scores use
replay=False for speed; reproduce.py re-checks a configuration with the exact replay.

    python3 search.py --generations 12 --jobs 6        # memory: about 2.6 GB per worker once caches are warm
    python3 search.py --evaluate '{"abo": "cyclic"}'
"""
import argparse
import contextlib
import io
import json
import random
import sys
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import generator                                    # installs the shared basis cache first
from paired_cube.graph import Graph
from paired_cube.modules import restricted_triples_from, pair_module_from, all_but_one, merge_outputs
from paired_cube.gauges import select
import frames_open
import modules_open

SRC = generator.ROOT / 'references/paired-cube/sources'
PR161 = dict(tk=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 16], abo='tree', merge='w02')
DIAGNOSTICS = ('numerical_complex_root', 'status', 'gauge_selection', 'gauge_cost_rejections', 'gauge_trial_saving')


def build(cfg):
    cfg = dict(PR161, **cfg)
    abo = {'tree': lambda: all_but_one(9), 'prefsuf': lambda: modules_open.prefix_suffix(9),
           'cyclic': lambda: modules_open.cyclic(9), 'split': lambda: modules_open.tree_split(9, cfg.get('frac', 0.4))}
    G = Graph(11)
    g = G.finish(restricted_triples_from(SRC / 'h20_g1.json.gz', cfg['tk']),
                 pair_module_from(SRC / 'pmod_C35_5.483127e-4.json', 10), abo[cfg['abo']]())
    if cfg['merge'] != 'none':
        g = merge_outputs(g, G, cfg['merge'])
    g['matching_frames'] = 'coordinate'
    return g


def evaluate(cfg, frozen_arcs=None, passes=2, replay=False):
    """Float complex saving of a configuration (-1 if any stage rejects it) and the checker result."""
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            g = build(cfg)
            base, wit = frames_open.compile_graph(g, frozen_arcs)
            record, word = select(g, base, wit)
            record = json.loads(json.dumps(record))
            for key in DIAGNOSTICS:
                record.pop(key, None)
            saving, res = generator.optimize(g, wit, word, record, passes=passes, replay=replay)
        return dict(cfg=cfg, saving=saving, R=record['R'], W=res['W_per_vertex'], pairs=res['pairs'])
    except Exception as e:                           # a rejected candidate scores -1; the reason is kept
        return dict(cfg=cfg, saving=-1, error=repr(e)[:300])


def key(c):
    return json.dumps([c['tk'], c['abo']])


def mutate(c, rng):
    c = json.loads(json.dumps(c))
    for _ in range(rng.choice([1, 1, 2])):
        if rng.random() < 0.85:
            out = rng.choice(c['tk']); new = rng.choice([x for x in range(20) if x not in c['tk']])
            c['tk'] = sorted([x for x in c['tk'] if x != out] + [new])
        else:
            c['abo'] = rng.choice(['cyclic', 'tree', 'prefsuf'])
    return c


def cross(a, b, rng):
    both = sorted(set(a['tk']) & set(b['tk']))
    rest = [x for x in sorted(set(a['tk']) | set(b['tk'])) if x not in both]
    return dict(tk=sorted(both + rng.sample(rest, len(a['tk']) - len(both))), abo=rng.choice([a['abo'], b['abo']]))


def ga(generations, jobs, seed, population=20, elite=6):
    rng = random.Random(seed); cache = {}
    start = dict(tk=PR161['tk'], abo='cyclic')
    pop = [start] + [mutate(start, rng) for _ in range(population - 1)]
    with Pool(jobs) as pool:                         # workers persist, so the frame caches stay warm
        for gen in range(generations):
            todo = [c for c in pop if key(c) not in cache]
            for c, r in zip(todo, pool.map(evaluate, todo)):
                cache[key(c)] = r['saving']
            ranked = sorted(pop, key=lambda c: -cache[key(c)])
            print(json.dumps(dict(generation=gen, best=cache[key(ranked[0])], cfg=ranked[0], evaluated=len(cache))), flush=True)
            parents = ranked[:elite]; kids = []
            while len(kids) < population - elite:
                c = mutate(cross(*rng.sample(parents, 2), rng), rng) if rng.random() < 0.6 else mutate(rng.choice(parents), rng)
                if key(c) not in cache and c not in kids:
                    kids.append(c)
            pop = parents + kids
    return ranked[0], cache[key(ranked[0])]


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--generations', type=int, default=12)
    p.add_argument('--jobs', type=int, default=6)
    p.add_argument('--seed', type=int, default=11)
    p.add_argument('--evaluate', help='score one JSON configuration and exit')
    a = p.parse_args()
    if a.evaluate:
        print(json.dumps(evaluate(json.loads(a.evaluate))))
        return
    best, saving = ga(a.generations, a.jobs, a.seed)
    print(json.dumps(dict(final=best, saving=saving)))


if __name__ == '__main__':
    main()

"""PR70/76 fixed-cardinality profile-cost carry exchanges, reusable adapter.

Method: Alejandro Zarzuelo Urdiales (PR70). This implementation is adapted
from Dominik Scholz's PR76 run.py at 2333abcea79793fe301b479a7c971cc2be45596c.
Integration with balanced split graphs: huxint with OpenAI Codex assistance.
All inherited Apache-2.0 notices remain applicable. A discovery heuristic;
literal replay and the full exact profile determine correctness and saving.
"""
import json
from pathlib import Path
import struct
import subprocess
from binary_frame_math import logs


def install(compiler, h, work, passes, two_cycles=False, two_paths=False):
    original = compiler.match
    def matching(blocks, uses, enabled):
        result = original(blocks, uses, enabled)
        edges, chosen, right, stats = result
        cardinality = len(chosen)
        if not passes:
            return result
        owner = {x: g for g, b in enumerate(blocks) for x in b['nodes']}
        path = Path(work)/'matching-oracle.bin'
        with path.open('wb') as stream:
            stream.write(struct.pack('<6I2Q', h, h*(h-1)*(h-2)//6, 0, len(blocks)+2, 0, 0, h*(h-1), h*(h-1)))
            stream.write(struct.pack('<2QI', 0, 0, 0))
            stream.write(struct.pack('<2QI', 0, 0, h))
            for b in blocks:
                stream.write(struct.pack('<2QI', *compiler.oracle_frame(b['frame']), b['rank']))
        oracle = subprocess.Popen([compiler.ORACLE_EXE, str(path)], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, text=True, bufsize=1)
        weights = [0]+[int(t*sum(logs(t))*10**30//2) for t in range(1, h+1)]
        cache = {}
        def entropy(x, y):
            if (x, y) not in cache:
                oracle.stdin.write(f'{x} {y}\n'); oracle.stdin.flush()
                line = oracle.stdout.readline(); assert line
                values = list(map(int, line.split())); assert len(values) == h+1
                cache[x, y] = sum(n*w for n, w in zip(values, weights))
            return cache[x, y]
        try:
            prices = []
            for j, (g, u, i) in enumerate(edges):
                provider = owner[blocks[g]['inputs'][i]]
                target = uses[u][1]
                prices.append(-entropy(g+2, target+2)+entropy(g+2, 1)+
                              entropy(0, provider+2)+entropy(provider+2, target+2))
                if j % 20000 == 0:
                    print('CARRY_PRICES', h, j, len(edges), flush=True)
        finally:
            oracle.stdin.close()
            assert oracle.wait() == 0
        priority = sorted(range(len(edges)), key=lambda e: (prices[e], edges[e]))
        by_group_use = {(g, u): e for e, (g, u, _) in enumerate(edges)}
        assert len(by_group_use) == len(edges)
        by_group = {}
        for e in priority:
            by_group.setdefault(edges[e][0], []).append(e)
        initial = sum(prices[e] for e in chosen)
        def can(e, drop=None):
            g, u, i = edges[e]
            rows = blocks[g]['outbasis']+[1 << edges[f][2] for f in blocks[g]['selected'] if f != drop]
            return compiler.independent(compiler.basis(rows), 1 << i)
        for phase in range(passes):
            changed = 0
            for e in priority:
                if e in chosen:
                    continue
                g, u, i = edges[e]
                f = right.get(u)
                if f is not None:
                    if prices[e] >= prices[f] or not can(e, f if edges[f][0] == g else None):
                        continue
                else:
                    f = next((z for z in sorted(blocks[g]['selected'], key=lambda z: (-prices[z], z))
                              if prices[e] < prices[z] and can(e, z)), None)
                    if f is None:
                        continue
                fg, fu, _ = edges[f]
                chosen.remove(f); blocks[fg]['selected'].remove(f); del right[fu]
                chosen.add(e); blocks[g]['selected'].add(e)
                assert u not in right
                right[u] = e
                changed += 1
            cycles = 0
            paths = 0
            if two_cycles or two_paths:
                # Replace two selected edges simultaneously. Each region loses
                # its own old row before gaining the other eligible input row.
                # Both occupied right uses remain unique, and cardinality is fixed.
                for e in priority:
                    if e in chosen:
                        continue
                    g, u, _ = edges[e]
                    f = right.get(u)
                    if f is None:
                        continue
                    other = edges[f][0]
                    if other == g:
                        continue
                    options = []
                    for old in blocks[g]['selected'] if two_cycles else ():
                        old_use = edges[old][1]
                        partner = by_group_use.get((other, old_use))
                        if partner is None or partner in chosen:
                            continue
                        gain = prices[old]+prices[f]-prices[e]-prices[partner]
                        if gain > 0:
                            options.append((-gain, old, partner))
                    if two_paths:
                        old = next((z for z in sorted(blocks[g]['selected'], key=lambda z: (-prices[z], z))
                                    if can(e, z)), None)
                        if old is not None:
                            for partner in by_group[other]:
                                if prices[e]+prices[partner] >= prices[old]+prices[f]:
                                    break
                                if edges[partner][1] in right:
                                    continue
                                if can(partner, f):
                                    options.append((prices[e]+prices[partner]-prices[old]-prices[f], old, partner))
                                    break
                    for _, old, partner in sorted(options):
                        if not can(e, old) or not can(partner, f):
                            continue
                        old_use = edges[old][1]
                        chosen.remove(old); chosen.remove(f)
                        blocks[g]['selected'].remove(old)
                        blocks[other]['selected'].remove(f)
                        chosen.add(e); chosen.add(partner)
                        blocks[g]['selected'].add(e)
                        blocks[other]['selected'].add(partner)
                        del right[u]; del right[old_use]
                        partner_use = edges[partner][1]
                        assert partner_use not in right and partner_use != u
                        right[u] = e; right[partner_use] = partner
                        if partner_use == old_use:
                            cycles += 1
                        else:
                            paths += 1
                        break
            stats['carried_signal_exchanges'] += changed
            stats['two_region_exchange_cycles'] += cycles
            stats['two_region_exchange_paths'] += paths
            print('CARRY_EXCHANGES', h, phase, changed, 'cycles2', cycles, 'paths2', paths, flush=True)
            if not changed and not cycles and not paths:
                break
        assert len(chosen) == len(right) == cardinality
        for b in blocks:
            assert len(compiler.basis(b['outbasis']+[1 << edges[e][2] for e in b['selected']])) == len(b['outbasis'])+len(b['selected'])
        stats['exchange_entropy_gain_1e30'] = initial-sum(prices[e] for e in chosen)
        stats['exchange_profile_pairs'] = len(cache)
        (Path(work)/'matching.json').write_text(json.dumps(dict(edges=edges, chosen=sorted(chosen), stats=dict(stats)), separators=(',', ':'))+'\n')
        return edges, chosen, right, stats
    compiler.match = matching

"""First support-span drop while preserving a complete P104 frame puncture."""
import importlib.util
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source():
    require(not sys.flags.optimize, 'Pinned predecessor model requires assertions enabled')
    pins = json.loads((ROOT / 'SOURCES.json').read_text())
    path = ROOT / 'sources/PR968-verify.py'
    require(hashlib.sha256(path.read_bytes()).hexdigest() == pins['files']['sources/PR968-verify.py']['sha256'],
            'predecessor model source pin mismatch')
    spec = importlib.util.spec_from_file_location('pinned_pr968', ROOT / 'sources/PR968-verify.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run():
    model = source()
    cuts = []
    for a in range(120):
        support = model.support_mask(model.LINES[a]) & ~(1 << a)
        entries = {}
        for lam, violations in model.VMASK.items():
            cut = support & violations
            if cut:
                entries.setdefault(cut, lam)
        require(len(entries) == 255, 'support does not have 255 hyperplane cuts')
        cuts.append(tuple(sorted(entries.items())))
    frames = model.frames_in(model.P112)
    histogram = Counter()
    global_min = 120
    witness = None
    frame_records = []
    pair_count = 0
    edge_histogram = Counter()
    for f1 in frames:
        # PR968 identifies the inadmissible class by four shared neighbours.
        if any(sum(bool(model.IP[g][f]) and bool(model.IP[h][f]) for f in model.FRAME0) == 4
               for index, g in enumerate(f1) for h in f1[index + 1:]):
            continue
        base = model.mask(model.FRAME0 + list(f1))
        support_min = 120
        for a in model.FRAME0 + list(f1):
            for cut, lam in cuts[a]:
                added = cut & ~base
                cost = added.bit_count()
                support_min = min(support_min, cost)
        solutions = model.frame_pair_solutions(model.FRAME0, list(f1))
        require(len(solutions) == 8, 'frame admission differs from exact dual solutions')
        edges = sorted({tuple(sorted(pair)) for pairs in solutions for pair in pairs})
        require(len(edges) == 32, 'unexpected root-pair inventory')
        local_min, local_hits = 120, []
        for a, b in edges:
            edge_min = 120
            for normal, partner in ((a, b), (b, a)):
                admitted = 0
                for cut, lam in cuts[normal]:
                    if (lam & model.PHI[partner]).bit_count() & 1:
                        continue
                    admitted += 1
                    added = cut & ~base
                    cost = added.bit_count()
                    edge_min = min(edge_min, cost)
                    if cost < local_min:
                        local_min, local_hits = cost, [(normal, partner, lam, added)]
                    elif cost == local_min:
                        local_hits.append((normal, partner, lam, added))
                require(admitted == 127, 'quotient does not have 127 hyperplane cuts')
            edge_histogram[edge_min] += 1
        pair_count += len(solutions)
        histogram[local_min] += 1
        frame_records.append({'frame': list(f1), 'minimum_added': local_min,
                              'first_support_span_drop': support_min,
                              'minimum_quotient_cuts': len(local_hits)})
        if local_min < global_min:
            global_min, witness = local_min, None
        if local_min == global_min and witness is None:
            # The seed rotates the choice of attaining normal; coverage stays
            # exhaustive and independent of this deterministic witness tie rule.
            for a, b, lam, added in sorted(local_hits, key=lambda h: ((h[0]-46) % 120, h[1], h[2])):
                puncture = base | added
                live = [i for i in range(120) if not (puncture >> i & 1)]
                for pairs in solutions:
                    if tuple(sorted((a, b))) not in [tuple(sorted(pair)) for pair in pairs]:
                        continue
                    exact, ranks = model.pair_decoder(pairs, live)
                    require(exact, 'decoder lost exact duality')
                    if min(ranks) < 7:
                        witness = {'frame0': list(model.FRAME0), 'frame1': list(f1),
                                   'normal': a, 'partner': b, 'functional': lam,
                                   'added_punctures': [i for i in range(120) if added >> i & 1],
                                   'pairs': [list(pair) for pair in pairs], 'ranks': ranks,
                                   'live_ports': len(live), 'copy_cost': sum(ranks),
                                   'side_span': model.span_dim([i for i in live if model.IP[a][i]])}
                        break
                if witness:
                    break
    require(len(frame_records) == 896 and pair_count == 7168, 'family coverage mismatch')
    require(witness is not None, 'support threshold not attained by a COPY rank drop')
    require(edge_histogram == Counter({22: 896 * 32}), 'term threshold is not uniformly 22')
    f0, f1 = witness['frame0'], witness['frame1']
    base = model.mask(f0 + f1)
    span_control = None
    for a in f0 + f1:
        for cut, lam in cuts[a]:
            added = cut & ~base
            if added.bit_count() != 20:
                continue
            live = [i for i in range(120) if not ((base | added) >> i & 1)]
            exact, ranks = model.pair_decoder(witness['pairs'], live)
            require(exact and ranks == [7] * 8, 'span-only control accidentally changed COPY cost')
            span_control = {'normal': a, 'functional': lam,
                            'added_punctures': [i for i in range(120) if added >> i & 1],
                            'side_span': model.span_dim([i for i in live if model.IP[a][i]]),
                            'ranks': ranks, 'live_ports': len(live)}
            break
        if span_control:
            break
    require(span_control and span_control['side_span'] == 7, 'missing span-only control')
    digest = hashlib.sha256(json.dumps(frame_records, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return {'format': 'p104-first-copy-drop/1', 'assignment_seed': 46,
            'base_commit': 'c0e3631dc24e3c24a861f7d3d79e0608481cccec',
            'frames_in_p112': len(frames), 'admissible_frames': len(frame_records),
            'exact_decoders': pair_count, 'normal_hyperplanes': 255,
            'support_cut_evaluations': 896 * 16 * 255,
            'quotient_cut_evaluations': 896 * 32 * 2 * 127,
            'frame_minimum_histogram': dict(sorted(histogram.items())),
            'term_minimum_histogram': dict(sorted(edge_histogram.items())),
            'first_extra_punctures': global_min, 'first_total_punctures': 16 + global_min,
            'frame_records_sha256': digest, 'frame_records': frame_records,
            'witness': witness, 'span_only_control': span_control}


if __name__ == '__main__':
    if len(sys.argv) == 2 and Path(sys.argv[1]).exists():
        raise FileExistsError('Use a fresh output path; existing files are preserved')
    result = run()
    if len(sys.argv) == 2:
        with Path(sys.argv[1]).open('x', encoding='utf-8', newline='\n') as f:
            f.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('frame_records','witness')}))
    print('WITNESS', json.dumps(result['witness']))

"""PR #495's retimed kernel complex word (Ali Romman; PR #449 kernel, PR #458 paid residual adapters) in PR #433/#442's
compressed nine-stage template (m = 73, eight replicas), every helper residual hosted on idle data coordinates:
  * width-9 residuals on PR #448's cross-copy tape (owner [3, child, offset] whole, [5, child, o1, w1, family2, o2, w2]
    split across two copies of the same child), or whole on a pattern copy ([3, child, offset]);
  * the 79 entering (width-8) residuals whole on pattern copies with PR #495's paid two-sided residual adapters and route
    chart (owner [4, child, offset, width, entrance frame, axes]); such a helper is the only owner of its family in its call.
usage: complex_retimed9.py PARENT_SPLIT_CENTRES DATA_PHASES.json LOCAL_DIR OUT [--discover]
  PARENT_SPLIT_CENTRES: PR #442 replay output parent/changed/split-centres (PR #433's nine-stage template)
  DATA_PHASES.json:     parent/changed/work/complex-nine-native/DATA-PHASES.json (bound by the template's hash)
  LOCAL_DIR:            the word-level outputs of PR #495's vendored scripts (CANONICAL-WORD, LOCAL-REVIEW, ADAPTED-PROGRAMS, ...)
  --discover:           recompute the frozen selection (SELECTION.json) with scipy/HiGHS"""
import copy, gzip, hashlib, json, sys, time
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import hybrid_core as HY
V, K, T, L, M, H, R = 120, 4, 8, 9, 73, 9, 560
DATA = 2 * K * V * T
blob = lambda x: json.dumps(x, sort_keys=True, separators=(',', ':')).encode()
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
ld = lambda p: json.loads(gzip.decompress(Path(p).read_bytes())) if str(p).endswith('.gz') else json.loads(Path(p).read_text())

def windows(t):
    """Per idle child (one side of one idle pair): (pair, rank, stages strictly inside its window and off its pair)."""
    rank = {}
    for it in t['idle_children']:
        rank.setdefault(it['child'], it['rank']); assert rank[it['child']] == it['rank'] and it['replicas'] == T
    pair_of_stage = {e['stage']: e['pair'] for e in t['recipe'] if e['kind'] == 'local'}
    last = {}; seen = []; win = {}; side_of = {}; pair_of = {}
    for pos, e in enumerate(t['execution_schedule']):
        if e['kind'] == 'local_cover_sweep': p = pair_of_stage[e['stage']]; seen.append((pos, e['stage'], p)); last[p] = pos
        elif e['kind'] == 'bridge': last[e['dst']] = pos; last[e['src']] = pos
        elif e['kind'] == 'idle_cover_sweep':
            for sd, ch in enumerate(e['child_indices']):
                if ch not in rank: continue
                side_of[ch] = sd; pair_of[ch] = e['pair']; lo = last.get(e['pair'], -1)
                st = frozenset(s for q, s, pp in seen if lo < q < pos and pp != e['pair'])
                if rank[ch] > 0 and st: win[ch] = (e['pair'], rank[ch], st)
    seen_k = {}
    for ch, (p, r, st) in win.items():          # children of one (pair, side) share their families: windows must be disjoint
        for s in st:
            kk = (p, side_of[ch], s); assert kk not in seen_k, ('windows overlap', ch, seen_k[kk]); seen_k[kk] = ch
    return win, side_of, pair_of, rank

def port_bases(ports):
    """PR #495's exact idle basis U_q followed by the exterior coordinates (emit.py), here in dimension 73."""
    out = []
    for q in ports:
        z = next(i for i in range(H) if not (q >> i & 1)); a = q ^ (1 << z); order = list(range(H)); order[0], order[z] = order[z], order[0]
        out.append([(1 << i) ^ (a if a >> i & 1 else 0) for i in order] + [1 << i for i in range(H, M)])
    return out

def main(src, php, local, out, discover):
    t0 = time.monotonic(); out.mkdir(parents=True, exist_ok=False)
    raw = gzip.decompress((src / 'GLOBAL-TEMPLATE.json.gz').read_bytes()); t = json.loads(raw); parent_sha = hashlib.sha256(raw).hexdigest()
    integ = json.loads((src / 'INTEGRATION.json').read_text())
    assert parent_sha == integ['global_template_sha256'] and t['live'] == integ['live'] and t['m'] == M and len(t['calls']) == L * T
    ph = json.loads(Path(php).read_text()); assert sha(php) == t['exact_data_phase_recipe_sha256'] and ph['m'] == M
    word = ld(local / 'CANONICAL-WORD.json.gz'); review = ld(local / 'LOCAL-REVIEW.json'); ad = ld(local / 'RESIDUAL-ADAPTERS.json')
    programs = ld(local / 'ADAPTED-PROGRAMS.json.gz')
    assert review['status'] == 'PASS_INDEPENDENT_COMPLEX_KERNEL_LOCAL_REALIZATION' and review['canonical_word_sha256'] == hashlib.sha256(blob(word)).hexdigest()
    assert review['adapters_sha256'] == sha(local / 'RESIDUAL-ADAPTERS.json') and review['phase_recipes_sha256'] == sha(local / 'CLIFFORD-RECIPES.json')
    assert (word['h'], word['v'], word['R']) == (H, V, R) and [p['q'] for p in ph['recipes']] == word['ports']
    widths = [H - len(word['frames'][word['start'][2 * V + h]]) for h in range(R)]
    entering = [h for h in range(R) if widths[h] < H]; assert all(widths[h] == 8 for h in entering)
    assert all(str(word['start'][2 * V + h]) in ad['recipes'] and ad['recipes'][str(word['start'][2 * V + h])]['rank'] == widths[h] for h in entering)
    win, side_of, pair_of, rank = windows(t)
    wc = Counter(widths); avail = {(s, w): wc[w] for s in range(L) for w in wc}
    selp = out / 'SELECTION.json' if discover else HERE.parent / 'data/SELECTION.json'
    if discover:
        psel, tsel, val = HY.solve(win, V, avail, M)
        selp.write_text(json.dumps(dict(rule='hybrid: pattern copies (whole, distinct stages; every entering residual) + #448 tape (width 9)',
                                        patterns=psel, tape=tsel, objective_proxy=val), indent=1) + '\n')
    sel = json.loads(selp.read_text()); psel, tsel = sel['patterns'], sel['tape']
    slots, rem = HY.expand(win, psel, tsel, widths, L, V)
    assert set(slots) == {(s, h) for s in range(L) for h in range(R)}
    assert all(slots[s, h][1] == 'pattern' and len(slots[s, h][2]) == 1 for s in range(L) for h in entering)
    bases = port_bases(word['ports'])
    def fam(rep, i, port): return rep * 960 + (2 * pair_of[i] + side_of[i]) * V + port
    route = {}
    for (s, h), (i, kind, segs) in slots.items():
        if widths[h] == H: continue
        (cp, off, w), = segs; pending = ph['recipes'][cp]['idle_children'][i]['orthogonal_axes']
        assert ph['recipes'][cp]['idle_children'][i]['rank'] == rank[i]
        axis = [bases[cp].index(x) for x in pending[off:off + w]]; axis += [j for j in range(M) if j not in axis][:H - w]
        assert len(axis) == H and len(set(axis)) == H; route[s, h] = axis
    paid = Counter(); split = 0; digest = hashlib.sha256(); events = wrappers = 0; W = DATA
    prog_sha = {o: hashlib.sha256(blob(programs[o])).hexdigest() for o in programs}
    for c in t['calls']:
        s, rep, p, ori = c['stage'], c['replica'], c['pair'], c['orientation']; own = c['owners'][:2 * V]
        assert own == [[rep * 960 + (2 * p + j // V) * V + j % V, [1, s, j % V]] for j in range(2 * V)]
        for h in range(R):
            i, kind, segs = slots[s, h]; assert pair_of[i] != p and s in win[i][2]
            if widths[h] < H:
                (cp, off, w), = segs; own.append([fam(rep, i, cp), [4, i, off, w, word['start'][2 * V + h], route[s, h]]])
            elif len(segs) == 1:
                (cp, off, w), = segs; own.append([fam(rep, i, cp), [3, i, off]])
            else:
                (p1, o1, w1), (p2, o2, w2) = segs; own.append([fam(rep, i, p1), [5, i, o1, w1, fam(rep, i, p2), o2, w2]]); split += 1
        assert len({(f, json.dumps(r_)) for f, r_ in own}) == 2 * V + R and all(f < W for f, r_ in own)
        fc = Counter(f for f, r_ in own)
        assert all(fc[f] == 1 for f, r_ in own[:2 * V]), 'data families are distinct and host no helper of their own call'
        assert all(fc[own[2 * V + h][0]] == 1 for h in range(R) if slots[s, h][1] == 'pattern'), 'a pattern-hosted helper is alone on its family in its call'
        c['owners'] = own; c['local_program_sha256'] = prog_sha[ori]
        for r_, z in review['checks'][ori]['paid_profile'].items(): paid[int(r_)] += z
        for e in programs[ori]:
            z = copy.deepcopy(e); tag = z[0]
            if tag in ('adapter', 'climb'): z[2] = own[z[2]]
            elif tag == 'residual_adapter':
                f = z[3]; assert f == word['start'][z[2]] and widths[z[2] - 2 * V] < H
                z[2] = own[z[2]]; z.append(ad['recipes'][str(f)][z[1]]); wrappers += 1
            elif tag == 'center': z[1] = [W + z[1], ['private_center', z[1]]]
            elif tag == 'scalar':
                z[1] = [own[x[1]] if isinstance(x, list) and x[0] == 'L' else [W + x[1], ['private_center', x[1]]] if isinstance(x, list) and x[0] == 'C' else x for x in z[1]]
            else: assert tag == 'phase'
            digest.update(blob([s, rep, z]) + b'\n'); events += 1
    newidle = []
    for it in t['idle_children']:
        ch, port = it['child'], it['port']; rr = rem[ch, port] if ch in win else it['rank']
        newidle.append(dict(child=ch, port=port, rank=rr, hosted=it['rank'] - rr, replicas=T))
        if rr: paid[rr] += T
    mass = sum(r * n for r, n in paid.items()); D = M * W - mass; assert D == 2496, D
    assert M * M > 2 * max(paid) ** 2
    centres = len(word['centers']); physical = W + R + centres + 2; assert integ['physical'] - integ['live'] == R + centres + 2
    t.update(version='hamming-mutable-basis-nine-v1+retimed-kernel-pr495+hybrid-cross-copy-hosting', live=W, physical=physical,
             idle_children=newidle, local_programs=programs, residual_adapters=ad,
             exact_local_clifford_recipe_sha256=sha(local / 'CLIFFORD-RECIPES.json'), source_template_sha256=parent_sha,
             source_canonical_word_sha256=hashlib.sha256(blob(word)).hexdigest(),
             private_namespace=dict(centers=[W, W + centres], reserved_tableau=[W + centres, W + centres + R], coefficient=[physical - 2, physical]),
             hosting=dict(windows={str(i): [w[0], w[1], sorted(w[2])] for i, w in sorted(win.items())}, sides={str(k): v for k, v in sorted(side_of.items())},
                          pairs={str(k): v for k, v in sorted(pair_of.items())},
                          slots=[[s, h, i, kind, [list(x) for x in segs]] for (s, h), (i, kind, segs) in sorted(slots.items())], banks=[0] * L,
                          rule='every residual hosted; entering (width-8) residuals whole on pattern copies, alone on their family per call; '
                               'width-9 residuals on pattern copies or on the PR #448 cross-copy tape'),
             residual_route_semantics=dict(
                 owner3='PR #442: whole width-9 residual on the pending interval [offset, offset+9) of the child copy, routed by a coordinate permutation followed by the pending idle basis U_q',
                 owner5='PR #448: width-9 residual split into two pieces on two copies (data families) of the same idle child, each piece on its pending interval',
                 owner4='PR #495/#458: entering residual made coordinate by explicit paid two-sided monomials (pre P_d (R^-1 tensor I) P_d^-1 before the invocation, post P_d (L^-1 tensor I) P_d^-1 after full-frame cleanup); chart: the recorded axes are the child\'s orthogonal pending axes [offset, offset+w) in U_q, then unused basis indices as spectators; identity on all spectator axes; the helper is the only owner of its family in the invocation',
                 monomial_compiler_groups_per_wrapper=8))
    t['route_semantics']['helper'] = 'see residual_route_semantics: owner records 3 and 5 (PR #442/#448 idle-axis hosting) and 4 (PR #495/#458 paid two-sided residual adapters)'
    t['bank_padding']['families'] = []; t['cover_final_correction']['families'] = [0, W]; t['cover_final_correction']['charged_calls_per_cover'] = W
    for e in t['execution_schedule']:
        if e['kind'] == 'bank_padding_cover_sweep': e['families'] = [DATA, W]
        elif e['kind'] == 'translate_every_live_family': e.update(t['cover_final_correction'])
    tb = blob(t); (out / 'GLOBAL-TEMPLATE.json.gz').write_bytes(gzip.compress(tb, mtime=0))
    res = dict(status='PASS_RETIMED_KERNEL_HYBRID_CROSS_COPY_COMPLEX_TEMPLATE', parent_template_sha256=parent_sha, template_sha256=hashlib.sha256(tb).hexdigest(),
               selection_sha256=sha(selp), live=W, physical=physical, global_profile={str(k): v for k, v in sorted(paid.items())}, rank_mass=mass, deficit=D,
               maxchild=max(paid), hosted_residuals=len(slots) * T, split_residuals=split, entering_residuals=len(entering) * L * T,
               pattern_copies=sum(e[2] for e in psel), tape_residuals=sum(e[2] for e in tsel) * T, wrapper_events=wrappers,
               local_events=events, emitted_program_sha256=digest.hexdigest(), source_local_checks=review['checks'],
               source_canonical_word_sha256=hashlib.sha256(blob(word)).hexdigest(), source_local_phase_sha256=sha(local / 'CLIFFORD-RECIPES.json'),
               residual_adapter_sha256=sha(local / 'RESIDUAL-ADAPTERS.json'), data_phase_sha256=sha(php), private_centers=centres,
               seconds=round(time.monotonic() - t0, 1))
    (out / 'HOSTED.json').write_text(json.dumps(res, indent=2) + '\n')
    print(json.dumps({k: res[k] for k in ('live', 'maxchild', 'hosted_residuals', 'split_residuals', 'pattern_copies', 'wrapper_events', 'deficit', 'global_profile')}))

if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    main(Path(a[0]), Path(a[1]), Path(a[2]), Path(a[3]), '--discover' in sys.argv)

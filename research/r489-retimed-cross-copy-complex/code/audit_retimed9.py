"""Independent audit of the hybrid cross-copy hosted nine-stage template of PR #495's retimed kernel complex word.
Shares no code with complex_retimed9.py or hybrid_core.py.  From the parent template (PR #433/#442), the exact data phases
and PR #495's local artifacts it re-derives the windows and checks, per replica and invocation: data owners unchanged; every
helper residual has exactly one owner record of the right kind; pieces lie on copies (data families) of the idle child they
name, inside its pending coordinates, pairwise disjoint per (child, copy), with the invocation inside the child's window and
off the active pair; a split piece pair covers the end of one copy and the start of the next; every entering residual is
whole on a pattern copy; a pattern copy holds residuals of pairwise distinct stages only, so each is alone on its family in
its call; PR #495's route chart for entering residuals; program events, wrappers and the paid profile recomputed from the
programs; remainder children exact; live stock, deficit 2496 and the halving bound.  Then mutation controls.
usage: audit_retimed9.py PARENT_SPLIT_CENTRES DATA_PHASES.json LOCAL_DIR TEMPLATE_DIR OUT.json"""
import copy, gzip, hashlib, json, sys
from collections import Counter, defaultdict
from pathlib import Path
V, K, T, L, M, H, R = 120, 4, 8, 9, 73, 9, 560
DATA = 2 * K * V * T
canon = lambda x: json.dumps(x, sort_keys=True, separators=(',', ':')).encode()
digest_of = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):
    p = Path(p); return json.loads(gzip.decompress(p.read_bytes())) if p.name.endswith('.gz') else json.loads(p.read_text())

def derive_windows(parent):
    stage_pair = {}
    for e in parent['recipe']:
        if e['kind'] == 'local': stage_pair[e['stage']] = e['pair']
    rk = {}
    for it in parent['idle_children']: rk[it['child']] = it['rank']
    events = []
    for e in parent['execution_schedule']:
        if e['kind'] == 'local_cover_sweep': events.append(('L', e['stage'], stage_pair[e['stage']]))
        elif e['kind'] == 'bridge': events.append(('B', e['dst'], e['src']))
        elif e['kind'] == 'idle_cover_sweep':
            for sd, ch in enumerate(e['child_indices']): events.append(('I', ch, e['pair'], sd))
    touched = {}; done = []; out = {}; side = {}; pair = {}
    for k, ev in enumerate(events):
        if ev[0] == 'L': done.append((k, ev[1], ev[2])); touched[ev[2]] = k
        elif ev[0] == 'B': touched[ev[1]] = k; touched[ev[2]] = k
        else:
            ch, pr, sd = ev[1], ev[2], ev[3]
            if ch not in rk: continue
            side[ch] = sd; pair[ch] = pr; start = touched.get(pr, -1)
            out[ch] = {s for q, s, pp in done if start < q < k and pp != pr}
    return out, side, pair, rk

def bases_for(ports):
    res = []
    for q in ports:
        pivot = next(j for j in range(H) if not (q >> j) & 1); a = q ^ (1 << pivot)
        order = [pivot if j == 0 else 0 if j == pivot else j for j in range(H)]
        basis = [(1 << j) ^ (a if (a >> j) & 1 else 0) for j in order] + [1 << j for j in range(H, M)]
        assert basis[0] == q and all((u & v).bit_count() % 2 == int(i == j) for i, u in enumerate(basis[:H]) for j, v in enumerate(basis[:H]))
        res.append(basis)
    return res

def program_profile(prog, word):
    prof = Counter(); wr = 0
    for z in prog:
        if z[0] == 'climb': prof[z[5]] += 1
        elif z[0] == 'center': prof[z[4]] += 1
        elif z[0] == 'residual_adapter':
            assert z[3] == word['start'][z[2]] and z[3] and 2 * V <= z[2] < 2 * V + R and z[1] in ('pre', 'post'); wr += 1
    return prof, wr

def validate(t, parent, ph, word, programs, ad, review):
    keep = ['m', 'recipe', 'cover', 'loop_order', 'exact_data_phase_recipe_sha256', 'adapter_policy', 'expanded_scalar_interface']
    for k in keep: assert t[k] == parent[k], ('parent field changed', k)
    assert t['source_template_sha256'] == hashlib.sha256(canon(parent)).hexdigest()
    assert t['local_programs'] == programs and t['residual_adapters'] == ad and t['live'] == DATA
    assert t['physical'] == DATA + R + len(word['centers']) + 2 and t['bank_padding']['families'] == []
    sched_p = [e for e in parent['execution_schedule'] if e['kind'] not in ('bank_padding_cover_sweep', 'translate_every_live_family')]
    sched_t = [e for e in t['execution_schedule'] if e['kind'] not in ('bank_padding_cover_sweep', 'translate_every_live_family')]
    assert sched_p == sched_t
    corr = [e for e in t['execution_schedule'] if e['kind'] == 'translate_every_live_family']
    assert len(corr) == 1 and corr[0]['families'] == [0, DATA] and corr[0]['charged_calls_per_cover'] == DATA == t['cover_final_correction']['charged_calls_per_cover']
    assert t['execution_schedule'][-1]['kind'] == 'translate_every_live_family'
    win, side, pair, rk = derive_windows(parent)
    for ch, st in win.items():                 # children of one (pair, side) never share an invocation
        for ch2, st2 in win.items():
            if ch < ch2 and (pair[ch], side[ch]) == (pair[ch2], side[ch2]): assert not (st & st2)
    widths = [H - len(word['frames'][word['start'][2 * V + h]]) for h in range(R)]
    hs = t['hosting']; cells = defaultdict(set); slot = {}; pat_stage = defaultdict(list); kinds = defaultdict(set)
    for s, h, i, kind, segs in hs['slots']:
        assert 0 <= s < L and 0 <= h < R and (s, h) not in slot and i in win and s in win[i] and rk[i] > 0
        assert kind in ('pattern', 'tape') and 1 <= len(segs) <= 2 and sum(w for _, _, w in segs) == widths[h] and all(w > 0 for _, _, w in segs)
        if widths[h] < H: assert kind == 'pattern'
        if kind == 'pattern': assert len(segs) == 1
        if len(segs) == 2:
            (c1, o1, w1), (c2, o2, w2) = segs; assert c2 == c1 + 1 and o1 + w1 == rk[i] and o2 == 0
        for cp, off, w in segs:
            assert 0 <= cp < V and 0 <= off and off + w <= rk[i]
            new = set(range(off, off + w)); assert not (new & cells[i, cp]), ('overlap', i, cp); cells[i, cp] |= new; kinds[i, cp].add(kind)
            if kind == 'pattern': pat_stage[i, cp].append(s)
        slot[s, h] = (i, kind, [tuple(x) for x in segs])
    assert len(slot) == L * R
    for key, ks in kinds.items(): assert len(ks) == 1, ('pattern and tape on one copy', key)
    for key, st in pat_stage.items(): assert len(st) == len(set(st)), ('two residuals of one invocation on a pattern copy', key)
    bases = bases_for(word['ports']); events = 0; wrappers = 0; prof = Counter(); dig = hashlib.sha256(); split = 0
    pprof = {}
    for o in ('forward', 'backward'):
        pp, wr = program_profile(programs[o], word); assert wr == 158
        assert dict(pp) == {int(r): n for r, n in review['checks'][o]['paid_profile'].items()}, ('program profile', o)
        pprof[o] = (pp, wr)
    assert len(t['calls']) == L * T
    pcalls = {(c['stage'], c['replica']): c for c in parent['calls']}
    for c in t['calls']:
        s, rep, p, ori = c['stage'], c['replica'], c['pair'], c['orientation']; pc = pcalls[s, rep]
        assert (pc['pair'], pc['orientation']) == (p, ori) and c['local_program_sha256'] == hashlib.sha256(canon(programs[ori])).hexdigest()
        own = c['owners']; assert len(own) == 2 * V + R and own[:2 * V] == pc['owners'][:2 * V]
        fams = Counter(f for f, r_ in own); assert all(fams[f] == 1 for f, r_ in own[:2 * V])
        for h in range(R):
            f, rec = own[2 * V + h]; i, kind, segs = slot[s, h]; assert pair[i] != p
            fam = lambda cp: rep * 960 + (2 * pair[i] + side[i]) * V + cp
            if kind == 'pattern': assert fams[f] == 1, ('pattern-hosted helper shares its family in its call', s, rep, h)
            if widths[h] < H:
                (cp, off, w), = segs; assert f == fam(cp) and rec[:5] == [4, i, off, w, word['start'][2 * V + h]] and len(rec) == 6
                axis = rec[5]; assert len(axis) == H and len(set(axis)) == H and all(0 <= a < M for a in axis)
                pend = ph['recipes'][cp]['idle_children'][i]; assert pend['rank'] == rk[i]
                assert [bases[cp][a] for a in axis[:w]] == pend['orthogonal_axes'][off:off + w]
                rest = [a for a in range(M) if a not in axis[:w]]; assert axis[w:] == rest[:H - w]
                assert ad['recipes'][str(word['start'][2 * V + h])]['rank'] == w
            elif len(segs) == 1:
                (cp, off, w), = segs; assert f == fam(cp) and rec == [3, i, off]
            else:
                (c1, o1, w1), (c2, o2, w2) = segs; assert f == fam(c1) and rec == [5, i, o1, w1, fam(c2), o2, w2]; split += 1
        prof.update(pprof[ori][0]); wrappers += pprof[ori][1]
        for z0 in programs[ori]:
            z = copy.deepcopy(z0); tag = z[0]
            if tag in ('adapter', 'climb'): z[2] = own[z[2]]
            elif tag == 'residual_adapter': z[2] = own[z[2]]; z.append(ad['recipes'][str(z[3])][z[1]])
            elif tag == 'center': z[1] = [DATA + z[1], ['private_center', z[1]]]
            elif tag == 'scalar': z[1] = [own[x[1]] if isinstance(x, list) and x[0] == 'L' else [DATA + x[1], ['private_center', x[1]]] if isinstance(x, list) and x[0] == 'C' else x for x in z[1]]
            else: assert tag == 'phase'
            dig.update(canon([s, rep, z]) + b'\n'); events += 1
    remaining = {}
    for it in parent['idle_children']:
        ch, port = it['child'], it['port']; remaining[ch, port] = it['rank'] - len(cells[ch, port])
    got = {(it['child'], it['port']): (it['rank'], it['hosted'], it['replicas']) for it in t['idle_children']}
    assert got == {k: (r_, rk[k[0]] - r_, T) for k, r_ in remaining.items()}
    for k, r_ in remaining.items():
        if r_: prof[r_] += T
    mass = sum(r_ * n for r_, n in prof.items()); assert M * DATA - mass == 2496 and M * M > 2 * max(prof) ** 2
    assert wrappers == 158 * L * T
    return prof, dig.hexdigest(), events, wrappers, split, len(slot) * T

def main():
    psc, php, local, td, outp = map(Path, sys.argv[1:6])
    parent = load(psc / 'GLOBAL-TEMPLATE.json.gz'); ph = load(php); t = load(td / 'GLOBAL-TEMPLATE.json.gz'); hosted = load(td / 'HOSTED.json')
    word = load(local / 'CANONICAL-WORD.json.gz'); programs = load(local / 'ADAPTED-PROGRAMS.json.gz'); ad = load(local / 'RESIDUAL-ADAPTERS.json'); review = load(local / 'LOCAL-REVIEW.json')
    assert digest_of(php) == parent['exact_data_phase_recipe_sha256'] and [r['q'] for r in ph['recipes']] == word['ports']
    assert review['status'] == 'PASS_INDEPENDENT_COMPLEX_KERNEL_LOCAL_REALIZATION' and review['canonical_word_sha256'] == hashlib.sha256(canon(word)).hexdigest()
    assert review['adapters_sha256'] == digest_of(local / 'RESIDUAL-ADAPTERS.json') and review['phase_recipes_sha256'] == digest_of(local / 'CLIFFORD-RECIPES.json')
    assert t['exact_local_clifford_recipe_sha256'] == digest_of(local / 'CLIFFORD-RECIPES.json')
    assert hashlib.sha256(gzip.decompress((td / 'GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest() == hosted['template_sha256']
    prof, dig, events, wrappers, split, nhost = validate(t, parent, ph, word, programs, ad, review)
    assert hosted['global_profile'] == {str(k): v for k, v in sorted(prof.items())} and hosted['emitted_program_sha256'] == dig
    assert (hosted['local_events'], hosted['wrapper_events'], hosted['split_residuals'], hosted['hosted_residuals']) == (events, wrappers, split, nhost)
    rejected = []
    def reject(name, fn):
        q = copy.deepcopy(t); fn(q)
        try: validate(q, parent, ph, word, programs, ad, review)
        except (AssertionError, KeyError, IndexError, TypeError, ValueError, StopIteration): rejected.append(name)
        else: raise AssertionError('mutation accepted: ' + name)
    sl = t['hosting']['slots']
    first = lambda q, pred: next(z for z in q['hosting']['slots'] if pred(z))
    split_slot = lambda z: len(z[4]) == 2
    entering_slot = lambda z: len(z[4]) == 1 and z[4][0][2] == 8
    tape_whole = lambda z: z[3] == 'tape' and len(z[4]) == 1
    win, side, pair, rk = derive_windows(parent)
    def outside(q):
        z = first(q, tape_whole); z[0] = next(s for s in range(L) if s not in win[z[2]])
    reject('hosted residual outside its window', outside)
    reject('split piece widths do not sum to nine', lambda q: first(q, split_slot)[4][0].__setitem__(2, first(q, split_slot)[4][0][2] + 1))
    reject('split pieces on non-adjacent copies', lambda q: first(q, split_slot)[4][1].__setitem__(0, first(q, split_slot)[4][1][0] + 1))
    reject('entering residual moved onto the tape', lambda q: first(q, entering_slot).__setitem__(3, 'tape'))
    def overlap(q):
        a = first(q, tape_whole); b = next(z for z in q['hosting']['slots'] if z is not a and z[2] == a[2] and z[3] == 'tape' and len(z[4]) == 1 and z[4][0][0] != a[4][0][0])
        b[4][0][0] = a[4][0][0]; b[4][0][1] = a[4][0][1]
    reject('two residuals on the same pending cells', overlap)
    def pattern_alias(q):
        # swap two equal-width pattern residuals between two copies of one child so that one copy receives a second
        # residual of an invocation it already serves: cells stay disjoint and every residual stays hosted
        pats = defaultdict(list)
        for z in q['hosting']['slots']:
            if z[3] == 'pattern': pats[z[2], z[4][0][0]].append(z)
        for (i, cp), zs in sorted(pats.items(), key=lambda kv: kv[0]):
            for za in zs:
                others = {z[0] for z in zs if z is not za}
                for (i2, cp2), zs2 in sorted(pats.items(), key=lambda kv: kv[0]):
                    if i2 != i or cp2 == cp: continue
                    for zb in zs2:
                        if zb[4][0][2] == za[4][0][2] and zb[0] in others:
                            za[4][0][0], zb[4][0][0] = zb[4][0][0], za[4][0][0]; za[4][0][1], zb[4][0][1] = zb[4][0][1], za[4][0][1]; return
        raise RuntimeError('no alias control found')
    reject('two helpers of one invocation on one pattern family', pattern_alias)
    reject('remainder child understated', lambda q: q['idle_children'][0].__setitem__('rank', q['idle_children'][0]['rank'] - 1))
    reject('dropped live family', lambda q: q.__setitem__('live', q['live'] - 1))
    reject('understated physical reserve', lambda q: q.__setitem__('physical', q['physical'] - 1))
    reject('duplicated hosted residual', lambda q: q['hosting']['slots'].append(list(q['hosting']['slots'][0])))
    reject('missing hosted residual', lambda q: q['hosting']['slots'].pop())
    reject('omitted local event', lambda q: q['local_programs']['forward'].pop())
    reject('omitted residual pre-adapter', lambda q: q['local_programs']['backward'].pop(next(k for k, z in enumerate(q['local_programs']['backward']) if z[0] == 'residual_adapter')))
    reject('wrong route axis', lambda q: next(o for o in q['calls'][0]['owners'][2 * V:] if o[1][0] == 4)[1][5].__setitem__(0, next(o for o in q['calls'][0]['owners'][2 * V:] if o[1][0] == 4)[1][5][1]))
    reject('helper owner on the active pair', lambda q: q['calls'][0]['owners'][2 * V].__setitem__(0, q['calls'][0]['owners'][0][0]))
    reject('changed data owner', lambda q: q['calls'][5]['owners'][3].__setitem__(0, q['calls'][5]['owners'][4][0]))
    reject('cross-replica helper family', lambda q: q['calls'][0]['owners'][2 * V].__setitem__(0, q['calls'][0]['owners'][2 * V][0] + 960))
    reject('omitted cover correction', lambda q: q['execution_schedule'].pop())
    reject('undercharged cover correction', lambda q: q['cover_final_correction'].__setitem__('charged_calls_per_cover', 0))
    reject('wrong local orientation', lambda q: q['calls'][0].__setitem__('orientation', 'backward'))
    res = dict(status='PASS_INDEPENDENT_RETIMED_HYBRID_CROSS_COPY_COMPLEX_AUDIT', complex_template_sha256=hosted['template_sha256'],
               complex_profile={str(k): v for k, v in sorted(prof.items())}, complex_live=DATA, complex_physical=t['physical'],
               complex_hosted_residuals=nhost, complex_split_residuals=split, complex_maxchild=max(prof), wrapper_events=wrappers,
               local_events=events, emitted_program_sha256=dig, mutations_rejected=rejected)
    outp.write_text(json.dumps(res, indent=2) + '\n'); print(json.dumps({k: v for k, v in res.items() if k != 'complex_profile'}))
if __name__ == '__main__': main()

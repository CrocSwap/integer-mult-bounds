# Adapted from PR #442's audit.py (DaysSky), complex half only, generalised to mixed residual widths by DreamingOfClouds with
# Claude Opus 5.5 (Anthropic), via Claude Code.  Shares no code with the generators.  Apache-2.0.
"""Independent audit of the idle-axis-hosted complex template with entrance widths.
Re-derives the hosting windows from the template's own schedule and checks, for every replica and invocation:
  * every helper residual has exactly one owner: a bank slot or a hosted slot, of the width 9 - dim(entrance frame);
  * a hosted slot lies on the data family of the idle child it names, inside that child's pending coordinates, disjoint from every
    other hosted slot of the family, in the child's window (strictly between the last local invocation or bridge naming the pair
    and the child), off the active pair;  NO residual is split across families or children (every piece is a whole residual);
  * the child keeps exactly the remaining coordinates; a bank holds residuals of one width, padded to 73;
  * strict (PR #458's rule on EVERY register class of an invocation): the active data wires and all hosted helpers have pairwise distinct data families; an entering
    helper is the only owner of its bank family and its route carries the bank chart (spectators = the first cells beyond every residual cell of the bank); the 9-cell
    footprints of a bank family are disjoint; no owner lies in the private namespace, whose record is re-based on the live stock; a bank holds width-9 residuals or entering ones;
  * the paid profile, live stock and the rank deficit 2496 are recomputed from scratch.
Mutation controls must be rejected.   usage: audit_hosted_gk.py PARENT_SC_DIR HOSTED_DIR OUT.json"""
import copy, gzip, hashlib, json, sys
from collections import Counter, defaultdict
from pathlib import Path
V, K, T, L, M = 120, 4, 8, 9, 73
DATA = 2 * K * V * T


def split_pad(p):
    n = -(-p // 51); return [p // n + (1 if i < p % n else 0) for i in range(n)]


def wins(events):
    last = {}; seen = []; w = {}
    for pos, e in enumerate(events):
        if e[0] == 'local': seen.append((pos, e[1], e[2])); last[e[2]] = pos
        elif e[0] == 'bridge': last[e[1]] = pos; last[e[2]] = pos
        else:
            lo = last.get(e[2], -1); w[e[1]] = {s for q, s, p in seen if lo < q < pos and p != e[2]}
    return w


def idle_basis(q):
    """the parent's orthonormal idle basis U_q (+) I for port q (derived here independently of the generator)"""
    z = min(i for i in range(L) if not (q >> i & 1)); a = q ^ (1 << z); order = list(range(L)); order[0], order[z] = order[z], order[0]
    return [(1 << i) ^ (a if a >> i & 1 else 0) for i in order] + [1 << i for i in range(L, M)]


def audit_complex(t, parent_t, local_checks, widths, strict=False, charts=None):
    """strict = PR #458's rule: at most one helper per physical family per invocation, spectators placed exactly.
    charts = (ports, DATA-PHASES recipes) for the spectator chart."""
    R = len(widths)
    assert t['local_programs'] == parent_t['local_programs'] and len(t['calls']) == 72
    prank = {}
    for it in parent_t['idle_children']: prank.setdefault(it['child'], it['rank'])
    stage_pair = {e['stage']: e['pair'] for e in t['recipe'] if e['kind'] == 'local'}
    ev = []; side = {}; pairs = {}
    for e in t['execution_schedule']:
        if e['kind'] == 'local_cover_sweep': ev.append(('local', e['stage'], stage_pair[e['stage']]))
        elif e['kind'] == 'bridge': ev.append(('bridge', e['dst'], e['src']))
        elif e['kind'] == 'idle_cover_sweep':
            for sd, ch in enumerate(e['child_indices']):
                if ch in prank: ev.append(('idle', ch, e['pair'])); side[ch] = sd; pairs[ch] = e['pair']
    W = wins(ev); hs = t['hosting']
    if strict:
        assert hs.get('max_helpers_per_physical_family_per_call') == 1
        seen = {}                                            # the children of one (pair, side) share their families: windows disjoint
        for i in W:
            for s_ in W[i]:
                k = (pairs[i], side[i], s_); assert k not in seen, ('overlapping windows in one family group', k); seen[k] = i
    used = defaultdict(set); hosted = {}
    for i, port, off, w, s, h in hs['slots']:
        assert w == widths[h] and s in W[i] and 0 <= off and off + w <= prank[i] and 0 <= port < V
        cells = set(range(off, off + w)); assert not cells & used[i, port]; used[i, port] |= cells
        assert (s, h) not in hosted; hosted[s, h] = (i, port, off, w)
    rem = {}
    for it in parent_t['idle_children']: rem[it['child'], it['port']] = it['rank'] - len(used[it['child'], it['port']])
    got = {(it['child'], it['port']): it['rank'] for it in t['idle_children']}
    assert got == {k: r for k, r in rem.items() if r} and all(it['replicas'] == T for it in t['idle_children'])
    LIVE = t['live']; occ = defaultdict(set); bw = {}; specs = []; foot = defaultdict(set)
    for c in t['calls']:
        s, rep, p = c['stage'], c['replica'], c['pair']; own = c['owners']; assert len(own) == 2 * V + R
        if strict:   # PR #458's rule on EVERY register class of the invocation (no register class is filtered out)
            cnt = Counter(f for f, r in own)
            for i_, (f, r) in enumerate(own):
                assert f < LIVE, ('owner in the private namespace', f)      # centres, reserved tableau and coefficient are never owners
                if f < DATA: assert cnt[f] == 1, ('two helpers on one physical family in one invocation (data class)', s, rep)     # active wires and hosted helpers of any width
                elif i_ >= 2 * V and widths[i_ - 2 * V] < L: assert cnt[f] == 1, ('an entering helper shares its bank family in one invocation (bank class)', s, rep)
                else: assert i_ >= 2 * V and r[0] == 2, ('bank class: helpers only', s, rep)       # width-9 helpers share a pure bank as in #433 (no wrapper acts on them)
        assert own[:2 * V] == next(q for q in parent_t['calls'] if (q['stage'], q['replica']) == (s, rep))['owners'][:2 * V]
        for h, (f, r) in enumerate(own[2 * V:]):
            w = widths[h]
            if (s, h) in hosted:
                i, port, off, w2 = hosted[s, h]
                assert w2 == w and f == rep * 960 + (2 * pairs[i] + side[i]) * V + port and pairs[i] != p
                if not strict: assert r[0] in (3, 4) and r[1:3] == [i, off] and (r[0] == 3 or w < L)      # PR #442's rule: slot only (a spectator record, if any, is not read)
                elif w == L: assert r == [3, i, off]
                else:       # exact host chart: residual vectors = pending[off:off+w] in B_q, spectators = the first unused indices
                    ports_, recipes = charts; B = idle_basis(ports_[port]); pend = [int(x) for x in recipes[port]['idle_children'][i]['orthogonal_axes']]
                    occ_ = [B.index(x) for x in pend[off:off + w]]; sp = [j for j in range(M) if j not in occ_][:L - w]
                    assert r == [4, i, off, w, sp] and len(set(occ_) | set(sp)) == L
            else:
                assert r[0] == 2 and DATA <= f < LIVE
                if w == L: assert len(r) == 2; off = r[1] * L        # [2, slot]: a width-9 residual of a pure width-9 bank (#433)
                else: assert len(r) == 4 and r[2] == w and isinstance(r[3], list); off = r[1]      # [2, offset, width, spectator cells]: a banked ENTERING residual
                assert 0 <= off and off + w <= M
                cells = set(range(off, off + w)); assert not cells & occ[f]; occ[f] |= cells; bw.setdefault(f, []).append((w, len(r) == 2))
                if w < L: specs.append((f, off, w, r[3]))
                fp = cells | (set(r[3]) if w < L else set())
                if strict: assert len(fp) == L and not fp & foot[s, rep, f], ('footprints overlap on a bank family', s, rep, f); foot[s, rep, f] |= fp
    banks = sorted(occ); assert banks == list(range(DATA, LIVE))
    if strict:   # bank chart: the spectators of a banked entering helper are the first cells beyond every residual cell of the bank
        for f, off, w, sp in specs:
            n_ = len(occ[f]); assert occ[f] == set(range(n_)) and sp == list(range(n_, n_ + L - w)) and n_ + L - w <= M, ('bank spectators are not the first cells beyond the residuals', f)
        pn = parent_t['private_namespace']; C_ = pn['centers'][1] - pn['centers'][0]      # the private registers sit beyond the live stock and do not overlap it
        assert t['physical'] == LIVE + C_ + R + 2 and t['private_namespace'] == {'centers': [LIVE, LIVE + C_], 'reserved_tableau': [LIVE + C_, LIVE + C_ + R], 'coefficient': [t['physical'] - 2, t['physical']]}, 'private namespace'
    paid = Counter()
    for c in t['calls']:
        for r_, z in local_checks[c['orientation']]['paid_profile'].items(): paid[int(r_)] += z
    for (ch, port), r_ in rem.items():
        if r_: paid[r_] += T
    for f in banks:
        pad = M - len(occ[f]); assert pad > 0 and occ[f] == set(range(len(occ[f])))      # packed from offset 0, rest is the pad
        pure = all(w == L for w, _ in bw[f]); assert all(sh == (pure and w == L) for w, sh in bw[f]) and (pure or all(w < L for w, _ in bw[f]))    # a bank holds only width-9 residuals (short route) or only entering ones
        for part in split_pad(pad): paid[part] += 1      # a pad above 51 is paid as nested commuting children (73^2 > 2*child^2)
    mass = sum(r * n for r, n in paid.items()); assert M * LIVE - mass == 2496
    assert M * M > 2 * max(paid) ** 2
    return paid, len(hosted) * T


def main():
    psc, cd, outp = map(Path, sys.argv[1:4])
    pct = json.loads(gzip.decompress((psc / 'GLOBAL-TEMPLATE.json.gz').read_bytes()))
    can = json.loads(gzip.decompress((psc / 'CANONICAL-WORD.json.gz').read_bytes()))
    widths = [L - len(can['frames'][can['start'][2 * V + i]]) for i in range(len(can['start']) - 2 * V)]
    ct = json.loads(gzip.decompress((cd / 'GLOBAL-TEMPLATE.json.gz').read_bytes()))
    ch = json.loads((cd / 'HOSTED.json').read_text())
    assert hashlib.sha256(gzip.decompress((cd / 'GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest() == ch['template_sha256']
    lc = json.loads((psc / 'LOCAL-CHECKS.json').read_text())
    strict = '--one-helper-per-family' in sys.argv; sys.argv = [a for a in sys.argv if a != '--one-helper-per-family']
    charts = None
    if strict:
        ph = json.loads(Path('work/complex-nine-native/DATA-PHASES.json').read_text()); assert [p['q'] for p in ph['recipes']] == can['ports']; charts = (can['ports'], ph['recipes'])
    cp, chh = audit_complex(ct, pct, lc, widths, strict, charts); assert cp == Counter({int(k): v for k, v in ch['global_profile'].items()})
    prank = {}
    for it in pct['idle_children']: prank.setdefault(it['child'], it['rank'])
    controls = []; skipped = []
    def reject(name, fn):
        q = copy.deepcopy(ct); fn(q)
        try: audit_complex(q, pct, lc, widths, strict, charts)
        except (AssertionError, KeyError, IndexError, StopIteration): controls.append(name)
        else: raise AssertionError('mutation accepted: ' + name)
    sl0 = lambda q: q['hosting']['slots'][0]
    reject('hosted residual outside its window', lambda q: sl0(q).__setitem__(4, next(s for s in range(9) if s not in q['hosting']['windows'][str(sl0(q)[0])][2])))
    reject('remainder child understated', lambda q: q['idle_children'][0].__setitem__('rank', q['idle_children'][0]['rank'] - 1))
    reject('dropped bank', lambda q: q.__setitem__('live', q['live'] - 1))
    reject('duplicated hosted residual', lambda q: q['hosting']['slots'].append(list(sl0(q))))
    reject('hosted width not the entrance width', lambda q: sl0(q).__setitem__(3, sl0(q)[3] + 1))
    def overlap(q):          # two different residuals of one (child, port) forced onto the same coordinates
        seen = {}
        for sl in q['hosting']['slots']:
            k = (sl[0], sl[1])
            if k in seen: sl[2] = seen[k][2]; return
            seen[k] = sl
        raise RuntimeError('no (child, port) with two residuals: control not applicable')
    reject('overlapping hosted coordinates', overlap)
    reject('hosted owner on the active pair', lambda q: q['calls'][0]['owners'].__setitem__(240 + next(h for h in range(len(widths)) if q['calls'][0]['owners'][240 + h][1][0] == 3), [0, [3, 0, 0]]))
    reject('missing remainder child', lambda q: q['idle_children'].pop())
    if strict:
        def share_family(q):     # move a stage-s helper onto the family of another stage-s helper of the same child, at free coordinates
            used_ = defaultdict(set); by = defaultdict(list)
            for sl in q['hosting']['slots']:
                used_[sl[0], sl[1]] |= set(range(sl[2], sl[2] + sl[3])); by[sl[0], sl[4]].append(sl)
            for (i, s_), sls in by.items():
                for a in sls:
                    for sl in sls:
                        if sl is a or sl[1] == a[1]: continue
                        w = sl[3]; free = [o for o in range(0, prank[i] - w + 1) if not (set(range(o, o + w)) & used_[i, a[1]])]
                        if not free: continue
                        old_port = sl[1]; sl[1] = a[1]; sl[2] = free[0]
                        for c in q['calls']:
                            if c['stage'] == s_:
                                f0, r0 = c['owners'][2 * V + sl[5]]
                                c['owners'][2 * V + sl[5]] = [f0 + (a[1] - old_port), [3, i, sl[2]] if w == L else [4, i, sl[2], w, None]]
                        return a, sl
            raise RuntimeError('control not applicable')
        def refresh_remainders(q):       # keep the remainder children consistent with the (mutated) slots
            used_ = defaultdict(int)
            for sl in q['hosting']['slots']: used_[sl[0], sl[1]] += sl[3]
            q['idle_children'] = [dict(child=it['child'], port=it['port'], rank=it['rank'] - used_[it['child'], it['port']], hosted=used_[it['child'], it['port']], replicas=T)
                                  for it in pct['idle_children'] if it['rank'] - used_[it['child'], it['port']] > 0]
        q = copy.deepcopy(ct)
        try: a, sl = share_family(q); refresh_remainders(q)
        except RuntimeError: a = sl = None      # no free coordinates in this word's hosting: control not applicable (recorded below)
        if sl is not None:
            if sl[3] < L:        # complete the spectator record so that only the family rule is violated
                ports_, recipes = charts
                for c in q['calls']:
                    if c['stage'] == sl[4]:
                        f0, r0 = c['owners'][2 * V + sl[5]]; B = idle_basis(ports_[sl[1]]); pend = [int(x) for x in recipes[sl[1]]['idle_children'][sl[0]]['orthogonal_axes']]
                        occ_ = [B.index(x) for x in pend[sl[2]:sl[2] + sl[3]]]; r0[4] = [j for j in range(M) if j not in occ_][:L - sl[3]]
            audit_complex(q, pct, lc, widths, False, charts)          # the PR #442 rule accepts this template ...
            try: audit_complex(q, pct, lc, widths, True, charts)
            except AssertionError: controls.append('two helpers on one physical family in one invocation (accepted by the #442 rule, rejected here)')
            else: raise AssertionError('mutation accepted: two helpers on one family')
        else: skipped.append('two helpers on one physical family: no free coordinates to build the violation in this word')
        def entering_owner(q):          # (owner record of the first hosted entering helper in call 0)
            return next(o for o in q['calls'][0]['owners'][2 * V:] if o[1][0] == 4)
        def spectator_is_residual(q):
            o = entering_owner(q); f = o[0]; i, off, w = o[1][1], o[1][2], o[1][3]; port = (f % 960) % V      # family = rep*960 + (2*pair+side)*V + port
            B = idle_basis(charts[0][port]); pend = [int(x) for x in charts[1][port]['idle_children'][i]['orthogonal_axes']]
            o[1][4] = [B.index(pend[off])] + o[1][4][1:]
        reject('a spectator coordinate that is a residual coordinate', spectator_is_residual)
        reject('spectator coordinates shifted', lambda q: entering_owner(q)[1].__setitem__(4, [x + 1 for x in entering_owner(q)[1][4]]))
        reject('spectator record dropped', lambda q: entering_owner(q)[1].__setitem__(slice(4, None), []))
        reject('entering helper routed without a spectator record', lambda q: entering_owner(q).__setitem__(1, [3, entering_owner(q)[1][1], entering_owner(q)[1][2]]))
        reject('rule flag removed from the template', lambda q: q['hosting'].pop('max_helpers_per_physical_family_per_call'))
        # ---- the rule on the other register classes: banks, the private namespace (centres, tableau, coefficient), copies (replicas), data wires
        def reject_with(name, fn, must):
            q = copy.deepcopy(ct); fn(q)
            try: audit_complex(q, pct, lc, widths, strict, charts)
            except (AssertionError, KeyError, IndexError, StopIteration) as e:
                assert any(m_ in str(e) for m_ in must), (name, str(e)); controls.append(name)
            else: raise AssertionError('mutation accepted: ' + name)
        def banked_pos(q):      # (call, index) of the first banked ENTERING owner
            return next((c, i) for c in q['calls'] for i, o in enumerate(c['owners']) if i >= 2 * V and o[1][0] == 2 and len(o[1]) == 4)
        def pack_banks_by_call(q):
            """re-lay every entering bank of a stage so that eight entering helpers (their footprints are nine cells each) share a bank family, whatever their
            replica: residuals packed from cell 0, the spectators of the bank's helpers in its pad (cells after the residuals), disjoint.  The layout of
            'nine-cell bank slots': cell-level everything is valid (residuals packed from 0, pad recomputed, disjoint footprints); only the one-owner rule is
            violated.  RuntimeError when the stage cannot be re-laid on its own bank families."""
            for s_ in sorted({c['stage'] for c in q['calls']}):
                items = [(c, i) for c in sorted((c for c in q['calls'] if c['stage'] == s_), key=lambda c: c['replica']) for i, o in enumerate(c['owners'])
                         if i >= 2 * V and o[1][0] == 2 and len(o[1]) == 4]
                if not items: continue
                fams = sorted({c['owners'][i][0] for c, i in items}); groups = [items[k:k + M // L] for k in range(0, len(items), M // L)]
                if len(groups) != len(fams): raise RuntimeError('control not applicable')
                for f0, grp in zip(fams, groups):
                    cells = sum(c['owners'][i][1][2] for c, i in grp); off = 0; spec = cells
                    for c, i in grp:
                        w = c['owners'][i][1][2]; c['owners'][i] = [f0, [2, off, w, list(range(spec, spec + L - w))]]; off += w; spec += L - w
        if any(o[1][0] == 2 and len(o[1]) == 4 for c in ct['calls'] for o in c['owners'][2 * V:]):
            q = copy.deepcopy(ct)
            try: pack_banks_by_call(q)
            except RuntimeError: q = None; skipped.append('two entering helpers on one bank family: the entering banks of this word cannot be re-laid eight per family')
            if q is not None:
                audit_complex(q, pct, lc, widths, False, charts)          # the PR #442 rule accepts this layout (cells disjoint, spectators not read) ...
                try: audit_complex(q, pct, lc, widths, True, charts)
                except AssertionError as e:
                    assert 'bank class' in str(e), str(e); controls.append('two entering helpers on one bank family in one invocation, disjoint footprints, spectators in the pad (accepted by the #442 rule, rejected here)')
                else: raise AssertionError('mutation accepted: two entering helpers on one bank family')
            reject_with('a bank spectator that is a residual cell', lambda q: (lambda r: r.__setitem__(3, [r[1]]))(banked_pos(q)[0]['owners'][banked_pos(q)[1]][1]), ('footprints overlap', 'bank spectators'))
            reject_with('bank spectator cells shifted', lambda q: (lambda r: r.__setitem__(3, [x + 1 for x in r[3]]))(banked_pos(q)[0]['owners'][banked_pos(q)[1]][1]), ('bank spectators',))
            reject_with('bank spectator count wrong', lambda q: (lambda r: r.__setitem__(3, r[3] * 2))(banked_pos(q)[0]['owners'][banked_pos(q)[1]][1]), ('bank spectators',))
            reject_with('bank spectator record dropped', lambda q: (lambda o: o.__setitem__(1, o[1][:3]))(banked_pos(q)[0]['owners'][banked_pos(q)[1]]), ('',))
            reject_with('a banked entering helper on an active data family', lambda q: (lambda c, i: c['owners'][i].__setitem__(0, c['owners'][0][0]))(*banked_pos(q)), ('data class',))
            reject_with('a bank owner in the private namespace (centres)', lambda q: (lambda c, i: c['owners'][i].__setitem__(0, q['live'] + 1))(*banked_pos(q)), ('private namespace', ''))
            reject_with('a bank owner in the private namespace (reserved tableau)', lambda q: (lambda c, i: c['owners'][i].__setitem__(0, q['live'] + 16 + 5))(*banked_pos(q)), ('private namespace', ''))
        else: skipped.append('bank controls: this word has no banked entering helper')
        for bi in [i for i, e in enumerate(ct['execution_schedule']) if e['kind'] == 'bridge']:     # copies: the children of one (pair, side) share their families
            q = copy.deepcopy(ct); q['execution_schedule'].pop(bi)
            try: audit_complex(q, pct, lc, widths, True, charts)
            except AssertionError as e:
                if 'overlapping windows' in str(e): controls.append('windows of two idle children of one family group overlap (a bridge removed from the schedule)'); break
        else: skipped.append('windows of two idle children of one family group: no schedule mutation creates an overlap in this word')
        reject_with('private namespace left at the parent\'s ranges', lambda q: q.__setitem__('private_namespace', pct['private_namespace']), ('private namespace',))
        reject_with('private namespace overlapping the live stock', lambda q: q['private_namespace'].__setitem__('centers', [q['live'] - 1, q['live'] + 15]), ('private namespace',))
        reject_with('hosted helper on the data family of another replica', lambda q: next(o for o in q['calls'][0]['owners'][2 * V:] if o[1][0] in (3, 4)).__setitem__(0, next(o for o in q['calls'][0]['owners'][2 * V:] if o[1][0] in (3, 4))[0] + 960), ('',))
        reject_with('active owner on the family of another replica', lambda q: q['calls'][0]['owners'][0].__setitem__(0, q['calls'][0]['owners'][0][0] + 960), ('',))
        reject_with('a second owner on an active data family', lambda q: q['calls'][0]['owners'].__setitem__(1, [q['calls'][0]['owners'][0][0], q['calls'][0]['owners'][1][1]]), ('data class',))
    res = dict(status='PASS_INDEPENDENT_HOSTING_AUDIT_WITH_ENTRANCE_WIDTHS', one_helper_per_family=strict, complex_template_sha256=ch['template_sha256'],
               complex_profile={str(k): v for k, v in sorted(cp.items())}, complex_live=ct['live'], complex_hosted_residuals=chh,
               complex_maxchild=max(cp), widths=dict(sorted(Counter(widths).items())), mutations_rejected=controls, controls_not_applicable=skipped)
    outp.write_text(json.dumps(res, indent=2) + '\n'); print(json.dumps({k: v for k, v in res.items() if 'profile' not in k}))


if __name__ == '__main__': main()

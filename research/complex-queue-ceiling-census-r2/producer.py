#!/usr/bin/env python3
"""Producer: derive SNAPSHOT2.json - full pins for the 16 uncovered claims.

For each claim: pin its current head, locate its own package (changed-file prefixes,
title-derived for #1172), find the record whose kappa equals the title kappa carrying
a paid profile (complex_profile or global_profile) and idle_remainder_profile (+ live,
calls derived when live % 896 == 0), verify the coverage identity and idle split, and
screen the per-call local word with merged #1240's ceiling calculator. Unscreenable
claims are pinned with the reason and the fields they must record.
Emits SNAPSHOT2.json. Stdlib only.
"""
import gzip, json, re, subprocess, sys, time
from decimal import Decimal
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / 'research/complex-local-word-ceiling'))
import ceiling as C  # noqa: E402

PRS = [1104, 1107, 1111, 1117, 1121, 1150, 1154, 1169, 1172, 1175, 1176, 1183, 1192, 1201, 1207, 1218]
MAXB = 12 * 1024 * 1024
M, CENTRE = 73, 64
M64 = {1172: 'research/gauge44-ends7-t16'}

def git(*a):
    r = subprocess.run(['git', '-C', str(REPO), *a], capture_output=True)
    if r.returncode:
        raise RuntimeError(' '.join(a))
    return r.stdout

def sh(*a):
    return subprocess.run(a, capture_output=True).stdout

# Audit heads frozen at triage time (2026-10-15 ~12:50Z), full SHAs resolved from the
# local object store. Live refs move mid-session (force-pushes rework packages); the
# snapshot pins the exact audited heads, exactly as the first census pins its heads.
HEADFIX = {
    1104: 'd8982686afd7ef6ce52ddeaa17011ccda558d666',
    1107: '6123fc5d57db16aaa3e8a26b4a11a34b46c0c391',
    1111: '381831ea554ea983e16224dabed8921b7d0ffdbc',
    1117: '342b67f23dfa8f41a520a0d58978b2875e9eb0dd',
    1121: '61e816c29165a94f6cfc57d9e195063a5b027bc2',
    1150: 'bebf64ffda3fd5128342d19ee6d419b1150b49f7',
    1154: '390de2866a03758e7f4ddbb2846e5b2ee4e72154',
    1169: '13d02293a7af67d7e3bd2e4d7f1a2943ac20537e',
    1172: '4d2cc9df55ed5a17786b7c0a200d70332afbe41e',
    1175: '007a7c64280053e2ddabdb92e60b51bfd9105119',
    1176: '3a0d419341879a395d921693112c3b826de93677',
    1183: '9e7ccda21f28f5dd0397aa04a596e4f0e1d75d1d',
    1192: '970793428d346b4aa8d8fa2af03aa6dd5ad6f994',
    1201: '86a7072626d9b3e49222378bb76601a11d2f58ea',
    1207: 'd53f23eafc378a6e680294081d09886597129733',
    1218: '0aa147977ad226f9d777d6a21a610ab037985b1e',
}


def head_of(pr):
    if pr in HEADFIX:
        return HEADFIX[pr]
    for ref in (f'refs/remotes/pull/{pr}', f'refs/remotes/pull/{pr}/head'):
        try:
            out = git('rev-parse', '--verify', ref).decode().strip()
            if out:
                return out
        except RuntimeError:
            continue
    git('fetch', '-q', 'origin', f'pull/{pr}/head')
    return git('rev-parse', 'FETCH_HEAD').decode().strip()

TRE = re.compile(r'(?:kappa|\u03ba)\s*=?\s*(0\.\d+)', re.IGNORECASE)

def title_kappa(pr, titles):
    m = TRE.search(titles.get(pr, ''))
    return Q(Decimal(m.group(1))) if m else None

# Static own-package prefixes, established by the live changed-file scan of 2026-10-15
# (triage pass; see README). Kept static so the producer needs no network: rerunning
# `gh pr view N --json files` reproduces this map.
PREFIXFIX = {
    1104: ['research/gauge44-ends7-t16'],
    1107: ['research/gauge44-ends7-t16'],
    1111: ['research/demote635-t16'],
    1117: ['research/gauge44-ends7-t16'],
    1121: ['research/gauge44-ends7-t16'],
    1150: ['research/complex-rank7-owner-exchanges'],
    1154: ['research/adaptive-kernel-demotion'],
    1169: ['research/three-demotions-t37-composition'],
    1172: ['research/gauge44-ends7-t16'],
    1175: ['research/gauge44-slots-arcflow'],
    1176: ['research/crosscall-kernel-demotion'],
    1183: ['research/mixed-t37-entrances'],
    1192: ['research/crosscall-t37-entrances'],
    1201: ['research/mixed-t37-source-holder-fusions'],
    1207: ['research/x54-mixed-t37-fusions'],
    1218: ['research/global-mixed-x54-fusions'],
}


def prefixes_for(pr):
    if '--fetch-prefixes' in sys.argv:
        raw = sh('timeout', '90', 'gh', 'pr', 'view', str(pr), '--repo', 'CrocSwap/integer-mult-bounds',
                 '--json', 'files', '--jq', '.files[].path').decode(errors='replace')
        prefs = set()
        for p in raw.splitlines():
            p = p.strip()
            if p.startswith('research/') and not p.startswith('research/community-'):
                seg = p.split('/')
                if len(seg) >= 2:
                    prefs.add('/'.join(seg[:2]))
        if pr in M64:
            prefs.add(M64[pr])
        return sorted(prefs)
    return list(PREFIXFIX[pr])

def all_dicts(obj):
    stack = [obj]
    while stack:
        x = stack.pop()
        if isinstance(x, dict):
            yield x
            stack.extend(x.values())
        elif isinstance(x, list):
            stack.extend(x)

def as_int_hist(h):
    try:
        return {str(int(k)): int(v) for k, v in h.items()} if isinstance(h, dict) else None
    except Exception:
        return None

# Title lines (PR-state snapshot fetched 2026-10-15 via `gh pr view N --json state,title`).
# Static so the producer runs offline; refetch with --fetch-titles.
TITLES_RAW = {
    1104: '1104\tOPEN\tConditional \u03ba = 0.001672691689152441: rank-seven helper ends and T16 owner packing on the seven-slot k8 word',
    1107: '1107\tOPEN\tConditional \u03ba = 0.001672765980186726: rank-seven helper ends and T16 owner packing on the seven-slot k8 word',
    1111: '1111\tMERGED\tConditional \u03ba = 0.001672780159952542: reverse one entrance promotion to fill T16 gaps',
    1117: '1117\tOPEN\tConditional \u03ba = 0.001672846995880185: rank-seven helper ends and T16 owner packing on the seven-slot k8 word',
    1121: '1121\tOPEN\tConditional \u03ba = 0.001672965558289236: rank-seven helper ends and T16 owner packing on the seven-slot k8 word',
    1150: '1150\tOPEN\tConditional kappa 0.001672716806120974: rank-seven T16 owner exchanges',
    1154: '1154\tOPEN\tConditional kappa = 0.001673260706543984: adaptive joint kernel demotion on PR1117',
    1169: '1169\tOPEN\tConditional \u03ba = 0.001675568675201533: joint entrances with T37 owner packing',
    1172: '1172\tOPEN\tresearch/gauge44-ends7-t16: cross-replica exchange extinguishing remainders 5 and 6 (kappa = 0.001672802407467250)',
    1175: '1175\tOPEN\tConditional kappa 0.001675338871723469: whole-owner map at the packing boundary',
    1176: '1176\tOPEN\tAdd files via upload - Conditional kappa 0.001675224519162937: cross-call gap augmentation for three extra kernel islands',
    1183: '1183\tOPEN\tConditional kappa 0.001675603180601302: mixed entrance providers on T37 owners',
    1192: '1192\tOPEN\tConditional kappa 0.001675670695307702: cross-call T37 entrance augmentation',
    1201: '1201\tOPEN\tConditional kappa 0.00167576776285696: mixed T37 source-holder fusions',
    1207: '1207\tOPEN\tConditional kappa 0.001675807682652: X54 on mixed T37 fusion providers',
    1218: '1218\tOPEN\tConditional kappa 0.001675809683500501: global mixed allocation with X54 and fusions',
}


def titles_map():
    if '--fetch-titles' in sys.argv:
        out = {}
        for pr in PRS:
            raw = sh('timeout', '60', 'gh', 'pr', 'view', str(pr), '--repo', 'CrocSwap/integer-mult-bounds',
                     '--json', 'number,state,title', '--jq', '"\\(.number)\\t\\(.state)\\t\\(.title)"').decode(errors='replace')
            f = raw.strip().split('\t')
            if len(f) >= 3:
                out[int(f[0])] = raw.strip()
        return out
    return dict(TITLES_RAW)


def main():
    titles = titles_map()
    out = {'snapshot_utc': '2026-10-15', 'producer': 'producer2.py (this package)',
           'selection': 'The 16 claims left not-covered by research/complex-queue-ceiling-census, at current heads.',
           'claims': []}
    for pr in PRS:
        t0 = time.time()
        head = head_of(pr)
        tk = title_kappa(pr, titles)
        prefs = prefixes_for(pr)
        rec = dict(pr=pr, head=head, title_kappa=str(tk), prefixes=prefs)
        entries = []
        for pref in prefs:
            if time.time() - t0 > 150:
                break
            tree = git('ls-tree', '-r', '-l', '-z', head, '--', pref + '/').decode(errors='replace').split('\0')
            for ent in tree:
                parts = ent.split('\t', 1)
                if len(parts) != 2:
                    continue
                meta, path = parts
                if not (path.endswith('.json') or path.endswith('.json.gz')):
                    continue
                bits = meta.split()
                if len(bits) < 4:
                    continue
                try:
                    if int(bits[3]) > MAXB:
                        continue
                except ValueError:
                    continue
                try:
                    raw = git('cat-file', 'blob', bits[2])
                    if path.endswith('.gz'):
                        raw = gzip.decompress(raw)
                    entries.append((bits[2], path, json.loads(raw)))
                except Exception:
                    continue
        rec['nfiles'] = len(entries)
        done = False
        for blob, path, obj in entries:
            for r in all_dicts(obj):
                if 'complex_profile' not in r and 'global_profile' not in r and 'idle_remainder_profile' not in r:
                    continue
                kap = r.get('kappa')
                try:
                    if kap is None or Q(kap) != tk:
                        continue
                except (TypeError, ValueError, ZeroDivisionError):
                    continue
                P = as_int_hist(r.get('complex_profile')) or as_int_hist(r.get('global_profile'))
                prof_key = 'complex_profile' if r.get('complex_profile') is not None else 'global_profile'
                if P is None:
                    continue
                I = as_int_hist(r.get('idle_remainder_profile')) or {}
                live, calls = r.get('live'), r.get('calls')
                idle_file = None
                if not I:
                    for b2, p2, o2 in entries:
                        for r2 in all_dicts(o2):
                            if 'idle_remainder_profile' in r2:
                                cand = as_int_hist(r2.get('idle_remainder_profile'))
                                if cand and r2.get('live') is not None:
                                    I, live = cand, r2['live']
                                    idle_file = p2
                                    break
                        if I:
                            break
                if calls is None and live is not None and live % 896 == 0:
                    calls = live * 9 // 896
                if live is None or calls is None or not I:
                    continue
                mass = sum(int(k) * n for k, n in P.items())
                if mass != (M - 1) * live + CENTRE * calls:
                    continue
                if not (all(I[k_] <= P.get(k_, 0) for k_ in I) and max(int(k_) for k_ in I) <= C.max_idle_rank(M)):
                    continue
                local = {int(k_): Q(n - I.get(k_, 0), calls) for k_, n in P.items() if n - I.get(k_, 0)}
                lo, hi = C.ceiling(local, M, live, calls, CENTRE)
                rec.update(screened=True, kappa=str(kap), complex_lower=str(r.get('complex_lower')),
                           profile_file=path, profile_blob=blob, prof_key=prof_key,
                           idle_file=idle_file or path, idle_blob=(idle_file and git('rev-parse', f'{head}:{idle_file}').decode().strip()) or blob,
                           profile=P, idle=I, live=live, calls=calls, mass=mass,
                           a_lo=str(lo), a_hi=str(hi), cap=str(Q(hi, 1 + hi)),
                           local_per_call={str(k_): str(v) for k_, v in sorted(local.items())})
                done = True
                break
            if done:
                break
        if not done:
            rec['screened'] = False
            ks = {}
            for _, path, obj in entries:
                for r in all_dicts(obj):
                    if 'global_profile' in r or 'idle_remainder_profile' in r:
                        ks[path] = sorted(r.keys())[:28]
                        break
            rec['observed_keysets'] = {k: ks[k] for k in sorted(ks)[:6]}
        out['claims'].append(rec)
        print(json.dumps(dict(pr=pr, screened=rec['screened'], head=head[:12])), flush=True)
    Path('SNAPSHOT2.json').write_text(json.dumps(out, indent=1, sort_keys=True) + '\n')
    print('WROTE SNAPSHOT2.json claims=%d screened=%d' % (len(out['claims']), sum(c['screened'] for c in out['claims'])))

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Apply Josie Elliston's owner/event-window audit and Sagar Thakrar's code-disjoint pricing to the four packages
of PR #1175 (six packages), unchanged; the mixed package has two providers and the owner audit's interface takes one word's
widths, so it receives the pricing only (its map is covered by the strict audit and the per-call-width recount) (the composition pattern of research/community-batch1099-audit/check_frontier1094.py).

  owners   research/t16-owner-audit-seed67/verify.py: rules R1-R7, X1, X2 and the eleven mutation controls, on the
           package's data/OWNERS.json.gz, data/PLAN.json and data/SPEC.json, with the helper widths and local profile
           read from the package's rebuilt native word (--word NAME=FULL-WORD.json.gz) and the audit's own pinned
           parent template and DATA-PHASES (its SOURCES.json hashes are checked). T = 8 for the three T8 maps, 16 for
           research/gauge44-slots-t16-arcflow.
  price    research/pending-claims-independent-pricing/sweep.py price(): rank mass, deficit D = W - 64N, halving
           guard, the complex endpoint certified against the 10^-24 grid, kappa from the selected outer reduction with
           the unchanged PR589 bit endpoint, compared with the package's exact kappa and its decimal.

Usage: check_independent.py --main ROOT --output OUT.json --word arcflow=... --assembly arcflow=... (all four)
Neither auditor's inherited-interface scope is extended. Prepared by G. V. Chudnovsky with Anthropic Claude assistance.
Apache-2.0.
"""
import argparse, gzip, hashlib, importlib.util, json, sys
from collections import Counter
from pathlib import Path

PACKAGES = {'arcflow': ('research/gauge44-slots-arcflow', 8), 'unpromo': ('research/gauge44-slots-unpromo-arcflow', 8),
            'deepen': ('research/gauge44-slots-deepen-arcflow', 8), 't16': ('research/gauge44-slots-t16-arcflow', 16),
            'balance': ('research/gauge44-slots-balance-arcflow', 8), 'mixed': ('research/gauge44-slots-mixed-arcflow', 8)}
KAPPA = {'arcflow': '0.001674083482880778', 'unpromo': '0.001674576537247681',
         'deepen': '0.001675338871723469', 't16': '0.001674087289164567', 'balance': '0.001675784247432857', 'mixed': '0.001675867534384272'}


def load_module(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


def read(p):
    b = Path(p).read_bytes(); return json.loads(gzip.decompress(b) if str(p).endswith('.gz') else b)


def require(ok, msg):
    if not ok: raise SystemExit('FAIL independent check: ' + msg)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--main', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--word', action='append', default=[], help='NAME=path of the package\'s rebuilt FULL-WORD.json.gz')
    ap.add_argument('--assembly', action='append', default=[], help='NAME=path of the package\'s strict ASSEMBLY.json')
    a = ap.parse_args()
    root = a.main.resolve()
    words = dict(x.split('=', 1) for x in a.word); asms = dict(x.split('=', 1) for x in a.assembly)
    require(set(words) == set(asms) == set(PACKAGES), 'one word and one assembly per package')

    aud = load_module('owners', root / 'research/t16-owner-audit-seed67/verify.py')
    pins = read(root / 'research/t16-owner-audit-seed67/SOURCES.json')['inputs']
    require(hashlib.sha256((root / aud.TEMPLATE).read_bytes()).hexdigest() == pins['template_sha256'], 'parent template pin')
    require(hashlib.sha256((root / aud.PHASES).read_bytes()).hexdigest() == pins['data_phases_sha256'], 'DATA-PHASES pin')
    geo = aud.geometry(read(root / aud.TEMPLATE), read(root / aud.PHASES))
    sys.path.insert(0, str(root / 'research/pending-claims-independent-pricing'))
    sweep = load_module('pricing', root / 'research/pending-claims-independent-pricing/sweep.py')

    out = {}
    for k, (rel, T) in PACKAGES.items():
        p = root / rel; w = read(words[k]); asm = read(asms[k])
        if k == 'mixed':
            spec = read(p / 'data/SPEC.json'); plan = read(p / 'data/PLAN.json'); roles = read(p / 'data/OWNERS.json.gz')
            idle = aud.as_profile(spec['expected']['idle_remainder_profile']); prof = aud.as_profile(plan['profile'])
            # recount the idle histogram from the roles with per-call widths (standard library)
            pcw = {(c['stage'], c['replica']): c['widths'] for c in plan['per_call_widths']}; used = {}
            for z in roles:
                require(z['width'] == pcw[z['stage'], z['replica']][z['helper']], 'mixed role width')
                b = (z['owner_replica'], z['child'], z['port']); cells = set(range(z['offset'], z['offset'] + z['width']))
                require(not (used.get(b, set()) & cells), 'mixed overlap'); used[b] = used.get(b, set()) | cells
            rc = Counter()
            for key, (cap, _) in plan['windows'].items():
                rep_, ch = map(int, key.split(','))
                for port in range(112):
                    u = used.get((rep_, ch, port), set()); require(u == set(range(len(u))), 'mixed prefix')
                    if cap - len(u): rc[cap - len(u)] += 1
            require(rc == idle, 'mixed idle recount')
            c = dict(pr=1175, head=k, profile={str(r): n for r, n in sorted(prof.items())}, live=896 * T, calls=9 * T,
                     complex_lower=asm['complex_lower'], record_kappa=asm['kappa'], claimed_kappa_decimal=KAPPA[k], bit_lower=asm['bit_lower'])
            priced = sweep.price(c)
            for key in ('endpoint_certified', 'deficit_equals_W_minus_64N', 'halving', 'record_bit_is_pr589', 'kappa_equals_record', 'kappa_equals_title'):
                require(priced[key], '%s pricing: %s' % (k, key))
            out[k] = dict(package=rel, T=T, idle={str(r): n for r, n in sorted(rc.items())}, providers=sorted(plan['provider_registry']),
                          owner_audit='not applicable: two providers (the audit takes one word\'s widths); idle histogram recounted here with per-call widths', price=priced)
            print('PASS', k, 'T', T, 'two providers; idle', out[k]['idle'], 'kappa', priced['kappa_exact_decimal'], flush=True); continue
        widths = aud.word_widths(w); local = aud.as_profile(w['report']['local_profile'])
        require(Counter(widths) == aud.as_profile(w['report']['width_inventory']), k + ' word width inventory')
        spec = read(p / 'data/SPEC.json'); plan = read(p / 'data/PLAN.json'); roles = read(p / 'data/OWNERS.json.gz')
        require(aud.as_profile(spec['providers']['gauge44']['expected_profile']) == local, k + ' SPEC local profile')
        require(Counter(widths) == aud.as_profile(spec['providers']['gauge44']['inventory']), k + ' SPEC inventory')
        idle = aud.as_profile(spec['expected']['idle_remainder_profile'])
        owned = aud.audit(geo, widths, local, roles, plan, idle, T)
        require(owned['profile'] == aud.as_profile(plan['profile']) == aud.as_profile(spec['expected']['global_profile']), k + ' PLAN/SPEC profile')
        result = read(p / 'RESULT.json')
        require(owned['profile'] == aud.as_profile(result.get('complex_profile', plan['profile'])), k + ' RESULT profile')
        require(owned['idle'] == {int(r): n for r, n in result.get('idle_remainder_profile', spec['expected']['idle_remainder_profile']).items()}, k + ' idle profile')
        controls = aud.controls(geo, widths, local, roles, plan, idle, T)
        names = [c['name'] for c in controls]
        top = {}
        for z in roles:
            b = (z['owner_replica'], z['child'], z['port']); top[b] = max(top.get(b, 0), z['offset'] + z['width'])
        slack = any(used < geo['rank'][b[1]] for b, used in top.items())
        if slack:
            require(len(controls) == 11, k + ' eleven controls')
        else:   # every occupied bin is full: no last slice can be shifted up, so the auditor's prefix_gap control has no instance
            require(len(controls) == 10 and 'prefix_gap' not in names and all(1 for n in ('drop_role', 'narrow_width', 'duplicate_helper', 'private_family', 'active_pair', 'family_collision', 'past_idle_sweep', 'overlap', 'claimed_idle_tampered', 'plan_window_truncated') if n in names), k + ' ten controls on a map without partially filled bins')
            controls.append(dict(name='prefix_gap', rejected_by=None, not_applicable='no occupied bin has slack: every bin of this map is full or empty'))
        c = dict(pr=1175, head=k, profile={str(r): n for r, n in sorted(owned['profile'].items())}, live=896 * T, calls=9 * T,
                 complex_lower=asm['complex_lower'], record_kappa=asm['kappa'], claimed_kappa_decimal=KAPPA[k], bit_lower=asm['bit_lower'])
        priced = sweep.price(c)
        for key in ('endpoint_certified', 'deficit_equals_W_minus_64N', 'halving', 'record_bit_is_pr589', 'kappa_equals_record', 'kappa_equals_title'):
            require(priced[key], '%s pricing: %s' % (k, key))
        owned['width_inventory'] = {str(r): n for r, n in sorted(Counter(widths).items())}
        owned['local_profile'] = {str(r): n for r, n in sorted(local.items())}
        out[k] = dict(package=rel, T=T, owner=owned, controls=controls, price=priced)
        print('PASS', k, 'T', T, 'idle', owned['idle'], 'kappa', priced['kappa_exact_decimal'], flush=True)
    res = dict(status='PASS_INDEPENDENT_OWNERS_AND_PRICE_SIX_PACKAGES', packages=out,
               auditors=dict(owners='research/t16-owner-audit-seed67/verify.py (Josie Elliston; rules R1-R7, X1, X2, 11 controls)',
                             price='research/pending-claims-independent-pricing/sweep.py (Sagar Thakrar; code-disjoint endpoint and kappa)'),
               scope='Both auditors applied unchanged to the five single-provider packages of PR #1175, the pricing to the two-provider package as well; their inherited-interface scope is not extended.')
    a.output.write_text(json.dumps(res, indent=1, default=lambda o: {str(k): v for k, v in o.items()}) + '\n')
    print(res['status'])


if __name__ == '__main__':
    main()

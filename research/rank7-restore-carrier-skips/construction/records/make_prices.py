"""construction/STAGE-PRICES.json: search-time certified prices (lane A / lane RW, r14) as evidence; argv[1] = output path."""
import json, sys
from pathlib import Path
S = Path('S')
A = S / 'r14/agents/A-extract/out'
C = {1: 2116671, 2: 4228346, 3: 6338140, 4: 8446713, 5: 10554378, 6: 12661320, 7: 14767661, 8: 16873488, 9: 18978865}
BE = 2091300
GROUPS = {'V45': [256, 128, 64, 35, 16, 11, 5], 'A': [256, 128, 64, 38, 20, 10, 1], 'B': [256, 128, 64, 34, 17, 11, 4],
          'C': [256, 128, 64, 32, 19, 11, 6], 'D': [256, 128, 64, 37, 21, 8, 3]}
HS = {'V45': [249, 251, 265, 267], 'A': [331, 450, 451, 508, 509], 'B': [299, 448, 449, 484, 485], 'C': [452, 453, 532, 533], 'D': [454, 455, 556, 557]}
joint = json.load(open(A / 'lowerA-joint.json'))
vl = json.load(open(A / 'V2942-base-vlower.json'))
groups = []
for g, W in GROUPS.items():
    if g == 'V45':
        full = next(r for r in vl if sorted(r['Q']) == HS[g])
        singles = {str(r['Q'][0]): r['margin_vs_k_BE'] for r in vl if len(r['Q']) == 1}
        groups.append(dict(group=g, W=W, helpers=HS[g], singles_margin=singles, joint_delta=full['delta_units'], joint_margin=full['margin_vs_k_BE'],
                           subsets=[{'helpers': sorted(r['Q']), 'delta': r['delta_units'], 'margin': r['margin_vs_k_BE']} for r in vl]))
    else:
        r = next(r for r in joint if r.get('W') == W)
        assert sorted(r['helpers']) == sorted(HS[g])
        groups.append(dict(group=g, W=W, helpers=HS[g], singles_margin={str(h): m for h, m in zip(r['helpers'], r['singles'])},
                           joint_delta=r['joint_delta'], joint_margin=r['joint_margin']))
for g in groups:
    assert g['joint_margin'] == -g['joint_delta'] - len(g['helpers']) * BE, g
unions = [dict(Ws=r['union'], helpers=r['helpers'], joint_delta=r['joint_delta'], joint_margin=r['joint_margin']) for r in joint if 'union' in r]
unused = [dict(W=r['W'], helpers=r['helpers'], margin=r['joint_margin']) for r in joint if 'W' in r and r['W'] not in GROUPS.values()]
s1 = sum(g['joint_delta'] for g in groups)
assert s1 == -46150994
out = {
 'note': 'Search-time pricing with the certified frame solver (r12 harness on the #1186 toolkit, exact chain dual decomposition) by lanes A and RW of round r14; units of 2^-40 at the base saving b. Evidence only: the claim rests on verify.py, check_allocation.py, check_cap.py and the complete admission. verify.py recomputes the literal stage prices from the frame-report profiles with these weights and checks them against this table.',
 'weights': {'c': {str(k): v for k, v in C.items()}, 'b': '0.001703676387993676', 'definition': 'c_r = floor(2^40 * T_r(b)), the solver integer surrogate of the per-child moment term of rank r',
             'break_even': BE, 'break_even_definition': 'the round value guide: local saving that buys one freed width unit at fixed packing (about c1 - 25,371); margins below are -delta - k * break_even'},
 'stage1': {'groups': groups, 'pairwise_unions': unions, 'unused_single_W_groups': unused, 'literal_price_units': s1, 'freed_width_units': 22,
            'margin': -s1 - 22 * BE, 'groups_independent': all(u['joint_delta'] == sum(g['joint_delta'] for g in groups if g['W'] in u['Ws']) for u in unions if all(w in GROUPS.values() for w in u['Ws'])),
            'leave_one_out_reported': 'lane A (combine.py, base provider): leaving any single helper out of its group costs 23,490 .. 25,371 units, so every member contributes; not stored per helper',
            'candidates': 'necessary condition: the lowered end frame W must contain L_h, the solver lower bound at h\'s last vertex; over all 86 restored helpers exactly 20 (end dim 8, L_h dim 7, W = L_h) plus PR2942\'s four pivots qualify; no helper has slack for a two-dimension lowering'},
 'stage2': {'steps': [dict(step=1, normal=42, helper=226, delta=-2101683), dict(step=2, normal=42, helper=228, delta=-2106679), dict(step=3, normal=42, helper=230, delta=-2101683),
                      dict(step=4, normal=7, helper=363, delta=-2106679), dict(step=5, normal=7, helper=395, delta=-2106679)],
            'literal_price_units': -10523403, 'freed_width_units': 5, 'margin': 10523403 - 5 * BE,
            'kopt_on_stage1_word': {'7': {'margin': 30758, 'k': 2, 'X': [5, 73, 363, 395], 'P': [363, 395]}, '42': {'margin': 26153, 'k': 3, 'P': [226, 228, 230], 'realized_margin': 36145},
                                    '25': {'margin': 20766, 'k': 2, 'P': [232, 363], 'note': 'conflicts with normal 7 (shares pivot 363)'}, '52': {'margin': 20766, 'k': 2},
                                    '76/82/97/127': {'margin': -34529}, '486/504': {'margin': -29645}},
            'recensus_after_stage2': {'7': 'pairing rank 0', '42': 'pairing rank 0', '52': 'pairing rank 0', '25': {'margin': -34529, 'k': 1}},
            'on_parent_without_stage1': 'kopt on PR2942 words: best margin -29,645 (486/504); no positive normal'},
 'stage3': {'rewrites': {'5997': -4996, '6000': -4996, '6004': -4996, '6008': -4996, '3779': -3102, 'swap3749': -3102, 'swap3755': -3102, 'swap3761': -3102,
                         'swap3767': -3102, 'swap3773': -3102, '1564': -6877, '1569': -6877, '4604': 0, '4630': 0},
            'literal_price_units': -52350, 'additive': 'the composed delta equals the sum of the single-rewrite deltas, the same -52,350 as on PR2917 and PR2942 words',
            'credit': 'rewrites by Jeremy Kothe (jeremykothe2), PR2957; re-addressed to this word with exact preimages by our lane RW'},
 'codim2_census': {'subspaces': 43435, 'theorem': 'a 7-dim V lies in exactly three hyperplanes E_n1, E_n2, E_(n1 xor n2), and the admissible pairing at V restricts the pairing at each of them, so a fresh helper can pair at V only if all three normals pair',
                   'rows': [{'word': 'PR2894 parent (literal frames)', 'normals_with_pairing': [52, 76, 82, 97, 127, 486, 504], 'V_all_three': 0, 'V_nonzero': 0},
                            {'word': 'PR2917 (lowered frames)', 'normals_with_pairing': [7, 25, 42, 45, 52, 76, 82, 97, 127, 486, 504], 'V_all_three': 4,
                             'V_nonzero': 1, 'V': [256, 128, 64, 35, 16, 11, 5], 'note': 'V45 = E_7 n E_42 n E_45, prank 4: the normal-45 structure itself'},
                            {'word': 'PR2942', 'normals_with_pairing': [7, 25, 42, 52, 76, 82, 97, 127, 486, 504], 'V_all_three': 0, 'V_nonzero': 0},
                            {'word': 'stage 1 (L22)', 'normals_with_pairing': [7, 25, 42, 52, 76, 82, 97, 127, 486, 504], 'V_all_three': 0, 'V_nonzero': 0}],
                   'pr2918_consistency': 'at E7 = (256,128,66,36,22,8,1) on the PR2894 parent: non-restored R_V = {105, 408}; with restored helpers allowed R = {105,307,309,314,369,371,373,378,408,572,573}, |H| = 226, dimA = dimB = 0, as RossRichardson\'s PR2918 (research/helper408-rank7-pairing)'},
 'caps': {'PR2942': '0.0017228172707428495209099', 'stage1': '0.0017262265796413098725813', 'stage2': '0.0017278107473204236839366', 'stage3': '0.001729035764875516181444'},
 'total': {'literal_price_units': -46150994 - 10523403 - 52350, 'freed_width_units': 27, 'margin': 46150994 + 10523403 + 52350 - 27 * BE},
}
assert out['stage1']['groups_independent']
Path(sys.argv[1]).write_text(json.dumps(out, indent=1) + '\n')
print('margins', out['stage1']['margin'], out['stage2']['margin'], out['total']['margin'])

# RECORDED results: asserts the headline counts in the shipped long-run logs (evidence/logs/), which verify.sh does NOT re-run by default.
import os, re, sys
L = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'evidence', 'logs')
ok = True
def has(f, pat, name):
    global ok
    t = open(os.path.join(L, f + '.txt')).read(); c = re.search(pat, t) is not None; ok &= c
    print(('PASS ' if c else 'FAIL ') + 'recorded ' + name + '  [' + f + ']')
has('cnt_P112.log', r'uncertified single classes 8 sizes \[56(, 56){7}\]', 'P112 census: 8 survivor classes of 56 lines')
has('cnt_P112.log', r'2-dim orbits 71 ', 'P112: 71 orbits of 2-dim label subspaces')
has('cnt_P112.log', r'\nDONE \d+\n?$', 'P112 census ran to completion')
has('cnt_P104.log', r'uncertified single classes 16 ', 'P104 census: 16 survivor classes')
has('cnt_P104.log', r'\nDONE \d+\n?$', 'P104 census ran to completion')
has('cnt4_P112_2.log', r'histogram of max k over orbit reps \[\(-1, 6\), \(2, 1\), \(3, 8\), \(4, 12\), \(5, 13\), \(6, 20\), \(7, 11\)\]', 'dim-2 max k <= 7')
has('cnt4_P112_3.log', r'\(5, 37\), \(6, 11\)\]', 'dim-3 max k <= 6')
for D, n in ((4, 417), (5, 2035), (6, 3498)): has(f'cnt6_P112_{D}.log', rf'DONE D {D} residue subspaces {n}\n?$', f'cnt6: D={D} -> {n} subspaces admit k >= max(2, 9-D)')
for D, n, r in ((2, 65, 8), (3, 217, 1), (4, 417, 17), (5, 2035, 0), (6, 3498, 0), (7, 6, 0), (8, 1, 0)):
    has(f'cnt7_P112_{D}.log', rf'DONE D {D} subspaces {n} residue configurations {r}\n', f'cnt7: d0={D}: {n} subspaces, {r} class-level residue configurations')
    has(f'cnt8_P112_{D}.log', rf'DONE D {D} alive after support filter 0\n?$', f'cnt8: d0={D}: 0 survive the support filter')
has('cnt9_P112.log', r'compatible \(rep, plane\) pairs 41\n', 'cnt9: 41 compatible (rep, plane) pairs')
has('cnt9_P112.log', r'DONE multi-big: big configurations 41 alive after J \+ support filter 0\n?$', 'cnt9: 41 multi-big configurations, 0 survive')
has('cnt9b_P104.log', r'compatible \(rep, plane\) pairs 413\n', 'cnt9b: 413 compatible pairs (P104)')
has('cnt9b_P104.log', r'DONE multi-big: big configurations 701 alive after J \+ support filter 0\n?$', 'cnt9b: 701 multi-big configurations, 0 survive (P104)')
print('ALL PASS' if ok else 'SOME FAIL'); sys.exit(0 if ok else 1)

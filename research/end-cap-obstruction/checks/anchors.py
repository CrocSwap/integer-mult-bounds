"""Anchors of the rules the theorem uses: every quoted file:line is read from the vendored copy and must contain the quoted text.
Prints one PASS/FAIL line per anchor; exits 1 on any FAIL.   usage: anchors.py   (EO_ROOT = the work tree)"""
import os, re, sys
R = os.environ['EO_ROOT'] + '/inputs/repo/'
GK = 'research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/complex-local/static44/gk/gk_word.py'
AL = 'research/gauge44-slots/independent/audit_local.py'
MO = '../spec/03-motifs.tex'
LA = '../spec/05-layers.tex'
SW = '../spec/04-swap.tex'
FL = 'research/format-limits-corrected/README.md'
A = [
 ('R3 gk_word.py:102', GK, 102, 102, r"assert basis\(list\(o\) \+ list\(F\)\) == F, \('frame violation'"),
 ('R1 gk_word.py:116 (both ADD operands climb)', GK, 116, 116, r"for r in \[e\[1\]\] \+ \(\[e\[2\]\] if e\[0\] == 'add' else \[\]\): climb\(r, e\[-1\]\)"),
 ('E  gk_word.py:117 (final climb to perp of the target port)', GK, 117, 117, r"climb\(r, FULL if \(r < V or r >= 2 \* V\) else perp\(P\[r - V\]\)\)"),
 ('E  audit_local.py:115 (target end = perp of its port)', AL, 115, 115, r"end=\[full\]\*v\+\[basis\(\[x for x in range\(1,1<<h\) if \(x&p\)\.bit_count\(\)%2==0\]\) for p in w\['ports'\]\]\+\[full\]\*R"),
 ('E  audit_local.py:116 (arbitrary ends: helpers only)', AL, 116, 116, r"for q,U in w\.get\('helper_final',\{\}\)\.items\(\):end\[int\(q\)\]=basis\(U\)"),
 ('R3 audit_local.py:122 (frame not monotone)', AL, 122, 122, r"require\(contained\(cur\[q\],U\),'frame not monotone '"),
 ('R1 audit_local.py:137-138 (every register of the op climbs to e[-1])', AL, 137, 138, r"for e in w\[section\]:\n\s*for q in registers\(e\):climb\(q,e\[-1\]\)"),
 ('E  audit_local.py:142 (final climb to end)', AL, 142, 142, r"for q,U in enumerate\(end\):climb\(q,U\)"),
 ('R1 audit_local.py:88 (no non-target reads a target)', AL, 88, 88, r"non-target reads target"),
 ('R1 03-motifs.tex:157 (one frame per gate incidence)', MO, 155, 158, r"incoming and outgoing\s+incidences of one gate use the same \$D_v\$"),
 ('R2 03-motifs.tex:568 (complex-motif-interface)', MO, 568, 568, r"prop:complex-motif-interface"),
 ('R2 03-motifs.tex:625-668 (sink operator C_{U_sink} C_{U_src}^{-1})', MO, 625, 668, r"Applying \\eqref\{eq:common-frame-identity\} with \$D_v=\\mathcal C_\{U_v\}\$"),
 ('R2 05-layers.tex:141-154 (recursive contract)', LA, 141, 154, r"The exact recursive contract"),
 ('R2 04-swap.tex:117-121 (finite-shear-contract)', SW, 117, 121, r"eq:finite-shear-contract"),
 ('R2 format-limits-corrected C.3 (Lemma R)', FL, 454, 454, r"\*\*Lemma R\.\*\* If the sources whose content reaches target t drop-free span u_t\^⊥"),
 ('R2 format-limits-corrected row 6 (class C)', FL, 294, 294, r"Terminal labels X_a: U_a → F, Y_a: 0 → U_a\^⊥; targets inside u_t\^⊥ \| C"),
 ('R3 format-limits-corrected row 3 (nesting: C, priced)', FL, 291, 291, r"Nesting: climbs along a register's life.*C \(priced, not forbidden\)"),
 ('R1 format-limits-corrected row 1 (common frame: S)', FL, 289, 289, r"Common frame at every gate \| S \|"),
 ('C.6 format-limits-corrected (pairing unique at window <= 9)', FL, 47, 47, r"label pairing B = W·Uᵀ is unique"),
]
bad = 0
for name, f, a, b, rx in A:
    lines = open(R + f, encoding='utf-8').read().split('\n')[a - 1:b]
    ok = re.search(rx, '\n'.join(lines), re.S) is not None
    print(('PASS ' if ok else 'FAIL ') + 'A.' + name)
    bad += not ok
sys.exit(1 if bad else 0)

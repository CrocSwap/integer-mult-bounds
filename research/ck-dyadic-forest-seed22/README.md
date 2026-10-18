# Independent corroboration of the CK all-dyadic forest floor

**Independent verification of a scoped negative result; no new kappa.** The historical CK
target-forest minimum remains **16,364 primitives per scalar component** when
each parent coefficient may be any nonzero dyadic, under the fixed independent
binary-Horner price and forest schedule. Both real components cost 32,728.

This independently checks the gap explicitly left by PR964.
It uses PR961's all-dyadic reduction and same-parent exchange method on CK,
rather than claiming that method or PR816's original circuit savings as new.
The checked CK census is not a rerun of the X4 matrix. In particular **941
nonunit edges beat a root**, but all are dominated by a signed-unit relation
to the same parent. The minimum nonunit margin against the best such
alternative is **63**, across **13,476,288** nonunit comparisons.

Run from the repository root, offline with standard-library Python 3.10+:

```sh
python -I -B research/ck-dyadic-forest-seed22/verify.py
python -I -O -B research/ck-dyadic-forest-seed22/test_package.py
```

The first command reconstructs the complete census and spanning-tree
certificate, invokes the separate integer checker and compares the frozen
receipt. Expected final marker:

```text
PASS_CK_DYADIC_FOREST cases=13501152 minimum_margin=63 floor=16364 no_new_kappa
```

The [proof](PROOF.md) gives the complete bill, infinite-tail reduction and
scope. [RESULT.json](RESULT.json) contains the finite certificate;
[SOURCES.json](SOURCES.json) binds the two mathematical input files and source
heads. [CLAIM.md](CLAIM.md) records assignment seed22, three candidates,
overlap selection and stopping rule. [VALIDATION.md](VALIDATION.md) records
executed verification and unrun gates. This package does not alter the selected
frontier, which at the base is PR890 with conditional kappa
0.001661957774647029.

Exact base: `007664306fff84fbb1c9a1b4053b69f439764034`.
At the final metadata refresh, main was
`dadfea6e8a78ff6ba901705f87532a71c6f5bbb8`, selecting PR1094 at conditional
kappa 0.001672660197076918. Both consumed CK inputs are byte-identical to the
base. This historical result neither depends on nor changes that selection.

The final overlap refresh found **Adam Gall's concurrent
[PR1220](https://github.com/CrocSwap/integer-mult-bounds/pull/1220)** at
`9cd42fb94d2b74e7308ad783b20081aa85b868a1`, which already reports the same
mathematical result. No priority or additional coefficient-domain coverage is
claimed here. This package adds independently written scalar-arithmetic
checks without its 16/20-bit packed cost lanes, an independent full ordered
census digest, and a Windows/minimal-tree/recompression replay. PR1220's
pinned receipt agrees on the domain, extrema, witnesses and floor. No PR1220
executable code was consumed; its receipt was inspected only after both
implementations here agreed. This is corroborating evidence that can be
reviewed alongside that PR, not a proposed replacement of its contribution.

Credit **dd-hemant PR816** for the CK signed-unit forest and its attained
floor; **woklerx PR961** for the all-dyadic cutoff and exchange method on X4;
**Gareth Davidson (bitplane) PR964** for the CK power-weight exclusion and
**ToikY PR909** for earlier tail work;
**Ross Richardson PR932** for the X4 forest; **Oscar Fennell PR759** and
**Sricharan Vagvala PR749** for predecessor forest/restored-pair mechanisms.
Credit **Adam Gall PR1220** for the concurrent same-result contribution.
The CK supplier lineage includes **Jeremy Kothe**, **Chafik Boukhalfa**,
**icekylinx**, and the contributors retained in the source notices and
repository CONTRIBUTORS.md. Pending PR961/964 executable code is not imported.

Prepared for **Lauren with substantial OpenAI Codex assistance** in research,
code, independent implementation, proof review and writing. Both checkers and
the review are AI-assisted; no independent human review is claimed. New files
are licensed under the repository's Apache-2.0 license. The inherited
all-size/compiler, realization, hosting, precision/tape, analytic and bit
interface assumptions remain; finite checking is not a full theorem proof.

## Publication scope and open next questions

Scope is **unchanged**: the historical CK matrix, all nonzero dyadic parent
weights and the declared one-parent forest cost model. Publication status is
independent corroboration after the PR1220 overlap was identified. Assignment
seed22 predates the current task-card workflow; no reassignment is claimed.

**Open next questions: none justified by this corroboration.** It supplies
independent evidence for the existing scoped result, without a new mechanism
that would justify reopening the closed coefficient search. The exclusions
listed above remain scope limits, not proposed investigations.

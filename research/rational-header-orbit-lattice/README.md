# Rational header orbits need an integer-lattice invariant

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof with exact finite corroboration.
For normalized saturated headers on Q^n, n even, in one fixed rational
symplectic form, the exact Hurwitz-equivalence criterion is

```text
T ~ T'  iff  L(T) = L(T') and C(T) = C(T'),
L(T) = sum_i Z x_i,
C(T) = multiset {x_i + 2L(T)} in L(T)/2L(T).
```

The integer lattice is embedded in the original rational coordinate
space. The two residue multisets must be compared in that same lattice.
Rational changes of frame are not allowed as extra equivalences.

DreamingOfClouds's [#6842](https://github.com/CrocSwap/integer-mult-bounds/pull/6842)
classifies the integral case and explicitly leaves non-integral frames
outside its scope. Its structure and integral classification are cited
premises. The new step is the embedded-lattice invariant, the transport of
that classification to rational headers, and an infinite counterexample
to using only ambient mod-2 data in the 2-local domain.

For every positive odd integer m, in the fixed form [[0,-1],[1,0]], take

```text
x_0 = (1/m,0),  x_1 = (0,m),  x_2 = (-1/m,m),
y_i = x_i^T omega,  U_i = I-2x_i y_i.
```

These are normalized headers with U_2 U_1 U_0 = -I. All have the same
ambient reduction {(1,0),(0,1),(1,1)} modulo 2 and covolume one.
Their lattices (1/m)Z e_0 + m Z e_1 are pairwise distinct, so their
Hurwitz orbits are pairwise distinct. In dimension two the lattice alone
is also sufficient. [PROOF.md](PROOF.md) gives the universal argument.

## Evidence and reproduction

The standalone exact checker enumerates new rational instances only:

- Twelve rational initial headers, dimensions 2, 4, 6 and 8, followed
  through 16 literal Hurwitz moves each. All 192 steps preserve the
  lattice and intrinsic residues and pass the full header product.
- Sixteen odd-denominator headers, m = 1,3,...,31. All 120 pairs have
  distinct embedded lattices despite identical ambient mod-2 data.
- One rational dimension-four pair has the same lattice but different
  intrinsic residue multisets. This demonstrates why the second
  invariant is still required when the lattice is fixed.
- Five rejection controls cover singular bases, even denominators,
  vectors outside the chosen lattice, an invalid move and an altered
  normalized header.

From the worktree root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/rational-header-orbit-lattice/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/rational-header-orbit-lattice/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/rational-header-orbit-lattice
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/rational-header-orbit-lattice --check-source-history
```

Another CPython 3.12 path may be substituted. The direct marker is
`PASS_RATIONAL_HEADER_ORBIT_LATTICE`; the registered runner prints
`PASS_REGISTERED_RESEARCH_PACKAGE`. The final command checks committed
publication bytes and source history. The verifier accepts no arguments,
writes no files and prints a generated receipt bound to SHA256 hashes of
all six package files. There is no handwritten or committed receipt.
It also runs in a Git-free export of these six files.

## Scope, provenance and credit

Base is canonical main e54523517d0f03e58352e647c403a5af3e525a57, priority
revision 8. The selected #7000 record, not the older narrative checkpoint,
is the baseline. Its cheap binding orientation passed; its scientific
replay was not run. The formal-interface-lemma card changes scope to this
algebraic side result. It does not discharge a selected assumption.

[The advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19538524)
records the rational-header question. Live PRs, recent account submissions,
handoffs, local reservations, distinctive main README searches and merged
searches were checked. The overlap snapshot covered 477 open PRs and
7,129 Discussion records with complete pagination; sparse local notes
were incomplete. These checks do not establish absence of unpublished work.
No open PR studying this rational-header equivalence was found.

Credit DreamingOfClouds #6842 for normalized header structure, Hurwitz
action, the integral theorem and this excluded domain; #6832/#6833/#6836,
CubeJerry #6839/#6840 and zxv #6726 retain its root lineage. Brendle and
Margalit's *The level four braid group*, Theorem 3.3(1), supplies the
cited higher-dimensional pure braid image, with A'Campo credited there.
The dimension-two elementary-generation argument is written here.
Lattice transport and the Euclidean algorithm are classical; no
literature-wide priority is claimed. SOURCES.json pins predecessor texts
as provenance. No predecessor code is imported or scientifically replayed.
All predecessor files and credit lines remain unchanged.

The classification assumes normalized headers, the same rational form,
exactly n+1 square-zero rank-one units and only the stated Hurwitz moves.
It is not an orbit classification under rational conjugacy, a bounded
word-length result or a constructive braid-synthesis algorithm. Its
sufficiency cites the integral theorem; the lattice obstruction itself
does not need that input. The finite checks corroborate the new instances;
the written proof supplies the universal and infinite claims.

No new kappa, native supplier, legal site-mask program, physical frame
conversion, complete paid/target bill, compiler closure, precision/tape
or stock bound follows. No selected cold replay, Lean, Docker or complete
multiplication theorem was run or claimed. Independent human and formal
proof-kernel review are unclaimed.

## Open next questions

Can a physically legal rational frame change join two distinct header
lattices at a favorable complete cost? Begin with one literal root and
conversion, charging dirty restoration, every native conversion, movement
and target effect. The present invariant rules out a Hurwitz-only route;
it does not price a changed operation alphabet. TASK.json records the
first step and the missing physical contract. Research stops at the
classification and explicit infinite family.

## Verifier constraints

Power of Ten inspection covers the single new Python file. Functions
are below 60 lines. The fixed computation has matrices of dimension at
most nine, 12 walks of exactly 16 steps and 16 family members. There is
no recursion, subprocess, network, dynamic code execution or external
scientific dependency. State is local, checks use explicit exceptions,
and warning-strict normal and optimized modes are registered. Six hash
reads are capped at 256 KiB each, and the verifier rejects CLI inputs.

Rule 3 has a managed-runtime deviation. CPython allocates exact integers,
Fractions and containers dynamically; the fixed fixtures and bounded
walks bound algorithmic collections. Interpreter allocation has not been
instrumented, and a fixed-storage implementation would require separate
work. Rule 10 uses the registered warning-strict executions and AST
inspection; no separate static type checker or proof assistant is claimed.

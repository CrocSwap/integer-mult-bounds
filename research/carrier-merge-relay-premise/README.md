# Audit the source-normal premise in relay-enabled carrier merges

The merge lemmas in CrocSwap/integer-mult-bounds#6315 explicitly require source
subspace retention and/or full union span. Its broad abstract information-walk
model permits public-relay shrinking, which does not imply those hypotheses.
Using the actual selected #6030 geometry, this package gives receiver-covering
countermodels to that **frame-only implication**, and proves the corrected bound

`total + (k-1)*tail >= 7k + sum(eta_c)`.

Each `eta_c` is zero or one according to whether that carrier's union escapes
its receiver hyperplane. Source-normal retention recovers the predecessor's
`8k` right-hand side. **No new κ.**

This is a precise missing-application-lemma audit, not a false Lean theorem,
a cheaper physical network, a counterexample to the pair floor 14 or owned
floor 56, or an exclusion of triple merges. All five selected framework
assumptions remain. A pure-carrier relay with arbitrary dirty restoration is
not constructed or assumed free.

## Evidence and reproduction

Canonical base: `2485805a6d47f36ea83ddde6327d453ac82d44dc`.
Audited #6315 head: `3667554dab1bf08bb9ce6c267b6047fdc9978498`.
Base sources are pinned in [SOURCES.json](SOURCES.json); the exact predecessor
head, original Git paths and retained-byte hashes are in
[PREDECESSOR.json](PREDECESSOR.json), itself pinned by the verifier.
Five relevant predecessor files are retained verbatim under `inputs/`; their
authors and notices are unchanged. The selected word is a declared live input.

From the repository root, with CPython 3.12 and the standard library:

```sh
python3 -B scripts/research_package.py --package research/carrier-merge-relay-premise
```

Expected: `PASS_CARRIER_MERGE_RELAY_PREMISE subsets=247 controls=11` in both
normal and optimized modes, followed by `PASS_REGISTERED_RESEARCH_PACKAGE`.

[PROOF.md](PROOF.md) identifies the exact Lean hypotheses and gives the general
repaired proof. [RESULT.json](RESULT.json) is the exact replay receipt. The
independent implementation uses finite sets of binary vectors and imports no
predecessor executable. It checks:

- All eight source-normal/receiver hyperplanes against the 104 selected ports.
- Every one of 247 carrier subsets, including 28 pairs and 56 triples, with
  source roots, nested moves, all 52 receivers per carrier, common merge,
  paid growth seven, and explicit failure of `hG` and `htop`. Two further pair/triple
  fixtures use the actual selected Y112 endpoint chart with nonzero merge dual `<11>`.
- Seven source-normal-preserving controls that attain the `8k` dimension count;
  these controls also test only the frame-walk algebra, not scalar decoding.
- All 2,457 applicable tuples in the enumerated 16-subspace lattice of
  `F2^3`, corroborating both values of the repaired excess indicator.
- Eleven rejection controls: wrong paid amount, missing source, illegal nonnested
  step, missing receiver growth, false pair/triple hypotheses, unjustified
  `8k`, an invalid merge line, and a Boolean disguised as an integer cost.

To regenerate the canonical receipt without changing repository files:

```sh
python3 -I -W error -B research/carrier-merge-relay-premise/verify.py --output /absolute/new/external/result.json
```

The output path must be new and outside the checkout. Finite replay corroborates
the written dimension argument; it is not a proof-kernel verification of it.

## Scope and limitations

The exact countermodel is `line(g_c) -> H_c -> 0` in dual frames. It grows at
cost seven, serves every receiver in `H_c`, then shrinks freely to the common
merge. Such a frame path does not specify how to remove a public helper's
arbitrary dirt. Its scalar feasibility, decoding and restoration invoice are
deliberately unresolved. A physical purity/restoration theorem might supply
the missing implication even though the frame rules alone cannot.

The correspondence of the source receipt's carrier code with the complete
selected word is inherited; the geometric facts used here are freshly checked.
The predecessor's pair-cover census, Lean build, full selected scalar/native/
caller replay and complete supplier invoice are not run as this deliverable.
No formal-kernel or human acceptance, supplier admission, or complete
multiplication theorem is claimed. See `VALIDATION.md` for executed release
checks and the independent review.

## Open next questions

The structured questions are in [TASK.json](TASK.json). The next useful task
is a physical relay with arbitrary-input purity and restoration, or a proof
that every admissible such relay satisfies the needed source-normal/full-span
conditions after all costs are charged. Only then should the broader
three-carrier search inherit those conditions. The corrected `eta_c` invariant
can be used immediately when the actual unions are known.

## Credit

Prepared for @CubeJerry with substantial OpenAI Codex assistance: worker B,
independent mathematical/source reviewer D, and lead review. Credit Matarener
for #6315, #6267 and the question; DreamingOfClouds for #6030; the fragmentation,
owned-boundary and carrier-uniqueness lineage retained in the source files; and
the classical subspace dimension identity. Apache-2.0. No predecessor result
is presented as a new theorem of this package.

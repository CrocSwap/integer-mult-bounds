# Plane-level signatures of invertible 4x4 bases: cancellations add none

**Scoped proof with exact finite corroboration; no new κ.** The selected result,
the selected suppliers and `upstream/` are unchanged.

[PR3997](../rational-joint-support-screen/README.md) (Gonzalo-Mier,
`research/rational-joint-support-screen`) prices a joint 4x4 basis on two planes
of two ports each from its **plane-level signature**. For each of the four
messages, the signature records which planes its source support (a column of P)
and its reader support (a row of P^-1) meet. PR3997 finds 439 signatures from
generic coefficients, the same 439 from all 3^16 signed ternary matrices, and
minimum copy invoice 8 on each of the 1,540 plane pairs. It leaves open whether
rational values outside {-1, 0, 1}, through exact cofactor cancellations, give a
signature outside those 439 and lower the invoice.

A later merged package, CubeJerry's
[PR4365](https://github.com/CrocSwap/integer-mult-bounds/pull/4365)
(`research/two-plane-copy-floor`), settles the *invoice* half of that question
more strongly. By a rank argument, the COPY mass on any two matched planes is at
least 8 for arbitrary coefficients, over every field, for any number of scalar
messages. It does not classify signatures. This package answers the structural
question: which plane-level signatures can an invertible basis have at all? The
invoice consequence below agrees with PR4365 and does not improve it.

**Answer to the signature question: no cancellation adds one.** Over any field,
the plane-level signature of an invertible 4x4 matrix lies in a set N of 439
signatures defined by three conditions. Over Q the signatures fill N exactly. N is
the set of signature codes recorded by PR3997. So no coefficient value, however
special, adds a signature to the 439.

## Result

1. **Exact parametrization (Lemma 1).** The signature of P depends only on the
   row spaces `W_A`, `W_B` of its top and bottom port pairs, two complementary
   2-planes of K^4. A source mask tests whether a plane lies in a coordinate
   hyperplane. A reader mask tests whether a coordinate vector lies in the
   *other* plane. Coefficient values enter only through these row spaces.
2. **Three necessary conditions (Lemma 2).** C1: no message has source mask {A}
   with reader mask {B}, or the reverse. C2: at most two messages are confined to
   one plane, on either side. C3: two confined messages on one side force the
   other two to be confined to the opposite plane on the other side. All three
   follow from Lemma 1; see [PROOF.md](PROOF.md).
3. **Tightness.** Exactly 439 of the 6,561 candidate signatures satisfy C1, C2
   and C3. Each is realized by an explicit integer matrix with entries in
   {-1, 0, 1}; [WITNESSES.json](WITNESSES.json) holds all 439, each checked by
   exact rational inversion.
4. **Consequence (not new).** PR3997's pricing is a function of the signature,
   and its `RESULT.json` records minimum 8 on all 1,540 plane pairs over these 439
   signatures. The same minimum therefore holds for every invertible 4x4 basis
   over any field, including every cofactor-cancellation stratum. PR4365 proves
   the stronger statement that 8 is a floor for arbitrary scalar factorizations.
   This is its signature-level counterpart.

## Evidence

| Check | Result |
|---|---|
| Candidate signatures | 9^4 = 6,561 |
| Pass C1, C2 and C3 | 439 |
| Pass two conditions (without C1 / C2 / C3) | 555 / 805 / 1,771 |
| Equal to the 439 codes in PR3997's `TERNARY-SCREEN.txt` | yes |
| Distinct planes spanned by two ternary vectors | 362 |
| Signatures of all their complementary pairs | 439, none outside N |
| Integer witnesses, exact rational inversion | 439 |
| F_2: planes / complementary pairs / signatures | 35 / 560 / 355 |
| F_3: planes / complementary pairs / signatures | 130 / 10,530 / 439 |
| F_5: planes / complementary pairs / signatures | 806 / 503,750 / 439 |
| F_7 (opt-in `--extended`): planes / pairs / signatures | 2,850 / 6,842,850 / 439 |
| Plane rule against direct inversion | every pair at F_2 and F_3; every 61st at F_5; every 997th at F_7 |
| Direct census of all of GL_4(F_2) | 20,160 matrices, the same 355 signatures |
| Rejection controls | 11 |

The finite-field counts follow from the formula `(q^2+1)(q^2+q+1)` planes and
`q^4` complements per plane. They corroborate Lemma 1 on every complementary
pair; the proof does not use them. Over F_2 only 355 of the 439 signatures occur,
so the statement "the realizable set is N" is a statement about Q and about fields
where all 439 occur (F_3, F_5 and F_7 by enumeration).

## Reproduce

From the repository root; the standard library suffices:

```sh
python3.12 -I -B research/two-plane-signature-classes/verify.py
python3.12 -I -O -B research/two-plane-signature-classes/verify.py
python3.12 scripts/research_package.py --package research/two-plane-signature-classes
```

Each verifier run takes a few seconds and prints
`PASS_TWO_PLANE_SIGNATURE_CLASSES`. It recomputes `RESULT.json` and
`WITNESSES.json` and compares their bytes. `--write` regenerates both. `--extended`
adds the F_7 enumeration (about 13 seconds) and compares nothing.

The verifier also binds to two committed PR3997 files by SHA256: its
`TERNARY-SCREEN.txt` (the 439 recorded signature codes) and its `RESULT.json` (the
recorded minimum 8 on 1,540 pairs). It does not recompute any plane pricing.

## Limitations

- The theorem concerns plane-level signatures of invertible 4x4 matrices with two
  planes of two ports. The finer joint zero pattern of P and P^-1, which the
  original question called the cofactor strata, is not classified. It is not
  needed for the invoice.
- The invoice consequence relies on PR3997's definition of the pricing (a function
  of the signature) and on its recorded minimum. This package does not rerun them.
  The invoice floor itself is PR4365's theorem; nothing here lowers or re-proves it.
- Three or more planes, overcomplete factorizations, coefficient scaling cost,
  physical routing and restoration, and any change to a selected supplier are
  outside scope, as they are in PR3997.
- No independent human or formal proof-kernel review is claimed. The finite checks
  corroborate Lemma 1; the proof is the written argument in [PROOF.md](PROOF.md).

## Open next questions

The structured versions, with relevance and blockers, are in
[TASK.json](TASK.json).

1. **Two planes of three ports (6x6).** Lemma 1 holds verbatim for two planes of
   d ports. Is the realizable signature set still the generic census for d = 3?
   First step: enumerate complementary 3-planes of F_2^6 (1,395 planes, 714,240
   complementary ordered pairs) by incidence data, and compare with the
   necessary-condition set. Blocker: the generic 6x6 census has 2^36 supports, so
   it needs an incidence-based generator.
2. **Three planes of two ports.** The reader test generalizes to "e_j is not in the
   sum of the other planes". Does a third plane make cancellation signatures
   possible? PR4365's first open question asks for a genuinely joint three-plane
   decoder and names 49 closure-pair tariffs, which appear to be the 7 x 7 source
   and reader masks of three planes. First step: the same enumeration over
   complementary plane triples in F_2^6. Blocker: 49^6 candidate signatures need
   symmetry reduction.
3. **Port-level pricing.** A model that reads which individual ports a support
   meets would see the finer zero patterns of P and P^-1. First step: classify
   pairs of supports `(supp P, supp P^-1)` for 4x4 matrices over F_3, where
   cancellation is plentiful. Blocker: no pricing model reading port-level
   supports has been written down.

## Credit

This package was produced by Nick Petalas. It answers the open question left by
Gonzalo-Mier's PR3997 (`research/rational-joint-support-screen`) and builds on its
signature model, its generic and signed-ternary censuses and its recorded pricing
result, and on the earlier binary screen of Gonzalo-Mier's PR3990. CubeJerry's
PR4365 proves the invoice floor for arbitrary scalar factorizations; it is cited,
not built upon. Apache-2.0.

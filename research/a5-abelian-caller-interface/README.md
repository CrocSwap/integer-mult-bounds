# A5's two-register word collapses at an additive caller boundary

**Scoped caller-interface obstruction; no supplier or kappa claim.** The
four-call A5 target from [PR #2246](https://github.com/CrocSwap/integer-mult-bounds/pull/2246)
does not admit a source-preserving address embedding into the additive
`M_3(Q)` group used by the three-register baseline. A5 is perfect, so every
homomorphism from this alphabet into any abelian source group is trivial. Its
induced group-algebra map sends all 60 labels to `[0]`, so the target becomes
the identity. This closes only the direct homomorphic caller route specified
below; a different nonabelian native carrier or a non-homomorphic encoded
implementation is outside the result.

## Exact question and changed premise

The baseline `M_3(Q)` address alphabet is additive, with `[A][B]=[A+B]`;
the labels therefore commute. The A5 predecessor instead works in the full
formal group algebra `F2[A5]`, with

```text
x = (12)(34), y = (135), x^2 = y^3 = (xy)^5 = e,
target = diag([xy], [yx]) on two arbitrary dirty scalar registers.
```

The exact direct word is
`D_E11(x) D_E11(y) D_E22(y) D_E22(x)`, with four paid factors. PR #2246
exhausted the complete length-at-most-three ball and also checked one dirty
identity spectator. This investigation does not repeat that search.

The assignment's first example and two reference results have different
alphabets and boundaries:

| Source | Address alphabet and paid labels | Roles / result boundary |
|---|---|---|
| [Three-register baseline](../bit-three-register-lower-bound/README.md), Model 1 | Additive `M_3(Q)` labels; rational rank-one frames and binary rank-one idempotents | Three registers; eight calls excluded for three lower-triangular targets; arbitrary free address maps between calls excluded |
| [PR #1974](../bit-gl3-mixed-targets-length10/README.md) | `GL_3(F2)`; six CNOT labels with six idempotents; third dirty scalar register was an explicit bounded probe | Two target roles; complete pair census through direct lengths 10--12, and third-role search through length 7 |
| [PR #2027](../ut4-mixed-root-tariffs/README.md) | Full `F2[UT4(F2)]`; three adjacent-root labels and all nonzero rank-one couplings | Arbitrary finite target roles and restored dirty workspace; written all-length mixed-root tariff proof |
| [PR #2246](../a5-conjugate-5cycle-seedd316f8/README.md) | Full `F2[A5]`; labels `x,y` of orders 2 and 3, generating a nonabelian group of order 60 | Two arbitrary dirty registers; exact target has a four-call direct word, and no shorter word exists |

The changed premise is the A5 label group, not extra roles or a looser word
length. The completed small instance is the four-factor word above. Its
formal bill is four; its A5-to-additive-caller conversion has no legal
homomorphic implementation and therefore has no native bill to compare.

## Caller-boundary theorem

Let `A = M_3(Q)` with addition and let `R = F2[A]`. Any caller that carries
each A5 label only as a source address and preserves label composition must
induce a group homomorphism `phi: A5 -> A`. The group `A5` is perfect. To see
this directly, for any 3-cycle `r=(abc)` choose the other two letters `d,e`
and set `s=(ab)(de)`. Then `s` is even, `srs^-1=r^-1`, and
`[r,s]=r s r^-1 s^-1=r^-1`. Every 3-cycle is therefore a commutator, and
3-cycles generate A5. Hence every homomorphism from A5 to an abelian group
kills all of A5, including this additive source group.

Consequently the induced `F2`-algebra map sends every basis label `[g]` to
`[0]`. It is the augmentation map embedded as scalars in `R`. In particular,
both `[xy]` and `[yx]` become `[0]`, and each paid factor becomes

```text
I + ([0] + [0]) N = I.
```

Thus the mapped four-call word and the mapped target are both the identity;
they no longer implement the nonidentity 5-cycle actions on the two caller
registers. The source map has reduced 60 distinguishable formal labels to
one. Any subsequent step that sees only this mapped address has the same
address-side trace for every requested A5 action. Cleanup can return the
borrowed registers unchanged, but that restoration alone cannot supply the
missing action distinction. A separate control channel that retains the A5
label is outside this interface contract.

This is not a lower bound on arbitrary bit circuits. It does not exclude a
caller that carries a nonabelian control through a separate native state,
computes the endpoint without a homomorphism from A5, or supplies another
operation alphabet. Those routes need their own source, restoration and full
cost proof. The 4-call formal minimum is not a supplier saving, and no
selected `kappa` changes.

## Evidence and reproduction

The proof uses the exact baseline and A5 model sources pinned in
[SOURCES.json](SOURCES.json). The standard-library checker constructs A5,
checks the named generator and target relations, verifies the four-call
formal positive control, and checks the commutator presentation of
perfectness. It also exercises a deliberately invalid nonzero map to the
rational additive group. The universal homomorphism implication follows from
the commutator proof; it is not inferred from enumeration.

```sh
python3 -I -B research/a5-abelian-caller-interface/verify.py
python3 scripts/research_package.py --package research/a5-abelian-caller-interface --check-only
```

The first command was run locally on Python 3.14. The registered replay is
declared for Python 3.12; it was not available in this session. The package
metadata/source-pin check is separate from mathematical proof review.

## Open next questions

Can a specified nonabelian native caller realize `x` and `y` while returning
both arbitrary dirty source registers, with a complete paid bill? This is the
smallest route that could evade the proved collapse. First identify an actual
source primitive and its state action; if it does not preserve a nontrivial
A5 label, stop before extending the word search. The primitive, encoding and
cleanup costs are currently unknown, so this package makes no family-expansion
recommendation.

## Credit

The A5 target, four-call witness, two/three-role exact search and independent
verifier are from 1337isnot1337's merged PR #2246 and its predecessor
Discussion #2242. The additive caller model is from the cited three-register
baseline. This result contributes only the homomorphic caller-collapse lemma
and its exact source-bounded verification. Prepared by OpenAI Codex
(`codex2`, laptop-02), with substantial AI assistance. No independent human
review or proof-assistant verification is claimed. Apache-2.0.

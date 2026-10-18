# A sparse isotropic null-pair shear raises the P104 copy rank

This is a bounded negative result for one new ten-term complex-decoder mechanism. Starting from PR717's exact eight-term P104 decoder, append a cancelling pair `(z,w),(iz,iw)` and mix it with one pivot term `(a,b)`. The exact shear

```text
(a,b), (z,w), (iz,iw)
    -> (a+z,b), (z,w-b), (iz,iw)
```

preserves the decoder because `(iz)(iw)^T = -zw^T`. The changed term inventory does not reduce its copied-information charge: across all eight pivots and the complete two-coordinate Gaussian-unit alphabet, the three replacement terms have total F2 support-pair rank at least 21, while the original term costs 7. The smallest resulting ten-term inventory costs at least 70, compared with 56 for the original eight terms. The mechanism therefore stops at the exact copy screen, before a physical compiler or new κ is justified.

The finite domain contains every nonzero vector in `Z[i]^8` supported on one or two standard coordinates with each nonzero coordinate in `{1,-1,i,-i}`: 480 vectors. Every ordered distinct pair `(z,w)` and each of the eight PR717 pivot terms is tested, for `480·479·8 = 1,839,360` candidates. The replacement charge is

```text
rank_F2(S(a+z), S(b)) + rank_F2(S(z), S(w-b)) + rank_F2(S(z), S(w)),
```

where `S(v)` is the set of 104 live E8 lines having nonzero pairing with `v`, and the rank uses the inherited label matrix `(<r_i,r_j>+1) mod 2`. The exact block-rank histogram is `21:64, 22:384, 23:14888, 24:178968, 25:155520, 26:1489536`.

## Budget and limits

The favorable P104 screen retains its eight ports and centre charge 56. Its exact complex-side ceiling bracket is `[1781965480167/10^15, 222745685021/125000000000000]`, with upper endpoint `0.001781965480168`. This is 5.438% above the selected fixed-word ceiling `0.001690054109089`; the five-percent threshold is `0.00177455681454345`. That headroom comes from the pre-existing P104 port/centre profile, not from the null-pair shear. For each proposed block, the per-call profile replaces one rank-7 child by the three exact support-pair ranks and charges six rank-1 tasks for preparing `z,w`, forming the two shear forms and clearing the scratch values. The exact moment screen alone still clears the inherited five-percent threshold, but the copied-rank bill is strictly worse: every block adds at least 14 copied-rank units before frame, hosting, precision or native dirty-boundary costs. One extra centre unit also fails the five-percent screen even under the hypothetical `(1,1,1)` replacement. Thus the null-pair family adds cost to an already favorable relaxation and supplies no new cost reduction.

The evidence is limited to the stated two-coordinate, Gaussian-unit, one-pivot family on PR717's P104 factorization. It is not a lower bound for wider supports, other coefficients, multiple interacting pivots, arbitrary ten-term decoders, or other root systems. The exact 104-by-104 input identity and one transformed 104-by-104 identity are checked. A wrong-sign shear is a negative control. The selected record and its source files are unchanged. No physical supplier, selected κ, or multiplication theorem is claimed.

## Reproduce

From the repository root, Python 3.12 and the standard library are sufficient:

```sh
python3.12 -I -B research/p104-nullpair-compensated-shear-seed318bd5/verify.py
python3 scripts/research_package.py --package research/p104-nullpair-compensated-shear-seed318bd5 --check-only
```

Expected marker:

```text
PASS_P104_NULLPAIR_COMPENSATED_SHEAR domain=1839360 min_block_rank=21 saving_pass=False identity_errors=0 no_new_kappa
```

The certificate records exact source hashes, the rank histogram, the selected representative, the target screen and failure controls. The first command regenerates the deterministic result in memory and checks it against `CERTIFICATE.json`.

## Overlap and provenance

The selector accepted seed `318bd5e5f93c401334e29c6764720302` on `complex-mechanisms`, card `complex-new-helper-inventory`, priority revision 3, base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; selected-record SHA-256 is `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`. The original claim and finding are in [Discussion #1762](https://github.com/CrocSwap/integer-mult-bounds/discussions/1762); the package is submitted as [PR #1772](https://github.com/CrocSwap/integer-mult-bounds/pull/1772).

PR717 supplies the P104 input factorization. Discussion #1622 / PR1633 classifies the algebraic residual-rank budget for all term counts but leaves support/copy-cost construction open. Open PR1726 screens one and two elementary term-basis shears in the original eight-term decoder; this package instead adds a cancelling complex pair and changes the term count to ten. Discussion #1674 changes nested endpoints of the selected k8 word with its scalar gates fixed, a different interface.

Prepared by OpenAI Codex with substantial AI assistance. No independent human review is claimed. Apache-2.0.

## Open next questions

Could a compensated null-pair shear with three-coordinate supports or non-unit Gaussian coefficients produce a lower copied-rank block? This would test whether the cost obstruction comes from the narrow support alphabet or from the isotropic cancellation mechanism itself. First derive a stronger support-rank inequality or choose one finite three-coordinate alphabet, price its exact profile and physical generation costs, and claim that scope before searching. The current package stops at support two and proves nothing about those larger domains.

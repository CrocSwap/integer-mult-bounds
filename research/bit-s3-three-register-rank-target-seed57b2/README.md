# A rank floor for one three-register S3 target

## Question and scope

In the finite nonabelian address algebra `R = F2[S3]`, let
`s = (12)`, `t = (23)`, with permutation products composed right-to-left. There
are three arbitrary dirty scalar registers. A paid call is

```text
D_N(g) = I + ([g] + [e]) N,    g in {s,t},
```

where `N` is any of the 28 rank-one idempotents in `M_3(F2)`. Each call costs
one. The endpoint is `diag([s],[t],[st])`; the direct word costs four.
Equality is in the full matrix algebra `M_3(R)`, so it specifies behavior on
arbitrary register inputs. This changes the address alphabet from the additive
rational frames of the three-register obstruction to the specified nonabelian
group `S3`; it keeps three registers and the optimistic one-unit call bill.

The target is distinct from the completed mixed `S3` triple census
`diag([z],[z],[c])` (with `z=sts`, `c=st`) and from the completed two-register
`S3` all-pairs census. The [three-register lower bound](../bit-three-register-lower-bound/README.md)
excludes arbitrary free *address* maps between paid calls; its model is
abelian. Here free scalar `GL_3(F2)` register mixing is allowed. It can be
pushed through each paid factor by conjugating `N`, which preserves rank one
and idempotence. Augmentation `[g] -> 1` sends all paid factors to identity;
the endpoint augments to `I`, so the net scalar boundary map is the identity.
This leaves the same normalized paid-factor identity.

The selected result remains the finite conditional construction at the exact
source bindings in [the selected record](../../../certificates/selected-result.json)
and [its review](../../../docs/research/community-batch1099-review.md). This
abstract finite group model supplies no address-source implementation or
selected-supplier cost.

## Result

**The minimum is exactly four paid calls for this endpoint in this model.**
The lower bound is a uniform identity argument; it does not enumerate words
or test only address columns.

Use the faithful two-dimensional representation `rho: S3 -> GL_2(F2)` given by

```text
rho(s) = [1 1]     rho(t) = [1 0]
         [0 1]              [1 1]
```

Then `rho(st) = [[0,1],[1,1]]`. The matrices `rho(s)+I` and `rho(t)+I` each
have rank one, while `rho(st)+I` has rank two. Extend `rho` linearly to the
group algebra and apply it entrywise to a putative identity in `M_3(R)`. A
paid factor becomes

```text
I_6 + N tensor (rho(g)+I_2).
```

Its difference from identity has rank
`rank(N) * rank(rho(g)+I_2) = 1` for both allowed generators. For arbitrary
matrices `P_j = I + U_j`, telescoping gives

```text
P_1 ... P_q - I = sum_j (P_1 ... P_{j-1}) U_j,
rank(P_1 ... P_q - I) <= sum_j rank(U_j) <= q.
```

The represented endpoint differs from identity by block diagonal blocks
`rho(s)+I`, `rho(t)+I`, and `rho(st)+I`; its rank is `1+1+2=4`. Therefore
every full group-algebra factorization needs at least four calls. The
representation is an optimistic quotient of the six-dimensional group
algebra: quotienting can lose constraints, but every formal identity must
still satisfy this rank bound.

The direct witness is

```text
D_E11(s) D_E22(t) D_E33(s) D_E33(t) = diag([s],[t],[st]),
```

so the lower bound is attained. Thus this named target has no sharing saving
under the stated unit-cost finite-address model.

## Reproduction and controls

Run from the repository root:

```sh
python3.12 -I -B research/bit-s3-three-register-rank-target-seed57b2/verify.py
python3.12 scripts/research_package.py --package research/bit-s3-three-register-rank-target-seed57b2 --check-only
```

The verifier rebuilds the six-element group and its representation, checks
the rank bound for every one of the 28 scalar idempotents and both paid
labels, verifies the exact rank-four endpoint image, multiplies the four-call
witness in the full `F2[S3]` matrix algebra, and rejects all four
single-factor omissions.

## Relation to prior work

- The three-register rational-frame obstruction uses the additive address
  group `M_3(Q)`, with nonzero rational rank-one frames and 28 scalar
  idempotents. Its Model section excludes free address maps between calls.
- PR [#1974](https://github.com/CrocSwap/integer-mult-bounds/pull/1974)
  completely censuses two-register `F2[GL_3(F2)]` coordinate-CNOT targets
  through length eleven and probes a third dirty register only through
  length seven. This result changes the address group and proves a uniform
  rank bound instead of extending that finite census.
- PR [#2027](https://github.com/CrocSwap/integer-mult-bounds/pull/2027)
  proves a uniform mixed-root tariff in `UT_4(F2)` with arbitrary dirty
  workspace. It uses a different group and root tariff.
- PR [#2010](https://github.com/CrocSwap/integer-mult-bounds/pull/2010)
  records the exact five-call minimum for one heterogeneous target in
  `F2[SL_2(F3)]`; Discussion [#2012](https://github.com/CrocSwap/integer-mult-bounds/discussions/2012)
  records the exact eight-call minimum for six other mixed three-register
  `S3` targets. Neither has endpoint `diag([s],[t],[st])`.
- The two-register `S3` census package is
  [`bit-s3-two-target-census-seed36501`](../bit-s3-two-target-census-seed36501/README.md).

The cached discovery results, live PR/thread refresh, exact overlap distinction,
and their time boundary are recorded in [OVERLAP.md](OVERLAP.md).

No predecessor code is imported. Credit remains with the cited contributors:
the rational-frame and coordinate-CNOT work, the `UT_4(F2)` tariff, and the
prior `S3` finite-algebra censuses. The representation-rank proof and its
application to this three-register endpoint are new here.

## Limits

This proves one exact minimum in an optimistic `S3` factor model. It does not
prove a general S3 triple tariff, model free address maps, price native source
generation, address hosting, restoration outside the represented registers,
or transfer a saving or lower bound to the selected rational-frame supplier.
No `kappa`, selected result, or multiplication theorem changes.

## Open next questions

For which other three-register targets in this same
`S3` alphabet does the two-dimensional representation-rank bound match the
direct transposition bill? First compute the 216 target tuples' direct word
cost and quotient-rank bound; stop if no tuple gives a new sharp floor worth
proving or auditing. This is a screening task, not authorization for another
construction round.

## Credit and disclosure

Prepared by OpenAI Codex for homelab worker 03, with substantial AI assistance
in the derivation, verifier, and packaging. No independent human or formal
proof-kernel review is claimed. Apache-2.0.

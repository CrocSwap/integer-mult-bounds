# Independent review: Boolean disjointness repair

Verdict: PASS for the stated rank theorem over F2 and its conditional
additive rank-one cost consequence. No material proof or replay error was
found. This is an independent OpenAI Codex agent review. It is not human
review or formal proof verification.

The checked package is `boolean-disjointness-repair`. `RESULT.json` gives
the SHA-256 hash of each checked file. The publication base is
`cef4b52f2a59009865bf8eabde1be3f159063703`.

## Claims checked

Let A_h be the disjointness matrix on the nonempty proper subsets of [h],
over F2, and put B_h = I + A_h. For every integer h >= 2, the proof gives

```text
rank_F2(B_h) = (2^(h+1) - 2*(-1)^h - 3)/3.
```

If B_h is a sum of ell rank-one matrices over F2, then ell is at least
this rank. Under the assumed ledger D = 2v - 3ell with v = 2^h - 2,
this gives D <= 2*(-1)^h - 1. The bound is 1 for even h and -3 for odd h.

The cost consequence requires that additive rank-one model and ledger.
The package does not prove that all physical corrections have that form.
It does not cover a product of general maps, a different source basis,
another endpoint, or a different compiler. No rational or complex-field
extension is submitted. No complete supplier or kappa improvement follows.

## Proof review

The 2-by-2 factor L = [[1,1],[1,0]] has two distinct eigenvalues omega
and omega^2 over F4. It satisfies L^3 = I. Thus its h-fold tensor power
T_h has order dividing 3 and is diagonalizable. If a_h counts its
eigenvalues equal to 1, tensoring once more gives a_(h+1) = 2^h - a_h.
The initial value a_0 = 1 gives the stated closed formula. Extension from
F2 to F4 preserves rank, since a nonzero minor remains nonzero.

The deletion of the empty and full subsets is the main step. I checked
the displayed block matrix directly. If e_0 is the empty-set column,
T_h e_0 is the all-one column and T_h^2 e_0 is the full-set column.
Hence P e_0, for P = I + T_h + T_h^2, is exactly the column supported on
the proper nonempty subsets. It is nonzero when h >= 2. Also P(I+T_h)=0.

For B_h z = 0, applying P to (I+T_h)(0,z,0) proves that z has even
parity. Since B_h is symmetric, the all-one column is in its image.
Choose B_h w = 1. Applying the same identity to (1,w,1) proves that w
has odd parity. The full kernel is then the direct sum of the embedded
kernel of B_h and the span of (1,w,1). Its nullity is one larger, so
rank(I+T_h) = rank(B_h) + 1. This proves the claimed formula.

I also checked the alternate deletion proof in `HISTORICAL-REVIEW.txt`.
The central block identity gives B_h^3 + B_h^2 + B_h = J. The vector
(I+B_h+B_h^2)e has image 1 and odd parity. These claims agree with the
first proof. The hypothesis h >= 2 is necessary for this formula: at
h = 1, B_h is empty and has rank 0, while the proposed expression is 1.

Finally, rank of a sum of ell rank-one matrices is at most ell.
Substituting the proved lower bound for ell into the assumed ledger gives
the stated deficit bound. No other implementation cost is inferred.

## Fresh checks

From the workspace root, I ran:

```sh
python3 -B work/project-final-cleanup-20261022/early-remainder-audit/packages/boolean-disjointness-repair/verify.py
python3 -B work/project-final-cleanup-20261022/reviews/boolean-repair/review_checks.py
```

The first command passed exact binary rank elimination for h=2..11 and
the separate complete kernel enumeration for h=2,3,4. It reproduced both
committed mathematical receipts. The second command passed with this output:

```text
PASS_INDEPENDENT_BOOLEAN_REPAIR_REVIEW_CHECKS
baseline=PASS pythonoptimize_1=PASS negative_controls=5 independent_set_matrices=h2..7
h1_excluded=CONFIRMED all_h_claim=WRITTEN_PROOF_ONLY no_new_kappa
```

The review script also accepts the package path as its one argument.
It constructs the matrices from sets and checks their ranks independently
for h=2..7. The two full receipt replays pass both with no optimization
environment and with `PYTHONOPTIMIZE=1`. The final wrapper uses isolated
child interpreters, so that environment cannot disable their assertions.

Five controls run on temporary copies, with `PYTHONOPTIMIZE=1` set:

- A changed proof without a new hash is rejected by the source hash check.
- A wrong rank formula, with its source hash updated, fails the rank assertion.
- A wrong full-kernel factor, with its hash updated, fails the kernel assertion.
- A wrong preimage parity, with its hash updated, fails the parity assertion.
- A changed receipt, with its hash updated, fails the fresh receipt comparison.

These controls test different failure paths. They do not prove the theorem
for arbitrary h. That claim rests on the reviewed written proof. No
selected-supplier replay, complete repository test suite, Lean check, or
physical circuit construction was run or is claimed.

## Source and attribution check

I read the PR description standard before this review. I fetched live
[PR #172](https://github.com/CrocSwap/integer-mult-bounds/pull/172) and
verified its head `427b23bc79489e7b2b7548bfd434dd9670fd5c47`. It remains
an open draft. Its
[pinned README](https://github.com/mikey1201/integer-mult-bounds/blob/427b23bc79489e7b2b7548bfd434dd9670fd5c47/research/zeta-family/README.md),
[graph source](https://github.com/mikey1201/integer-mult-bounds/blob/427b23bc79489e7b2b7548bfd434dd9670fd5c47/research/zeta-family/zeta.py),
and verifier support the disjointness endpoint and the stated ledger.
They leave the required scalar identity as an open obligation. This rank
theorem addresses the specified F2 additive repair of that obligation.

The pinned
[NOTICE](https://github.com/mikey1201/integer-mult-bounds/blob/427b23bc79489e7b2b7548bfd434dd9670fd5c47/research/zeta-family/NOTICE)
has Git blob `5d32242250b85a59268cd27a2e63cb615c4850d9`. It credits
@icekylinx for the
[PR #144](https://github.com/CrocSwap/integer-mult-bounds/pull/144)
compiler, orthogonality contract, and bookkeeping lineage, and discloses
Cline assistance for PR #172. I verified that contributor login against
PR #144. The package retains these credits without claiming that work as
new. No predecessor code is imported into the new mathematical checkers.

`PREDECESSOR-SOURCES.json` records the fetched source bytes and metadata.
Every original-workspace hash in `ORIGINS.json` matches the existing
historical file. The changed proof-reference paths and the removal of
unrelated routing discussion match the listed adaptations. The submitted
proof itself is byte-identical to its original local version.

## Overlap check and publication limits

`OVERLAP.json` records the exact search terms, source scope, base pin, and
hash of the supplied 315-PR snapshot. The matching open contribution is
PR #172 itself; it does not contain this rank theorem. The overlap check
completed for Markdown, text, and Python sources under `research/`, plus
Markdown under `docs/`. Two earlier broad searches were killed; their
partial output is not treated as a completed check. The final search uses
one worker and exits successfully.

I read the matching
[even-subset kernel proof](https://github.com/CrocSwap/integer-mult-bounds/blob/cef4b52f2a59009865bf8eabde1be3f159063703/research/even-subset-dyadic-kernels/PROOF.md)
and its README and overlap note. It constructs a different fitting kernel
on a fixed even-subset shell with complementary labels. It neither proves
this all-subset disjointness rank formula nor contradicts the stated
restriction to this endpoint. The coalescing-subset audit match concerns
finite frame edits, not this matrix. Other matches are old ledgers,
unrelated cubic scalar rank bounds, and PR-number substring matches.

This is a bounded repository and open-PR check, not a novelty claim against
all mathematical literature or a proof that every archived JSON receipt
and compressed source has been semantically reviewed.

The coordinating agent must check the final PR description, commit-pinned
links, and GitHub rendering. Those publication actions are outside this
review. Mathematical claims in the final description must retain the F2
field, additive rank-one model, assumed ledger, and absence of a kappa gain.

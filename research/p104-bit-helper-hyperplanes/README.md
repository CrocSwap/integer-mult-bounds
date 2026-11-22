# Dropping one co-endpoint helper from the 111-port BIT word

For the pinned 39,600-instruction word, set one nonzero XOR of helpers with identical start and end charts to zero. Keep every surviving native MOVE and its original normalized input field and clock. Even if every chart keeps all earlier full-field values forever, every receiving chart can XOR them for free, and all eligible MOVE deletions are made together, none of these changes has a positive raw moment gain for `3/4 ≤ t ≤ 1`. This covers every equal-endpoint helper class on this tape. It does not yield a new κ bound.

The primary result exhausts all `2^391 − 1` XORs of the rank-eight helpers, whose saving is at most `1 + 4^t` against lost credit `8^t`; this stronger comparison holds for `2/3 < t ≤ 1`. Exactly 549 choices permit two saved MOVEs; every other choice permits one. The two-MOVE rank histograms are 394 of `{1,1}`, 152 of `{1,2}`, two of `{1,4}`, and one of `{2,2}`. The other 17 helpers have rank four and form ten exact endpoint classes. All 24 nonzero XORs within those classes save at most `1 + 2^t`, against lost credit `4^t`. These are upper bounds with historical stock granted. A separate positive control implements the best rank-eight `{1,4}` example on the actual live owners and replays every normalized output, but its saving is less than its lost helper credit. [Proof and limits](PROOF.md)

## Replay

The literal binary graph is from [PR #8027 at `fb9b6a7b0d27da1cf98430893a3016bf811e2aa4`](https://github.com/CrocSwap/integer-mult-bounds/pull/8027), retained by the [physical single-band supplier #8035 at `ea776471bf8ed143a0625cf2d7532f65d15eb5f9`](https://github.com/CrocSwap/integer-mult-bounds/pull/8035). The compressed SHA-256 is `74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326`; the expanded SHA-256 is `b096d6df2a0c4688296b13ab0cfd50fec1c7dec732819c624ddd7a745a144b69`.

```sh
python3.12 -I -B verify.py
```

This standard-library replay authenticates both hashes, checks the complete 630-input normalized circuit, reconstructs the rank-eight recipient affine cosets, verifies their flag and disjointness, independently tests the 24 rank-four constraints, checks the live-owner example and its first reads, and rejects a one-byte source corruption. `VERIFY.json` registers the same replay. The chart/projector geometry and physical meaning of the literal MOVE remain those of the pinned supplier; this package independently checks the normalized combinatorics and algebra, not the supplier's full physical or numerical application.

This result differs from [#8034](https://github.com/CrocSwap/integer-mult-bounds/pull/8034): it permits exact linear cancellations and recoded receiving ADDs with multiple original paid positions deleted. It does not cover new or recoded surviving paid transfers, retiming, two or more omitted helper dimensions, other input families, arbitrary tensor correlations, or a different compiler price rule. The sample live rewrite does not fund a changed complete caller.

## Open next questions

Can changed surviving paid payloads or two omitted helper dimensions fund a complete, profitable rewrite? Begin with an explicit source schedule and verify every live owner, first read, scrub and rank-moment charge. The present screen does not decide that question.

## Attribution

Ali Romman supplied the pinned word and its physical binding. The retained [source notice](PARENT-NOTICE) credits its predecessors, and the [binding notice](BINDING-NOTICE.md) documents the later supplier. Clear1nsight prepared this scoped analysis with substantial OpenAI Codex assistance. New material is Apache-2.0; see [LICENSE](LICENSE).

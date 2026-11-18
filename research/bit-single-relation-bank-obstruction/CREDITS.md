# Sources and credit

Ali Romman prepared this result with substantial OpenAI Codex assistance in
research, implementation, verification and writing. New code and prose use
Apache-2.0. The two checker implementations have one author and are not
independent human review. No priority claim is made for helper deletion.

The exact word and caller are declared inputs from
[PR #7001](https://github.com/CrocSwap/integer-mult-bounds/pull/7001),
head `d777f3a0aa2878bea0478918923dabcf86b9878b`:
[native](https://github.com/CrocSwap/integer-mult-bounds/blob/d777f3a0aa2878bea0478918923dabcf86b9878b/research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz),
[caller](https://github.com/CrocSwap/integer-mult-bounds/blob/d777f3a0aa2878bea0478918923dabcf86b9878b/research/paired-query-only-bit/EFREE-CALLER.json.gz),
[proof](https://github.com/CrocSwap/integer-mult-bounds/blob/d777f3a0aa2878bea0478918923dabcf86b9878b/research/paired-query-only-bit/PROOF.md) and
[notice](https://github.com/CrocSwap/integer-mult-bounds/blob/d777f3a0aa2878bea0478918923dabcf86b9878b/research/paired-query-only-bit/NOTICE).
The notice credits Jerry Chen / @CubeJerry for the paired source and
QUERY-only caller lineage, DreamingOfClouds for the chain-root caller, zxv
and retained authors for the source-native export, and Ali Romman and Cinna
Davis for the root/native lineage. These notices and the license are kept
unchanged. [SOURCE-PINS.json](SOURCE-PINS.json) authenticates them.

The source admission review is
[PROOF-REVIEW.md](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/docs/research/pr-intake-evidence/pr7000-application/PROOF-REVIEW.md).
Its physical and uniform conclusions are inherited, not proved again here.

The overlap check read these related results:

- ToikY's [PR #7304](https://github.com/CrocSwap/integer-mult-bounds/pull/7304)
  excludes its fixed original-pivot productive split domain.
- Jerry Chen / CubeJerry's
  [PR #7573](https://github.com/CrocSwap/integer-mult-bounds/pull/7573) and
  [proof](https://github.com/CrocSwap/integer-mult-bounds/blob/34016136b3aadfcace5116aac0da70e7bc4637ff/research/bit-alternate-carrier-split-bound/PROOF.md)
  exclude clean alternate-carrier pairing at fixed cuts. That operator result
  does not grant a promise on a productive helper.
- [PR #1043](https://github.com/CrocSwap/integer-mult-bounds/pull/1043) deletes
  a helper on an older R439 source. The associated fixed-anchor exclusion in
  [PR #1250](https://github.com/CrocSwap/integer-mult-bounds/pull/1250) uses a
  different word and does not cover this current-source bank model.
- Ali Romman's [PR #5679](https://github.com/CrocSwap/integer-mult-bounds/pull/5679)
  and [PR #5708](https://github.com/CrocSwap/integer-mult-bounds/pull/5708)
  give helper splits and changed paths on an older G20 word.
- Ali Romman's [PR #7713](https://github.com/CrocSwap/integer-mult-bounds/pull/7713)
  supplies the related rational helper-quotient method on a P104 word.
  No P104 certificate is used as a binary proof.
- DreamingOfClouds's
  [PR #7618](https://github.com/CrocSwap/integer-mult-bounds/pull/7618)
  already treats the conservative complex BIT premise. This result does not
  duplicate that lift or change the source admission.

The new contribution is the exact single-relation receiver criterion,
complete current-word certificate in both orientations and complete signed
exclusion. The source word and caller are unchanged.

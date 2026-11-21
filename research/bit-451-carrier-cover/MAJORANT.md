# Independent fixed-word uniform bound

The exact #7863 supplier under the #8026 cover analysis has ambient A=134^451, maximum paid cutoff r=11^451, minimum retained rank k=16^451 and carrier N=2^H for H=1202400000000000. Freeze the original word, all integer replication choices, routes and scalar/physical premises. The ambient-cap compiler lemma gives L(N)=P_N/B_N ≤ N^t (1+H)^p, where t=1−0.003879928046148. The original strictification theorem allows any real p>0. The exponent is used in strong induction on the already determined selector and normalized count. [Original source and proof of fixed-word dependence](https://github.com/CrocSwap/integer-mult-bounds/blob/7c49fe32c55de02c2c873655c804b16e4c3fef0a/research/higher-moment-strictification/README.md#L186-L259) · [Ambient generalization](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/p104-shared-native-helper-splits/retained/compiler/PROOF.md#L225-L289)

Take θ̄=173/200, p=237/4, e=2969/H. Integer comparisons give r^200<k^173 and 2^27·r^200≤A^173. Let η=t·A^(t−1). Using the pinned lower enclosure for η and upper for A^(1−t), check θ̄^237<η⁴ and (A^(1−t))⁴<2^237. The first inequality also follows by substituting the certified upper A^(1−t) in t/η. Then (1+H)^237<2^(4·2969) gives L(N)<N^(t+e). For every real x≥H the derivative of log(2^(xe)/(1+x)^p) is positive because (H+1)e>2p and ln 2>1/2. No smaller carrier, cutoff, or physical word is introduced.

Use #8026's fixed q/cylinder cover with unchanged d=1/(H·2^44). Its charged bad-class multiplier bound and freshness conditions are identical. Bound the covered rate by C−e−d. From the same completed seed, seven strictly interior rational stage estimates give the final admissible ordinary service 0.00387992804367877. As in #8026 the improved rate changes only the analytical thresholds. Original dispatch, all nested bank loans and restoring operations, separate ordinary/precision/tape bills and recovery hypotheses remain those of the baseline. The frozen seven-stage physical transfer remains an assumption.

The pinned outer compiler returns at most the lesser signed/ordinary grid predecessor minus eight ticks, for tick 10^−14. Its auditor requires the tested point, exactly seven ticks above the public claim, to be strictly below the ordinary cap. The independently replayed application gives 0.00387992804359, tested at 0.00387992804366 with BIT headroom 0.00000000000001877. Even allow #8026 its native raw upper 0.003879928046155, grant zero cover loss and ignore every strict seven-stage debit. Its previous fixed uniform loss 3006/H then implies an upper bound of 0.003879928043585 on a complete claim under those outer rules. The proposed point clears this generous ceiling by 5·10^−15. This is a comparison of certified complete bounds for specified proofs. The exact physical leaf count and optimal crossing remain unknown.

The exact change over #8026 is +0.00000000000003, or (75/96998201089)% = +0.0000000007732102158388% when rounded. [Predecessor #8026](https://github.com/CrocSwap/integer-mult-bounds/pull/8026)

## Replay

From the repository root, CPython 3.12 runs the package's complete verifier:

```sh
python3.12 -I -B research/bit-451-carrier-cover/verify_majorant.py
```

The runner rebuilds the predecessor and checks the complete application. The independent component calculation can also run against the extracted, authenticated #7863 producer directory:

```sh
python3.12 -I -B research/bit-451-carrier-cover/majorant_audit.py "$producer" majorant-receipt.json
cmp research/bit-451-carrier-cover/MAJORANT.json majorant-receipt.json
```

Passing `--outer` with a fresh complete-consumer results directory also checks the installed cap, tested point, complete claim, and hashes of the application and audit against its run receipt. Both modes return the same deterministic component receipt. The checker exercises the original passing p=60 instance. Lowering p to 59 or lowering the loss numerator to 2968 makes the corresponding test fail. The predecessor p=60 fails at the proposed loss.

## Provenance

zxv established the arbitrary-positive-power argument used here in #4433, extending #4411. zxv's #4480 separately studied normalized logarithmic majorants and the paid exit law. This application uses the ambient-cap adaptation of #4433's bound, fixes every physical choice and N, and changes the two parameters of that bound to prove the lower loss. Jacob Alan Sussman's integral flow supplies the normalized paid/productive count to which the induction applies. DreamingOfClouds supplied the ambient-cap source construction, and the retained compiler proof credits its chronological product and specialization predecessors. Clear1nsight supplied the #7863 fixed binary schedule and signed rational consumer, independently reviewed in #7973. #8026 supplies the charged delayed-cover proof, seven-stage stock contract and comparator. The source proofs credit the original column, compiler and recovery contributions. OpenAI Codex materially assisted the new estimates, proofs and replay. [#4433](https://github.com/CrocSwap/integer-mult-bounds/pull/4433) · [#4480](https://github.com/CrocSwap/integer-mult-bounds/pull/4480) · [Finite precompilation](https://github.com/CrocSwap/integer-mult-bounds/blob/7c49fe32c55de02c2c873655c804b16e4c3fef0a/research/kappa-rebuild/architecture/FINITE-PRECOMPILATION.md#L137-L201) · [#7863](https://github.com/CrocSwap/integer-mult-bounds/pull/7863) · [#7973](https://github.com/CrocSwap/integer-mult-bounds/pull/7973)

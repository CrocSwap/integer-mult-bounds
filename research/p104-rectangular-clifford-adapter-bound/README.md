# A rectangular adapter bound for paid complex MOVE pairs

**NO VERIFIED GAIN.** At κ = 0.0040075385047236 the exact #7161/#7113 invoice would need 25,328 ideal rank-one pairs. A one-child rank-two replacement with bounded-norm rectangular linear adapters cannot implement the required arbitrary-input map for all widths, even with destructive scratch erasure. A separate reversible bound applies with arbitrary coefficients and bounded-support recovery. [Proof and price](PROOF.md) · [Exact receipt](ADAPTER.json)

## Reproduction

Use CPython 3.12 with assertions enabled. From a clean checkout:

```sh
python3.12 -B scripts/research_package.py --package research/p104-rectangular-clifford-adapter-bound
```

The verifier authenticates bundled sources, reconstructs the full paid invoice, and checks 512 signed chart columns and 60 Gaussian projection controls. [Source paths and hashes](INPUTS.json)

## Open next questions

Can an adapter with growing norms satisfy the same complete tape, precision and ownership budget? Begin with the two independent stage-1 and stage-2 occurrences of MOVE535. Construct a literal all-width pair with priced bank expansion below $2^C$, then charge its setup, routing, returned state and precision. The projection control in the proof instead uses expansion $2^f$.

## Credit

Clear1nsight #7161 supplied the native word. Rohan Arun #7113 supplied the signed caller and the inherited Gaussian compiler/interpreter closure. The #7165 paid-position verifier is reused. [Proof attribution](PROOF.md#attribution) and the [upstream source notice](inputs/PEER-NOTICE.txt) preserve the earlier lineage. OpenAI Codex and subagents materially assisted. New work is Apache-2.0.

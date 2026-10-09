# Completed entrance banks on PR200's bit word

This package applies PR186's completed entrance banks to the bit word of PR200 and prices the result against the v4 source-assisted complex supplier of PR194/PR202. Under the retained interfaces it certifies

$$
T(n)=O\left(n(\log n)^{1-\kappa}\right),\qquad
\kappa=\frac{6830611}{10^{10}}=0.0006830611 .
$$

That is 0.913% above PR202 (6768823/10^10) and 2.342% above PR194 (1668581/2500000000). The bit supplier still binds; the complex saving is 219037/312500000 ≈ 7.009184e-4.

| Bit supplier, per group vertex | PR200 word | With completed banks |
|---|---:|---:|
| Live physical chains | 17,114 | 17,114 |
| Persistent stock W | 20,634 | 56402/3 ≈ 18,800.67 |
| Rank mass | 1,483,712 | 1,351,712 |
| Deficit | 1,936 | 1,936 |
| Largest child | 60 | 22 |
| Coarse saving (10^-18 grid) | 677773948354561/10^18 | 683528191056257/10^18 |
| κ, PR184 assembly | 6768823/10^10 | 6826211/10^10 |
| κ, with PR185's 3-level leaf | 1693287/2500000000 | **6830611/10^10** |

## What changes

The banks remove one rank-60 exterior child for each of the 2,200 surviving rank-20 entrance gauges. They pack each entrance's rank-4 residual 18 to a width-72 bank, and each other live chain's rank-24 residual 3 to a bank. The banks are stage-private, with nine physical replicas, exactly as PR186 does on PR168's word. The round-8 supplement (BANK-SCHEDULE.md) schedules them.

PR200's word differs from PR168's in two ways that matter here. It has a new local circuit, and it deletes 34 terminal sinks. A deleted sink has no register, so it has no residual to bank: the live chains are 18,908 − 1,760 splices − 34 sinks = 17,114. Of these, 2,200 are entrances and 14,914 are completed chains.

## Run

From the repository root, with Python 3.11 or newer:

```sh
python3 -B research/pr200-entrance-banks/verify.py          # about 70 s
python3 -B research/pr200-entrance-banks/verify.py --full   # also runs PR200's verify.py first
```

The verifier works as follows:

1. It checks its pins and recomputes the git blob id of every vendored reference file.
2. It confirms that the four PR186 functions it ports are AST-identical to the upstream ones.
3. It loads PR200's literal word and reruns PR200's terminal prover: F2 and integer columns, both directions, with three mutation controls.
4. It requires the result to equal PR200's certified profile.
5. It rebuilds the bank inventory, the exact entrance charts, the projector and weighted endpoint checks, and the round-8 schedule diagnostic.
6. It prices the packed profile with PR186's paid moment and an independent base-two moment, then runs PR184's 47-constraint assembly with and without the finite leaf.
7. It rejects five mutations and compares everything with `certificate.json`.

[PROOF.md](PROOF.md) states the claim, the construction and the scope. [NOTICE](NOTICE) records provenance and assistance. `references/` holds byte-identical copies of the reused upstream files; `references/manifest.json` names their commits and blob ids.

This is a conditional finite witness, not a proof of the multiplication theorem. PR200, PR202, PR197 and PR199 have no maintainer review.

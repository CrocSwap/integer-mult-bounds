# P104 shared-chart retiming

This source-bound construction crosses two early ADD stars in the pending
[PR2662](https://github.com/CrocSwap/integer-mult-bounds/pull/2662) word by
moving **both operands** to a common earlier chart. It retains every ADD
coefficient, all 358 independent input/output fields and all dirty-helper
restoration. Four direct positive children replace four pairs of transports:

| Quantity | PR2662 | This word |
| --- | ---: | ---: |
| Positive transports | 1,942 | 1,938 |
| Total events | 5,270 | 5,266 |
| Rank mass | 3,542 | 3,542 |
| Scalar ADDs | 3,104 | 3,104 |
| Restored dirty helpers | 150 | 150 |
| Owned zero/zero-erase lifetimes | 8 | 8 |

The changes are two `H1+H1 -> H2`, one `H1+H4 -> H5` and one
`H1+H6 -> H7`. The local child sum strictly decreases for every exponent
`0<p<1`; it is unchanged at `p=1`. This is a finite same-boundary replacement,
not a complete favorable moment or an admitted physical supplier.

PR2662 fixes ADD frames in its role-local endpoint-run class. This word
jointly changes four ADD frames, so it does not contradict that scoped
optimum. N33 and N34 still pay their line-entry children after their ADDs;
their arbitrary initial dirt is retained. No new field or extra scalar
operation is introduced.

## Contract and evidence

[PROOF.md](PROOF.md) gives the local operator identity, exact source-use
intervals, positive-child construction and complete invoice. The final
physical frames and complete logical map equal the source. As in PR2586,
the other 102 forward rows retain the Gram/2 contract; this is not a fully
corrected identity core. All unchanged native edges inherit the pending
predecessor's proof and source review.

The replay checks the complete 358-by-358 rational boundary, all 150 dirty
helpers and eight exact zero erasures. Three new native recipes cover four
edge occurrences. Each has a monomial wrapper and one positive child, with
signed Pauli, exact phase and all 512 Gaussian-column checks (1,536 total).
Nine failure controls reject unilateral retiming, omitted paid compensation,
changed public output, a crossed undeclared source read and native defects.
An equivalent binary-frame basis is accepted as a positive control.

`WORD.json`, `NATIVE.json` and `RESULT.json` are retained outputs. `build.py`
regenerates the first two in a new directory. Default verification is
read-only and does not import a compiler or predecessor generator. The only
external executable input is the SHA-256/Git-blob-bound native interpreter
listed in `SOURCES.json`; the exact authenticated byte buffer is compiled,
so a stale timestamp bytecode cache is ignored. The four retained predecessor files are bound in
`PREDECESSORS.json`; historical task/catalog pins are provenance only.

From the repository root, with Python 3.12 or later:

```text
python -I -B scripts/research_package.py --package research/p104-shared-chart-retiming
python -I -O -B research/p104-shared-chart-retiming/verify.py --regenerate
python -I -O -B research/p104-shared-chart-retiming/build.py --out-dir NEW_DIRECTORY
```

The package uses only the standard library. `test_verify.py` also checks
Git-free export, deterministic regeneration, read-only replay and corrupted
source/receipt rejection. The registered runner command handles declared
external inputs explicitly.

## Revision 5 decision

The local exit values and frames are identical, so no extra consumer
compensation is needed **for this replacement**. The complete consumer's
physical scalar/address work, monomial movement, owners/windows, hosting,
idle/residual children, precision and rounded erasure remain unknown. Those
costs are not assigned zero. PR2674's different-word precision bound is not
transferred. The decision is to finish this finite interface and stop before
further dependent optimization or a family-expansion claim.

## Open next questions

Can the corrected physical-dual caller be given a complete ownership,
transport, scalar, hosting and precision invoice that includes this exact
word? A useful next step is that boundary-and-cost ledger, including remaining
identity corrections and unpriced monomial wrappers. Another child-only
search does not close it.

Credit commdata2338's PR2662 and its explicit ADD-barrier handoff, ywz65's
PR2586/2497/2551, Nick Petalas's PR2550 and the full lineage in the retained
source READMEs. Common-chart linearity and `C^-1=X*C` are standard identities.
Prepared for ywz65 with substantial OpenAI Codex assistance. Apache-2.0;
no independent human or formal-kernel review is claimed.

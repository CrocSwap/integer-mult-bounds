# A conditional increase to kappa .00302152

**TL;DR: joint changes to native warp maps and scalar-contact frames give
kappa .00302152, up by .000001355 from the public .003020165 proposal
(about .0449% more exponent saving).** This is a verified construction under
the repository's retained assumptions. It has not received maintainer or
independent human review, and the selected `.0023` record is untouched.

The key was to change the maps themselves together. Fixed-map retiming,
individual changed maps, productive query extensions and new tree controllers
did not produce the gain. The successful joint search frees 60 native maps;
34 change in the emitted construction, together with 422 scalar frame labels.
All original scalar opcodes and all 408 arbitrary productive helpers remain.

| Quantity | PR4470 / public PR4535 invoice | New construction |
| --- | ---: | ---: |
| Local rank-1 children | 2237 | 2201 |
| Local rank-2 children | 388 | 412 |
| Local rank-3 children | 494 | 506 |
| Local rank-4 children | 147 | 135 |
| Local rank-5 / rank-8 children | 36 / 8 | 36 / 8 |
| Local paid calls | 3310 | 3298 |
| Full p16 paid calls | 64620 | 64404 |
| Full p16 rank-mass surplus | 752 | 752 |
| Claimed conditional kappa | .003020165 | .00302152 |

The paid difference is `12(3 H1 - 2 H2 - H3 + H4)`. The proof establishes a
strict moment improvement for every `0<t<1`. Exact interval arithmetic places
the new raw crossing in `(.0030215551,.0030215552)`, leaving explicit room for
the finite compiler and all outer inequalities at the claimed saving.

Validation includes both retained literal interpreters on all 632 arbitrary
persistent inputs in both orientations; the 408 dirty helpers remain autonomous.
The new exact native operators, all used warp classes and every new paid
transport are checked with absolute phases. The recursive ledger checks two
rational moment engines, both paid tails, productive completion, a finite
uniform compiler and all 58 outer predicates, with mutation controls.

The solver is used only to discover the frozen word. Replay uses Python3.14
and the pre-existing NumPy, without SciPy or an environment. The optional
discovery solver was installed into an ignored local `.deps` directory; it
did not alter the global interpreter.

`PROOF.md` explains the substitution theorem and accounting. `ARITHMETIC.json`
contains exact rational margins and compiler parameters. The emitted local
word and physical certificates are in `../warp-interface-20261022/`.
`SESSION-VERIFICATION.json` binds the fresh replay and independent AI audit.
Source hashes and a final file inventory make the result reproducible.

From the repository root, replay the frozen construction without a solver:

```powershell
& 'C:\Users\caoyi\AppData\Local\Python\pythoncore-3.14-64\python.exe' -B research/kappa-interface-round2-20261022/verify_result.py
```

The seven fresh gates reconstruct the exact word from the patch, check both
native orientations and physical phases, prove the uniform moment gain,
replay retained native/BIT dependencies, rebuild the complete arithmetic and
run the separately implemented AI audit. Logs are hashed in the receipt.

The old source head is `f626db5c3a3d781d8f7695038776c621651f75e1`. The comparison
is the open [PR4535](https://github.com/CrocSwap/integer-mult-bounds/pull/4535),
head `a6d7237f697185e857090e174c23c1cb22c6563c`, and Cinna Davis's
[PR4470 supplier](https://github.com/CrocSwap/integer-mult-bounds/pull/4470).
The community-selected value remains `.0023` at this source snapshot.

Prepared with substantial OpenAI Codex assistance. Apache-2.0. Verification
here means exact executable checks plus mathematical arguments under the
existing assumptions; no complete Lean proof, human review or measured
practical speed improvement is claimed. Nothing was published externally.

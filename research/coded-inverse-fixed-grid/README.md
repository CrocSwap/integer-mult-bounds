# A finite classical inverse-code kernel

**Conditional local implementation, with no new kappa.** This package implements one signed fixed-grid invocation of the actual 112-owner inverse code `A^-1=I-MM^T/52`. It uses eight exact integer mode sums, a bitwise denominator-13 transducer and symmetric nearest rounding. PR4933 supplied the factorization, exact-real program and 56/69-over-13 bounds; this package adds the bounded implementation, sharp rounding bound, guard/width policy and paid sequential tape tariff.

This does **not** repair PR4940's physical caller. Its formal scalar `A` cannot be substituted for PR4933's actual `C_ij=A_ij K_i^-1 K_j`. The separate task02 pair audit owns that frame/chronology question. This kernel applies only after a caller establishes legal access to all 112 owners at common coordinates and accepts classical destructive owned writes. A physical `C^-1` call additionally pays its actual `K_i` wrappers and movement.

The grid is `2^-P`. The finite program returns an owner vector within `2*2^-P` component error of exact `A^-1 x`. This bound is attained: at `x=26e_0` its owner-0 result is 22, while the exact result is 24. At `x=-26e_0` the corresponding results are -22 and -24. Choosing `P=p+g` gives at most `2^(1-g)` units on a target grid `2^-p`; output retains the guard bits.

The first fixture is `x=4e_0`: four mode numerators equal 4, so `/52` needs the non-dyadic value `1/13`. The implemented owner-0 result is 4 versus exact `48/13`. It is an approximate finite invocation, never an exact-real division oracle.

The rounded map is **noninjective**: `recode(M[:,0])=recode(0)=0`. Owned scratch is explicitly overwritten with zero, with every bit write and scan paid; this is not reversible uncomputation. A caller requiring reversible return cannot use this kernel under the stated contract. No round-trip through a rounded forward code or paid Gaussian child is asserted.

For integer input magnitudes at most H, let `W=bit_length(56H+2)+1`. On a fixed 122-tape classical machine, N scalar components per owner cost at most `N(2898W+5922)+18W+100` transitions. Space is `112[N(W+1)+1]` owner cells, `9(W+1)` owned scratch cells and `W+1` readonly bound cells, plus fixed framing. The invoice includes all 896N signed ADDs, 8N odd-division calls, 112N numerical validations, `136N+9` full-word zero-writing scans, component advancement and final head rewind. The eight mode words and one division buffer are reused. The 408 native helper tapes are absent and untouched. See [PROOF.md](PROOF.md) for the literal sweep schedule, source ABI and uniform argument.

## Evidence and reproduction

`TASK.json` and `FIRST-FIXTURE.json` were written before computation. `SOURCES.json` pins canonical base `f259dabc7d70e0db8d6d36bfda888f008bbfecc1`, priority 7 and the exact live source bytes. The PR4933 lineage is head `d969c458c24278e0fd37e5b4c0ff8a53a496b430`; all needed files are present in the base, so replay does not depend on an unpublished Git object. Selected result provenance remains the conditional `0.00302015` record and is not changed.

```sh
python3.12 -B research/coded-inverse-fixed-grid/verify.py
python3.12 -O -B research/coded-inverse-fixed-grid/verify.py
python3.12 scripts/research_package.py --package research/coded-inverse-fixed-grid
```

The standard-library replay authenticates seven source inputs; checks all 12,544 matrix entries and 64 mode Gram entries; exhausts 3,328 signed division cases covering every `/13` remainder and low-two-bit class; compares 12 owner fixtures to an independent `Fraction` matrix oracle; checks seven guard precisions and the noninjective collision; rejects five real-kernel semantic mutants and five malformed/aliased inputs. `RESULT.json` records the deterministic receipt. All correctness checks use explicit exceptions and remain active under `-O`. A finite replay corroborates the written scoped theorem; it is not a formal-kernel proof or full multiplication theorem.

No local production build, Lean build, historical controller replay or full reserve calculation is needed or claimed. The classical ABI is source-bound to the pinned PR4630 `MACHINE-INTERFACE.md` and `TM-TO-WORD-RAM.md`; their store/arbitrary-symbol-write semantics allow the paid destructive cleanup used here. The tape tariff is a constructive sweep proof, not a fresh Lean-checked or emitted RAM program. Logarithmic word-width admission still needs the caller's polynomial numerical/address bounds.

## Open next questions

1. Can an actual physical caller present the common-coordinate 112-owner inputs and legal chronological output access? First use task02's exact frame-pair finding; the `C != A` substitution gap remains outside this arithmetic package.
2. Does a complete caller fund this precision, storage, tape movement and repeated local rounding, and does it accept classical destructive owned return? Substitute this tariff into one explicit caller/error ledger. No global reserve, reversible cleanup or new frontier follows from this local result.

Structured questions, first steps and blockers are retained in `TASK.json`. The source claim is [Discussion #4930 comment 19139521](https://github.com/CrocSwap/integer-mult-bounds/discussions/4930#discussioncomment-19139521).

## Credit

PR4940 by Cayden/Seth Burkart supplies the inverse-coded controller question. Dillon's PR4933 supplies the physical recoding, exact mode factorization, prefix bounds and predecessor cleanup bill. Dugongue/mdumitrean's PR4929 supplies the coded producer and stable code. PR4630 by Dugongue supplies the actual classical machine/compiler interface and retains its Problem 1.8 authors. Cinna Davis, Cao Yifan/intqwq, zxv, Jacob Alan Sussman and the retained native, precision, ownership, Clifford and tape lineage keep their predecessor credit and source notices. This package changes none of their frozen sources. New implementation, scoped proof and checks are by JoyboyBrian with substantial OpenAI Codex assistance, Apache-2.0. No independent human or formal-kernel acceptance is asserted.

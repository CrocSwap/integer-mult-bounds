# R420 compensation through a reversible target basis

**Finite bit-circuit improvement; no new kappa.** Eumemic's
[PR543](https://github.com/CrocSwap/integer-mult-bounds/pull/543) R420 word
implements its frame-zero dirty-helper compensation with 19,922 binary XORs.
This package implements exactly the same F2 boundary map with **12,043 XORs**,
including both target-basis changes. The complete native word falls from
**26,916 to 19,037 XORs**, a saving of 7,879 (29.27%). It uses the same helpers,
copies, frame paths and recursive children.

The tradeoff is a larger cancellation-free prefix bound. A budget-constrained
search keeps the nine-stage prefix within its existing **192-bit charge**;
the complete invoice still fits its existing **512-bit coefficient charge**.
Fresh native, nine-stage, physical hosting and exact assembly checks pass.
This is a circuit-count result, not a measured multiplication speedup.

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. The selected construction at
that base is #626 with #543, at conditional
`kappa = 51110230636731/31250000000000000 = 0.001635527380375392`.
Its actual [assembly](../community-k492-audit/pr626/replay/ASSEMBLY.json)
is complex-bound. The selected files and all predecessor inputs are untouched.

The final overlap refresh found concurrent **PR686/PR694**, which also factor
this compensation but change and restore helper rows. This contribution uses
the **target side**, permits successive noncommuting row operations, enforces
the complete nine-stage prefix budget during nomination, and includes a fresh
hosted invoice/assembly replay. The comparison and credit are explicit below.

## Reproduce

From the repository root, Python 3.11+ and its standard library suffice for
the finite construction, native labels/frames, both complete column walks,
local invoice and 13 negative controls:

```sh
python3 -I -B research/r420-target-compensation/verify.py
```

Expected final line:

```text
PASS_R420_TARGET_COMPENSATION D=19922->12043 total=26916->19037 columns=660 rank_mass=5112 nine_bits=192 controls=13
```

The command verifies the frozen recipe without trusting or rerunning the search.
It makes no output files by default. `--output build/NEW-DIRECTORY` also saves
the reconstructed word and report; existing directories are refused. Word
identity is canonical decompressed JSON, not a regenerated gzip-container hash.

For a fresh complete hosted replay, use a C++17 compiler with Boost headers and
install `requirements.txt` into a virtual environment. Then run:

```sh
python3 -I -B research/r420-target-compensation/replay_hosted.py
```

Expected final status:

```text
PASS_R420_TARGET_COMPENSATION_HOSTED local_adds=19037 hosted_events=6334560 prefix_charge=192 coefficient_charge=512 kappa=unchanged
```

It creates a unique directory under `build/`, records the exact subprocess
commands and logs, and uses the frozen original hosting selection. It needs
SymPy, but no NumPy, SciPy, optimization solver or network. Compilation and
replay are sequential. `--cxx` selects the compiler and `--output` selects a
fresh output directory. The checked environment was Linux, Python 3.12.3,
SymPy 1.14.0, mpmath 1.3.0 and GCC 13.3.0. Assertions must remain enabled.

## The boundary identity and its interface

Write `s` for the 420 arbitrary helper inputs and `y` for the 120 arbitrary
target inputs. The original D is `y <- y + K s`, for a fixed binary
120-by-420 matrix K. Its rows are recovered directly from the pinned word.
All participating rows start and finish D at frame zero.

The 205 pairs in [candidate.json](candidate.json) denote elementary
transvections `y[a] ^= y[b]`, using zero-based target indices. Let E be their
product in execution order, and put `R = E K` over F2. Execute:

1. The 205 transvections, giving `E y`.
2. The 11,633 helper additions specified by the nonzero entries of R.
3. The same 205 transvections in reverse order.

Each transvection is its own inverse over F2. The output is therefore
`E^-1 (E y + R s) = y + K s`. Sources and helpers are never written. This
argument applies to arbitrary incoming target values, including dirty targets;
it requires no initially zero workspace and introduces no workspace row.

The new transcript does **not** satisfy PR543's syntactic H2, which requires
every D gate to read only helpers. Its old direct-summation computation of
`K_equals_D` also does not apply. The verifier records both old predicates as
false, retains every other H1–H5/U/J/U-inverse check, and separately verifies
the exact D boundary `(x,y,s) -> (x,y+K s,s)` on all 660 symbolic columns.

This is a sufficient replacement for H2: the unchanged raw word has
`(z,y) -> (U z, y + J x + K s)`, with `J = I`, and the unchanged C restores
`z = (x,s)`. Substituting any legal frame-zero transcript with the stated D
boundary gives the same composite map as the original D. Every new ADD is
between rows already at frame zero, and D leaves their frames there; the
unchanged remainder consequently sees identical values and frames. The
inherited common-label realization treats these frame-zero XORs in the same
way as other common-frame additions. Its all-size realization remains an
inherited assumption.

The equality asserted here is over F2. This is not equality of the positive
integer transfer matrices: those matrices grow, as the next section records.
The signed inverse in the inherited lifted program reverses the literal
instructions and negates ADD coefficients. Both orientations' absolute-value
prefix bills are recomputed from those actual instructions.

## Complete cost and prefix accounting

| Quantity | Original | New |
|---|---:|---:|
| D helper-read XORs | 19,922 | 11,633 |
| D entrance / exit target-basis XORs | 0 / 0 | 205 / 205 |
| Total D XORs | 19,922 | 12,043 |
| Other native XORs, including scatter and cleanup | 6,994 | 6,994 |
| Complete native XORs | 26,916 | 19,037 |
| Native record count | 29,874 | 21,995 |
| Native MOVE records | 2,940 | 2,940 |
| Helpers / retained COPY–ERASE pairs | 420 / 9 | 420 / 9 |
| Native paid rank mass | 5,112 | 5,112 |
| Native forward bound F | 144,651 | 144,651 |
| Native reverse bound B | 2,270,064 | 4,409,580 |
| Five-stage bound `64 F^3 B^2`, bits | 100 | 102 |
| Nine-stage bound `2^18 F^5 B^4`, bits | 189 | 192 |
| Charged nine-stage prefix bits | 192 | 192 |
| Two-level coefficient bits | 416 | 424 |
| Charged two-level coefficient bits | 512 | 512 |
| Emitted hosted instructions | 8,603,712 | 6,334,560 |

Every register has the same ordered frame path. Including the nine rank-8
COPY charges, the local profile remains
`{1:1320, 2:1440, 4:60, 5:120, 8:9}`. Its moment for every `0 < p < 1` is
`1320 + 1440*2^p + 60*4^p + 120*5^p + 9*8^p`.

In units of inherited frame-zero ADD work, the changed local cost is
`C_fixed + (205 + 11633 + 205) * C_ADD0` in place of
`C_fixed + 19922 * C_ADD0`. Here `C_fixed` includes the unchanged A/scatter/B/C,
all frame transitions, all source access outside D, retained copies, clears
and recursive children. D's helper accesses and both basis changes are fully
included; there is no deferred basis restoration.

The complete nine-stage construction makes 288 local calls. Its local-ADD
invoice term falls by `288 * 7879 = 2,269,152`. The 69,120 bridge additions,
2,592 COPY–ERASE episodes, 120,960 hosted residuals, 30,720 live / 30,729
physical rows, all route selectors, and the hosted recursive profile remain.
Maximum child rank is 42 and halving depth is two. The inherited emitter,
parent audit and hosting audit rebuild and check these quantities.

[HOSTED-CERTIFICATE.json](HOSTED-CERTIFICATE.json) expands every finite-invoice
term: local/bridge additions, high-level and physical-row routing, paid calls
and compiler work, fixed setup, copies/clears, selectors and the prefix. The
**unrounded coefficient increases** because the prefix grows; the existing
192/512-bit allowances still suffice. This package claims neither entrywise
positive domination nor a reduced unrounded coefficient. Both exact moment
engines reproduce the bit lower bound
`413456747036699736067/250000000000000000000000`. All 47 assembly inequalities
reproduce the selected kappa using the pinned #626 complex lower bound. The
complex supplier is cited, not rebuilt by this bit-only replay.

## Bounded experiment and evidence

Assignment seed **18** was drawn from OS randomness. It chooses the first of
three candidates by `18 mod 3`: factor D; resynthesize the nine retained totals;
or resynthesize phase-B block 8. The D object was chosen before experimentation
and recorded in the local sprint claims. [RESEARCH.json](RESEARCH.json) records
the overlap scan and exact pending-PR heads.

The nomination greedily replaces row `R[a]` by `R[a] XOR R[b]`, charging two
extra basis gates. It examines every ordered distinct pair at each step and
uses a seeded tie break among maximum positive savings. To respect the prefix
bill, it admits only steps that keep F at most 144,651 and B at most **4,409,638**,
the exact integer fourth-root cutoff for `2^18 F^5 B^4 < 2^192`.

The fast admission calculation is exact. If A is the positive forward basis
matrix and B0 the positive reversed-basis matrix, a new row step `(a,b)` raises
the output-bound vector by
`2 * B0[:,a] * ((A y)[b] + sum(h[j] for j in R[b] minus R[a]))`.
This follows by expanding the new endpoint
`B0 T (T A y + R' h)`: `T^2 = I + 2 e_ab`, and the changed helper row differs
by twice the entries in `R[b] minus R[a]`. Admission is applied to the actual
forward and reverse entry bounds. Fresh literal execution checks the resulting
bound independently of this incremental calculation.

The guarded trial accepted 205 steps and examined **2,941,680 ordered pairs**,
including the final pass with no admissible positive-gain pair. An unrestricted
control with the same seed accepted 328 steps, examined **4,698,120 pairs** and
reached 10,384 D XORs, but needed 201 nine-stage bits (charged 256) and exceeded
the five-stage 104-bit allowance. It was rejected. Both trials had a cap of
1,000 accepted steps and stopped before it. No zero-gain detours, column
operations or other target bases were exhaustively searched; 12,043 is not
claimed optimal.

The exact nomination, counts and trace hashes reproduce with:

```sh
python3 -I -B research/r420-target-compensation/search.py
```

`verify.py` uses the predecessor's exact lattice/frame/symbolic-row engine and
a separate Boolean-column walk of all 660 columns in both orientations. The
full replay freshly compiles the predecessor C++ engines: 900 five-stage and
1,380 nine-stage formal columns, six and eighteen omitted-bridge controls,
and exact record geometry/copy accounting. The global template checks 4,740
unbanked columns and eighteen omitted bridges; the parent and hosted audits
reject seventeen and sixteen mutations. Four new record controls omit a basis
ADD, helper ADD or COPY, or understate a MOVE rank. Four assembly controls also
remain active. The finite results do not constitute a formal proof of the
complete multiplication theorem.

The 13 native controls cover missing entrance/exit gates, wrong inverse order,
untransformed helper injection, helper omission, illegal frames/operands,
extra registers, an incorrect source pin, and a cancelling gate pair that
preserves F2 semantics while exceeding the prefix allowance. A specific
control omits the entire entrance basis: it still passes when targets start
at zero, but fails the required arbitrary-target boundary. This demonstrates
why clean-target tests would be insufficient.

## Scope and attribution

PR543's word, compensation matrix, interleaved interface and checker are
**eumemic's**, at reviewed head `2065fe4f72a914d907f1046603f5a36f17018535`,
building on #493. Credit also remains with **Dylan Crow** for the E8 word and
record/checker lineage; **DreamingOfClouds** for #503/#510 and generalized
nine-stage accounting; **DaysSky** for bridged columns and whole-call hosting;
**Zhihao Chen** for the mutable-source/common-label and compressed geometry
lineage; and **Chafik Boukhalfa** for physical routes, templates and audits.
See the original [R420 README](../e8-bit-r420/README.md) and the selected
[maintainer review](../../docs/research/community-k492-review.md) for cumulative
credit. All consumed predecessor source files are pinned in
[SOURCES.json](SOURCES.json) and remain unchanged.

PR670 and PR674 reduce phase-B blocks 3 and 5, and PR790 (seed 19)
resynthesizes block 9. This result changes only D and uses a
reversible target-basis factorization under a prefix budget. No composition
with those pending block changes is certified here. PR661's fixed-order
phase-B frame bound is not reopened. PR677 completes a native
ADDRESS-query restored DATA shear; it is a different interface and algebra.
None is an execution dependency. PR249/309's compensation transport concerns
later frames; this construction keeps compensation at frame zero.

The final anonymous refresh, at **2026-10-13 04:25:33 UTC**, inspected the 100
most recently updated open PRs in addition to the initial 497-PR snapshot.
It found directly related work published during this experiment:

- **Mikhail R. Gadelha's [PR686](https://github.com/CrocSwap/integer-mult-bounds/pull/686)**,
  head `23dcb610c2b156b76b9d599ea296c3cbde224b2d`, restores a single helper pair
  and saves 108 ADDs. Its written semantic D-boundary substitution is credited.
- **Greer Guthrie's [PR694](https://github.com/CrocSwap/integer-mult-bounds/pull/694)**,
  head `9732ac127dd4bef98a846aaa904c20b5a84e72c1`, reports 201 disjoint helper
  pairs and 6,934 saved ADDs. It factors on the right, `K' = K P^-1`, and
  restores the helper basis. The present factorization is on the left,
  `R = E K`, and restores arbitrary incoming target values without writing
  helpers. Its 205 successive target operations are not restricted to a
  disjoint matching. The result uses **945 fewer native ADDs** than PR694's
  reported construction; its forward/reverse norm tradeoff is different,
  so this is not an entrywise domination claim. PR694 explicitly leaves the
  hosted-parent invoice open at that head; this package supplies a full
  nine-stage hosted replay for its own target-basis word.

The frame-zero substitution principle and elementary basis-change identity
are not claimed as new priority over those contributions. No PR686/694 code,
pair matching or recipe was imported: the target circuit and initial complete
hosted replay were already frozen before this refresh. The package was renamed
to `r420-target-compensation` to avoid PR694's directory name. This is a
meaningfully different implementation of the same D boundary with additional
budget and integration evidence; no composition with either helper circuit is
claimed. The same refresh found **Ali Romman's PR688** hosting the PR670/674
block composition, and **mtpsl's PR691** changing phase-A quad 13. Those change
different scalar subwords and are also credited as concurrent work.

All-size compilation, common-label/mutable-basis realization, pooled hosting,
normalized residuals, precision/tape recovery and analytic transfer remain
inherited assumptions. There is no circuit optimality theorem, new kappa,
eleven-stage physical replay or complete Lean multiplication proof. Adopting
the replacement into a selected supplier would require a maintainer to accept
the D-boundary lemma and update the relevant source bindings; this standalone
package makes no such selection change.

Submitted by **@commdata2338** with substantial AI assistance: **OpenAI Codex**
(GPT-6-Astra) did the research, code, proof text and verification, and Claude
Code packaged the submission. Computational cross-checks do not claim
independent human review.
New files are under the repository's **Apache-2.0** license.

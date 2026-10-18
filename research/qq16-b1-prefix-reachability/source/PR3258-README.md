# The rounded QQ16 child return loses dirty-input information

The unchanged finite implementation in [PR3250][prior] admits 3^256
distinct legal local inputs with one identical returned source/destination.
An exact inversion procedure using only that return needs at least 406
additional retained bits. A 2^256-input subfamily also has the same complete
operation-count dictionary, so exposing those counts still requires at
least 256 retained bits. The [uniform proof](PROOF.md) holds for every
integer precision 2<=p<=2046 and any positive dyadic scale q.

The literal pair is B1_2 event11795, L470 frame0-to5 rank1, followed by
event11796, `L524 -= L470/2`. In the right monomial's coordinates, put
`(q*2^(p+1), q*c_j)` on each complex pair, with independently chosen
`c_j` in `{-1,0,1}`. Nearest-even rounding erases c_j before the second
mixing layer. The half-ADD is exact on these witnesses and preserves the
collision. Every entry satisfies PR3250's dyadic, range and p-bit
significand requirements; its signed width p+8 and zero-scratch return
remain valid. This is an information bound at that interface, not a defect
in PR3250's stated accuracy theorem.

The proof does not establish that the full B1 prefix reaches all these
entries with other fields fixed. A caller may retain an input copy,
correlated outside fields or a rounding transcript. A finer exact grid
also separates the witnesses. No whole-producer restoration failure,
universal reversible-implementation barrier, physical tariff, supplier,
selected-frontier change or new kappa is claimed.

## Reproduction and evidence

The scientific/submission base is canonical main
`463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
[SOURCES.json](SOURCES.json) binds the live joint-query certificate and
selected recipe archive by Git blob and SHA256. It pins PR3250's proof and
executable at `02ff0bb88a2e808bb07c75722f3595861ce2b20d` through
retained-source head/blob/SHA receipts. The old proof is retained under
`vendor/pr3250/PROOF.md`; fresh CI needs no pending fork Git objects.
`reference.py` is a byte-identical copy of that executable; the checker
authenticates both retained files before the static local import. It is retained to execute
the actual claimed program, not presented as a new independent kernel.

```sh
python3.12 -Werror -B scripts/research_package.py --package research/qq16-rounded-child-inversion
python3.14 -Werror -O -B research/qq16-rounded-child-inversion/verify.py
python3.14 -Werror -O -B research/qq16-rounded-child-inversion/test_verify.py
```

Expected marker: `PASS_QQ16_ROUNDED_CHILD_INVERSION` followed by
`PASS_REGISTERED_RESEARCH_PACKAGE` for the registered command.
[RESULT.json](RESULT.json) records eight precisions, including 53, 104 and 2046,
five full 512-coordinate witnesses at each precision, exact output
digests, fixed-summary counts and all 81 four-pair ternary inputs.
The proof supplies the exponential-family uniformity; those families
were not exhaustively materialized.

Seven behavioral groups check exact midpoint positions, separately written
actual binary64 arithmetic on every returned component, the two-extra-bit
exact escape, perturbations beyond the collision radius, signed monomial
pullback and ideal-map separation, all 16 four-sign products with fixed
summary, invalid domains and executable-source corruption. The binary64
engine shares the source-bound monomial tables, not rounded arithmetic.
Native unitary semantics and PR3250's range/error theorem are inherited.
No full historical suite, selected cold replay, arbitrary-depth execution,
human review or formal proof-kernel check is claimed.

## Open next questions

The family decision is narrow and stop. This closes a specific missing
implication: completed local relative accuracy plus cleared owned buffers
does not supply exact inversion from this return interface. PR3250's
direct arithmetic/storage upper bounds remain unchanged. Input acquisition,
retention lifetime, global helper restoration, owner placement/routing,
physical movement, recursive tariffs and F17 consumption remain unknown.

The next useful question is which actual whole-producer caller retains the
entry or rounding information. Pin one full caller cut and identify every
input-correlated field or transcript available to its restoration step.
Whole-prefix reachability and a complete paid consumer block any stronger
conclusion. [TASK.json](TASK.json) gives the structured next question.
No further construction round is assigned here.

Initial overlap covered all 301 open PRs at 19:29:43Z and 2082 Discussion
records at 19:30:11Z on 2026-10-17, with complete pagination, plus task and
collision searches and live #2727. Titles, bodies and local notes exclude
arbitrary diffs and unpublished work. This is no novelty certificate.
The [canonical investigation][discussion] records the scoped claim.

## Credit and reference limits

Ross Richardson's [PR2999][p104], pinned at
`ac6025235b6f1233291000d35a067198628569e9`, already establishes the
analogous information-loss principle for an adaptive P104 collector and
diagnostic totals. This contribution binds the different literal QQ16
child/half-ADD program and its two return interfaces. Credit Nick Petalas
for PR3250/2965, commdata2338 for PR3235/3226, Sricharan Vagvala for
the pair-first native rounding reference, Tekalign for the native vector
conventions, Ali Romman for the joint-query construction, and the retained
QQ16/native source lineage. New work is Apache-2.0; predecessor bytes
and notices are preserved.

Power-of-ten rule3 has a managed-runtime deviation in this bounded Python
reference. Integer, Fraction and list objects allocate dynamically.
Eight fixed precisions capped at 2046, fixed 512-coordinate payloads,
bounded source readers and at most 81 product fixtures bound live work;
there is no recursive or background execution. The reference permits wider
inputs, but this checker invokes only those fixed capacities. The new
proof does not turn Python allocation into a physical-memory invoice.
Rule9's reference-module dispatch has one authenticated static target;
the module and its called paths are visible in this package. A physical
restoration implementation must separately allocate and pay for its
retained information before treating these bounds as a machine bill.

[prior]: https://github.com/CrocSwap/integer-mult-bounds/pull/3250
[p104]: https://github.com/CrocSwap/integer-mult-bounds/pull/2999
[discussion]: https://github.com/CrocSwap/integer-mult-bounds/discussions/2727#discussioncomment-19003329

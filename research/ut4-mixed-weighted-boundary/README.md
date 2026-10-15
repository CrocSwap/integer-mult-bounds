# A sharp weighted region for the mixed UT4 z/uz target

Every fourteen-call word for `diag([z],[uz],I_rest)` has exactly **four a,
six b and four c calls**, for every finite number of arbitrary restored dirty
registers in the formal UT4 model below. The two five-b alternatives explicitly
left open by Nick Petalas's [PR2175](https://github.com/CrocSwap/integer-mult-bounds/pull/2175)
are excluded. Its unit minimum fourteen and direct upper word are credited
predecessor results.

Consequently, for nonnegative per-letter prices `(alpha,beta,gamma)`, the direct
word is optimal throughout **`beta <= 2 min(alpha,gamma)`**, with exact price
`4 alpha + 6 beta + 4 gamma`. At prices `(1,2,1)`, the minimum is twenty;
neither proposed nineteen-cost word exists, even with extra dirty workspace.
This is a formal-model theorem and does not provide a native bit supplier or
improve κ.

## Model and evidence

Work in the full group algebra `F2[UT4(F2)]`, with adjacent letters
`a=I+E12`, `b=I+E23`, `c=I+E34`, and targets `u=I+E13`, `z=I+E14`.
A paid factor is `I+([g]+1)xy^T` for `g in {a,b,c}` and any nonzero binary
rank-one coupling, including nilpotents. Every restoration call is charged.
Scalar GL mixing is optimistically free and normalized into these couplings.
All extra registers start arbitrary dirty and must be restored without
contaminating the outputs. There are no clean roles, free address maps,
COPY/ERASE, higher-rank unit factors or uncharged undo.

[PROOF.md](PROOF.md) supplies the uniform workspace implication. The six scalar
column/row spans contain the active plane. PR2175's mixed middle bound leaves
at most one excess span dimension at fourteen calls. Thus every factor shares
one block-triangular orientation. Active-corner projection preserves the full
noncommutative product; zero projected factors can be deleted. The retained
thirteen-call exclusion prevents such deletion at fourteen calls. This reduces
both new domains to two roles with their exact label counts.

The finite checker retains all nine rank-one couplings on two roles and all
3,600 zero-sum ordered five-b sequences. The five-call outer catalogue has
47,521 profiles and 907,200 concrete realizations. Every surviving profile pair
is expanded through all concrete gap placements and A/C interleavings, then
tested against all seventeen coefficients of the necessary degree-three quotient.

| Split (a,b,c) | Profile pairs | Fully expanded words | Quotient survivors |
| --- | ---: | ---: | ---: |
| (4,5,4), predecessor control | 152 | 5,536 | 0 |
| (5,5,4), new | 944 | 211,968 | 0 |
| (4,5,5), new | 912 | 209,920 | 0 |

The predecessor control reproduces its exact transcript digest. The new total
is **421,888 expanded words**. No symmetry, numerical threshold, digest-only
equality or sampled-address acceptance is used. A formal identity is excluded
by failure in the quotient; a construction is never accepted from that image.

The separate controls check:

- all 907,200 five-call gap realizations for validity, uniqueness and coverage;
- a separately constructed quotient on all 20,440 words through length three,
  plus planted long-word reconstruction for all three census domains;
- all 4,096 literal group products, 882 common-orientation pairs, all seven
  one-excess span profiles, and rejection of an opposite-orientation feedback pair;
- all 192 faithful regular columns of the credited direct word, including a
  dirty spectator; the primary replay also rejects fourteen omitted calls and
  a wrong letter;
- 125 price grids and an outside-region control that prevents false sharpness.

Finite role checks support the algebra; the arbitrary-workspace and arbitrary-
word-length quantifiers come from the written proof. No proof-assistant or
independent human review is claimed.

## Scope of the price result

For all nonnegative letter prices, every word has the necessary lower bound

```
min(4 alpha + 6 beta + 4 gamma,
    4 alpha + 5 beta + 4 gamma + 2 min(alpha,gamma)).
```

The first branch is attained by the predecessor direct word. The second is
only a relaxed count bound: five b calls require at least ten outer calls,
but no word attaining that branch is provided. For example `(1,3,1)` leaves
price between twenty-five and twenty-six. General weighted optimality and
compression beyond fourteen calls remain open. Physical address realization,
rational frames, native/compiler conversion, common labels, hosting, recursive
precision/reserves and analytic transfer are separate obligations. The selected
complex-binding frontier is unchanged.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 scripts/research_package.py --package research/ut4-mixed-weighted-boundary
# Direct commands also work in a source export without Git:
python3.12 -I -O -B research/ut4-mixed-weighted-boundary/verify.py
python3.12 -I -O -B research/ut4-mixed-weighted-boundary/controls.py
```

Both registered commands run in full; no C++ build, optimizer or network is
needed. Normal replay writes nothing. `verify.py --write-result` explicitly
regenerates [RESULT.json](RESULT.json). The census was about fifty seconds in
the author environment. [TASK.json](TASK.json) records actual validation,
the original one-draw assignment, overlap and remaining questions.

The full registered replay passed on CPython 3.12.3 with assertions disabled.
Both commands also passed on CPython 3.14.4 in a Git-free, read-only export of
ten package files and two declared inputs. A write probe was rejected and
all twelve exported file hashes remained unchanged.

[SOURCES.json](SOURCES.json) pins canonical main
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, two live predecessor proof inputs,
and the exact PR2175 head `1d943bc9e0718c8a2f15e1d0a22b73ad528ef0ca`.
Only its actually used verifier library is retained byte for byte in `vendor/`;
its CLI is not invoked. The old receipt is retained as source-bound control
data. The new census extends its profile/gap method and does not claim an
independent exhaustive implementation. The separate control oracles are new.

## Open next questions

Can five b calls attain a complete word with at least ten outer calls, and
can extra dirty workspace help beyond fourteen calls? This matters outside
the proved price cone. A first step is the `(6,5,4)`, `(5,5,5)` and `(4,5,6)`
two-role domains, with complete formal acceptance of any quotient survivor.
At fifteen calls the common-orientation proof no longer follows from the
same rank slack, so a two-role exclusion alone would leave the workspace
question open. These larger domains are not searched here.

## Credit

Gareth Davidson / @bitplane, with substantial OpenAI Codex assistance in proof,
implementation, checking and writing. No subagents were used. Apache-2.0.

Credit Nick Petalas / @petalas, PR2175, for the mixed middle bound, thirteen-call
census, explicit weighted handoff and retained checker. Credit Gareth Davidson's
PR2027 for mixed-root span unions, ToikY's PR1662/1680 for the quotient and
common-orientation compression, Aaron Wang / @navinor's PR1690 for profile
screening, and Josie Elliston's PR1816 for the distinct two-central-target case.
Retain the steph4n-gh/PR1573, Arham Tahir/PR1589, Hanson Sun/PR1607,
eumemic/PR288, Ali Romman/PR468 and preceding register-model lineage. The old
direct words, quotient methods and unit optimum are not new contributions here.

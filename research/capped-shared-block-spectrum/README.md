# Sharp capped spectra: every cap at corank one, every rank at cap two

**Scoped mathematical proof with exact finite corroboration; no new kappa.**
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.

For every characteristic-two field, idempotent D of rank r-1 in dimension r,
and common zero-primary Jordan-chain cap 1 <= m <= r, the exact maximum is

    A+B=D,  nu_0(A),nu_0(B)<=m
    max [z(A)+z(B)] = r + (largest odd integer <= m).

Here z(X)=dim ker(X^r), and nu_0(X) is the nilpotency index of X restricted
to its zero-primary space, with nu_0(X)=0 for invertible X. Nonzero-primary
parts are allowed. Explicit binary matrices attain the maximum.

There is also an exact complementary law for **every idempotent rank k**:
when both zero-primary caps are at most two, the maximum is **2r-k**.
The short proof uses `D(A^2+B^2)D=D`, hence
`k <= rank(A^2)+rank(B^2) = 2r-z(A)-z(B)`. The pair `(A,B)=(0,D)`
attains it. A cap-three example in dimension three violates this bound,
so the restriction cannot simply be dropped or raised to three.

This answers the corank-one part of Open next question 2 in Nick Petalas's
[#5928](https://github.com/CrocSwap/integer-mult-bounds/pull/5928), including
its proposed first case r=5,k=4,m=4: the sharp answer is **eight**. At r=5:

| Cap m | 1 | 2 | 3 | 4 | 5 |
| --- | --- | --- | --- | --- | --- |
| Sharp z(A)+z(B) | 6 | 6 | 8 | 8 | 10 |

The cap must be specified precisely. If one instead requires A^m=B^m=0 on
the entire space, the r=5,m=4 admissible set is empty by #5928's rigidity.
More generally, for corank one and 1<=m<=r, globally nilpotent pairs exist
exactly when r is odd and m=r. The value eight uses the zero-primary cap.

The [proof](PROOF.md) constructs a surviving primary subspace under the
rank-one perturbation E=I+D to obtain z(A)+z(B)<=r+m. At equality both
operators have only zero and one primary parts; trace parity rules equality
out for even m. The odd-block construction from #5928 plus scalar identity
coordinates attains the resulting bound. No finite search substitutes for
the universal argument.

## Exact evidence and reproduction

Use CPython 3.12 with its standard library, from the repository root:

```sh
python3 -I -W error -B research/capped-shared-block-spectrum/verify.py
python3 -I -O -W error -B research/capped-shared-block-spectrum/verify.py
python3 -I -W error -B research/capped-shared-block-spectrum/independent_oracle.py
python3 -I -O -W error -B research/capped-shared-block-spectrum/independent_oracle.py
python3 -B scripts/research_package.py --package research/capped-shared-block-spectrum
python3 -B scripts/check_research_commit.py --package research/capped-shared-block-spectrum --check-source-history
```

The author engine reports `PASS_CAPPED_SHARED_BLOCK_SPECTRUM`. It checks
all 66,066 binary matrices A through dimension four, with B=A+diag(I_(r-1),0),
and all 263,714 corank-one pair/cap combinations. It additionally covers all
329,780 binary ordered pairs with every coordinate endpoint rank under cap
two. Each zero multiplicity computed by
binary matrix powers and elimination is checked against a separate Leibniz
characteristic polynomial. Every cap's exact maximum, admissible count and
maximizer count is printed. It also verifies 561 corank-one and 594 general-rank
attaining constructions through dimension 33 and fifteen explicit
domain/witness rejection controls, including the cap-three counterexample.

The separately implemented lead oracle reports
`PASS_INDEPENDENT_CAPPED_SPECTRUM`. It uses characteristic determinants and
literal kernel-vector counts, without importing the author engine or any
predecessor. Its complete censuses cover all 66,066 binary matrices through
dimension four and all 260 matrices over F4 through dimension two, across
every endpoint rank for the cap-two theorem. This is
independent AI implementation evidence, not independent human or proof-kernel
certification. Both engines also run with optimization enabled.
The exact reviewed file hashes and review boundaries are in [REVIEW.md](REVIEW.md).

Every direct command is read-only and needs no repository, Git, network,
third-party dependency or external source file. The manifest registers all
four bounded runs. Metadata/source-history checks are separate from the
mathematical verifier and require the repository's Git history.

Local CPython 3.12.14 warning-strict normal and optimized registered runs
passed, as did metadata/source pins and committed-byte checks. The optional
`--check-source-history` command was attempted and refused this shallow
checkout with `source-history check requires full Git history`; full-history
ancestry validation is not claimed. No history hydration or full selected
baseline replay was performed for this standalone side result.

## Sources, scope and overlap

The base is canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`,
priority revision 8. [SOURCES.json](SOURCES.json) binds the selected result,
original task card and the proof, README and open question from #5928 at
that commit. All are historical provenance; no predecessor program is
imported or claimed independently replayed. The selected JSON governs
current status despite older task text: selected #6030 has conditional
kappa 0.003125804, complex binding, admitted BIT 0.0034, and five retained
framework assumptions. This package changes none of those.

The assigned `bit-helper-contract` task is explicitly changed to this local
side obligation. It supplies no G20 word or full supplier budget. All-state
PR metadata/body searches for shared block, spectral, nilpotent plus cap,
corank, and #5928 found the credited predecessor and no successor solving
this object. #6560 concerns reflection-call compilation of an individual
nilpotent chain and has a different contract. The lead also checked chain
length and nilpotent index. These searches do not exhaust arbitrary old
diffs, all historical Discussions, mathematical literature or unpublished work.

Credit Nick Petalas/#5928 for the unrestricted spectral envelope, explicit
odd-block construction, corank-one rigidity and cap question. Credit
JoyboyBrian/#5507 for the two-owner four-support funding obstruction and
triple compensation; Ali Romman/#5456 for the early-helper model; and the
retained #5452/#5388/#589/#555 BIT, native, owner and compiler lineage. General
rank-one perturbation, primary decomposition, Jordan, trace and triangular
splitting methods are classical; no general mathematical priority is claimed.

## Limits and unrun obligations

The two sharp formulas cover every cap at corank one and cap two at every
rank, only in characteristic two. Finite enumeration stops at dimension four over F2 and dimension two
over F4; other dimensions and fields rely on the written proof. The
construction checks through dimension 33 are samples of the proved formula.
No native support history is supplied, and no theorem identifies a physical
call's chain restriction with this algebraic zero-primary cap. Larger-corank
sharpness, global compensation, chronology, ownership, dirty restoration,
precision/tape, compiler realization, full target/paid accounting and supplier
admission remain outside scope. No selected scientific replay, Lean or Docker
run is needed or claimed. Hosted CI status is reported separately by the PR.

## Open next questions

- Determine the sharp envelope at corank two with a cap of three. Start with
  the rank-two version of the surviving-subspace argument and an exact
  small-dimensional census. The cap-two compression argument no longer
  identifies square ranks with nonzero-primary dimensions, and corank-one
  parity and its single odd core do not establish a sharp general law.
- For one pinned larger-support caller, prove that its actual chronological
  A,B blocks satisfy this precise zero-primary cap, then complete its
  ownership and full target/paid invoice. No such caller or applicability
  argument is supplied here.

The relevance, first steps and blockers are also in [TASK.json](TASK.json).

## Implementation bounds

Both engines use explicit exceptions for admission and equality checks,
which remain active under `-O`. Author enumeration stores at most 65,536
small profiles; construction dimensions are at most 33. The independent
oracle enumerates at most 65,536 matrices and sixteen vectors at a time,
with determinants of order at most four. No recursion, dynamic code,
subprocesses, plugins, external imports or writes occur in either engine.
Python containers and arbitrary-precision integers use managed allocations;
these are bounded finite verifiers, not fixed-memory native implementations.

# Choosing precision from target dirt can destroy injectivity

A coarsest-compatible-grid policy applied to the pinned PR628 length-one
leaf is **two-to-one**, despite every executed call passing the leaf's
admission checks. With source `1`, the policy sends both target `0` and target
`1/32` to `-5/16`, and restores the source. Thus this adaptive forward map has
no inverse on the visible data unless additional branch information is kept.
This is a counterexample to a proposed adaptive policy, not a bug in the
retained caller, which uses one fixed execution precision.

## The policy and actual source execution

Use `dirty-prefix-precision/vendor/pr628/dirty.py:compose` with one outside
factor `b=1/4`, scale `1`, phase `[1]`, `beta=1/2`, direction `+1`, source
`[1]`, and no scratch. The real target is `q/32`, for any integer `q`; its
imaginary component may be arbitrary on the coarse `1/16` grid. Choose
`bits=4` if `q` is even and `bits=5` if `q` is odd. This is the coarsest of the
two precisions that admits the incoming data. Both grids satisfy the leaf's
closure precision and stability checks.

The length-one leaf adds a source-only deterministic increment. In literal
order, its recurrence is

```
power = Q_p(1/4)
seed = Q_p(1/(1-power))
value = 1 + Q_p(Q_p(1/4)*seed)
increment = Q_p(-value/4)
```

Here `Q_p(v)=2^-p floor(2^p v+1/2)`. It gives `-5/16=-10/32` at `p=4`, and
`-11/32` at `p=5`. The verifier derives these using separate rational
rounding code and compares them to the actual imported source execution.
The target is added to exactly and is not an input to this recurrence.
Therefore, for every integer `k`,

```
F(2k/32)     = (2k-10)/32
F((2k+1)/32) = (2k-10)/32.
```

The imaginary component and the source are unchanged. This is an infinite
collision family, not merely a finite failure of a proposed reverse word.
The result extends the prior [mixed-precision inverse boundary](../mixed-precision-inverse-boundary/README.md)
(PR1451), which exhibits a noncancelling inverse after changing precision.
Here the forward adaptive policy itself is noninjective. PR1054's allowance
for target-dependent approximation error is a separate contract; no change
to its error estimate is asserted here.

## Residue-translation theorem

Let `m>=1` and fix integer increments `a_0,...,a_(m-1)`. On the whole integer
lattice define `F(q)=q+a_r` when `q congruent to r (mod m)`. Then the number of
preimages of any integer `y` is exactly

```
#{r in 0,...,m-1 : r+a_r congruent to y (mod m)}.
```

Proof: within branch `r`, the only possible preimage is `q=y-a_r`, and it
belongs to that branch precisely under the displayed congruence. Distinct
valid branches give distinct preimages because their residues differ.
Thus `F` is bijective if and only if `r -> r+a_r mod m` is a permutation.
This criterion also classifies its exact missing-image residues and fiber
multiplicities. The proof concerns the unbounded integer lattice; clipping,
wrapping and saturation require their own models.

For `m=2`, bijectivity holds exactly when `a_0` and `a_1` have the same parity.
Otherwise both branches map bijectively onto the same output parity class,
so each point in that class has two preimages and the other class is missed.
Our actual leaf has increments `a_0=-10`, `a_1=-11`, yielding the collision
family above. A fixed source slice already fails injectivity, so preserving
that source as visible data cannot repair it.

## Branch information and positive controls

Storing the chosen precision distinguishes the two inputs. Executing the
negative leaf at that same precision restores each exactly, because the
increment is source-only and deterministic. At least two distinguishable
auxiliary states (one bit) are necessary to distinguish each two-element
fiber. This is an information lower bound; no free clean bit, transcript
allocation, native reversible compiler or transcript erasure is supplied.
Choosing precision afresh from the shared output always selects the coarse
grid and restores the even input, failing on the odd input. A single fine
precision used for both signs remains a valid baseline on the whole fine
grid. The retained caller's same-grid restoration argument is unaffected.

## Reproduce and evidence

```sh
python3.12 scripts/research_package.py --package research/adaptive-grid-injectivity-audit
python3.12 -I -O -B research/adaptive-grid-injectivity-audit/verify.py
```

The registered Python 3.12 and optimized runs passed. `EXPECTED.json` records
387 actual admitted collision pairs (129 adjacent real pairs and three
imaginary dirt values), 1,161 fixed-grid inverse positive cases, 774
stored-branch inverse cases, and 387 failures when the branch is forgotten.
An off-grid coarse call is required to fail with the actual admission error.
A separate brute integer-image implementation checks the residue theorem
for every residue policy at moduli 2 through 5: 3,412 policies, of which 152
are bijective. Added whole-period shifts test that the classification does
not assume increments are reduced residues. The proof above supplies the
all-integer statement; the finite census is an independent failure control.
All imported PR628 modules and contextual retained sources have immutable
Git blob and SHA256 pins in `SOURCES.json`. No predecessor verifier is used
as an oracle. The baseline selected-record binding was replayed; full
selected-supplier/native/physical/Lean replays were not run.

## Open next questions

Can a useful target-adaptive precision policy preserve injectivity without
retaining a branch transcript? Start with a proposed finite-residue policy
and check whether its translated residue images form a permutation; then
prove that the actual rounded leaf has those source-conditioned increments
for every admitted source. Source-dependent increments, nonlinear precision
selection and the cost of reading/erasing the precision choice remain
obligations. This audit changes no selected profile, supplier or kappa.

## Credit

woklerx with substantial OpenAI Codex assistance; Apache-2.0. Chafik
Boukhalfa's PR628 supplies the rounded cyclic inverse prototype; Gareth
Davidson's dirty-prefix-precision retains its fixed-grid caller and proof;
woklerx's PR1451 supplies the prior mixed-grid inverse boundary. Ali
Romman's PR621 and the pinned vendor NOTICE retain the kernel lineage.
No independent human review or new multiplication result is claimed.

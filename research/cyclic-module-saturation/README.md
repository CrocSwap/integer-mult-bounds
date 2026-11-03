# Multiplication tensor reconstruction without field enumeration

Scoped constructive proof with exact finite corroboration. A deterministic
O(n^7) exact-field-operation algorithm recognizes tensors isotopic to
commutative unital n-dimensional algebra multiplication and returns the table
and three invertible factor maps. It uses neither primitive decomposition nor
field-scalar enumeration. No new kappa is claimed.

Ali Romman's [PR5540](https://github.com/CrocSwap/integer-mult-bounds/pull/5540),
head `831b41da0fc09e3e4cb983c03662da5df7970f68`, reconstructs these tensors by
testing the local tops of two nucleus modules. Its stated complexity is
polynomial for fixed prime, with scalar enumeration in primitive decomposition.
The new implementation replaces that step by the following bounded scan.

```text
v=0, e=0
for each coordinate vector w of the module:
    z = v + (1-e)w
    J = Ann_A(M/Az)
    e = identity of J^(dim A)
    v = ez
return v, e
```

The output satisfies Av=eM. The idempotent e is the largest one for which eM
is cyclic, so e=1 decides cyclicity. At most dim M coordinate probes are
needed. Combining this constructor with the nucleus reconstruction yields
the O(n^7) bound over every supplied exact field, including small fields with
many local components. [PROOF.md](PROOF.md) gives all quantifiers, the power
bound, the three factor maps and the operation count.

General deterministic cyclicity algorithms are established, including
[Lenstra and Silverberg, 2015](https://arxiv.org/abs/1501.00183v2).
The new repository contribution is the explicit saturation constructor and
its uniform tensor-reconstruction application. No general cyclicity-theory
or literature-priority claim is made. Classical Artinian local structure,
Nakayama's lemma and the predecessor's nucleus reconstruction retain credit.

## Evidence and reproduction

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/cyclic-module-saturation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/cyclic-module-saturation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/cyclic-module-saturation
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/cyclic-module-saturation --check-source-history
```

Substitute another CPython 3.12 executable on another machine. The verifier
prints `PASS_CYCLIC_MODULE_SATURATION` in a generated JSON receipt bound to the
SHA256 hashes of all nine package files. Redirect stdout outside the checkout
to retain it. It writes no files. The registered normal and optimized commands
run the same checks, with all acceptance and rejection checks active in both.

- The complete prescribed quadratic-algebra/two-dimensional-module grid over
  F2, F3 and F5 has 16,418 candidate actions, of which 750 satisfy the module
  equation. The saturation output agrees with a separate literal enumeration
  of every module vector and algebra idempotent in every valid case. There are
  712 cyclic modules and 28 proper nonzero maximal cyclic parts. The remaining
  ten have zero maximal cyclic part. These counts describe this finite domain.
- Eighty-five constructed module fixtures over characteristics 2,3,7,257,65537
  cover regular, nonregular dual, mixed, changed-basis and truncated examples.
  Fifteen mixed presentations have a proper cyclic component. The split
  coordinate examples attain every scan length through eight. The tests also
  distinguish Ann(M/Av) from Ann(v) and force nilpotent ideal powers to vanish.
- Seventy-five independent-basis tensor presentations reconstruct successfully.
  Their direct certificate checker verifies 630 transported basis products.
  Ten nonregular module tensors reject, as do 75 altered output maps and ten
  explicit input/mathematical controls.

These checks exercise the new construction. They import no predecessor code
and replay no predecessor scientific suite. Quantified conclusions rest on
the written proof. Independent human and formal proof-kernel review are
unclaimed. CI execution is reported separately in the PR body.

## Interfaces and limits

`model.py` exports validated `Algebra` and `Module` inputs and `cyclic_part`.
Algebra tables use `table[i][j][k]` for the coefficient of basis k in i*j.
The unit is explicit and need not be a coordinate vector. Module matrices
act on column vectors. The returned `(v,e,trace)` includes the orbit-rank
trace; `check_part` checks generation of eM, while maximality uses the proof
and the bounded independent oracle.

`tensor.py` exports `recognize(t,p)`. It returns `(certificate,None)` on
acceptance and `(None,reason)` on mathematical rejection. Invalid inputs
raise `ValueError`. Certificate maps have basis images in columns and obey
`t(Ua,Vb)=W*mu(a,b)`. The separate `check` verifies algebra laws, invertibility
and every basis product without reconstructing the nucleus.

The bounded reference accepts prime p<=65537, algebra/module dimensions 1..8
and tensor dimensions 1..4. Prime validation uses bounded trial division.
The theorem's field-operation model assumes a supplied exact field, so it
includes no primality/factoring/field-construction guarantee. Extension fields
and rational arithmetic are covered by the proof but have no executable input
layer here. Polynomial field-operation count does not imply polynomial
rational bit complexity or a measured runtime improvement.

The output is some multiplication table and its isotopy. General recovered
algebra isomorphism, prescribed local presentations, height types and
determinant-one orbit labels remain separate tasks. No native coefficient
execution, caller invoice, restoration, ownership, precision/tape, compiler
closure, analytic recovery, complete multiplier or selected-frontier update
is supplied. Selected cold replay, native replay, Lean and Docker were not run.

## Engineering bounds

The code has no recursion, generated code, network or subprocess calls.
Production loops inherit the enforced eight-dimensional bound, or the
four-dimensional tensor bound. The largest nucleus has 64 equations in 32
unknowns. Ideal-product spans have at most 64 candidate vectors of length
eight. The exhaustive verifier streams its fixed grids and retains no history;
the literal oracle stores at most 25 vectors. Every function stays below
60 physical lines. Explicit representation laws, monotonicity and endpoint
checks remain active under optimization.

Power of Ten rule 3 has a Python-runtime deviation. Integer, tuple and list
allocation occurs during exact arithmetic. The enforced domains above bound
live state; canonical modular arithmetic bounds residues by 65536, and the
bounded dense arithmetic intermediates fit within 64 bits. The replay hashes
exactly nine files, each capped at one MiB. Normal and optimized warning-strict
execution and syntax/function-size inspection check these bounds. A production
fixed-capacity backend would require a separate implementation. Rule 9's ten
test callbacks are explicitly listed, local and do not escape the verifier.

## Open next questions

Can a recovered table and its transporter be realized by an affordable complete
native caller? Choose one accepted table and price every coefficient map,
arbitrary dirty input, native action, return and restoration before widening
construction search. Recognition supplies none of these physical costs.
The structured first step and blocker are in [TASK.json](TASK.json).

## Credit and provenance

This contribution was produced by Nick Petalas. Apache-2.0.
Credit Ali Romman / PR5540 for the reconstruction interface and fixed-field
algorithm; apoursh / PR5502, Nick Petalas / PR5252 and David Ganz retain the
algebra/atlas lineage named there. Lenstra and Silverberg retain prior
cyclicity-algorithm credit. No predecessor credit line or frozen source changes.

Base main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8,
selected PR6030. [SOURCES.json](SOURCES.json) pins the source README as provenance,
not an executable input. The baseline source-binding control passed.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19362864)
reserves the generator step. This package includes its explicit tensor corollary
and implementation. Main/general-form searches, merged/all-state PR searches,
live handoffs and local reservations found no matching saturation-reconstruction
result in inspected coverage. The full overlap snapshot covered 406 open PRs,
6,350 Discussion records and 8,917 tracked research notes. Unpublished work and
arbitrary historical code diffs remain outside that coverage.

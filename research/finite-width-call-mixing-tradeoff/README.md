# Exact finite-width slice-call versus binary-addition tradeoff

For one dense m-axis transform at width f, using at most s slice calls,
the exact minimum number of binary scalar additions is

```
A_min(m,f,s) = f*(m-s),   m,f >= 1,  0 <= s <= m.
```

This is a scoped mathematical proof with exact finite corroboration. The
lower bound permits arbitrary monomial free operations. Attainment permits
permutations acting on individual digit columns, one zero helper, free copies
and free resets. Those are explicit assumptions of this resource model.
The tied-column engine of Jacob Alan Sussman's [PR #4628](https://github.com/CrocSwap/integer-mult-bounds/pull/4628)
is a narrower model. The upper construction here is width-aware and does not
supply an upper construction in that engine. No new kappa is claimed.

The first fixture is m=3, f=2, s=2. Two tied slice calls and two binary
additions attain the transform. One addition cannot suffice, regardless of
the number of zero helpers, free monomial maps, copies or resets.

## Contract

Put a=(1+i)/2, b=(1-i)/2 and C=a*I+b*X, where X exchanges the two basis
vectors. A register has coordinate space

```
V = (complex^(2^m))^(tensor f),  dim V = 2^(mf).
K = (C^(tensor m))^(tensor f).
```

Index V by f columns of m binary address coordinates. For a
nonzero v in F2^m, X_v translates one address by v and a paid slice call is

```
(C_v)^(tensor f),  C_v=a*I+b*X_v.
```

There are finitely many registers, with no fixed upper bound. One register
starts with arbitrary input x; all others start at zero. A program is a finite
straight-line sequence of input-independent linear operations. Its operations
are:

- A paid slice call on one register, counted once per invocation.
- A binary scalar addition r := lambda*p + mu*q, counted once. Coefficients
  are arbitrary fixed complex numbers, with no magnitude restriction.
- Free unary monomial maps, scalar multiplications, copies and resets to zero.

A monomial map has one nonzero entry in every row and column. Its choice can
depend on m and f, but not on x. Free copies may create a register or overwrite
one; arbitrary-arity sums must be expressed using counted binary additions.
The output is K*x in the input register, with every helper returned to zero.
All call and addition costs include their use on helpers. There is no free
arbitrary scalar matrix mixing across registers and no nonzero advice input.
The program must be exact for every x at its stated finite width.

The lower bound below also holds if helpers need not be returned. Attainment
uses one helper and the explicitly allowed resets; it does not restore an
arbitrary dirty helper or provide a reversible implementation of a reset.

## Proof of the lower bound

Fix any input basis column e_j. At the start, every register has support at
most one. Let p and q be the numbers of paid calls and binary additions so
far. By induction every register has support at most 2^(fp+q).

A unary monomial map preserves support. Scaling, copying and resetting cannot
increase the largest support. An addition has support contained in the union
of its two inputs, so it increases the global support bound by a factor at
most two. Every column of C_v has two nonzero entries, so every column of its
f-fold tensor power has 2^f nonzero entries. Applying a paid call therefore
increases the support bound by a factor at most 2^f. Cancellations can only
reduce support. These observations prove the induction for any register and
any finite program, including singular mixing and erasures.

Both a and b are nonzero. Every column of K consequently has exactly 2^(mf)
nonzero entries. An exact program with p calls and A additions must satisfy

```
2^(mf) <= 2^(fp+A),  hence A >= f*(m-p).
```

If p<=s<=m, this implies A>=f*(m-s). This is a support argument over the
complex field, not a numerical approximation or a finite-search inference.
It is the quantitative resource consequence of the support method cited below.

## Attainment in the width-aware model

First apply one tied slice call C_(e_j)^(tensor f) for each of s distinct
coordinate axes j. These calls implement C on sf individual bits.

For each remaining axis and each of the f columns, use the following four
steps. Let X_(j,c) flip that single address bit in that one column.

```
helper := input_register
helper := X_(j,c) * helper
input_register := a*input_register + b*helper
helper := 0
```

The third step is one binary addition. Its action on the input register is
exactly C on the selected bit. All selected bit operators commute. After the
f*(m-s) iterations, every one of the mf bits has received C once, so the
complete endpoint is K*x with the helper zero. There is no input-dependent
control or free dense transform in the construction.

The complete declared invoice is s paid calls, A=f*(m-s) binary additions,
A copies, A one-bit monomial permutations and A resets. The additions use two
free scalar multiplications apiece. No further workspace is needed. Thus the
lower bound is attained for every m,f,s in the theorem's domain.

The uncharged monomial operations and resets are a formal resource assumption;
they do not describe a physical instruction invoice. In particular, individual
column flips are wider than the tied-column free-address operations in #4628.

## Explicit width threshold

A proposed all-width family with fixed s<m and fixed addition budget A fails
at every integer width

```
f >= floor(A/(m-s)) + 1.
```

The formula needs no bound on the number of free monomial maps or helpers.
It sharpens an eventual support-growth obstruction to an exact width/resource
tradeoff. For example, at m=3 and s=2, a budget of 17 binary additions cannot
work at width 18. At finite widths a zero-call construction is possible in
the wider model, but it uses exactly mf additions. A fixed program whose
addition count is independent of f cannot obtain that behavior at all widths.
The theorem gives no direct-sum lower bound for several independent outputs.

## Evidence and reproduction

The universal statements are the written proofs above. The standalone
standard-library checker corroborates bounded instances using Gaussian-integer
numerators with a common power-of-two denominator. It executes the copy,
permutation, addition and reset steps on every input basis column. An independent
closed Hamming-distance formula supplies each expected target column. It checks
both the complete output operator and the helper's zero endpoint.

The 33 construction fixtures cover m=1..4, f=1..3, mf<=8 and every s=0..m,
with all 1,928 input basis columns checked.
A separate subset expansion tests all nonzero paid directions for m=1..3,
f=1..3, mf<=6, comprising 26 cases and 770 input columns. Eight invalid-input
controls and seven operation mutations reject, including omitted operations and
replacement of the required individual-column permutations by a tied flip.
The printed receipt enumerates the exact coverage, hashes the endpoint
transcript and binds all five package source files. `--emit-receipt` produces
JSON alone. Both modes write nothing; store any receipts outside the checkout.

From the repository root:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/finite-width-call-mixing-tradeoff
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/finite-width-call-mixing-tradeoff/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/finite-width-call-mixing-tradeoff/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/finite-width-call-mixing-tradeoff --check-source-history
```

The direct marker is `PASS_FINITE_WIDTH_CALL_MIXING_TRADEOFF no_new_kappa`.
Normal and optimized execution retain all checks through explicit exceptions.
The verifier needs neither Git, network access nor predecessor executables.
The metadata and source-history checks additionally use Git provenance.

## Scope, provenance and implementation limits

The original formal-interface-lemma card is changed to a written resource
lemma, with no proof-assistant formalization. The selected-source orientation
command passed on base a5df48c55ea806d7952b65acc9c76d878ff09b13, priority 7.
This is a side result about the cost hidden by free register mixing. It does
not resolve the small-saving cases listed in #4628 or change any selected input.

The live overlap snapshot covered 333 open PRs and 4,362 Discussion records
with complete pagination. The sparse local scan covered 145 of 6,918 indexed
notes. Distinctive main-tree and merged-PR searches were also run. This coverage
does not establish novelty against unpublished work or arbitrary historical diffs.

All verifier loops have fixed bounds. Vectors have at most 256 coordinates;
Gaussian exponents are at most eight, and each program has at most 32 steps.
No recursive call, external process, dynamic code loading or callback dispatch
is used. Functions fit within 60 physical lines. Python and its standard library
allocate managed objects during replay, a Power-of-Ten rule 3 deviation. The
fixed domains bound live vectors and integer sizes; runtime allocations are
not independently instrumented. Warning-strict normal and optimized replay
provide the configured diagnostics. No external static analyzer is configured.

Independent human and formal proof-kernel review are unclaimed. There is no
physical tape, routing, precision, compiler or ownership implementation here;
no supplier admission, selected cold replay or complete multiplication theorem
is claimed. No kappa or selected-frontier change follows.

## Open next questions

- What is the exact finite-width addition/call tradeoff when every free address
  permutation must act identically on every digit column? Start with m=2,f=2
  and identify which dense endpoints lie in the generated operator span. The
  one-column shifts used for attainment here are forbidden in that model.
- What changes when the helper is arbitrary dirty data and every operation
  must be reversible? Start with one unimplemented bit and derive a complete
  return word. This construction's copies and resets cannot supply that word.

## Credit

This contribution is produced by Nick Petalas. Jacob Alan Sussman's #4628,
head ee4fd87f064017c23e5a86fc1dcfe0a5237caed3, supplies the all-width support
argument in [PROOF.md section 4](https://github.com/CrocSwap/integer-mult-bounds/blob/ee4fd87f064017c23e5a86fc1dcfe0a5237caed3/research/complex-small-m-lower-bounds/PROOF.md)
and the width-one zero-scratch example. That argument and those certificates
are cited predecessors, not replayed deliverables. The new step is the exact
binary-addition resource law, its explicit first failing width and its sharp
width-aware construction. Support counting and the one-bit linear identity
are elementary methods; no literature-priority claim is made for them.
Credit eumemic #288 and Swapnil Jain for the retained subspace/call framework,
Jose Manuel #2108 for the scalar-mixing obstruction context, and the retained
register-model contributors. New material is Apache-2.0.

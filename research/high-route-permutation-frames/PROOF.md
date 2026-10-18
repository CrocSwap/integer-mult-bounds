# Carry permutation frames through the high-field word

This is an opt-in change to the factor words consumed by Jose Manuel's
PR2915 registry and unchanged physical high-cube executor. It preserves the
completed interface. It does not supply a fitted B1 implementation, change
the recursive child profile, or certify a multiplication exponent.

## 1. Exact scheduling identity

Let `x` be the logical row after a prefix of the original column word, and
`y` the row after the emitted physical word. Maintain a permutation `p` with

    x[j] = y[p[j]] for every logical field j.

Initially `p` is the identity. A logical swap of `a,b` changes only
`p[a],p[b]`; the values need not move at this point. A logical scale of `a`
is a physical scale of `p[a]`. An ADD `x[t] += c*x[s]` is a physical ADD
`y[p[t]] += c*y[p[s]]`. If `p[s] > p[t]`, physically swap these two fields
first and update both the location and inverse-location tables. The ADD
then has its control before its target, exactly the order accepted by the
unchanged `kernels.added` path. These three updates preserve the invariant.

At the end, for each `j` with `p[j] != j`, emit the actual swap of physical
positions `p[j]` and `j`, updating the tables. Previously fixed positions
are not disturbed. This terminates with `p=id`, using one less swap than
the length of each nontrivial cycle. Every terminal swap is retained and
paid. The completed physical word therefore equals the original linear
operator for arbitrary input rows, including dirty values.

The implementation also applies this procedure to the inverse word, then
inverts the emitted word. Exact equality and the swap-call count survive
inversion. It selects the cheaper of those two deterministic candidates,
and keeps the original unless native calls strictly fall and the complete
setup/adapter upper-bound coefficient does not increase (Section 3).
This is a bounded heuristic,
not an optimal permutation-scheduling theorem. Both candidates contain
only ordered ADDs. All non-swap factors and coefficients occur in their
original relative order, with remapped target/control indices.

The proof holds over any commutative ring where the scale coefficients
are units. The reached dyadic coefficient alphabet is legal over odd
q-power rings. It neither identifies nor discards global phases.

## 2. Exact low carries and the completed high cube

PR2915 first specializes a rational column word to a low class `l` modulo
odd `q`, then emits the high-field program. Apply the same invariant to
the low residues: the logical low value is always in the position specified
by `p`. At a scale or ADD, the rational numerator, denominator and actual
target/control residues are unchanged. Thus the canonical following residue
and carry computed by `Registry.compile` are unchanged, with their field
indices remapped. Emitted physical swaps change low residues as well as
high fields. The paid final swaps restore canonical field order. This
proves the same target low class and the same full q-adic address map for
every legal low class and high width, without enumerating all low classes.

For dimension d there are d row copies of the column word and N=d² high
fields. The argument acts independently on each row. Every binary call
still has the complete layout `[B][Q][M][Q][S]`, volume `V=B Q M Q S`,
where the four extents are rebuilt by unchanged `high_route.extents`.
Remapping a field can change B,M,S, but cannot change V or omit a spectator.

No runtime rename is assumed free. Only the offline compiler uses the
location tables; every emitted field exchange is an existing paid B1 call.
The optional registry is finite for fixed q,d and uses the same keys and
fixed physical executor. Each factor returns its distinct output lease
before the prior owned intermediate is erased. The original cube copy,
borrowed-source restoration, numerical setup/erasure, terminal ordering,
prefix wrapper and final output ownership all remain in the execution.
The new schedule needs no additional payload or numerical tape roles.
Successful execution and the existing native endpoint/head/spectator
contracts remain premises, as in PR2915.

## 3. Complete cost, including changed setup

For a column word let S be its explicit swaps and R its reversed ADDs.
For positive high width, the original complete native-call count per row
is `S+2R`. The selected candidate has count S' and no reversed ADDs, so
the whole cube has

    t = d(S+2R),       t' = d S' <= t.

If the original is retained, its count and complete program are unchanged.
The number of ADDs, doublings/halvings, negations and carry translations
is unchanged. However the number of explicit high operations changes by
`delta_s = d(S'-S)`. It is incorrect to call that setup free, or to infer
that every small invocation is faster just from t' <= t.

Here is an explicit complete conditional tariff using Krzysztof Wójt's
PR3301 source argument, pinned with credit in `sources/pr3301-PROOF.md`.
That pending proof is an inherited premise, not independently admitted by
this package. Put

    beta = 3[716 + 1866 bit_length(N)] + 36.

For a cube of V bits, original input-bank width I and K high-bank roles,
and unchanged counts a,h,g,c of ADD, scaling, sign and carry factors, its
bound applied to the new word is

    T' <= sum of every complete new native interval A'_j
          + 27 I + 10 K
          + [373 + s' beta + 4096 a + 530 h + 4096 g
             + 32768 c + 100000 t'] V.

This includes all copies, source access, frame changes, intermediate
clearances, numerical setup and teardown inside cube entry/return. Add
the inherited complete-prefix wrapper once (265 times the complete packet
volume, or 277 including final output disposal). For Q=1 the executor
skips all factors; the original copy/setup bound applies. Provisioning,
finite-control compilation and enclosing recursive stock/backing remain
outside this local tariff, exactly as in the cited source contract.

If a same-domain uniform native tariff is `A_j <= C_B V u^p`, then the
change in these *upper-bound expressions* is

    [(t'-t)(C_B u^p + 100000) + beta delta_s] V.

The compiler requires `100000(t'-t) + beta delta_s <= 0` before accepting
a candidate. Since t' < t and C_B u^p >= 0, the complete upper-bound
expression cannot increase, pointwise for every admitted V and width. The
gate is substantive: the four-factor word ADD(0,3), ADD(0,1), SWAP(0,1),
ADD(0,2), embedded in dimension 64, permits a seven-to-five call reduction
whose per-row setup/adapter coefficient rises from 774958 to 874790. The
compiler retains the original, and a control checks this case.

This is not a comparison of unknown actual native times. It accounts for
the extra explicit-swap setup. There is no claimed selected-stage
coefficient or universal physical speedup. The exact certificate
records delta_s and the setup term for every chart orientation so consumers
can use their own native tariff. No missing native or outer obligation is
priced at zero.

## 4. Evidence boundary

`check_algebra.py` uses separately written rational row-vector semantics;
it imports no predecessor evaluator. Exhaustive small words and seeded
larger words test the implementation, including omitted final restoration
and a wrong remapped control. The invariant above is the general proof;
the finite checks alone are not that proof.

`check_catalogue.py` authenticates the source closure, constructs the actual
PR2915 selected registry, and checks each source chart and inverse with
independent exact row semantics. Its occurrence-weighted call bill uses the
retained catalogue's occurrence multiplicities and 64 row copies. It is a
finite routing invoice, not a complete recursive/native execution or a new
child histogram. Complete selected GL64 payloads are not materialized.

`check_physical.py` uses Jose Manuel's existing complete-column oracle and
physical simulator. It adds an observer counting each Tape read, write and
unit move once, isolates every complete native interval, and keeps three
occupied dirty scratch leases with nonorigin heads. The output map, source,
spectators, lease ownership, heads and erasure are checked. Its q=3/5
fixtures execute elementary B1 calls; they do not establish the fitted
all-width native premise. Timings and operation counts cover these exact
fixtures only. No full supplier, formal-kernel proof or new kappa follows.

Tekalign (`tekuuu`), with substantial OpenAI Codex assistance. Apache-2.0.
Credit Jose Manuel/PR2915 and PR2899, David Arias/PR2753, Nick Petalas's
ordinary wrapper and prefix/scaling invoices, commdata2338's PR3233 ADD
invoice, Sagar Thakrar's PR3265 setup work, Krzysztof Wójt's PR3301
composition, Arham Tahir's sign/countdown bounds, ywz65's parking work,
and the original PR2157/PR589/PR555 geometry and factor-word lineage.

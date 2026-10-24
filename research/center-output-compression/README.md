# Sharp information tradeoff for retained center outputs

This scoped algebraic proof determines what remains recoverable when a caller
compresses the output of Cinna Davis's retained-center interface. Given all 632
old output fields and only j independent scalar linear observations of its
eight center outputs, exactly **624+j independent linear functions of the
desired old endpoint** are recoverable, for 0 <= j <= 8. Recovering all 632
requires eight observations. Arbitrary nonlinear decoding cannot improve this
threshold. These are dimensions of information, not native call prices.

The contribution was produced by Nick Petalas. New work is Apache-2.0.

## Interface and exact target-specific theorem

Let F be any field. Let x in F^n and z in F^k be arbitrary independent inputs.
A is n by n, B is n by k, and R is k by n. The record matrix L has k columns
and the target matrix T has n columns; their row counts are unrestricted.
Assume the block map

    y = A x + B z,        w = R x + z

is invertible. Write S=A-BR, which is then invertible: a nonzero vector in
ker(S), together with z=-Rx, would give a nonzero kernel vector of the block
map. A caller sees all of y
and the linear record Lw. There is no other input-dependent state. L is fixed
independently of x and z. A target Tx is recoverable on every input, by an
arbitrary decoder, if and only if

    ker(L) is contained in ker(T S^-1 B).

Equivalently, every row of C=T S^-1 B lies in the row space of L. Therefore the
least possible rank of a center record recovering Tx is exactly

    rank(T S^-1 B).

This includes singular targets T and rank-deficient B. A basis of the rows of C
is an attaining record. The theorem does not assume that individual center
coordinates, rather than their linear combinations, must be retained.

### Proof

Substitute z=w-Rx. Then y=Sx+Bw, and hence

    Tx = T S^-1 y - Cw.

If ker(L) is contained in ker(C), row-space duality supplies a matrix D with
C=DL. The displayed expression gives a linear decoder using y and Lw.

Conversely choose v in ker(L) with Cv nonzero. Compare the zero input with

    delta x = -S^-1 Bv,       delta z = v-R delta x.

Their y and Lw observations agree, whereas their targets differ by -Cv. No
decoder, linear or nonlinear, can distinguish these inputs. This proves the
criterion. It also forces rank(L) >= rank(C). Choosing a row basis of C attains
that lower bound. This is a standard kernel argument applied to this boundary;
no priority is claimed for rank-nullity or block elimination themselves.

## Sharp full-endpoint tradeoff

Assume additionally that A is invertible and B has column rank k. For a fixed
record L of rank j, all possible differences in x between inputs with equal
observations form exactly

    U = S^-1 B ker(L).

Since S^-1 B is injective, dim(U)=k-j. The recoverable linear functions of Ax
are exactly the annihilator of AU. That space has dimension n-k+j. Each of
its functions has the decoder just proved, so this is an equality for every
rank-j record L, rather than only a lower bound or an optimized choice of L.
It does not say that n-k+j particular coordinate entries can always be chosen.

Over a finite field of order q, every observation fiber has exactly q^(k-j)
possible old endpoints. Thus arbitrary decoding does not distinguish two old
endpoints in the same fiber. The statement about independent linear functions
over an infinite field does not assert a bound on arbitrary nonlinear encodings.

## Application and predecessor credit

Cinna Davis's [PR #4694](https://github.com/CrocSwap/integer-mult-bounds/pull/4694),
head `2add42d1edf14a263abe90a3bcde67fc1ba30768`, supplies n=632, k=8,
A(X,Y,H)=(X,Y+X,H), invertibility of the whole interface, and rank(B)=8.
The merged [#4698 helper normalization](../center-helper-normal-form/README.md)
retains these properties and constructs eight explicit three-step chains.
Its [proof](../center-helper-normal-form/PROOF.md) states B's injectivity.
Those facts are cited premises, not reverified results of this package.
Their rational matrices give the specialization over Q and C. Their dyadic
native interface is not being specialized to characteristic two or three.

The theorem gives the following complete rank table:

    retained center rank j:  0   1   2   3   4   5   6   7   8
    recoverable old rank:  624 625 626 627 628 629 630 631 632

The new result is this sharp observation-compression law and its
target-specific minimum. The predecessor's helper basis and conditional
two-call consumer are not new here. Chris R's
[PR #4839](https://github.com/CrocSwap/integer-mult-bounds/pull/4839) constructs
and prices a particular physical terminal. Our theorem concerns the amount of
linear center information required when all old endpoint functions are
demanded; it neither reprices nor excludes other terminal policies.

Credit Cinna Davis #4694/#4698 and the #4440/#4441/#4447/#4470 lineage,
Cao Yifan #4610, Chris R #4839, zxv, Jacob Alan Sussman and the retained
native, scalar, E8, Clifford, precision and outer contributors. ywz65's
earlier center-observation-floor work supplies the information-boundary
perspective; its owner-routing model is a different theorem.
Ross Richardson's [#2480](https://github.com/CrocSwap/integer-mult-bounds/pull/2480)
proves a sharp retention threshold for another fixed QQ16 observation cut.
Ali Romman's [#4720](https://github.com/CrocSwap/integer-mult-bounds/pull/4720)
proves historical routed-query information and snapshot bounds. These are
credited precedents for kernel-based observation lower bounds. Neither counts
compression of the #4694 coupled endpoint studied here.

## Evidence and reproduction

The all-field claim is the written proof above. The self-contained verifier
uses two independent three-step chains at n=4,k=2. It enumerates every
zero-, one- and two-row record L over F2 and F3, including dependent rows.
For every L it enumerates every dirty input, checks every observation fiber,
constructs collisions, computes the recoverable row-space dimension and
checks target-specific recovery against literal zero fibers. It tests every
one-row target plus a full endpoint and a two-row target, and enumerates the
minimum record rank for each target. These small examples corroborate the
new theorem; they do not substitute for a native 640-column replay.

From the worktree root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/center-output-compression
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/center-output-compression/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/center-output-compression --check-source-history
```

On another machine substitute its CPython 3.12 path. There are no external
runtime inputs or dependencies. SOURCES.json pins the cited merged proof as
historical provenance; the scientific verifier does not import or replay it.
Checks use explicit exceptions and remain active with -O. The verifier writes
only stdout. No receipt is handwritten or accepted as evidence.

The card's historical first example was attempted and raised
`KeyError: 'complex_profile'` after the selected schema changed. The current
`scripts/research_selected_baseline.py` source-binding control passed. Neither
is an input to this algebraic theorem, and neither was repaired here.

## Scope, obligations and expansion decision

This is a scoped proof with finite corroboration, not a new supplier, kappa,
search failure, proof-kernel certificate or complete multiplication theorem.
The observation contract grants all old output fields and fixed scalar linear
center records. Additional input-dependent caller state, changed demanded
targets, nonlinear measurements, multiple calls or intermediate observations
can change the problem. The decoder is algebraic; endpoint chart conversions,
native reads, precision, routing, restoration, retained helper jobs and a
complete paid moment remain unknown. No information dimension is converted
into a recursive call count. The selected frontier is unchanged.

Power-of-ten inspection: loops have fixed n<=6 and p in {2,3}; no recursion or
child processes occur. The finite census intentionally allocates Python tuples,
sets and dictionaries, bounded by 729 inputs and 729 fibers per record.
This is a managed-runtime allocation deviation, not a fixed-memory claim.
No additional tooling or native/formal replay is required for the written proof.
Independent human and formal proof-kernel review are unclaimed.

Decision: stop at this information result. It does not justify another
construction round without a fully charged changed consumer.

## Open next questions

For one literal proposed consumer, compute C=T S^-1 B for its actual demanded
target T and find whether rank(C)<8. This can reduce the observation demand,
but the first step needs that consumer's explicit target matrix and costs.
Those are not supplied here. If all old outputs remain demanded, the sharp
threshold is settled under this observation contract.

Separately, price one attaining row-basis record in the actual endpoint charts.
Start with its literal read and restoration word. Scalar rank alone supplies
no native cost bound; this is the blocker to applying the result to a moment.

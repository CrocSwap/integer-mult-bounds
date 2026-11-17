# Exact correction rank for paired primal and dual support maps

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type.** Scoped algebraic proof with exact finite corroboration.

Let an injective map $f:S\to V$ prescribe the primal action. Let
surjections $g,\pi:V\to Q$ prescribe $P^{-\mathsf T}$ on dual support
through the equation $\pi P=g$. Under the compatibility condition
$\pi f=g|_S$, the minimum of $\operatorname{rank}(P-I)$ among
invertible completions $P$ is

$$
\operatorname{rank}(g-\pi)+\operatorname{rank}d
-\min(\operatorname{rank}(\pi d),\operatorname{rank}(g d)),
\qquad d(s)=f(s)-s.
$$

[PROOF.md](PROOF.md) constructs a largest possible fixed subspace and
extends the paired constraints by basis completion. The proof works over
every field. Allowing singular completions can lower the minimum. A
two-dimensional example has relaxed minimum one and invertible minimum
two over every field.

The support-completion route in GQ08 uses low-rank corrections to limit
the size of the auxiliary inverse in G17. The formula gives the smallest
possible rank for that step before factoring or pricing the coefficients.
It also detects when a low-rank completion of the primal and row equations
is too optimistic for a reversible word. [Atlas, #5803](https://github.com/CrocSwap/integer-mult-bounds/pull/5803).

## Evidence and reproduction

The verifier enumerates every binary matrix action in dimensions one
through three. For every primal subspace and dual row space it groups
the matrices by their literal primal and quotient actions, then compares
the minima with and without invertibility to the proof's formula. For
each dual row space it uses one basis. A different basis only changes
both quotient maps by the same invertible change of coordinates.

| Dimension | All matrices | Invertible matrices | Compatible contracts | Strict rank increases |
|---|---:|---:|---:|---:|
| 1 | 2 | 1 | 4 | 0 |
| 2 | 16 | 6 | 118 | 6 |
| 3 | 512 | 168 | 21,232 | 2,016 |

The verifier also checks the explicit two-dimensional gap and rejects a
mutated minimum that omits the invertibility charge. Its JSON output
records the counts and hashes of the six package files. The verification
commands are read-only. The census uses only the standard library. Its
matrix size is bounded by three, and live collections use managed Python
allocation within that finite domain.

From the repository root, run these with CPython 3.12. A different
installation can substitute its interpreter path.

~~~sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/primal-dual-completion-rank/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/primal-dual-completion-rank/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/primal-dual-completion-rank
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/primal-dual-completion-rank --check-source-history
~~~

The direct marker is `PASS_PRIMAL_DUAL_COMPLETION_RANK`. The two
repository commands report `PASS_REGISTERED_RESEARCH_PACKAGE` and
`PASS_RESEARCH_COMMIT_BYTES`, respectively.

## Scope

This is the algebraic part of GQ08. The construction works with compatible
maps over fields. Dyadic-unit realizability, coefficient growth, a retained
caller, signed native realization, owner restoration, tape and precision
costs, and the complete signed moment remain open. The selected $\kappa$
and its five framework assumptions are outside this scope.
Independent human and formal proof-kernel review are unclaimed.
Predecessor scientific replays, Lean, Docker and the selected cold replay
were unrun.

## Open next questions

- Does a named retained cut admit an optimal correction with paid scalar
  coefficients? First extract its two exact support maps and compute the
  field minimum. The resulting completion needs a literal word and a
  complete restoration and caller invoice.
- Which paired contracts over $\mathbb Z[1/2]$ attain the field
  minimum by a dyadic-unit completion? First test the optimal fixed
  subspace for a complementary saturated submodule and check its
  reductions at odd primes. A field complement need not give an
  admissible scalar word.

## Credit

David Ganz / Dugongue posed GQ08 and supplied G16's extension
parameterization and G17's low-rank inverse formula. Ali Romman's
dyadic helper-basis work is a related implementation precedent for
one normalized row/column pair. The ordinary block rank-completion
problem is classical. The contribution here is the fixed-space bound
and attaining construction under simultaneous invertibility and paired
support constraints. [#5803](https://github.com/CrocSwap/integer-mult-bounds/pull/5803),
[#5611](https://github.com/CrocSwap/integer-mult-bounds/pull/5611),
[Epperly, Govindarajan and Chandrasekaran, §2](https://arxiv.org/abs/2106.11267).

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19693317).
The atlas and dyadic precedent are pinned as historical provenance in
[SOURCES.json](SOURCES.json).

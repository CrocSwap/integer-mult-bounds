# Exact 60-call signed connector for all three-source ternary rows

One dirty connector can deliver every nonzero row of `{-1,0,1}^3` in
exactly **60 complete calls** over any field of characteristic zero.
An eight-call source cycle and 52 target readouts attain the bound.
The lower bound permits arbitrary extra readouts. Serving the same rows
separately takes 160 calls in the explicit comparator below.

Claim type: scoped written mathematical proof with finite exact corroboration.
This contribution was produced by Nick Petalas. Independent human and formal
proof-kernel review are unclaimed. No new kappa is claimed. Apache-2.0.

## Interface and predecessors

There are three immutable sources `x_0,x_1,x_2`, one arbitrarily dirty
connector `z`, and 26 distinct arbitrarily dirty outputs `y_v`, indexed by
nonzero `v in {-1,0,1}^3`. For arbitrary compatible linear maps over a
characteristic-zero field, the required complete action is

```text
y_v += sum_(j=0..2) v_j A_v B_j x_j;
every x_j and z unchanged.
```

The maps may be singular and noncommuting. Each allowed call has unit cost:

```text
+B_j: z += B_j x_j          -B_j: z -= B_j x_j
+A_v: y_v += A_v z          -A_v: y_v -= A_v z
```

Every call is a complete restored operation at fixed ports, including its
private scratch and entry heads. Negative means subtract the same map
application. The 30 public arrays remain reserved throughout. Outputs are
observed only after the complete word and cannot serve as workspace.
There are no other calls, extra connectors, source mutations, free copies,
root scalings, coefficient letters or address/frame changes. The fixed word
must work for every admissible collection of maps and arbitrary initial data.

Ross Richardson's [#944](https://github.com/CrocSwap/integer-mult-bounds/pull/944)
supplies this signed one-connector interface, the paired-prefix reduction,
and a canonical three-output obstruction. The new result changes its demand
to all 26 ternary rows and proves an exact all-word optimum for that batch.
It neither checks the predecessor's 19,683-matrix classification nor replays
its path census. His #934/#943 prefix and Gray-walk lineage, shhxera/CubeJerry
#889, and Chafik Boukhalfa #628 retain credit. No historical priority is
claimed for cube cycles or compute/uncompute.

## Construction

Use the following chronological source word:

```text
+B0 +B1 -B0 +B2 +B0 -B1 -B0 -B2
```

Its prefixes are

```text
000, 100, 110, 010, 011, 111, 101, 001, 000.
```

Thus every vertex of `{0,1}^3` is available before closure. For each demanded
row v define `p_j=max(v_j,0)` and `q_j=max(-v_j,0)`. Both p and q are cube
vertices and `p-q=v`. Insert `+A_v` at p and `-A_v` at q. These readouts
can be arranged by boundary time because they change neither z nor another
output. At prefix r the connector is

```text
z_initial + sum_j r_j B_j x_j.
```

The two reads therefore add `sum_j v_j A_v B_j x_j`; incoming connector dirt
cancels. The source path restores z as an integer identity. The construction
works in every compatible dimension and gives `8+2*26=60` complete calls.
The generated stdout receipt includes the literal 60-event stream.

For the comparator, handle each v separately: read `-A_v` at the initial
connector, add each nonzero `v_j B_j x_j`, read `+A_v`, and subtract those
source contributions. This restores z after each output. There are 6, 12,
and 8 rows of support sizes 1, 2, and 3, respectively. It uses 108 source
calls and the same 52 readouts, or 160 calls. The verifier constructs and
checks this comparator's complete formal action. The improvement is in
this declared query model, not a measured runtime comparison.

## Lower bound, including extra readouts

Fix any correct word and let b be its source-call count. Since it must
restore z for arbitrary independent source contributions, each source's
signed count is zero. Every source is demanded, so each appears at least
twice. Consequently `b>=6` and b is even.

For each output, set all source maps to zero and vary incoming connector
dirt and that output's map. Its signed readout count must be zero.
Every demanded row is nonzero, so every output has at least two readouts,
and its readout count is even. This gives the universal floor of 52.
If `b>=8`, the total is already at least 60.

It remains to exclude a total below 60 when `b=6`. Each source then occurs
exactly once with each sign. Its prefix coefficient belongs to `{0,s_j}`,
where `s_j` is that source's first sign. All prefixes lie in one reflected
unit cube. There are at most six distinct vertices: the final prefix equals
the initial one, leaving only six indexed source boundaries.

An output with exactly two readouts uses opposite signs, so its demanded
row must be the difference of two visited vertices. A difference with
all three coordinates in `{-1,1}` can only come from antipodal cube vertices.
The cube's four antipodal pairs give its eight distinct full-support signed
rows. Six visited vertices contain at most three antipodal pairs, so at least
two of those eight demanded rows cannot be served with two readouts.
Each requires at least four. The complete bill is therefore at least

```text
6 + 52 + 2*2 = 62.
```

The cases `b=6` and `b>=8` exhaust every word. The upper construction proves
the exact minimum 60. This is a written proof of all-word optimality in the
specified interface, rather than an inference from a search failure.

## Reproduce

From the worktree root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/full-signed-ternary-three/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/full-signed-ternary-three/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/full-signed-ternary-three
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/full-signed-ternary-three --check-source-history
```

Any CPython 3.12 installation can replace the absolute interpreter path.
The marker is `PASS_FULL_SIGNED_TERNARY_THREE optimum=60 source=8 readouts=52`.
The verifier writes no files and prints a generated receipt bound to SHA256
hashes of all five package files. It imports no predecessor implementation.
There are no live external inputs; source pins are historical provenance.

The exact formal interpreter checks arbitrary connector dirt and every
`A_v B_j x_j` coefficient for both words. An independent subset check visits
all 247 subsets of the cube with at most six vertices and checks the
antipodal bound. It supplements the proof; it is not an enumeration of all
legal words. Twenty-four dense integer cases at widths 2, 3, and 4 check the
complete action on arbitrary initial sources, connector and outputs, with
singular maps, noncommuting examples and inverse round trips. All 60 single
omissions, all 60 sign flips and five invalid-event controls are rejected.
These are two arithmetic representations within one contribution, not
independent human review.

The bounded verifier has no recursion, subprocesses, network calls or writes.
Functions fit within 60 physical lines. Explicit exceptions remain active
under optimized Python. Each word has at most 160 events, formal states have
four connector coefficients and 26 four-coefficient outputs, and dense states
have 30 arrays of width at most four. The subset check has exactly 256 masks
before its size filter. Python-managed allocation is a Power of Ten rule 3
deviation, bounded by these fixed domains and the 60-second command limit.
Reconsider fixed-capacity storage if the checker becomes an online component.
Warnings-as-errors execution is the applicable diagnostic check; no separate
project type checker is configured for this standalone verifier.

## Scope, overlap and family decision

Base `ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c`, priority revision 7.
[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19145564).
This changes the connector-alphabet-change card to a larger signed demand
family in the existing alphabet. It is a combinatorial interface side result.
The card's 945-pairing control and the selected-source metadata baseline
passed as orientation, not as new scientific results.

Live PRs, this account's recent work, active Discussions, handoffs, local
reservations, all-main README searches and merged-PR searches were checked.
The cached helper covered 314 open PRs and 4,389 Discussion records, with
incomplete sparse local-note coverage. These checks do not cover unpublished
work or prove novelty. The relevant comparison is Richardson's three-output
signed characteristic-zero model. Prime-field two-source full coefficient
demand and duplicated canonical obstructions have different domains.

The call optimum is proved, and a literal word is supplied. A concrete
recursive consumer, preparation, routing, frames, physical hosting, scalar
instruction cost, stock, precision, tape and supplier admission remain
unknown. Unknown costs are not zero. For actual positive complete event
prices the same source word has the constructive bill

```text
2(c_+B0+c_-B0) + (c_+B1+c_-B1) + (c_+B2+c_-B2)
  + sum_(v!=0) (c_+Av+c_-Av),
```

plus setup, storage and dispatch not already included in those event prices.
No optimality for unequal prices is asserted. No physical caller, selected
cold replay, formal build or complete multiplication theorem is supplied.
The family decision is to retain this exact small result and stop expansion.

## Open next questions

1. What is the exact all-word optimum for all 80 nonzero ternary rows on
   four immutable sources? Start with the reflected four-cube cycle and
   distinguish minimum source paths from cheaper words buying extra reads.
   The present six-call cube argument does not settle that domain.
2. Can unequal complete source/readout prices make a six-source-call path
   preferable to the 60-call word? Begin with one named price vector and
   charge every extra readout. The unit-price theorem does not answer it.
3. Does an actual supplier expose this demand? Pin its maps and ports before
   construction work, then price preparation, routing and full restoration.
   No such consumer is identified here.

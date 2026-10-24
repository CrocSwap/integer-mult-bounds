# Gaussian public headers with localized sources pay a strict surcharge

**Scoped proof with exact finite corroboration.** In the Gaussian nonlinear
message model of ywz65's [PR2641](https://github.com/CrocSwap/integer-mult-bounds/pull/2641),
allow the public routing header M to depend only on inputs at a declared
nonempty source set A. Charge each header bit its actual declared source-span
rank r, rather than the predecessor's full-space price four. Then

```text
E[C] >= (2/3) B + r L - lambda(A) H(M)
     >= (2/3) B + L/3,
```

where B is total independent uniform demand, L is expected header length,
and lambda(A) is the total weight of the retained nonorthogonal cliques
meeting A. For equal b-bit demands this is `40b + L/3`. Localizing the header
source can reduce the predecessor's `2L/3` guaranteed surcharge, but cannot
eliminate a positive surcharge under this public-observation contract.

This answers the **localized-source, public-reader** part of PR2641's Open next
question. It leaves private readers open. The new step is to retain the header's
source support in every conditional entropy term, then use the credited flat
census to obtain a uniform positive gap. Geometry, clique weights, transcript
injectivity and prefix-coding entropy are cited predecessor results. No
predecessor verifier or census is replayed here.

## Model and cited premises

There are 60 Gaussian E8 lines. Port t has an independent uniform b_t-bit
input X_t, and receiver t must recover it exactly on every input. Its free side
information consists only of orthogonal ports. Source and receiver roles are
distinct. The header is a deterministic function `M=h(X_A)` with a finite
prefix-free code. All receivers and payload encoders receive it. Its price
per bit is `c(All,A)=r`, the Gaussian rank of the span of A.

Conditional on M, payload count, order, source/reader supports and prefix-free
codebooks are fixed. Payload encoders use M and their declared original source
inputs, without relays. Arbitrary nonlinear encoding and decoding are allowed.
A payload bit costs its source/reader pairing rank, additively. Encoding,
decoding and source access remain free in this abstract relaxation.

Sagar Thakrar's [PR738](https://github.com/CrocSwap/integer-mult-bounds/pull/738)
supplies 640 nonorthogonal cliques, each of weight 1/192, with incidence 128
at every line, and the support inequality

```text
sum_Q [Q meets R and S]/192 <= c(R,S).
```

Its unchanged [certificate](../gaussian-clique-copy-bound/certificate.json)
also supplies the root-generated flat census used below. These are mathematical
premises of this extension; source hashes authenticate retained bytes, not
independent acceptance of their geometry. PR2641 supplies the conditional
transcript argument and paid prefix-code model.

## Proof

Fix a clique Q and the inputs outside Q. Let Z_Q be the tuple of payloads
whose source and reader sets both meet Q. The pair `(M,Z_Q)` determines X_Q:
other payloads received by Q have sources outside Q and are determined by M
and the fixed outside inputs; all permitted side information is outside Q.
Exact recovery therefore gives the inherited entropy inequality

```text
sum_(t in Q) b_t
  <= H(M | X_outside_Q)
     + E[sum_j length(Y_j) [Q meets R_j(M) and S_j(M)]].
```

If Q does not meet A, its outside inputs determine the header, so the first
term is zero. Otherwise it is at most H(M). Multiply by 1/192 and sum over Q.
The 128 incidences at every port and the cited support inequality imply

```text
(2/3) B <= lambda(A) H(M) + E[payload charge].
```

Adding the actual header price rL proves the first displayed bound. No
conditional independence after observing M was assumed. Kraft's inequality
and the entropy bound for prefix codes give `H(M)<=L`.

Let F be the Gaussian span closure of A among the 60 lines. Then
`lambda(A)<=lambda(F)` and `rank(F)=r`. The following table transforms the
**inherited** flat census; it does not claim new flat enumeration.

| r | Lines in F | lambda(F) | r-lambda(F) |
|---:|---:|---:|---:|
| 1 | 1 | 2/3 | 1/3 |
| 2 | 2 | 4/3 | 2/3 |
| 2 | 3 | 77/48 | 19/48 |
| 2 | 6 | 5/3 | 1/3 |
| 3 | 4 | 109/48 | 35/48 |
| 3 | 6 | 41/16 | 7/16 |
| 3 | 15 | 8/3 | 1/3 |
| 4 | 60 | 10/3 | 2/3 |

Every nonempty source set consequently has `r-lambda(A)>=1/3`. Thus
`rL-lambda(A)H(M)>=(r-lambda(A))L>=L/3`, proving the theorem for every finite
block width and every finite prefix-coded payload list. When r=4 the stronger
`2L/3` bound survives even if A is a proper spanning subset. A positive-length
constant header has H(M)=0 and pays its full rL.

The support-sensitive entropy estimate is exact as an information-loss bound.
Take one independent bit at every port of any nonempty A and let M be their
parity. Conditional on outside-Q inputs, this parity has entropy one precisely
when Q meets A. Therefore the total conditional header entropy is exactly
lambda(A), while `H(M)=L=1`. Singleton, six-line rank-two and fifteen-line
rank-three flats attain the geometric gap 1/3. **This does not establish an
attaining complete communication code at charge `(2/3)B+L/3`.** The Gaussian
nonlinear optimum itself remains open.

## Exact corroboration and reproduction

From the repository root, using the available CPython 3.12 interpreter:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -B research/gaussian-localized-header-tax/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/gaussian-localized-header-tax
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/gaussian-localized-header-tax --check-source-history
```

The registered replay runs both ordinary and optimized Python. The verifier
reads cited data, transforms its eight flat types, and performs new bounded
information checks:

- All 65,536 Boolean headers on four independent bits at orthogonal lines.
  Each clique meets at most one of those lines. Conditional header entropy
  at a singleton cut equals its Boolean edge influence. The support-sensitive
  entropy bound is checked using integer powers; no floating logarithm decides
  an inequality. The 32 equality cases are exactly the affine headers.
- All 63 nonempty cuts of a six-input parity, with 4,032 input/cut pairs,
  confirming the exact support-loss witness.
- Three literal public-observation protocols on the credited six-line rank-two
  flat with source indices `(0,1,2,11,12,45)`: parity header, nonlinear header
  `x0 XOR (x1 AND x2)`, and variable header code `{0,10,11}`. All 64 inputs and
  six receiver demands are checked for each protocol. Header-dependent payload
  orders and counts are included. Their expected charges are 7, 7 and 8;
  these corroborate correctness and pricing, not optimality.
- Eight rejection controls: an invalid surcharge table, three invalid prefix
  codes, three missing-payload protocols and an undeclared header source.

`RESULT.json` is generated by `verify.py --output NEW_PATH` and binds every
package source file and live predecessor input by SHA256. Default replay
regenerates and compares the entire result. Exclusive output refuses an
existing path. The all-width theorem is the written proof, not an extrapolation
from these finite examples or a proof-kernel result.

## Scope and implementation limits

The result bounds expected and hence worst-case charge, not each execution.
All receivers see the paid header; private schedule knowledge, interactive
relays, correlated or restricted demands, errors, non-prefix termination,
cheaper physical sharing and changed stage accounting are excluded. The
nonempty declared-source premise excludes a free empty-source constant header.
No physical supplier, helper-restoration implementation, native caller,
precision/tape bound, improved kappa or complete multiplication theorem follows.
The selected frontier is unchanged.

The verifier is a finite standard-library calculation. Its scientific loops have fixed
bounds: 65,536 headers, four variables with eight edges each, 64 inputs, 63 cuts,
three protocols and eight cited flat types. The source manifest has four entries;
five fixed package source files are hashed. Each file read is capped at 256 KiB.
No recursion, dynamic code or network is used. The verifier authenticates before
reading live data and does not execute predecessor code. Warning-strict normal
and optimized replay are the recurring Python diagnostics; no unavailable
static analyzer is claimed.

Power of Ten deviations are confined to this verifier:

- Rule 3, managed allocation: Python allocates integers, JSON and dictionaries
  during execution. Reads are capped; the header loop is 65,536 iterations;
  each receiver map has at most 64 entries and each cut has at most 64 fibers.
  The equality list has capacity at most 65,536 identifiers. Normal/optimized
  full replay verifies the finite bounds' path. Resources are process-local and
  files use context managers. Follow-up: if the domain grows, retain explicit
  input/collection caps and measure peak allocation before enlarging the limit.
- Rule 9, indirect calls: the rejection helper invokes only four fixed local
  targets (table, prefix, protocol and source-support checks). This is confined
  to eight deliberate fault controls and exposes each failure. Normal/optimized
  replay exercises them. Follow-up: replace this helper with explicit cases if
  external callbacks or stateful targets are ever introduced.

## Open next questions

1. Can localized **private-reader** headers preserve a useful transcript
   bound? This changes who knows the payload schedule. Start with one rank-one
   header and specify every recipient's observation and routing information.
   The blocker is avoiding uncharged schedule leakage to other receivers.
2. Does a chronological sequence of public headers with source supports chosen
   by earlier headers retain the `L_total/3` surcharge? Start with two rounds
   and condition the support-sensitive entropy argument on the first paid
   header. Branch-dependent source ranks and stopping information need an
   explicit contract. No multi-header theorem is claimed here.

## Provenance and credit

Base `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7. TASK.json
records the changed card scope. SOURCES.json pins the unchanged geometric
certificate and predecessor proof as live inputs and the task/selected context
as historical provenance. The claim is [here](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19134282).

This contribution is **produced by Nick Petalas**. Credit ywz65 / PR2641 for
the public-header argument and open localized-header question; Sagar Thakrar /
PR738 for the Gaussian geometry, clique weights, flat census and support bound;
ToikY / PR888, Alexander Templeton / PR785, Michael Fischler / PR814 and Jerry
Chen / PR912 for the nonlinear transcript and paid-header lineage, retaining
Joel Pulikkan, Douglas Colkitt and DreamingOfClouds's prior credit. Entropy,
Kraft's inequality and Boolean influence are standard methods. Independent
human and formal proof-kernel review are unclaimed. Apache-2.0.

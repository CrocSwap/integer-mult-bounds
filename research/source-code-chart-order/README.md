# Swapping source-code charts destroys periodic restoration

Scoped source-algebra obstruction. No new supplier or kappa is claimed.

Ali Romman's [PR1862](https://github.com/CrocSwap/integer-mult-bounds/pull/1862)
constructs a valid order-six source code. It explicitly leaves changing-chart
restoration open. On the actual selected 112-port query matrix, alternating its
compensation and query port sets gives an **infinite-order** product. The product
has a real eigenvalue strictly between 170 and 171. Repeating this pair cannot
restore every source, even after arbitrarily many repetitions.

This is a concrete, quantitative witness, not a correction to PR1862. David
Arias's [PR1973](https://github.com/CrocSwap/integer-mult-bounds/pull/1973)
uses these same two admissible charts to check a different statement, the
three-chart F-B-F exchange defect. Its all-length winding theorem concerns a
fixed code. This package instead derives the repeated source-only pair's
characteristic polynomial and growth. It imports neither predecessor's code.

## Exact instance and result

The selected source has an 8 by 112 query matrix R, with

```text
K = R^T/4,   RK = 14 I_8,
A = [0,7,20,27,36,46,57,111],
T = [21,37,47,76,81,87,92,110].
```

Let P and S be K restricted to its A and T rows respectively. Let L_A and L_T
be R restricted to those columns. Both eight-port minors are orthogonal with
squared norm four. Thus

```text
RP = RS = L_A P = L_T S = L_A K = L_T K = I_8,
L_A S = L_T P = 0.
```

PR1862's ordered code for a compensation section P and logger L is

```text
Z = K - P(RK-I),   Q = R-L,
G(P,L) = (I-PL)(I+ZQ) = I+ZQ-PR.
```

Set G_A = G(P,L_T), G_T = G(S,L_A), and C = G_T G_A. Products act on
column vectors, so G_A executes first. Both charts meet exactly the predecessor's
algebraic hypotheses RP=I, LK=I and LP=0.

The checked full characteristic polynomial is

```text
char_C(t) = (t-1)^88 (t^3-171t^2+27t-1)^8.
```

In particular, trace C is 1456. Each individual code has exact order six,
whereas C has infinite order over Q and Q(i). The same-chart pair G_A G_A has
order three and provides a positive restoration control.

## Proof by three sections

Put U = K-P-S. The three sections satisfy

```text
L_A U = L_T U = 0,   RU = 12 I_8.
```

The 112 by 24 matrix E = [P S U] therefore has the left inverse

```text
D = stack(L_A, L_T, (R-L_A-L_T)/12),   DE = I_24.
```

Every source splits uniquely into a vector in ker D and a vector E(u,v,z).
The complement has dimension 88. Both codes fix it pointwise because each of
R, L_A and L_T vanishes there. On the section coordinates, the two codes act
by the following matrices tensored with I_8:

```text
H_A = [[-12,  -1,  -156],
       [  1,   1,    12],
       [  1,   0,    13]],

H_T = [[  1,   1,    12],
       [ -1, -12,  -156],
       [  0,   1,    13]].
```

For example, G_A P = -12P+S+U, G_A S = -P+S, and
G_A U = -156P+12S+13U. These follow directly from the ordered code formula.
Swapping P and S gives H_T. Their product is

```text
H_T H_A = [[   1,   0,    12],
           [-156, -11, -2016],
           [  14,   1,   181]].
```

Its trace is 171, sum of principal two by two minors is 27, and determinant
is one. Its characteristic polynomial is p(t)=t^3-171t^2+27t-1. The direct-sum
decomposition proves the displayed full characteristic polynomial and
trace C = 88+8*171 = 1456.

The integer signs p(170)=-24311 and p(171)=4616 put a real eigenvalue lambda
strictly between 170 and 171 by continuity. A finite-order matrix has only
roots of unity as eigenvalues, so C cannot have finite order. For any induced
real operator norm, ||C^k|| is at least lambda^k, hence greater than 170^k for
positive k. This describes worst-case growth in the source-only port algebra.
It is not a physical precision bill or a claim that every rational source
vector expands at this rate.

There is also a short order obstruction independent of the cubic calculation.
For a finite-order 112-dimensional matrix in characteristic zero, each
eigenvalue has modulus one, so the absolute value of its trace is at most 112.
The measured exact trace 1456 already excludes finite order.

## Reproduce and evidence

From the repository root, Python 3.10 or later, standard library only:

```sh
python3 -I -B research/source-code-chart-order/verify.py
python3 -I -O -B research/source-code-chart-order/verify.py
python3 -I -B research/source-code-chart-order/test_verify.py
python3 scripts/research_package.py --package research/source-code-chart-order --check-only
```

Expected verifier line:

```text
PASS_SOURCE_CODE_CHART_ORDER orders=6,6,infinite trace=1456 eigenvalue=170..171 columns=336 controls=4 no_new_kappa
```

Standard and optimized registered replays pass, including the source pins,
336 column comparisons, four semantic controls and eight focused tests.
All 45 research-workflow tests pass with no skips; bytecode compilation with
`-Wall` also passes. Exact commands and unrun obligations are in TASK.json.

The registered hook uses Python 3.12:

```sh
python3.12 scripts/research_package.py --package research/source-code-chart-order
```

The verifier authenticates the selected PR1094 archive and two exact members
before parsing. It propagates all 112 source columns to the forward centre
cut. It does not replay helper or private-input columns. It independently
constructs the two 112 by 112 codes, proves DE=I, checks both section actions
and the fixed complement, and compares the matrix calculations with a
separate ordered-factor column interpreter in 336 cases. All checks remain
active under `-O`.

Four semantic controls detect a broken minor, overlapping compensation/logger
supports, a changed section basis and a wrong active coefficient. The focused
tests also reject an archive mutation and a forged receipt, and exercise CLI
failure behavior. `RESULT.json` records the deterministic result. Default
replay is read-only; `--write` regenerates only this package's receipt.

[SOURCES.json](SOURCES.json) records Git blobs and hashes at main
`d48fcf5eedae9d8e2296598a1868a0b1a37a83f1`.
[ARCHIVE.json](ARCHIVE.json) additionally pins raw members and decompressed
payloads. These payloads equal PR1862's historical PR1042 inputs. The query
matrix digest also equals PR1973's independently extracted digest.
The archive, selected record, frozen predecessors and `upstream/` are unchanged.

## Scope and task selection

Chooser seed `4a0e6caaf3f4e5d0026f7998e13a6835` proposed
`complex-new-helper-inventory` under priority revision 3. The scope changed
to a restoration audit of a proposed source-code interface. It does not meet
the original card's new-inventory construction gate. The binding complex
supplier motivates the question, but this is a scoped obstruction, not an
exponent improvement.

The card's ceiling positive control and ideal levers were run. Centre-free
work has a favorable 2.80-times ceiling before the source coding, chart
routing, restoration and other costs of realizing it. This audit rejects only
periodic restoration by repetitions of the specific pair C. It supplies no
candidate invoice and credits no omitted work as a realized saving.

[The coordination claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1976)
records the scope and overlap checks. A fully paginated refresh covered
404 open PRs and 625 Discussion records without warnings. Coverage timestamps
and pinned predecessor heads are in TASK.json. This is not a code-diff-wide
search or a global novelty certificate.

No physical route between these charts is constructed. Abstract admissibility
does not establish legal native-frame reads or equivalence to a stage in the
nine-call controller. In particular, the result does not rule out coherent
conjugate transport, explicit inverse codes, different chart sequences,
port-dependent repairs, changed endpoints or PR1969's joint-query interface.
The inherited all-size, native/compiler, hosting, precision/tape and analytic
obligations remain open. No full `make frontier1094-verify`, native recipe
replay, controller admission or proof-assistant verification is claimed.

## Open next questions

Can an actual paid stage transport replace this raw swapped-chart product
with a restoring source transition? First derive one transport U from the
controller and check the full-source map G_T^-1 U G_A, not only its query
compression. Then price all reads, frame moves, inverse work and endpoint
restoration. The missing typed native transport and complete invoice block
any supplier conclusion. The structured question is in TASK.json.

## Verification design and credit

Power-of-ten inspection found no recursion in the new checker. Every algebra
loop is bounded by the pinned 112-port/8-query dimensions. The source loop is
capped at 30,000 events, files at 8 MiB, and archive member count at 2,000.
Functions are below 60 physical lines; failures propagate as exceptions with
no writes on ordinary replay. Python's rational/dictionary allocation and
unittest's bounded method dispatch are deviations from rules 3 and 9. Pinned
source and matrix sizes bound live state. Tests own and discard their temporary
directories, and subprocesses have 30-second timeouts. If these scripts become
runtime components, replace them with fixed-capacity storage and direct calls.
`-Wall`, bytecode compilation and standard/optimized replays check the
interpreted code; no static type analysis is claimed.

Credit Ali Romman for PR1862's source-code construction and its explicit
changing-chart warning, inspected at
`bb29ea73ad9be9a0c3d53cdcb1d22b2ee9ffe42f`. Credit David Arias for PR1973's
fixed-code winding and universal F-B-F obstruction, inspected at
`165f08a694b26b0f4c521ce5e1132ede0b7362a2`. Those are valid predecessor
results, not claims introduced here.

The selected local source and assembly retain Jeremy Kothe's PR1042 and
mutable-leaver work, Rohan Arun's PR1094 and k8/slot work, Hao Yan's controller,
Chafik Boukhalfa's frame work, icekylinx and the earlier gauge44/split-centres
contributors. Original notices remain in the unchanged archive and source
packages. No predecessor executable or text is vendored. Nick Petalas.
New work is Apache-2.0 under the repository license.

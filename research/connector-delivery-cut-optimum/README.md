# Exact connector cost when each output has a delivery cut

Carrying one dirty connector between sequential output requests saves real
restoration work, but cannot inherit an offline universal schedule's bill.
For arbitrary binary masks M_i and positive complete-query prices, the exact
cost in the stated alphabet is

    2 sum_(active i) c_Ai + sum_j c_Bj (n_j + (n_j mod 2)),
    n_j = number of requested masks containing source j.

For the 31 nonzero five-source masks this is **142 unit queries**, compared
with **222** separately restored row stars and **74** in the predecessor's
offline model. Both savings and the additional delivery-cut obstruction are
proved for the full query alphabet, not merely for paired-readout candidates.

## Contract

Retain the exact F2-linear dirty connector model of Ross Richardson's
[universal connector boundary](../universal-connector-boundary/README.md).
Sources x_j are read-only; A_i,B_j may be noncommuting or singular; source,
output and connector rows are distinct and arbitrarily dirty. Allowed calls
are B_j: z+=B_j x_j and A_i: y_i+=A_i z. Every complete child restores its
private scratch and heads. Other operations and free copies are excluded.

Add a chronological condition: output i cannot be written before request i,
must have its final requested value when it is delivered, and cannot be written
afterward. Request i+1 begins after delivery i. The connector can remain open
between deliveries but must restore to its initial value at the end. Neither
knowing all requests in advance nor using extra A calls relaxes these cuts.
Zero masks require no A calls. Different requests have distinct output rows.

An open boundary is typed by q in F2^n with
z=z_initial+sum_j q_j B_j x_j; the closed type is q=0. The caller reserves z
until the final close. Prices are fixed positive complete costs at the actual
ports, including frame/routing admission, restoration and per-call dispatch.
Changing prices or admitting different data operations changes the theorem.

## Exact lower bound and attaining word

Specialize to scalar identity operators with independent source and connector
bits. Each nonzero output requires at least two A_i calls: the connector's
initial dirt forces an even number, and zero calls cannot change that output.

If mask i contains source j but no B_j call occurs during request i's interval,
the coefficient of that source in z is constant throughout the interval.
Its total contribution through an even number of A_i readouts is then zero.
Hence each demand for j forces at least one B_j inside its own disjoint
interval. There are n_j such demands. Global restoration independently forces
the B_j count to be even, so it is at least n_j+(n_j mod2). This reasoning
allows arbitrarily many readouts and toggles and proves the weighted bound.

Attain it by reading A_i, toggling each B_j in M_i once, then reading A_i again
and delivering output i. The two reads cancel the current connector dirt and
all previously carried source contributions, leaving exactly the desired mask.
Update q by XOR with M_i. After the last delivery, toggle every j with q_j=1
once. The terminal charge is exactly one call for every odd n_j. This proves
the formula for arbitrary sizes and maps by linearity and also supplies an
online implementation using n parity bits. Reversing the complete query word
inverts its final map; inverse execution has its own reversed delivery policy.

If the connector must instead close at every delivery, the same parity
argument applies in each interval, giving exactly 2 sum_j n_j c_Bj plus the
same A bill. Thus persistence removes sum_j c_Bj(n_j-(n_j mod2)) complete B
calls. This is an actual typed boundary saving, not a matrix reformulation
of an unchanged scalar recurrence.

## Complete budget and limits

Add input admission, coefficient preparation, request/mask reads, parity-bit
storage, output scheduling and instruction dispatch to the query formula.
Reading each explicit n-bit request costs at least its actual scan; the n-bit
parity record and one reserved full connector are not free. A fixed-port
complete c_B or c_A must include recursive expansion and every inverse leaf.
No rank charge is divided by the number of requests. Additional physical
frames or owners must be paid before applying this cost to a supplier.

The 142-query example has 80 B calls (each of five sources appears16 times),
62 A calls and no final B cleanup. The row-star baseline has160 B and62 A.
The retained 74-query offline word realizes the same final map, but writes
future outputs before their requests; it is a positive endpoint control and
a negative delivery-contract control. The theorem does not contradict its
optimality under the predecessor's different observation contract.

This is an abstract interface optimum and a finite universal-mask application.
No selected owner call sequence, contracting supplier recurrence, new kappa,
native tape trace or full multiplication theorem is established.

## Independent evidence

The constructor uses the explicit typed q transition. A separate Dijkstra
engine explores the complete finite state quotient consisting of request
index, connector source mask, current output source mask and dirty parity.
It allows any number of A/B calls and zero-cost legal delivery. All binary
request sequences through lengths5,4,2 for source counts1,2,3, respectively,
are tested under two nonuniform price vectors, including zero requests.
Its optima equal the formula and each generated word's exact invoice.

The full five-source word is replayed on independent formal source/dirt columns
at every delivery. Four failure controls address premature delivery, writes
before request, writes after delivery and omitted terminal restoration.
The unchanged predecessor74-query word passes the endpoint-only check.
These independent finite quotients support, but do not replace, the proof.

```sh
python -O -B research/connector-delivery-cut-optimum/verify.py
python scripts/research_package.py --package research/connector-delivery-cut-optimum
```

Python3.12+ standard library only. See [EXPECTED.json](EXPECTED.json) for exact
counts/word and [SOURCES.json](SOURCES.json) for base, Git blobs and SHA256.
The prior40-round scopes and shared863-PR/112-discussion snapshot were searched;
the sole chronological-cut match concerned unrelated physical phase charts.
Cached offline coverage may miss updates and is not a proof of novelty.

## Open next questions

Which actual recursive caller requires individual output delivery while
allowing its connector to stay reserved? Extract one caller's exact cuts,
prices and hosting conditions, then compare the formula with its current
closed-call invoice. Physical realization and a favorable fully charged
budget are the blockers to a selected-supplier application.

## Credit

woklerx with substantial OpenAI Codex assistance; Apache-2.0. Ross Richardson's
PR934 and universal connector package supply the dirty-query/prefix model,
the offline74-query comparator and predecessor attribution to dirty-product
commutators and fanout. No predecessor executable is imported. No independent
human review is claimed; all selected community contributions are unchanged.

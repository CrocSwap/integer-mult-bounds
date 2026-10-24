# Independent review of the direct centre-support bound

The actual support geometry and its restricted lower bound pass this
review. The source pins are in `CHECKS.json`. This check does not import
the root checker or use its basis calculation.

Explicit XOR closure gives dimension seven for each of the eight source
supports. An independent elimination of the orthogonality equations
gives each two-dimensional annihilator. There are four equal-space
classes, with vertex pairs (0,5), (1,6), (2,7), and (3,4). Distinct
classes meet in dimension six. All source spaces meet in dimension five.
Their span is the dimension-eight hyperplane perpendicular to 45.

The actual shared-port graph is K_(2,2,2,2). Each edge has two physical
ports. Each of the 48 ports belongs to two centres. An independent set
has at most two vertices, and the four maximum sets are the four parts.

Assume each original source value has one unwarped carrier on a monotone
subspace chain. Assume each full row is captured once at one common
frame, with no partial query, source code, or extra carrier. A capture
frame for row v must contain its dimension-seven support U_v. If the
frame has dimension seven, it is U_v. One shared carrier cannot visit
two distinct U_v spaces on a monotone chain, since neither contains the
other. Thus at most two of the eight direct captures have dimension
seven. The others have dimension at least eight. The sum is at least 62.

This is a bound on the common frames of direct captures under the stated
carrier model. It is not a bound on all native query words, all source
encodings, or the required computation. In particular, the new pair code
spreads each original value between two independent coded values. It
violates the one-unwarped-carrier premise. Its eight dimension-seven
captures therefore do not contradict this theorem.

No material finding was found. The certificate agrees with the separate
space and graph calculations.

Run from the workspace root:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/centre-support-review-20261018/check_support.py
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/centre-support-review-20261018/check_support.py
```

The final output is `PASS_INDEPENDENT_CENTRE_SUPPORT_GEOMETRY`.
This independent review was produced with AI assistance.

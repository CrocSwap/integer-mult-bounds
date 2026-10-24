# Independent review of the unit current-query encoder

The separate unit-T component passes. It maps arbitrary logical inputs
`(l,v)` to `(l,T(l+v))`, and its selected output stores `R(l+v)` without
an odd division. It restores all 480 borrowed helper contents and clears
the eight owned private fields. Its cost is 212,826 real scalar
primitives. The native mass is 5,530, including eight new rank-one children.

`UNIT-REVIEW.json` pins the separate producer inputs and the earlier
independent PJ review. The checker imports only that pinned independent
interpreter. It does not import or run either producer.

Let `L=R_A pi_A`, `K_A=iota_A R_A^-1`, `R_U=R-L`, and `K_U=K-K_A`.
The actual selected minor gives `L K_A=I`. Both operators `K_A R_U`
and `K_U L` have square zero. Thus

    T=(I-K_U L)(I+K_A R_U),
    T^-1=(I-K_A R_U)(I+K_U L)

are inverses over the dyadic coefficient ring. Expansion gives

    T-J=K_A(2R-L),       L T=R.

The first identity has only A output rows. It permits the same eight
positive-line normalization steps as the PJ word. No native operation
is needed on the other 104 target rows. The checker rebuilds the actual
matrices from R, checks both inverse orders, and verifies all 424 signed
unit coefficients of the final correction.

The independent interpreter replays every event of the 26,531-event
word on all 712 formal input columns. It checks every scalar frame and
every retained native frame change. Reversing the two prefix factors,
omitting the second factor, or omitting the suffix changes the map; all
three controls reject. The complete costs are 3,648 per prefix factor,
202,138 for the old core, and 3,392 for the suffix.

The old core, eight line recipes, and final frame ledger are byte-equal
to the independently reviewed PJ packet. The 4,096 spatial native
columns and 72 full exterior phase cases from that review therefore
apply without a new phase assumption. Selected Y is FULL; ordinary Y
is `F C_q^-1`. The relative old-baseline code is `C_A T`, not `T`.
The dyadic inverse alone does not make a mixed-frame inverse free.

Run:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/coherent-port/current-query-review-20261015/review_unit.py
```

Expected output:

```text
PASS_UNIT_QUERY_REVIEW: all 712 columns, both inverse orders, and 212826 scalar
```

The review accepts this local word. It does not admit its new children
to owner intervals, remove the next-call selected phase, or establish a
complete controller, precision bound, supplier, or kappa improvement.
The original PJ review and all producer bytes remain unchanged.

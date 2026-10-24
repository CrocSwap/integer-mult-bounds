# The native prefix and the fixed-reader dispatcher

This packet joins the emitted carrier prefix to the fixed past-reader
query. It gives the exact data interface at the D25 stages 1 and 2.
It preserves the native helper contract as an explicit premise.
It does not give a complete supplier or a multiplication exponent.

The inputs are the frozen `CARRIER-PREFIX.json.gz`,
`REUSE-PROGRAM.json`, `ROUTED-QUERY.json.gz`, and
`DIMENSION25-VIEWS.json`. The dispatcher records their paths and hashes.
It does not change those files.

## The physical level and the reader label

Let P be the fixed sixteen selected ports. Let R be the other 96 ports.
Let \(F_\ell\) be the full transform on the first \(9+8\ell\) axes.
Put

\[
G_R=\operatorname{diag}(I_P,q_R).
\]

Here q is the portwise inverse intrinsic line. Fix a reader stage s
and a service stage t, with \(s<t\). The physical input must have
completed level \(t-1\), even when \(s<t-1\). For example, the pair
\((s,t)=(0,2)\) uses a reader from stage 0 that has already been carried
to level 1. It is not a direct physical jump from level 0 to level 2.

The selected records can be arbitrary independent values. Write w for
the complete bank of selected records and ordinary values. The exact
global input is

\[
(F_{t-1}x,\ F_{t-1}G_Rw).
\tag{1}
\]

If \(w=C_sy\), then its selected entries are \(L_sy\), and its other
entries are \(y_R\). The unit row code makes this interpretation valid
for every w.

## The current native prefix

The current DATA entry views take (1) to a common exterior frame,
with local input types

\[
X=Qx_{\rm body},\qquad
Y_P=Q_Pw_{P,\rm body},\qquad
Y_R=w_{R,\rm body}.
\tag{2}
\]

For each field, the body owner d reads the global owner
\(h=d\rho_{t,p}\). The map is a bijection on the regular \(O(25,2)\)
cover. The program retains both the literal route and the entry
translation. It checks the full Z4 phase equation. In particular,
the selected target input in (2) is a positive intrinsic line,
not an I frame.

The pinned prefix then executes 2,406 events. The first 2,390 events
are the retained core. The last sixteen events carry the selected
records from their intrinsic line to FULL with H8 calls. There is
no selected query in this prefix.

The exact local output is

\[
X'=F_9x_{\rm body},\quad
Y'_P=F_9w_{P,\rm body},\quad
Y'_R=F_9q_R
   \bigl(w_{\rm body}+E x_{\rm body}\bigr)_R.
\tag{3}
\]

All 112 source fields and all 416 helper fields retain their contents.
This statement holds for arbitrary values in those fields. The
checker replays all 640 input columns and the full frame ledger.
The native phase recipes and the local endpoint adapters are bound
to the pinned independent line-entry review.

There are 128 local input adapters: 112 source adapters and sixteen
copies on the selected target fields. There are 96 ordinary target
output adapters. There is no output adapter on a selected target.

After the ordinary output adapters, use the current DATA exit views.
For selected targets, use the FULL exit translation, the same
translation used for X. The actual source records also have equal
X and Y exit translations, but the required FULL phase equation is
checked directly.

Let \(E_t\) include the current owner routes. After the complete
native cover sweep, (3) becomes

\[
X'=F_tx,\quad
Y'_P=F_tw_P,\quad
Y'_R=F_tq_R(w+E_tx)_R.
\tag{4}
\]

The checker verifies all 448 data entry phase equations and all 448
data exit phase equations for stages 1 and 2. These checks include
the common exterior factors.

## The query after the cover barrier

Finish the native prefix and its DATA exits for the complete cover
before the late query. At this cut, every X field and every selected
Y field has the global FULL frame \(F_t\). The ordinary Y fields
remain in their hole frames and are not read by the query.

Use the six-step word in `REUSE-PROGRAM.json` for the selected pair
\((s,t)\), with its literal map and scalar expansion in
`ROUTED-QUERY.json.gz`. It adds \(L_sE_tx\) to the sixteen selected records. It
restores every X field. The past reader, current code, complete
middle owner paths, and their translations remain in the exact order
given in that program.

Define \(A_{s,t}\) by

\[
(A_{s,t})_P=L_sE_t,\qquad
(A_{s,t})_R=(E_t)_R.
\]

Equations (1)--(4) and the late query give the complete data interface

\[
(F_{t-1}x,\ F_{t-1}G_Rw)
\longmapsto
(F_tx,\ F_tG_R(w+A_{s,t}x)).
\tag{5}
\]

If the input records represent \(L_sy\), the output records represent
\(L_s(y+E_tx)\). Thus the same past reader is carried through the new
service. No old-stage ordinary target read is used.

Equation (5) includes the actual stage routes. The two stage responses
are not replaced by a common scalar matrix. The reader label s does
not change any native entry frame.

## The schedule and the helper premise

Each dispatcher record has this order:

1. Apply the current DATA entry views.
2. Apply the local input adapters.
3. Execute the complete carrier prefix.
4. Apply the ordinary target output adapters.
5. Apply the current DATA exit views.
6. Complete the cover barrier.
7. Execute the fixed past-reader query at global FULL.

For each data field, the owner map \(d\mapsto d\rho_{t,p}\) is a
bijection. Thus two body invocations do not write the same data
record of that field. Complete body invocations can use the inherited
helper host and restore it before the next invocation. Moving the
query to the cover barrier needs no additional helper.

This packet does not construct a new helper host. The prefix retains
416 arbitrary helper fields and their typed input contract. A complete
supplier must still provide those fields through a valid host, and
must price any helper access and recursive parking that the host
requires. The data route bijection alone does not prove that contract.

The same-chronology inverse-adjoint in `DUAL.md` applies to (5).
Its central upper response is \(-A_{s,t}^*\), with the same unitary
input and output frames. It is not an inverse response unless a
separate identity proves that fact.

## The invoice

The prefix has

```text
1392 H1 + 64 H2 + 48 H3 + 16 H8
```

Its native rank is 1,792. It has 1,520 native children and 6,456 real
scalar primitives. The late query has no native child and has 11,168
real scalar primitives. The complete word therefore has 17,624 real
scalar primitives. The smaller 9,880 price belongs to the separate
same-reader local word and does not price this past-reader service.

The conservative monomial call bound is:

| Part | Calls |
| --- | ---: |
| DATA entry and exit | 448 |
| Local endpoint adapters | 224 |
| Native side maps | 3,040 |
| Fixed past-reader query | 2,064 |
| Total | 5,776 |

The native side-map bound allows two maps for each child. The bound
does not include helper acquisition, recursive parking, or an outer
caller. A map call is not a finite real-operation price. That price
and recursive precision remain separate obligations.

## Validation and scope

Run `check_integration.py --output <new-directory>` with normal Python
and with `python3 -O`. The two dispatcher files and the two receipts
must be byte equal. The checker rejects an existing output directory.

The checks bind both providers and the three pairs
\((0,1),(0,2),(1,2)\). They replay the carrier prefix, check every
adjacent data boundary phase, and bind the complete late-query
program. The pinned native integration lane replay covers the 2,064
literal query maps and its scalar word after this exact prefix.

This work extends the controller lane's normalized row capture, the
native lane's line-entry carrier, and the earlier D25 view proof.
OpenAI Codex assisted the work. No publication is authorized. Before
any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.

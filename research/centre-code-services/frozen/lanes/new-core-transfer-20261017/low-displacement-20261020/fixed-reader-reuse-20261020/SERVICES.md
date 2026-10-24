# Six complete data services that retain a past centre reader

This packet joins the exact native carrier prefix, the actual D25 DATA
dispatcher, and the literal global FULL query. It gives both native
providers for each pair \((s,t)=(0,1),(0,2),(1,2)\). It uses the inherited
416-field helper host contract. It does not construct or price that host.

Let \(F_\ell\) act on the first \(9+8\ell\) coordinates. Let \(P\) be the
sixteen fixed pivots and \(U\) their complement. Define
\(G=\operatorname{diag}(I_P,q_U)\). The complete data interface is

\[
(F_{t-1}x,\ F_{t-1}Gw)
\longmapsto
(F_tx,\ F_tG(w+A_{s,t}x)),
\]

where

\[
(A_{s,t})_P=L_sE_t,\qquad (A_{s,t})_U=(E_t)_U.
\]

The contents of w, including all selected records, are independent and
arbitrary. If \(w=C_sy\), then the selected output is
\(L_s(y+E_tx)\), while the ordinary output is \((y+E_tx)_U\).
Thus the service carries and updates the same reader from stage s.
It does not replace it by the current reader.

The physical input level is \(t-1\). In particular, pair \((0,2)\)
requires a stage-zero reader that has already reached physical level
one. It is not a direct jump from physical level zero to level two.

## Exact schedule and binding

The bundled service executes these blocks in order:

1. Apply the 224 current DATA entry views.
2. Apply the 128 local native input adapters.
3. Execute all 2406 native-prefix events over the complete cover.
4. Apply the 96 ordinary target output adapters.
5. Apply the 224 current DATA exit views.
6. Complete the cover barrier.
7. Execute the literal past-reader query at global FULL.

The selected target entry is an intrinsic positive line. The native
prefix carries it to FULL with an H8 child. Its ordinary targets retain
their hole paths. After the DATA exits, all source X fields and selected
Y fields are in global FULL. The late query can then read them through
the pinned past/current source maps. It does not read an ordinary Y
field.

`emit_service.py` checks all 896 DATA entry and exit phase equations for
the two service stages, including the common exterior, translation
order, intrinsic lines, and final hole or FULL type. It checks that the
current query views equal the actual DATA exit views. It then replays
all six complete content maps using those DATA route matrices.

The native programs and every literal query instruction are included in
one payload. The dispatcher, prefix, and query source pins remain in the
payload. The local native phase proofs are inherited by exact byte
identity from the independent line-entry review.

For each field the owner route is an orthogonal bijection on the regular
\(O(25,2)\) cover. Complete body calls restore their arbitrary helpers
before those helpers are reused. The complete cover sweep is required
before the query. The data route argument does not prove a new helper
allocation or recursive child host.

## Complete service invoice

Every service has native profile

\[
1392H_1+64H_2+48H_3+16H_8,
\]

with mass 1792 and 1520 children. Its scalar cost is
\(6456+11168=17624\). The explicit monomial call bound is:

| Part | Calls |
| --- | ---: |
| DATA entry and exit | 448 |
| Local endpoint adapters | 224 |
| Native side-map upper bound | 3040 |
| Past-reader query | 2064 |
| Total | 5776 |

The bound includes identity maps where the fixed instruction stock
retains them. No extra owned or private field is used. There is no odd
division. A map call still needs its finite implementation cost in a
complete supplier.

All 640 independent fields pass the local and ordered-owner content
replays. Every source and all 416 helpers are restored as specified.
The query formal coefficient bound is 448 with binary height two.
The native-prefix bound is 22 with binary height one. These bounds do
not replace the recursive precision proof.

Normal and optimized Python produce byte-identical service payloads and
receipts. Reproduce into new directories:

```sh
python3 emit_service.py --out replay-normal
python3 -O emit_service.py --out replay-optimized
```

The result closes the data-chart splice for this forward reuse family.
The inherited helper host, recursive parking, finite map costs, an
outer caller, and the complete supplier invoice remain explicit
obligations. No complete kappa improvement is claimed.

This result combines the bridge-access dispatcher and fixed-reader
theorem with the native carrier and literal query from this lane.
The controller supplied the normalized row code. AI agents prepared
the proof, implementation, and checks. Independent joined-service
review is recorded separately.

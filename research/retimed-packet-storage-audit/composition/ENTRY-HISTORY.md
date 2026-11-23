# Applicability to fresh and warm fixed-head reservations

This note clarifies the entry boundary of the frozen composition proof
`PROOF.md`, SHA256
`f40697245c65ade66b84d49f7ed64c5c13a598d962a71bb3e2881bd64f65f9fd`.
Its equations and retained premises are unchanged.

## Fresh source files and an inherited physical reserve differ

The actual source's `Arena` opens new temporary files. The composition proof
bounds the endpoints touched during one successful public call that **enters
a native ordinary stage**, allowing all prefix slabs, same-stage descendants,
earlier-stage calls and retired siblings within that call. Its `X` is the
maximum binary slab volume in that call; the source uses a common shape for
those slabs. In this fresh-entry interpretation there is no inherited
historical capacity on a newly opened role file.

A physical lowering that repeatedly reuses the same fixed heads may retain
earlier larger allocation extents even after every byte is zero. Returning
pages and packet markers to the empty baseline proves data/lifetime safety;
it does not reset a physical head's historical maximum. Applying the frozen
coefficient only to the latest, smaller call would therefore be unjustified
unless the previous capacity receives its own charge.

This is the established coordinatewise history principle from
[#5286](https://github.com/CrocSwap/integer-mult-bounds/pull/5286) and
[#5404](https://github.com/CrocSwap/integer-mult-bounds/pull/5404), applied at
the public-entry boundary of this source. It is an applicability condition,
not an additional premise discharge or a claim of a new accounting method.

## Exact entry-capacity formula

Fix the physical role universe for one installation. Let `K0_r` be the
historical allocated extent already charged on role `r` at public entry,
including blank retained backing. Let `h_r` be the highest endpoint that
this call reaches on that role, measured from the reused role origin.
The empty marker baseline and source return contracts ensure that new calls
reuse this origin, rather than appending to an old sibling's end.

In the historical-reserve model the exact update is

\[
 K'_r=\max(K0_r,h_r),\qquad
 H'=\sum_r\max(K0_r,h_r). \tag{11}
\]

Roles not touched by this call have `h_r=0` and retain their old capacity.
This includes any additional reserved roles outside the native-entry
coefficient. Erasure does not replace either maximum by `h_r` alone.

The composition proof supplies uniform coordinatewise constants `c_r`
under its explicit binary-capacity and transient-envelope premises, with
`h_r <= c_r X` and `sum_r c_r <= C`. For seven native stages one may use
`C=37764+2286A`, retaining the same definition of `A`. Thus a sufficient
warm-entry grant is

\[
 H'\le\sum_r\max(K0_r,c_rX)
       \le \sum_r K0_r+CX. \tag{12}
\]

The first expression keeps the useful componentwise maxima; the second is
a simpler conservative bill when only total entry capacity is known. The
per-role constants come from the named-role table, its geometric factors,
the actual stage-index pad factors, the public/root/cold-role coefficients
and the declared individual `a_r` values. Knowing only a scalar local
per-call total is insufficient to reconstruct those constants.

Alternatively, consider a whole reservation history with a fixed role map,
the same installation and valid uniform envelopes. Let
`X_max=max_i X_i` over **every** native-entry call since its initial capacity
vector `K_init` was charged. Induction in (11) gives

\[
 H_{history}
 =\sum_r\max(K_{init,r},\sup_i h_{i,r})
 \le\sum_r\max(K_{init,r},c_rX_{max}). \tag{13}
\]

For an initially empty reservation, `H_history <= C X_max`. Both the
maximum-volume boundary and the fixed role/domain boundary are necessary.
If earlier calls used additional roles, changed installations or were
public cold-only binary calls, retain their capacities in `K_init` or supply
their separate uniform history bounds; do not silently discard them.

## Native-entry scope

The installed inventory's 91 work positions includes six
`compact_crt.binary_swap` positions used by the initial public cold-only
branch. That branch does not pass through the native-entry path bounded in
equations (8)--(10) of the frozen proof. These six positions have zero new
extent in a native-entry call but can have nonzero inherited capacity after
a different earlier call. They are therefore covered by `K0` when present,
not assigned zero historical storage merely because the current call does
not reach them. A separate cold-only public bound can be combined later.

This note does not assume that changing or closing a Python file implements
deallocation of an unbounded tape-machine reserve. Such a lowering would
need its own explicit storage convention. The stated formulas use the
historical convention of the current source's storage argument.

## Shrinking-history control

`check_history.py` runs the actual source `pipe`, `Page`, `Arena` and erasure
methods on fresh in-memory files for complete fields of 128 and then 8
bytes. The two weighted heads each reach the full field size in each call,
and every retained byte is zero on release. Their per-call sums are 256 and
16 bytes. Reusing their physical reservation retains 256 bytes after the
second call, rather than 16. Even the production named-role envelope
`G(17,2)*8=891/16` is smaller than that inherited extent; the current-call
grant alone fails. Using `X_max=128` or (12) covers it.

The checker also retains an asymmetric blank entry vector, checks roles
untouched by the current call, and verifies (11)--(13) with exact integer
and rational arithmetic. These are actual allocator/pipe executions plus
a separate historical-reservation ledger, not a full production calendar
or a new local-byte proof.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
The frozen proof and receipt remain unchanged. Apache-2.0.

# Exact optimum for the retained pure-reset family

The backward tagged-centre proposal cannot reduce the recursive profile
under the width rule below, for **any reset policy in the stated family**.
The minimum for each query-subset size has the same value as the earlier
bounded screen. Some individual subsets improve. The new result replaces
that screen's search limitation with a complete finite proof. It does
not change or replace the frozen screen files.

## Source and family

Use the backward word in `history-encoding/FULL-MODE-PROGRAMS.json.gz`,
with decompressed SHA-256
`f271842a741584389e166e700e262f161b0dd570ce8c7a540f2717e90ead5205`.
Stop before event 12995. Event indices start at zero. The eight centre
fields, in mode order, are

`[92,57,81,224,11,240,9,256]`.

Both data banks receive the tag `(1+delta)`. Helper inputs have no tag.
The ideal logical centre row is `u_k+(1+delta)R_kY/4`. The proposed
decoder rounds to its coarse part and divides the residue by `delta`.
The calculation below concerns native errors that can reach this read.
It does not supply a physical rounding program or its margin proof.

A permitted reset is on the individual target of an existing scalar
or native event, immediately after that event and before the fixed
centre cut. Its ideal row must have either no data-input coefficient
or no helper-input coefficient. A pure helper value is rounded to its
coarse value. A pure data value is rounded and tagged again. Under the
required margin, either operation preserves the ideal value and has
zero error derivative. Any subset of these sites is permitted.

The family does not include new scalar edges, a change of basis, joint
resets, resets at other chronology points, changed native interfaces,
or a special child-error contract. In particular, this is not a bound
for every circuit that can read or encode the centre information.

The exact scalar replay uses the accepted named native frames. A
native event preserves canonical content; its output error is an
arbitrary vector in its complete principal field. An adapter is an
exact change of view. The proof does not replace a canonical frame
by a plain partial transform on its listed basis. No literal native
phase cancellation or new phase recipe is used.

## Three independent groups

First replay all 704 initial coordinates through the exact scalar
prefix. This determines the permitted reset sites and whether each
native input has data and helper coefficients. The last pure-data
reset is event 637. The first native event is 9742. Thus every subset
of pure-data resets leaves the native error response unchanged.
There are 216 permitted pure-helper sites after the first native event.

Now propagate Boolean centre supports backward. At an ADD, take the
union into its source. A nonzero SCALE preserves support. A native
event and an exact adapter preserve the field identity. This graph
ignores coefficient cancellation. It therefore contains every possible
error path. A derivative-zero reset only deletes paths: it cannot
create a path absent from this graph.

Exactly 180 of the 216 sites have empty Boolean centre support. They
are irrelevant under every reset policy. The other 36 sites split as
follows. The masks use bit `k` for centre mode `k`.

| Modes | Mask | Relevant reset events |
|---|---:|---|
| 0 through 3 | 15 | 10008,10009,10012,10013,10014,10015,10016,10023,10024,10034,10035,10037 |
| 4 and 5 | 48 | 10226,10227,10230,10231,10232,10233,10234,10241,10242,10252,10253,10255 |
| 6 and 7 | 192 | 10444,10445,10448,10449,10450,10451,10452,10459,10460,10470,10471,10473 |

Every relevant reset has Boolean support in one group. Every native
error that can reach any centre also has support in one group. All
such native inputs contain both data and helper coefficients. The
complete receipt gives every Boolean support, each native group,
and the filtered reverse scalar programs.

These statements prove independence, rather than only suggest it.
A reset in one group cannot change any other group's response. No
native job contributes to two groups, so their union costs add. Each
choice of three local policies is a legal global policy. Therefore
the optimum for a query subset is the sum of the three local optima
for its intersections with the groups.

Each group has 12 sites. It suffices to check `3*4096=12288` local
policies, in place of all `2^36` effective global policies. The other
180 site choices and every earlier pure-data choice are irrelevant.

## Exact enumeration and optimum

The checker propagates exact response vectors backward. It uses an
integer common denominator that contains the product of all scalar
denominators in the filtered program. Every division is checked for
exact divisibility. It uses no floating-point arithmetic.

For each local policy and each nonempty query subset in that group,
the active profile contains only ranks one and four. The number of
rank-four jobs is always the number of selected queries. Therefore
minimizing the rank-one count minimizes every nonnegative rank moment
at the same time. There is no trade between a rank-one and rank-four
job hidden by the mass objective.

The exact minimum masses, over all query subsets of each size and all
policies in the family, are:

| Removed centre jobs | Minimum extra-accuracy rank mass |
|---:|---:|
| 1 | 25 |
| 2 | 44 |
| 3 | 60 |
| 4 | 65 |
| 5 | 90 |
| 6 | 109 |
| 7 | 134 |
| 8 | 153 |

For all eight queries, resets after events 10008 and 10012 attain
profile `{1:121,4:8}`. For modes 0 through 3 the same policy attains
`{1:49,4:4}`. The complete receipt gives an optimal policy for each
of the 255 nonempty query subsets.

Of these subsets, 32 improve the earlier screen by one rank-one job.
They are precisely the masks whose intersection with mask 15 is 5 or
13. For example, mask 5 improves from 44 to 43 rank-one jobs, and mask
13 improves from 49 to 48. The other 223 profiles do not change. The
minimum for each subset size and both inequalities below do not change.

A separate forward impulse path checks every Boolean native ancestor
under no resets, all eligible resets, and the best all-query policy.
It agrees with each exact reverse response. This also checks that the
180 Boolean-irrelevant sites do not change these forward responses.

## Recursive precision consequence

For a query subset `S`, let `C(S)` be the union of native jobs with a
nonzero response in at least one selected query. The exact optima give

`number of rank-one jobs in C(S) >= 8|S|+13`

for every policy and every nonempty `S` in this family. Since an
optimum is a lower bound for every other policy, this inequality is
not limited to the displayed optimal witnesses. Also,

`rank mass of C(S) >= (65/4)|S|`.

For `0<=sigma<=1`, the first inequality implies

`sum_(j in C(S)) r_j^sigma - |S|*8^sigma >= 13`.

Thus a doubled-width charge for the native jobs exceeds the removed
rank-eight centre terms at every exponent in this range. This
comparison grants all other new work for free. It also grants each
retained private centre job its original width. The original private
centre inputs are pure data, but the needed tag removal and repacking
have not been emitted as a complete partial-centre word.

For a uniform width multiplier `beta`, write `sigma=1-a`. All active
ranks are at most four, so

`sum_(j in C(S)) r_j^(1-a) >= mass(C(S))*4^(-a)`.

If `beta>=97/65`, then `beta-1>=32/65`. The added moment is at least
`8|S|*4^(-a)`, whereas the removed moment is `8|S|*8^(-a)`. The change
is nonnegative at `a=0` and strictly positive for every `a>0`.

The nonuniform conclusion uses the same width premise as the earlier
screen. Give query `k` a nonnegative allocation `gamma_k`. Charge a
child the maximum allocation among queries to which its error can
flow. For `S(t)={k:gamma_k>t}`, integration of the subset inequality
gives

```
sum_j r_j^sigma max_(k in support(j)) gamma_k
    >= 8^sigma sum_k gamma_k + 13 max_k gamma_k.
```

This proof applies to every policy in the full stated family. It also
holds if the policy changes by bit layer and the costs add by layer,
since the same subset inequality holds at each layer. That observation
does not assert that such policy changes form a legal native word.

These are conditional cost statements. The exact support result does
not prove that every child algorithm needs this width. A lattice-error
contract, new reads, a new basis, or a different permitted reset cut
can fall outside the result. No complete supplier or kappa gain is
claimed.

## Reproduction and review

```
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/temporal-reuse/check_exact_tagged_resets.py
```

The expected final status is `PASS_EXACT_ALL_PURE_RESET_POLICIES`.
The checker imports no other research checker. It reads the pinned
actual scalar word and emits the complete exact local case lists,
Boolean witnesses, global minima, and direct impulse controls.
Independent review of this new group reduction is pending. Earlier
independent reviews of the 227-policy screen do not by themselves
certify this larger family.

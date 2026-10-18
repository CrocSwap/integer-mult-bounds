# Independent review of local bulk resampling and tape transfer

The combination of [the principal-window analytic construction](downstream-microbox-resampling.md)
and [the complete tape schedule](bulk-resampling-tape-transfer.md) has a
positive conditional transfer review. The arbitrary-source router and the
phase-cell scalar solver are separately reviewed dependencies. The new
construction replaces d separate full-width axis exposures by a constant
number of full routing scales and O(d) moves of polynomial-size local
fields. This report does not promote a numerical multiplication exponent;
strict assembly arithmetic is a separate check.

Review date 2026-10-08. Original retained input:
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`; compact-control input:
`6e564879f51ae16f23d392e9e196c605f36d90df`. Historical campaign deadline
08:25:21 UTC is retained in earlier identities; the same campaign was
subsequently authorized through 10:00:00 UTC. No inputs, completed sources
or previous experiment identities were replaced. The result remains
conditional on the original chunk/phase and scalar interfaces; it is not
an unconditional integer-multiplication theorem or a novelty claim.

## One global matrix and principal-window accuracy

All windows restrict the SAME globally fixed rounded H. Its diagonal is
exactly one; its off-diagonal cyclic halfwidth is w, its row gap is at
least `1/(8p)`, and its inverse norm is at most `8p`. Global within-cell
weights and Toeplitz coefficients are not locally rerounded. These
properties follow from the accepted phase inverse construction; merely
having a row-dominant matrix with another diagonal would not justify the
Neumann series in `H-I`.

With `F=H-I`, the conservative gap `g=1/(16p)` gives
`||F||<=1-g`. For a core row farther than Jw from a principal interval's
artificial ends, each path in the first J powers stays within that
interval. Therefore their core rows agree exactly after zero extension.
Two Neumann tails give

```
||R H^-1-R H_I^-1 P_I|| <= 2*(1-g)^J/g
                           <= 32p*2^(-J/(16p)).
```

This is a row-norm bound for arbitrary signed complex inputs. With
`J=512p^2`, it is below `2^-16p` for p>100. The independent resolvent
bound `||H^-1-N^-1||<=32p^2*e_p`, where
`e_p=p*2^(16p+7)*2^-32768p+2^-46p`, is smaller still.

Two period qualifications are essential. First, `|I|<s` alone does not
make a cyclic principal matrix noncyclic: for s=20, w=3 and I=[1,20),
indices 1 and 19 retain a width-two cyclic edge at unwrapped distance18.
The repaired condition `s-|I|>w`, implied here by
`s>2*(L+2A+2w)`, excludes such endpoint coupling. Second, a lifted
constant phase can join the last and first physical cells, but their
cross-cut entry in H was separately rounded. The local partition must
preserve the ORIGINAL physical period cut, even if unwrapped `q_j-j`
agrees across it. The reviewed construction now explicitly does both.

## Local arithmetic and normalized tensor maps

Intersect a window with original global cells. Its at most two clipped
endpoint pieces have all vertices designated boundary when their length
is at most4w. Otherwise retain the first and last w vertices. Preserving
the physical period cut adds at most O(w) boundary vertices. Every
remaining interior is a principal Toeplitz block with the same global
similarity weights; different interiors do not interact.

The inherited Schur elimination retains the diagonal-dominance gap and
does not increase row norm. Boundary fill connects only the two groups
of one interior or neighboring groups, giving bandwidth O(w). Thus the
accepted Gohberg-Semencul, directed Schur rounding, banded LU, reciprocal
and local residual proofs apply. They are bounds in row norms, not sums
over all cells; there is no omitted factor proportional to the line or
window count. Empty interiors are skipped. For M window indices,

```
n_boundary <= 4*M*w/d+12w,
online line cost = O((M+M*w^2/d+w^2)*p^(1+delta)).
```

The retained error `2^(64p)*p^64*2^-32768p` is far below one p-grid unit.
Short convolution lengths are at most `4d+1`, with O(p)-bit retained
factors and an unconditional conventional multiplier. Exact rational
factor construction is polynomial in t and p and remains `n^o(1)`
under the retained axis-size relation. No stronger multiplication result
being proved by this campaign is used to multiply those local operands.

Set `j_scale=ceil(log2(32p))` and `D_normalized=D/2^(2u)`. The local
compression `D_normalized H_I^-1 C/2^j_scale` has norm at most1/4,
and the true global normalized compression at most1/8. Selection C
has norm one and uses only the supplied target halo by definition of I.
Comparing restricted local products with global tensor products therefore
adds at most the sum of one-axis row errors. Early core cropping is done
ONLY in the completed axis. Other axes retain their own input halos until
their maps are applied. No intermediate boundary output is supplied as a
purported global halo value, so a halo refresh is unnecessary.

Expansion uses positive restricted Gaussian rows and norm below3/4.
The actual short chirp blocks retain the original global s,t and ratio,
with only the requested local outputs; they do not chirp an entire p^8
tile using unbounded diagonal weights. Their O(p)-bit per-block descriptor
work is absorbed in the block's O(block_length*p) scans. The local tile
contains many short blocks. Source omissions are beyond the existing
O(p) Gaussian radius, so the accepted tail bound applies. Together with
componentwise directed truncation and the local inverse bounds, the
original loose tensor interface `d*p^2*2^-p` and gamma normalization remain
valid. Approximate maps have sufficient norm headroom to retain disk
outputs; no unnormalized large intermediate is passed as a disk input.

## Fractional cores, two different volume bounds

Take `L=2^ceil(8*log2(p))` and `A=4096p^3`. The target cores are
`[kL,(k+1)L)`, with corresponding source cores
`J_k=[floor(kL/rho),floor((k+1)L/rho))`. They partition the source period
in exact increasing order. Selecting nearest q indices from target halo
`[kL-A,(k+1)L+A)` gives source I with endpoints

```
ceil((2*(kL-A)-1)*s/(2t)),
ceil((2*((k+1)*L+A)-1)*s/(2t)).
```

This also fixes ties and wrapping endpoints. Each core has source distance
at least `A/2-3>512p^3` from its artificial cuts. The near-one constraint
gives `L-|J_k|>=L/(8d)-1`, while `L>=64dA` ensures the full source halo
fits in L. Padding each source halo to L therefore produces exactly T
records, governed by the retained `T/S<2`. It does not double every
source interval.

Target halo fields instead have persistent length `L+2A`; their exact
tensor volume is `T*(1+2A/L)^D<2T`. Only the CURRENT local field is
temporarily padded to its next binary length for a move, and its added
zeros are removed before the next axis. Simultaneously rounding all halo
fields to2L would introduce2^D volume and is invalid. All these
inequalities hold uniformly for eventual p>100 and d<=p; finite exact
integer controls include p=101,127,256,1023.

## Ordered scans, catalogs and final row order

The small complete-field move has a direct fixed-tape construction.
Transpose `[B]x[2]x[R]` by scanning complete R-blocks onto two parity
tapes and concatenating them. Its inverse interleaves the two complete
halves. Repeat on most significant then subsequent bits, inside the
preceding-bit fibers. This preserves internal significance and B order.
It costs O(log(p)*V) for a polynomial-size field, across arbitrary
complete mixed-radix spectators. Rewinds are within the current work
fiber and cost its volume. A line map changing its field length uses
the new field's transpose on return, not an inversion with stale names.

For halo duplication, starts and ends are monotone. One initial bounded
set of current-fiber scans retains the periodic head/tail; it does not
rescan the entire tensor for each window. Emit the first window while
mirroring its next overlap. Each later window first writes that saved
overlap, then reads the new source portion, mirroring its tail on the
other of TWO overlap tapes. Core spacing greater than twice the halo
ensures the next saved tail lies in this newly read portion. Thus no FIFO
shift, repeated whole-window read or random source seek is needed.
Head resets and mirrored copies are proportional to written traffic.

The binary global gather and its inverse use the independently reviewed
coordinate router, with paid untouched spectator records. All other
passes move only short local fields. After exposing axis i's short field,
its global j row is increasing before a complete spectator suffix. Source
embedding zeros can be removed, monotone I windows emitted and padded,
then the short field returned. Coarse `k_i` stays in its original order.
For compression the same procedure emits target halos before any inverse.

Factor catalogs follow `[A_prefix]x[k_i]x[B_suffix]`. Scan k_i in order
for each A_prefix; retain its page across B_suffix and all inner lines;
rewind at the next A_prefix. The page has
`O((L+L*w^2/d+w^2)*p)` bits. Per-line page scans are part of the line
solve cost. Copying an entire page or doing polynomial metadata work per
origin is absorbed by the other complete inner fields, at least
`L^(D-1)` records. Here retained D=d-1 tends to infinity for fixed
epsilon>0; this is not a claim about an isolated one-axis short-record
contract. The page catalogue is a sequential tape, not random memory.

Final source assembly exposes `[k_i,local_i]`, copies only the first
`|J_k|` complete suffix blocks from each tile in k order, appends zeros
to t_i, and splits the now ordinary increasing global j field into its
coarse and low bits. Returning those low bits leaves the canonical
binary microbox layout. After the inverse gather, fixed-cut scans remove
the global j>=s_i zeros. This restores the original prime-box row order
and normalization without a large mixed-radix transpose.

## Cost, independent evidence and scope

Summing the local line cost over each axis and the halo volume gives

```
O(Tp*[p^tau*polylog(p)+d*polylog(p)
      +d*p^delta+w^2*p^delta+d*w^2*p^delta/L])
+ polynomial(t,p) setup.
```

The first term pays the constant number of large router calls. Embedding,
small-field exposure, periodic halos, core crops, factor traffic and ordered
assembly contribute the displayed short passes. `w^2=O(p^(1-r))`; setup
is negligible under the retained axis sizes. A fixed collection of tapes
and bounded current work fibers suffices. The changed movement margin is
a, while the Gaussian margins `1-epsilon-delta` and `r-delta` remain.
Every recurrence, guard, normalization, compact reservation and eventual
prime capacity condition must still be checked in the final assembly.

[review_bulk_resampling.py](../code/review_bulk_resampling.py) imports no
producer. It executes small-field complete-block split/interleave moves,
alternating-buffer monotone halo emission, source zero embedding,
fractional source padding, local selector lines, early core cropping,
sequential page visits and final source assembly. The global gather models
the separately accepted router contract. Selector maps check exact payload
provenance and order; they do not simulate true Gaussian arithmetic.

The [fresh joined run](../runs/20261008T030514Z-review-bulk-resampling/)
passed all84,824 complete output records in six two/three-axis expansion
and compression schedules. It performed124 binary split passes,135
interleave passes,58 small-field moves,11 current-field-only paddings,
76 halo rows,280,744 monotonically new records,12,584 mirrored overlap
records,76 sequential page visits and14,400 local lines. Arbitrary
prefix and coefficient-suffix cardinalities, wrapping windows and unequal
source cores are included. The largest persistent halo volume was46,656
against target32,768, and temporary one-field padding82,944; the latter
is a constant work-volume factor, not persistent2^D growth. Independent
wrapped short-path checks cover1,242 exact entries.

Python3.14.4, one worker,0.79 seconds,28,592 KiB maximum RSS. Source
SHA256 `c05c41f3fcec2f845043c4b00fd8c939d516f8ea3826a0112228ad625aa1f39f`;
certificate `f3883ec3404b1bebbea2c2b6e8961de1e9fb958e10ce5b8da27a0e086931b5a4`.
Small fixtures satisfy their actual halo-fit, overlap and capacity tests;
they are not numerical simulations of the enormous asymptotic halo.
The all-size analytic proof and accepted Gaussian solver supply accuracy.

[review_bulk_boundary_negatives.py](../code/review_bulk_boundary_negatives.py)
and its [fresh run](../runs/20261008T031019Z-review-bulk-boundary-negatives/)
retain four exact negatives: insufficient complement gap, merging across
the original phase period cut, cropping an unprocessed axis's halo, and
simultaneous binary padding. The latter two give respectively1/16 versus
zero for a tensor core, and256T versus a near-one persistent halo volume.
These controls distinguish the repaired construction from plausible
invalid variants. Certificate
`b01739e355f97d122a4d0bdd6e9523af51bb63839065c860003f6185ea164560`.

The positive conclusion is a written all-size conditional transfer backed
by independent finite operator and ordering controls, not formal machine
verification. No remaining structural counterexample was found after
the explicit endpoint and layout repairs. Strict composed arithmetic is
the next review step. Reproduce the two scripts with `python3 -B
code/<review-script>.py --output <fresh-path>` from the topic directory;
the standard library suffices. Exact commands, hashes, logs, version and
owned reservation release are retained in the run protocols.

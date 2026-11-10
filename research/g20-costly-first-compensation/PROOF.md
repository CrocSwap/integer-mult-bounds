# Costly-first A2 compensation on the final G20 word

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.

## Domain and accounting contract

The source is Ali Romman's final 11,930-record, 685-role word from
[PR #5708](https://github.com/CrocSwap/integer-mult-bounds/pull/5708), head
`829d01fc031f7323ffcfa423fdfd1f24dcbe3190`, retained at canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. `SOURCES.json` pins exact
bytes and Git blobs. The 645-frame catalogue and its 52,624 directed
proper-nesting native edges are authenticated by
[PR #6324](https://github.com/CrocSwap/integer-mult-bounds/pull/6324).
Every edge rank is an integer from 1 through 7.

An A2 interval has equal outer ADDs `a += b`, no INIT/ERASE on a or b,
and no reversed ADD `b += a`. Delete both outer ADDs and keep every
interior event in order. Immediately after `b += s`, insert `a += s`;
after `d += a`, insert `d += b`. Corrections retain contact frames.
Include zero-contact cancellations.

[PR #6324](https://github.com/CrocSwap/integer-mult-bounds/pull/6324)'s independently authored first certificate records 2,248 costly
and 22 neutral intervals. For every costly first interval, enumerate all
second intervals on its literal output. All 2,248 first outputs have no
zero-source ADD, checked on formal rows, so literal and emitted scalar
indices agree. There are 5,114,417 ordered rewrite paths, with no contact
cutoff or sampled within-domain search. Each path is a sequence of program
rewrites; its invoice belongs to the resulting final word. Different paths
can yield the same word. Every demanded frame change may take any finite native path, charged
separately. Correction frames, role ownership, public final frames and
emitter chronology remain fixed. Zero-source omissions and final returns
are included. The complete source local paid histogram is
`{1:1281, 2:1338, 3:58, 4:57, 5:102, 6:10}`. Write `H_r=r^t`, `0<t<1`.
A common rank normalization multiplies the comparison by a positive factor.

## Scalar invariant and target bill

Let E be the transvection `a += b` on formal GF(2) rows. At each interior
boundary after an event and its forced correction, changed rows equal E
applied to original rows. Only row a differs: it is `old_a XOR old_b`.
For `b += s`, b updates normally and the correction adds the same s to a.
For `d += a`, the changed event uses `old_a XOR old_b`, then the correction
adds old_b, restoring d. Other ADDs commute with E. Resets outside a,b
commute with E; resets on a,b and reversed gates are excluded. Removing
the right E therefore restores every original row, including owned rows.
This is an identity on all columns, not an input sample.

Every first word is additionally replayed on all 685 formal columns. All
35 exceptional/tie second words below receive independent full-column
replays. The remaining second endpoints follow this symbolic identity
and their exhaustively verified interval conditions; 5,114,417 separate
full-column chronological replays are not claimed. The productive target
interface and owned final zeros are unchanged: `Delta T=0`. Under the
source paired-address native contract, frame queries telescope along each
wire and every ADD uses a common actual frame. Thus preserving the scalar
map and public entrance/exit frames preserves that native boundary contract;
its uniform interpretation remains inherited. In the retained 18-full-call
context, query differences add across calls and the target difference stays
zero. The present local lower bound therefore remains nonnegative under
those fixed-context substitutions. A fresh global word or ordinary-fee
admission is not claimed.

## Exact per-role invoice

Each role has a chronological request list recording its requested frame
and pre-ADD nonzero-row flag. INIT/ERASE records a free reset. Zero-source
ADDs contribute no requests. Append every public final return; owned final
rows must be zero. A different-frame request pays exactly when the row is
nonzero. A zero destination still changes frame without a paid query.

Within an interval, the invariant determines all changed a,b requests.
At `b += s`, correction source is old_s and its destination is
`old_a XOR old_b`, with b taken before the contact. At `d += a`, the
changed source is `old_a XOR old_b`; correction source is old_b and its
destination is `old_d XOR old_a XOR old_b`.

Third-role requests are unchanged except when a `d += a` contact has
old_a=0 and old_b nonzero. The old event was omitted, but the changed pair
requests the contact frame on d. Insert this first request, paid iff old_d
is nonzero. When old_a=old_b is nonzero, the changed original event is
omitted but its correction preserves the old d request. Repeated requests
at the same frame are free.

For each affected role, start from its actual frame before the left gate,
replace its interval requests, and include its first subsequent request
or reset. Both words then have the same frame, and their formal rows agree
after the right gate, so every later charge agrees. A final return is that
subsequent request when appropriate; a free reset clears the difference.
This proves suffix stitching without dropping restoration costs.

`trace.py` implements this lemma. `controls.py` uses an independent full
chronological interpreter, comparing both paid histograms and complete
per-role frame movements with zero/payment flags. It exhausts 30,941
words of length at most four over the declared 13-event alphabet, then
checks 2,000 deterministic length-20 words. The latter are additional
finite controls, not exhaustive length-20 coverage. Actual missing-toggle,
missing-side-demand, missing-suffix and charged-zero code mutants reject.

## Arbitrary paths and the stronger non-edge floor

Let d(u,v) be shortest total native rank. The inherited exact metric
checker verifies edge potentials and tight descending parents. For any
path with positive ranks r_i, subadditivity and monotonicity give

\[
\sum_i r_i^t \ge (\sum_i r_i)^t \ge d(u,v)^t.
\]

Thus `H_d` is an optimistic bill, not an admitted rank-eight child or an
attainment claim when the endpoints are not a native edge.

If `(u,v)` is not a native edge, every realizing path has at least two
edges. Let its total rank be S and split it into first rank a and remaining
sum b. Then `sum r_i^t >= a^t+b^t`. For integer `1<=a<=S-1`, concavity
makes `a^t+(S-a)^t` smallest at an endpoint. Hence

\[
\sum_i r_i^t \ge 1+(S-1)^t \ge 1+(d-1)^t.
\]

A non-edge cannot have d=1: a positive-integer path of total rank one is
a single rank-one edge. The verifier still checks d>=2 at each refined
occurrence. This covers arbitrary finite paths, including loops. Charge
each **occurrence**, not merely each distinct endpoint pair.

The collapsed census has two exceptional shapes:

| Collapsed difference | Paths | Mandatory non-edge occurrences |
|---|---:|---|
| `-2H1-5H2+2H3+4H4` | 20 | two distance-4 and one distance-2 |
| `-2H1-4H2+H3+3H4+H5` | 10 | two distance-4 and one distance-2 |

Both tend to -1 as t tends to zero and cannot be called universal losses.
All 30 words receive full chronological replay, with endpoint pairs and
multiplicities retained. The stronger floor changes them respectively to
`2H1-6H2+4H3+2H4` and `2H1-5H2+3H3+H4+H5`. Their exact hinge vectors
are `[2,2,8,10,10,10,10,10]` and `[2,2,7,9,10,10,10,10]`, proving strict
loss throughout `(0,1)`. The apparently favorable raw shapes are
relaxation artifacts. Both raw invoices and refinement witnesses remain
in the certificate.

## Exact universal signs

For signed delta_r, r=1,...,8, define integer hinges
`q_k=sum_r min(r,k) delta_r`. Put `a_8=f(8)-f(7)` and
`a_k=2f(k)-f(k-1)-f(k+1)` for k=1,...,7, where `f(r)=r^t` and f(0)=0.
Strict increase and concavity give every a_k>0. Telescoping yields

\[
\sum_{r=1}^{8}\delta_r f(r)=\sum_{k=1}^{8}a_kq_k.
\]

Nonnegative hinges prove a nonnegative invoice. The hinge transform is
invertible, so nonzero delta has some positive q_k and gives strict loss.
This is exact over the whole exponent interval; no numerical exponent
sampling is part of the certificate. All but the two exceptional raw
shapes have this witness directly; their 30 occurrences have it after
non-edge refinement.

Five zero bills have no paid non-edge demands. Every paid demand is a
single admitted native edge with rank equal to its metric distance, so
zero is attained. Zero-row demands can use connected native paths without
paid-query charge. This is not a complete ordinary-cost supplier claim.

## Coverage and limitations

The indexed primary enumerator checks every equal-gate pair, barriers,
reversed contacts and all corrections. A separately authored bit-mask
enumerator supplies an independent domain check. Both include zero contacts.
Receipts bind each ordered second descriptor and raw invoice, and regenerate
all multiplicities and sign witnesses.

The result excludes paid savings after two fixed-contact-frame A2 rewrites
with a costly first step, under separately charged demands. Combined with
[PR #6324](https://github.com/CrocSwap/integer-mult-bounds/pull/6324)'s neutral-first result, it closes the complete two-rewrite domain
on this exact word. It excludes neither changed correction frames, new
frames, demand sharing, other identities, deeper rewrites nor changed
public interfaces. Native/all-size, ordinary, compiler, precision/tape,
caller and assembly obligations remain inherited or unrun. Selected kappa
stays 0.003125804 and admitted BIT cap stays 0.0034; the source's proposed
0.003507719059749 is a component bound. No human or formal-kernel scientific
acceptance is claimed.


## Precisely bounded third-step extension

After the full two-step census froze, the one allowed scalar-rewrite pivot
used exactly the five attained costly-first ties, at first-domain indices
1085,1086,1088,1308,1310. Each first word has direct native paid attainers and difference `2H2-H4`.
Each second move is a zero-contact cancellation that repays this debt exactly.
The five resulting literal words have lengths 11,932, 11,932, 11,931, 11,931, 11,931
and no zero-source ADD. Reconstructing the 473 zero paths in the pinned
[PR #6324](https://github.com/CrocSwap/integer-mult-bounds/pull/6324) certificate yields 242 distinct literal words; none equals these
five. This compares literal words, not an unproved equivalence quotient.

`third.py` enumerates every A2 interval on each of these five hosts, and the
independent bit-mask domain agrees exactly. The 11,363 total third paths
comprise 11,236 strict losses and 127 attained ties, including 15 zero-contact
intervals. All 211 raw signed shapes have nonnegative hinge vectors; no
non-edge refinement is needed for this extension. All 127 tied outputs
receive full chronological native invoice and 685-column endpoint replay;
every paid demand has a direct native attainer. The target and ownership
proof is the same symbolic A2 identity. `THIRD.json.gz` records every host,
complete domain digest, neutral interval, shape multiplicity and hinge.

This extension covers only these five hosts. The complete third neighborhood
after every second word, including the other neutral-first paths, is outside
the result. Search stops here; no arbitrary deeper scan was attempted.

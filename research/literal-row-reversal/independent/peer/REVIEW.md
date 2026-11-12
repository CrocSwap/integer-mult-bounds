# Independent source, interface and universal-cost review of row reversal

**Disposition: accept the scoped component theorem.** This independent
AI-assisted review for Jerry Chen / @CubeJerry is complementary to the
lead's separately written CPU/address-map replay. I did not execute the
author's CPU or test suite. No whole foundational assumption or new kappa
is established by this local component.

## Exact reviewed objects

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.

| Object | SHA256 |
|---|---|
| reverse.py | `4b516d85baf3303db809bc1174394009b1fc71a8f7d17fb6c729ec8bb6aba245` |
| Revised PROOF.md | `9dc3019f115098e1c14d41308b07266e48a6cd84f473e1205d472c640539f049` |
| Canonical graph JSON | `1cc5dec939a090d90a7fcfe6828df1f19b4603cad5d93419668ca198a9f9aa2f` |

All nine source copies were independently checked against both their stated
Git object identifiers and exact `commit:path` bytes. SOURCE-BINDINGS.json
records that authentication, including the published phase helper and the
original controller source. It is more than a comparison with an author's
local manifest. No Git ancestry inference from the shallow checkout is used.

## Source-domain correction made during review

The original source-join sentence gave `P=2^j` for the retained
`flip_digit(source,d,j,b)`. That equality requires a complete d-bit address
rectangle of volume `2^d*b`. The actual function only checks divisibility
by its slab `2^(d-j)*b` and accepts extra outer repetitions as well.
The author now states the complete-rectangle premise and the general
matching prefix count `P=V/(2^(d-j)*b)`. The code and core reversal theorem
were unchanged. This clarification prevents source binding from silently
narrowing or misdescribing the old function's admitted input extent.

The retained adapter path is an exact map precedent. Its filename and this
local equivalence do not establish a completed current native caller.
Descriptor production and that caller's other operations remain unproved
by this package.

## Actual entry boundary and universal map

Canonical 02-streams.tex explicitly supplies a fixed number of collapsed
lengths in canonical binary on descriptor tapes. It reserves Gamma codes
for interfaces that explicitly concatenate a header. The three separate
binary descriptors here therefore match the elementary boundary; no layer
header or hidden decoded shape is substituted. The program concretizes
finite descriptor fields as leading-one MSB words with blank terminators.
The fixed-number-of-collapsed-lengths premise does not pay for constructing
those lengths from a growing layout. That work remains assigned to callers.

At each prefix, the load loop puts exactly R complete B-bit records on
GROUP. Popping backward produces records in reversed order and each record's
bits in reversed order. RECORD then reverses those B bits again. Thus the
final source index of output bit `(p,r,b)` is `(p,R-1-r,b)`, for all positive
P,R,B and arbitrary correlated payloads. Each prefix exhausts GROUP and
RECORD and returns their heads before the next prefix begins. This proves
both suffix-order preservation and prefix isolation; neither follows from
merely reversing all payload bits.

The number of tapes, finite control graph and tape-port references are
fixed. `compile_reverse()` has no runtime arguments. Inspection and the
checker confirm exactly 524 local instructions over 13 tape owners and
four symbols, using only read/write/unit-move/goto/halt. The four unchanged
helper bodies are AST-identical to the independently reviewed phase
predecessor. Binary descriptor decoding is the newly adapted boundary.

## Encoded arithmetic and exact complete cost

For each scanned binary prefix v and next digit t, the guide loop replaces
v unary marks by `2v+t`, erases DOUBLE and returns both local heads. The
fixed digit branch is the only choice; no varying integer is decoded into
host control. The three public descriptor heads are returned by one trace
mark per forward move. Their blank terminators are read but not crossed.

Independently counting the local helper operations gives a prefix update
cost `47v+17t+23`, including the descriptor read/advance. For a positive n
with bit length ell and popcount s, the strict prefix sum is `n-s`: writing
n in binary proves this by summing each bit's contribution to the prefixes.
Leading setup, final blank and descriptor return contribute `9+5ell`.
The exact full descriptor cost is therefore

`47n - 30s + 28ell - 31`.

A direct count of the payload loops gives, per prefix, load
`R(12B+7)+1`, GROUP setup `3R+4`, pop/emit `R(17B+10)+1`, and final local
reset `3R+7`. Including prefix tests yields `29V+23PR+14P+1`.

The final data test, two DATA trace returns, two OUTPUT rewinds, complete
owner commit, guide cleanup, guard retirement and halt cost
`24V+10P+7R+7B+57`. Adding the initial 27 guard instructions and all three
decodes gives exactly

`53V+23PR+71P+54R+54B+28E-30(s(P)+s(R)+s(B))-8`.

This derivation agrees with the author's expression and the lead's separate
count. Since each of PR,P,R,B is at most V, the claimed
`256(V+E+1)` envelope follows. Unary parameter expansion is paid, not hidden
behind logarithmic descriptor lengths. The complete O(V) claim is scoped
to the supplied elementary entry boundary and includes current-shape resets
and return, not caller acquisition or a different ABI's conversion.

## Owner, failure and historical backing

No DATA write occurs while decoding, loading, popping or emitting. GROUP
and RECORD are private; the full output is staged before DATA's final
cardinality check. Commit then writes exactly the original V DATA cells,
with no replacement public owner. Both DATA returns and private erasures
use local markers and traces rather than numerical head origins. The
success theorem returns every head and erases all nine private guards.

Short DATA, an extra immediate bit, and invalid finite descriptor symbols
reject before commit. The proof correctly withholds head/private cleanup
and retry guarantees on rejection. The caller supplies enough blank owned
work through the stated visit caps; finite probes do not certify a blank
infinite tail. Opaque cells outside those regions remain protected on
successful legal calls.

The private caps are exactly those obtained from the loops: two V bodies,
P, R, two B bodies, maximum parameter M, maximum descriptor length L, and
one RB group. Including their guards/end probes gives
`2V+P+R+2B+M+L+RB+18 <= 8V+E+18` additional backing. Erasure is not
subtracted from pre-entry historical K0. Fixed-origin reuse takes a maximum
on each role, followed by a sum, rather than the maximum current-call sum.
The sequence `(8,1,1),(1,8,1),(1,1,8)` has total role-union allowance 86,
while its largest current-call allowance is only 72. The proof explicitly
retains this distinction and excludes uncharged arbitrary origin transport.

## Native corollary and retained limits

For R a power of two, `R-1-q` is XOR by the all-ones word on the entire
contiguous coordinate. For R=2 the unchanged suffix block is exchanged
within each prefix, precisely matching the retained flip_digit map with
the corrected prefix count. A fixed finite number of such supplied calls
composes at O_m(V), but the paper correctly does not claim a newly emitted
multi-call descriptor/scheduling controller.

A strided selected mask such as 1010 is not full-field reversal's 1111.
Also full reversal is not modular negation, which must leave row zero
fixed. General affine routing, source descriptor construction, native
lifecycle composition and all five complete-theorem assumptions remain
open. For the actual phase recipe reviewed separately, this primitive can
supply its offset translation only at the correct post-affine coordinate
and with paid descriptors; it does not supply the intervening linear map.

## Reproduction and finite independent evidence

Run the independent mathematical/static checker with a package path:

```sh
python -I -W error -B check.py /path/to/research/literal-row-reversal
python -I -W error -O -B check.py /path/to/research/literal-row-reversal
```

Expected status: `PASS_C3_INDEPENDENT_ABI_COST_HISTORY`. The receipt checks
all source copies, the fixed graph, four unchanged helpers, 4,829 binary
integers including 256-bit boundaries, 4,916 shapes including very large
symbolic parameters, and 114,752 exact source-map addresses. Those large
shape checks use mathematical integers, not claimed physical executions.
Six negative controls distinguish wrong maps, unpaid source/packing
premises, a false history equality and a wrong popcount tariff. They are
mathematical controls, not additional executed-program mutants.

The universal conclusions above come from the loop and arithmetic proofs.
The lead's separate CPU supplies runtime and program-mutation evidence.
This review is independent AI work, not human or proof-kernel acceptance.

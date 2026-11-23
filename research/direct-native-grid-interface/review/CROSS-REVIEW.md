# Independent review of the native requested-grid interface

**Decision: accept the stated conditional interface theorem.** Reviewed author
proof SHA256: `69ce2e2d57df59cf706960df2495cde5b3556e392acd7bc50a2d06c0800d5a8b`.
The author and this reviewer used separate implementations and proof checks.
This is model-assisted review, not human peer review or proof-kernel acceptance.

## What was checked independently

Let the external array be `u/2^P`, with Gaussian integer vector u, and let A
be the exact raw Hadamard action on h distinct address bits. Its entries are
integers and the normalized source action is `2^-h A`. At `R=E+1` and
`Q=P+R+h`, the private input integers are `2^h u`, representing the original
array divided by `2^R`. The normalized result is `A u / 2^Q`. Consequently
the native final truncation changes no component, and its returned integers
are precisely `A u`. Reinterpreting them on the external P-grid is the required
raw result. Another integer rescaling at return would be incorrect.

The single-basis numerator witness is admissible for every stated P,E,h.
On its complete spectator fiber every nonzero normalized output has magnitude
`2^-Q`. Truncation to `Q-1` makes it zero. The witness concerns this return
contract and scaling, not arbitrary algorithms or a minimum private space.

I independently read the actual `TensorWord` stride construction and raw
integer update. They cover complete padded arrays, not a restricted true-index
block. A dense sign-matrix interpreter checks all spectator fibers. A separate
Gaussian-rational calculation keeps the absolute phases in `b^h S C S`.
Neither calculation imports the author adapter or checker.

The computed-radius argument has a valid order of dependence: the unlimited
integer reference exists first; the frozen parent bounds that reference; and
the replacement execution agrees by induction. An ideal-prefix bound alone
would not prove the stated actual-data radius. The proof explicitly reuses
the parent's stronger computed-state theorem.

## Review finding and resolution

The first draft specialized the C-interior width without explaining the final
`b^h` allowance, while the source separately mentioned extra boundary guards.
I requested a proof or conservative extra padding. The accepted revision
supplies the credited endpoint divisibility/parity argument.

For `h=2k`, every C-tensor entry is a Gaussian unit divided by `2^k`.
For `h=2k+1`, it is a Gaussian unit times `(1+i)/2^(k+1)`. On the private
`Q+h` grid the completed endpoint integers are divisible by `2^k`; for odd h,
after that division their two components have equal parity. Fourth-root
phases preserve both facts. The final b multiplication therefore uses exact
even sums. Its temporary addition needs one extra signed bit, within the
explicit retained allowance of 26. This licenses that completed-endpoint
macro only. Arbitrary private-grid or unfinished-prefix values need not obey
the divisibility or parity, and the controls reject them.

## Parameters and physical scope

The inequalities `C0 < 2^29 L^9`, `bit_length(C0)<=29L`, `E<=1483L`, and
`P<=4p+3318L` hold for the stated integer domain. They imply `Q<=4807p` and
the conditional temporary width `<=4839p` when `L<=p`. The 13-bit logarithmic
parameter allowance follows. The suffix bound uses the actual production
inequality `d<=L/(2^16 s^3)`; no fixed subpower bound on h is substituted.
The original source's unspecified reservoir constants remain retained, so
this establishes eventual scale compatibility, not a new numerical activation
threshold or completed native realization.

The conversion accounting reserves one complete reusable window and charges
its full historical extent and scans. It does not free old backing after a
smaller call, count a correlated copy as productive stock, or price the native
provider's private banks as part of that one window. Native geometry, actual
provider execution, callback costs, storage and the multiplier recurrence
remain separate premises. All five canonical assumptions remain unchanged.

## Executed evidence

The separate oracle verifies 5,460 Gaussian-rational phase entries and 5,460
terminal-normalization entries, 360 complete fields with 32,004 components,
240 signed one-bit-coarser witnesses, and 430 exact parameter enclosures.
Normal and optimized results agree. Missing normalization, insufficient return
precision, nonendpoint divisor/parity and altered raw-source controls fail.
These finite computations corroborate the universal algebra above.

Both author modes were also replayed and compared with their frozen receipts:
1,829 adapter cases, 132,460 macro components, 180 sharp witnesses, 107 packing
cases and 84 selectors. These are author regression checks, not the independent
evidence. All eight retained files were separately compared byte-for-byte with
their exact Git commit/path sources.

The author checker needs its package import path and is registered with `-B`
or `-O -B`; a direct `-I` invocation fails to import its sibling module. The
registered launcher supplies a fresh private bytecode-cache path to each child
and compares newly produced JSON without overwriting frozen evidence.

The original #7849 scaling, normalized-H identity, fixed-root parity lemma,
native common-grid proof and earlier #8093 numerical work retain credit. The
new accepted implication is the explicit exact requested return grid and its
source-bound use. No new kappa is claimed.

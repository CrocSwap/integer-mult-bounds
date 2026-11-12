# Independent peer review: literal layer egress

Reviewer: the separate `crt_reusable_history` research agent, with OpenAI
assistance, for Jerry Chen / @CubeJerry. This is an independent source and
mathematical review, not human acceptance or a proof-kernel certificate.
The parent reviewer separately implemented a dense machine interpreter; this
review focuses on the universal algebra and complete interfaces.

## Decision and exact artifact

**Accept the scoped egress theorem and its stated 65536 time / historical-space
envelopes.** No scientific-code defect was found. A source-padding inference
was tightened during review; the author has incorporated the coupled-width
derivation without changing the scientific code. This does not accept a
complete layer, multiplier, removal of a whole foundational assumption, or
improved kappa.

Reviewed package: `worker-b/research/literal-layer-egress`, canonical base
`e54523517d0f03e58352e647c403a5af3e525a57`.

- `egress.py` SHA256:
  `5875981b27bbb131a1e13ffca7f7eb920aa85b90699e6d40a85bd3902ff073e7`.
- Emitted table SHA256, compact sorted-key JSON:
  `d3021bc0d7b378741e64ae768171f5aec1f289b15265f4463e7b91b887f11243`.
- Exactly 17,814 instruction locations, eighteen tapes, alphabet
  `{blank,0,1,|}`, and only read/write/unit-move/goto/halt instructions.
- All seven source files in the current `SOURCES.json` independently matched
  their byte lengths, SHA256 values and Git blob identities. This authenticates
  local bytes against the supplied exact provenance pins; canonical retrieval
  and GitHub ancestry are the orchestrator's separate responsibility.

The review read `egress.py`, the pinned Builder/Machine source, full `PROOF.md`,
and the relevant exact source sections. It did not execute or import the
author's numerical `verify.py`.

## Source domain and corrected padding argument

Canonical `05-layers.tex` defines `H0=(1/2)[[1,1],[1,-1]]`. Its phase identity
is `H0^tensor D=b^D S_D C^tensor D S_D`, with `b=(1-i)/2`. The nine Gamma
fields and MSB two's-complement ordering match the source, including the
distinction between global bound d and operated dimension D. Canonical
`02-streams.tex` defines Gamma exactly as used by this decoder.

The separate inequalities `F<=p+d` and `W<=p+2d+4` do not alone imply that
fractional zero-padding to p+d fits the latter width. The pinned selected
application section 5 supplies the stronger coupled formulas. With total
operated dimension t and preliminary-axis count q=Q0, substitute

```
p' = p+q, h' = q+1, D_remaining = t-q
F = p'+D_remaining = p+t
W = p'+h'+2D_remaining+3 = p+2t+4.
```

Padding by d-t zeroes then needs at most
`p+2t+4+(d-t)=p+d+t+4<=p+2d+4` bits. The all-individual small-root branch
has the same conservative bound. The author incorporated this derivation
after the review request. The actual producer/padding conversion remains
outside this egress program and must be supplied and charged.

The caller also supplies complete N>=1 pairs, legal r,P,S,K,rho+1 semantics
and the relation N=Mr. The program consumes the five skipped values' syntax
without unary expansion or cardinality validation. Distinct physical tapes
and blank visited private windows are necessary retained premises. In
particular, a blank origin does not prove blank backing further right.

For wider output, the public owner reserves payload positions through
`2N max(H,w)-1` and a blank end at `2N max(H,w)`. The proof pays for this
caller capacity and preserves exterior outside the reserved windows.

## Universal signed arithmetic

Write D=2m+e, e in {0,1}. Since b^2=-i/2, normalization has denominator
2^(m+e), an (-i)^m rotation, and, for odd D, numerator rows a+c,c-a. The
eight fixed row choices suffice for every D. The shift retains
d+ceil(D/2), so reducing D modulo eight does not lose scalar attenuation.

Every row has coefficients in {-1,0,1} with l1 norm at most two. The digit
recurrence `t=carry+alpha*x+beta*y`, `digit=t mod 2`, `carry'=floor(t/2)`
preserves the exact low-prefix identity. The carry set {-2,-1,0,1} is closed
because -4<=t<=3. After H input digits, feeding the sign bits twice gives
the signed row residue modulo 2^(H+2). Its magnitude is at most 2^H,
strictly inside that signed width, so the residue is the exact signed answer.
This covers negative source minima, positive sums and every rotation.

Absolute-value conversion cannot encounter the minimum signed value of its
own H+2 width: 2^H<2^(H+1). Also s=d+ceil(D/2)<H+2, so dropping s magnitude
digits cannot overrun NUM. The unsigned quotient followed by sign restoration
equals trunc_0(n/2^s), including negative fractions and negative-path zero.
It is the single final projection required by the source.

On the negative path, complement/add-one carry is zero or one. Past the
magnitude, synthetic zeroes give the stable all-one tail for a negative
nonzero answer or the all-zero tail for zero. Comparing all remaining finite
digits and this tail with the wth retained digit is necessary and sufficient
for signed w-bit representability, including both legal endpoints. No
divisibility condition is needed or imposed.

## Original-owner installation and failure

DATA remains read-only throughout arithmetic. OUTPUT holds all 2Nw result
bits before the first DATA write. Every numerical range rejection therefore
preserves the entire public payload, even after earlier successful pairs.
The theorem correctly makes no cleanup/head-return/restart guarantee on
failure.

DTRACE first reaches 2NH, is erased, and is reused during installation. Its
second excursion reaches 2N max(H,w), because output writes and shorter-output
tail erasure both move DATA. OUTPUT is erased as it is copied. Origins are
recovered by explicit marker scans; final writes erase the owned guards.
Header movements are reversed using HTRACE without scanning exterior. The
cleanup proof follows the table, including the unused VALUE role's initial
and final marker actions. No owner swap or free head reset is used.

## Complete cost audit

I independently counted the loops, including reads, writes, moves and jumps:

- Rewind of a length-L prefix: 3L+3; clearing it: 7L+4.
- One H-bit load: 15H+7.
- One signed row through the sign choice, including operand-end searches:
  21H+25.
- Absolute conversion: at most 7H+19.
- Low-bit removal and SHIFT return: 8s+5.
- Remaining signed output, range inspection, staging and NUM cleanup fit
  13H+16w+42. The fact s>=2 leaves at most H magnitude cells, so this bound
  includes the final empty read and jump.
- Clearing both X/Y fits 14H+10.

Together these give at most 126H+32w+16s+220 per pair before harmless fixed
entry/exit allowances. As s<H+2, the proposed 256(H+w+1) allowance is ample
on H>=7,w>=3.

The three unary-update helpers for v->2v+t cost at most
47v+17t+18<=47v+35; Gamma wrapper reads, trace movements and control add a
constant per digit. Previous prefix values sum to less than the final value,
and the number of tail digits is at most that value. Four decoded values
therefore cost linear work in p+d+D+w+E. Skipped values cost linear work in
encoded length, even when their numeric values are huge. Initial markers,
header return, comparisons, H/SHIFT construction and parameter cleanup fit
the proof's 512 metadata envelope. No decoded integer is supplied for free.

The final source/output work, before fixed cleanup, has direct bound

```
10NH + 28Nw + 12N max(H-w,0) + 10N max(H,w) + O(H+w+1).
```

It fits 64N(H+w+1)+128(H+w+1). Substituting H=p+2d+4 into the three group
bounds proves the published complete envelope

`T <= 65536(E+p+d+D+w+N(H+w+1)+1)`

with substantial slack. Numerical rejection executes a bounded prefix of
the same pass. Fixed table precompilation is separate; no exchange rate for
unrelated native or movement services is inferred.

## Historical backing audit

OUTPUT reaches at most 2Nw+2 private cells; DTRACE reaches at most
2N max(H,w)+2. Their sum is at most 4N(H+w)+4. Each of the other fourteen
roles uses at most H+w+E+1 new possible cells: NUM has H+4, QBUF has w+2,
and the longest unary doubling buffer has at most max(p,d,D,w)+2. On
H>=7,w>=3,E>=9 this includes each guard and end blank. Four residual cells
fit in the two unused copies of that allowance. Therefore the exact bound

`K0+4N(H+w)+16(H+w+E+1)`

holds for translated origins and arbitrary entry histories under the stated
blankness premise. Erasure does not reclaim backing and no histories reset.
Public DATA/HEADER capacities remain separately charged. Charging the commit
trace only for 2NH would fail for w>H; the current proof avoids this error.

## Final phase join and remaining assumptions

Toward-zero truncation is odd and commutes with real/imaginary permutations
and sign changes, hence with every i^k phase and the supplied final S sweep.
For generic accepted packets, this alone does not ensure a later negation of
a signed minimum fits. The source-admitted disk premise supplies the needed
stronger fact: H0 has absolute row sum one; tensoring retains it; S preserves
the disk. Before final S, the normalized packet thus lies in the disk.
After projection each component has magnitude at most 2^p and fits with
room for all phases when w>=p+2. This verifies the intended source join.

The result is a local egress implementation conditional on the producer,
phase services, physical windows and source semantics. Compiler, stock,
permutation, recursive-C and analytic-recovery obligations remain. O(Np)=O(V)
follows in the selected parameter bands; no complete multiplication exponent
improvement follows from this local result.

## Executed independent corroboration

From the run root:

```
python -I -W error -B reviews/b-peer/check.py
```

Expected status: PASS_INDEPENDENT_LOCAL_ALGEBRA_AND_SOURCE_CHECK.
Executed successfully: 128 finite carry transitions; 174,752 signed-row cases
at widths 1 through 7; 4,106 range cases; Gaussian powers 1 through 128; all
seven source pins; emitted table identity. Four negative controls expose
floor versus toward-zero, overly narrow signed sums, source-only trace
accounting, and the insufficient independent-width padding inference. These
checks supplement the universal arguments; they do not replace them. The
parent's separately implemented dense-machine execution is separate evidence.

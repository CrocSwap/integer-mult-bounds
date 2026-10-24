# Gaussian core verification scope

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.
I ran the component and complete-join checks on Darwin arm64,
Python3.12.13. I use Python integers/Fractions only in separate checking
models. During physical execution I disable payload decoding and seal
new tape constructors. I record final committed-export and hosted
receipts in the public PR and Discussion3664.

## Complete Gaussian producer and consumer

I prepare one global axis with s=13,t=14,u=1,w=1, work precision24 and
target precision16. I construct its actual coefficients and exact
structured H on encoded tapes. For each window I form the exact old-H
Schur complement, round it before exact LU, emit rounded structured
factors, and execute the complete complex consumer.

| Target halo | Lifted source interval | Cell lengths | Interior/boundary rows | Interior/boundary calls |
|---|---|---|---|---|
| [1,6) | [1,6) | 5 | 3 / 2 | 4 / 2 |
| [11,19) | [10,18) | 3,5 | 3 / 5 | 4 / 2 |
| [4,11) | [4,10) | 3,3 | 0 / 6 | 0 / 2 |

The call counts cover both real and imaginary components. The first two
windows execute both interior passes; the last exercises the all-boundary
path and a missing target coordinate in C selection. The wrapped window
retains the original physical period cut. I compare the full page,
including its old-H LU factors, with independent exact rational models.
In both nonempty-interior cases, replacing the old interior with the
dense q-model changes the exact Schur complement; I check that distinction.

The returned p-grid numerator pairs are:

```text
[1,6) target halo:   (9,2), (-5,-12), (14,2)
[11,19) target halo: (-4,-10), (10,0), (-2,10), (13,-3)
[4,11) target halo:  (15,7), (-17,-23), (-15,23), (19,-7)
```

I obtain these raw-return SHA256 values, in the same order:

```text
6725455590b59109edf00accef3b1e81be47adb36c51a8f79be0b0902cd58e50
aded20c627af8dd4313662af656b2c6a19f45ee9a554397ec84351e0bed98c7d
f19643e83c9b3461dcb7b4998c184b980b511d2c487addf321542c1743343e48
```

I match a separate staged model exactly. I also compare each result with
a dense exact inverse of the original principal H, followed by its
normalization. The component error is below two target-grid units.
I verify the complete word-API invoice, borrowed values/heads, child
returns and scratch restoration.

These finite parameters do not satisfy the asymptotic production domain.
I use them to execute the algorithm and its source relations. PROOF.md
supplies the quantified production argument; I do not infer it from
these three packets.

## Public ownership and rejection checks

I run `Preparation.run_explicit` and `Core.run` together on s=8,t=9,u=w=1,
P=p=16, target halo[0,3), source core[1,2). I compare its result (-4,8)
with a separate Gaussian-interval/exact-LU oracle. Preparation clears its
dense matrices before returning the protected page. After consuming it,
I prepare the same page again and require identical bytes.

The page SHA256 is
`3dd6dd7bee0defb19f98000498e0c47b19e8eb51efe7e5937793cb02fffa4913`;
the core SHA256 is
`f45b83f5b86d3e09cb74e3c01f76cc678372fbb325d748ca2ed958085f417723`.

I check15 controls: protected producer output; wrong page version,
precision order, core range, odd band and selection volume; short/extra
page and input; input outside the disk; negative normalization; zero
pivot reciprocal; physical tape allocation during execution; and
protected core output. I mutate clones for malformed-packet tests,
preserve the original page/input, and execute a positive packet after
the rejections. These controls validate framing and ownership, not
arbitrary advice pages' mathematical correctness.

## Additional coverage

- `setup`:25 rational pairs, exact3-by-3 inverse/LU identities and complete
  record reversal preserving internal bit order.
- `convolution`: four actual signed Kronecker packets, cancellation, zeros,
  integer-grid data, strict coefficient separation and one final rounding.
- `exponentials`: seven encoded decay/scaled-growth enclosures against a
  separate exact-rational oracle. At P12,F2 the routine uses
  R148,J45,N58,k7 and stays inside the four-ulp allowance. I include zero,
  a one-unit positive Taylor term and continuing terms, and compare each
  shortened enclosure with a full-length directed reference.
- `interior`: complete q-factor preparation and two-convolution application
  at lengths3,3,1, with exact agreement to the pinned PR489 staged
  evaluator and separate dense exact inverse checks.
- `axis`: a full s8,t9,P16 global H, including beta4=-1/2,12 exact
  within-cell entries and four directed cross-cell entries. I verify
  coefficient intervals, reflected-weight reuse, the seam, strict row
  dominance and restoration.
- `boundary`: exact LU preparation and complete sequential rounded solves
  at lengths3 and1, including early/late zero padding and reuse.
- `consumer`: whole-consumer conformance with independent supplied-factor
  fixtures, nonzero couplings and both components. I keep this separate
  from the true-Gaussian producer joins above.
- `production`: encoded domain/locality checks at p16384,u32,d384. I derive
  w93,P536870912 and margin12781822672896, and reject seven malformed
  domains. This is metadata-only; I do not allocate those coefficient
  grids or halo payloads.
- `sources` and `budget`: complete source authentication, shared classes,
  acyclic actual child identities, binding controls, exact guard/packing
  arithmetic and the inherited Fourier-power comparison. Finite arithmetic
  controls supplement the universal argument in PROOF.md.

The Gaussian owners use FftWord's fixed crossover4096, so these finite
packets execute its actual Karatsuba branch. PR3787's retained tests
executed the FFT branch at widths17 and19 with its default16 crossover.
I retain that coverage boundary.

## Bounded-replay adjustment and limits

I stopped an initial s19,t20,P32 three-window fixture after it exceeded
600seconds in weighted exact rational elimination. I do not count that
run as a pass. I then cancelled the exact similarity weights during
Schur setup and inverted the old truncated Toeplitz blocks. I retained
the same old-H equation and chose the bounded cases above to cover
interiors, wrapping, clipped pieces and a C-selection gap. I make no
timing comparison across those different fixtures.

My first registered replay passed the first ten checks, then exceeded
the ownership command's 120-second allowance. I increased that allowance
to 240 seconds and reduced the joined-window allowance to 540 seconds.
I retain eight commands and a 1200-second sum of timeouts. I do not count
the timed-out replay as a pass; the public receipt records the final replay.

The first hosted run exceeded the numerical group's180-second allowance
during global-axis preparation. I then shortened each positive Taylor
sum when its encoded upper term reaches one work-grid unit. The remaining
tail is at most h/7; I retain the one-unit outward padding and explicitly
close the iterator. I also reuse weight/normalization pairs at reflected
indices after checking their equal squared offsets. PROOF.md covers
both arguments. I retain the same complete-window and ownership fixtures
and add the seventh coefficient case above. I rebalance the registered
allowances to210 seconds for numerical and300 for ownership, retaining
the540-second window allowance and1200-second total. The public receipt
records the final head's export and hosted verification.

I have not executed a production-size P=32768p packet, a complete Gaussian
expansion/compression tensor, or the CRT/integer theorem. I retain the
word recovery and analytic premises and leave the selected frontier
unchanged. The scoped proof and finite checks still need independent
human or formal-kernel review.

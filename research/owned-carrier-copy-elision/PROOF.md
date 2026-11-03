# Eliding one quarter-scaled owned copy

This construction and proof are produced by Nick Petalas. The input is
DreamingOfClouds's PR6621 native word at
`c51a142bb94c6d46ebee9a48c3f71cde8022da91`. Its native operations,
arbitrary-input interface and paid construction are credited premises.
The claim is exact equivalence of a new, shorter scalar program and a
strict reduction in its declared scalar allowance. No new kappa is claimed.

## Construction

Use zero-based indices in the source's 18,561-event program.

| Source event | Action |
| --- | --- |
| 9045: INIT 774 in frame 394 | Remove |
| 9053: ADD 774, 785, 1 in frame 394 | Remove |
| 9054: SCALE 774 by 1/4 in frame 394 | Remove |
| 9056: ADD 786, 774, 1 in frame 394 | Replace source by 785 and coefficient by 1/4 |
| 9058: ADD 713, 774, 1 in frame 394 | Replace source by 785 and coefficient by 1/4 |
| 9067: CLEAR 774 in frame 394 | Remove |

Every other event and every public boundary datum is unchanged. The
constructor checks that these are all uses of role 774 in this lifetime.
Role 774's later lifetime is retained. The new word has 18,557 events.

## Equivalence for arbitrary payloads

Carrier 785 reaches frame 394 at event 9052 and is unchanged throughout
both consumer reads. Let its value be `v` in any vector space over a field
where four is invertible. The old lifetime initializes 774 to zero, copies
`v` into it, then scales it to `v/4`. Its only consumers are the two displayed
ADDs. The new program adds `v/4` directly from 785 at both consumers.

All other registers therefore agree after each retained event. The old
private register 774 is unobserved except at those two reads, and is erased
before the window closes. Both programs agree on every remaining field at
the end of the window. Induction through the identical suffix proves the
same complete public and owned endpoint for every input.

Both new reads use an already live field in the same frame 394. No transport,
new independent input, dirty erasure or public-field overwrite is introduced.
The argument applies coordinatewise for every payload width. It uses no
special value of `v`, no zero-input assumption on public helpers, and no
commutation of chronologically separated native calls. It is a local program
equivalence proof; the predecessor endpoint theorem need not be replayed.

## Exact scalar bill

Use the predecessor's declared scalar allowance, with dyadic `q=n/d` in
lowest terms and positive `|n|,d`:

```text
INIT or CLEAR: 2
ADD or COPY:   2 (3 + bitlength(|n|)-1 + popcount(|n|) + bitlength(d)-1)
SCALE:         2 (|bitlength(|n|)-bitlength(d)| + [q<0])
```

The removed INIT, unit ADD, quarter SCALE and CLEAR cost `2+8+4+2=16`.
The two retained consumer ADDs each change cost from 8 to 12. Thus the
complete scalar allowance decreases by `16-2(12-8)=8`, from 137,866 to
137,858. Owned lifetimes decrease from 46 to 45. Peak live owned storage
remains 13; no reduction in the allocated register inventory is claimed.

The entire ordered MOVE list, including role IDs, source and destination
frames and private/public flags, is identical. The public initial/final
frames and all productive target data are identical. Consequently this
construction changes neither the recursive paid profile nor the productive
moment. The source's conditional kappa is a cited result, not improved or
re-certified here. A physical operation saving beyond this declared scalar
tariff would require the corresponding implementation bill.

## Verification and limits

The verifier constructs the new word without changing the retained input.
A rational sparse interpreter checks frame/lifetime legality and compares
all 799 by 799 coefficient positions of the two complete scalar maps.
An independently written dense interpreter checks the same 799-column
comparison modulo 65,537. This modular check corroborates the implementation;
the rational comparison and the local proof establish exact equivalence.
Neither interpreter asserts or rechecks the predecessor's claimed endpoint.
Six controls reject a wrong coefficient, wrong frame or omitted read at each
of the two new consumers.

This is a scoped scalar-program construction with a finite exact certificate.
It is not supplier admission, a paid-job reduction or a complete multiplication
theorem. Native all-column behavior, owned erasure, compiler closure,
precision/tape and analytic recovery remain the inherited obligations.
Independent human and formal proof-kernel review are unclaimed.

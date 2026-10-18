# P104 cross-incidence pooling reduces the three-target word to 91 helpers

An exact finite logical construction submitted for review. No new kappa is claimed.

Two correction groups can share a secondary fanout collector. The restored
three-target word of [PR2504](https://github.com/CrocSwap/integer-mult-bounds/pull/2504)
uses 92 new dirty helper lifetimes. Pooling its groups `{0,2}` and `{0,1,2}`
reduces that count to **91**, with all other insertions retained literally.
The new word has 4,852 events and 371 independent inputs. Two separate
interpreters check all 137,641 endpoint coefficients and every frame transition.

This answers the cross-group mixing question left open by
[PR2460](https://github.com/CrocSwap/integer-mult-bounds/pull/2460).
Its four-extra-collector theorem assumes incidence-separated groups. This word
changes that premise and uses three extra collectors overall. It does not
contradict the theorem and does not prove an unrestricted 91-helper minimum.
The other 101 targets still implement their original `G/2` updates.

## The pooled identity and its legal cuts

Write `S = I-G/2` on the frozen 104 ordered roots. Let A be the 14 sources with
incidence `{0,2}`, and let C be the eight sources with incidence `{0,1,2}` for
rows Y0/Y1/Y2. In both groups the nonzero correction coefficients are identical
across their incident target rows. Let

```
a = sum(s in A) S[0,s] x_s
c = sum(s in C) S[0,s] x_s.
```

Those groups must contribute `(a+c, c, a+c)` to the three targets. Rather than
separately duplicate `a` twice and `c` three times, duplicate `c` twice, reserve
one copy for Y1, combine the other with `a`, then duplicate `a+c` twice.
This needs two additional dirty collectors rather than three.

Let `H_t` be the frozen endpoint hyperplane of Yt, `J012 = H0 intersect H1
intersect H2`, and `J02 = H0 intersect H2`. Their exact dimensions are six and
seven, and `J012` is strictly contained in `J02`. Every C initial source line
lies in J012; every A initial source line lies in J02. Therefore all captures
and the following gather occur at original cut zero, before any source moves.

1. Capture each C source in its own arbitrary dirty helper at its initial
   line. Raise those eight helpers to J012 and gather their sum in one of them.
2. Raise the arbitrary dirty helper POOL1 from ZERO to J012 and add that sum.
   POOL1 waits there for eventual Y1 delivery.
3. Raise the original sum collector to J02. Capture all 14 A sources in their
   original acquisition helpers and raise them to J02. Add them into that
   collector, which now contains the `a+c` source row.
4. Raise arbitrary dirty helper POOL2 from ZERO to J02 and add the combined
   collector. The combined collector and POOL2 wait for Y0 and Y2 respectively.
5. At original cut 4058, raise each collector to its designated Ht, deliver,
   and raise it to FULL. All other pooled helpers have already reached FULL.
   Reverse all gather ADDs at FULL and subtract every captured source there.

The new helpers start with independent arbitrary dirt, not zero data. Before
any capture or movement, subtract from each Yt the exact dirty row its future
collector will deliver. This is legal in the ZERO frame. The old channel never
reads a Y register, so those offsets persist through it. The full replay checks
these offsets, inverse gather and final source cleanup on every dirty input.

For example, if `d_C` and `d_A` denote the sums of the initial acquisition dirt,
and `e1,e2` are the two new collector inputs, the three delivered rows are

```
Y0 receives d_C + d_A + c + a
Y1 receives e1 + d_C + c
Y2 receives e2 + d_C + d_A + c + a.
```

Their matching initial dirty compensation leaves exactly the desired source
contributions. Reversing the shears restores every collector and acquisition
helper. No new allocation, COPY, erasure or source mutation is used.

## Complete finite bill

The comparison is against PR2504 head
`9db4192bf3fd7f43c5f41ae040649067191682e0`, not against the separated 94-helper
initial-line construction. Its late-exclusive branch is unchanged literally.
The replacement touches only the 22 acquisition helpers and three extra
collectors belonging to the two pooled groups. They become 22 acquisition
helpers and two extra collectors.

| Added quantity | PR2504 | Pooled word |
| --- | ---: | ---: |
| Dirty helper lifetimes | 92 | **91** |
| Logical ADDs | 517 | **514** |
| Nested transports | 283 | **280** |
| Source reads, including cleanup | 180 | 180 |
| ZERO-to-FULL dimension-gap rank mass | 828 | **819** |
| Complete event count | 4,858 | **4,852** |

The new added profile is

`145 H1 + 37 H2 + 7 H3 + H4 + 8 H5 + 39 H6 + 43 H7`.

The exact difference is deletion of **H1 + H2 + H6**, with no increases at
other ranks. Thus the local transport bill decreases for any strictly positive
rank tariff. No numerical root calculation or substituted idle credit is
needed for this local comparison. Each new helper travels monotonically from
ZERO to FULL, so its dimension-gap charge telescopes to nine. The original
4,058 events, original paid profile and eight private-copy lifetimes remain
unchanged. [RESULT.json](RESULT.json) records the full comparison and controls.

These ranks are boundary progress, not recursive excess work. Helper lifetimes
are not a simultaneous physical stock bound. No favorable complete moment or
selected-frontier improvement follows from this partial invoice.

## Reproduce and coverage

Python 3.12, standard library, no network. Default replay writes nothing.

```sh
python3.12 -I -O -B research/p104-pooled-collectors/verify.py
python3.12 -I -O -B research/p104-pooled-collectors/independent.py
python3.12 -I -B research/p104-pooled-collectors/test_verify.py
python3.12 scripts/research_package.py --package research/p104-pooled-collectors
```

`build.py --out NEW_PATH` regenerates the full candidate in a new file. The
behavioral tests compare its entire parsed payload with CIRCUIT.json. Both
builder and verifier refuse to overwrite an existing requested output.

The primary interpreter uses sparse rational rows and explicit XOR subspaces.
The independent interpreter imports neither builder nor primary checker. It
uses dense quarter-integer rows, binary Gaussian elimination and a separate
240-root construction. Both replay the exact 92-helper predecessor and the
candidate. The primary also replays the original 280-input channel and compares
all unaffected correction events literally, with their original cut numbers.

Five primary controls reject omitted root fanout, secondary fanout, dirty
compensation, inverse gather and a wrong transport charge. The independent
interpreter separately rejects both fanout faults. Behavioral tests cover a
missing capture, illegal common frame, equivalent bases, complete regeneration,
read-only Git-free execution, source drift, missing or corrupted receipt, and
exclusive output. No independent human review or proof-assistant verification
is claimed.

## Limits

This is an exact finite logical/frame construction only. Native phases,
scalar/address lowering and physical copies of these new source reads remain
unimplemented. The old native channel does not automatically admit the added
word. Reverse-orientation admission, chronological owners, idle/residual
children, physical precision/tape, all-size lifting, the remaining 101 target
corrections and analytic transfer remain open. No selected cold replay or native
compiler replay is claimed. Frozen predecessors and selected-result.json are
unchanged.

## Open next questions

Can the remaining `{1,2}` group pool with this combined fanout to remove the
third extra collector? This would test a genuinely interacting cross-incidence
schedule, not the separated-group rank bound. First derive all three required
source rows at each branch and check whether a two-extra invertible dirty
schedule can respect the J012/J02/J12 inclusions. The incomparable J02/J12
branches and restoration are the current blockers; no optimum is claimed here.

Can this exact 91-helper word receive native transport and scalar/address
lowering? First compile its 280 added transports against the canonical charts
and bind actual source reads, then check full arbitrary-input columns. A
complete chronological owner/idle invoice is still needed before any supplier
moment comparison. Structured next questions and stop rules are in TASK.json.

## Sources and credit

Scientific base is canonical main
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
Source commits, Git blobs and hashes are in SOURCES.json. The retained PR2504
circuit is byte-for-byte, SHA256
`96459a07c79fd1b711af6343bc9c004d91e28cd0da3306c290cff657082b110d`.

Credit CubeJerry / PR2504 for the late-exclusive branch and full 92-helper
construction; ywz65 / PR2460 for incidence groups, the restricted collector
bound and the cross-group handoff; Ross Richardson / PR2445 for two-target
sharing and its dirty two-total shear; commdata2338 / PR2393, Hiroki Kumazaki /
PR2353 and Philippe Van Velzen for the acquisition/relay model; Rohan Arun /
PR1972 for the original channel; Chafik Boukhalfa / PR1991 for native realization;
Adam Gall / PR1940 for the schedule; Josie Elliston / PR1071 and Ali Romman /
PR1125 for the fixture/carrier lineage, with PR968/717/446/595/620 retained.
The predecessor source is Apache-2.0. New files use the repository's Apache-2.0
license. No maintainer acceptance or full supplier admission is claimed.

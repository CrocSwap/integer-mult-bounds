# P112 sparse lift: equality rigidity and the sharp active-term gap

**Scoped structural refinement; no new kappa.** For the fixed P112 coordinate
frame plus its three-coordinate-sum ninth normal, the only minimum-cost
per-root shifts are the four global functions `t=0,r0,r1,r2`. Each has exactly
eight active terms and copy cost 64. Requiring **all nine terms active** gives
the sharp minimum **65**, attained by `(8,8,8,8,8,8,8,8,1)`. The classification
allows arbitrary complex shifts independently on all 112 rows.

**The lower bound 64 is prior work.** Mihir Srivastava's
[PR845](https://github.com/CrocSwap/integer-mult-bounds/pull/845), retained in
`research/p112-single-lift`, already proves it for arbitrary real ninth normals
and corrections with the eight coordinate readers fixed. This package narrows
to one specified normal and adds its complete equality classification and
sharp all-active gap, using a different finite compatibility certificate. It
does not claim a new copy floor or priority over that obstruction. The final
full overlap refresh found this incorporated predecessor; the initial open-PR
scan alone had missed it.

The normal frame is fixed; it differs from the A8 simplex in PR1248/1304.
Joaqcoo's PR1224 supplies the general one-sided representation context, not a
new cost-64 question in this already excluded real subfamily.
[PROOF.md](PROOF.md) gives the universal argument; [CERTIFICATE.json](CERTIFICATE.json)
records the complete finite premises and witnesses.

## Reproduce

From the repository root, Python 3.12 and standard library only:

```sh
python3.12 scripts/research_package.py --package research/sparse-redundant-decoder
```

Expected: six passing package-test groups, followed by `PASS_REGISTERED_RESEARCH_PACKAGE research/sparse-redundant-decoder outcome=completed`.
The direct mathematical command is:

```sh
python3 -I -O -B research/sparse-redundant-decoder/verify.py
```

Expected: `PASS_SPARSE_REDUNDANT_DECODER planes=32385 single_vectors=765 minimum=64 all_active=65 equality_shifts=4 controls=6 no_new_kappa`.

The primary check reconstructs the standard E8 roots and exhausts **32,385
binary deficiency planes** plus **765 single functions**. The separate checker
reconstructs signed affine planes of F2^3, switches to nine-coordinate code
functions, and computes compatibility by equation rank. It imports no primary
or predecessor implementation. Both check all entries of the five sharp
witnesses. Six semantic controls and receipt/source corruption, omitted receipt,
optimized execution, regeneration and read-only relocation tests delimit the
claim. See [VALIDATION.md](VALIDATION.md) for actual runs.

## Cost and scope

The best ratio here is `64/112=4/7`, exactly the coordinate decoder's ratio;
all-nine-active redundancy costs `65/112`. Consequently this extra normal
cannot save copied information even granting all additional helper, source,
frame, restoration, hosting and recursive expenses zero. This is a copy-budget
screen, not a complete realized supplier or a theorem about every moment with
that copy sum. No changed paid histogram, complete recurrence or new kappa is
produced.

Not covered: different coefficients/normals, other punctures, more terms,
masked identities and shared-copy billing. All selected PR1094 all-size/compiler,
common-label/mutable-source, hosting, precision/tape and analytic conditions
remain. The selected record is unchanged at conditional kappa
`0.001672660197076918`; its actual source manifest, construction, review and
`make frontier1094-verify` command were followed for orientation. That complete
supplier cold replay, native admission, Lean and independent human review are
not claimed.

## Assignment, overlap and credit

Base `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`; OS-random seed **40**, original
structural-decoder track. The three candidates and the full live overlap scan
are recorded in [TASK.json](TASK.json) and [OVERLAP.json](OVERLAP.json).
The new claims are equality rigidity and the all-active cost-65 gap for this
fixed normal. No priority over PR845's cost-64 obstruction, PR1224's general
one-sided normal form or PR1248's deficiency method is claimed. The all-active witness row is `seed mod 112`.

Credit **Mihir Srivastava / mihir-s-05 / PR845**, head
`125ce25bdae421627b56077adc14940c2d0aa52f`, for the fixed-coordinate single-lift
obstruction and annihilator approach; **Joel Pulikkan / GamingPuzzled / PR620**
for the prior coordinate cost64; **joaqcoo / PR1224**, head
`00e6ed0810b8ebc7f6133e2c036d0f1c9a3a4162`, for the overcomplete normal form,
ratio-class compatibility and open residual class; **mightyOil / PR1248** for
the A8 binary-plane method; **commdata2338 / PR1304** for the distinct A8 P112
matching-frame result; **DreamingOfClouds / PR446,717,595** for the cost model;
**themilkman216 / PR968** and **woklerx / PR1077** for the eight-term floor.
The E8 geometry is classical. The selected supplier lineage, including Rohan
Arun, Jeremy Kothe, Hao Yan and eumemic, retains its attribution.

Prepared for **Philipp / @mightyOil** with substantial **OpenAI Codex GPT-6 Astra**
assistance in research, proof, both implementations, testing and writing.
Separate implementations are not independent human review. Apache-2.0.
Predecessor files and `upstream/` remain unchanged. [SOURCES.json](SOURCES.json)
records exact live-source hashes and predecessor pins.

## Open next questions

- Which other specified ninth normals admit all-nine-active equality at64?
  First vary the three nonzero coefficients and recompute the two compatibility
  lemmas. PR845 already excludes a lower real copy budget; the open question is
  equality and the active-term gap. The dimensions here need not be preserved.
- Can an explicit masked or shared-copy implementation beat the separate-term
  cost on the same geometry? First give a legal decoding and delivery identity,
  then price source accesses, helpers, restoration and recursive children. The
  model change needs a physical interface proof; an algebraic support alone
  does not provide one.

Structured questions, blockers and the bounded stopping rule are in TASK.json.

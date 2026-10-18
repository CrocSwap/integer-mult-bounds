# A fanout batch with no dedicated connector

**Recursive-interface research construction; no new kappa.** For at least two
outputs, the exact update `y_i += A_i B x` can borrow an output as its connector.
All initial data may be dirty. The batch uses **4 B calls and two calls per A_i**,
and no additional length-L connector row. This is a scratch/work tradeoff against
CubeJerry's [PR889](https://github.com/CrocSwap/integer-mult-bounds/pull/889),
whose dedicated-connector batch uses two B calls.

The seed-59 example has three outputs, six factors in B, and 5, 3, 1 factors in
the A_i. Balanced binary child lowering gives:

| Explicit schedule | Complete leaf calls | Extra dirty rows | Total data rows |
| --- | ---: | ---: | ---: |
| Separate echoes, each borrowing another output | 318 | 3 | 7 |
| **Output-borrowed batch** | **238** | **3** | **7** |
| PR889-style dedicated-connector batch | 158 | 4 | 8 |

Thus batching saves 80 calls against the equal-scratch comparator. Removing the
dedicated row costs 80 calls against the dedicated batch. The new word does not
dominate that batch. Counts are for full length-L calls, not measured runtimes.
All outputs are exclusively held during execution; intermediate values are not
observable. Child scratch excludes **every other output**, even temporarily.

## One-command reproduction

From the repository root, Python 3.9+ and its standard library suffice:

```sh
python3 -I -O -B research/output-borrowed-fanout/verify.py
```

Expected:

```text
PASS_OUTPUT_BORROWED_FANOUT cases=41 leaves=318->238 private_rows=3 dedicated_rows=4 census=224
```

`python3 -I -O -B research/output-borrowed-fanout/test_package.py` also checks
offline relocation, exact regenerated **decompressed** certificate payloads,
the complete evidence receipt, and eight package corruptions. The compressed
container is not a mathematical identity. To regenerate separately:

```sh
python3 -I -B research/output-borrowed-fanout/build.py --out /tmp/output-borrowed-certificate.json.gz
```

## Exact scope and evidence

[PROOF.md](PROOF.md) proves the identity, the sharp `2k+4` query minimum in a
specified output-to-output unit-generator alphabet, and the complete local
resource recurrence. This minimum is not a lower bound for arbitrary circuits,
scalar copies, direct product calls, or a fixed matrix representation.

[CERTIFICATE.json.gz](CERTIFICATE.json.gz) contains literal macro and leaf
words for 40 declared grid fixtures plus the seed-selected example. The verifier
does not import the generator. It replays free noncommutative polynomials and
checks every complete child boundary with arbitrary independent dirty symbols.
It separately checks exact dense integer matrices in dimensions 1, 2, 3,
including every prefix's conservative width and literal inverse. Both resource
prices and the one-tape travel invoice are independently recomputed.

For two outputs, the written degree argument reduces **all** minimum words to
40,320 permutations of eight distinct signed queries. Full free-polynomial
replay finds 224 correct words. This finite classification supports the general
written proof; it is not proof-assistant verification of multiplication.
Deliberate missing restoration, wrong sign, factor reversal, source/row and
invoice defects reject. A rounded nonlinear control has exact reversal but a
dirty-dependent output, so linearity is an explicit assumption.

The domain is fixed at `k=2..6`, `|B|=1..8`,
`|A_i|=1+((|B|+3i) mod 5)`, pivot `59 mod k`, plus the displayed seed fixture.
There is no adaptive search or claim that this class is globally optimal.
The experiment stops after that domain and the complete two-output census.

Base: `bbc600db2fc15007b7c914f4f2b2ed55fa909c87`.
[SOURCES.json](SOURCES.json) pins the selected context and exact predecessor
commits/blobs. [NOTICE.md](NOTICE.md) credits predecessor work and discloses
substantial OpenAI Codex assistance. [CLAIM.md](CLAIM.md) records scope selection;
[VALIDATION.md](VALIDATION.md) records the final checks and publication status.

The base's selected PR942 conditional exponent is
`1661960547713947/10^18`, with the unchanged PR589 bit supplier. No native
supplier is instantiated here. Common labels, physical frames/owners,
whole-call hosting, efficient source/tape access, preparation/precision,
all-size compilation and outer analytic transfer remain obligations.
`upstream/`, the selected certificate and existing source packages are unchanged.

# The one-scalar chart-282 reader cut on #7830

After the two funded retargets described below, withdrawing rational slots
`88960` and `90369` at chart 282 leaves three independent local arrivals.
The five protected reader rows raise that rank from **3 to 5**. Readers
`89198` and `91110` supply the two independent directions. An arbitrary
replacement payload at `88960` can supply at most one rational scalar, so
this repair is excluded with every other arrival and protected row fixed.

## Pinned word and observation

The exact graph is the rational word from PR #7830 at
`14c74c6a67108f675ac1196a5f2415ead0920e71`. The gzip SHA-256 is
`1b1b3294e86979f1f41076fb056f3c0a08ace6df7bf80f2886bc579a22962f4b`
and its canonical JSON payload SHA-256 is
`7660985e0b618cdbee13e4190a4c6d5f91fbdf01a8f7a5186fdde8b980c19b48`.
The application reports layout
`f7de788c4a559282d35a9fce42f841a0e8de5a4015db871e718f9245569b0aa7`
and 48-call caller
`156fdf3a4a129b39225fd6ca51011de27974d7f104e8b04907c17ed5344bc858`.
[Word](https://github.com/CrocSwap/integer-mult-bounds/blob/14c74c6a67108f675ac1196a5f2415ead0920e71/research/p104-chart306-chain/DOUBLE-CANDIDATE.json.gz) · [Application](https://github.com/CrocSwap/integer-mult-bounds/blob/14c74c6a67108f675ac1196a5f2415ead0920e71/research/p104-chart306-chain/DOUBLE-APPLICATION.json)

On the three-coordinate probe from #7795, set `x674 = x722 = 1` and
`x1288 = -1/845660160`, with other public inputs zero. The rational word
has 901 retained chart-127 arrivals and ten then-ready chart-278 source
atoms that vanish on this probe. Old slot 88 and terminals 155442 and
155490 evaluate to one. Paid grade-three slot 90369, a 3 → 282 transfer
at zero-based clock 297, evaluates to **1865/148**. Its original direct
readers are `91110`, `98703` and `94251`.
[Predecessor probe and context](https://github.com/CrocSwap/integer-mult-bounds/pull/7795)

Pulling the exact rational forms back through the literal schedule gives
`terminal156056 = x1288` and `old88 = old95914 - 845660160*x1288` over
all 1,289 public input axes. Perturbing the coefficient by one leaves a
nonzero residual. This identity permits the proposed direct outlet to use
the old 95914 source form and one causal copy of `x1288`.

## Cut and charge

The two-retarget contract sends `x1288` on 94019 from chart 3 to 278
and replaces the old outlet path with grade-seven 88 from 278 to 127.
It retires 95914. It redirects 90369 from chart 282 to chart 304 with
the old 94019 form. The operands are already present at the proposed
senders, and the redirected 90369 arrives before both old 94019 readers.

Hold the three legs 88908 → 88955 → 88960 at their original grade-one
routes while allowing their payloads to change. The receiver test grants
an arbitrary new scalar on the last leg, even if the original upstream
stock could not supply that scalar. Any source-side or side-reader
constraint would restrict the allowed payloads further.

Removing old 88960 and 90369 leaves arrivals `88959`, `90605` and
`90604` at chart 282. There is no public input at that chart and there
are no additional unchanged arrivals, even if clock restrictions are
relaxed. All three retained arrivals strictly precede all five demands.

| Protected reader | Old clock | Rank after adding its old row |
| --- | ---: | ---: |
| 89198 | 2826 | 4 |
| 91110 | 2827 | 5 |
| 98703 | 2828 | 5 |
| 91131 | 2995 | 5 |
| 94251 | 2996 | 5 |

The replay derives the complete protected roster from the literal readers
of the two removed slots and computes the ranks on their exact public-input
rows. Adding either old ingress alone raises the available rank to four.
Adding both restores rank five and spans all five readers. Suppressing the
two original sends also changes protected reader values on the probe.

The original replaced grades are `2, 3, 3, 5` and the proposed grades are
`2, 3, 7`. With productive grades held, the 48-call paid delta is
`{3: -48, 5: -48, 7: +48}`. For the tariff $P_g=g^{1-\kappa}$, the gross
nominal saving is `48*(P3 + P5 - P7)`, at most
`48.4218097282314662393658762` at κ = `0.003889928046155`. One further
unpaired grade-one job per call would leave at most `0.4218097282314662393658762`
of credit before covering the complete invoice. The cut prevents earning
the nominal saving and gives zero κ credit.

## Reproduction

Run with Python 3 and the standard library, using the public commit-pinned
word as the only input file.

```sh
src=https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/14c74c6a67108f675ac1196a5f2415ead0920e71
curl -fLsS "$src/research/p104-chart306-chain/DOUBLE-CANDIDATE.json.gz" -o word.json.gz
python3 -B replay.py word.json.gz > replayed.json
diff -u RESULT.json replayed.json
```

The scope is the stated fixed-stock receiver cut on one rational native
word, with the published caller multiplicity inherited for pricing.
A repair with additional independent ingresses, different held stock or
changed protected observations has different cut and complete application
obligations. The replay qualifies the local witness and grade delta.
Credit Clear1nsight's #7795 probe, #7830 word and the predecessor
contributors named in those packages. OpenAI Codex assisted with the
constructions and independent computational checks.

# R438 bit supplier with PR3190's idle-remainder donors: the complex side binds again at κ = 0.001734770557111513160495 − 10⁻⁴⁶ − 10⁻⁷⁰

**Author-checked conditional composition; not maintainer-reviewed.** The selected record on
`main` is still #1094. This package stacks on the open PR3190
(`research/rank7-idle-remainder-donors-t740`).

| | complex endpoint | bit endpoint | binds | κ headline |
|---|---|---|---|---|
| PR3190 | 0.0017347705571115131604951 | PR589 0.001733427039589844234749 | bit | 0.001733427039589844234749 − … |
| **this** | 0.0017347705571115131604951 | **R438 0.001734846264120199151475** | **complex** | **0.001734770557111513160495 − 10⁻⁴⁶ − 10⁻⁷⁰** |

The gain is **+1.3435e-6 (+0.0775%) over PR3190**, +4.58e-6 over PR3184 and +4.99e-6 over
PR3148.

## Idea

PR3190's idle-remainder exchanges pushed the complex root of PR3133's words above the PR589 bit
saving, so its κ was capped by the bit supplier. A stronger certified bit supplier already exists on
main.

The R438 word:

- comes from Ali Romman's PR1043, with helper 470 deleted;
- adds Sagar Thakrar's PR2423 transport and optimal re-hosting;
- has a complete native, parent and hosted replay in `research/r438-native-rehost`.

Its bit endpoint is 0.001734846264120199151475, accepted at c and rejected at c + 10⁻²⁴. That is
above the new complex root, so with R438 the complex side binds again.

## Verification

`verify.py` uses the standard library only and runs in about 1 s:

1. **Complex endpoint.** It recomputes PR3190's complex root bracket on its declared complete
   profile, with its own interval arithmetic at 10⁻⁷².
2. **Bit endpoint.** It re-derives the R438 endpoint from the certificate's own bit profile:
   m = 64, live = 28,416, with the 10⁻¹⁶·32m² bad-edge fallback envelope. The endpoint is accepted
   at c and rejected at c + 10⁻²⁴.
3. **Composed κ.** It computes `κ = min(floor₂₄(complex), floor₂₄(bit)) − 10⁻⁴⁶ − 10⁻⁷⁰`, checks it
   equals CLAIM.json, and gates it against PR3148, PR3184 and PR3190.

Three mutation controls are rejected: the complex next grid point, the bit next grid point, and
the PR589 endpoint on the R438 profile. PR3190's moves and profile are checked by its own
registered verifier.

```sh
python3 -B research/rank7-idle-donors-r438-bit/verify.py
```

## Scope

**Conditional on two unreviewed claims:**

- PR3190 and its stack: PR3148, PR3133, and the hosted-remainder donor hypothesis.
- R438: PR1043 is open, and `r438-native-rehost` does not promote a selected supplier.

The R438 bill fits the inherited row bound: row coefficient 18,355 < 20,161, maxchild 42 with
`2·42² < 64²`.

The T74 outer ledger currently pins the PR589 bit constant, and only uses it to assert
`complex < bit`. With R438 that assertion holds directly, but the release needs the constant
re-pinned. All inherited all-size, compiler, realization, precision and analytic obligations
remain.

## Open next questions

- **Does the T74 outer release accept R438 in place of PR589?** First step: rerun PR3148's outer
  release with the R438 bit endpoint and its finite bill. Blocked by: PR1043 is open, and the outer
  ledger pins PR589.
- **Can the complex side close the remaining 7.6e-8 gap to the R438 endpoint?** First step: drain
  more of the 149,514 rank-1 remainders that are blocked by commuting legality, or widen the
  receiver set.
- **Bit side.** R438's own idle remainder (`{34:32, 42:320}`, cap 45 at m = 64) admits the same
  axis-exchange question, should the bit side bind again.

## Credit

- Ali Romman (PR1043): the R438 word.
- Sagar Thakrar (PR2423): transport and re-hosting.
- commdata2338 (PR2653): native emission.
- The `r438-native-rehost` authors.
- PR3190 / PR3184 and their credits: PR1252 Gonzalo-Mier; Guéorgui Maissouradze; PR3148 Jeremy
  Diviney; PR3133 dcharb78; PR2979 Marius-Paul Dumitrean.
- DreamingOfClouds and eumemic (PR589/PR555).

Prepared by Rohan Arun. Done with help from **OpenCode (Space bunny free)**, and with Anthropic
Claude assistance. Apache-2.0.

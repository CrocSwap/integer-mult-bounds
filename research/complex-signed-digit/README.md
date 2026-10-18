# Signed-digit preparation in the selected JP8 supplier

**Finite local circuit improvement / research note. No new kappa.**

Signed-digit numerator preparation saves **3,276 real-component primitives in
each orientation** of the selected JP8 supplier. It changes 250 additions per
orientation. Every source read, doubling, signed accumulation, halving and
scratch clear is charged. The original initial clear and leading source add
are retained.

| JP8 orientation | Original real primitives | With numerator recoding | Saved |
| --- | ---: | ---: | ---: |
| Forward | 257,232 | 253,956 | 3,276 |
| Backward | 257,280 | 254,004 | 3,276 |

These are scalar primitive counts, not measured runtimes or total recursive
costs. The paid child profile remains
`{1:2512, 2:400, 3:448, 4:160, 5:70, 6:8, 8:8}`.
The source/helper count, scalar macro word, frames, adapters, phases and
restoration boundaries are unchanged. The selected conditional result remains
`kappa = 51110230636731/31250000000000000` from #626 with #543.

## Reproduce

From the repository root, with Python 3.11 or later and the standard library:

```sh
python3 -I -B research/complex-signed-digit/verify.py
```

Expected:

```text
PASS_COMPLEX_SIGNED_DIGIT jp8 additions=250+250 real_saved=3276+3276 columns=716 controls=9
```

The command is offline and writes no files. It checks all input byte and Git
blob pins, also checks decompressed payload hashes, replays the circuits with
an exact rational interpreter, reconstructs the 716-column scalar projection
in both orientations, recounts costs and intermediate envelopes, and compares
the complete result with [EXPECTED.json](EXPECTED.json).
`--report` performs the same calculations and controls and prints the receipt
without comparing it to EXPECTED.json.

The executable recipe is [lowering.py](lowering.py). For every scalar add
`t += q*s`, `circuit(q)` returns a literal real primitive list over distinct
registers `t`, `s`, and private `w`. Apply that list to both real components,
in the original event's frame. Other scalar and non-scalar events stay intact.
The receipt hashes the ordered list of changed event indices, exact rational
coefficients and primitive lists, separately for each orientation.

## Cost and boundary argument

Write a nonzero dyadic coefficient as `q = sign * a / 2^k`, with positive
integer `a`. The original circuit costs

`3 + floor(log2(a)) + popcount(a) + k`

real primitives per component. The three fixed operations are initial scratch
clear, signed target accumulation, and final scratch clear. Binary numerator
preparation accounts for every doubling and source add. The proposed circuit
uses most-significant-first digits in `{-1,0,1}` and costs

`3 + (digit_length - 1) + nonzero_digits + k`.

It uses signed digits only when this complete cost is strictly smaller;
otherwise it emits the original binary circuit. This comparison includes an
extra leading digit when recoding introduces one. No minimal-circuit or global
optimality claim is made.

The recoding step chooses `d=0` for even `a`, `d=1` for `a=1 mod 4`, and
`d=-1` for `a=3 mod 4`, then replaces `a` by `(a-d)/2`. Each step preserves
the represented integer and decreases it until zero. Reading the resulting
digits backwards and applying `w <- 2w + d*s` therefore produces `a*s`.
The `k` halvings produce `abs(q)*s`, the single final signed accumulation
produces `t+q*s`, and clearing `w` removes the private value. The initial
clear makes the circuit independent of arbitrary incoming scratch. The
source is never written.

All operations before target accumulation affect only scratch, at the
existing scalar event's frame. Thus the replacement has the same complete
three-register boundary map. Substitution through the ordered program
preserves every scalar boundary on arbitrary correlated input, including
dirty helper restoration. It inserts no frame change, child call, source
adapter, centre copy, or residual wrapper. It uses the same private coefficient
stream as binary Horner. The exact three-column interpreter checks this
identity for every coefficient that occurs, with explicit private input.

## Intermediate magnitudes must be repriced

Signed recoding sometimes reaches `a+1` before subtracting the source. The
exact maximum scratch coefficient for the signed-digit numerator is `a+1`
when `a=3 mod 4`, and `a` otherwise. To prove it, write `a=2m+d`. The
most-significant-first execution computes `m`, doubles it, then adds `d`,
so `M(a)=max(M(m),2m,a)`, with `M(1)=1`. Induction gives the stated bound;
every intermediate coefficient is nonnegative. Halving cannot increase it.
Binary circuits retained by the cost comparison have maximum `a`.

The checker interprets all primitive prefixes to obtain the actual maximum,
then multiplies it by the source's exact rational L1 envelope at that event.
Macro-boundary envelopes use `env[t] + abs(q)*env[s]` in both versions. This
uses the exact same-source correlation inside coefficient preparation; it
does not replace subtraction with an unsigned accumulation. The syntax check
rejects any extra target excursion that would invalidate this argument.

There are 100 changed macros with scratch overshoot per orientation. The
forward maximum increases at zero-based event 27551,
`L353 += (-34078711/4)*L355`, frame 1:

| Envelope | Exact value |
| --- | --- |
| Original forward | `4536094588619580433782972610869617/281474976710656` |
| New forward | `567011840215747740443164774152233/35184372088832` |
| Backward, both circuits | `16753412757380464429924108070201913461/8388608` |

The forward inflation factor is exactly `34078712/34078711`. Its bit bound
stays 64; backward stays 101. Both fit the retained 192-bit local allowance.
The old exact forward prefix receipt must be updated if this lowering is
integrated. This package does not overwrite that receipt.

## Completed coverage and limits

This is deterministic synthesis over the two pinned JP8 programs, not a
random or open-ended search. Assignment seed 36 selects JP8 as recorded in
[CLAIM.md](CLAIM.md). The domain is all 27,909 events per orientation, including
22,693 scalar events and 439 distinct signed addition coefficients. The
stopping rule is completion of both programs; all were processed. Exactly
188 distinct signed coefficients per orientation receive cheaper circuits.
The largest absolute coefficient is 67,108,862. The per-component saving is
at most 22 primitives per changed macro.

Nine controls reject a wrong signed digit, omitted initial or final clear,
omitted target accumulation, omitted halving, nondyadic and zero coefficients,
an undercharged scratch peak, and an endpoint-neutral target excursion.
The full scalar projection check is an additional exact finite check. It
does not independently replay Clifford amplitudes, geometry, or physical
hosting. Those operations are inherited and unchanged.

No selected emitter, global invoice, certificate, or `upstream/` file is
modified. This does not supply new owner maps or a revised asymptotic
recurrence. All-size compilation, common-label and mutable-basis realization,
pooled hosting, residual normalization, rounded arithmetic and precision,
tape/exact recovery, analytic transfer and the bit H1-H5 assumptions remain.
Finite replay is not a formal proof of the full multiplication theorem.

## Provenance and concurrent work

Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
The selected #626 source head is `660de893d27bb7abd1d5b01b1640207528a5c851`,
with #622 at `f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`.
[SOURCES.json](SOURCES.json) pins every consumed repository input by SHA-256
and Git blob, with additional decompressed payload pins for gzip artifacts.
The retained compressed inputs are immutable sources; no recompression is
used as a mathematical comparison.

Credit to Jeremy Kothe and the Claude Code contributors for #622's supplier,
Chafik Boukhalfa for #626's packaging and owner repair, icekylinx for the
#425/#433/#531 scalar-emission lineage, DreamingOfClouds for the native and
emitted verification lineage, Dugongue for the scalar and rank-sector work,
and eumemic for the selected #543 bit supplier and earlier #411 dyadic
lowering. Their original notices remain in the source packages.

Concurrent [#696](https://github.com/CrocSwap/integer-mult-bounds/pull/696),
head `5a3f983715027c4fd83f50bc9001d4b18463bed1`, removes the initial
clear/add pair in favor of a copy and specializes unit coefficients. It
retains binary digits for non-unit numerators. This contribution retains
that original pair and all unit circuits to isolate the additional
numerator-recoding saving. Copy initialization would reduce binary and
signed-digit costs equally, so the 3,276-primitives difference per orientation
persists under composition, but this package does not implement or certify
that combined package. #681 changes a factory macro word; #687 examines a
K-triangle frame neighborhood. None is an implementation dependency.

Concurrent [#722](https://github.com/CrocSwap/integer-mult-bounds/pull/722),
by @ellipsi2 at `a0766ab0fab379e1997fadc3ca157578d57986c1`, arrived between
the final overlap snapshot and submission. It shares binary-Horner preparation
across forward cleanup runs, changing private-work clearing to block boundaries.
This contribution recodes individual numerators and preserves clearing after
every macro. It also saves work backward, where #722 reports no eligible runs.
No combined saving is claimed without a composed recount. #722 is credited
related work and is not imported or independently verified here.

Prepared for **Sagar Thakrar, @thakrarsagar**, with substantial **OpenAI Codex
assistance** in research, code, proof analysis, verification and writing.
A separately delegated Codex worker independently checked the cost census
and prefix calculation. That is AI-assisted cross-checking, not independent
human review. New material is under the repository's Apache-2.0 license.

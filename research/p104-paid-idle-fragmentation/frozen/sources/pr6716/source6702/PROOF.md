# Splitting a public helper register: exact invoice delta

## 1. Source and what changes

The comparison is PR6621: the PR6551 caller (the PR6545 Gaussian retirement
and the PR6398 mixed root with child trees `(7,2,5,4)`) with the PR6621
native word, itself the PR6529 word with three compensated rewrites. The
caller, the trees, the dual pairs and the retirement proof of PR6551 are
unchanged and retained in `source.tar`. In particular the unchanged prefix
through event 328 and the equal-target argument of PR6551 section 2 apply
without modification, because the caller sees the native word only through
its public boundary.

Only the native word changes, by one exact rewrite with its own
compensation (README.md gives the events).

- Public helper register 607 is cut at frame 115: `final[607]` changes from
  127 to 115.
- Its tail, the frames 115 to 127, moves to a new public register 770 with
  `initial[770] = 115` and `final[770] = 127`. The verifier requires every
  other initial and final frame to be unchanged apart from the shift of the
  owned registers by one place, and the other fields of the word to be equal.
- Three compensating ADDs are placed in frame 3 at the start and three in
  frame 127 at the end.

The verifier regenerates the PR6529 word from its retained construction and
compares it with `BASEWORD.json.gz` before it substitutes `WORD.json.gz`. The
edited word is then replayed against all 800 columns, the owned lifetimes (47
lifetimes, peak 14), the helper maps, the absolute phases and the 7,488
caller contacts.

## 2. Exact profile delta

Let H_r denote one Gaussian target or paid job of rank r. The native word is
called 18 times. From the replay in RESULT.json the edited word's local
profile differs from the PR6621 word's as follows, per call.

```text
paid    {2:+1, 4:+1, 6:-1}
targets {4:+1, 5:+1, 9:-1}
```

One rank-9 helper target is replaced by two targets of ranks 4 and 5, and
one rank-6 paid job by two paid jobs of ranks 2 and 4. Each replacement
preserves the rank mass (9 = 4 + 5 and 6 = 2 + 4). The complete invoice
changes by 18 times these counts:

```text
Delta T = 18 H4 + 18 H5 - 18 H9,
Delta P = 18 H2 + 18 H4 - 18 H6.
```

The caller side of the invoice is identical, so these are the only changes
against PR6621. The checks in `pricing.py` confirm that the complete profile
is exactly the PR6621 profile plus this delta: productive fields rise from
13,756 to 13,774, paid jobs from 67,042 to 67,060, and the target minus paid
rank mass stays 760 (each of the two masses is unchanged per call).

## 3. Why the gain is positive

The signed gain is `Delta(T-P) = Delta T - Delta P`:

```text
Delta(T-P) = 18 * [ (H5 + H6) - (H2 + H9) ].
```

Take `H_r = r^t` with `0 < t < 1`. Then `f(x) = x^t` has the strictly
decreasing derivative `f'(x) = t x^(t-1)`. Hence

```text
(H6 - H2) - (H9 - H5) = integral over [2,6] of ( f'(x) - f'(x+3) ) dx > 0,
```

which is `(H5 + H6) - (H2 + H9) > 0`. This is an exact all-exponent
comparison. It does not depend on the tested saving.

Equivalently, the pair of ranks `{2, 9}` has the same sum 11 as `{5, 6}` and
majorizes it, so every strictly concave sum is larger on `{5, 6}`: the
gaining side holds two jobs of middle rank instead of one short and one long.

## 4. Costs that are charged

The new word has 18,577 events (16 more than before). The owned inventory
has 29 labels and 47 lifetimes with peak 14, there are 771 public registers,
and the local scalar allowance is 137,990 (was 137,866). The rank mass of
local paid and target jobs is 5,924, as before. The full ordinary-work upper
bound stays below the retained 10^9 allowance. The edit adds no unpaid
channel, helper, copy or restoration. The erasure obligations are those of
PR6621 (one shadow register, erased in frame 127 while nonzero, covered by
the same `owned_erasure` assumption), renumbered by the shift.

### Declared package-local bounds

Two inventory literals of the retained local and forward replay sources
bound the word. They are verifier literals from earlier packages, not SPEC.
They are changed by exact text replacement, each required to occur exactly
once in each unpacked source:

```text
767 <= public <= 770   becomes   767 <= public <= 771
0 < peak <= 13         becomes   0 < peak <= 14
```

The edit needs the first because it adds a public register to the 770 of the
base word, and the second because the owned peak of the edited word is 14.
The retained sources are not otherwise changed.

## 5. Conditional numerical result

The new claimed saving is 0.00329760. The tested saving is 0.003297605. Two
rational engines certify a positive complete moment at the tested saving and
both signs of the raw root enclosure in RESULT.json. The raw crossing is
0.0032976213479979, above PR6621's 0.0032970138574525 by 6.075e-7. A
negative derivative bound gives a unique crossing below the retained BIT
cap. Both engines reject the full PR6621 invoice at the new claim.

The retained completion tails, the integer compiler threshold and all 54
strict plus four functional outer predicates are evaluated with the new
profiles. The completion ratio `delta` is enclosed in
`(0.970282747194658038492971336484, 0.970282747194658038492971336485)`.
As in PR6551 and PR6621, the source tail decay 31/32 is below it, and the
decay 97/100 of PR6621 is now below it as well, so the decay of this package
is 33/34 = 0.970588..., with reserve 10^(-27) at power 1920. The strict
checks are:

- `delta` upper bound 0.970283 is below 33/34 (the charged ratio test);
- `delta` lower bound exceeds 31/32, so the source decay still does not fund
  the tree;
- `gamma`, enclosed near 0.9206, and `alpha`, below 1 minus the reserve, are
  also below the decay;
- `(33/34)^128 < 1/16` (about 0.0219), the block estimate used for power
  1920 = 15 * 128.

The tail decay enters only these tail estimates. It does not enter the
crossing, so the claimed κ does not depend on it. The conditional bound has
the same form `O(n (log n)^(1-kappa))` with `kappa = 0.00329760` under the
five source framework assumptions.

No global optimum over words or callers, unconditional multiplication
theorem, independent review or selected-frontier change is claimed.

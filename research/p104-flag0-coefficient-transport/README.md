# P104 flag 0: coefficient and sign through the native word

**Scoped exact row audit. No new kappa, correction program, supplier, or cost claim.**

## Question and result

For the first record of PR #2981's 208-flag collection, does the exact
coefficient for source `X0` reach target `Y34` through the cited 4,058-event
native word, and what sign does the complementary `I-G/2` term require?

Flag 0 is `(X0, Y34)` with basis head `232`. The source and target roots have
dot product `4` in the fixture's doubled E8 coordinates (root norm `8`). Thus
the native `G/2` coefficient is `4/8 = +1/2`, while the off-diagonal
coefficient required from `I-G/2` is `-1/2`.

The exact one-hot row replay sets `x0=z`, all other source and dirty
coefficients to zero, and the `y34` baseline to zero. It follows the scalar
rows through the pinned word: transports retain rows, additions use their
literal `Fraction` coefficient, and private zero/copy/erase events update the
row as specified by the native-channel proof. The `Y34` additions carrying
`z` occur at events 2815 (`+z/2`), 2998 (`-z/2`, canceling it), and 3369
(`+z/2`). The final native row is therefore `z/2`; the required side term is
`-z/2`.

The zero-based event order is `Y34` first touched at 129, `X0` first touched at
591, `Y34` last touched at 3500, and `X0` last touched at 3954. PR #3242's
whole-word scan reports no X/Y pair sharing an event; this check confirms that
`X0` and `Y34` do not share one. The one-hot replay shows that first-touch
ordering alone does not rule out later relay delivery in this native word:
`Y34` gets its nonzero `X0` coefficient after event 591. These are
native-channel additions, not an executable side correction.

## Scope and limits

This checks one exact coefficient row for one named flag. It uses the
independent linear-row invariant already proved for the pinned native
realization; it does not rerun that package's Clifford or all-column proof.
The dirty coordinates are zero in this one-hot coefficient slice. The audit
does not deliver the opposite side term, restore arbitrary dirty inputs,
certify frame availability for a correction, or price correction/idle/hosting
work. The newer pooled support audits (#3259, #3803, and #3810) concern whether
fixed-cover correction coefficients have support; this package checks the
opposite-sign native row for one actual word path and does not extend those
support claims.

Reproduce the bounded check from the repository root:

```sh
python3 scripts/research_package.py --package research/p104-flag0-coefficient-transport --check-only
python3.12 scripts/research_package.py --package research/p104-flag0-coefficient-transport
```

## Open next questions

Can an added correction deliver `-z/2` to `Y34` at a legal common-frame cut
while restoring all dirty inputs? This matters because the native word
delivers `+z/2`, and the opposite sign is required for this off-diagonal entry.
The next step is to name a legal source/target frame cut and an explicit
correction writer, then test its full dirty row. A complete bill and the
correction construction remain outstanding.

## Credit

Credit Nick Petalas / PR #2981 for the static flag certificate; Rohan Arun / PR
#1972 and Chafik Boukhalfa / PR #1991 for the low-rank channel and native row
invariant; and jwr404 / PR #3242 for the event-index chronology that motivated
this flag-0 check. The coefficient trace and sign comparison here are new.
The pooled support lineage remains credited to PR #3182, #3259, #3803, and
#3810. Prepared by OpenAI Codex, laptop-03 session; no independent human or
formal-kernel review is claimed. New work is Apache-2.0.

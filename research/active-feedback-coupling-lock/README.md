# Declared decoder cannot clear the active-feedback y0 coupling

**Scoped obstruction; no new κ.** In the published two-edge feed of
[research/coded-active-feedback](../coded-active-feedback/README.md),
every rational sum of alternating `C1`/`C3` words, with or without a
right `Q^2`, preserves one monomial of the second-input coupling
whenever it keeps the restored coefficient `D1 Q^{-1}`.

The predecessor already showed that one bounded search attains only one
of the four jobs. The new statement is exact for the whole infinite
decoder family, and it uses all 39 saved banks. The witness is two basis
coefficients. [PROOF.md](PROOF.md) gives the support bound and the length
count. The selected frontier is unchanged.

## Result

Let α be the `D1`-line key `Q^{-1}` and β the `D1`-line key
`Q^{-1} C1 Q`. The restored coefficient is the α term. The coupling
`Q^{-1} C1 Q (I-Q) D1` contains the β term with coefficient `+1`.

On every saved bank the α and β coefficients agree. Every longer declared
control pulls both keys outside the seven-word `D1`-line support of the
trace, so it contributes 0 to both. A decoder output that keeps α
coefficient 1 therefore keeps β coefficient 1, and the y0 block is not
zero.

An explicit two-term correction built from final bank 1 does clear that
y0 block, but both of its words have an odd power of `Q`. It lies outside
the declared family and is not offered as a free repair.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 -B scripts/research_package.py --package research/active-feedback-coupling-lock --check-only
python3 -B scripts/research_package.py --package research/active-feedback-coupling-lock
```

Direct replay:

```sh
python3 -I -W error -B research/active-feedback-coupling-lock/verify.py
python3 -I -O -W error -B research/active-feedback-coupling-lock/verify.py
```

The optimized command still executes the checks. They are `need` failures,
not assertions. Allow a few seconds. No network, native build or full
multiplier replay is used.

## Scope

Original card: `joint-query-controller`. Scope status: **refined**. The
card asks whether one changed caller removes real work. This package
does not change the query demand. It takes the open coupling question
left by the active-feedback package, which is the live remainder of the
passive saved-query handoff
[discussion comment 19138525](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19138525)
after that package had already restored the missing coefficient.

Base commit: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Pins are in
[SOURCES.json](SOURCES.json). The catalogue and selected record are
provenance. `search.py` and `gauge.py` are live inputs.

## Open next questions

Can a port-dependent map, rather than one left multiplier, remove the y0
term while every required final bank stays intact? The first step is one
owner-indexed map with the x0 block fixed, the y0 block zero, and the
other endpoint banks unchanged, then a charge for every new monomial.
Nothing here supplies that map, and the restored bank's x1 term is a
separate unpaid obstruction.

Does one feedback edge outside the 8,281-policy family make the whole
four-input row autonomous? Name the edge and test the row before adding
calls. This package does not construct one.

## Credit

The trace, algebra and decoder family are Cinna Davis's
`research/coded-active-feedback`, using Dugongue's PR4948 chronology,
Dillon's PR4933 code and the passive ceiling packaged by Chris R /
Clear1nsight. The gauge engine remains the inherited
`research/coded-native-caller/gauge.py`. New work is the two-point
support argument and its checker.

Prepared by unpaidmoon with substantial Cursor Grok assistance.
Apache-2.0.

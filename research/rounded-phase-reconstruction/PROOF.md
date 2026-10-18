# Exact rounded-grid reconstruction

This independently formalizes the exact reconstruction argument already given
by Ali Romman in PR1141, `PROOF.md` Sections 1 and 5. It introduces no new phase
algorithm and proves no analytic error estimate. The formal domain is every
pair of integer-grid registers, including arbitrarily large dirty values.

## 1. Source interpretation and rounding

Fix an integer precision `b >= 0` and grid spacing `h = 2^-b`. Identify a
complex register `(h*x,h*y)` with `(x,y) : Int × Int`. For any fixed rational
coefficient `c`, the pinned `real_round` satisfies

```
real_round(c*(h*x), b) = h * floor(c*x + 1/2).
```

Thus each rounded multiplication is a deterministic function `Int -> Int`.
The theorem permits *any* such function, without linearity, oddness, bounded
inputs, or a small coefficient assumption. In particular half-up rounding is
not odd: `floor(1/2+1/2)=1`, while `floor(-1/2+1/2)=0`.

Define `X_f^-(x,y)=(x-f(y),y)`, `X_f^+(x,y)=(x+f(y),y)` and similarly
`Y_g^±(x,y)=(x,y±g(x))`. Each pair are exact two-sided inverses because their
controlling coordinate is untouched. The inverse must add the *same* rounded
product; subtracting the rounded product with a negated coefficient need not
work at a tie.

For a quadrant `q`, let `Q_q` be the signed coordinate permutation. The source
`rotate` is, in function-composition order,

```
R = Q_q o X_f^- o Y_g^+ o X_f^-.
R^-1 = X_f^+ o Y_g^- o X_f^+ o Q_q^-1.
```

`unrotate_rotate` and `rotate_unrotate` prove both identities on every input.
Both `rotate` and `real_round` are defined in the unchanged
`vendor/pr1141/vendor/pr1038/chirp.py`; `phase_stream.py` binds them through
its imported predecessor module.

## 2. Deterministic chart and nonlinear state

The source `phase_stream.chart` selects the quadrant by the largest signed
component, with its written tie order. After undoing that quadrant, `c >= |s|`
and `c >= 0`, so `1+c > 0` even for arbitrary dirty input. It deterministically
rounds `s/(1+c)` at `b+8` bits, clips it to `[-1/2,1/2]`, and clips `s` to
`[-1,1]`. This is a total coefficient-producing function on the grid.
The proof allows an arbitrary deterministic function `chart : Grid -> Coeff`;
it does not use or establish the chart's approximation to a unit phase.

For a fixed coefficient `omega` and state `(value,ratio)`, define

```
F(v,r) = (R_chart(r)(v), R_omega(r)).
B(v',r') = let r = R_omega^-1(r'); (R_chart(r)^-1(v'), r).
```

`back_step` and `step_back` prove `B(F(s))=s` and `F(B(s))=s` for all states.
This is precisely the arithmetic order in `State.step`: in reverse mode the
ratio is restored *before* the chart is reconstructed. Building the chart from
`r'` can apply a different inverse and is rejected by a concrete control.

The source creates and erases coefficient scratch while the chart input is
unchanged. This equality is visible in the source and exercised by the replay;
the Lean `Coeff` is a mathematical parameter, not a physical scratch register.
The source's index/active/busy guards, meter state, seed preparation and erasure
are not represented in the Lean state. They must still be respected by callers.

## 3. Every length, both directions, and repeated readout

`walk f n` applies `f` exactly `n` times. Induction with the one-step inverse
identity gives both arbitrary-length laws, including `n=0`:

```
B^n(F^n(s)) = s,       F^n(B^n(s)) = s.
```

The proof distinguishes chronological walk from reverse nesting, then proves
they coincide for repetitions of the same function. These are the exported
`reconstruct` and `reconstruct_reverse` theorems. `same_readout` allows any
deterministic readout function and proves its output unchanged after a complete
forward/backward reconstruction. Reapplying the same deterministic forward
walk consequently reproduces each readout. No history log or input-magnitude
bound is a premise of these mathematical identities.

This is not a space theorem about their physical realization. In particular it
does not infer a register-width bound from the absence of a mathematical log.

## 4. What is and is not machine checked

`Reconstruction.lean` uses Lean 4.34.1's `Std`, without Mathlib. All seven
exported roots have only `propext` in their reported axiom sets. `kernel.py`
copies the source into a fresh directory, compiles it, audits those exact roots,
and requires four false concrete inverse/reconstruction statements to fail in
the kernel. It also tests rejection of a forged `sorryAx` report. The toolchain
and its foundational rules remain trusted.

The identification of the pinned Python operations with the definitions above
is a reviewed mathematical interpretation, **not a verified Python-to-Lean
translation**. `verify.py` strengthens that boundary with a separately written
integer-lattice interpreter, exact rational source comparisons, both inverse
directions, arbitrary dirty states, 64/257/1024-bit coordinates, nonlinear
trajectories and source-level mutation controls. These are finite checks.
The four `Phase.prepare`/`phase_pass` fixtures exercise actual caller cleanup;
they do not extend the Lean theorem to every source caller or all seed logic.

The predecessor's analytic precision, phase approximation, uniform runtime,
tape restoration, physical scratch budget and complete dirty convolution remain
outside this contribution. No supplier admission, selected-result change, or
new kappa follows from the exact reconstruction theorem alone.

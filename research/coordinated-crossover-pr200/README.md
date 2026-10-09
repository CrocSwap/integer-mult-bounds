# κ = 6.94787513005285e-4 — refine the 471-source physical frame word

This conditional finite witness reaches
`κ = 694787513005285/10^18 = 0.000694787513005285`, an exact increase of
`4793314502/10^18` over PR210's `694782719690783/10^18`.

The change is a deterministic equal-frame plateau descent on PR210 head
`df95878d11190518e45ef9717c9ee05011f88ace`. It retimes 19 operation frames in
14 accepted moves: operation 18750 grows from dimension 5 to 6; five adjacent
pairs at operations 23544/23545 through 23732/23733 grow from dimension 9 to
12; and eight operations in the late plateau grow from dimension 13 to 14.
The original scalar operations and all source, target, dirty-register and
bank roles are retained. Exact frame containment, nondegeneracy and nested
role chains admit every move. The `d log d` objective proposes moves only; the
reported κ comes from the complete rational 47-constraint assembly.

The final normalized profile keeps `m=72`, `W=438838`, rank mass `31549872`,
deficit `46464`, and maximum child `22`. The changed raw child histogram has
zero rank-mass change and 27 fewer child occurrences per vertex; its exact
distribution lowers the paid bit moment. The bit saving rises from
`695265778339166/10^18` to `695270578321263/10^18`; the bit branch still binds.
The adjacent `10^-18` grid point is rejected, and all 47 strict assembly
inequalities remain positive.

Reproduce the committed deterministic search and full offline certificate:

```sh
python3 -B research/coordinated-crossover-pr200/search/joint-plateau-search-prdf958.py --verify-committed
python3 -B research/coordinated-crossover-pr200/verify.py --temp-root /tmp
```

The first command regenerates the 14-move record from the pinned parent frame
file. The second replays the scalar word over F2 and both defining integer
signs, checks all formal columns and restorations, rebuilds the complete source,
internal and target ledgers, verifies the 231 charts and 3,594,888 bank
assignments, replays the frozen complex supplier, and reruns the two exact
moment engines and all 47 inequalities. The package workflow runs both checks.

This is a conditional finite supplier certificate, not an unconditional
integer-multiplication theorem. The all-size compiler, weighted/restored
selector, source-line, routing, prime, precision, fixed analytic tape and
finite-bridge assumptions are inherited unchanged. The complex supplier keeps
its exact local-flow contract.

Provenance and retained upstream credits are recorded in `NOTICE`. The new
retiming search and integration were prepared by sennemmi with substantial
OpenAI Codex assistance and extend eumemic's PR210 construction; the new search
claims no ownership of the inherited source word, bank construction or proof
dependencies.

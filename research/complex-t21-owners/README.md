# Twenty-one replicas on the U8 word

The retained conditional framework admits

```
kappa = 1661957774647029 / 10^18 = 0.001661957774647029
```

This is **1.474747145e-9 above PR870**. The local U8 word, its 504 helper
widths, and the PR589 bit supplier are unchanged. A new 21-replica owner map
uses 189 complete invocations and 95,256 whole-helper roles. Its idle profile
is `{48:6292, 3:1, 1:3}`. The independent finite checks give prefix
`491 < 512` and physical row coefficient `16469 < 20161`.

The construction combines Hao Yan's PR858 T16 map with an explicit five-replica
map, delays the latter's placement by four T16 calls, and applies nine frozen
owner edits. It includes a checked `8+8+5` dedicated-bank envelope: the last
group pads the complement of five active lanes. The final hosted controller
removes every dedicated bank. See [PROOF.md](PROOF.md) and [NOTICE.md](NOTICE.md).

## Reproduce

From the repository root, with Python 3.11+ and the existing frontier replay's
NumPy/SymPy/SciPy, C++17 and Boost dependencies:

```sh
python -B research/complex-t21-owners/verify.py --work /tmp/t21-cold
```

The default rebuilds PR589, PR741 and PR799, then rebuilds U8 including phases,
checks both literal owner maps and the partial bank group, emits the controller,
recounts its complete invoice, and runs two exact moment engines plus all 47
outer inequalities. No optimizer is required. Outputs must be new and outside
the checkout. Assertions must remain enabled.

A completed PR799 replay can be explicitly reused; its complete ancestry,
fixed stage coverage, source hashes, artifact hashes and log hashes are checked
again before it is consumed:

```sh
python -B research/complex-t21-owners/verify.py --work /tmp/t21-reuse \
  --baseline799 /absolute/verified799 \
  --ancestor741 /absolute/verified799/ancestor
```

U8 is rebuilt even in this mode. The retained controls include 38 U8 construction
cases, 95 inherited end mutations, eleven inherited T16 omitted edits, six
independent controls for each of T5 and T21, nine omitted T21 edits, one omitted
delay, eight partial-bank mutations, fifteen controller mutations, 69 admission
mutations, and twelve bit-supplier mutations. Exact outer boundary controls also
run. Source and generated-content identities are checked separately.

The additional package-boundary controls are run by CI after the strict replay:

```sh
python -B research/complex-t21-owners/package_controls.py \
  --replay /tmp/t21-cold --baseline799 /tmp/t21-cold/baseline799 \
  --ancestor741 /tmp/t21-cold/baseline799/ancestor \
  --out /tmp/t21-package-controls.json
```

They mutate stage coverage, ancestry, owner semantics, runtime SPEC and package
bytes, and include two positive gzip-recompression cases. Receipt coverage and
hash consistency do not authenticate a claimed historical execution.

This is a finite conditional witness. All-size compilation, common-label and
mutable-source realization, whole-call hosting, precision/tape, analytic transfer
and bit H1–H5 interfaces remain inherited hypotheses. It is not an unconditional
multiplication theorem, a claim that kappa is close to one, or an optimality claim
over other local words or controller families.

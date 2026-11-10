# Faster complete current P104 scalar replay

The complete PR6453 forward scalar check now has an explicit sparse integer
engine. Five alternating fresh-process triples give median complete command
time 1.0791 to 0.2789 seconds, or **3.87 times as fast** on this host. The
checker function itself falls from 0.9793 to 0.1747 seconds, or 5.60 times as
fast. Every complete receipt agrees. This is a scalar verification speedup,
not a full supplier replay or multiplication speedup. No new kappa is claimed.

Both sparse shared-denominator and packed signed-radix representations were
implemented and checked. Packing takes 0.4181 seconds per complete command
on the same sample set. Sparse rows are the recommended engine for this
forward workload. Coefficient parsing and scalar-bound arithmetic were also
profiled and improved. The result does not stop at the initial row port.

## Verification

Use CPython 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/p104-forward-integer-replay
python3.12 -I -B research/p104-forward-integer-replay/run.py sparse
```

The registered marker is `PASS_P104_FORWARD_INTEGER_REPLAY`. Both normal and
optimized modes check:

- All 35,749 event prefixes of the current and clean words. Their changed
  rows represent 28,563,451 coefficient positions, including zeros.
- Every retained scalar branch, all 19 scalar guards, helper control flow,
  complete receipts and all seven published scalar rejection controls.
- Thirteen extra malformed-word controls, 3,840 arithmetic cases, a COPY
  variant of the full current word, source isolation and cache eviction.
- Five exact source pins, source corruption, an omitted guard, a lost ADD,
  and the benchmark's source, receipt and median bindings.

[PROOF.md](PROOF.md) proves exact representation equivalence and the packed
radix bound. [RESULT.json](RESULT.json) records the checks. The recommended
sparse engine preserves the original first error messages on the control
corpus. The packed prepass rejects one invalid public dimension earlier;
its error-order interface is not a drop-in replacement.

[BENCHMARK.json](BENCHMARK.json) retains all 15 sequential fresh-process
samples. Run `python3.12 -I -B research/p104-forward-integer-replay/benchmark.py`
to repeat the experiment. Timings are local observations and can vary with
host load. No timing threshold is a mathematical acceptance test.

## Source and scope

Base: canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority8,
selected PR6030. The main word is PR6453 at
`b1a3e525793eca35c56324aa7ffd0b714cf606d4`. The clean word is PR6399 at
`a928a7aa5ab5b21b7cf841d6d960ab2e7efd1041`. The scalar checker is PR5827 at
`05cd36e5af06d7a3790e30ce3f449fa89b853768`. All five retained files are
byte-exact. Replay needs no network, Git object or external package source.

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5600#discussioncomment-19363428).
The fresh live overlap check and main object search found earlier generic
integer-row methods and the distinct PR6021 packed transpose checkpoint.
They retain credit. PR6479 covers native replay, and a separate active claim
covers exact root-search cost. This package does not repeat those results.
Sparse notes, unpublished work and arbitrary historical diffs remain limits.

The native maps, independent transpose, physical caller, prices, compiler,
outer rows and all five selected assumptions are outside this scalar replay.
Full-history ancestry checking is unavailable in this shallow checkout.
No selected command or source is changed. Independent scientific acceptance
and proof-kernel checking are unclaimed.

## Open next questions

- Integrate the sparse engine as an explicit dependency in a maintained
  complete candidate verifier. Compare every full receipt and rejection
  control, and measure the complete caller before claiming a wider speedup.
- Profile a named changed-word search. Test whether scalar screening can
  reject invalid candidates before native and price checks. A new search
  still needs a legal producer, consumer and complete invoice.

Ali Romman with substantial OpenAI Codex assistance; no subagents.
[NOTICE](NOTICE) retains the P104, native, integer-row and packed-method
attribution. Apache-2.0. No predecessor algorithm is claimed as new.

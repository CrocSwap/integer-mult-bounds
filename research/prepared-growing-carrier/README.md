# A decoder with three prepared carriers and growing read frames

This package gives one exact finite complex decoder on 11 streams of
64 values. Three carrier inputs start in prescribed line frames. Eight
target inputs start in the zero frame, which is the identity operator;
their values are arbitrary. In scalar coordinates the endpoint is
`X_i -> X_i` and `Y_t -> Y_t + sum_i bit_i(t) X_i`.
The word has 12 scalar ADDs, 27 paid children, rank mass 55, and no COPY.
This is a local construction. It gives no complete supplier or kappa gain.

Read the [independent proof](historical/work/autonomous-kappa-run/growing-cycle-independent/PROOF.md)
and [literal word](historical/work/p518-next/complex/paired-five/GROWING-CYCLE-WORD.json).
The three source ports are `e_0,e_2,e_4`; target `t` has port
`sum_i e_(2*i+bit_i(t))`. The canonical frame operator is `T_F`.
For physical input streams `h`, the carrier output is
`T_FULL T_(e_(2*i))^-1 h_i`. The target output is
`T_(q(t)^perp) (h_(3+t) + sum_i bit_i(t) T_(e_(2*i))^-1 h_i)`.
The carriers preserve their scalar values; their physical frames change.

The [saved exit extension](historical/work/p518-next/complex/paired-five/add_growing_exits.py)
adds eight exact monomial adapters. Each target then ends in `F C_q^-1`
in place of its canonical hyperplane operator. These adapters add no
positive child rank. Their scalar and monomial operations still need a
payment in a complete supplier. The historical independent proof states
that these exits are absent from its base word; the separate saved exit
word and replay make that distinction explicit.

The mechanism permits a carrier to grow after an earlier target is served.
A final read frame need not fit every earlier target. This supplies a
concrete counterexample to extending the saved
[fixed-frame delivery argument](historical/work/p518-next/complex/paired-five/independent/DELIVERY-FLAGS-PROOF.md)
to arbitrary growing read frames. It is not a lower bound on all decoders.
The source factory, initial frame preparation, routing, precision, storage,
owner controller and complete invoice remain outside this result.

## Replay

From this package directory, with Python 3.10 or later:

```sh
python3 -B verify.py --build /tmp/prepared-growing-carrier-replay
```

The build path must not exist. Only the standard library is required.
The runner verifies all source hashes, copies the historical files into
the new build path, reconstructs both words, and compares their exact
bytes and receipts. It then runs the independent Gaussian-integer checker.
Python child processes ignore Python environment options; the wrappers
reject optimized Python because the saved sources use assertions.
The final line must be:

```text
PASS_PREPARED_GROWING_CARRIER 704 55 8
```

The independent check covers all 11 scalar input columns, all 1,472
recipe basis columns, and all 704 whole-word basis columns and inverse
round trips. It checks exact global phase, common labels at each ADD,
compatibility of every pending target, the rank profile, and a phase
mutation. The exit generator checks all 512 target-adapter columns.
Complex linearity then gives the displayed endpoint for every input.
The independent checker shares the canonical frame definitions with the
producer. It imports neither the builder nor its lowering procedure.

`SOURCE-MANIFEST.json` records the unchanged historical inputs.
`replay.py` is a portable copy of the original independent checker:
it replaces the old absolute input path and result path with explicit
arguments and adds an optimized-Python guard. The original is retained.
The only expected receipt difference is the checker's own source hash.
`replayed-receipt.json` and `replay.log` record the fresh cleanup replay.

## Sources and related work

The consumed exact Clifford definitions came through the historical
[PR #518](https://github.com/CrocSwap/integer-mult-bounds/pull/518)
source copy. Their bytes are also present in @icekylinx's
[PR #531](https://github.com/CrocSwap/integer-mult-bounds/pull/531), at
[this pinned source](https://github.com/CrocSwap/integer-mult-bounds/blob/e07a8a3f9f79c22113398a0c5dbbc7601f489b3e/research/direct-delivery504-global/vendor/clifford/clifford_exact.py).
The [notice](public-source/NOTICE.md) and [source ledger](public-source/SOURCES.json)
retain its predecessor credit. The local word, checks and packaging were
prepared with substantial OpenAI Codex and research-agent assistance under
the user's direction. No independent human review is claimed.

The later [shared-carrier decoder](https://github.com/CrocSwap/integer-mult-bounds/blob/cef4b52f2a59009865bf8eabde1be3f159063703/research/shared-carrier-decoder/README.md)
is a different P111 module with 452 dirty helpers and a nonzero COPY
endpoint. The paired-hypercube parity results concern the scalar source
factory, not this prepared three-carrier interface. No cost gain from
those different models is added to this result.

## Open next questions

Can a complete source factory supply these three carriers at the stated
initial frames and give a favorable cost after all other work is paid?
The first step is to compose an existing literal source factory with this
11-stream endpoint and check every dirty input column. No such composition
or cost certificate is included here.

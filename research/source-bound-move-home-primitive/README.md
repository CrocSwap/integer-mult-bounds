# Actual selected MOVE through one complete HOME field

This package installs the **unchanged exact selected MOVE24472** as one typed
uniform primitive of the permanent-home dispatcher. The supplied binary body
is six positive Gamma codes `f,r,P,S,w,cutoff`, followed immediately by the
complete packed DATA and B1's outside `|`. Its extent is F=E+V. The result
returns the identical header and complete transformed DATA to the same HOME.

The native core is pinned at `3a27ab1d302d13b1ce52411f8a174e7a32baab77`;
B1 is pinned at `b4fcc9d64971fdabd0b1d82cfb749d8aac920437`. All runtime
imports are retained locally with exact source pins. The prototype no longer
uses shared checkout paths. See [PROOF.md](PROOF.md) and [SOURCES.json](SOURCES.json).

The graph copies/splits HEADER and DATA onto 31 distinct private core tapes,
then runs the actual 82,813-instruction core. B's permanent origin is relative
cell 0; native origins are shifted to 2, leaving private guard cell 1 blank.
Successful repacking retires copies and returns all private heads to B origin
0 without erasing `^`. The complete graph has 82,980 states on 35 tapes.
No runtime Python factor callback, decoded integer oracle or replacement core
implements the MOVE.

The standalone bill is
`128(F+1)+2^24(fV+E+1)`, with history bounded by entry history plus
`1088(F+1)`. B1 still pays its separate O(RKF) full-field gathering/return.
At a fixed admitted leaf cutoff f<=q, the primitive is O_q(F); a large encoded
cutoff still pays all of its E bits. No faster nonleaf rate is asserted.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -I -W error -B research/source-bound-move-home-primitive/verify.py
python3 -I -O -W error -B research/source-bound-move-home-primitive/verify.py
```

The result marker is `PASS_SOURCE_BOUND_MOVE_HOME_PRIMITIVE`. `--write`
regenerates RESULT.json. Default execution compares its full scientific
payload. Source bytes authenticate before imports; source bytecode caches
are isolated from the retained inputs. No Git, network, shared source checkout
or full historical suite is needed.

The full f=1, m=9 packet contains 512 Gaussian entries, with odd real signs
and zero imaginary components. The original-frame Gaussian oracle sums all
numerators before checking integrality: individual half-integral basis terms
are allowed to cancel. It uses frames []/[239], not the core's factor/CNOT
word. E=10, V=4096 and F=4106. The complete run takes **14,495,822 literal
transitions**, writes exactly 4106 selected HOME bits after primitive return,
and preserves another arbitrary same-F source HOME. Every head, permanent
origin, private guard/body and opaque exterior restores.

The rejected arithmetic prefix takes 4,748,143 transitions with zero HOME
writes. Seven parser-only identity probes cover cutoff bit lengths through
4097 and preserve an explicitly older guide history. Those small DATA bodies
are codec tests, not legal full native fields.

Six controls detect a dropped header return, wrong-home scatter, wrong guard
offset, arithmetic rejection before HOME mutation, raw-zero capacity treated
as a formatted packet and actual corruption of a disposable native-source
copy. Header/drop and wrong-home controls reuse a genuine completed full-core
snapshot and mutate only suffixes. Wrong guard detection is a test monitor
reporting an attempted forbidden origin write; it is not a compiled runtime
protection. Rejection cleanup/retry is unclaimed.

## Scientific boundary

The complete positive six-code packet, common grid, width, packed layout,
cutoff and exact core numerical admission are **supplied caller promises**.
Owned `0^F` is not a packet or an initializer. Earlier history and opaque
storage remain in K_entry; monitored head-span windows do not infer that
complete entry bound. All nine native blocks, P/S spectators, r coefficients
and signed bits remain in DATA throughout.

This proves one actual primitive/dispatcher ABI composition. It supplies no
complete native supplier, selected source-word generation, caller/initializer
admission, new precision reserve, endpoint scale conversion, faster recurrence
or analytic recovery. All five assumptions and κ=.00363005817 remain.

## Open next questions

1. Connect one actual field producer to this exact Gamma/packed ABI and prove
   its grid, width, cutoff, layout and complete transport bill. The supplied
   entry promise is not that producer.
2. If arithmetic-failure retry is required, compose a source-bound retirement
   transformer for the entire adapter/core, retaining public contents and all
   prior backing. Successful return alone does not establish rejection reuse.

Prepared with substantial OpenAI Codex assistance. Source and predecessor
attribution is retained in [NOTICE.md](NOTICE.md) and the unchanged nested
notices. No human or formal-kernel acceptance is claimed.

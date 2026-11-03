# Bounded arithmetic for the complete P104 price

The complete PR6453 price/compiler/outer replay uses a second interval engine
whose exact exponential endpoints can have 82,380-bit denominators. This package
bounds its logarithm and exponential arithmetic on a 160-bit dyadic grid. Every
new interval contains the retained source interval. All signed-price, compiler
and outer predicates pass, and the complete displayed receipt is unchanged.
The output exponential denominators have at most 161 bits. No new kappa.

The complete command median is 15.975660 seconds with the prior
exact integer Taylor baseline and 0.988312 seconds with bounded
arithmetic (16.16 times faster on this host). BENCHMARK.json contains all
three alternating fresh-process pairs and the environment. Both commands include
imports, source authentication, full price/compiler/outer execution and receipt
serialization. Native and caller receipts are inputs. This is not a whole-caller
measurement or a universal speed guarantee.

The baseline is Nick Petalas's PR6395, which follows ywz65's integer Taylor work.
Its exact-endpoint improvement is not claimed again. The new numerical contract
rounds outward at every operation and contains the original 80-term logarithm
and 48-term exponential intervals. PR6505's checked root certificate is used in
both modes. No frozen source is edited or patched.

PROOF.md gives the all-input enclosure and arithmetic size bounds. RESULT.json
records 266 exponential and 725 logarithm fixtures, all 108 live exponential
calls, complete rank-power containment, 54 strict and four functional outer
predicates, and failure controls. The exact receipt first passes at 124 bits;
123 fails. The default retains 36 extra bits. A 64-bit call fails the scientific
path. Actual arithmetic mutants remove a term or tail or round an upper bound
down; exact containment checks reject them. Invalid inputs also reject.

Run with CPython 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/bounded-dyadic-moment
python3.12 -I -B research/bounded-dyadic-moment/benchmark.py
```

Both registered modes reproduce the same receipt. Committed-byte/mode checks,
official export input checks, read-only Git-free replays with an empty PATH,
and exported-source corruption controls are required before publication. The
checkout is shallow; the optional full-history check is not claimed. No Lean,
Docker, independent human review or native/physical acceptance is claimed.
The five framework assumptions and selected frontier remain unchanged.

Ali Romman with substantial OpenAI Codex assistance; Apache-2.0. Credit Nick
Petalas, ywz65, zxv, Cinna Davis, Cao Yifan, Jacob Alan Sussman and all retained
construction authors. Exact source bytes and notices are in inputs. New code
uses explicit dependencies. No known fragile workaround is used.

## Open next questions

Can these explicit arithmetic and native adapters reduce the complete caller
command while regenerating every native, scalar and physical receipt? First
bind that full path and compare its entire scientific output. See TASK.json.

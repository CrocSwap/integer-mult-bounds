# Quadratic-scan QQ16 Context construction

For fixed compiled radix q and dimension d, this package reduces the actual
Context constructor's numerical/record source-action count from a cubic
Word-division term to a quadratic bound in the radix exponent w. It uses one
fixed-q quotient scan per radix digit, reuses the first quotient as cap, and
retains the credited shared Count multiplications. Runtime w is never decoded.

At q=5,w=8,d=4, the complete new_context/save_count interval uses 96660 actions,
versus 407496 for the already-shared predecessor and 2614926 for the literal
source. The local peaks fall from two record leases and nine numerical Words
to one lease and four Words, including modulus and ring.one.

[PROOF.md](PROOF.md) gives the exact bills, all-size proof, source boundary
and full predecessor credit. [constructor.py](constructor.py) is the new
implementation. [RESULT.json](RESULT.json) records 1512 complete quotient
cases, 21 actual constructor runs in seven matched triples, and four
non-power rejection/rollback controls. The comparisons include dimension64
at w=1, dirty highs replacement, canonical heads and exact alias checks.

```sh
python3.12 -B scripts/research_package.py --package research/qq16-linear-radix-context
```

Both registered isolated, warning-strict normal and optimized modes print
`PASS_LINEAR_RADIX_CONTEXT`. The standard library suffices. Source hashes
and the complete typed receipt are checked. No timing benchmark is claimed.

The complete kappa calculation is unchanged. The count formula, loop sharing
and fixed-radix long division are credited predecessor methods; the new part
is the fixed-Word scan and fused actual constructor with its complete local
invoice. Compiled q and d belong to fixed control. The bound does not certify
uniform control size as q grows. Pool/metadata control, the full loader,
source codebook, physical root closure, complete frontend F(K), parent parking,
stock/precision and supplier admission remain separate. Lean, Docker, selected
cold replay and full-history validation were not run.

## Open next questions

Compose this constructor with the finite-handle restore/adopt implementation
and actual parked caller roots. Start from the literal new_context and
restore_context replacement path, retaining all source aliases and record
slots. The numerical/record improvement does not give a complete controller
bill or resolve arbitrary live caller references.

## Credit and coordination

Base 7c472563474e60185e6ca101a17622133d047e56, priority 7. Current main, the live
Context handoff, all-state numerical-producer PR search and relevant main notes
were checked. Arbitrary historical diffs and unpublished work remain outside
coverage. [SOURCES.json](SOURCES.json) pins all inputs. The byte-exact fixture
in vendor/ is consumed from pending PR5363; its status is explicit. Replay
pins resolve to that retained copy in this PR history. The upstream_pin
retains the original commit and path. Thus a clean checkout does not need
the unmerged predecessor commit.

ToikY supplied shared traversal; Chris R/Clear1nsight applied it to Context.
Mihir Srivastava supplied the high-count installation audit and source loader.
Jose Manuel/jmbarrancoml and David Arias supplied the retained physical caller
and cardinality source. JoyboyBrian supplied the constructor handoff; Tekalign,
ywz65 and the retained control/record lineage keep their attribution. The
retained Natural.divide_small is the algorithmic precedent for fixed-q division.
See PROOF.md for full PR links. Original notices are unchanged.

New work: Ali Romman with substantial OpenAI Codex assistance in derivation,
implementation, review and verification. Apache-2.0. No independent human or
proof-kernel acceptance is claimed.

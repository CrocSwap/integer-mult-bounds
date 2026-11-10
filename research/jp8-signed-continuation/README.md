# One signed JP8 continuation saves six scalar primitives

This contribution was produced by Nick Petalas.

Claim type: finite local circuit certificate with a scoped substitution proof.
The historical PR626 JP8 forward fragment at zero-based event interval
`[19709,19713)` has a shorter implementation than Ryan Haines's PR811
positive-read compiler. Two cleared blocks cost 17 primitives per real
component. One signed continuation costs 14. Applying it separately to the
real and imaginary components saves exactly six real-component primitives.
Every source read, shift, target update and boundary clear is counted.

The recursive paid profile and productive targets are unchanged. This is a
historical scalar-program improvement, with no new kappa or selected-frontier
change. The search stopped at this first retained source-bound improvement;
there is no wider census or optimality claim.

## Exact fragment and construction

The four consecutive full-frame cleanup events use source `s=L81` and distinct
targets `a=L227`, `b=L230`, `c=L231`, `d=L232`:

```text
a += 3s/2
b -= 3s/2
c -= s/2
d += 5s/2
```

The existing private work register is `w=L724`. Its initial value is arbitrary
and its required exit value is zero. PR811's two blocks are
`[19709,19711)` and `[19711,19713)`. The new literal program is:

```text
clear w
w += s
double w
w += s
halve w
a += w
b -= w
w -= s
c -= w
halve w
w += s
double w
d += w
clear w
```

After the first five instructions, `w=3s/2`, independently of its initial
value. The next two instructions perform the first two target updates. The
new subtraction leaves `w=s/2`. After updating `c`, the inherited three-step
positive route changes `s/2` to `5s/2`. Updating `d` and clearing `w` gives the
stated complete map. Source and all other registers remain unchanged. This
proves equality for arbitrary scalar inputs over the rationals or complexes,
including arbitrary target and private-work inputs.

The changed interface is the private-work clear between the two old blocks.
The old four-instruction sequence `clear w; clear w; w += s; halve w`
is replaced by `w -= s`, under the established entry value `w=3s/2`.
The subsequent instructions are identical. There is no crossed child,
adapter, phase or frame change, and no extra register. Equality at the
fragment's complete boundary permits exact substitution into any unchanged
surrounding scalar program. It does not establish a rounded physical caller.

The exact work coefficient never exceeds three in absolute value in either
program, and its finest intermediate dyadic denominator is four. Each target
is updated once, by the same amount and in the same order. These exact prefix
facts use cancellation. They do not imply that the predecessor's
cancellation-free triangle majorant, whole-word precision receipt or rounding
error bound transfers without a new calculation.

## Evidence and reproduction

Use CPython 3.12 and the standard library, from the worktree root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/jp8-signed-continuation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/jp8-signed-continuation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/jp8-signed-continuation
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/jp8-signed-continuation --check-source-history
```

Substitute another CPython 3.12 executable elsewhere. Direct verification
writes a generated hash-bound receipt to stdout, with marker
`PASS_JP8_SIGNED_CONTINUATION`. It writes no files into the checkout.
`WITNESS.json` is the circuit witness, not a claimed execution receipt.

The verifier authenticates the three declared inputs, extracts exactly the
four new application events, and uses only the parent constructor's two local
lowerings. It runs no predecessor scientific verifier and does not recount
the parent program. It checks the complete six-input matrix against a direct
specification. A separate integer scalar interpreter executes both literal
programs on all 15,625 fourfold-grid inputs per program. Seven semantic
controls reject missing boundary clears, a missing or reversed subtraction,
a wrong source, a wrong target sign and an endpoint-neutral work excursion.
Normal and optimized execution use explicit checks.

The matrix proof covers arbitrary inputs; the finite grid is corroboration.
The interpreter does not execute native frame or phase operators. No whole
supplier replay, selected cold replay, rounded induction, compiler, hosting,
tape/storage pricing, stock proof, outer assembly, Lean or Docker run is
included. All five selected framework assumptions remain. Independent human
and formal proof-kernel review are unclaimed.

## Sources and distinction

The exact base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8,
selected PR6030. `SOURCES.json` pins the current catalogue and selected record
as provenance, and the source program, PR811 constructor and README as live
inputs. The task explicitly changes the scalar-to-moment card to this side
result; it does not satisfy that card's moment-improvement acceptance gate.

Ryan Haines's [PR811](https://github.com/CrocSwap/integer-mult-bounds/pull/811),
head `b5c244c916dd0b30957332edad7ae7ae22b0eb9d`, supplies the positive-read
compiler and this historical source application. Its positive transition
search leaves signed reads outside scope. Its local code and credit are
unchanged. Ryan's [PR830](https://github.com/CrocSwap/integer-mult-bounds/pull/830)
supplies backward transposition context; this contribution makes no backward
application claim.

AmazedBot's [PR860](https://github.com/CrocSwap/integer-mult-bounds/pull/860)
already studies signed continuation on CK. Signed shift/add arithmetic and
that mechanism are predecessor work. The new result is the explicit shorter
JP8 source fragment and its exact local application certificate. This is
not a new general signed-digit method. Sagar Thakrar's PR696/723, Sebastien
Taillieu's PR999, Philipp's PR882 and Michal Ciemiega's PR1223 change other
standalone lowering menus. No superiority to every compiler or additive gain
with those packages is claimed.

Credit the retained Jeremy Kothe PR622/623, Chafik Boukhalfa PR626,
icekylinx, Jeffrey Cox PR739, ellipsi2 PR722, Sagar Thakrar PR751 and the
native/compiler/owner lineage recorded in the unchanged source README.
New source, witness and prose are Apache-2.0. The public
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19370136)
states this investigation's boundary.

## Implementation limits

The verifier has no recursion and bounds words by 32 instructions, literal
grid inputs by `5^6`, source events by 100,000 and JSON input sizes explicitly.
Functions stay below 60 physical lines. Python and its exact arithmetic
allocate dynamically; this is a managed-runtime deviation from Power of Ten
rule 3. Source decompression and JSON parsing allocate before their payload
size checks; the authenticated immutable input is the resource contract.
The fixed, authenticated parent constructor is loaded through `runpy`; this
is a bounded dynamic-code/dispatch deviation under rules 8 and 9 for replay
only. It executes local lowering definitions, with no predecessor scientific
entry point. The source-hash and direct replay commands above check these
controls. A future untrusted-input service would need streaming/decompression
caps and a declarative replacement for loading constructor definitions.
No fixed-allocation or hard real-time verifier is claimed.

## Open next questions

Can a signed continuation be installed in one current complete scalar caller
with a fully recomputed rounded prefix budget? It would connect an exact
scalar saving to a current implementation. First extract one source-compatible
boundary and its private-work contract, then charge every conversion and
cleanup operation and derive its cancellation-free error bounds. Current
source binding, native/private-work integration and a complete consumer bill
remain blockers. This package reserves no follow-up.

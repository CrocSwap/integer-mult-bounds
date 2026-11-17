# Generate the outer layer phase from its real encoded header

This package implements the required `S_D` boundary in one fixed literal
20-tape program. It consumes the actual nine-Gamma layer header, generates
its selected-bit geometry, enumerates implicit `[P] x [2^K]^D x [S]`
addresses, repeats each phase over r Gaussian coefficients, and installs
the exact w-bit integer rotations on the original DATA owner.

**No new kappa.** This is a local constructive interface result. All five
global assumptions and the selected conditional multiplication bound retain
their status. The recursive C service, common-grid conversion, owner
allocation, compiler/native admission, permutations and integer recovery
remain separate obligations.

## Exact result

The canonical base is `e54523517d0f03e58352e647c403a5af3e525a57`.
For positive header parameters, D<=d, 0<=rho<K and w>=p+2, let

```
L=DK, Q=2^L, M=PQS, N=Mr, V=2Nw, E=header bit length.
```

The table has 2,146 instruction locations and alphabet `{blank,0,1,|}`.
There is no decoded runtime parameter, address oracle, input-sized lookup,
supplied active mask, or host payload arithmetic. Successful execution
preserves HEADER, restores all twenty heads, erases all eighteen private
bodies/guards, and returns `i^(sum selected bits)` times every coefficient
on the same public owner. If a required negation cannot fit, the complete
public input is unchanged; failure cleanup and recovery are unclaimed.

The [proof](PROOF.md) establishes complete bounds

```
time <= 65536(E+p+d+DK+Nw+1)
private retained history <= K0+4V+32(E+p+d+DK+w+1).
```

All source access, parameter acquisition, copies, rewinds, staging, commit,
erasures and repetition loops are included. Unary r/P/S acquisition is paid
because each is at most N. Full binary carries and prefix returns cost
O(P*2^(DK)); there is no per-record DK scan. In the selected source bands
the complete time and added private backing are O(V). Entry blankness is a
whole-window premise, and erasure never resets physical history.

## Relationship to prior work

Ali Romman's [#5375](https://github.com/CrocSwap/integer-mult-bounds/pull/5375)
already supplies sequential monomial phases with a supplied active-position
mask, fixed recipe dimension and one coefficient per record. Its counter
amortization and Gaussian arithmetic retain full credit. The present result
constructs its geometry from the actual header, supports variable D on a
fixed tape inventory, supplies r/P/S repetition and lowers the complete
same-owner sweep to a fixed literal graph.

CubeJerry's pinned [literal normalization/egress package](https://github.com/CubeJerry/integer-mult-bounds/tree/51ab0539059214fcfa044938c36a0b6017232be5/research/literal-layer-egress)
implements b^D and the single required toward-zero projection. It leaves
both S_D sweeps supplied; this package fills that boundary. Its literal
Gamma/trace/cleanup patterns are credited. No upstream PR number is assigned
to that remote contribution in these frozen notes.

The phase table uses eighteen private roles, and the egress uses sixteen.
Two public tapes plus distinct private banks give a direct 36-tape wrapper.
The phase bank is retired and reused for the final sweep. A correctly bound
exact C producer and paid format conversion remain premises. The complete
known boundary work is O(V), with both histories retained.

## Reproduction and evidence

Standard-library Python, from the repository root:

```sh
python -I -W error -B research/literal-layer-phase/verify.py
python -I -W error -O -B research/literal-layer-phase/verify.py
python -I -W error -B research/literal-layer-phase/compose.py
python -I -W error -O -B research/literal-layer-phase/compose.py
```

Expected markers are `PASS_LITERAL_LAYER_PHASE` and
`PASS_LITERAL_PHASE_EGRESS_JOIN`. `--write` regenerates the committed
receipts; default checks only print them. `VERIFY.json` registers the checks.

The main check runs 319 packets containing 29,586 coefficients, including
52 geometries, all 256 signed three-bit pairs isolated at four phase values,
31 correct range rejections, five malformed/domain controls and seven
detected mutations of the actual emitted table. It checks translated origins,
opaque exterior, exact original-owner writes, and grow/shrink/regrow use of
the same private histories. Independent Cartesian-address and integer
oracles are in `oracles.py`; the runtime table never calls them.

The separate join check executes literal S, a **test-only exact C oracle**,
the pinned literal egress and literal S again, using the original public
owner and 36 distinct tapes. Ten source disk-grid tensors, with 316
coefficients, agree with a direct normalized Walsh tensor followed by one
toward-zero projection. This verifies the interfaces and preserves the
unimplemented-C obligation. It does not time the host oracle as machine work.

Finite coverage supports the written universal proof; it does not replace
it. Two separate AI-assisted reviews accepted the scoped result: a dense
Gaussian/address interpreter and a universal/structural interpreter checking
the exact carry movement census. Their source, receipts and accepted hashes
are recorded in `REVIEW.md` and `independent/`. Hosted CI, human review and
formal proof-kernel acceptance remain separate.

## Open next questions

The next useful join is an executable C consumer with exact header,
canonical address order, common-grid output and complete physical cost.
Other questions are shared-bank economy under preserved histories and
header-generated geometry for more general quadratic monomial phases.
See the proof's final section for exact scope.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance in
construction, proof, implementation, independent agent review and checking.
Credit Ali Romman / #5375; Jose Manuel / #2250; JoyboyBrian / #5329; Cinna
Davis and Ryanson Jonathan / #4325; the canonical layer/header authors;
and CubeJerry's frozen literal controller and egress packages. All retained
predecessor notices are preserved. Apache-2.0.

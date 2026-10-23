# Independent P193 contract validation for the signed B3 bridge

**FINITE SCALAR ENDPOINT KERNEL-VERIFIED.** `P193Adapter.lean` passed an
independent offline build with official Lean 4.34.1 at trust level zero. Its
closed concrete provider discharges the existing signed B3 interface for
1320-dimensional complex bank vectors and all 9412 live helper coordinates.
The audit checked 33 named axiom targets and all 180 declarations in the four
newly compiled modules (92 theorem declarations), using only `propext`,
`Classical.choice` and `Quot.sound`. This closes the prior adapter compilation
gap; it establishes no physical B3 construction or compiler certification.

The only executable repair to the previously reviewed adapter is
`open OAI.PowerSaving.SS Matrix`; theorem statements, hypotheses and proof
bodies are unchanged. `KERNEL-RECEIPT.json` records the source, dependency and
axiom bindings; `AXIOMS.txt` contains the exact 33 target outputs and endpoint
type. The exact arithmetic replication and written helper re-derivation below
remain separate evidence routes.

The mathematical content is already present in the pinned upstream Lean source:

- `GXD.P193.scalOK` in `Work/GCert/Data/P193ScalOK.lean:10–15`, backed by
  `scal0_ok`, `scal1_ok` and `ychk_ok`, asserts the five scalar premises.
  Their projections `GS.ScalOK.hAi`, `hBi`, `hx`, `hy` and `hid` are in
  `Work/GCert/Scalar/Main.lean:62–200`.
- `dirt_fwd` and `dirt_bwd` in `Work/Carrier/Ring.lean:45–68` prove the
  generic helper algebra. `GX.Scal.hF` and `hB` in
  `Work/GCert/Chain/Phased.lean:119–126` specialize those identities.
- `GX.Scal.fwd_scalar` and `bwd_scalar` in `Phased.lean:158–189` state the
  completed shears for arbitrary live slots with erased scratch copies.

These are attributions to existing source declarations. The independent kernel
audit rebuilt the required upstream/dependency closure and checked the adapter
against those declarations. The separate exact checkers re-verify their
computational premises without running upstream's checker.
The argument below re-derives the already-stated helper result; the B3
application is a direct instantiation. No novelty or priority claim is made
for the helper identity or the arbitrary/correlated-helper qualification.

At `jacobalansussman/wht-power-saving-lean` commit
`f010392c923279e3dd59ef3aa5fedad23affc5fd`, let (M) be the rational matrix of
the literal P193 main word, in its source order. The dimensions are

\[
x,y\in\mathbb C^{1320},\qquad h\in\mathbb C^{9412}.
\]

Let (P_X,P_Y,P_H) be the coordinate projections. Define the completed
operations by the actual source formulas

\[
\begin{aligned}
g_1&=I-P_YMP_H,&g_{1i}&=I+P_YMP_H,\\
g_8&=P_X+P_Y+P_HM^{-1},&h_8&=P_X+P_Y+P_HM,\\
F&=g_8Mg_1,&B&=(g_{1i}M^{-1}h_8)^T.
\end{aligned}
\]

Then, for **all** such complex vectors,

\[
F(x,y,h)=(x,y+x,h),\qquad B(x,y,h)=(x-y,y,h).
\]

The helpers may depend on either bank or any common parameter. One invocation
acts on the entire coupled 1320-port vector; it is not 1320 independent calls.

## Literal source and exact checks

`source-bindings.json` records the commit, Git blob SHA-1, SHA-256 and byte count
of all 29 source files inspected in the independent review. The record
`Work/GCert/Data/Gen/P193.lean` binds `h=22`, `v=1320`, `R=9412`, `ports`, `ret`,
`scat`, `A=gA` and `B=gB`. The scalar literals are in `Gen/P193/S0.lean` and
`S1.lean`; later segments do not redefine those fields or their scalar semantics.

The `.out` and `.inn` constructors expand to `target += coefficient * source`
in list order. The retained-copy scatter reads `ret[k].first` with `k` descending
from 21 to 0; its coefficient is (1/3) for a set port bit and (-1/6) otherwise.
The expansion has 12,158 A additions, 29,040 scatter additions and 39,623 B
additions: **80,821** total. Its normalized JSON tuple sequence has SHA-256
`718d5e12e8d475aa373833cce98e438de5362c458bf4663784c8baba28fcc5df`.

The checker parses only the required literal grammar. It does not execute Lean
source, repository scripts, generators, or upstream checkers. It verifies:

1. Every elementary addition has distinct in-range registers and a positive
   denominator. Reversing order and negating coefficients gives an actual
   inverse for A and B. The helper-to-Y scatter is also invertible.
2. A writes only helpers from X/helpers; scatter writes only Y from helpers;
   a B write to X reads only X, and a B read from Y can write only Y.
   Induction gives no non-X influence on X and no Y influence on non-Y.
3. All 1320 X basis columns have their required X and Y outputs. All 1320 Y
   basis columns have their required Y outputs. With the structural constraints,
   these establish the complete equalities (P_XM=P_X), (MP_Y=P_Y), and
   the identity Y-from-X block.

The portable checker uses exact integer radix packing, not random sampling or
modular fingerprints. For a row with common denominator (D), let (L) bound
the numerator coefficient 1-norm. Under (t\mathrel{+}=(a/b)s), put

\[
D'=\operatorname{lcm}(D_t,bD_s),\quad
u=D'/D_t,\quad z=aD'/(bD_s),\quad L'=uL_t+|z|L_s.
\]

The integer numerator update is exactly (N'_t=uN_t+zN_s). These bounds are
computed from the literal program. A radix larger than every possible
actual-minus-expected coefficient magnitude is then chosen. If
\(\sum_j a_j R^j=0\) and \(|a_j|<R\), reduction modulo (R) forces (a_0=0);
division and induction force every coefficient to be zero. Thus equality of
the packed integers certifies all coefficients, including signed ones. The
computed X-pass bounds are (L\le278976), (D\le192), with radix (2^{20}).
The last partial batch is checked too. The Y pass has no effective Y-symbol
reads and uses radix (2^3).

An independently written dense C++ rational-vector checker accepted
**19,393,440 coefficient equalities**: all X inputs against all X/Y outputs,
and all Y inputs against all live outputs. It used checked integer arithmetic
and no packed columns, and rejected **two first-addition mutations**. A
separate Python `Fraction` replay in the independent review reproduced
**nine negative-control witnesses**, including incorrect completion wrappers,
dual chronology and signs. `review-evidence.json` records the two evidence
routes separately, with hashes of the underlying review artifacts. That
record is evidence from the separate review; the small replay below does
not rerun the dense C++ engine or the nine Fraction-replay controls.

## Re-derivation of the upstream universal helper proof

For any (z=(x,y,h)), (g_1z) subtracts (P_YMP_Hh) from Y and leaves X/H
unchanged. Since (MP_Y=P_Y), applying (M) cancels that old helper response
from Y. The unit X rows give X output (x); the checked Y-from-X block gives
Y output (y+x). Finally (g_8) preserves X/Y and has helper output

\[
P_HM^{-1}Mg_1z=P_Hg_1z=h.
\]

For the backward word, order coordinates as ((x,h,y)). The complete unit X
rows, unit Y columns and checked Y-from-X block force

\[
M=\begin{pmatrix}I&0&0\\N&D&0\\I&E&I\end{pmatrix}.
\]

The finite square block (D) is invertible: if (Dh=0), then

\[
M(0,h,-Eh)=0,
\]

so invertibility of (M) gives (h=0); finite-dimensional injectivity implies
invertibility. Consequently (g_8) sends helpers to (D^{-1}(h-Nx)), while

\[
h_8(x,h,y)=(x,Nx+Dh,y).
\]

They are inverse maps. Also ((P_YMP_H)^2=0), so (g_{1i}=g_1^{-1}). Therefore

\[
g_{1i}M^{-1}h_8=F^{-1},\qquad B=F^{-T}.
\]

Taking the inverse transpose of the proved forward shear gives the claimed
backward shear. Transpose here is the algebraic transpose; all matrix entries
are rational. Rational identities extend to complex vectors by scalar
embedding. No clean-helper, independence or binary-input restriction is used.

## Actual scratch word and source binding

The completion matrices are defined in `Work/Carrier/Live.lean:184–191` and
used in `Work/GCert/Chain/Phased.lean:98–150`. The forward chronology is

```
erase copies; g1; MA; copies += Cc*helpers; y += Jr*copies; MB; g8; erase copies
```

The backward chronology is

```
erase copies; g1i^T; MAi^T; copies += Jr^T*y;
helpers -= Cc^T*copies; MBi^T; h8^T; erase copies
```

Here `Cc` selects the literal retained helpers and `Jr` is the literal star
matrix. The **22 scratch copies are distinct from the 9412 arbitrary live
helpers**. Erasing copies eliminates them to the scalar scatter forward and
its inverse transpose backward. Old scratch contents are erased, not restored;
all live helper contents are restored. The original chronological order with
swapped registers and negated coefficients implements an inverse transpose.

Omitting the completions is invalid. On input `x[0]=1` with other coordinates
zero, raw (M) leaves `helper[0]=1` instead of 0. On input `helper[0]=1` alone,
raw (M) leaves `y[0]=1` instead of 0. The actual completed (F) repairs both.

## Application to the existing bridge theorem

Set (A=(\operatorname{Fin}1320\to\mathbb C)) with pointwise abelian operations
and (H=(\operatorname{Fin}9412\to\mathbb C)). Encode banks/helpers into the
actual phased word with zero scratch, run that word, and decode. The argument
above proves both `Invocation` fields for this concrete provider.

The previously reviewed `Tintagel.Abelian.sourceB3_correlated_signed_endpoint`
therefore applies. For every parameter type \(\Omega : \mathrm{Type}\) (universe zero), every
\(p,q,r:\Omega\to A\times A\), every \(h:\Omega\to H\), and every
\(\omega\in\Omega\), use the same completed P193 provider at all seven calls.
The literal B3 word followed on each bank pair by the **signed** exchange
\((X,Y)\mapsto(Y,-X)\) returns \(([p(\omega),q(\omega),r(\omega)],h(\omega))\).
This specializes the existing source-bound bridge; no invocation contract is
assumed without its concrete finite discharge.

The bridge dependency is the actual published [PR397 commit
`a4e0135990efa1df734d8b9dd3af0f17cfae6f5d`](https://github.com/CrocSwap/integer-mult-bounds/commit/a4e0135990efa1df734d8b9dd3af0f17cfae6f5d),
with tree `33d0637863dde1a9a0658cfeb40bdfc4baa29363`. Its exact repository paths,
commit-tree blob identities and content hashes were retrieved and checked:

| Repository path | Git blob SHA-1 | SHA-256 |
|---|---|---|
| `research/tintagel-scalar-bridge-lean/BridgeChain.lean` | `18089b17513ecfe784a2c021dac41c4a9534fafe` | `a13c844c270f42ac585bb1d51339ba68ef9ffff161ff035b790d2428c4a86771` |
| `research/tintagel-scalar-bridge-lean/IndexedBridge.lean` | `3f65cc879800f73e612633fe11b0f4ca9af205f5` | `dc674afa79a98fb25275c9f23b6ad553ac3da48712e9a0528cb507be0784dbb3` |
| `research/tintagel-scalar-bridge-lean/SourceBound.lean` | `7e262f65dddbceb7b4590104ca1f4361a3e7791d` | `8ca546aa7adadc8f9ee1eca3d7583520e9baacb9195087dabb0a31ac67b9ffe9` |

Provenance: the prior reviewed local `SourceBound.lean` variant has blob
`3cbed9b63fcceeb9f493f68f2c25f7694228d219` and SHA-256
`ba4d2ebd2ce30e511e9b31a8ecaf8bf1cb0363b6cd4655935d019f5cb026e55f`.
The published version changes only the documentation phrase “fail-closed
AST recognition” to “hash-locked selected-AST recognition”. Every byte
outside that documentation comment, including all definitions and proofs,
is identical. The other two interface files match the reviewed local bytes
exactly. This application binds to the published files above; no proof was
changed to reconcile the pin. `review-evidence.json` records the binding.

The literal CrocSwap bridge source is `research/e8-seven-stage/code/complex/code/bridged.py`,
Git blob `626a28614b07066528fd5f189d87cffa5015ac60`, SHA-256
`5fe7174cd3a6580a74e4c1bf8fa7b426e8673f1c285603bf3076d4e758d70731`,
bound by the existing bridge packet to PR363 commit
`9df55dad6ddd05c3458793dfd82d1c2fe0ddbbb4`, PR373 commit
`3ff87b5dc0b22a57958547ee347d5da25b7f9401`, and PR375 commit
`79874623cf86d92325c26ccafc31413d12e9d248`.

## Offline replay and acceptance boundary

Use Python 3.9 or newer with an already available upstream source tree:

```sh
python3 check_p193.py --source-root /path/to/wht-power-saving-lean
```

The script reads and hash-checks the 29 files, rejects differing bytes, parses
the literals, recomputes the exact identities, rejects two first-addition
mutations, and compares its stable result with `certificate.json`. It writes
only progress/results to stdout, needs no third-party Python package and never
fetches sources. Do not use Python `-O` or `-OO`; they are explicitly rejected.
The SHA manifest can be checked with `shasum -a 256 -c SHA256SUMS`.

The Python replay still reports `lean_certified: false`: that field describes
what this exact arithmetic checker itself proves. `review-evidence.json`
preserves the earlier review and publication status. The later kernel result
is recorded separately in `KERNEL-RECEIPT.json`; neither Python nor C++ results
are imported as Lean proofs. The adapter uses the existing upstream
`GXD.P193.scalOK` computation to discharge its concrete scalar premises.

## Lean reproduction and scope

Use an already installed official Lean 4.34.1 and a separately rebuilt,
hash-checked dependency closure for upstream commit
`f010392c923279e3dd59ef3aa5fedad23affc5fd` and the package revisions in
`KERNEL-RECEIPT.json`. The independent audit rehashed 9,133 rebuilt modules;
2,357 official modules account for the remaining imports. This small supplement
does not contain those dependencies, their full rebuild manifests, or a download
script. Do not substitute unverified compiled artifacts.

In a new writable build directory, copy the exact `BridgeChain.lean`,
`IndexedBridge.lean` and `SourceBound.lean` from the sibling
`../tintagel-scalar-bridge-lean/` directory and this `P193Adapter.lean` into
`src/`, and create an empty `lib/`. Set `LEAN_BIN` to the installed Lean binary,
`LEAN_STDLIB` to its `lib/lean`, and `VERIFIED_DEP_LIB` to the independently
rebuilt dependency library. From that build directory:

```sh
export LEAN_PATH="$PWD/lib:$VERIFIED_DEP_LIB:$LEAN_STDLIB"
export LEAN_SRC_PATH="$PWD/src"
for module in BridgeChain IndexedBridge SourceBound P193Adapter; do
  "$LEAN_BIN" -t 0 -j 1 -M 8192 -DmaxSynthPendingDepth=3 \
    -R "$PWD/src" -o "$PWD/lib/$module.olean" "$PWD/src/$module.lean" || exit
done
```

Leave `autoImplicit` at its default. The four `#print axioms` commands at the
end of `P193Adapter.lean` print its upstream scalar premise, scalar provider,
invocation and endpoint dependencies. Every build must succeed; each of those
four outputs must contain only `propext`, `Classical.choice` and `Quot.sound`.
The independent audit additionally checked all 33 named targets and every new
declaration, an independently transcribed B3 word and endpoint, four positive
examples, and three sign/unsigned-exchange negative controls. Those broader
checks are reported with evidence hashes in the receipt; the commands above
repeat the four-module build and four adapter axiom reports.

The endpoint permits arbitrary bank/helper dependence on a common
`Ω : Type` and a supplied `ω : Ω`. The 22 scratch copies are initialized and
erased to zero; the theorem preserves arbitrary live helpers, not arbitrary
initial scratch contents. An empty Ω supplies no ω; ordinary inputs can use
`Ω = Unit`.

The audit's upstream commit-to-tree association relied on saved GitHub receipts;
it reconstructed source trees but did not authenticate raw commit bytes. The
publication step separately refreshes the three remote PR397 interface pins.
The external `gcert1-p11-pr193.json.gz` binding covers compressed/decompressed
identity and five scalar header fields only. Full serialized gate/frame-to-Lean
reconstruction and the original PR168/193 derivation remain outside this result.

This supplement establishes no geometric provider, stage/frame legality, label
or paid physical cost claim, all-size compiler theorem, analytic transfer, E8/bit
implementation, or broad B17 result. Existing Jacob Sussman scalar/helper and
bridge mechanisms retain their attribution; no novelty or priority is claimed.

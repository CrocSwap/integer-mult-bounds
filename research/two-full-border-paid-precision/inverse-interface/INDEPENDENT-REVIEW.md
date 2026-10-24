# Independent review of the inverse interface

Prepared by Yiyang (@Lyy-iiis), with substantial OpenAI Codex assistance from
a separate source-audit and implementation lane. Apache-2.0.

**Result: PASS within the explicit inverse-child, exact-arithmetic and
private-workspace hypotheses.** This is a source-level inverse-interface
result, not an admitted approximate Gaussian supplier or an improved bound.

## Reviewed bytes and executed checks

The source compressed SHA256 is
`7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05`;
its Git blob is `46d929df83817b85a5387bcdb9745e0627d6366e`.

| Artifact | SHA256 |
|---|---|
| `verify.py` | `6ea9ca67839bcaf6aa71566cfb40a166ae1ef7a756462106fcddafccde933d3a` |
| `RESULT.json` | `12195f89540df8f7462558abfafb5899a60fbba1d34a1fdb22ca1308dd9f261f` |
| `PROOF.md` | `753f0e1e7f6305ed550cb7247204190d9f4f258e07744e16ee55a35ee42e3f85` |
| Decompressed canonical inverse recipe | `01cb91d58b3fa64d31c1e8792a3998426fcff6da4caceed5ee71403ff9d62c85` |
| `independent_centers.py` | `fa57b5f7217864b3efed1dc5baa5f068a8b512d1ad26254b1ab3afe1b5466a39` |
| `INDEPENDENT-CENTERS.json` | `f0df352f947da218270671f43a3d0559d0f0a2a04ac7f0727adb3f4be89fe23a` |

The primary default read-only verifier passed under `python3 -I -O -B`.
The independent checker imports no primary generator or native evaluator.
Its receipt records 96 local round trips, eight complete two-coordinate
632-role round trips and five rejecting controls. Its complete forward and
inverse frame walks, separately for both retained source orientations,
each retain all 3,298 paid sites, 240 warp sites and 17,437 scalar contacts.

To replay the independent check from the repository root, with a fresh
output path:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -I -O -B research/two-full-border-paid-precision/inverse-interface/independent_centers.py --source research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz --output /tmp/independent-centers-replay.json
```

## Macro and frame review

The initial primary recipe covered only the forward source's COPY/fanout
macros. Review identified the retained backward source's different gather
shape. The final primary recipe and independent check now cover both.

The eight source macro starts are `11309+26*j`, for `j=0,...,7`. The
rank-eight frame IDs are `254,274,619,279,621,280,624,281`.

| Source orientation | Capture | Center frame itinerary | Fanout |
|---|---|---|---|
| Forward | One unchanged field, coefficient 1 | Listed rank-eight frame to frame 0 | 22 distinct fields, coefficients ±1/4 |
| Backward | 22 unchanged fields, coefficients ±1/4 | Frame 0 to listed rank-eight frame | One field, coefficient -1 |

In all sixteen macros the capture-role set is disjoint from the fanout-role
set. No capture field changes during the macro. Recomputing the identical
captured value and the same deterministic center map, then negating the
fanout, is therefore its inverse on arbitrary persistent inputs. The proof
does not reverse a nonzero CLEAR, invert the center map, or count the owned
buffer as productive output. Both clears remain present.

The reversed global order restores each persistent field to the same frame
it had at the corresponding original macro. Its capture and fanout frame
requirements therefore still hold, while the center's retained paid
orientation remains unchanged. Ordinary paid and warp boundaries reverse
their frame itinerary. The scalar inverse operations have the proper
source/destination frames and restore every endpoint frame.

The independent checker works in the scalar logical gauge and omits known
phase/adapter annotations. The primary stress test additionally assigns
invertible test maps to adapter nodes and reverses them explicitly. Neither
test reruns the inherited exact Clifford lowering or establishes a new
physical free-adapter allowance. The inherited source and its typed
normalizers remain the basis for that allowance.

## Conditional costs and remaining obligations

The macro replacement adds no declared paid calls. Each complete source
word and its inverse retain `{1:2201,2:412,3:510,4:127,5:40,8:8}`. The
center inverse uses the same deterministic child in the same orientation.

For the rest of the program, the result assumes the **actual inverse of the
same persistent-child realization**, available at the same declared rank
charge. It does not construct such inverses for arbitrary recursively
rounded child algorithms. Both child directions must restore private
workspace; an inverse of only a projected productive endpoint is not
sufficient. The serialized source exposes one reused owned register, which
does not establish a bound on opaque child-private storage.

Exact rational ADD/SCALE inversion and deterministic increment recomputation
are valid. The tests do not prove a uniform finite-grid precision bound,
absence of overflow, or reversibility of rounding a complete destination
sum. A sufficiently fine grid for a fixed finite dyadic computation is not
by itself a bijection on one fixed bounded grid for all future inputs.
The proof correctly keeps these costs open. Its final wording states zero
additional **rank calls**, without claiming zero precision overhead.

Finally, reversing a complete supplier reverses its productive-D orientation.
It does not automatically yield the second fresh-D supplier or preserve the
Gaussian/frame factorization used by the Laurent controller. Nonlinear
rounded bijections also do not supply the linear operator-ring identities.
These are remaining constructive obligations, not conclusions of the
successful local and whole-IR tests.

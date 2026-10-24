# The actual compact width and the local parking condition in N(i)

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0. This is a scoped source-to-caller invoice with an explicit implementation gap, not physical acceptance of the complete complex node.

## Caller and distinct hypotheses

The target is N(i) in `research/complex-stopped-recursion-cost/PROOF.md`: a node of width e and logical volume v must pay at most `c_N Lambda(p) v e^(1-a2)` for adapters, monomials, scans and parking. The source is Cinna Davis's `research/unconditional-batched-crt/COMPLEX.md`, its literal mixed PR4088 template, and Jose Manuel's PR2250 `research/selected-complex-compact-adapters/{compact,monomial,streams}.py` and PROOF.md sections 1–6. Exact bytes are pinned at canonical main `f259dabc7d70e0db8d6d36bfda888f008bbfecc1` in SOURCES.json. The retained PR2250 proof in `complex-record-amortization/source` is also pinned for attribution and comparison.

Assume the completed ordinary-interchange contract of BIT.md, including arbitrary complete spectators, owned output, erased work and local head return, at `a2 = 0.001733394791695384296`. Put tau = 1-a2. Assume the mixed finite identities and that each rank-r occurrence is one complete width-rf child of volume v/(W Gamma), with f = floor(e/73). That is the separate task08 hypothesis; this package does not prove its physical realization.

Two additional reached interfaces must be distinguished from the child-volume statement:

1. **Compact layout L.** Before each monomial row addition, the actual packet has two complete fK-bit wide slots, selected positions rho+jK, and complete `(f-1)G`-bit u,t,b fields in PR2250's required physical order. Every unused reservoir digit, remainder bit, high axis, label and suffix remains a spectator. The record length rho_record retains the full long suffix, and the local address/key length satisfies A=O(p).
2. **Local suspension P.** At a child boundary, the current node's serializable state occupies at most C_P v bits plus absorbed metadata. Only that state is pushed/popped. Its segment boundary is the stack head position on entry and return. Every reused work role is erased locally before it is handed to the child. The child and its ordinary callees do not rewind, read, erase or seek through older parked segments.

L and P are the exact missing caller contracts isolated below. They are not consequences of equal volume, endpoint equality, a scalar event list or O(V_root) total space.

## One actual F2 row addition

`monomial.py:execute_monomial` compiles a fixed binary matrix with `binary_word`; for f>1 it invokes `Compact(f-1,K,G,rho,control,target,late)`. `Compact.validate` requires each compact field to have exactly `(f-1)G` bits and each wide slot exactly fK bits. `Compact.operations` emits four swaps/four rotations for an earlier source or constant toggle, and twelve swaps/ten rotations for a later source. `compact.py:ordinary` records and uses the compact field width, not the number of selected columns and not the width of the full root reservoir. For f=1 the actual monomial caller uses elementary digit operations and emits no zero-width ordinary request.

Under L, one F2 row addition therefore has the source tariff

    12 K_O v_packet ((f-1)G)^tau
      + O(v_packet + M A^C + delta M A(rho_record+A)),
    v_packet = M rho_record,
    delta <= min(1,(f-1)(2*2^-G + 8*2^(G-K))).

Twelve is a valid common upper bound; the earlier-source case pays four. The fixed exponent C includes the ordered rotations, guard and inverse-key arithmetic and phase preparation. Gaussian sign/swap phases have linear payload traffic plus polynomial control preparation per complete record; role-level scalars remain scalars. The fixed native dimension gives a fixed number of row additions/toggles per recipe. There is no factor f outside the interchange width.

The actual COMPLEX.md choice is `G=4 ceil(log2 p)+6`, `K=128G`. Although PR2250's summary domain states the stronger `K/log p -> infinity`, its explicit sufficient proof condition is `K>=G+4 ceil(log2 p)+10`. The actual choice satisfies that inequality for every p>=2. For f-1<=p, writing L_p=ceil(log2 p),

    (f-1) 2*2^-G <= 1/(32 p^3),
    (f-1) 8*2^(G-K) <= 1/(128 p^3),
    delta <= 5/(128 p^3).

For the second inequality, `1024 p^4 <= 2^(127G)` follows already from `10+4L_p <= 127(4L_p+6)`. This uses the source's original guard and repair; it changes neither. Complete compact ranges are essential: no bound on a restricted bad-only fibre is inferred.

COMPLEX.md places a complete suffix of ceil(log2(p)^2) address bits, so its complete long record is at least `p*2^ceil(log2(p)^2)` bits. With A<=C_A p this absorbs every fixed polynomial preparation: if x=log2 p then `p^(C-1)/2^(x^2)=2^((C-1)x-x^2)` is bounded and tends to zero. The repair term divided by volume is `delta A(1+A/rho_record)=O(p^-2)`. The remaining ordinary term obeys

    ((f-1)G)^tau <= e^tau G^tau <= e^tau G = O(e^tau log p).

The finite initial range enlarges the constant. This proves the compact/monomial contribution under L and the ordinary contract. It does not validate L at every recursive entry. In particular, passing the unsplit root hG-bit reservoir to the actual source caller fails its exact field-width check when h != f-1. Splitting off the needed complete chunk with the rest kept as spectators is a required layout operation, not an extra Gamma division.

## The conditional complete nonchild invoice

Let J_M, J_S and J_C be fixed counts from the literal mixed source template: monomial invocations, scalar/packet scan actions and child boundaries per common cover value. They may be enormous, but are independent of e and p. Set W=322560 and B=W Gamma. The cover is fixed finite source data, not a dimension growing with e.

For gather/replace, a safe upper bound scans the entire current node for each fixed source family/cover/request, selects its declared complete rows with sequential encoded counters, and writes the packet. It retains the original copy until the literal word finishes. No random-access lookup or arbitrary sort is needed for this bound. A whole-node scan at every fixed cover value costs Gamma v, still a fixed multiple of v; a cover-filtered scan is not necessary for the asymptotic claim. Scalar COPY/ADD/CLEAR, fixed dyadic operations, entry/exit copies and zero-work initialization are likewise fixed numbers of full-volume scans. Their control costs are polynomial per complete long record and are absorbed as above.

Under P, every child boundary additionally costs at most C_P' v for the current-node snapshot, child input copy, return descriptor, local restoration, replacement and erasure. Charging the entire current node at every boundary is allowed: Gamma J_C is a fixed source constant. It does not require charging only the smaller child packet. Including root record labels and dirty parent streams changes the fixed state constant; it does not change W in the child moment.

Under the stated finite-template, ordinary, long-record, L and P hypotheses, the nonchild time at this node is therefore bounded by

    T_nonchild(e,v)
      <= Gamma [C_M J_M v (1+e^tau G) + C_S J_S v + C_P' J_C v] polylog(p)
      <= C_source v e^tau polylog(p),        e>=73.

Using v rather than the smaller packet volume in each summand is deliberately conservative and affects only the fixed constant. This is the desired N(i) inequality, conditional on the reached interfaces. It does not use the stopped-moment induction or recompute its root.

## Why geometric space does not supply P

Even with the child-volume hypothesis, the sum of ancestor logical volumes along one unfinished path is at most `V_root sum_k B^-k < 2 V_root`. That proves a space bound. It does not prove that suspending a width-e node costs O(v), because seeking across that ancestor history may cost V_root.

There is a countermodel on an admitted path of the actual positive rank-1 bin. For integer d>=2 choose `h=73^(2d)`, `p=h^2` and take d rank-1 children. The current node has `e=73^d`, `v=V_root/B^d`. It is internal for COMPLEX.md's root stop `s=max(73,h^eta)`, since eta=10^-32<1/2. The complete-domain condition h<=p^(1/2) holds. An implementation that scans/rewinds through at least the root snapshot at this boundary costs at least V_root, while the proposed normalized toll is

    v e^tau polylog(p) = V_root (73^tau/B)^d poly(d).

Since B>=W>73 and 0<tau<1, its ratio to V_root tends to zero. Thus no fixed polylog factor or constant can absorb this ancestor traversal. All endpoints and the geometric space bound may still hold in this countermodel. This is not a source bug or an impossibility theorem: it disproves the inference from geometric space alone to N(i) and states the locality that a correct implementation must provide.

Similarly, one full v scan per active axis costs v e. Taking e=p^(1/2) gives `e^a2/polylog(p)` unbounded. A factorwise implementation cannot be justified by calling that term polylogarithmic. The actual PR2250 batch avoids this loss when L holds.

## Exact artifact gap and bounded evidence

COMPLEX.md says to serialize inactive streams and return labels and cites geometric parked volumes, but supplies no uniform node-level tape request/continuation artifact with the compact slot views and segment origins required by L and P. The scalar `bw_emit.py` emits phases, scalar macros, climbs, centres and adapters, rather than these complete physical boundaries. The PR2250 simulator's `streams.Tape.rewind` returns to absolute zero and `erase` clears that tape's full data extent. Its documented local-input contract is valid; naively passing an ancestor-prefixed backing tape would cross or erase protected history. That naive embedding is not an admissible use of the source primitive.

The neighbouring physical support router and sparse XOR package have their own successful-input, supplied-shape and backing-extent qualifications. They do not claim installation of the mixed complex recursive suspension contract. The local #4100 coverage map's #4202 reference is a Discussion under shallow interior/tensor circuits, not PR4202 or evidence that this node boundary is closed. A live web fetch of that Discussion returned a cache miss during this session, so no claim about unobserved later comments is made.

`verify.py` authenticates the source bytes and executes the actual PR2250 lowering to inspect all-column request shapes, with payload execution explicitly replaced by a trace recorder. It is not a monomial endpoint test. It checks the reached guard inequalities and includes a tiny literal complete-row gather/relative-stack park/return/replace trace with dirty ancestors. That trace preserves borrowed data, every spectator/row and dirty history, returns the local head, and has the same payload movement count at several ancestor extents. It demonstrates the local protocol requirement, not an installed fixed-tape recursive allocator. Actual `Tape.rewind`/`erase` counterexamples and omission/width controls reject unsafe embeddings. Assertions are not used.

## Open next question and credit

Emit one actual FOUR-base child boundary, right/left compact layouts and inverse return descriptor, with every current-node role serialized and every older segment protected. Check the actual ordinary request width, work erasure and head origins. Extend that adapter over the finite mixed event inventory before claiming physical N(i); the task08 complete child request remains separate. No new generic allocator or full-cover runtime is proposed here.

Cinna Davis supplied PR4100 and PR4088. Jose Manuel (`jmbarrancoml`) supplied PR2250's compact adapters and physical-caller lineage; Douglas Colkitt supplied the retained compact algebra, guard and repair method. The stopped-recursion premise is JoyboyBrian's predecessor work. Matarener supplied #4424's cover/stock audit and padding correction. The BIT/parking/ordinary and native predecessors retain their existing source notices. No frozen predecessor files or selected frontier files are changed; no new kappa or multiplication theorem is asserted.

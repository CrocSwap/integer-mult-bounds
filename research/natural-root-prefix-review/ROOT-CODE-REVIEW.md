# Static code-to-contract review of natural-root production

**Result: conditional static PASS; no blocking connection defect found.** The
code supports producing the root A/R/H packets from the supplied T/R_body/w
packets and unary depth, then invoking the retained two-site bit grammar and
physically erasing the generated A/R. It does not produce its entry markers,
T/R_body/w/depth or the promised full payload from an integer input. It is
not a new supplier, native invoice, Gaussian leaf or frontier admission.

## Evidence, independence and exact boundary

This review reads source text only. Source PR6719 is pinned at
`e4e52d6ba2c805fa78bb57778c3b7bbc064edba5`. I independently checked raw length,
SHA256 and Git blob for the 18 inert objects (142,117 bytes) listed in
`SOURCE-PINS.json`, manifest SHA256
`8bb8211ef666ac5c28f5ed71d64abb33b69b900d8eecba0ece662fa0d0eebce3`.
The reviewed `recursion/root/root_prefix.py.txt` SHA256 is
`5c7e5982202298349498af39d510c77066140768e7d3ea80b0b125a8b3507e35`;
the source root proof SHA256 is
`0712baeaa4e8086f06800a21a9f0d916d29c8393966f58d624458b39368d2452`.
These checks authenticate bytes; they do not establish the program's theorem.

No source import, constructor invocation, emitted-table generation, machine
run, checker execution, numerical experiment or peer-draft reading occurred.
For the entry ABI only, I read the root checker's encoding/descriptor/put
helpers (lines46–60) and initializer (lines106–122). A bounded text search
also exposed function names and observer-check descriptions. I did not read
or copy its expected-output function or use its reported results. The source
proof and earlier core reviews were already exposed, so this is a source-aware
AI-assisted static review, not a blind reconstruction or independent execution.

The execution precondition needs all of the following, not merely the three
numerical descriptor values:

- All K+11 physical tapes are genuinely distinct, with
  K=max(16,L+11), L>=2, fixed odd q>=3 and N>=1.
- Each payload tape has its nearest outer raw LEFT marker; each global tape
  has its outer raw BASE marker. Data encode logical symbols as three raw
  Z/O bits. These outer markers are different from the encoded logical LEFT.
- T,R_body,w are positive canonical encoded packets with heads at their
  logical body origins. The complete input payload has the promised length
  and the same source ABI. Unary depth is raw O^d followed by physical BL,
  with its head at the first body position, including d=0.
- Root A/R/H, output, scratch, relays, control/phase and the reserved return
  body are initially owned blank regions with sufficient owned blank growth.
  Prefixes before the outer markers are external and must remain unchanged.

The initializer supplies those outer markers on **every** tape. Neither this
prefix nor the old core creates them. `Builder.origin` scans left to a known
marker; without the precondition it can run indefinitely or find an unrelated
marker. No invalid-input rollback or termination claim follows. Entry
preparation **time** is separate, open and nonzero; `K_entry` charges initial
physical backing **space only**, and cannot pay that preparation time.

## Exact roles and descriptor trace

Write p for the retained router ports. The relevant payload roles are root
A=p.repeats_input=L+2, root R=p.block_input=L+3, conversion scratch L+4,L+5,
L+6, grantA=L+7, grantR=L+8 and R-guide=L+9. The temporary dummy g uses the
reserved return K−1. All are distinct for every L>=2. The old global roles
end at H=K+8. The added readonly T and R_body roles are K+9 and K+10, beyond
every tape index in the old core. For L4 this gives 27 tapes, not a tape
allocation proportional to depth.

The old `recursive.py` lines203–210 first lower `high_program(b)` with
b=q^(N*N), using physical w, H, unary-width scratch and binary work. Width
is only read/moved; the converter restores its body head. The output starts
at one and is multiplied by b exactly w−1 times, so H=b^(w−1). The old
width guides and work are physically retired before its entry jump. This
semantic conclusion is conditional on the named counter/codec primitives;
no host width, power or decoded packet is passed to execution.

In `root_prefix.py` lines35–47:

1. `copy(T,A,source_marker=BASE)` copies the actual raw encoded packet into
   the empty owned A body. Explicit `body` calls restore both input T and
   owned A to their logical body heads. The copy itself only reads T.
2. `copy(H,dummy,source_marker=BASE)` likewise preserves H. The logical
   fixed-L multiplier is applied only to the owned dummy. It delivers
   g=L*H, with H and dummy at their logical body heads.

The nine-port `product(source,target,...)` mapping at lines49–55 is injective:
logical `(A,H,R,Aout,Rout,Au,Hu,Ru,work)` goes to
`(dummy,H,source,grantA,target,p.repeats,p.block,Rguide,p.binary_work)`.
Both call sites keep all nine distinct. The inherited producer receives
A=g=L*H, so its exact-division output is one and its product output is the
actual H*source. This is a real use of its quotient/product loops, not a
host multiplication hidden in a new primitive. The quotient and all four
guide/work bodies are physically retired after every call. Retirement scans
raw Z/O through coded logical 000 and stops only at physical BL; logical
blank data are not treated as erased physical cells.

Line57 first applies that product to the readonly R_body packet, delivering
R0=H*R_body directly into owned root R. The converter restores the borrowed
R_body and H heads. For each actual raw depth mark, lines59–66 deliver
H*A_k into the separate grantR body; erase old A; copy the new value back;
erase grantR; then apply the fixed-L multiplier. Thus the loop invariant is
exactly A=A_k=T*(L*H)^k. Source T/R_body and depth symbols are never written.
Each iteration advances the raw depth head once; on its terminating BL,
`origin(depth,BASE)` scans back across the existing marks to the original
body head. It also works for d=0: its first left move finds BASE immediately.

Finally the dummy g is physically retired. At the handoff, A_d/R0/H have
the exact old logical body heads, unary depth is restored, root source and
width retain their original states, and every reused temporary/return body
is blank at the old expected origin. Root A/R are owned delivered headers;
they are not additional independent inputs or credited targets.

## Link and final ownership

`build` lines93–118 constructs the old table, the root prefix and final
cleanup at compile time. On the L4/q3/N1 specialization it compares the
entire reconstructed old program and metadata to its retained table. This
is a code-path obligation, **not** a table comparison performed in this
review: no constructor/table is executed or regenerated here.

The link modifies exactly the jump immediately before old node entry and
the old unique halt. The code checks that the former is literally
`goto node_entry`, that the old halt is unique, and that the final changed-PC
list consists of those two locations. Relocation shifts every branch case,
branch default and goto destination. Prefix HALTs become direct jumps to
the old entry; the final cleanup HALT remains a real charged HALT. Writes
and moves retain ordinary next-PC fallthrough. Reject instructions remain
rejects, so invalid paths are not silently converted into success.

This preserves every recursive split/merge, grant, CALL/RETURN, phase and
output-before-pop instruction, conditional on the original constructor/table
equality. The old core cannot address the two new T/R_body tape roles. It
already preserves the borrowed root source, width and unary depth bytes and
heads under its contract. At root completion it erases H, then its former
halt now jumps to lines75–79: raw physical retirement of generated root A
and R, returning both heads to their owned blank origins. Original T,
R_body,w,depth and payload survive; the complete output remains live.
This does not rely on generated header values being zero.

For all d, exact divisibility is supplied by the prefix invariant:

    A_j=T*(L*H)^(d-j),  R_j=H^(j+1)*R_body.

At j<d, A_j is divisible by L*H. At j=d the leaf needs no child grant.
The child volume is V_j/L; the whole-high address identity, not volume alone,
binds its ordering: if a_parent=(a_child*L+l_child)*H+h_child, then

    a_parent*R_j+r_parent
      =(a_child*L+l_child)*(H*R_j)+h_child*R_j+r_parent.

Thus the prefix establishes the old domain and exact header ABI; it does
not create a new proof of the underlying router, stack or leaf primitives.

## Bill review and precise conditionality

The claimed root linearity is supported by the actual call structure. The
inherited producer bill for dummy input g, H and source X specializes to

    80*g + 58*H + 48*X + 24*H*X + 46

logical instructions. There is one call for X=R_body, and d calls for
X=A_0,...,A_(d−1). With g=L*H>=2 and d>=1,

    sum A_k <= A_d/(g−1),
    H*sum A_k <= A_d,
    d*g <= g^d <= A_d,  d*H <= d*g.

The second uses H/(L*H−1)<=1; the third follows from
d<=g^(d−1), proved by induction. These separately pay the repeated dummy/H
conversions, each current-A conversion, product and per-call overhead. They
do not charge d copies of final volume. For d=0 the repeated loop is absent;
the single root-R product and finite copies still have to be charged.

Each of g,H,A_d,R0,T,R_body is at most V0=L*A_d*R0, even at d=0. Fixed-L
multiplier work over all calls is bounded using its actual binary lengths
and the same geometric sum, with a template constant depending on ell(L).
The old H setup has its separate converter/fixed-b bill; w^2<=2*b^(w−1)=2H
for b>=3 covers its physical unary guide and cleanup. The unary depth scan
is charged because d<=A_d for d>=1. Binary descriptor length scans are
included, not free reads of supplied integers.

At the lowering boundary, inspection of `code_write`, `code_move` and
`code_branch` supports the inherited factor32: their respective paths use
at most9,13 and9 physical instructions per logical operation, before the
deliberately larger allowance for table entry/continuations. Raw copy/retire
and marker restoration are extra real scans. For space, their successive
guides/products grow within a fixed set of suffixes, bounded by the maxima
of g,H,A_d,R0. Erasure does not remove visited backing. Add prefix backing
and the core's active-chain backing; do not count sequential sibling reuse
as deallocation of previously visited cells.

The conclusion is a conditional `O_template(V0)` root setup/cleanup bill
plus the separately charged core occurrence sum. The displayed numerical
envelopes C_root=10^8*(K+ell(b)+ell(L)+1) and
S_root=1000*(K+ell(b)+ell(L)+1) are coarse source proof bounds conditional
on the named <=44x converter, amortized increment, producer extent,
factor32 codec and raw-helper scan bounds. This review did not independently
recertify every primitive bill or count a generated table, and does not
promote those constants to a new physical tariff. The actual two-site
recursion contributes sum_nodes V_node=V0*sum_j(2/L)^j; arbitrary final
templates retain their own occurrence/route/precision/lifetime obligations.

## Written controls and remaining obligations

The following are hand-derived contract controls, not executed tests:

- Skip depth rewind with L4,H1,d1,T1,R_body1 and zero payload. The depth
  head remains on terminating BL, so the root incorrectly takes its leaf.
  The intended depth-one grammar flips root indices0 and1; the wrong root
  leaf flips0,4,8,12. In particular index1 distinguishes their endpoints.
- Omit dummy retirement: even if a depth-zero output is correct, reserved
  return retains nonblank g at final ownership. On a call path its occupied
  parent return body also conflicts with later blank-target output delivery.
- Omit final A/R cleanup: the bit output may be correct while generated
  owned root descriptors remain live. Functional correctness alone does
  not satisfy the stated contract.
- Alias T with owned A, or another pair of producer ports: an immutable
  nonblank input conflicts with blank-target copy/work preconditions.
  Logical role names do not imply physical distinctness.
- Remove an outer marker: the leftward origin helper has no guaranteed
  stopping point. This is outside the promised ABI, not a free marker
  production theorem or guaranteed rejection path.

Remaining premises are exact valid initial encoding and outer markers with
separate preparation time, owned blank growth and charged initial backing;
the authenticated old constructor/table equality if actual emission is
claimed; converter/multiplier/producer/router/codec/stack correctness and
their stated bills; and the retained all-depth core induction. No finite
case, source checker result or constructor count was independently run here.
Producing T,w,d, the complete natural payload, numerical ancestor weights,
Good/Pair descriptors, Gaussian/BIT children and the full compiled supplier
remains outside this result. No frontier record is changed.

Credit: thu-nmrc and the source's disclosed OpenAI Codex/parallel-agent work
for the current root/core connection; Ali Romman/PR5829 for complete-fiber
whole-high geometry; David Arias/PR2776 for machine, assembler, counter and
physical-stream lineage; Mason Hale and the retained segment/codec/owned
return authors for suspension and protected output. The new contribution
here is an external written code-to-contract review of this root boundary,
not a claim to their algorithms or independent human acceptance.

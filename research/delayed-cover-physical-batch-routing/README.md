# Literal delayed-cover routing and recursive shape production

This package physically implements delayed-cover split/return, root shape
production and on-path child descriptors in a fixed-width recursive grammar.
The new program receives positive binary T, R_body and w, unary depth d and
an arbitrary complete payload. A,R,H start blank. Literal tape instructions
produce

    H=q^(N*N*(w-1)), A0=T*(L*H)^d, R0=H*R_body,
    A_child=A_parent/(L*H), R_child=H*R_parent.

Every child produces its own next grants from its live frame before suspension. One finite
instruction table controls split, two statically named child sites, physical
suspension, protected output-before-pop and merge at every finite depth.
No runtime host arithmetic, decoded descriptor, host recursion, callback or
per-depth tape allocation supplies these operations. The leaf complements bits;
an ordinary BIT/Gaussian supplier remains a separate obligation.

For L=4,q=3,N=1, the complete natural-root program has 31,821 instructions on
27 fixed tapes, independent of width/depth. From T=R_body=1,w=2,d=2 it generates
root A144/R3/H3 and executes seven actual nodes and six physical returns:

    (A,R,V)=(144,3,1728) -> (12,9,432) -> (1,27,108).

This case uses 1,449,116 microtransitions and 23,807 visited cells. Original
input bytes and heads survive; generated root/child grants, guides, relays,
control and scratch are physically erased. Erased backing stays charged.
The same table runs four natural-root cases. Five actual instruction faults
reject; the stale-H fault passes one edge and fails at grandchildren.

[recursion/root/PROOF.md](recursion/root/PROOF.md) proves root production and its
O_template(V0) setup/cleanup bound by geometric growth, including d=0. The exact
retained [recursive core proof](recursion/core/PROOF.md) supplies the all-depth
address/return induction and actual occurrence-sum time/geometric active-chain
space bill. For the two sites, sum_nodes V_node=V0*sum_(j=0..d)(2/L)^j.
These are scoped written proofs, not conclusions inferred from finite tests.
The full tree is not assigned the isolated router's 94V bound.

## Retained stages and provenance

The original [PROOF.md](PROOF.md), core/, independent/, composition/, shape/
and shape-independent/ remain exact earlier stages. Their one-edge limits and
ten-replay description refer to those stages. The isolated split/merge still
has L+7 tapes and bounds 94V time/13V visited cells. The separate router/shape
walkers retain their original coverage; they are not a second interpreter for
the new recursion.

recursion/core and recursion/root retain exact frozen production packets,
tables, receipts and FILES manifests. The root packet contains the complete
unchanged core; only two declared instruction links change in its linked table.
The new recursive builder/root prefix are authored in this publication. Eight
retained inputs have actual 3bad Git-tree/blob pins, in addition to the original
thirty generic source pins. recursion/CUSTODY.json authenticates the two new artifact
manifests; a private seal is not a historical source or scientific admission.
recursion/REVIEW.json records separate author-side static/source/proof review
and targeted controls. Historical pending-review fields in frozen packets are
preserved; the later review does not rewrite their evidence.

PR5829 by Ali Romman supplies whole-high addresses, V/L contraction and allocator
lineage. PR2776 by David Arias supplies the finite machine/counter/assembler.
Retained stack, codec and protected-return sources keep their original credit.
Generic arithmetic, Good/Pair/ancestor evaluators and geometric sums retain
predecessor credit; the new result is this source-bound literal connection.

## Reproduction and limits

Python3.12, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/delayed-cover-physical-batch-routing
```

Eight registered commands execute fourteen scientific replays in normal and
optimized modes. The first six commands are unchanged. Each shape_checks driver
retains the original two checks, then runs the authenticated recursive core and
natural-root checks. Standalone scientific checks need no Git or network and are
read-only by default. Verification orchestration is outside the literal runtime.

Outer integer-input T/w/depth production, numerical ancestor weights, actual
BIT/Gaussian leaves, final-template route/fallback/stock and precision remain
separate interfaces. The actual final template keeps its own call multiplicity
and complete bill. All five project assumptions remain. No new paid profile,
kappa, selected-frontier change or external scientific acceptance is claimed.

## Open next questions

- Bind one exact numerical ancestor-weight or ordinary BIT source obligation to
  this recursive skeleton, with actual ports, ownership and complete pricing.
- Produce an outer descriptor or final-template route/precision interface before
  considering a whole framework-assumption discharge. TASK.json records blockers.

Prepared for thu-nmrc with substantial OpenAI Codex and parallel-agent assistance.
The separate reviews are author-side AI-assisted evidence. Original notices
remain exact. Apache-2.0.

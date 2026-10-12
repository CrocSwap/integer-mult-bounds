# R715 reordered deliveries and whole hosting

Reconstruct PR467 from the exact PR463 pre-kernel word, its original99 shared-donor pivots of entrance rank118,56 target-prefix receiver transformations,60 single-gate retimings and14 connected-pair retimings. The stored parent word is matched exactly. Remove the old kernel corrections and reset its pivot entrance frames while retaining the target mixing and retimed original gates. Exact rational-span/F2 replay verifies this precursor; reapplying the old kernel restores the parent's exact local profile. Select a new shared-donor kernel:105 pivots of total entrance rank113, with104 donor slots. The new word is checked independently. Its11 entrance spaces are coordinate subspaces with explicit complementary permutation routes. After this reconstruction, apply the frozen delivery transformation sequence. Each reordering step changes only listed gate frames and stably orders B by frame dimension. For every two scalar ADDs whose destination is an operand of the other, preserve their original relative order; all other B ADDs commute because helpers are constant and their target destinations only accumulate additions. The 280 noncommuting pair constraints are checked before replay. The transformation does not assume that donor-target deliveries may cross a mixing read. Interleave these steps with primitive single/pair frame changes, each bound by input/output word hashes and old-frame assertions. Exact rational source-span and F2 replay verifies the final chains and formal operator. The frozen witness contains20 reordered gate-frame moves and14 connected-pair timing moves; the final alternating round has no further move in that scope.

Pool eight replicas when assigning each whole residual to a pending idle block.
Each occurrence has exactly one physical owner and one contiguous complementary-rank
slot on that family. No residual crosses a physical-family boundary. The
assignment is expanded for all62920 occurrences. A host may lie in another
replica, but its pair is untouched by every local call or bridge throughout
the inherited window. Calls remain sequential, and all private work is erased
before reuse. At each call, the whole-family permutation selecting an idle
owner is followed by the unchanged residual isometry and slot-coordinate map.
The existing complete-call correlated-dirty-helper interface applies to the
borrowed family irrespective of its replica number. Residual coordinate
factors on disjoint pending subspaces commute; each later idle child retains
exactly its unused coordinates. Both the family permutation and the existing
isometry are charged. This uses the same whole-residual interface as PR456,
not the challenged factor-splitting argument of PR448.


## A fresh bound on intermediate integer growth

The old independent-replica prefix charge is not reused. Track a nonnegative
row-L1 envelope for each physical family in the actual schedule, initialized
to1 for every borrowed/data family and0 for cleared private work. For each
literal ADD on physical owners, update B_dst += |coefficient| B_src, even if
both logical roles name the same physical family. COPY copies the bound to
the private stream; erase resets that stream to0. Include every bridge shear
in chronological order. Climb/route operations in the bit supplier are address
permutations and do not increase this envelope. Updating an entire-family
bound overcharges restricted-coordinate operations. Thus induction bounds
intermediate values independently of cancellations or correlations among
borrowed inputs, within the retained cover/compiler interpretation.

The maximum takes807bits, charged832. The finite coefficient takes807bits; its three-level composition takes2477bits, charged2496. Each bootstrap cutoff uses the new2496-bit charge. The complete row coefficient is19431<20161. Maximum child56 satisfies78^3>2*56^3. Owner reassignment costs retain the two extra selector factors.

The exact bit lower is258628981874989456643/200000000000000000000000. PR458 complex lower is1297203880559577927527/10^24. Six bootstrap levels and47 strict outer inequalities yield kappa645737422626611/500000000000000000 =0.001291474845253222; adjacent-grid and invalid-parameter controls reject. The final bit emitted profile is recorded in EXPECTED.json and independently recomputed from1720752events.

Full default verification runs the pinned complex supplier with the documented PR460 metadata-only portability adapter, then every new bit check. Explicit reuse checks a completed full complex receipt and emits a distinct status. Only two non-proof floating discovery report fields are normalized; all pinned source bytes and exact reconstruction checks remain unchanged.

This retains the complete-call correlated-dirty-hosting, compiler, mutable-basis/target-label, compressed-window, restored-work, common-grid/tape, precision, row and analytic contracts. It is a conditional finite construction, not an unconditional multiplication theorem, new Lean proof, global optimum, or proof of cross-family residual splitting.

# Complete packet-loop backing envelope

Source inspected: unchanged PR2697 `a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`, `research/selected-bit-node/packet_engine.py`, its `vendor/packet.py:read_prefix`, `vendor/bitstream.py:copy_bits`, and `vendor/records.py:Tape`. Related predecessor: PR2874 `08dd02bd8d8b1fadc5fe8589c2d2875d21fe5fce` counted the prefix-return cuts alone. Two separately delegated AI source/lifetime derivations agreed before reviewing the primary checker. This is neither independent human nor formal-kernel verification.

## Domain and metric

Successful invocation, at least two primitive passes, N>=1 prefixes, F>=1 payload symbols per prefix, common fresh-prefix backing Q>=2, directory backing D, and borrowed source backing K>=NF+1. Include the separately retained Consumer preflight `first` of backing Q; it is distinct from source, directory and all fresh arrays. Each payload factory returns a fresh native Tape with one LEFT; each action keeps the identity and backing length F+1 of local throughout its execution and returns a distinct, fresh F-symbol result of backing F+1. Caller backing lengths must not grow during the action; endpoint content restoration alone is insufficient. Local content preservation is unnecessary for this storage claim. No retained aliases among those arrays other than the stated source/current and current/output aliases. Successful fresh directory parsing implies D>=1+N(Q-1); use actual D when padded. Enter/return events do not alter packet roots or allocate cohort payload/record arrays. No external capture or retention by observer/factory/action counts as reclamation.

Metric: sum `len(Tape.cells)` over distinct arrays in the explicit cohort. Includes LEFT and cleared retained entries. Excludes allocator capacity beyond bytearray length, implicit blank positions, count/control tapes, numerical arenas, Program, layout/event/source objects and externally retained owners. Clearing does not shorten cells. This is a named-cohort lemma, not a total memory theorem.

Let t be primitive ordinal, j the number of already copied prefixes, 0<=j<N. Current aliases source when t=0. For t>0, current is a distinct NF+1 array. Within a pass output has jF+1 entries before its next prefix, and reaches (j+1)F+1 while copying the changed result.

## Three cuts and two exact structural maxima

1. Prefix read return before assignment to `fields`: except the very first cut, stale `local` and `changed` each retain F+1 entries, stale fields Q, fresh fields Q, preflight first Q. Thus

   R(t,j)=K+[t>0](NF+1)+(jF+1)+2(F+1)+D+3Q.

   The first cut has K+1+D+2Q. Maximum attained at t>0,j=N-1:

   R=K+(2N+1)F+4+D+3Q.

2. Copy-complete before `finally` cleanup: local and changed each F+1; no fresh/previous prefix overlap, so record contribution D+2Q. Output now (j+1)F+1. Thus

   E(t,j)=K+[t>0](NF+1)+((j+1)F+1)+2(F+1)+D+2Q.

   Maximum attained at t>0,j=N-1:

   E=K+(2N+2)F+4+D+2Q.

3. The `factory()` right-hand side in `local,changed=factory(),None` creates a new LEFT while old local/changed remain. It has the same source/current/output and stale payload terms as cut 1, plus one fresh LEFT, but only D+2Q record entries after assigning fields. Since Q>=1, this temporary cut is bounded by R(t,j). The analogous new-output factory RHS at pass transition counts the old output only once with current, plus the new LEFT; it is bounded by the next R(t,0). Factories are here atomic native one-LEFT constructors; other factory-owned scratch belongs to a separate contract.

All remaining structural cuts are dominated: prefix read grows only to Q; local copy grows only to F+1 after dropping old local/changed; changed-result copy grows output monotonically to E; clear/rewind retain array lengths; assigning current=output aliases those two names and drops the preceding current binding. Initial cuts and first-pass versions have no extra distinct current NF+1. The final return has current/output aliased and is no larger.

Therefore exact maximum of this explicitly defined caller cohort, including pending fresh return arrays at structural assignments, is

   max(R,E) = K+(2N+1)F+4+D+2Q+max(Q,F).

The F/Q comparison is material: if F>Q, using the prefix-return maximum as a whole-loop maximum understates this cohort by F-Q. This is an extension of PR2874, not an error in its explicitly return-only claim. It differs from PR2743/PR2731's nonblank payload bounds by retaining erased backing and record arrays.

## Composing action interiors without double counting

During action invocation, packet-engine `changed` is None. Define action-owned arrays as every fresh array reachable inside that one action, excluding borrowed local and every other caller-cohort array. Include any eventual returned result in this action-owned set until the action returns. Let their total backing be <=A. Distinct ownership is essential; never add the same returned-result array both as `changed` and as action-owned.

The suspended caller portion at an action interior is exactly

   C(t,j)=K+[t>0](NF+1)+(jF+1)+(F+1)+D+2Q.

At all such sites C<=K+2NF+3+D+2Q, attained structurally at t>0,j=N-1. Consequently the caller-plus-action cohort has upper bound

   max(R,E,K+2NF+3+D+2Q+A).

An action can be specified instead by A=F+1+S; then the third term is

   K+(2N+1)F+4+D+2Q+S.

This S is an allowance AFTER reserving one complete F+1 returned-result envelope. Do not define S merely as all arrays except `result` unless that result is identified throughout every interior: before result creation, other arrays may already exceed S. Safer contract: total additional action-owned backing <=F+1+S. On the action-return seam, the result becomes caller-owned changed, action-owned scratch ceases to be included only under its last-owner/disposal premise, and the ordinary E bound resumes. If an action leaves retained scratch in any external owner, that storage remains a separate obligation and cannot be discarded from a total reserve ledger.

No universal sharpness claim for the A or S expression follows from an upper-bound-only action contract. The structural max(R,E) is sharp; an action fixture that attains A at the final prefix can corroborate sharpness in that fixture model.

## Verification targets and limitations

The primary runtime suite covers F<Q, F=Q, F>Q; N=1 and multiple prefixes; three passes; oversized source backing; intra-pass and cross-pass stale fields; source/current alias in the first pass; copy-complete and factory-RHS cuts; and nonzero synthetic private scratch with returned-result membership counted by identity. The independent symbolic model also covers padded directory backing and the fact that an early-only scratch peak need not attain a uniform composition upper bound. Runtime failure controls reject prefix-only and copy-only maxima, an omitted preflight Q, and unpriced private scratch. A literal engine counterexample grows borrowed local backing during an action and restores it before return, demonstrating the necessity of the stronger interior invariant. Separate tests reject malformed domains, altered source/manifest bytes, source-module preloading and typed-receipt substitutions.

This does not price native ADD/swap/sign action scratch, counters/continuations/numerical storage, arbitrary event generator state, a physical last-borrower allocator, failure cleanup, recursive callers, full selected GL64 execution, supplier admission or kappa. Input-origin, success, backing-length preservation, freshness, and field-size premises remain explicit. The reader's cleared remaining.tape and Consumer.apply.fields count Word are excluded count/numerical storage, distinct from packet_engine.fields prefix Tape. A complete selected primitive bound needs its own source proof before substitution for A.

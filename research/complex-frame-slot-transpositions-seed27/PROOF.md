# A closure barrier for commuting ADD moves with fixed frame slots

The input is the exact PR1042 R480 seven-slot word selected at the frozen base, member `slots/local/FULL-WORD.json.gz` of `research/community-frontier1042-audit/selected-replay.tar.gz`, with decoded SHA-256 `c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8`. Its A and B stages contain 3,451 and 1,846 scalar operations.

## Class and theorem

In each stage, keep the ordered list of frame label subspaces fixed at its original positions. An elementary move exchanges two adjacent ADD operations, including their registers and rational coefficient, while the two frame slots remain in place. The two elementary linear maps must commute. Scale operations cannot move or be crossed. The stage must obey every label-subspace containment check, with its original entrance and exit label frames. The A/B separator and all other word sections are fixed.

Consider any finite sequence of these moves in which each intermediate word passes these checks. **Every reachable word has the same paid local climb profile as the input.** In fact, no gate crosses a boundary between distinct constant-frame runs, regardless of earlier moves within those runs.

The checks use the F2 label-span model of `independent/audit_local.py`: a register can be used in a frame U only when its current label span is contained in U; its frame then becomes U and the dimension increase is charged. These are necessary conditions for the retained supplier interface. This package does not claim that passing them alone proves native, Clifford, physical, precision or hosted legality. Excluding moves under this relaxed model also excludes them under any stronger model with the same necessary conditions. The fixed stage exit frames are an explicit restriction of the studied class.

## Commutation and movable gates

For nonzero coefficients q,r and distinct destination/source indices, the ADDs i<-i+q*j and k<-k+r*l commute exactly when i!=l and k!=j. This follows by multiplying I+q E_ij and I+r E_kl; the two possible cross terms vanish precisely under those conditions. The verifier also multiplies the two maps over Q on all coordinates they touch for every tested crossing. Thus any allowed swap preserves the complete scalar map on arbitrary input dirt, not just clean inputs.

Partition a stage into maximal consecutive runs having the same label subspace. Within one run, a particular ADD can be moved to the end using permitted swaps if and only if it commutes with every later operation in that run and every such operation is an ADD. Necessity: the chosen occurrence must reverse its relative order with every later occurrence, and an adjacent swap can reverse only a commuting pair. Sufficiency: bubble it right in the original order. The corresponding statement for the start of a run uses every earlier occurrence. Non-ADD operations are fixed barriers, including scales sharing the same frame.

Therefore, for neighboring runs [a,b) and [b,c), every possible first crossing is exposed by some pair i,j where i is movable to the left run's end, j is movable to the right run's start, and i,j commute. A representative schedule is

    left run except i; j; i; right run except j.

The fixed frame slots still put j in the last left slot and i in the first right slot. The exposure moves are themselves legal inside the constant-frame runs. They do not alter the set of registers touched or the frame at the end of either run.

## Why one representative per exposed pair is complete

For a constant-frame run U, every touched register ends at U; its state before its first touch is its entrance label span. The order of operations otherwise does not affect label frames. Hence, once i and j are specified, all possible internal exposure orders have the same relevant frames immediately before and after the crossing. Registers not touched by i or j keep the same frame evolution up to harmless ordering inside each run. Checking the representative therefore covers every within-run exposure of that pair.

The fast checker recomputes the two runs on the at most four registers touched by i,j, then checks each changed register's next unchanged touch or its stage exit. The second checker constructs the entire representative stage, begins at its actual input frames, and checks every register use and the complete exit vector. Their outcomes must agree for every crossing. The receipt hashes the deterministic rejection transcript and gives representative witnesses.

## Complete finite census

| Quantity | A | B | Total |
|---|---:|---:|---:|
| Stage operations | 3,451 | 1,846 | 5,297 |
| Unequal-frame boundaries | 482 | 1,184 | 1,666 |
| Exposed pairs | 1,441 | 10,407 | 11,848 |
| Noncommuting exposed pairs | 14 | 23 | 37 |
| Commuting pairs tested by both checkers | 1,427 | 10,384 | 11,811 |
| Accepted boundary crossings | 0 | 0 | 0 |

There is no search cap, random sampling or optimizer. The initial adjacent-only census separately finds 3,440 commuting pairs, of which 1,925 pass the label checks. Every passing pair already uses equal frames. This initial result is not used as a substitute for the exposure census.

Every one of the 11,811 crossing rejections is a failed subspace containment during the stage; none relies only on a changed exit frame. The receipt records these rejection reasons separately.

Suppose a reachable word had a gate outside its original frame run. Choose the first move in its legal path that crosses an unequal-frame boundary. All preceding moves stayed within the original runs. By the movable-gate characterization, this first crossing is one of the exposed pairs tested above; by the order-independent label-frame argument, its representative has the same legality. The census rejects it, a contradiction. This proves the claimed closure for paths of arbitrary length.

## Exact paid-profile invariance

Inside one constant-frame run U, each touched register r contributes exactly dim(U)-dim(F_r) if positive, where F_r is its entrance frame, independently of the gate ordering. All later touches in that run cost zero. A within-run permutation preserves its touched-register set, and hence its exit frames and entire profile. Applying this run by run proves invariance over the reachable component. The untouched center routes, early cleanup and terminal promotions contribute identically.

The verifier independently recounts the input's full local profile, including those fixed sections, and reproduces

    H = {1:2412, 2:418, 3:432, 4:142, 5:82, 8:8},
    sum_r r H_r = 5586.

Thus every paid moment determined only by H is unchanged; no numerical exponent approximation is needed. Gate count and the complete scalar endpoint are also invariant under the moves.

## What remains open

The theorem does not cover changing frame slots together with gates, noncommuting circuit identities, moving scales, crossing the cut or other sections, moving several gates in one step, or paths whose intermediate words violate the label checks even if their final word is legal. It also does not independently certify the baseline native/Clifford/physical construction, precision, wrapper semantics or global owner map. Within-run reorderings can change coefficient prefixes; this obstruction claims no new precision admission. No new supplier or kappa is proposed.

PR815 already reports commuting-reorder annealing with exact frame re-solving on older PR626/741 words. Its simultaneous frame optimization is outside this theorem. The contribution here is an exact first-crossing obstruction and complete reachability argument for the actual selected R480 frame-slot schedule, not a claim that commuting reorder research is new.

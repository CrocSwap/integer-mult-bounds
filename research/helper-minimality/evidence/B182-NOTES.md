# B182: Lawler certificates on the "uncovered" helper classes of #799. VERDICT: 0 removable, all certified (scope below). ship=false, no kappa claim, no oracle run needed. No heavy jobs (single process, <1 min).
Tool: b182.py (reuses B171 lawler799 + B172 lawler; generalises copy detection: first op filling an empty row t>=v from a nonempty source; bridges = class 'BR').
## Bridge registers 716..727 (12)
- Role: 4 groups (716-719 around 712-715; 720-727 around 133/149/159/222). Start frames 423-427. Phase 1 (B 311-378) is VALUE-ZERO: empty rows used purely as frame couriers (e.g. 190,211,155,216 += +-1/2*716; 716 += 717/718/719). Phase 2 (B ~1178-1189) each becomes an 8-support copy of one S3 helper (716<-528, 717<-529, 718<-516, 719<-517, 720<-494, 721<-495, 722<-518, 723<-519, 724<-530, 725<-531, 726<-506, 727<-507). Phase 3 (B 1878-1916): swap with 714/715-type registers (X+=bridge, bridge+=-1/2 X) then flushed into 155/216/159/... with coeff -2/+1.
- Lawler (post-copy visits of source+bridge, no precedence, as B171): 12/12 FAIL (each chain alone passes) => no bridge merges into its source helper under any reorder.
- Merge into any OTHER register: the 12 fill rows are pairwise non-proportional 8-supports with overlapping lifetimes (B1178..B1916) => value-impossible without extra undo/redo ADDs.
- Phase-1 frame-courier role is ignored in the test (pre-copy visits only add conflicts), sound for a FAIL certificate.
## Entering helpers 450..457 and 6-frame/24-30-frame holders 484..569
- These are S3 packet copies; the 94 copies in these ranges (ledger S3) all FAIL Lawler too (94/94, chains-alone ok); consistent with B171 268/268. B169 already showed holder reuse is legal only for 450..457 (8 slots, #869) and illegal elsewhere (final caps).
## Proven minimal (KPR3 material), scope: #799 op multiset fixed, value-forced lower-bound frames, caps = reached-target ports
- bridge 12/12, S3 holders/entering 94/94. Removable: 0.
## Not covered (unchanged)
- Multiset-changing merges (undo-ADD of a source then reuse); precedence-aware variants unneeded; no independent second-reader audit of g/caps; S1 (0,1,*) blocks (B177).

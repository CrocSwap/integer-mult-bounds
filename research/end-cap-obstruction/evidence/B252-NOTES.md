# B252 NOTES - VERDICT: with the true final y cap perp(P_t) (B253 caps.py) NO class is deletable. 0 of every class. Nothing to chain.
Before the caps check, the pre-cap gauge-forward gates (explicit frames + hyper(P_t) y reads, scalar identity) said more, but ALL of it is invalid (every word fails caps.py; base passes []).
## Pre-cap counts (gauge-forward, GLAZY=1, tool cgx_y.py = cgx_x + RO/WRC; S3 copies = 144 of 480; S1 = 224 block-local helpers, no copy ops; S4 = 112 slots)
Roles of the 144 S3 copies by consumer (W = consumer merge writes it, r = merge reads only, S = selected y load): SS16 rr32 Wr32 WW32 WS8 SW8 rS8 Sr8.
- rr 32 (G4's "64 value-redundant" = rr32+SS16+rS/Sr16): passes alone and together (NH 448), any stagger, GLAZY needed (no-GLAZY: frame violation). Caps: 0/32 singles OK (4 y fail each).
- SS 16 (B245 set, STAG hubs first, GLAZY, CF=0..15): NH 464, 32 widened explicit events (3->5). Caps: all y160..175 fail (B253).
- Wr 32 (one consumer reads only, other writes: delete copy, order merge of the reader before the writer; acyclic, no stagger needed): passes pre-cap, NH 448. Caps: 6/6 singles tried fail (4 y each), all-32 fails.
- Combos pre-cap: rr+Wr NH 416; rr+Wr+SS NH 400. Caps fail (y120.. etc).
- Blockers: WW32 (both consumers write: value needs the copy). WS/SW 16: assert 'second' (y cap at selected second load, needs second loads before merge). rS/Sr 16: 'second' alone; cold-first needs sender before S consumer but mutual 0246<->0257 style 2-cycles, so block-order impossible (needs event-level order, not done).
- S4 slots 112: not tested by run: each slot is written by the pair mixer (add(a,b),add(b,a)), so sharing breaks value; coded route 0/112 (B247). Count 0.
- S1: not copies (224 working registers); none.
## GLAZY enabling cost alone
No deletion: 0 widened events, 0 mass (profile identical to base, NH 480, mass 6312). Cost appears only with a deletion: SS16 = 32 events + mass +16 vs formula; rr32 = 0 explicit events but climbs (profile H6/H7 shifts, mass +48 vs formula).
## Price bands (pre-cap, w1018 convention of B247 mapping H6/H7->r H1, reproduces gall +1.34/+2.02/-0.35) -- MOOT given caps
gall SS16: H1 -0.35, H16 +1.34, H48 +2.02. rr32: -2.31/+0.78/+2.05. rr+SS48: -2.64/+2.14/+3.52. rr+Wr64: -4.15/+2.64/+3.52. rr+Wr+SS80: -4.47/+3.52/+3.52 (H48 cap is the same as 64; credit saturates).
## Flags (pre-cap only; run via q.sh/run.sh tag, env)
SS16: STAG=1 GLAZY=1 CF=0..15. rr32: GLAZY=1 RO=10,11,12,13,16-19,26-29,34-37,40-55 (idx in ROL). Wr32: GLAZY=1 WRC=Wr WR=all. All: STAG=1 GLAZY=1 CF=0..15 RO=<rr> WRC=Wr.
Fix needed for any of these: the final y cap perp(P_t) (y ends at 9 after the widened climb); a gate must include caps.py before counting. Not tried: re-planning y ladders / hosting the widened register elsewhere.

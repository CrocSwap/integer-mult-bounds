# Eight B-frame coalescences after SW4

**Conditional κ = 0.001661202643272239** (`1661202643272239/10^18`). This improves independently replayed PR699 at `03e8d7ca494a083e5053cd6b1228f66b98414479`, κ = 0.001660666354374641.

Eight B-gate frames grow from dimension four to six. This merges paid rank jumps without changing any scalar gate, entrance, terminal frame, helper width or physical owner assignment. The input is PR699's four read exchanges on its four-promotion p6n word. The complex side binds; PR589's bit supplier and surcharge are unchanged.

| Quantity | PR699 | This word |
| --- | ---: | ---: |
| Local profile | 1:2548, 2:342, 3:438, 4:186, 5:56, 8:8 | 1:2556, 2:334, 3:430, 4:194, 5:56, 8:8 |
| Local rank mass | 5634 | 5634 |
| Residual width mass | 3778 | 3778 |
| Helpers / native columns | 504 / 728 | 504 / 728 |

The global profile is `{1:184033, 2:24048, 3:30961, 4:13968, 5:4032, 8:576, 44:1, 48:2396}`, with rank mass 520704 and deficit 2560. Idle children are exactly 2,396 of rank 48 and one each of ranks 44, 3 and 1. The exact complex lower endpoint is `1663966829367501881629/10^24`; the bit endpoint is `1733427039589844234749/10^24`.

## Reproduce

Python 3.11+ and the standard library suffice; no network or optimizer is needed:

```bash
bash research/complex-sw4-frame8/verify.sh /tmp/sw4-frame8-fresh
```

Use a new output directory outside the package. Set `SW4_FRAME8_PYTHON` to select Python. Assertions must remain enabled; allow several minutes.

The driver freshly replays PR558 and checks the pinned ancestral inputs consumed by global admission. It rebuilds gauge44, the no-triangle word and the original gauge44 control, the layered 66-end word, p6n's 72 ends, four promotions, four read exchanges and the eight new frames. The final word passes all 728 arbitrary-dirt columns in both orientations, 2,953 phase edges and residual wrappers.

Controls include 30 pivot mutations, 59 intermediate layer mutations, 95 p6n end mutations, 11 promotion mutations, four SW4 checks (one positive, three negative), three frame-recipe pin mutations, ten focused final-frame mutations, 95 final end mutations and nine owner-certificate mutations. Global verification includes 69 admission mutations, 12 bit-supplier mutations, two exact moment engines and 47 strict outer constraints. Independent scalar/frame/cone and literal-owner/profile/rational-moment checks must agree.

The integer flow/matching certificate and one helper permutation reconstruct all 36,288 owner roles byte-for-byte. `PROOF.md` explains the construction; `PROVENANCE.md` identifies reused sources. Historical gauge44 identifiers remain for compatibility; actual helper counts, recipes, widths and native programs are checked explicitly.

## Scope and weakest steps

This is a finite exact conditional witness. All-size compilation, common-label/mutable-source realization, complete-invocation hosting, precision/tape accounting and analytic transfer remain inherited obligations. PR589's punctured bit-unit and interleaved-interface assumptions remain. This command exactly reprices its pinned bit record; the companion validation package retains a separate complete bit-circuit replay. No packing or frame-search optimality is claimed, and κ = 1 is not established.

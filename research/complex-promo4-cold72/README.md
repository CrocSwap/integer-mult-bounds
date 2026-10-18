# Four entrance promotions and 72 cold ends

**Conditional κ = 0.001660339298410333** (`1660339298410333/10^18`). This improves independently replayed PR671 at `16a27439d4ba1db451b6179c9475793529a485b6`, κ = 0.001658714981837397.

This witness composes six new cold dimension-eight ends with PR664's entrance promotions on the 504-helper no-triangle word. It then promotes a fourth four-helper group and reconstructs an exact physical owner assignment. The complex side binds; PR589's bit supplier, derived deficit and exceptional-residue surcharge are unchanged.

| Quantity | PR664/671 | This word |
| --- | ---: | ---: |
| Helpers | 504 | 504 |
| Cold ends | 66 | 72 |
| Promoted entrances | 12 | 16 |
| Local rank mass | 5644 | 5634 |
| Residual width mass | 3788 | 3778 |
| Width inventory | 4:76, 5:36, 7:54, 8:116, 9:222 | 4:80, 5:32, 7:54, 8:122, 9:216 |

The six new cold ends are raw helpers 510, 511, 512, 513, 522 and 523. The fourth promotion uses helpers 659, 661, 662 and 663. The global profile is `{1:185185, 2:23472, 3:30961, 4:13968, 5:4032, 8:576, 44:1, 48:2396}`, with rank mass 520704 and deficit 2560. Idle children are exactly 2,396 of rank 48 and one each of ranks 44, 3 and 1. No packing-optimality claim is needed.

The exact complex lower endpoint is `1663100609709845015347/10^24`; the bit endpoint is `1733427039589844234749/10^24`.

## Reproduce

Python 3.11+ and the standard library suffice. No network, optimizer or third-party Python package is needed:

```bash
bash research/complex-promo4-cold72/verify.sh /tmp/promo4-cold72-fresh
```

Use a new output directory outside the package. Set `PROMO4_COLD72_PYTHON` to select Python. Assertions must remain enabled; allow several minutes.

The driver freshly replays PR558 and checks every pinned ancestral input consumed by global admission. It rebuilds gauge44, the no-triangle word and the original gauge44 control, then the layered 66-end word, the 72-end cold recipe and the four-promotion recipe. The final word passes all 728 arbitrary-dirt columns in both orientations, phase identities and residual wrappers.

Local suites include 30 pivot mutations, 59 inherited layer mutations, 59 end mutations on the final word, 30 focused cold-end mutations and 11 promotion mutations. Global verification includes 69 admission mutations, 12 bit-supplier mutations, two exact moment engines and 47 strict outer constraints. Independent scalar/frame/cone and literal-owner/native-profile/rational-moment checks must agree.

The 9.5 KB integer flow/matching certificate reconstructs all 36,288 owner roles byte-for-byte and rejects seven corruptions. The optimizer is neither trusted nor run by verification. `PROOF.md` describes the construction; `PROVENANCE.md` identifies reused sources. Historical gauge44 identifiers remain for compatibility; actual helper counts, recipes, widths and native programs are checked explicitly.

## Scope and weakest steps

This is a finite exact conditional witness, not an unconditional multiplication theorem, practical speedup or κ = 1. All-size compilation, common-label/mutable-source realization, complete-invocation hosting, precision/tape accounting and analytic transfer remain inherited obligations. PR589's punctured bit-unit and interleaved-interface assumptions remain. This command exactly reprices its pinned bit record; the companion validation package retains a separate complete bit-circuit replay.

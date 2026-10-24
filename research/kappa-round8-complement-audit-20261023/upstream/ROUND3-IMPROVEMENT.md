# Orthogonal restriction of the round-three native word

Prepared for Dugongue with substantial OpenAI Codex assistance. Apache-2.0.

This is a second, strictly stronger local C supplier with the same 56 A / 56 C paired-port partition, the same typed interface, and the same productive helper profile as DUAL-PROVIDER.md. It restricts Cao Yifan's actual round-three word of PR #4610, pinned at 1eb8da6cfb35512c0cc2533413e5ca42f48e13c6, rather than the older #4470 base.

The input word has decompressed payload SHA-256 cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd. Its scalar opcodes and port endpoints are retained. Every frame is intersected with the orthogonal hyperplane H = 153-perp in the fixed nine-bit coordinates. The same constructive shared-map argument as in DUAL-PROVIDER.md applies. The four rank-one output retimings now occur at native operators 2, 3, 4, and 29. Each retiming is represented by an ordinary paid rank-one climb in the complete emitted word; it is not an uncharged warp.

The complete profiles are

    P_new = {1:2011, 2:445, 3:427, 4:112, 5:12, 7:8},
    H_new = {3:26, 4:2, 6:6, 7:48, 8:326}.

The local paid-minus-productive rank mass is 1680. Compared with the older orthogonal-restriction supplier, the change in the paid rank moment at exponent t is exactly

    Delta(t) = -36 + 28*2^t + 4*3^t - 8*4^t.

For every 0 <= t < 1 this change is strictly negative. Here is an elementary proof. Set x = 2^t and a = log_2(3), so 1 <= x < 2 and 1 < a < 2. Write g(x) = -36 + 28*x + 4*x^a - 8*x^2. On [1,2],

    g''(x) = 4*a*(a-1)*x^(a-2) - 16 < -8,
    g'(2) = 6*a - 4 > 2,
    g(2) = 0.

Hence g' is decreasing but remains positive on this interval. Thus g(x) < g(2) = 0 for x < 2. At t = 1 the two paid rank masses coincide. The productive profile is identical, so the new complete local supplier strictly lowers the paid-minus-productive rank moment for every t in [0,1).

The endpoint construction is a complete local supplier change. No multiplication kappa claim follows until its enclosing controller and native compiler invoice are supplied.

The old supplier and all its checked receipts remain unchanged. Source ownership and credit remain with the PR #4610 and #4470 authors and their retained upstream contributors; these scripts add the orthogonal restriction, exact shared-map construction, and independent typed endpoint admission.

Credit Cao Yifan for the round-three helper/map changes and complete input witness; Cinna Davis for the native supplier lineage; DaysSky for the quotient mechanism; Nick Petalas and Ryanson Jonathan for quotient/endpoint analysis; Dugongue for transported frames, arbitrary-frame rank, the repaired quotient and typed interfaces; zxv and Jacob Alan Sussman for retained native/compiler foundations; and all original source notices.

## Reproduction and evidence

The source-code closure in SOURCE-CLOSURE-ROUND3.json pins the 13 retained upstream interpreter and Clifford files. BASE-ROUND3-WORD.json.gz is the complete frozen input word; its decompressed payload is checked before derivation. With those source files installed under any chosen source root, run:

```sh
python -I -B intersection_newer_base.py --source-root /path/to/source
python -I -B admit_newer_base.py --source-root /path/to/source
python -I -B admit_newer_main.py --source-root /path/to/source
```

The first command deterministically rebuilds the clipped frames and discovery word. The second constructs 72 shared native maps, emits the four paid output retimings, replays every independent input through both exact interpreters and both orientations, and checks 180 actual warp classes in both orientations including absolute phase. The third constructs 448 exact monomial wrappers and checks 336 block identities for all 112 ports, then lowers all 2048 distinct paid, center, and helper frame pairs in both orientations with exact rank and absolute phase. Every helper input remains arbitrary and independent.

The resulting actual word has decompressed payload SHA-256 7f137c4b95db519d04ad2336ef1a146fbc953124e95940d10b572a63ab958c87. Both logical orientations have 632 final rows, 744 terms, and zero nonempty free-group words. Hence the universal free-group-algebra evaluation argument from DUAL-PROVIDER.md proves the scalar-word identity at every digit-column width for the newly constructed shared native operators. This statement does not rely on preserving sums under tensor powers.

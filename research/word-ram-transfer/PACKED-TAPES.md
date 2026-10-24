# Uniform packed tape kernels

## Representation theorem

Fix k tapes and a fixed alphabet with blank 0, represented by c-bit fields, where c is a fixed power of two and the alphabet has at most 2^c symbols. Fix H = 2^h >= 2k. Registers below 64 and packed storage beginning at address 128 are disjoint. The RAM has w-bit modular values and addresses, Boolean operations, shifts, addition, natural monus subtraction, indirect loads/stores and branches. No multiplication or division is used.

For input bit length n, set lambda = floor(log2(n+2)), q = floor(lambda/(8c)), and let B be the largest power of two at most q, or 1 when q = 0. INIT in packed_tape.py computes log2(B) and B-1 using the same finite program at every input length and word width. The fixed program depends on c, not on n, w or a time-horizon advice string.

Map tape i and signed coordinate z to tag = 2i + [z < 0], and u = z for z >= 0 or -z-1 otherwise. Write u = Bt+j with 0 <= j < B. Store the symbol in field j of word address

    128 + Ht + tag,

at bit offset cj. For valid parameters and nonwrapping addresses, GET returns that symbol in exactly 13 successful RAM instructions, and SET writes a supplied c-bit symbol in exactly 17 successful RAM instructions. SET preserves every other field, every unused high bit of that word, and every other data word. Scratch registers are explicitly clobbered. Halt is terminal and is not counted as a successful transition.

### Proof

INIT repeatedly right-shifts n+2 until it is less than 2, incrementing lambda once per shift. Dividing lambda by 8c is a fixed right shift because c is a power of two. Repeated doubling then selects B and computes B-1. Since B is a power of two, t = u >> log2(B) and j = u AND (B-1). Both computations take one instruction. The address is formed by shifting t left by h, adding the tag and adding 128.

Addresses of different blocks or tags cannot coincide: equality modulo no wrap reduces to H(t-t') = tag'-tag, and the right side has magnitude below H. Hence t=t' and tag=tag'. The two sign banks partition integer coordinates without losing coordinate -1 or 0. The c-bit fields at offsets cj do not overlap. GET shifts the selected word right and ANDs with 2^c-1. SET constructs mask (2^c-1) << cj, clears precisely that mask, shifts the supplied symbol into it, and ORs the result. These Boolean identities prove the result even with arbitrary values in neighboring fields or high padding. Counting the displayed address macro's 9 instructions and the respective 4 or 8 field instructions proves the exact costs.

For width safety, let S >= max(n,N+T+m+2), where N is the physical input size, T the number of TM steps, and m the requested output window. All touched head magnitudes and output positions are below S. A sufficient condition is

    w >= max(10, c, ceil(log2(256 + H(S+1)))).

Then n+2, all indices, masks, effective addresses and scratch addresses fit. If B=1, cB=c<=w. Otherwise cB<=lambda/8<=w/8. Thus the final field ends by bit cB<=w; left shifts cannot discard any field. INIT's doubled trial value also fits. Standard modular arithmetic consequently agrees with the natural address calculations just proved.

The active data footprint is at most 2k ceil(S/B) words, plus constant scratch; this is a word-count upper bound, not the numeric address span. For fixed c and sufficiently large n, B is between lambda/(16c) and lambda/(8c), up to the harmless small-input cutoff. It is therefore Theta(log n). Combined with a known polynomial bound on S, the sufficient word width is O(log(n+2)). This width is an external machine parameter satisfying a proved lower bound; the program neither obtains nor assumes a time horizon as input.

## Use in the compiler migration

For a fixed TM, replace each tape read/write by the displayed macros, and maintain each head's sign and magnitude with bounded additions, subtraction and branching. The fixed transition dispatcher reads all k symbols before performing writes, as in compiler/TM-TO-WORD-RAM.md. These operations require O(1) instructions per TM transition for fixed machine and alphabet. Physical input initialization and output serialization still cost O(N+m). Packed storage does not prove a T/w execution speedup.

For a complete backend with many reserved head/control cells, use a fixed machine-dependent base R >= 128 above all those cells. The emitters accept this base as a literal parameter. Replace 128 by R in the address and 256 by 2R in the sufficient width bound; the same proof and 13/17 counts apply. This prevents large fixed-k control storage from overlapping the packed data. Replay includes bases 256, 1024 and 4096 with 128 tape tags.

This is a constructive representation and macro theorem, with an informal universal proof and exact finite replay. The complete packed finite-control backend has not been emitted or Lean-verified. The separate unpacked compiler is the executable end-to-end semantic baseline.

Zero-initialized RAM fields represent initially blank tape cells. A caller that reuses dirty memory must initialize the fields it will read; arbitrary dirty unvisited fields are allowed only if never read as blanks. The field-preservation theorem permits arbitrary dirty neighboring fields without asserting they are blank. Initializing N input symbols takes O(N) SET calls. No uncharged conversion from arbitrary symbol words into densely packed bit input is assumed.

## Evidence

The optimized isolated replay covers 15,360 traces, tape counts 1, 2, 4 and 8, field widths 1, 2 and 4 bits, and word widths 10, 16, 32, 64 and 128. It checks retained writes across banks and signs, exact instruction counts, dirty-padding preservation and an intentionally wrong-bank control. These finite checks support the implementation; the representation proof above supplies the universal argument.

Prepared by Dugongue with substantial OpenAI Codex assistance. Apache-2.0.

# Changing the scalar field without expanding the payload

Status: **proved encoding interface; independently accepted by Route A**. See [review-full-rate-field-packing.md](https://github.com/CubeJerry/integer-mult-bounds/blob/a2a17b61d943676c757e0bbfaef3f4fae03ab8e5/research/moonshot-overhead-program/sessions/2026-11-26-S003/route-a/review-full-rate-field-packing.md). This replaces one-bit-to-one-extension-symbol embedding when a growing-arity interchanger needs a common linear-space bound. It relies on the completed field-swap identity; intermediate scalar operations need not act componentwise.

## 1. A power-of-two coordinate degree

For B=O(m) check nodes, choose e to be the least power of two at least max(1,ceil(log_4 B)). Then e<2max(1,ceil(log_4 B)), and K=F_(4^e) has at least B elements. Its binary coordinate dimension h=2e is a power of two and O(log(m+2)). The predecessor bounded monic-polynomial enumeration constructs K in4^(3e/2)poly(e)=poly(m) actual work and space. Store the resulting field arithmetic in coordinates, not an alphabet truth table.

Suppose a complete K-linear main program on W independent K rows implements exactly the desired physical-address permutation Q on every row. Its intermediate maps may mix rows, field coordinates and physical positions. Its completed identity is I_W tensor Q with coefficients0,1 in F2.

**Lemma FP.** The same complete program implements Q on hW independent binary rows with no increase in payload bit volume. Packing and unpacking use O(V(1+log h)) tape steps, O(V) visited payload cells and fixed-polynomial descriptor work. Tape count and alphabet are absolute.

## 2. Exact full-rate linear identification

Fix a basis of K over F2. Interpret the h independent bits at corresponding positions of h input rows as the h coordinates of one K symbol. This is a bijection F2^(hW|Omega|) to K^(W|Omega|); no row is initialized to zero or discarded. Because the completed scalar coefficient is the whole identity times the spatial permutation, conjugating by this identification gives exactly Q on every binary component. This proves correctness for arbitrary independent bit inputs.

It is insufficient to cite only one output coordinate of the K program. The full-rate whole-identity property of the accepted cyclic/repair construction is essential here. No such property is required of its individual intermediate operations.

## 3. Physical packing by short-coordinate digit moves

Use binary row order `(coarse role,module,coordinate[h],physical address)`. A multi-digit leading batch contains hW rows. After padding and exposing the row index, this is already a lexicographic factorization, with a complete coordinate range. Physical packing changes the order to

    (coarse role,module,physical address,coordinate[h]).

The h bits are now a contiguous K record. Since h is a power of two, move its log2 h binary digits, last digit first, across the arbitrary complete physical-address range. One such digit move splits its two classes onto two tapes and merges them in the desired order, preserving every trailing component block. This is the source elementary-stream operation for a single bit and an arbitrary intervening range. It costs O(V) including head returns. A fixed number of alternating work regions implements all passes, so visited payload remains O(V), not O(V log h).

Reverse these moves to unpack. Coarse roles, module coordinates and every arbitrary prefix remain intact. The procedure does not transpose the exponential module index bit by bit; the module is an unchanged prefix. Big range counters use amortized scans and fixed-degree descriptor arithmetic as in PB. Their setup is separately included.

The required leading radix-3 block now has ell=ceil(log_3(hW)) digits. Since log W=poly(m) and h=O(logm), ell remains polynomial m. Leading padding stays below two. No field-coordinate padding is needed because h itself is a power of two.

## 4. Recursive field changes

A paid spatial call during the K program is a permutation of physical fields acting identically on all h binary components. Invoke the interchanger on its encoded bit stream, treating the component index as an ordinary suffix spectator. A recursive node may choose a different m and a different K'. It packs its own independent leading bit rows into K' coordinates by the same lemma. Its completed operation returns exactly the requested bit permutation, hence reconstructs the parent's K records correctly.

Thus fields may change between spatial levels without multiplying volume by h at every descent. Every level packs the same incoming bits bijectively; only its explicitly bounded leading-range padding changes volume. The physical machine itself always uses a fixed binary alphabet and tape count. Field arithmetic is ordinary programmed coordinate arithmetic with descriptors supplied by the current m.

Within one finite four-child repair tree the scalar field and formula remain fixed. The dynamic change described here occurs only when a spatial interchange is recursively invoked on bit payloads. The old scalar programme's proof applies at each complete parent call because each child is an exact permutation on those bits.

## 5. Workspace and scope

Packing uses a fixed number of V-bit arrays. Field construction, descriptors and arithmetic scratch use poly(m,log(V+2)) additional bits. For a growing-arity choice m<=e_active^gamma and complete width-e_active fields, V>=3^(2e_active), so any fixed polynomial in m and log V is O(V) after fixing the absolute parameters. The bounded initial width range is handled separately. Additive setup/workspace must still be summed over the actual recursion; the nonstationary theorem performs that accounting.

The lemma removes the scalar-extension factor from proportional payload space. It does not make every other row operation constant-space, alter recursive call mass, or prove a new multiplication rate by itself.

## Credits and limits

The full-rate scalar construction and basis descent are predecessor results. Single-bit digit moves are the source elementary-stream algorithm. This note gives their explicit coordinate-packing implementation and variable-field recursive interface, needed for a growing parameter and common visited-space cap. Prepared for Jerry Chen (@CubeJerry) with substantial AI assistance. No full multiplier or Lean build is claimed.

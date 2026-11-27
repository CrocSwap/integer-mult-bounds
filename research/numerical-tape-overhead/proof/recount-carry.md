# From recovered coefficients to the raw product on physical tapes

Let $c_0,\ldots,c_{S-1}$ be the recovered nonnegative integer coefficients in ordinary rank after the inverse CRT. Choose $b\ge1$ and $u\ge b$ so that $c_i<2^u$. The integer caller can take $u=5k$, since $h\le 2^{k-2}$, $b<2k$ and $c_i<h2^{2b}$. Let $C=2n\le Sb$. All bit fields of a recovered coefficient are fed to the carry procedure least significant first. The [fixed control](../checks/recount-carry.py) then emits exactly the first $C$ normalized bits in reverse order onto the otherwise blank physical output.

## The numerical ports

Put $B=2^b$ and $q_0=0$. At row $i$ the machine computes

$$
  d_i=(c_i+q_i)\bmod B,\qquad
  q_{i+1}=\lfloor(c_i+q_i)/B\rfloor .
$$

If $c_i,q_i<2^u$ and $b\ge1$, then $q_{i+1}<2^u$. The $u$-bit carry representation therefore remains valid at every row, including all-one input words. Multiplication instances satisfy $q_S=0$ and their high $Sb-2n$ digit bits vanish. These are proved for the actual cyclic convolution and arbitrary input words by [the original-source assembly theorem](../S008/RecountProduct.lean).

The six physical heads are the formatted source, the two alternating $u$-bit carry banks, the consecutive low-bit bank, a budget of $C$ unary marks, and the initially blank raw output. There are 15 control states. Bit addition uses the three symbols currently read and one finite carry flag. Only the finite pair of carry-bank roles swaps. The literal table also operates on arbitrary coefficient lists, returning their low $C$ bits and a full surviving carry in the last active carry bank.

The [sequential formatter](../checks/recount-carry.py) accepts a stream of $u$-bit coefficient records with one delimiter per record. Its single reusable split mask has $b$ low marks followed by $u-b$ high marks. The head traverses the mask to tag each coefficient bit, emits a row-end marker, and then emits $b-1$ padding marks. The first scan also emits $u$ initialization marks. Its source words are therefore identified directly by the symbols that the physical result uses. Setting up the reusable mask from the two binary dimensions needs only the existing [binary-to-unary tape procedure](recount-node.md), plus one simultaneous removal pass of $b$ from $u$ and a concatenating copy. Reusing the staged mask pays every return to its origin. The caller's raw input traversal can emit one budget mark per operand bit, producing $2n$ in a single monotone walk. Reading the finite-width grid record, rounding it to a nonnegative integer, and positioning its $u$ bits in little-endian order use a constant number of full record scans. The [precision proof](outer-layers.md) gives the strict rounding margin.

## Exact unit-head invoice

The formatter takes $2u+4+S(2u+2b+6)$ transitions after its one split mask is available. The warm scan uses $u$ bit transitions, the colon uses one, its rewind uses $u+2$, and the terminal dollar uses one. Each record then takes $u$ bit transitions, one delimiter, $u+2$ to rewind, one skip of the first low mark, $b-1$ pad transitions, one end, and $b+2$ to return. The formatter visits at most the raw-record length, the formatted length and $u+2$ mask cells.

The six-tape machine first plants three left fences in two transitions. It consumes the $u$ warm marks, the colon and a rewind, taking $2u+3$ transitions. In every row it consumes $u$ source bits simultaneously with $u$ old-carry bits, erasing the old bank as it reads. Each of the $b$ low additions writes to the low bank. Each of the $u-b$ subsequent additions writes its sum bit to the new carry. The row-end transition writes the single overflow bit there. Appending the remaining $b-1$ zeroes makes the new carry exactly $u$ bits again. The closing marker starts the joint $u+2$-step rewind. This accounts for exactly $2u+b+3$ transitions per row.

One transition recognizes the final marker. The low bank rewinds in $Sb+2$ transitions, the length budget positions its head in $C+1$, and $C$ actual transitions reverse-read the selected bits into increasing absolute output positions. The final consulted rule halts. Thus the complete post-formatter price is

$$
 T_{\rm carry}=2+(2u+3)+S(2u+b+3)+1+(Sb+2)+(C+1)+C .
$$

The formatted source comprises $J=u+2+S(u+b+1)$ symbols. Its entire interval, both carry intervals of $u+2$ positions, the low interval of $Sb+2$ positions and two intervals of $C+1$ each include all initial and final head positions. Therefore

$$
 \operatorname{VisitsAtMost}\; J+2(u+2)+(Sb+2)+2(C+1).
$$

The formatter produces its bank in one direction. Rewinding it once to present the carry reader at the origin adds $J+O(1)$ unit moves if writer and reader use the same physical head. A dedicated bank copy by the [physical neutral adapter](recount-handoff.md) adds at most $2J+O(1)$ instead. In the integer caller, $u=5k$, $b<2k$, $C\le Sb$ and $S\le N$. All these costs fit the ordinary linear-in-$Nk$ stream term. There are no searches in the coefficient table and no per-row tape allocation.

## Kernel-checked physical scope

The [Lean carry module](../S008/RecountCarry.lean) imports the original, pinned OAI tape model through the [source product module](../S008/RecountProduct.lean). Its `whole_carry_trace` theorem runs every coefficient through a single four-head finite row rule. For any $S$ raw records at the stated widths, the rule constructs its own successive carry words, erases the obsolete bank, pads the new quotient, rewinds both heads and swaps their roles. It has exactly $S(2u+b+3)$ transitions. The raw records contain only the current coefficient bits. Each preceding carry is derived from the actual prior output.

The theorem `recovered_physical_readout` uses the matching physical low-bank windows of three source-level rules. Given the $u$-bit recovered words, the coefficient-error hypothesis and the ordinary limb/slot capacity assumptions, its traces cover the entire carry loop, the $Sb+2n+3$ steps that position the low bank using the length budget, and the $2n$ transitions that write the raw product. The proof restores the algebraic normal form, preserves leading zeros, and concludes original `TM.whole`, halt, `bitValue` equality and the raw writer's `VisitsAtMost (4n+2)`. The complete Python controller uses six physical heads to execute those stages in succession.

The kernel theorem enters with prepared records, the zero seed, an empty alternate bank, home fences and the unary length budget. The fixed formatter, its adapter to the rounded Fourier records, the warm word and the cross-stage control transitions have the priced implementation above. The upstream Fourier approximation and its achieved coefficient error remain supplied by the full construction. The reported global visited-cell inequality here is the explicit interval proof for the six-tape routine. The source-level numerical product, the three matching traces, and the raw writer's own visited-set assertion are distinct quantified statements.

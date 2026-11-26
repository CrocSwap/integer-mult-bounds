# Exact cost of handing one adaptive interchange to its child

This independently counted procedure implements the save, return, and restore paragraph of [AQ-P](foundations/aq-p.md#tape-ownership-and-displaced-heads). It accepts every parent word, every marked head position, an independently specified child argument, and any legal child that returns a word of the promised length. The parent’s canonical active bank may itself contain occupied data. The [step rule](https://github.com/openai/math/blob/3344da59991ed94f9ba711217b29c1d760badfa6/lean/OAI/Computability/IntegerMultiplication/TMModel.lean) reads the symbols at the heads, selects a new finite state, writes one symbol at each head and moves every head by at most one.

## Interface and bound

Fix the numbers of parent payload and descriptor banks. Every bank stores a left delimiter at its home, a string of bits, and a right delimiter. Its cursor may be anywhere between the two delimiters, inclusively. Let the parked banks, including both classes, have lengths $u_i$ and cursor displacements $d_i$ with $0\le d_i\le u_i+1$. Payload and control use different stacks. A stack head is at the first blank cell above its current frames. Its contents below that cell may already represent other suspended calls.

The neutral handoff bank contains an already gathered argument of $g$ bits, with its cursor at home. The child starts and returns with all ordinary scratch banks empty and at home, except for the designated active argument or reply bank, which starts and returns at home. The child need not compute the same word it received. In the source application a spatial interchange preserves length. The wrapper returns an arbitrary $g$-bit reply in the neutral bank, restores every parked string and every cursor exactly, and restores both stacks. Its time outside the child is exactly

$$
\boxed{\ T_{\rm contracted}
  =\sum_i (4u_i+8-2d_i)+4g+9.\ }
$$

The final $9$ pays six transitions from the two whole-bank transfers and three from the call/return tag. A second input/output bank for an already encoded descriptor of lengths $v_{\rm in},v_{\rm out}$ costs another $2v_{\rm in}+2v_{\rm out}+6$ if it is moved both ways. One-way prepared inputs cost $2v_{\rm in}+3$ when the child itself retires their active bank. These expressions count prepared words. Computing the next child’s dimensions, gathering the selected records, consuming a reply in its parent slot, and generating the finite template have distinct interfaces and must receive their own bills.

At a full reserve the sole surviving payload is already in the active bank with its head home. A full call parks only the descriptor banks $D$ and uses the same call tag. Its exact wrapper charge is

$$
\boxed{\ T_{\rm full}=3+\sum_{i\in D}(4u_i+8-2d_i).\ }
$$

The child itself may access ordinary work banks. While the caller is suspended its payload uses no new payload-stack cells. If the main word left the unique result in a different bank at offset $d$, first rewind that bank in $d+1$ steps and move its result of length $V$ to the empty active bank in $2V+3$. A displaced head on an already canonical active bank costs $d+1$ to rewind. Each additional occupied, dead bank of length $u$ at offset $d$ can be cleared and homed in $2u+4-d$. When the entry conditions are known from the preceding operation those normalizations can be omitted. The $2a$ successive reserve calls in [the constructive recursion](foundations/adaptive-interchange.md#3-the-executed-nonstationary-recurrence) pay the full-call expression $2a$ times, with their own actual descriptors and any actual normalization. They do not allocate a $V$-cell payload frame each time.

## Transition inventory

A bank alphabet needs blank, left, right, the two bits and the marked version of each bit. A stack can also hold three frame delimiters indicating an old left, interior or right cursor, a bottom symbol, and two return tags for contracted and full calls. The disjoint union is a fixed alphabet of 13 symbols. One copy of each primitive is compiled for each member of the fixed bank list. Its last transition selects the first state of the next primitive. The caller’s dynamic loop indices and instruction offsets belong in the saved binary descriptor banks. Appending the tag selects the single child entry state. The child’s return enters the common resume routine. Reading the top tag selects the contracted or full continuation. Thus no unbounded program counter or call stack is kept in finite control.

| Operation | One-head behavior | Transitions |
|---|---|---:|
| Begin park | Note the old cursor class in finite control. If it points to a bit, mark that bit in place. | $1$ |
| Seek the old right end | Move the bank head right one cell per step. | $u+1-d$ |
| Append a frame | Replace right by blank, move left, append a class delimiter on the stack and advance its head. | $1$ |
| Save and clear | Copy each bit, including its possible mark, to the stack while clearing the bank. The bank moves left and the stack moves right. | $u$ |
| Install the empty bank | At the left delimiter move right, write a right delimiter and step back to the left. | $2$ |
| **Park subtotal** | The bank is empty at home. The stack head advances $u+1$ places. | **$2u+5-d$** |
| Begin pop | Step the empty bank right and the stack left. | $1$ |
| Restore word | Read the saved bits in reverse frame order, writing the restored word forward and erasing the stack. | $u$ |
| Restore cursor | Erase the class delimiter at the stack head and write the bank’s right delimiter. If the old cursor was right, stop there. Otherwise step left on this transition, continue left until the marked bit or left delimiter, then clear the mark if present and stop. | $u+2-d$ |
| **Pop subtotal** | The original bits and cursor are restored; stack head is its previous top. | **$2u+3-d$** |
| Return tag | Write a tag and step right on issue. On return step left, then read and erase the tag while choosing the continuation. | $3$ |
| **Move $g$ bits to an empty bank** | From both left delimiters advance once. For each source bit write it into the destination and advance both heads. Turn the first bit of the source into its new right delimiter and its remaining bits into blanks. At the old right end erase it if a bit was seen, otherwise preserve it, write right at the destination and step both left. Rewind $g$ times, then enter the next state from the left delimiters. | **$2g+3$** |

For $u=d=0$, pop returns to the left delimiter of the restored empty word. For $u=0,d=1$, it returns immediately to its right delimiter. No special positive-length hypothesis is needed. Noncursor bits carry no mark, so the backward scan in pop stops at precisely the old bit position even when all bits agree.

Park the payload banks (including the active bank) and the descriptor banks. Move the neutral argument into the now-empty active bank, then append the return tag. On a contracted return remove the tag and **move the active reply to neutral before restoring the parent banks**. After that transfer, pop the banks of each stack in reverse order. This order works even when the caller’s previously occupied active word was shorter than the reply or had an interior cursor. The neutral bank’s old argument is already cleared. The independent parent word is recovered from its own frame. The sum of the table gives the displayed formula. For a full reserve both directions of the payload transfer and all payload-bank parks disappear. Its entry and exit reuse the same active tape interval.

## Distinct cells at arbitrary nesting depth

On a bank park/pop of length $u$, every new head position lies between the original left and right delimiters. A transfer of $g$ bits visits only positions from home through $g+1$ on each of its two banks. These bounds hold even if an ancestor once used a larger interval. A stack operation from old top $t$ visits only $[t,t+u+1]$. Popping leaves the stack head at $t$, so a later sibling reuses that interval. The return tag adds one position to the control frame. For any fixed stack the greatest coordinate ever visited equals its initial top plus the maximum simultaneous sum of those frame lengths along the path taken (with any initially used prefix counted once). Full calls add zero to the payload-stack sum.

For example, if each actual contracted parent of volume $V_i$ parks at most $bV_i$ payload bits in $k$ banks and its child has volume at most $V_i/2$, the extra payload-stack high-water mark above the starting top is at most $2bV_0+k(1+\lfloor\log_2 V_0\rfloor)$, with arbitrary intervening full reserves and arbitrary sibling multiplicities. A single frame cannot recur more often along the current path than there are contractions, and $\sum_i V_i\le 2V_0$. For descriptor lengths the exact high-water increment is the largest path sum of $1+\sum_{i\in D}(1+u_i)$, including every suspended full reserve. AQ-P separately bounds these lengths and path height. A numerical full-node space coefficient still requires a numerical inventory of its live banks and descriptor sizes. The handoff bounds apply to the union of tape/address pairs actually seen, including final head positions.

## Source-level kernel check

[The Lean proof](../S008/RecountHandoff.lean) defines a five-state, two-head physical rule over the 13-symbol handoff alphabet. It imports the unchanged OpenAI tape and visited-space declarations. For any bit list of length $g$, independent integer origins, and arbitrary exterior symbol words on each side of each physical bank, the theorem `S008.Recount.neutral_bank_transfer` constructs an actual `Trace (TM.advance rule)` of exactly $2g+3$ steps. It proves the destination contains the original word, the source is empty, and the exterior lists and both head origins are restored. The theorem `neutral_bank_halts` gives the next rule result. The theorem `neutral_bank_visits` proves the original `NearSquareRoot.VisitsAtMost` predicate with cap $2(g+2)$ across both tapes; each head stays between its own home and right boundary. The local list model is related by a proved simulation to `TM.Tape.apply` and `TM.advance`. The checked theorem concerns the destructive transfer. The park/pop, tag, and full recursive scheduler have the written and executable evidence above.

The first uncounted operation when entering this subroutine is the parent's construction of the next argument and its binary dimensions in the neutral banks. On exit the first unpaid operation is the selected scatter, accumulation or descriptor read consuming the returned word. Absolute counts for template interpretation and record routing are required before these wrapper constants imply a full-node polynomial with numeric coefficients.

Written for Jerry Chen (@CubeJerry) with ChatGPT assistance. AQ-P supplied the recursive ownership schedule. OpenAI supplied the fixed tape model and recursive interchange source. The numerical wrappers were independently derived from those specifications. This is a physical subroutine for the written semantics; the original source's complete `BoundedFits` body and complete multiplier are separate obligations.

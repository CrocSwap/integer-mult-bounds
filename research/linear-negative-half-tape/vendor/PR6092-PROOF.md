# A charged two-tape implementation of one signed stochastic half

This addresses the physical half-SCALE question of [PR6066](https://github.com/CrocSwap/integer-mult-bounds/pull/6066). It lowers one macro with a resident coin and explicitly available clean working bits. It does not supply the full scalar caller, random-bit delivery, a native MOVE or a new kappa.

## Contract, width and scratch

Let W>=2. A W-bit two's-complement register holds arbitrary x in [-2^(W-1),2^(W-1)-1]. A resident read-only coin u is 0 or 1, and a parity cell r and W working cells start zero. The sign s in {-1,1} is a compiled parameter. The endpoint is

    (x, u, r=0, work=0^W) -> (S(s*x,2,u), u, (s*x) mod 2, 0^W),

where S(n,2,u)=floor(n/2)+1[u < n mod 2]. Reversing the gate program restores x and clears r and every working cell. The coin cell is never written, even temporarily.

Data positions 0..W-1 hold the little-endian signed value; positions W, W+1 and W+2 hold r,u,t; positions W+3..2W+1 hold W-1 carry bits. Thus the data extent is exactly 2W+2 binary cells. Of these, W are clean working cells (t and carries), one is the retained residue, one is the resident coin and W contain the dirty input. No extra arithmetic guard bit is needed on this declared input range.

The interpreter has two Boolean control accumulators plus a fixed set of at most eight modes. The separate read-only program tape and its preparation are counted below. Clean workspace availability and placement of the resident coin are input obligations, not free consequences of a dirty caller.

## Exact reversible gate word

Extract the low bit with CNOT(x0,r), CNOT(r,x0). This records r=x mod 2 and clears x0. Swap neighboring bits from low to high, then copy the old sign bit into the vacated highest position. The value register now holds q=floor(x/2). This uses exactly 3W CNOTs and no arithmetic shift instruction.

For positive sign, increment q when r(1-u)=1. For negative sign, increment q when ru=1 and then negate it in two's complement. The identities are

    S(x,2,u)  = q+r(1-u),
    S(-x,2,u) = -q-ru.

The increment's control t is prepared and cleared reversibly. For r(1-u), use CNOT(r,t) then Toffoli(r,u,t), and reverse them after the increment; the coin is only a control. For ru, use one Toffoli before and after. The negative case complements every value bit and performs a controlled increment with t temporarily set to one.

A controlled ripple increment first computes carries c_(j+1)=c_j*x_j with c0=t. It XORs c_j into x_j and then clears the carries in descending order using

    c_(j+1) = c_j * (1-x'_j).

The negative bit control is two X gates around a Toffoli. Every carry and t returns zero. All gate operands are distinct. The increment has 2(W-1) Toffolis, W CNOTs and 2(W-1) X gates.

All arithmetic has its signed meaning without overflow. The intermediate q lies between -2^(W-2) and 2^(W-2)-1; q plus its controlled increment lies between -2^(W-2) and 2^(W-2). Its negation fits in W bits. The gate word is a permutation even away from these reached states, but only the specified clean-work endpoint is given the stochastic-half interpretation.

The exact gate counts are:

| Sign | X | CNOT | Toffoli |
|---|---:|---:|---:|
| + | 2W-2 | 4W+2 | 2W |
| - | 5W-2 | 5W | 4W-2 |

A zero-residue isolated implementation cannot restore x: for example S(0,2,1)=S(1,2,1). The one retained bit is necessary for this isolated map. Existing side information can change that contract, as the inferred sites in [PR6091](https://github.com/CrocSwap/integer-mult-bounds/pull/6091) illustrate. The W clean working cells are not claimed optimal.

## Explicit fixed-tape lowering

The tape alphabet has seven instruction symbols L,R,A,B,X,C,T, plus two boundary markers. L and R move the binary data head by one cell. A and B XOR the current data bit into the corresponding one-bit finite-control accumulator. X flips the current data bit; C flips it controlled by accumulator A; T flips it controlled by both A and B. Each action is reversible; L and R are inverse to each other. The program head moves one instruction at a time. There is no addressed data access in this interpreter.

Each Boolean gate expands into literal unary head walks. An X visits its target and returns. A CNOT visits control/target/control/home, with operations A,C,A. A Toffoli visits first control/second control/target/second control/first control/home, with operations A,B,T,B,A. Every macro returns the data head and both control accumulators to zero. The compiler emits every walk symbol, including long gaps between operands.

Let L be the emitted instruction-word length. A forward call executes L payload instructions and rewinds its read-only program head; an inverse call first sweeps to the end and executes the inverted instructions backwards. With the two marker transitions included, **each direction costs 2L+2 interpreter steps**, and both heads return to their entry positions. The program occupies L+2 fixed-alphabet cells. The inverse uses the same tape; it needs no second stored word. All input-dependent information is in the declared value, residue and resident coin, not in an unreturned head position or control register.

If D=2W+1 is the largest data address, then the three gate macros have lengths at most 2D+1, 4D+3 and 6D+5, respectively. Hence, with the exact counts above,

    L <= N_X(2D+1)+N_C(4D+3)+N_T(6D+5) = O(W^2).

This is a deliberately elementary implementation. Preparing its explicit unary program takes O(W^2 log W) charged setup time with O(log W) counter space; the output program itself has O(W^2) cells. It can be reused at the same width/sign. It does not establish a faster physical tariff, and the program storage is not excluded from the resource ledger.

## Source binding and verification

The frozen historical PR5599 prefix used by PR6066 contains 18 positive and 66 negative half SCALEs. Its first examples are zero-based event 52 at role345 and event89 at role259. Both use the coefficient signs implemented here. The module does not replace the whole 9,589-event source program or assume its other macros are free.

The verifier compares the Boolean gate interpreter with an independent integer divmod formula for every signed input, both coins and both signs at W=2..8 (2,032 cases). A separate literal tape-head interpreter executes 324 full forward/inverse round trips, including larger widths through 128 and signed endpoints. It checks all scratch, read-only coin cells, returned heads, program motion, gate counts and exact program hashes. The written ripple/sign proof supplies the all-width quantifier. Wrong sign and unsupported width controls are included; normal and optimized checks remain active.

## Remaining composition obligations

A complete caller still needs the resident coin fetched and returned, allocation of these clean cells, an integer-grid width that contains actual caller values, every other scalar macro, data-layout movement between registers, inferred-residue sites, native MOVE error propagation and the total paid bill. The O(W^2) unary program should not be inserted into a faster budget without those charges. No supplier, selected change, independent human review or proof-kernel acceptance is claimed.

Prepared by [zxv](https://github.com/zxv) with substantial OpenAI Codex assistance. Credit [Nick Petalas](https://github.com/petalas)'s [PR6026](https://github.com/CrocSwap/integer-mult-bounds/pull/6026), [Ali Romman](https://github.com/aliromman)'s [PR5599](https://github.com/CrocSwap/integer-mult-bounds/pull/5599), PR6066's stochastic ABI and retained predecessors. Ripple carries and reversible gate decompositions are classical. The contribution is their explicit signed stochastic-half/tape contract and complete local invoice. Apache-2.0.

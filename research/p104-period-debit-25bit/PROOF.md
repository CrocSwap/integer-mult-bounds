# Exact 25-bit period charge and signed allocation

The exact comparable witness is [#8081 at 51011382](https://github.com/CrocSwap/integer-mult-bounds/commit/510113821774bb27f7ddaad4e8b94837a1c2cf52), with κ 0.00389846, heights (8192,38102,604362)/18845936 and complete recurring log₂ C 4354317571. The new profile books κ 0.003898460000505 under the same assumptions on signed all-column operators, ownership and restoration, uniform compiler closure, fixed-alphabet tape and precision, and analytic recovery.

## Directed exterior period

For each actual exterior field, the authenticated schedule uses width s′=(e−8)k and four-aligned period q=4⌈M/(4s′)⌉. The upper cutoff and k≤258 imply x=M/(4s′)≥x₀=263772/1032>255. At x≤256, ⌈x⌉/x≤256/x₀<257/256. The strict inequality reduces to 65536·1032<257·263772. At x>256 use m=⌈x⌉−1≥256 and x>m, so ⌈x⌉/x<(m+1)/m≤257/256. Both the exact boundary x=256 and arbitrarily large x are covered. Thus q s′/M≤257/256 under the actual paid schedule. [#8085 period proof](https://github.com/CrocSwap/integer-mult-bounds/pull/8085)

Replace only the prior exterior multiplier 1+1032/263772. The actual q, typed widths, placements, phase and owner state, nested and exterior routes, source access, unmatched and late work, round and copy/rounding allowances, and restoration and recovery retain their charges. The directed finite factor with 192-bit outward powers funds 64934/524288 with reserve greater than 0.000000232515772047. The adjacent debit 64933/524288 misses the same envelope. The predecessor exterior factor also misses this booking. Ordinary debit 11239/8192 and its two-moment geometric charge still fund the three literal ordinary stages.

## Clear the exact stopped comparator

The stopped rate uses guard 5·10^-18. With #8081's old bookings and recurring cap, every Gaussian height at most 18845935 misses the old booked rate. Every larger height than 18845936 imposes ordinary height sum at most 650655. The directed ordinary bound rejects that entire sum, using the relaxed weighted reciprocal loss with weights (1/62500,1/250,1), Cauchy's inequality on the last two heights and the derivative at first height 8192. The old ordinary rate at its actual installed triple is strictly above the Gaussian rate at 18845936. The old Gaussian stopped bound is exactly 15407802515941573408769828489/3952279237427200000000000000000. At that crossing the paid margin is zero.

The new literal heights (8192,38102,604363)/18845934 and price strictly clear this stopped upper. The exact excess is 1994769718130907511/3952279237427200000000000000000. Both signed tiers pass all 54 strict and four functional checks. At the new target the old ordinary triple and old Gaussian debit each fail. The candidate Gaussian height is one above the minimum funded height 18845933. The latter is a positive control and 18845932 fails. Each smaller adjacent ordinary coordinate fails with the other heights fixed. These checks certify the chosen profile and the exact old stopped comparison. An alternative ordinary split with the previous sum can pass the new target, so optimizing the entire new shape family is open.

## Fully charged installer and recurring costs

One extra stage-three ordinary height costs 320 log units. Two fewer Gaussian heights save 440. Entry pays log₂ C 125660241 and 8744 rate-conversion units. The signed terminal ordinary bound is 208210368. The complete bound is

```text
1 + max(125660241+8744, 84500001, 1602+220·18845934+208210368) = 4354317451.
```

The cuts are (8290,46456,650883), first terminal header 2^19497093+4 and private control envelope 19298236419. Maximum height is 18845934 and fits 25 bits. The literal symbolic upper fence and small exact cutoff fixtures share the authenticated source. The physical installer checks both profiles' scalar field encodings, six invalid encodings, 2,407,819 directory records and the actual 18,845,935-bit carrier. The two large carrier bounds and seven metadata recipes retain the separate 2^40 indexed-action allowance, with complete conservative fixed serial setup below 2^228. [Setup proof and scope](SETUP-PROOF.md) · [Signed receipt](RESULT-460.json)

The product fixture uses the entry-tier coefficients. Separate signed checks cover both exact tier profiles, actual finite routes and products, and terminal analytic geometry and recovery under the five stated premises. The physical 25-bit setup result covers its fixed serial scope.

## Predecessor credit

Clear1nsight supplied [#8081's charged 25-bit signed installer](https://github.com/CrocSwap/integer-mult-bounds/pull/8081) and [#8078's expanded profiles](https://github.com/CrocSwap/integer-mult-bounds/pull/8078). Ali Romman supplied the [#8057 weighted producer and signed caller](https://github.com/CrocSwap/integer-mult-bounds/commit/cbe847a953b971f9c6c5a0a6661e2008acd29086) and [#8055 native setup](https://github.com/CrocSwap/integer-mult-bounds/pull/8055). SYLforge supplied the [#8052 K7 word](https://github.com/CrocSwap/integer-mult-bounds/pull/8052) and physical replay. #8064, #8070 and [#8072](https://github.com/CrocSwap/integer-mult-bounds/commit/75f7e1c44f48c43983016bcf8878c4d9e5e87c62) supplied the prior fence, debit, and signed allocation. #8085 supplies the narrower application of the same period proof. #7257 supplies the separate historical CI prerequisite. OpenAI Codex materially assisted the proof, implementation and independent replay.

# What entrance gauges and completed banks can absorb (no new κ)

A scoping note for the paired-cube words of #168 v4, #200 and #207–#213. **No κ is claimed, and no certificate changes.**

#208 prices "bank-absorption rungs" (for example, absorbing the bit word's rank-22 family for +2.52%) and leaves open which families a bank may absorb. This note says where the published mechanism stops. The absorbable families are already absorbed on the current words. The priced rungs need a lemma outside this mechanism.

## 1. What the published bank removes

By `notes/paired-cube-sharing.tex`, a role entering with gauge T_σ has the exact operator U = F_A T_σ⁻¹. Its forward correction F_A U⁻¹ = F_A T_σ F_A⁻¹ has Fourier rank dim σ, and its three stage blocks tensor into **one** child of width 3·dim σ: the exterior. #186 and #207 replace exactly this correction with the S_P bank endpoint, and say so: "Exactly the 2200 rank60 gauge exteriors are removed. Every internal chain increment, source and target connector, centre copy, original data endpoint … remains."

`notes/paired-cube-bit.tex` gives the converse. A role corrected at the zero frame has no exterior, and pays its first transition as an ordinary internal child.

So, under this mechanism, **the bankable children are exactly the gauge exteriors.** On #207's word the surviving genuine entrance gauges number 2,200, and all of them are banked. The 1,760 rank-21 recipient gauges are internal splices (#186).

## 2. When a register may carry an entrance gauge

The correction F_A T_σ F_A⁻¹ fixes the frame because the role's scalar contract **restores its own entrance value**. Its raw entrance z is read as T_σ ẑ, and it exits as F_A ẑ, a function of ẑ alone. Two other register classes fail this test.

- **Targets** accumulate. A target entering at gauge τ would end as T·T_τ⁻¹·y_old + T·f(x).
  - One end correction cannot apply T_τ to the old part while leaving the new part alone.
  - A start correction applied jointly on all three stage blocks breaks the gates. In stage j, a target is added to registers whose inactive blocks were not transformed the same way, so the inactive offsets no longer cancel.
- **Sources** are restored, but their values are *consumed*. Read as T_τ x̂, the injections would deliver x̂ ≠ x.

An entrance gauge, and with it a bank, therefore needs content that is **both don't-care and restored**, i.e. auxiliary dirt. This is a property of the gauge/bank mechanism, not an impossibility proof for other constructions.

## 3. Consequences for #208's rungs

#208's own allocation classifies the rank-22 family (and every later rung's) as "internal / target / center / compensating / terminal-substitution dirt". Its verdict is "not buildable with the construction as published". Sections 1–2 give the reason. None of those children is an entrance-gauge exterior, and the target, source and internal ones fail the gauge test of section 2. A rung needs a mechanism other than gauge reinterpretation.

## 4. Two measured near-misses

These are float discovery scores on our #173 bit word (p = 12, R = 22,120). They show the boundary is binding in practice, not only in principle.

- **Re-selecting auxiliary gauges once exteriors are free (banks).**
  - There are 3,552 ungauged, non-source auxiliary roles outside phase one that have targets. Their feasible σ lies in the first-operation frame ∩ each target's first event frame. No role has an empty adjoint.
  - Ignoring target cost, the upper bound is +4.17%.
  - A gauge read at σ inserts an event into each of the role's 4–9 targets, splitting their first increments. The best nested selection loses 1.46%.
  - A greedy pass that accepts a role only when the exact float saving rises accepts **zero** roles.
- **Target entrance gauges** (section 2) would price at +3.9%, or +4.5% merged with the final rank-two complement child. They are invalid for the reason given in section 2.

The pricing scripts are short and read the #173 package (`research/paired-cube-bit-rl-module`). They are in `regauge.py` here and need numpy.

## Scope

All interfaces of the cited words remain as stated by their authors. Sections 1 and 2 restate and apply the published sharing and bank arguments; they do not prove optimality of any construction. Credit goes to an664 (#128 completed-core sharing), icekylinx (paired cubes, general Clifford frames), the #186/#207 bank authors (Dugongue and others), chafreaky (#200 word), and maxime-fleury (#208 pricing).

Prepared by Joel Pulikkan (GamingPuzzled) with Anthropic Claude assistance; Apache-2.0.

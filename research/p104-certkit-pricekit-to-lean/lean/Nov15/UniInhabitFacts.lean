/-
UniInhabitFacts (lane UNI-INHABIT, Nov 19).  Pure-Nat kernel facts (decide +kernel) about the packed t7669 data:
frame closure certificates (frameOK), frame sizes 2^dim, end codes = json final frames, the 1501 births, the MOVE
chart pairs per segment, and the fold tables HS/HD/FI/FF (UniWCData, genwc.py) = dims of the trace's MOVE / birth /
final charts.  Core Lean only.
-/
import Nov15.UniInhabitFr0
import Nov15.UniInhabitFr1
import Nov15.UniInhabitFr2
import Nov15.UniInhabitFr3
import Nov15.UniInhabitFr4
import Nov15.UniInhabitFr5
import Nov15.UniInhabitFr6
import Nov15.UniInhabitFr7
import Nov15.UniInhabitTabs2
import Nov15.UniWCData

namespace UniInhabit

def lk (X i : Nat) : Nat := X / 2 ^ (11 * i) % 2048

def cntM (m : Nat) : Nat := ((List.range 512).filter (fun v => Nat.testBit m v)).length


theorem frames_all : ∀ i < 1097, frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by
  intro i hi
  by_cases h0 : i < 50
  · exact frames_0 i h0 (by omega)
  by_cases h1 : i < 100
  · exact frames_1 i h1 (by omega)
  by_cases h2 : i < 127
  · exact frames_2 i h2 (by omega)
  by_cases h3 : i < 131
  · exact frames_3 i h3 (by omega)
  by_cases h4 : i < 136
  · exact frames_4 i h4 (by omega)
  by_cases h5 : i < 141
  · exact frames_5 i h5 (by omega)
  by_cases h6 : i < 146
  · exact frames_6 i h6 (by omega)
  by_cases h7 : i < 151
  · exact frames_7 i h7 (by omega)
  by_cases h8 : i < 156
  · exact frames_8 i h8 (by omega)
  by_cases h9 : i < 161
  · exact frames_9 i h9 (by omega)
  by_cases h10 : i < 166
  · exact frames_10 i h10 (by omega)
  by_cases h11 : i < 171
  · exact frames_11 i h11 (by omega)
  by_cases h12 : i < 176
  · exact frames_12 i h12 (by omega)
  by_cases h13 : i < 181
  · exact frames_13 i h13 (by omega)
  by_cases h14 : i < 186
  · exact frames_14 i h14 (by omega)
  by_cases h15 : i < 191
  · exact frames_15 i h15 (by omega)
  by_cases h16 : i < 196
  · exact frames_16 i h16 (by omega)
  by_cases h17 : i < 201
  · exact frames_17 i h17 (by omega)
  by_cases h18 : i < 206
  · exact frames_18 i h18 (by omega)
  by_cases h19 : i < 211
  · exact frames_19 i h19 (by omega)
  by_cases h20 : i < 216
  · exact frames_20 i h20 (by omega)
  by_cases h21 : i < 221
  · exact frames_21 i h21 (by omega)
  by_cases h22 : i < 226
  · exact frames_22 i h22 (by omega)
  by_cases h23 : i < 231
  · exact frames_23 i h23 (by omega)
  by_cases h24 : i < 246
  · exact frames_24 i h24 (by omega)
  by_cases h25 : i < 267
  · exact frames_25 i h25 (by omega)
  by_cases h26 : i < 306
  · exact frames_26 i h26 (by omega)
  by_cases h27 : i < 353
  · exact frames_27 i h27 (by omega)
  by_cases h28 : i < 400
  · exact frames_28 i h28 (by omega)
  by_cases h29 : i < 447
  · exact frames_29 i h29 (by omega)
  by_cases h30 : i < 486
  · exact frames_30 i h30 (by omega)
  by_cases h31 : i < 518
  · exact frames_31 i h31 (by omega)
  by_cases h32 : i < 532
  · exact frames_32 i h32 (by omega)
  by_cases h33 : i < 548
  · exact frames_33 i h33 (by omega)
  by_cases h34 : i < 565
  · exact frames_34 i h34 (by omega)
  by_cases h35 : i < 592
  · exact frames_35 i h35 (by omega)
  by_cases h36 : i < 630
  · exact frames_36 i h36 (by omega)
  by_cases h37 : i < 648
  · exact frames_37 i h37 (by omega)
  by_cases h38 : i < 664
  · exact frames_38 i h38 (by omega)
  by_cases h39 : i < 682
  · exact frames_39 i h39 (by omega)
  by_cases h40 : i < 707
  · exact frames_40 i h40 (by omega)
  by_cases h41 : i < 739
  · exact frames_41 i h41 (by omega)
  by_cases h42 : i < 769
  · exact frames_42 i h42 (by omega)
  by_cases h43 : i < 794
  · exact frames_43 i h43 (by omega)
  by_cases h44 : i < 820
  · exact frames_44 i h44 (by omega)
  by_cases h45 : i < 839
  · exact frames_45 i h45 (by omega)
  by_cases h46 : i < 858
  · exact frames_46 i h46 (by omega)
  by_cases h47 : i < 877
  · exact frames_47 i h47 (by omega)
  by_cases h48 : i < 897
  · exact frames_48 i h48 (by omega)
  by_cases h49 : i < 910
  · exact frames_49 i h49 (by omega)
  by_cases h50 : i < 920
  · exact frames_50 i h50 (by omega)
  by_cases h51 : i < 930
  · exact frames_51 i h51 (by omega)
  by_cases h52 : i < 942
  · exact frames_52 i h52 (by omega)
  by_cases h53 : i < 952
  · exact frames_53 i h53 (by omega)
  by_cases h54 : i < 962
  · exact frames_54 i h54 (by omega)
  by_cases h55 : i < 972
  · exact frames_55 i h55 (by omega)
  by_cases h56 : i < 982
  · exact frames_56 i h56 (by omega)
  by_cases h57 : i < 992
  · exact frames_57 i h57 (by omega)
  by_cases h58 : i < 1002
  · exact frames_58 i h58 (by omega)
  by_cases h59 : i < 1012
  · exact frames_59 i h59 (by omega)
  by_cases h60 : i < 1024
  · exact frames_60 i h60 (by omega)
  by_cases h61 : i < 1046
  · exact frames_61 i h61 (by omega)
  by_cases h62 : i < 1072
  · exact frames_62 i h62 (by omega)
  by_cases h63 : i < 1086
  · exact frames_63 i h63 (by omega)
  by_cases h64 : i < 1097
  · exact frames_64 i h64 (by omega)
  omega

def mvAll : List (Nat × Nat) := Tabs.mv0 ++ Tabs.mv1 ++ Tabs.mv2 ++ Tabs.mv3 ++ Tabs.mv4 ++ Tabs.mv5 ++ Tabs.mv6 ++ Tabs.mv7 ++ Tabs.mv8 ++ Tabs.mv9 ++ Tabs.mv10 ++ Tabs.mv11 ++ Tabs.mv12 ++ Tabs.mv13 ++ Tabs.mv14 ++ Tabs.mv15 ++ Tabs.mv16 ++ Tabs.mv17 ++ Tabs.mv18 ++ Tabs.mv19 ++ Tabs.mv20 ++ Tabs.mv21 ++ Tabs.mv22 ++ Tabs.mv23 ++ Tabs.mv24 ++ Tabs.mv25

/-- nibble-by-nibble table check: X's nibble i = dim of L[i].1, Y's = dim of L[i].2. -/
def chkT : List (Nat × Nat) → Nat → Nat → Bool
  | [], _, _ => true
  | (c, d) :: L, X, Y => Nat.beq (X % 16) (gt 11 Tabs.dimT c) && Nat.beq (Y % 16) (gt 11 Tabs.dimT d) && chkT L (X / 16) (Y / 16)

theorem dims_0 : ∀ i < 100, 0 ≤ i → cntM (gt 11 Tabs.maskT i) = 2 ^ gt 11 Tabs.dimT i := by decide +kernel
theorem dims_1 : ∀ i < 200, 100 ≤ i → cntM (gt 11 Tabs.maskT i) = 2 ^ gt 11 Tabs.dimT i := by decide +kernel
theorem dims_2 : ∀ i < 300, 200 ≤ i → cntM (gt 11 Tabs.maskT i) = 2 ^ gt 11 Tabs.dimT i := by decide +kernel
theorem dims_3 : ∀ i < 400, 300 ≤ i → cntM (gt 11 Tabs.maskT i) = 2 ^ gt 11 Tabs.dimT i := by decide +kernel
theorem dims_4 : ∀ i < 500, 400 ≤ i → cntM (gt 11 Tabs.maskT i) = 2 ^ gt 11 Tabs.dimT i := by decide +kernel
theorem dims_5 : ∀ i < 600, 500 ≤ i → cntM (gt 11 Tabs.maskT i) = 2 ^ gt 11 Tabs.dimT i := by decide +kernel
theorem dims_6 : ∀ i < 700, 600 ≤ i → cntM (gt 11 Tabs.maskT i) = 2 ^ gt 11 Tabs.dimT i := by decide +kernel
theorem dims_7 : ∀ i < 800, 700 ≤ i → cntM (gt 11 Tabs.maskT i) = 2 ^ gt 11 Tabs.dimT i := by decide +kernel
theorem dims_8 : ∀ i < 900, 800 ≤ i → cntM (gt 11 Tabs.maskT i) = 2 ^ gt 11 Tabs.dimT i := by decide +kernel
theorem dims_9 : ∀ i < 1000, 900 ≤ i → cntM (gt 11 Tabs.maskT i) = 2 ^ gt 11 Tabs.dimT i := by decide +kernel
theorem dims_10 : ∀ i < 1097, 1000 ≤ i → cntM (gt 11 Tabs.maskT i) = 2 ^ gt 11 Tabs.dimT i := by decide +kernel

theorem fin_codes : ∀ j < 1501, gt 11 Tabs.ck26 j = lk Tabs.finP j + 2 ∧ lk Tabs.finP j < 1097 := by decide +kernel
theorem own_codes : ∀ j < 1752, 1501 ≤ j → gt 11 Tabs.ck26 j < 2 := by decide +kernel
theorem init_lt : ∀ j < 1501, lk Tabs.initP j < 1097 := by decide +kernel

/-- the first n events are the births of j, j+1, … at their json initial frames. -/
def chkB : List PE → Nat → Nat → Bool
  | _, _, 0 => true
  | e :: L, j, n + 1 => Nat.beq e.op 0 && Nat.beq e.r j && Nat.beq e.c (lk Tabs.initP j) && chkB L (j + 1) n
  | [], _, _ + 1 => false

theorem births_ok : chkB (decodeAll Tabs.seg0) 0 1501 = true := by decide +kernel

theorem mv0_eq : (decodeAll Tabs.seg0).filterMap mvOf = Tabs.mv0 := by decide +kernel
theorem mv1_eq : (decodeAll Tabs.seg1).filterMap mvOf = Tabs.mv1 := by decide +kernel
theorem mv2_eq : (decodeAll Tabs.seg2).filterMap mvOf = Tabs.mv2 := by decide +kernel
theorem mv3_eq : (decodeAll Tabs.seg3).filterMap mvOf = Tabs.mv3 := by decide +kernel
theorem mv4_eq : (decodeAll Tabs.seg4).filterMap mvOf = Tabs.mv4 := by decide +kernel
theorem mv5_eq : (decodeAll Tabs.seg5).filterMap mvOf = Tabs.mv5 := by decide +kernel
theorem mv6_eq : (decodeAll Tabs.seg6).filterMap mvOf = Tabs.mv6 := by decide +kernel
theorem mv7_eq : (decodeAll Tabs.seg7).filterMap mvOf = Tabs.mv7 := by decide +kernel
theorem mv8_eq : (decodeAll Tabs.seg8).filterMap mvOf = Tabs.mv8 := by decide +kernel
theorem mv9_eq : (decodeAll Tabs.seg9).filterMap mvOf = Tabs.mv9 := by decide +kernel
theorem mv10_eq : (decodeAll Tabs.seg10).filterMap mvOf = Tabs.mv10 := by decide +kernel
theorem mv11_eq : (decodeAll Tabs.seg11).filterMap mvOf = Tabs.mv11 := by decide +kernel
theorem mv12_eq : (decodeAll Tabs.seg12).filterMap mvOf = Tabs.mv12 := by decide +kernel
theorem mv13_eq : (decodeAll Tabs.seg13).filterMap mvOf = Tabs.mv13 := by decide +kernel
theorem mv14_eq : (decodeAll Tabs.seg14).filterMap mvOf = Tabs.mv14 := by decide +kernel
theorem mv15_eq : (decodeAll Tabs.seg15).filterMap mvOf = Tabs.mv15 := by decide +kernel
theorem mv16_eq : (decodeAll Tabs.seg16).filterMap mvOf = Tabs.mv16 := by decide +kernel
theorem mv17_eq : (decodeAll Tabs.seg17).filterMap mvOf = Tabs.mv17 := by decide +kernel
theorem mv18_eq : (decodeAll Tabs.seg18).filterMap mvOf = Tabs.mv18 := by decide +kernel
theorem mv19_eq : (decodeAll Tabs.seg19).filterMap mvOf = Tabs.mv19 := by decide +kernel
theorem mv20_eq : (decodeAll Tabs.seg20).filterMap mvOf = Tabs.mv20 := by decide +kernel
theorem mv21_eq : (decodeAll Tabs.seg21).filterMap mvOf = Tabs.mv21 := by decide +kernel
theorem mv22_eq : (decodeAll Tabs.seg22).filterMap mvOf = Tabs.mv22 := by decide +kernel
theorem mv23_eq : (decodeAll Tabs.seg23).filterMap mvOf = Tabs.mv23 := by decide +kernel
theorem mv24_eq : (decodeAll Tabs.seg24).filterMap mvOf = Tabs.mv24 := by decide +kernel
theorem mv25_eq : (decodeAll Tabs.seg25).filterMap mvOf = Tabs.mv25 := by decide +kernel

theorem mvAll_len : mvAll.length = 6157 := by decide +kernel
theorem tab_bank : chkT mvAll T7669Data.HS T7669Data.HD = true := by decide +kernel
theorem tab_field : ∀ j < 1501, T7669Data.FI / 16 ^ j % 16 = gt 11 Tabs.dimT (lk Tabs.initP j) ∧
    T7669Data.FF / 16 ^ j % 16 = gt 11 Tabs.dimT (lk Tabs.finP j) := by decide +kernel
theorem mv_lt : mvAll.all (fun p => Nat.blt p.1 1097 && Nat.blt p.2 1097) = true := by decide +kernel

end UniInhabit

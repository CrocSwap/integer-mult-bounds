import DyadicPower
import Selected

/-! Generated, untrusted certificate proposals; every inequality is proved by Lean.
Gareth Davidson with OpenAI Codex assistance. Apache-2.0. -/

open scoped BigOperators
open DyadicPower SelectedStoppedRecurrence

namespace SelectedBitMoment

theorem rank_1_upper : (1 / 64 : ℝ) ^ (9983 / 10000 : ℝ) ≤ 15735950448 / 1000000000000 := by
  have h0 : (1 / 64 : ℝ) ^ (0 : ℝ) ≤ 1 := by norm_num
  have h1 : (1 / 64 : ℝ) ^ (1 / 2 : ℝ) ≤ 125000000000 / 1000000000000 := by
    convert half_step (x := (1 / 64 : ℝ)) (e := 0) (b := 1)
      (u := 1) (v := 125000000000 / 1000000000000)
      (by norm_num) h0 (by norm_num) (by norm_num) using 1; norm_num
  have h2 : (1 / 64 : ℝ) ^ (1 / 4 : ℝ) ≤ 353553390594 / 1000000000000 := by
    convert half_step (x := (1 / 64 : ℝ)) (e := 1 / 2) (b := 0)
      (u := 125000000000 / 1000000000000) (v := 353553390594 / 1000000000000)
      (by norm_num) h1 (by norm_num) (by norm_num) using 1; norm_num
  have h3 : (1 / 64 : ℝ) ^ (1 / 8 : ℝ) ≤ 594603557502 / 1000000000000 := by
    convert half_step (x := (1 / 64 : ℝ)) (e := 1 / 4) (b := 0)
      (u := 353553390594 / 1000000000000) (v := 594603557502 / 1000000000000)
      (by norm_num) h2 (by norm_num) (by norm_num) using 1; norm_num
  have h4 : (1 / 64 : ℝ) ^ (1 / 16 : ℝ) ≤ 771105412705 / 1000000000000 := by
    convert half_step (x := (1 / 64 : ℝ)) (e := 1 / 8) (b := 0)
      (u := 594603557502 / 1000000000000) (v := 771105412705 / 1000000000000)
      (by norm_num) h3 (by norm_num) (by norm_num) using 1; norm_num
  have h5 : (1 / 64 : ℝ) ^ (1 / 32 : ℝ) ≤ 878126080188 / 1000000000000 := by
    convert half_step (x := (1 / 64 : ℝ)) (e := 1 / 16) (b := 0)
      (u := 771105412705 / 1000000000000) (v := 878126080188 / 1000000000000)
      (by norm_num) h4 (by norm_num) (by norm_num) using 1; norm_num
  have h6 : (1 / 64 : ℝ) ^ (33 / 64 : ℝ) ≤ 117135477132 / 1000000000000 := by
    convert half_step (x := (1 / 64 : ℝ)) (e := 1 / 32) (b := 1)
      (u := 878126080188 / 1000000000000) (v := 117135477132 / 1000000000000)
      (by norm_num) h5 (by norm_num) (by norm_num) using 1; norm_num
  have h7 : (1 / 64 : ℝ) ^ (33 / 128 : ℝ) ≤ 342250605744 / 1000000000000 := by
    convert half_step (x := (1 / 64 : ℝ)) (e := 33 / 64) (b := 0)
      (u := 117135477132 / 1000000000000) (v := 342250605744 / 1000000000000)
      (by norm_num) h6 (by norm_num) (by norm_num) using 1; norm_num
  have h8 : (1 / 64 : ℝ) ^ (33 / 256 : ℝ) ≤ 585021884842 / 1000000000000 := by
    convert half_step (x := (1 / 64 : ℝ)) (e := 33 / 128) (b := 0)
      (u := 342250605744 / 1000000000000) (v := 585021884842 / 1000000000000)
      (by norm_num) h7 (by norm_num) (by norm_num) using 1; norm_num
  have h9 : (1 / 64 : ℝ) ^ (289 / 512 : ℝ) ≤ 95608404185 / 1000000000000 := by
    convert half_step (x := (1 / 64 : ℝ)) (e := 33 / 256) (b := 1)
      (u := 585021884842 / 1000000000000) (v := 95608404185 / 1000000000000)
      (by norm_num) h8 (by norm_num) (by norm_num) using 1; norm_num
  have h10 : (1 / 64 : ℝ) ^ (801 / 1024 : ℝ) ≤ 38650760865 / 1000000000000 := by
    convert half_step (x := (1 / 64 : ℝ)) (e := 289 / 512) (b := 1)
      (u := 95608404185 / 1000000000000) (v := 38650760865 / 1000000000000)
      (by norm_num) h9 (by norm_num) (by norm_num) using 1; norm_num
  have h11 : (1 / 64 : ℝ) ^ (1825 / 2048 : ℝ) ≤ 24574745951 / 1000000000000 := by
    convert half_step (x := (1 / 64 : ℝ)) (e := 801 / 1024) (b := 1)
      (u := 38650760865 / 1000000000000) (v := 24574745951 / 1000000000000)
      (by norm_num) h10 (by norm_num) (by norm_num) using 1; norm_num
  have h12 : (1 / 64 : ℝ) ^ (3873 / 4096 : ℝ) ≤ 19595417972 / 1000000000000 := by
    convert half_step (x := (1 / 64 : ℝ)) (e := 1825 / 2048) (b := 1)
      (u := 24574745951 / 1000000000000) (v := 19595417972 / 1000000000000)
      (by norm_num) h11 (by norm_num) (by norm_num) using 1; norm_num
  have h13 : (1 / 64 : ℝ) ^ (7969 / 8192 : ℝ) ≤ 17497954333 / 1000000000000 := by
    convert half_step (x := (1 / 64 : ℝ)) (e := 3873 / 4096) (b := 1)
      (u := 19595417972 / 1000000000000) (v := 17497954333 / 1000000000000)
      (by norm_num) h12 (by norm_num) (by norm_num) using 1; norm_num
  have h14 : (1 / 64 : ℝ) ^ (16161 / 16384 : ℝ) ≤ 16534979180 / 1000000000000 := by
    convert half_step (x := (1 / 64 : ℝ)) (e := 7969 / 8192) (b := 1)
      (u := 17497954333 / 1000000000000) (v := 16534979180 / 1000000000000)
      (by norm_num) h13 (by norm_num) (by norm_num) using 1; norm_num
  have h15 : (1 / 64 : ℝ) ^ (32545 / 32768 : ℝ) ≤ 16073551247 / 1000000000000 := by
    convert half_step (x := (1 / 64 : ℝ)) (e := 16161 / 16384) (b := 1)
      (u := 16534979180 / 1000000000000) (v := 16073551247 / 1000000000000)
      (by norm_num) h14 (by norm_num) (by norm_num) using 1; norm_num
  have h16 : (1 / 64 : ℝ) ^ (65313 / 65536 : ℝ) ≤ 15847688735 / 1000000000000 := by
    convert half_step (x := (1 / 64 : ℝ)) (e := 32545 / 32768) (b := 1)
      (u := 16073551247 / 1000000000000) (v := 15847688735 / 1000000000000)
      (by norm_num) h15 (by norm_num) (by norm_num) using 1; norm_num
  have h17 : (1 / 64 : ℝ) ^ (130849 / 131072 : ℝ) ≤ 15735950448 / 1000000000000 := by
    convert half_step (x := (1 / 64 : ℝ)) (e := 65313 / 65536) (b := 1)
      (u := 15847688735 / 1000000000000) (v := 15735950448 / 1000000000000)
      (by norm_num) h16 (by norm_num) (by norm_num) using 1; norm_num
  exact upper_of_rounded_exponent (by norm_num) (by norm_num) (by norm_num) h17

theorem rank_2_upper : (2 / 64 : ℝ) ^ (9983 / 10000 : ℝ) ≤ 31434808292 / 1000000000000 := by
  have h0 : (2 / 64 : ℝ) ^ (0 : ℝ) ≤ 1 := by norm_num
  have h1 : (2 / 64 : ℝ) ^ (1 / 2 : ℝ) ≤ 176776695297 / 1000000000000 := by
    convert half_step (x := (2 / 64 : ℝ)) (e := 0) (b := 1)
      (u := 1) (v := 176776695297 / 1000000000000)
      (by norm_num) h0 (by norm_num) (by norm_num) using 1; norm_num
  have h2 : (2 / 64 : ℝ) ^ (1 / 4 : ℝ) ≤ 420448207628 / 1000000000000 := by
    convert half_step (x := (2 / 64 : ℝ)) (e := 1 / 2) (b := 0)
      (u := 176776695297 / 1000000000000) (v := 420448207628 / 1000000000000)
      (by norm_num) h1 (by norm_num) (by norm_num) using 1; norm_num
  have h3 : (2 / 64 : ℝ) ^ (1 / 8 : ℝ) ≤ 648419777327 / 1000000000000 := by
    convert half_step (x := (2 / 64 : ℝ)) (e := 1 / 4) (b := 0)
      (u := 420448207628 / 1000000000000) (v := 648419777327 / 1000000000000)
      (by norm_num) h2 (by norm_num) (by norm_num) using 1; norm_num
  have h4 : (2 / 64 : ℝ) ^ (1 / 16 : ℝ) ≤ 805245165976 / 1000000000000 := by
    convert half_step (x := (2 / 64 : ℝ)) (e := 1 / 8) (b := 0)
      (u := 648419777327 / 1000000000000) (v := 805245165976 / 1000000000000)
      (by norm_num) h3 (by norm_num) (by norm_num) using 1; norm_num
  have h5 : (2 / 64 : ℝ) ^ (1 / 32 : ℝ) ≤ 897354537503 / 1000000000000 := by
    convert half_step (x := (2 / 64 : ℝ)) (e := 1 / 16) (b := 0)
      (u := 805245165976 / 1000000000000) (v := 897354537503 / 1000000000000)
      (by norm_num) h4 (by norm_num) (by norm_num) using 1; norm_num
  have h6 : (2 / 64 : ℝ) ^ (33 / 64 : ℝ) ≤ 167458440507 / 1000000000000 := by
    convert half_step (x := (2 / 64 : ℝ)) (e := 1 / 32) (b := 1)
      (u := 897354537503 / 1000000000000) (v := 167458440507 / 1000000000000)
      (by norm_num) h5 (by norm_num) (by norm_num) using 1; norm_num
  have h7 : (2 / 64 : ℝ) ^ (33 / 128 : ℝ) ≤ 409216862443 / 1000000000000 := by
    convert half_step (x := (2 / 64 : ℝ)) (e := 33 / 64) (b := 0)
      (u := 167458440507 / 1000000000000) (v := 409216862443 / 1000000000000)
      (by norm_num) h6 (by norm_num) (by norm_num) using 1; norm_num
  have h8 : (2 / 64 : ℝ) ^ (33 / 256 : ℝ) ≤ 639700603754 / 1000000000000 := by
    convert half_step (x := (2 / 64 : ℝ)) (e := 33 / 128) (b := 0)
      (u := 409216862443 / 1000000000000) (v := 639700603754 / 1000000000000)
      (by norm_num) h7 (by norm_num) (by norm_num) using 1; norm_num
  have h9 : (2 / 64 : ℝ) ^ (289 / 512 : ℝ) ≤ 141388273444 / 1000000000000 := by
    convert half_step (x := (2 / 64 : ℝ)) (e := 33 / 256) (b := 1)
      (u := 639700603754 / 1000000000000) (v := 141388273444 / 1000000000000)
      (by norm_num) h8 (by norm_num) (by norm_num) using 1; norm_num
  have h10 : (2 / 64 : ℝ) ^ (801 / 1024 : ℝ) ≤ 66470922554 / 1000000000000 := by
    convert half_step (x := (2 / 64 : ℝ)) (e := 289 / 512) (b := 1)
      (u := 141388273444 / 1000000000000) (v := 66470922554 / 1000000000000)
      (by norm_num) h9 (by norm_num) (by norm_num) using 1; norm_num
  have h11 : (2 / 64 : ℝ) ^ (1825 / 2048 : ℝ) ≤ 45576488784 / 1000000000000 := by
    convert half_step (x := (2 / 64 : ℝ)) (e := 801 / 1024) (b := 1)
      (u := 66470922554 / 1000000000000) (v := 45576488784 / 1000000000000)
      (by norm_num) h10 (by norm_num) (by norm_num) using 1; norm_num
  have h12 : (2 / 64 : ℝ) ^ (3873 / 4096 : ℝ) ≤ 37739439245 / 1000000000000 := by
    convert half_step (x := (2 / 64 : ℝ)) (e := 1825 / 2048) (b := 1)
      (u := 45576488784 / 1000000000000) (v := 37739439245 / 1000000000000)
      (by norm_num) h11 (by norm_num) (by norm_num) using 1; norm_num
  have h13 : (2 / 64 : ℝ) ^ (7969 / 8192 : ℝ) ≤ 34341774509 / 1000000000000 := by
    convert half_step (x := (2 / 64 : ℝ)) (e := 3873 / 4096) (b := 1)
      (u := 37739439245 / 1000000000000) (v := 34341774509 / 1000000000000)
      (by norm_num) h12 (by norm_num) (by norm_num) using 1; norm_num
  have h14 : (2 / 64 : ℝ) ^ (16161 / 16384 : ℝ) ≤ 32759433045 / 1000000000000 := by
    convert half_step (x := (2 / 64 : ℝ)) (e := 7969 / 8192) (b := 1)
      (u := 34341774509 / 1000000000000) (v := 32759433045 / 1000000000000)
      (by norm_num) h13 (by norm_num) (by norm_num) using 1; norm_num
  have h15 : (2 / 64 : ℝ) ^ (32545 / 32768 : ℝ) ≤ 31995816644 / 1000000000000 := by
    convert half_step (x := (2 / 64 : ℝ)) (e := 16161 / 16384) (b := 1)
      (u := 32759433045 / 1000000000000) (v := 31995816644 / 1000000000000)
      (by norm_num) h14 (by norm_num) (by norm_num) using 1; norm_num
  have h16 : (2 / 64 : ℝ) ^ (65313 / 65536 : ℝ) ≤ 31620709514 / 1000000000000 := by
    convert half_step (x := (2 / 64 : ℝ)) (e := 32545 / 32768) (b := 1)
      (u := 31995816644 / 1000000000000) (v := 31620709514 / 1000000000000)
      (by norm_num) h15 (by norm_num) (by norm_num) using 1; norm_num
  have h17 : (2 / 64 : ℝ) ^ (130849 / 131072 : ℝ) ≤ 31434808292 / 1000000000000 := by
    convert half_step (x := (2 / 64 : ℝ)) (e := 65313 / 65536) (b := 1)
      (u := 31620709514 / 1000000000000) (v := 31434808292 / 1000000000000)
      (by norm_num) h16 (by norm_num) (by norm_num) using 1; norm_num
  exact upper_of_rounded_exponent (by norm_num) (by norm_num) (by norm_num) h17

theorem rank_3_upper : (3 / 64 : ℝ) ^ (9983 / 10000 : ℝ) ≤ 47119696168 / 1000000000000 := by
  have h0 : (3 / 64 : ℝ) ^ (0 : ℝ) ≤ 1 := by norm_num
  have h1 : (3 / 64 : ℝ) ^ (1 / 2 : ℝ) ≤ 216506350947 / 1000000000000 := by
    convert half_step (x := (3 / 64 : ℝ)) (e := 0) (b := 1)
      (u := 1) (v := 216506350947 / 1000000000000)
      (by norm_num) h0 (by norm_num) (by norm_num) using 1; norm_num
  have h2 : (3 / 64 : ℝ) ^ (1 / 4 : ℝ) ≤ 465302429553 / 1000000000000 := by
    convert half_step (x := (3 / 64 : ℝ)) (e := 1 / 2) (b := 0)
      (u := 216506350947 / 1000000000000) (v := 465302429553 / 1000000000000)
      (by norm_num) h1 (by norm_num) (by norm_num) using 1; norm_num
  have h3 : (3 / 64 : ℝ) ^ (1 / 8 : ℝ) ≤ 682130800913 / 1000000000000 := by
    convert half_step (x := (3 / 64 : ℝ)) (e := 1 / 4) (b := 0)
      (u := 465302429553 / 1000000000000) (v := 682130800913 / 1000000000000)
      (by norm_num) h2 (by norm_num) (by norm_num) using 1; norm_num
  have h4 : (3 / 64 : ℝ) ^ (1 / 16 : ℝ) ≤ 825912102414 / 1000000000000 := by
    convert half_step (x := (3 / 64 : ℝ)) (e := 1 / 8) (b := 0)
      (u := 682130800913 / 1000000000000) (v := 825912102414 / 1000000000000)
      (by norm_num) h3 (by norm_num) (by norm_num) using 1; norm_num
  have h5 : (3 / 64 : ℝ) ^ (1 / 32 : ℝ) ≤ 908797063384 / 1000000000000 := by
    convert half_step (x := (3 / 64 : ℝ)) (e := 1 / 16) (b := 0)
      (u := 825912102414 / 1000000000000) (v := 908797063384 / 1000000000000)
      (by norm_num) h4 (by norm_num) (by norm_num) using 1; norm_num
  have h6 : (3 / 64 : ℝ) ^ (33 / 64 : ℝ) ≤ 206397340938 / 1000000000000 := by
    convert half_step (x := (3 / 64 : ℝ)) (e := 1 / 32) (b := 1)
      (u := 908797063384 / 1000000000000) (v := 206397340938 / 1000000000000)
      (by norm_num) h5 (by norm_num) (by norm_num) using 1; norm_num
  have h7 : (3 / 64 : ℝ) ^ (33 / 128 : ℝ) ≤ 454309741188 / 1000000000000 := by
    convert half_step (x := (3 / 64 : ℝ)) (e := 33 / 64) (b := 0)
      (u := 206397340938 / 1000000000000) (v := 454309741188 / 1000000000000)
      (by norm_num) h6 (by norm_num) (by norm_num) using 1; norm_num
  have h8 : (3 / 64 : ℝ) ^ (33 / 256 : ℝ) ≤ 674025030091 / 1000000000000 := by
    convert half_step (x := (3 / 64 : ℝ)) (e := 33 / 128) (b := 0)
      (u := 454309741188 / 1000000000000) (v := 674025030091 / 1000000000000)
      (by norm_num) h7 (by norm_num) (by norm_num) using 1; norm_num
  have h9 : (3 / 64 : ℝ) ^ (289 / 512 : ℝ) ≤ 177749608398 / 1000000000000 := by
    convert half_step (x := (3 / 64 : ℝ)) (e := 33 / 256) (b := 1)
      (u := 674025030091 / 1000000000000) (v := 177749608398 / 1000000000000)
      (by norm_num) h8 (by norm_num) (by norm_num) using 1; norm_num
  have h10 : (3 / 64 : ℝ) ^ (801 / 1024 : ℝ) ≤ 91279860286 / 1000000000000 := by
    convert half_step (x := (3 / 64 : ℝ)) (e := 289 / 512) (b := 1)
      (u := 177749608398 / 1000000000000) (v := 91279860286 / 1000000000000)
      (by norm_num) h9 (by norm_num) (by norm_num) using 1; norm_num
  have h11 : (3 / 64 : ℝ) ^ (1825 / 2048 : ℝ) ≤ 65412104774 / 1000000000000 := by
    convert half_step (x := (3 / 64 : ℝ)) (e := 801 / 1024) (b := 1)
      (u := 91279860286 / 1000000000000) (v := 65412104774 / 1000000000000)
      (by norm_num) h10 (by norm_num) (by norm_num) using 1; norm_num
  have h12 : (3 / 64 : ℝ) ^ (3873 / 4096 : ℝ) ≤ 55373210231 / 1000000000000 := by
    convert half_step (x := (3 / 64 : ℝ)) (e := 1825 / 2048) (b := 1)
      (u := 65412104774 / 1000000000000) (v := 55373210231 / 1000000000000)
      (by norm_num) h11 (by norm_num) (by norm_num) using 1; norm_num
  have h13 : (3 / 64 : ℝ) ^ (7969 / 8192 : ℝ) ≤ 50947220038 / 1000000000000 := by
    convert half_step (x := (3 / 64 : ℝ)) (e := 3873 / 4096) (b := 1)
      (u := 55373210231 / 1000000000000) (v := 50947220038 / 1000000000000)
      (by norm_num) h12 (by norm_num) (by norm_num) using 1; norm_num
  have h14 : (3 / 64 : ℝ) ^ (16161 / 16384 : ℝ) ≤ 48868711251 / 1000000000000 := by
    convert half_step (x := (3 / 64 : ℝ)) (e := 7969 / 8192) (b := 1)
      (u := 50947220038 / 1000000000000) (v := 48868711251 / 1000000000000)
      (by norm_num) h13 (by norm_num) (by norm_num) using 1; norm_num
  have h15 : (3 / 64 : ℝ) ^ (32545 / 32768 : ℝ) ≤ 47861475530 / 1000000000000 := by
    convert half_step (x := (3 / 64 : ℝ)) (e := 16161 / 16384) (b := 1)
      (u := 48868711251 / 1000000000000) (v := 47861475530 / 1000000000000)
      (by norm_num) h14 (by norm_num) (by norm_num) using 1; norm_num
  have h16 : (3 / 64 : ℝ) ^ (65313 / 65536 : ℝ) ≤ 47365669694 / 1000000000000 := by
    convert half_step (x := (3 / 64 : ℝ)) (e := 32545 / 32768) (b := 1)
      (u := 47861475530 / 1000000000000) (v := 47365669694 / 1000000000000)
      (by norm_num) h15 (by norm_num) (by norm_num) using 1; norm_num
  have h17 : (3 / 64 : ℝ) ^ (130849 / 131072 : ℝ) ≤ 47119696168 / 1000000000000 := by
    convert half_step (x := (3 / 64 : ℝ)) (e := 65313 / 65536) (b := 1)
      (u := 47365669694 / 1000000000000) (v := 47119696168 / 1000000000000)
      (by norm_num) h16 (by norm_num) (by norm_num) using 1; norm_num
  exact upper_of_rounded_exponent (by norm_num) (by norm_num) (by norm_num) h17

theorem rank_4_upper : (4 / 64 : ℝ) ^ (9983 / 10000 : ℝ) ≤ 62795518809 / 1000000000000 := by
  have h0 : (4 / 64 : ℝ) ^ (0 : ℝ) ≤ 1 := by norm_num
  have h1 : (4 / 64 : ℝ) ^ (1 / 2 : ℝ) ≤ 250000000000 / 1000000000000 := by
    convert half_step (x := (4 / 64 : ℝ)) (e := 0) (b := 1)
      (u := 1) (v := 250000000000 / 1000000000000)
      (by norm_num) h0 (by norm_num) (by norm_num) using 1; norm_num
  have h2 : (4 / 64 : ℝ) ^ (1 / 4 : ℝ) ≤ 500000000000 / 1000000000000 := by
    convert half_step (x := (4 / 64 : ℝ)) (e := 1 / 2) (b := 0)
      (u := 250000000000 / 1000000000000) (v := 500000000000 / 1000000000000)
      (by norm_num) h1 (by norm_num) (by norm_num) using 1; norm_num
  have h3 : (4 / 64 : ℝ) ^ (1 / 8 : ℝ) ≤ 707106781187 / 1000000000000 := by
    convert half_step (x := (4 / 64 : ℝ)) (e := 1 / 4) (b := 0)
      (u := 500000000000 / 1000000000000) (v := 707106781187 / 1000000000000)
      (by norm_num) h2 (by norm_num) (by norm_num) using 1; norm_num
  have h4 : (4 / 64 : ℝ) ^ (1 / 16 : ℝ) ≤ 840896415254 / 1000000000000 := by
    convert half_step (x := (4 / 64 : ℝ)) (e := 1 / 8) (b := 0)
      (u := 707106781187 / 1000000000000) (v := 840896415254 / 1000000000000)
      (by norm_num) h3 (by norm_num) (by norm_num) using 1; norm_num
  have h5 : (4 / 64 : ℝ) ^ (1 / 32 : ℝ) ≤ 917004043205 / 1000000000000 := by
    convert half_step (x := (4 / 64 : ℝ)) (e := 1 / 16) (b := 0)
      (u := 840896415254 / 1000000000000) (v := 917004043205 / 1000000000000)
      (by norm_num) h4 (by norm_num) (by norm_num) using 1; norm_num
  have h6 : (4 / 64 : ℝ) ^ (33 / 64 : ℝ) ≤ 239400820175 / 1000000000000 := by
    convert half_step (x := (4 / 64 : ℝ)) (e := 1 / 32) (b := 1)
      (u := 917004043205 / 1000000000000) (v := 239400820175 / 1000000000000)
      (by norm_num) h5 (by norm_num) (by norm_num) using 1; norm_num
  have h7 : (4 / 64 : ℝ) ^ (33 / 128 : ℝ) ≤ 489286031045 / 1000000000000 := by
    convert half_step (x := (4 / 64 : ℝ)) (e := 33 / 64) (b := 0)
      (u := 239400820175 / 1000000000000) (v := 489286031045 / 1000000000000)
      (by norm_num) h6 (by norm_num) (by norm_num) using 1; norm_num
  have h8 : (4 / 64 : ℝ) ^ (33 / 256 : ℝ) ≤ 699489836270 / 1000000000000 := by
    convert half_step (x := (4 / 64 : ℝ)) (e := 33 / 128) (b := 0)
      (u := 489286031045 / 1000000000000) (v := 699489836270 / 1000000000000)
      (by norm_num) h7 (by norm_num) (by norm_num) using 1; norm_num
  have h9 : (4 / 64 : ℝ) ^ (289 / 512 : ℝ) ≤ 209088772456 / 1000000000000 := by
    convert half_step (x := (4 / 64 : ℝ)) (e := 33 / 256) (b := 1)
      (u := 699489836270 / 1000000000000) (v := 209088772456 / 1000000000000)
      (by norm_num) h8 (by norm_num) (by norm_num) using 1; norm_num
  have h10 : (4 / 64 : ℝ) ^ (801 / 1024 : ℝ) ≤ 114315564464 / 1000000000000 := by
    convert half_step (x := (4 / 64 : ℝ)) (e := 289 / 512) (b := 1)
      (u := 209088772456 / 1000000000000) (v := 114315564464 / 1000000000000)
      (by norm_num) h9 (by norm_num) (by norm_num) using 1; norm_num
  have h11 : (4 / 64 : ℝ) ^ (1825 / 2048 : ℝ) ≤ 84526462005 / 1000000000000 := by
    convert half_step (x := (4 / 64 : ℝ)) (e := 801 / 1024) (b := 1)
      (u := 114315564464 / 1000000000000) (v := 84526462005 / 1000000000000)
      (by norm_num) h10 (by norm_num) (by norm_num) using 1; norm_num
  have h12 : (4 / 64 : ℝ) ^ (3873 / 4096 : ℝ) ≤ 72683587387 / 1000000000000 := by
    convert half_step (x := (4 / 64 : ℝ)) (e := 1825 / 2048) (b := 1)
      (u := 84526462005 / 1000000000000) (v := 72683587387 / 1000000000000)
      (by norm_num) h11 (by norm_num) (by norm_num) using 1; norm_num
  have h13 : (4 / 64 : ℝ) ^ (7969 / 8192 : ℝ) ≤ 67399734508 / 1000000000000 := by
    convert half_step (x := (4 / 64 : ℝ)) (e := 3873 / 4096) (b := 1)
      (u := 72683587387 / 1000000000000) (v := 67399734508 / 1000000000000)
      (by norm_num) h12 (by norm_num) (by norm_num) using 1; norm_num
  have h14 : (4 / 64 : ℝ) ^ (16161 / 16384 : ℝ) ≤ 64903647099 / 1000000000000 := by
    convert half_step (x := (4 / 64 : ℝ)) (e := 7969 / 8192) (b := 1)
      (u := 67399734508 / 1000000000000) (v := 64903647099 / 1000000000000)
      (by norm_num) h13 (by norm_num) (by norm_num) using 1; norm_num
  have h15 : (4 / 64 : ℝ) ^ (32545 / 32768 : ℝ) ≤ 63690485504 / 1000000000000 := by
    convert half_step (x := (4 / 64 : ℝ)) (e := 16161 / 16384) (b := 1)
      (u := 64903647099 / 1000000000000) (v := 63690485504 / 1000000000000)
      (by norm_num) h14 (by norm_num) (by norm_num) using 1; norm_num
  have h16 : (4 / 64 : ℝ) ^ (65313 / 65536 : ℝ) ≤ 63092434919 / 1000000000000 := by
    convert half_step (x := (4 / 64 : ℝ)) (e := 32545 / 32768) (b := 1)
      (u := 63690485504 / 1000000000000) (v := 63092434919 / 1000000000000)
      (by norm_num) h15 (by norm_num) (by norm_num) using 1; norm_num
  have h17 : (4 / 64 : ℝ) ^ (130849 / 131072 : ℝ) ≤ 62795518809 / 1000000000000 := by
    convert half_step (x := (4 / 64 : ℝ)) (e := 65313 / 65536) (b := 1)
      (u := 63092434919 / 1000000000000) (v := 62795518809 / 1000000000000)
      (by norm_num) h16 (by norm_num) (by norm_num) using 1; norm_num
  exact upper_of_rounded_exponent (by norm_num) (by norm_num) (by norm_num) h17

theorem rank_5_upper : (5 / 64 : ℝ) ^ (9983 / 10000 : ℝ) ≤ 78464604053 / 1000000000000 := by
  have h0 : (5 / 64 : ℝ) ^ (0 : ℝ) ≤ 1 := by norm_num
  have h1 : (5 / 64 : ℝ) ^ (1 / 2 : ℝ) ≤ 279508497188 / 1000000000000 := by
    convert half_step (x := (5 / 64 : ℝ)) (e := 0) (b := 1)
      (u := 1) (v := 279508497188 / 1000000000000)
      (by norm_num) h0 (by norm_num) (by norm_num) using 1; norm_num
  have h2 : (5 / 64 : ℝ) ^ (1 / 4 : ℝ) ≤ 528685631721 / 1000000000000 := by
    convert half_step (x := (5 / 64 : ℝ)) (e := 1 / 2) (b := 0)
      (u := 279508497188 / 1000000000000) (v := 528685631721 / 1000000000000)
      (by norm_num) h1 (by norm_num) (by norm_num) using 1; norm_num
  have h3 : (5 / 64 : ℝ) ^ (1 / 8 : ℝ) ≤ 727107716725 / 1000000000000 := by
    convert half_step (x := (5 / 64 : ℝ)) (e := 1 / 4) (b := 0)
      (u := 528685631721 / 1000000000000) (v := 727107716725 / 1000000000000)
      (by norm_num) h2 (by norm_num) (by norm_num) using 1; norm_num
  have h4 : (5 / 64 : ℝ) ^ (1 / 16 : ℝ) ≤ 852706113925 / 1000000000000 := by
    convert half_step (x := (5 / 64 : ℝ)) (e := 1 / 8) (b := 0)
      (u := 727107716725 / 1000000000000) (v := 852706113925 / 1000000000000)
      (by norm_num) h3 (by norm_num) (by norm_num) using 1; norm_num
  have h5 : (5 / 64 : ℝ) ^ (1 / 32 : ℝ) ≤ 923420875834 / 1000000000000 := by
    convert half_step (x := (5 / 64 : ℝ)) (e := 1 / 16) (b := 0)
      (u := 852706113925 / 1000000000000) (v := 923420875834 / 1000000000000)
      (by norm_num) h4 (by norm_num) (by norm_num) using 1; norm_num
  have h6 : (5 / 64 : ℝ) ^ (33 / 64 : ℝ) ≤ 268593104760 / 1000000000000 := by
    convert half_step (x := (5 / 64 : ℝ)) (e := 1 / 32) (b := 1)
      (u := 923420875834 / 1000000000000) (v := 268593104760 / 1000000000000)
      (by norm_num) h5 (by norm_num) (by norm_num) using 1; norm_num
  have h7 : (5 / 64 : ℝ) ^ (33 / 128 : ℝ) ≤ 518259688535 / 1000000000000 := by
    convert half_step (x := (5 / 64 : ℝ)) (e := 33 / 64) (b := 0)
      (u := 268593104760 / 1000000000000) (v := 518259688535 / 1000000000000)
      (by norm_num) h6 (by norm_num) (by norm_num) using 1; norm_num
  have h8 : (5 / 64 : ℝ) ^ (33 / 256 : ℝ) ≤ 719902554889 / 1000000000000 := by
    convert half_step (x := (5 / 64 : ℝ)) (e := 33 / 128) (b := 0)
      (u := 518259688535 / 1000000000000) (v := 719902554889 / 1000000000000)
      (by norm_num) h7 (by norm_num) (by norm_num) using 1; norm_num
  have h9 : (5 / 64 : ℝ) ^ (289 / 512 : ℝ) ≤ 237154774569 / 1000000000000 := by
    convert half_step (x := (5 / 64 : ℝ)) (e := 33 / 256) (b := 1)
      (u := 719902554889 / 1000000000000) (v := 237154774569 / 1000000000000)
      (by norm_num) h8 (by norm_num) (by norm_num) using 1; norm_num
  have h10 : (5 / 64 : ℝ) ^ (801 / 1024 : ℝ) ≤ 136116555802 / 1000000000000 := by
    convert half_step (x := (5 / 64 : ℝ)) (e := 289 / 512) (b := 1)
      (u := 237154774569 / 1000000000000) (v := 136116555802 / 1000000000000)
      (by norm_num) h9 (by norm_num) (by norm_num) using 1; norm_num
  have h11 : (5 / 64 : ℝ) ^ (1825 / 2048 : ℝ) ≤ 103121801391 / 1000000000000 := by
    convert half_step (x := (5 / 64 : ℝ)) (e := 801 / 1024) (b := 1)
      (u := 136116555802 / 1000000000000) (v := 103121801391 / 1000000000000)
      (by norm_num) h10 (by norm_num) (by norm_num) using 1; norm_num
  have h12 : (5 / 64 : ℝ) ^ (3873 / 4096 : ℝ) ≤ 89757399326 / 1000000000000 := by
    convert half_step (x := (5 / 64 : ℝ)) (e := 1825 / 2048) (b := 1)
      (u := 103121801391 / 1000000000000) (v := 89757399326 / 1000000000000)
      (by norm_num) h11 (by norm_num) (by norm_num) using 1; norm_num
  have h13 : (5 / 64 : ℝ) ^ (7969 / 8192 : ℝ) ≤ 83739457978 / 1000000000000 := by
    convert half_step (x := (5 / 64 : ℝ)) (e := 3873 / 4096) (b := 1)
      (u := 89757399326 / 1000000000000) (v := 83739457978 / 1000000000000)
      (by norm_num) h12 (by norm_num) (by norm_num) using 1; norm_num
  have h14 : (5 / 64 : ℝ) ^ (16161 / 16384 : ℝ) ≤ 80883528327 / 1000000000000 := by
    convert half_step (x := (5 / 64 : ℝ)) (e := 7969 / 8192) (b := 1)
      (u := 83739457978 / 1000000000000) (v := 80883528327 / 1000000000000)
      (by norm_num) h13 (by norm_num) (by norm_num) using 1; norm_num
  have h15 : (5 / 64 : ℝ) ^ (32545 / 32768 : ℝ) ≤ 79492299317 / 1000000000000 := by
    convert half_step (x := (5 / 64 : ℝ)) (e := 16161 / 16384) (b := 1)
      (u := 80883528327 / 1000000000000) (v := 79492299317 / 1000000000000)
      (by norm_num) h14 (by norm_num) (by norm_num) using 1; norm_num
  have h16 : (5 / 64 : ℝ) ^ (65313 / 65536 : ℝ) ≤ 78805684340 / 1000000000000 := by
    convert half_step (x := (5 / 64 : ℝ)) (e := 32545 / 32768) (b := 1)
      (u := 79492299317 / 1000000000000) (v := 78805684340 / 1000000000000)
      (by norm_num) h15 (by norm_num) (by norm_num) using 1; norm_num
  have h17 : (5 / 64 : ℝ) ^ (130849 / 131072 : ℝ) ≤ 78464604053 / 1000000000000 := by
    convert half_step (x := (5 / 64 : ℝ)) (e := 65313 / 65536) (b := 1)
      (u := 78805684340 / 1000000000000) (v := 78464604053 / 1000000000000)
      (by norm_num) h16 (by norm_num) (by norm_num) using 1; norm_num
  exact upper_of_rounded_exponent (by norm_num) (by norm_num) (by norm_num) h17

theorem rank_6_upper : (6 / 64 : ℝ) ^ (9983 / 10000 : ℝ) ≤ 94128322322 / 1000000000000 := by
  have h0 : (6 / 64 : ℝ) ^ (0 : ℝ) ≤ 1 := by norm_num
  have h1 : (6 / 64 : ℝ) ^ (1 / 2 : ℝ) ≤ 306186217848 / 1000000000000 := by
    convert half_step (x := (6 / 64 : ℝ)) (e := 0) (b := 1)
      (u := 1) (v := 306186217848 / 1000000000000)
      (by norm_num) h0 (by norm_num) (by norm_num) using 1; norm_num
  have h2 : (6 / 64 : ℝ) ^ (1 / 4 : ℝ) ≤ 553340959851 / 1000000000000 := by
    convert half_step (x := (6 / 64 : ℝ)) (e := 1 / 2) (b := 0)
      (u := 306186217848 / 1000000000000) (v := 553340959851 / 1000000000000)
      (by norm_num) h1 (by norm_num) (by norm_num) using 1; norm_num
  have h3 : (6 / 64 : ℝ) ^ (1 / 8 : ℝ) ≤ 743868913083 / 1000000000000 := by
    convert half_step (x := (6 / 64 : ℝ)) (e := 1 / 4) (b := 0)
      (u := 553340959851 / 1000000000000) (v := 743868913083 / 1000000000000)
      (by norm_num) h2 (by norm_num) (by norm_num) using 1; norm_num
  have h4 : (6 / 64 : ℝ) ^ (1 / 16 : ℝ) ≤ 862478355139 / 1000000000000 := by
    convert half_step (x := (6 / 64 : ℝ)) (e := 1 / 8) (b := 0)
      (u := 743868913083 / 1000000000000) (v := 862478355139 / 1000000000000)
      (by norm_num) h3 (by norm_num) (by norm_num) using 1; norm_num
  have h5 : (6 / 64 : ℝ) ^ (1 / 32 : ℝ) ≤ 928697127776 / 1000000000000 := by
    convert half_step (x := (6 / 64 : ℝ)) (e := 1 / 16) (b := 0)
      (u := 862478355139 / 1000000000000) (v := 928697127776 / 1000000000000)
      (by norm_num) h4 (by norm_num) (by norm_num) using 1; norm_num
  have h6 : (6 / 64 : ℝ) ^ (33 / 64 : ℝ) ≤ 295068391613 / 1000000000000 := by
    convert half_step (x := (6 / 64 : ℝ)) (e := 1 / 32) (b := 1)
      (u := 928697127776 / 1000000000000) (v := 295068391613 / 1000000000000)
      (by norm_num) h5 (by norm_num) (by norm_num) using 1; norm_num
  have h7 : (6 / 64 : ℝ) ^ (33 / 128 : ℝ) ≤ 543201980495 / 1000000000000 := by
    convert half_step (x := (6 / 64 : ℝ)) (e := 33 / 64) (b := 0)
      (u := 295068391613 / 1000000000000) (v := 543201980495 / 1000000000000)
      (by norm_num) h6 (by norm_num) (by norm_num) using 1; norm_num
  have h8 : (6 / 64 : ℝ) ^ (33 / 256 : ℝ) ≤ 737022374488 / 1000000000000 := by
    convert half_step (x := (6 / 64 : ℝ)) (e := 33 / 128) (b := 0)
      (u := 543201980495 / 1000000000000) (v := 737022374488 / 1000000000000)
      (by norm_num) h7 (by norm_num) (by norm_num) using 1; norm_num
  have h9 : (6 / 64 : ℝ) ^ (289 / 512 : ℝ) ≤ 262860890222 / 1000000000000 := by
    convert half_step (x := (6 / 64 : ℝ)) (e := 33 / 256) (b := 1)
      (u := 737022374488 / 1000000000000) (v := 262860890222 / 1000000000000)
      (by norm_num) h8 (by norm_num) (by norm_num) using 1; norm_num
  have h10 : (6 / 64 : ℝ) ^ (801 / 1024 : ℝ) ≤ 156981554517 / 1000000000000 := by
    convert half_step (x := (6 / 64 : ℝ)) (e := 289 / 512) (b := 1)
      (u := 262860890222 / 1000000000000) (v := 156981554517 / 1000000000000)
      (by norm_num) h9 (by norm_num) (by norm_num) using 1; norm_num
  have h11 : (6 / 64 : ℝ) ^ (1825 / 2048 : ℝ) ≤ 121313728556 / 1000000000000 := by
    convert half_step (x := (6 / 64 : ℝ)) (e := 801 / 1024) (b := 1)
      (u := 156981554517 / 1000000000000) (v := 121313728556 / 1000000000000)
      (by norm_num) h10 (by norm_num) (by norm_num) using 1; norm_num
  have h12 : (6 / 64 : ℝ) ^ (3873 / 4096 : ℝ) ≤ 106645028258 / 1000000000000 := by
    convert half_step (x := (6 / 64 : ℝ)) (e := 1825 / 2048) (b := 1)
      (u := 121313728556 / 1000000000000) (v := 106645028258 / 1000000000000)
      (by norm_num) h11 (by norm_num) (by norm_num) using 1; norm_num
  have h13 : (6 / 64 : ℝ) ^ (7969 / 8192 : ℝ) ≤ 99989856482 / 1000000000000 := by
    convert half_step (x := (6 / 64 : ℝ)) (e := 3873 / 4096) (b := 1)
      (u := 106645028258 / 1000000000000) (v := 99989856482 / 1000000000000)
      (by norm_num) h12 (by norm_num) (by norm_num) using 1; norm_num
  have h14 : (6 / 64 : ℝ) ^ (16161 / 16384 : ℝ) ≤ 96819672822 / 1000000000000 := by
    convert half_step (x := (6 / 64 : ℝ)) (e := 7969 / 8192) (b := 1)
      (u := 99989856482 / 1000000000000) (v := 96819672822 / 1000000000000)
      (by norm_num) h13 (by norm_num) (by norm_num) using 1; norm_num
  have h15 : (6 / 64 : ℝ) ^ (32545 / 32768 : ℝ) ≤ 95272474132 / 1000000000000 := by
    convert half_step (x := (6 / 64 : ℝ)) (e := 16161 / 16384) (b := 1)
      (u := 96819672822 / 1000000000000) (v := 95272474132 / 1000000000000)
      (by norm_num) h14 (by norm_num) (by norm_num) using 1; norm_num
  have h16 : (6 / 64 : ℝ) ^ (65313 / 65536 : ℝ) ≤ 94508171340 / 1000000000000 := by
    convert half_step (x := (6 / 64 : ℝ)) (e := 32545 / 32768) (b := 1)
      (u := 95272474132 / 1000000000000) (v := 94508171340 / 1000000000000)
      (by norm_num) h15 (by norm_num) (by norm_num) using 1; norm_num
  have h17 : (6 / 64 : ℝ) ^ (130849 / 131072 : ℝ) ≤ 94128322322 / 1000000000000 := by
    convert half_step (x := (6 / 64 : ℝ)) (e := 65313 / 65536) (b := 1)
      (u := 94508171340 / 1000000000000) (v := 94128322322 / 1000000000000)
      (by norm_num) h16 (by norm_num) (by norm_num) using 1; norm_num
  exact upper_of_rounded_exponent (by norm_num) (by norm_num) (by norm_num) h17

theorem rank_7_upper : (7 / 64 : ℝ) ^ (9983 / 10000 : ℝ) ≤ 109787578824 / 1000000000000 := by
  have h0 : (7 / 64 : ℝ) ^ (0 : ℝ) ≤ 1 := by norm_num
  have h1 : (7 / 64 : ℝ) ^ (1 / 2 : ℝ) ≤ 330718913884 / 1000000000000 := by
    convert half_step (x := (7 / 64 : ℝ)) (e := 0) (b := 1)
      (u := 1) (v := 330718913884 / 1000000000000)
      (by norm_num) h0 (by norm_num) (by norm_num) using 1; norm_num
  have h2 : (7 / 64 : ℝ) ^ (1 / 4 : ℝ) ≤ 575081658449 / 1000000000000 := by
    convert half_step (x := (7 / 64 : ℝ)) (e := 1 / 2) (b := 0)
      (u := 330718913884 / 1000000000000) (v := 575081658449 / 1000000000000)
      (by norm_num) h1 (by norm_num) (by norm_num) using 1; norm_num
  have h3 : (7 / 64 : ℝ) ^ (1 / 8 : ℝ) ≤ 758341386481 / 1000000000000 := by
    convert half_step (x := (7 / 64 : ℝ)) (e := 1 / 4) (b := 0)
      (u := 575081658449 / 1000000000000) (v := 758341386481 / 1000000000000)
      (by norm_num) h2 (by norm_num) (by norm_num) using 1; norm_num
  have h4 : (7 / 64 : ℝ) ^ (1 / 16 : ℝ) ≤ 870827989032 / 1000000000000 := by
    convert half_step (x := (7 / 64 : ℝ)) (e := 1 / 8) (b := 0)
      (u := 758341386481 / 1000000000000) (v := 870827989032 / 1000000000000)
      (by norm_num) h3 (by norm_num) (by norm_num) using 1; norm_num
  have h5 : (7 / 64 : ℝ) ^ (1 / 32 : ℝ) ≤ 933181648466 / 1000000000000 := by
    convert half_step (x := (7 / 64 : ℝ)) (e := 1 / 16) (b := 0)
      (u := 870827989032 / 1000000000000) (v := 933181648466 / 1000000000000)
      (by norm_num) h4 (by norm_num) (by norm_num) using 1; norm_num
  have h6 : (7 / 64 : ℝ) ^ (33 / 64 : ℝ) ≤ 319478861275 / 1000000000000 := by
    convert half_step (x := (7 / 64 : ℝ)) (e := 1 / 32) (b := 1)
      (u := 933181648466 / 1000000000000) (v := 319478861275 / 1000000000000)
      (by norm_num) h5 (by norm_num) (by norm_num) using 1; norm_num
  have h7 : (7 / 64 : ℝ) ^ (33 / 128 : ℝ) ≤ 565224611350 / 1000000000000 := by
    convert half_step (x := (7 / 64 : ℝ)) (e := 33 / 64) (b := 0)
      (u := 319478861275 / 1000000000000) (v := 565224611350 / 1000000000000)
      (by norm_num) h6 (by norm_num) (by norm_num) using 1; norm_num
  have h8 : (7 / 64 : ℝ) ^ (33 / 256 : ℝ) ≤ 751814213321 / 1000000000000 := by
    convert half_step (x := (7 / 64 : ℝ)) (e := 33 / 128) (b := 0)
      (u := 565224611350 / 1000000000000) (v := 751814213321 / 1000000000000)
      (by norm_num) h7 (by norm_num) (by norm_num) using 1; norm_num
  have h9 : (7 / 64 : ℝ) ^ (289 / 512 : ℝ) ≤ 286757178781 / 1000000000000 := by
    convert half_step (x := (7 / 64 : ℝ)) (e := 33 / 256) (b := 1)
      (u := 751814213321 / 1000000000000) (v := 286757178781 / 1000000000000)
      (by norm_num) h8 (by norm_num) (by norm_num) using 1; norm_num
  have h10 : (7 / 64 : ℝ) ^ (801 / 1024 : ℝ) ≤ 177099030007 / 1000000000000 := by
    convert half_step (x := (7 / 64 : ℝ)) (e := 289 / 512) (b := 1)
      (u := 286757178781 / 1000000000000) (v := 177099030007 / 1000000000000)
      (by norm_num) h9 (by norm_num) (by norm_num) using 1; norm_num
  have h11 : (7 / 64 : ℝ) ^ (1825 / 2048 : ℝ) ≤ 139176888912 / 1000000000000 := by
    convert half_step (x := (7 / 64 : ℝ)) (e := 801 / 1024) (b := 1)
      (u := 177099030007 / 1000000000000) (v := 139176888912 / 1000000000000)
      (by norm_num) h10 (by norm_num) (by norm_num) using 1; norm_num
  have h12 : (7 / 64 : ℝ) ^ (3873 / 4096 : ℝ) ≤ 123379383306 / 1000000000000 := by
    convert half_step (x := (7 / 64 : ℝ)) (e := 1825 / 2048) (b := 1)
      (u := 139176888912 / 1000000000000) (v := 123379383306 / 1000000000000)
      (by norm_num) h11 (by norm_num) (by norm_num) using 1; norm_num
  have h13 : (7 / 64 : ℝ) ^ (7969 / 8192 : ℝ) ≤ 116166346457 / 1000000000000 := by
    convert half_step (x := (7 / 64 : ℝ)) (e := 3873 / 4096) (b := 1)
      (u := 123379383306 / 1000000000000) (v := 116166346457 / 1000000000000)
      (by norm_num) h12 (by norm_num) (by norm_num) using 1; norm_num
  have h14 : (7 / 64 : ℝ) ^ (16161 / 16384 : ℝ) ≤ 112719537543 / 1000000000000 := by
    convert half_step (x := (7 / 64 : ℝ)) (e := 7969 / 8192) (b := 1)
      (u := 116166346457 / 1000000000000) (v := 112719537543 / 1000000000000)
      (by norm_num) h13 (by norm_num) (by norm_num) using 1; norm_num
  have h15 : (7 / 64 : ℝ) ^ (32545 / 32768 : ℝ) ≤ 111034676650 / 1000000000000 := by
    convert half_step (x := (7 / 64 : ℝ)) (e := 16161 / 16384) (b := 1)
      (u := 112719537543 / 1000000000000) (v := 111034676650 / 1000000000000)
      (by norm_num) h14 (by norm_num) (by norm_num) using 1; norm_num
  have h16 : (7 / 64 : ℝ) ^ (65313 / 65536 : ℝ) ≤ 110201713955 / 1000000000000 := by
    convert half_step (x := (7 / 64 : ℝ)) (e := 32545 / 32768) (b := 1)
      (u := 111034676650 / 1000000000000) (v := 110201713955 / 1000000000000)
      (by norm_num) h15 (by norm_num) (by norm_num) using 1; norm_num
  have h17 : (7 / 64 : ℝ) ^ (130849 / 131072 : ℝ) ≤ 109787578824 / 1000000000000 := by
    convert half_step (x := (7 / 64 : ℝ)) (e := 65313 / 65536) (b := 1)
      (u := 110201713955 / 1000000000000) (v := 109787578824 / 1000000000000)
      (by norm_num) h16 (by norm_num) (by norm_num) using 1; norm_num
  exact upper_of_rounded_exponent (by norm_num) (by norm_num) (by norm_num) h17

theorem rank_42_upper : (42 / 64 : ℝ) ^ (9983 / 10000 : ℝ) ≤ 656720459372 / 1000000000000 := by
  have h0 : (42 / 64 : ℝ) ^ (0 : ℝ) ≤ 1 := by norm_num
  have h1 : (42 / 64 : ℝ) ^ (1 / 2 : ℝ) ≤ 810092587301 / 1000000000000 := by
    convert half_step (x := (42 / 64 : ℝ)) (e := 0) (b := 1)
      (u := 1) (v := 810092587301 / 1000000000000)
      (by norm_num) h0 (by norm_num) (by norm_num) using 1; norm_num
  have h2 : (42 / 64 : ℝ) ^ (1 / 4 : ℝ) ≤ 900051435920 / 1000000000000 := by
    convert half_step (x := (42 / 64 : ℝ)) (e := 1 / 2) (b := 0)
      (u := 810092587301 / 1000000000000) (v := 900051435920 / 1000000000000)
      (by norm_num) h1 (by norm_num) (by norm_num) using 1; norm_num
  have h3 : (42 / 64 : ℝ) ^ (1 / 8 : ℝ) ≤ 948710406774 / 1000000000000 := by
    convert half_step (x := (42 / 64 : ℝ)) (e := 1 / 4) (b := 0)
      (u := 900051435920 / 1000000000000) (v := 948710406774 / 1000000000000)
      (by norm_num) h2 (by norm_num) (by norm_num) using 1; norm_num
  have h4 : (42 / 64 : ℝ) ^ (1 / 16 : ℝ) ≤ 974017662455 / 1000000000000 := by
    convert half_step (x := (42 / 64 : ℝ)) (e := 1 / 8) (b := 0)
      (u := 948710406774 / 1000000000000) (v := 974017662455 / 1000000000000)
      (by norm_num) h3 (by norm_num) (by norm_num) using 1; norm_num
  have h5 : (42 / 64 : ℝ) ^ (1 / 32 : ℝ) ≤ 986923331600 / 1000000000000 := by
    convert half_step (x := (42 / 64 : ℝ)) (e := 1 / 16) (b := 0)
      (u := 974017662455 / 1000000000000) (v := 986923331600 / 1000000000000)
      (by norm_num) h4 (by norm_num) (by norm_num) using 1; norm_num
  have h6 : (42 / 64 : ℝ) ^ (33 / 64 : ℝ) ≤ 804778501430 / 1000000000000 := by
    convert half_step (x := (42 / 64 : ℝ)) (e := 1 / 32) (b := 1)
      (u := 986923331600 / 1000000000000) (v := 804778501430 / 1000000000000)
      (by norm_num) h5 (by norm_num) (by norm_num) using 1; norm_num
  have h7 : (42 / 64 : ℝ) ^ (33 / 128 : ℝ) ≤ 897094477427 / 1000000000000 := by
    convert half_step (x := (42 / 64 : ℝ)) (e := 33 / 64) (b := 0)
      (u := 804778501430 / 1000000000000) (v := 897094477427 / 1000000000000)
      (by norm_num) h6 (by norm_num) (by norm_num) using 1; norm_num
  have h8 : (42 / 64 : ℝ) ^ (33 / 256 : ℝ) ≤ 947150715265 / 1000000000000 := by
    convert half_step (x := (42 / 64 : ℝ)) (e := 33 / 128) (b := 0)
      (u := 897094477427 / 1000000000000) (v := 947150715265 / 1000000000000)
      (by norm_num) h7 (by norm_num) (by norm_num) using 1; norm_num
  have h9 : (42 / 64 : ℝ) ^ (289 / 512 : ℝ) ≤ 788395622066 / 1000000000000 := by
    convert half_step (x := (42 / 64 : ℝ)) (e := 33 / 256) (b := 1)
      (u := 947150715265 / 1000000000000) (v := 788395622066 / 1000000000000)
      (by norm_num) h8 (by norm_num) (by norm_num) using 1; norm_num
  have h10 : (42 / 64 : ℝ) ^ (801 / 1024 : ℝ) ≤ 719294534236 / 1000000000000 := by
    convert half_step (x := (42 / 64 : ℝ)) (e := 289 / 512) (b := 1)
      (u := 788395622066 / 1000000000000) (v := 719294534236 / 1000000000000)
      (by norm_num) h9 (by norm_num) (by norm_num) using 1; norm_num
  have h11 : (42 / 64 : ℝ) ^ (1825 / 2048 : ℝ) ≤ 687049516478 / 1000000000000 := by
    convert half_step (x := (42 / 64 : ℝ)) (e := 801 / 1024) (b := 1)
      (u := 719294534236 / 1000000000000) (v := 687049516478 / 1000000000000)
      (by norm_num) h10 (by norm_num) (by norm_num) using 1; norm_num
  have h12 : (42 / 64 : ℝ) ^ (3873 / 4096 : ℝ) ≤ 671473190224 / 1000000000000 := by
    convert half_step (x := (42 / 64 : ℝ)) (e := 1825 / 2048) (b := 1)
      (u := 687049516478 / 1000000000000) (v := 671473190224 / 1000000000000)
      (by norm_num) h11 (by norm_num) (by norm_num) using 1; norm_num
  have h13 : (42 / 64 : ℝ) ^ (7969 / 8192 : ℝ) ≤ 663817957791 / 1000000000000 := by
    convert half_step (x := (42 / 64 : ℝ)) (e := 3873 / 4096) (b := 1)
      (u := 671473190224 / 1000000000000) (v := 663817957791 / 1000000000000)
      (by norm_num) h12 (by norm_num) (by norm_num) using 1; norm_num
  have h14 : (42 / 64 : ℝ) ^ (16161 / 16384 : ℝ) ≤ 660023132020 / 1000000000000 := by
    convert half_step (x := (42 / 64 : ℝ)) (e := 7969 / 8192) (b := 1)
      (u := 663817957791 / 1000000000000) (v := 660023132020 / 1000000000000)
      (by norm_num) h13 (by norm_num) (by norm_num) using 1; norm_num
  have h15 : (42 / 64 : ℝ) ^ (32545 / 32768 : ℝ) ≤ 658133862059 / 1000000000000 := by
    convert half_step (x := (42 / 64 : ℝ)) (e := 16161 / 16384) (b := 1)
      (u := 660023132020 / 1000000000000) (v := 658133862059 / 1000000000000)
      (by norm_num) h14 (by norm_num) (by norm_num) using 1; norm_num
  have h16 : (42 / 64 : ℝ) ^ (65313 / 65536 : ℝ) ≤ 657191256011 / 1000000000000 := by
    convert half_step (x := (42 / 64 : ℝ)) (e := 32545 / 32768) (b := 1)
      (u := 658133862059 / 1000000000000) (v := 657191256011 / 1000000000000)
      (by norm_num) h15 (by norm_num) (by norm_num) using 1; norm_num
  have h17 : (42 / 64 : ℝ) ^ (130849 / 131072 : ℝ) ≤ 656720459372 / 1000000000000 := by
    convert half_step (x := (42 / 64 : ℝ)) (e := 65313 / 65536) (b := 1)
      (u := 657191256011 / 1000000000000) (v := 656720459372 / 1000000000000)
      (by norm_num) h16 (by norm_num) (by norm_num) using 1; norm_num
  exact upper_of_rounded_exponent (by norm_num) (by norm_num) (by norm_num) h17

noncomputable def upper : Fin 8 → ℝ := ![15735950448 / 1000000000000, 31434808292 / 1000000000000, 47119696168 / 1000000000000, 62795518809 / 1000000000000, 78464604053 / 1000000000000, 94128322322 / 1000000000000, 109787578824 / 1000000000000, 656720459372 / 1000000000000]

theorem per_rank_upper : ∀ r, ((ranks r : ℝ) / 64) ^ exponent ≤ upper r := by
  intro r
  fin_cases r
  · simpa [ranks, exponent, upper] using rank_1_upper
  · simpa [ranks, exponent, upper] using rank_2_upper
  · simpa [ranks, exponent, upper] using rank_3_upper
  · simpa [ranks, exponent, upper] using rank_4_upper
  · simpa [ranks, exponent, upper] using rank_5_upper
  · simpa [ranks, exponent, upper] using rank_6_upper
  · simpa [ranks, exponent, upper] using rank_7_upper
  · simpa [ranks, exponent, upper] using rank_42_upper

theorem fractional_moment_upper : fractionalMoment ≤ 11290320473664709188758299 / 11291503906250000000000000 := by
  calc
    fractionalMoment ≤ (∑ r, weight r * upper r) + bad * upper 0 := by
      unfold fractionalMoment
      apply add_le_add
      · exact Finset.sum_le_sum fun r _ => mul_le_mul_of_nonneg_left (per_rank_upper r) (by unfold weight; positivity)
      · apply mul_le_mul_of_nonneg_left _ (by norm_num [bad])
        simpa [exponent, upper] using rank_1_upper
    _ = 11290320473664709188758299 / 11291503906250000000000000 := by norm_num [Fin.sum_univ_succ, weight, counts, upper, bad]

theorem fractional_moment_strict : fractionalMoment < 9999 / 10000 :=
  lt_of_le_of_lt fractional_moment_upper (by norm_num)

end SelectedBitMoment

#print axioms SelectedBitMoment.rank_1_upper
#print axioms SelectedBitMoment.rank_2_upper
#print axioms SelectedBitMoment.rank_3_upper
#print axioms SelectedBitMoment.rank_4_upper
#print axioms SelectedBitMoment.rank_5_upper
#print axioms SelectedBitMoment.rank_6_upper
#print axioms SelectedBitMoment.rank_7_upper
#print axioms SelectedBitMoment.rank_42_upper
#print axioms SelectedBitMoment.per_rank_upper
#print axioms SelectedBitMoment.fractional_moment_upper
#print axioms SelectedBitMoment.fractional_moment_strict

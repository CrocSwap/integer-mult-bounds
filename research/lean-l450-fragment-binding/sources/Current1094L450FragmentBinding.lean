import Current1094L450FragmentDiagnostic
import Current1094L450FragmentData
import AsciiUtf8RoundTrip

/-!
Structural proof repair for the exact same literal/payload equality. The failed
single full byte-array decision is preserved. Accepted typed Nat values are
reused, decimal text is certified in nine groups of eight columns, and the generic
ASCII representation theorem removes all per-byte UTF-8 branch reduction.
There is no #eval, new parser, cap increase or selected-table census. The only
new text is the already byte-bound907-byte original fragment, grouped without
changing order. External file/member provenance remains separate.
Kappa=836330098538459/500000000000000000=0.001672660197076918.
Lean/Mathlib; Rohan Arun PR1094; Jeremy Kothe T16/PR514; accepted bank/frame
components. James Chang with OpenAI assistance. Apache-2.0. Uncompiled.
-/
set_option Elab.async false
set_option autoImplicit false
namespace CurrentMain.Current1094L450FragmentBinding
open Current1094L450FragmentDiagnostic (originalFragment)
open Current1094L450RecoveredEntry (columns)
open Current1094L450FragmentData (values typed_values)
open CompactNatColumnFragment (payload natArrayText natValues decimalTail)

private theorem decimalTail_append (xs ys : List Nat) :
    decimalTail (xs ++ ys) = decimalTail xs ++ decimalTail ys := by
  induction xs with
  | nil => simp only [List.nil_append, decimalTail, String.empty_append]
  | cons x xs ih =>
      simp only [List.cons_append, decimalTail, ih, String.append_assoc]

private theorem first_decimal : Nat.repr (386 : Nat) = "386" := by decide +kernel

private def group0 : List Nat := [4, 8, 16, 32, 64, 259, 385, 131]
private theorem tail0 : decimalTail group0 = ",4,8,16,32,64,259,385,131" := by
  decide +kernel

private def group1 : List Nat := [512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]
private theorem tail1 : decimalTail group1 = ",512,1024,2048,4096,8192,16384,32768,65536" := by
  decide +kernel

private def group2 : List Nat := [131072, 262144, 524288, 1048576, 2097152, 4194304, 8388608, 16777216]
private theorem tail2 : decimalTail group2 = ",131072,262144,524288,1048576,2097152,4194304,8388608,16777216" := by
  decide +kernel

private def group3 : List Nat := [33554432, 67108864, 134217728, 268435456, 536870912, 1073741824, 2147483648, 4294967296]
private theorem tail3 : decimalTail group3 = ",33554432,67108864,134217728,268435456,536870912,1073741824,2147483648,4294967296" := by
  decide +kernel

private def group4 : List Nat := [8589934592, 17179869184, 34359738368, 68719476736, 137438953472, 274877906944, 549755813888, 1099511627776]
private theorem tail4 : decimalTail group4 = ",8589934592,17179869184,34359738368,68719476736,137438953472,274877906944,549755813888,1099511627776" := by
  decide +kernel

private def group5 : List Nat := [2199023255552, 4398046511104, 8796093022208, 17592186044416, 35184372088832, 70368744177664, 140737488355328, 281474976710656]
private theorem tail5 : decimalTail group5 = ",2199023255552,4398046511104,8796093022208,17592186044416,35184372088832,70368744177664,140737488355328,281474976710656" := by
  decide +kernel

private def group6 : List Nat := [562949953421312, 1125899906842624, 2251799813685248, 4503599627370496, 9007199254740992, 18014398509481984, 36028797018963968, 72057594037927936]
private theorem tail6 : decimalTail group6 = ",562949953421312,1125899906842624,2251799813685248,4503599627370496,9007199254740992,18014398509481984,36028797018963968,72057594037927936" := by
  decide +kernel

private def group7 : List Nat := [144115188075855872, 288230376151711744, 576460752303423488, 1152921504606846976, 2305843009213693952, 4611686018427387904, 9223372036854775808, 18446744073709551616]
private theorem tail7 : decimalTail group7 = ",144115188075855872,288230376151711744,576460752303423488,1152921504606846976,2305843009213693952,4611686018427387904,9223372036854775808,18446744073709551616" := by
  decide +kernel

private def group8 : List Nat := [36893488147419103232, 73786976294838206464, 147573952589676412928, 295147905179352825856, 590295810358705651712, 1180591620717411303424, 2361183241434822606848, 4722366482869645213696]
private theorem tail8 : decimalTail group8 = ",36893488147419103232,73786976294838206464,147573952589676412928,295147905179352825856,590295810358705651712,1180591620717411303424,2361183241434822606848,4722366482869645213696" := by
  decide +kernel

private def compactText : String := "[386,4,8,16,32,64,259,385,131,512,1024,2048,4096,8192,16384,32768,65536,131072,262144,524288,1048576,2097152,4194304,8388608,16777216,33554432,67108864,134217728,268435456,536870912,1073741824,2147483648,4294967296,8589934592,17179869184,34359738368,68719476736,137438953472,274877906944,549755813888,1099511627776,2199023255552,4398046511104,8796093022208,17592186044416,35184372088832,70368744177664,140737488355328,281474976710656,562949953421312,1125899906842624,2251799813685248,4503599627370496,9007199254740992,18014398509481984,36028797018963968,72057594037927936,144115188075855872,288230376151711744,576460752303423488,1152921504606846976,2305843009213693952,4611686018427387904,9223372036854775808,18446744073709551616,36893488147419103232,73786976294838206464,147573952589676412928,295147905179352825856,590295810358705651712,1180591620717411303424,2361183241434822606848,4722366482869645213696]"

private theorem text_eq : natArrayText values = compactText := by
  change "[" ++ Nat.repr (386 : Nat) ++ decimalTail (group0 ++ group1 ++ group2 ++ group3 ++ group4 ++ group5 ++ group6 ++ group7 ++ group8) ++ "]" = compactText
  simp only [decimalTail_append, tail0, tail1, tail2, tail3, tail4, tail5, tail6, tail7, tail8, first_decimal]
  decide +kernel

theorem literal_data_eq_payload : originalFragment.data = (payload columns).data := by
  apply Array.ext'
  change originalFragment.data.toList =
    (CompactNatColumnFragment.encode (natValues columns)).data.toList
  rw [typed_values, CompactNatColumnAscii.encode_one_byte, text_eq]
  decide +kernel

theorem literal_eq_payload : originalFragment = payload columns :=
  congrArg ByteArray.mk literal_data_eq_payload

theorem literal_utf8 : String.fromUTF8? originalFragment =
    some (natArrayText (natValues columns)) := by
  rw [literal_eq_payload]
  exact AsciiUtf8RoundTrip.payload_roundtrip columns

theorem validation_of_parser
    (hp : ByteJsonGlobalCall.parseBytes originalFragment =
      .ok (StrictJsonValueBridge.reencode 2 (ParsedBinaryChartCertificate.vectorValue columns))) :
    CompactNatColumnFragment.validateFragment 73 originalFragment = some columns := by
  rw [literal_eq_payload] at hp ⊢
  exact CompactNatColumnFragment.validate_complete columns hp

end CurrentMain.Current1094L450FragmentBinding
#print axioms CurrentMain.Current1094L450FragmentBinding.literal_data_eq_payload
#print axioms CurrentMain.Current1094L450FragmentBinding.literal_eq_payload
#print axioms CurrentMain.Current1094L450FragmentBinding.literal_utf8
#print axioms CurrentMain.Current1094L450FragmentBinding.validation_of_parser
#check CurrentMain.Current1094L450FragmentBinding.literal_eq_payload
#check CurrentMain.Current1094L450FragmentBinding.validation_of_parser

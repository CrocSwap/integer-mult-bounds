/-
V2FloorKernel_j (lane LEAN-KERNEL, Nov 16): the joint V2-FLOOR bound for #7623's relaxed JB model, KERNEL-ONLY
(decide +kernel throughout; no native_decide / ofReduceBool / implemented_by; sorry-free). See V2FloorKernel.md.
-/
import Nov15.V2FloorKernelBase_j
import Nov15.V2FloorKernelBase1_j
import Nov15.V2FloorKernelBase2_j
import Nov15.V2FloorKernelBase3_j
import Nov15.V2FloorKernelBase4_j
import Nov15.V2FloorKernelBase5_j
import Nov15.V2FloorKernelBase6_j
import Nov15.V2FloorKernelBaseA_j
import Nov15.V2FloorKernelE_j_7_a
import Nov15.V2FloorKernelE_j_7_b
import Nov15.V2FloorKernelE_j_13_a
import Nov15.V2FloorKernelE_j_13_b
import Nov15.V2FloorKernelE_j_14_a
import Nov15.V2FloorKernelE_j_14_b
import Nov15.V2FloorKernelE_j_19_a
import Nov15.V2FloorKernelE_j_19_b
import Nov15.V2FloorKernelE_j_21_a
import Nov15.V2FloorKernelE_j_21_b
import Nov15.V2FloorKernelE_j_22_a
import Nov15.V2FloorKernelE_j_22_b
import Nov15.V2FloorKernelE_j_25_a
import Nov15.V2FloorKernelE_j_25_b
import Nov15.V2FloorKernelE_j_26_a
import Nov15.V2FloorKernelE_j_26_b
import Nov15.V2FloorKernelE_j_28_a
import Nov15.V2FloorKernelE_j_28_b
import Nov15.V2FloorKernelE_j_30_a
import Nov15.V2FloorKernelE_j_30_b
import Nov15.V2FloorKernelE_j_35_a
import Nov15.V2FloorKernelE_j_35_b
import Nov15.V2FloorKernelE_j_37_a
import Nov15.V2FloorKernelE_j_37_b
import Nov15.V2FloorKernelE_j_38_a
import Nov15.V2FloorKernelE_j_38_b
import Nov15.V2FloorKernelE_j_41_a
import Nov15.V2FloorKernelE_j_41_b
import Nov15.V2FloorKernelE_j_44_a
import Nov15.V2FloorKernelE_j_44_b
import Nov15.V2FloorKernelE_j_49_a
import Nov15.V2FloorKernelE_j_49_b
import Nov15.V2FloorKernelE_j_50_a
import Nov15.V2FloorKernelE_j_50_b
import Nov15.V2FloorKernelE_j_51_a
import Nov15.V2FloorKernelE_j_51_b
import Nov15.V2FloorKernelE_j_52_a
import Nov15.V2FloorKernelE_j_52_b
import Nov15.V2FloorKernelE_j_56_a
import Nov15.V2FloorKernelE_j_56_b
import Nov15.V2FloorKernelE_j_67_a
import Nov15.V2FloorKernelE_j_67_b
import Nov15.V2FloorKernelE_j_69_a
import Nov15.V2FloorKernelE_j_69_b
import Nov15.V2FloorKernelE_j_70_a
import Nov15.V2FloorKernelE_j_70_b
import Nov15.V2FloorKernelE_j_74_a
import Nov15.V2FloorKernelE_j_74_b
import Nov15.V2FloorKernelE_j_75_a
import Nov15.V2FloorKernelE_j_75_b
import Nov15.V2FloorKernelE_j_81_a
import Nov15.V2FloorKernelE_j_81_b
import Nov15.V2FloorKernelE_j_82_a
import Nov15.V2FloorKernelE_j_82_b
import Nov15.V2FloorKernelE_j_85_a
import Nov15.V2FloorKernelE_j_85_b
import Nov15.V2FloorKernelE_j_88_a
import Nov15.V2FloorKernelE_j_88_b
import Nov15.V2FloorKernelE_j_98_a
import Nov15.V2FloorKernelE_j_98_b
import Nov15.V2FloorKernelE_j_100_a
import Nov15.V2FloorKernelE_j_100_b
import Nov15.V2FloorKernelE_j_102_a
import Nov15.V2FloorKernelE_j_102_b
import Nov15.V2FloorKernelE_j_120_a
import Nov15.V2FloorKernelE_j_120_b
import Nov15.V2FloorKernelE_j_131_a
import Nov15.V2FloorKernelE_j_131_b
import Nov15.V2FloorKernelE_j_133_a
import Nov15.V2FloorKernelE_j_133_b
import Nov15.V2FloorKernelE_j_134_a
import Nov15.V2FloorKernelE_j_134_b
import Nov15.V2FloorKernelE_j_137_a
import Nov15.V2FloorKernelE_j_137_b
import Nov15.V2FloorKernelE_j_138_a
import Nov15.V2FloorKernelE_j_138_b
import Nov15.V2FloorKernelE_j_140_a
import Nov15.V2FloorKernelE_j_140_b
import Nov15.V2FloorKernelE_j_145_a
import Nov15.V2FloorKernelE_j_145_b
import Nov15.V2FloorKernelE_j_152_a
import Nov15.V2FloorKernelE_j_152_b
import Nov15.V2FloorKernelE_j_164_a
import Nov15.V2FloorKernelE_j_164_b
import Nov15.V2FloorKernelE_j_168_a
import Nov15.V2FloorKernelE_j_168_b
import Nov15.V2FloorKernelE_j_176_a
import Nov15.V2FloorKernelE_j_176_b
import Nov15.V2FloorKernelE_j_191_a
import Nov15.V2FloorKernelE_j_191_b
import Nov15.V2FloorKernelE_j_193_a
import Nov15.V2FloorKernelE_j_193_b
import Nov15.V2FloorKernelE_j_194_a
import Nov15.V2FloorKernelE_j_194_b
import Nov15.V2FloorKernelE_j_196_a
import Nov15.V2FloorKernelE_j_196_b
import Nov15.V2FloorKernelE_j_200_a
import Nov15.V2FloorKernelE_j_200_b
import Nov15.V2FloorKernelE_j_224_a
import Nov15.V2FloorKernelE_j_224_b
import Nov15.V2FloorKernelE_j_239_a
import Nov15.V2FloorKernelE_j_239_b
import Nov15.V2FloorKernelE_j_247_a
import Nov15.V2FloorKernelE_j_247_b
import Nov15.V2FloorKernelE_j_251_a
import Nov15.V2FloorKernelE_j_251_b
import Nov15.V2FloorKernelE_j_253_a
import Nov15.V2FloorKernelE_j_253_b
import Nov15.V2FloorKernelE_j_254_a
import Nov15.V2FloorKernelE_j_254_b
import Nov15.V2FloorKernelE_j_259_a
import Nov15.V2FloorKernelE_j_259_b
import Nov15.V2FloorKernelE_j_261_a
import Nov15.V2FloorKernelE_j_261_b
import Nov15.V2FloorKernelE_j_262_a
import Nov15.V2FloorKernelE_j_262_b
import Nov15.V2FloorKernelE_j_268_a
import Nov15.V2FloorKernelE_j_268_b
import Nov15.V2FloorKernelE_j_273_a
import Nov15.V2FloorKernelE_j_273_b
import Nov15.V2FloorKernelE_j_274_a
import Nov15.V2FloorKernelE_j_274_b
import Nov15.V2FloorKernelE_j_276_a
import Nov15.V2FloorKernelE_j_276_b
import Nov15.V2FloorKernelE_j_280_a
import Nov15.V2FloorKernelE_j_280_b
import Nov15.V2FloorKernelE_j_290_a
import Nov15.V2FloorKernelE_j_290_b
import Nov15.V2FloorKernelE_j_292_a
import Nov15.V2FloorKernelE_j_292_b
import Nov15.V2FloorKernelE_j_296_a
import Nov15.V2FloorKernelE_j_296_b
import Nov15.V2FloorKernelE_j_304_a
import Nov15.V2FloorKernelE_j_304_b
import Nov15.V2FloorKernelE_j_319_a
import Nov15.V2FloorKernelE_j_319_b
import Nov15.V2FloorKernelE_j_321_a
import Nov15.V2FloorKernelE_j_321_b
import Nov15.V2FloorKernelE_j_322_a
import Nov15.V2FloorKernelE_j_322_b
import Nov15.V2FloorKernelE_j_324_a
import Nov15.V2FloorKernelE_j_324_b
import Nov15.V2FloorKernelE_j_328_a
import Nov15.V2FloorKernelE_j_328_b
import Nov15.V2FloorKernelE_j_351_a
import Nov15.V2FloorKernelE_j_351_b
import Nov15.V2FloorKernelE_j_352_a
import Nov15.V2FloorKernelE_j_352_b
import Nov15.V2FloorKernelE_j_367_a
import Nov15.V2FloorKernelE_j_367_b
import Nov15.V2FloorKernelE_j_375_a
import Nov15.V2FloorKernelE_j_375_b
import Nov15.V2FloorKernelE_j_379_a
import Nov15.V2FloorKernelE_j_379_b
import Nov15.V2FloorKernelE_j_381_a
import Nov15.V2FloorKernelE_j_381_b
import Nov15.V2FloorKernelE_j_382_a
import Nov15.V2FloorKernelE_j_382_b
import Nov15.V2FloorKernelE_j_385_a
import Nov15.V2FloorKernelE_j_385_b
import Nov15.V2FloorKernelE_j_386_a
import Nov15.V2FloorKernelE_j_386_b
import Nov15.V2FloorKernelE_j_388_a
import Nov15.V2FloorKernelE_j_388_b
import Nov15.V2FloorKernelE_j_392_a
import Nov15.V2FloorKernelE_j_392_b
import Nov15.V2FloorKernelE_j_415_a
import Nov15.V2FloorKernelE_j_415_b
import Nov15.V2FloorKernelE_j_416_a
import Nov15.V2FloorKernelE_j_416_b
import Nov15.V2FloorKernelE_j_431_a
import Nov15.V2FloorKernelE_j_431_b
import Nov15.V2FloorKernelE_j_443_a
import Nov15.V2FloorKernelE_j_443_b
import Nov15.V2FloorKernelE_j_445_a
import Nov15.V2FloorKernelE_j_445_b
import Nov15.V2FloorKernelE_j_446_a
import Nov15.V2FloorKernelE_j_446_b
import Nov15.V2FloorKernelE_j_448_a
import Nov15.V2FloorKernelE_j_448_b
import Nov15.V2FloorKernelE_j_463_a
import Nov15.V2FloorKernelE_j_463_b
import Nov15.V2FloorKernelE_j_471_a
import Nov15.V2FloorKernelE_j_471_b
import Nov15.V2FloorKernelE_j_475_a
import Nov15.V2FloorKernelE_j_475_b
import Nov15.V2FloorKernelE_j_477_a
import Nov15.V2FloorKernelE_j_477_b
import Nov15.V2FloorKernelE_j_478_a
import Nov15.V2FloorKernelE_j_478_b
import Nov15.V2FloorKernelE_j_491_a
import Nov15.V2FloorKernelE_j_491_b
import Nov15.V2FloorKernelE_j_493_a
import Nov15.V2FloorKernelE_j_493_b
import Nov15.V2FloorKernelE_j_499_a
import Nov15.V2FloorKernelE_j_499_b
import Nov15.V2FloorKernelE_j_501_a
import Nov15.V2FloorKernelE_j_501_b
import Nov15.V2FloorKernelE_j_502_a
import Nov15.V2FloorKernelE_j_502_b
import Nov15.V2FloorKernelE_j_505_a
import Nov15.V2FloorKernelE_j_505_b
import Nov15.V2FloorKernelE_j_506_a
import Nov15.V2FloorKernelE_j_506_b
import Nov15.V2FloorKernelE_j_508_a
import Nov15.V2FloorKernelE_j_508_b
import Nov15.V2FloorKernelF_j_1
import Nov15.V2FloorKernelF_j_9
import Nov15.V2FloorKernelF_j_17
import Nov15.V2FloorKernelF_j_25
import Nov15.V2FloorKernelF_j_33
import Nov15.V2FloorKernelF_j_41
import Nov15.V2FloorKernelF_j_49
import Nov15.V2FloorKernelF_j_57
import Nov15.V2FloorKernelF_j_65
import Nov15.V2FloorKernelF_j_73
import Nov15.V2FloorKernelF_j_81
import Nov15.V2FloorKernelF_j_89
import Nov15.V2FloorKernelF_j_97
import Nov15.V2FloorKernelF_j_105
import Nov15.V2FloorKernelF_j_113
import Nov15.V2FloorKernelF_j_121
import Nov15.V2FloorKernelF_j_129
import Nov15.V2FloorKernelF_j_137
import Nov15.V2FloorKernelF_j_145
import Nov15.V2FloorKernelF_j_153
import Nov15.V2FloorKernelF_j_161
import Nov15.V2FloorKernelF_j_169
import Nov15.V2FloorKernelF_j_177
import Nov15.V2FloorKernelF_j_185
import Nov15.V2FloorKernelF_j_193
import Nov15.V2FloorKernelF_j_201
import Nov15.V2FloorKernelF_j_209
import Nov15.V2FloorKernelF_j_217
import Nov15.V2FloorKernelF_j_225
import Nov15.V2FloorKernelF_j_233
import Nov15.V2FloorKernelF_j_241
import Nov15.V2FloorKernelF_j_249
import Nov15.V2FloorKernelF_j_257
import Nov15.V2FloorKernelF_j_265
import Nov15.V2FloorKernelF_j_273
import Nov15.V2FloorKernelF_j_281
import Nov15.V2FloorKernelF_j_289
import Nov15.V2FloorKernelF_j_297
import Nov15.V2FloorKernelF_j_305
import Nov15.V2FloorKernelF_j_313
import Nov15.V2FloorKernelF_j_321
import Nov15.V2FloorKernelF_j_329
import Nov15.V2FloorKernelF_j_337
import Nov15.V2FloorKernelF_j_345
import Nov15.V2FloorKernelF_j_353
import Nov15.V2FloorKernelF_j_361
import Nov15.V2FloorKernelF_j_369
import Nov15.V2FloorKernelF_j_377
import Nov15.V2FloorKernelF_j_385
import Nov15.V2FloorKernelF_j_393
import Nov15.V2FloorKernelF_j_401
import Nov15.V2FloorKernelF_j_409
import Nov15.V2FloorKernelF_j_417
import Nov15.V2FloorKernelF_j_425
import Nov15.V2FloorKernelF_j_433
import Nov15.V2FloorKernelF_j_441
import Nov15.V2FloorKernelF_j_449
import Nov15.V2FloorKernelF_j_457
import Nov15.V2FloorKernelF_j_465
import Nov15.V2FloorKernelF_j_473
import Nov15.V2FloorKernelF_j_481
import Nov15.V2FloorKernelF_j_489
import Nov15.V2FloorKernelF_j_497
import Nov15.V2FloorKernelF_j_505
import Nov15.V2FloorKernelCost
import Nov15.V2FloorDefs_j
set_option maxRecDepth 100000
set_option maxHeartbeats 0
namespace V2Floor

theorem KE1_j : ∀ l < 512, (LT_j.get 9 l).isEmpty = true ∨ lineOK LT_j T_jk l = true := by
  have hall : ∀ l ∈ NL_j, lineOK LT_j T_jk l = true :=
    List.forall_iff_forall_mem.mp (show List.Forall _ NL_j from ⟨KL_j_7, KL_j_13, KL_j_14, KL_j_19, KL_j_21, KL_j_22, KL_j_25, KL_j_26, KL_j_28, KL_j_30, KL_j_35, KL_j_37, KL_j_38, KL_j_41, KL_j_44, KL_j_49, KL_j_50, KL_j_51, KL_j_52, KL_j_56, KL_j_67, KL_j_69, KL_j_70, KL_j_74, KL_j_75, KL_j_81, KL_j_82, KL_j_85, KL_j_88, KL_j_98, KL_j_100, KL_j_102, KL_j_120, KL_j_131, KL_j_133, KL_j_134, KL_j_137, KL_j_138, KL_j_140, KL_j_145, KL_j_152, KL_j_164, KL_j_168, KL_j_176, KL_j_191, KL_j_193, KL_j_194, KL_j_196, KL_j_200, KL_j_224, KL_j_239, KL_j_247, KL_j_251, KL_j_253, KL_j_254, KL_j_259, KL_j_261, KL_j_262, KL_j_268, KL_j_273, KL_j_274, KL_j_276, KL_j_280, KL_j_290, KL_j_292, KL_j_296, KL_j_304, KL_j_319, KL_j_321, KL_j_322, KL_j_324, KL_j_328, KL_j_351, KL_j_352, KL_j_367, KL_j_375, KL_j_379, KL_j_381, KL_j_382, KL_j_385, KL_j_386, KL_j_388, KL_j_392, KL_j_415, KL_j_416, KL_j_431, KL_j_443, KL_j_445, KL_j_446, KL_j_448, KL_j_463, KL_j_471, KL_j_475, KL_j_477, KL_j_478, KL_j_491, KL_j_493, KL_j_499, KL_j_501, KL_j_502, KL_j_505, KL_j_506, KL_j_508⟩)
  intro l hl; rcases Kemp_j l hl with h | h
  · exact Or.inl h
  · exact Or.inr (hall l h)

theorem KE2_j : ∀ l < 512, planeAll LT_j T_jk l = true := by
  have hall : ∀ l ∈ NL_j, planeAll LT_j T_jk l = true :=
    List.forall_iff_forall_mem.mp (show List.Forall _ NL_j from ⟨KP_j_7, KP_j_13, KP_j_14, KP_j_19, KP_j_21, KP_j_22, KP_j_25, KP_j_26, KP_j_28, KP_j_30, KP_j_35, KP_j_37, KP_j_38, KP_j_41, KP_j_44, KP_j_49, KP_j_50, KP_j_51, KP_j_52, KP_j_56, KP_j_67, KP_j_69, KP_j_70, KP_j_74, KP_j_75, KP_j_81, KP_j_82, KP_j_85, KP_j_88, KP_j_98, KP_j_100, KP_j_102, KP_j_120, KP_j_131, KP_j_133, KP_j_134, KP_j_137, KP_j_138, KP_j_140, KP_j_145, KP_j_152, KP_j_164, KP_j_168, KP_j_176, KP_j_191, KP_j_193, KP_j_194, KP_j_196, KP_j_200, KP_j_224, KP_j_239, KP_j_247, KP_j_251, KP_j_253, KP_j_254, KP_j_259, KP_j_261, KP_j_262, KP_j_268, KP_j_273, KP_j_274, KP_j_276, KP_j_280, KP_j_290, KP_j_292, KP_j_296, KP_j_304, KP_j_319, KP_j_321, KP_j_322, KP_j_324, KP_j_328, KP_j_351, KP_j_352, KP_j_367, KP_j_375, KP_j_379, KP_j_381, KP_j_382, KP_j_385, KP_j_386, KP_j_388, KP_j_392, KP_j_415, KP_j_416, KP_j_431, KP_j_443, KP_j_445, KP_j_446, KP_j_448, KP_j_463, KP_j_471, KP_j_475, KP_j_477, KP_j_478, KP_j_491, KP_j_493, KP_j_499, KP_j_501, KP_j_502, KP_j_505, KP_j_506, KP_j_508⟩)
  intro l hl; rcases Kemp_j l hl with h | h
  · exact planeAll_of_empty h
  · exact hall l h

theorem KFall_j : ∀ h < 512, 0 < h → hypOK NS_j T_jk (TD_j.getD (h - 1) 0) h = true := by
  have hall : ∀ h ∈ HL_j, hypOK NS_j T_jk (TD_j.getD (h - 1) 0) h = true :=
    List.forall_iff_forall_mem.mp (show List.Forall _ HL_j from ⟨KF_j_1, KF_j_2, KF_j_3, KF_j_4, KF_j_5, KF_j_6, KF_j_7, KF_j_8, KF_j_9, KF_j_10, KF_j_11, KF_j_12, KF_j_13, KF_j_14, KF_j_15, KF_j_16, KF_j_17, KF_j_18, KF_j_19, KF_j_20, KF_j_21, KF_j_22, KF_j_23, KF_j_24, KF_j_25, KF_j_26, KF_j_27, KF_j_28, KF_j_29, KF_j_30, KF_j_31, KF_j_32, KF_j_33, KF_j_34, KF_j_35, KF_j_36, KF_j_37, KF_j_38, KF_j_39, KF_j_40, KF_j_41, KF_j_42, KF_j_43, KF_j_44, KF_j_45, KF_j_46, KF_j_47, KF_j_48, KF_j_49, KF_j_50, KF_j_51, KF_j_52, KF_j_53, KF_j_54, KF_j_55, KF_j_56, KF_j_57, KF_j_58, KF_j_59, KF_j_60, KF_j_61, KF_j_62, KF_j_63, KF_j_64, KF_j_65, KF_j_66, KF_j_67, KF_j_68, KF_j_69, KF_j_70, KF_j_71, KF_j_72, KF_j_73, KF_j_74, KF_j_75, KF_j_76, KF_j_77, KF_j_78, KF_j_79, KF_j_80, KF_j_81, KF_j_82, KF_j_83, KF_j_84, KF_j_85, KF_j_86, KF_j_87, KF_j_88, KF_j_89, KF_j_90, KF_j_91, KF_j_92, KF_j_93, KF_j_94, KF_j_95, KF_j_96, KF_j_97, KF_j_98, KF_j_99, KF_j_100, KF_j_101, KF_j_102, KF_j_103, KF_j_104, KF_j_105, KF_j_106, KF_j_107, KF_j_108, KF_j_109, KF_j_110, KF_j_111, KF_j_112, KF_j_113, KF_j_114, KF_j_115, KF_j_116, KF_j_117, KF_j_118, KF_j_119, KF_j_120, KF_j_121, KF_j_122, KF_j_123, KF_j_124, KF_j_125, KF_j_126, KF_j_127, KF_j_128, KF_j_129, KF_j_130, KF_j_131, KF_j_132, KF_j_133, KF_j_134, KF_j_135, KF_j_136, KF_j_137, KF_j_138, KF_j_139, KF_j_140, KF_j_141, KF_j_142, KF_j_143, KF_j_144, KF_j_145, KF_j_146, KF_j_147, KF_j_148, KF_j_149, KF_j_150, KF_j_151, KF_j_152, KF_j_153, KF_j_154, KF_j_155, KF_j_156, KF_j_157, KF_j_158, KF_j_159, KF_j_160, KF_j_161, KF_j_162, KF_j_163, KF_j_164, KF_j_165, KF_j_166, KF_j_167, KF_j_168, KF_j_169, KF_j_170, KF_j_171, KF_j_172, KF_j_173, KF_j_174, KF_j_175, KF_j_176, KF_j_177, KF_j_178, KF_j_179, KF_j_180, KF_j_181, KF_j_182, KF_j_183, KF_j_184, KF_j_185, KF_j_186, KF_j_187, KF_j_188, KF_j_189, KF_j_190, KF_j_191, KF_j_192, KF_j_193, KF_j_194, KF_j_195, KF_j_196, KF_j_197, KF_j_198, KF_j_199, KF_j_200, KF_j_201, KF_j_202, KF_j_203, KF_j_204, KF_j_205, KF_j_206, KF_j_207, KF_j_208, KF_j_209, KF_j_210, KF_j_211, KF_j_212, KF_j_213, KF_j_214, KF_j_215, KF_j_216, KF_j_217, KF_j_218, KF_j_219, KF_j_220, KF_j_221, KF_j_222, KF_j_223, KF_j_224, KF_j_225, KF_j_226, KF_j_227, KF_j_228, KF_j_229, KF_j_230, KF_j_231, KF_j_232, KF_j_233, KF_j_234, KF_j_235, KF_j_236, KF_j_237, KF_j_238, KF_j_239, KF_j_240, KF_j_241, KF_j_242, KF_j_243, KF_j_244, KF_j_245, KF_j_246, KF_j_247, KF_j_248, KF_j_249, KF_j_250, KF_j_251, KF_j_252, KF_j_253, KF_j_254, KF_j_255, KF_j_256, KF_j_257, KF_j_258, KF_j_259, KF_j_260, KF_j_261, KF_j_262, KF_j_263, KF_j_264, KF_j_265, KF_j_266, KF_j_267, KF_j_268, KF_j_269, KF_j_270, KF_j_271, KF_j_272, KF_j_273, KF_j_274, KF_j_275, KF_j_276, KF_j_277, KF_j_278, KF_j_279, KF_j_280, KF_j_281, KF_j_282, KF_j_283, KF_j_284, KF_j_285, KF_j_286, KF_j_287, KF_j_288, KF_j_289, KF_j_290, KF_j_291, KF_j_292, KF_j_293, KF_j_294, KF_j_295, KF_j_296, KF_j_297, KF_j_298, KF_j_299, KF_j_300, KF_j_301, KF_j_302, KF_j_303, KF_j_304, KF_j_305, KF_j_306, KF_j_307, KF_j_308, KF_j_309, KF_j_310, KF_j_311, KF_j_312, KF_j_313, KF_j_314, KF_j_315, KF_j_316, KF_j_317, KF_j_318, KF_j_319, KF_j_320, KF_j_321, KF_j_322, KF_j_323, KF_j_324, KF_j_325, KF_j_326, KF_j_327, KF_j_328, KF_j_329, KF_j_330, KF_j_331, KF_j_332, KF_j_333, KF_j_334, KF_j_335, KF_j_336, KF_j_337, KF_j_338, KF_j_339, KF_j_340, KF_j_341, KF_j_342, KF_j_343, KF_j_344, KF_j_345, KF_j_346, KF_j_347, KF_j_348, KF_j_349, KF_j_350, KF_j_351, KF_j_352, KF_j_353, KF_j_354, KF_j_355, KF_j_356, KF_j_357, KF_j_358, KF_j_359, KF_j_360, KF_j_361, KF_j_362, KF_j_363, KF_j_364, KF_j_365, KF_j_366, KF_j_367, KF_j_368, KF_j_369, KF_j_370, KF_j_371, KF_j_372, KF_j_373, KF_j_374, KF_j_375, KF_j_376, KF_j_377, KF_j_378, KF_j_379, KF_j_380, KF_j_381, KF_j_382, KF_j_383, KF_j_384, KF_j_385, KF_j_386, KF_j_387, KF_j_388, KF_j_389, KF_j_390, KF_j_391, KF_j_392, KF_j_393, KF_j_394, KF_j_395, KF_j_396, KF_j_397, KF_j_398, KF_j_399, KF_j_400, KF_j_401, KF_j_402, KF_j_403, KF_j_404, KF_j_405, KF_j_406, KF_j_407, KF_j_408, KF_j_409, KF_j_410, KF_j_411, KF_j_412, KF_j_413, KF_j_414, KF_j_415, KF_j_416, KF_j_417, KF_j_418, KF_j_419, KF_j_420, KF_j_421, KF_j_422, KF_j_423, KF_j_424, KF_j_425, KF_j_426, KF_j_427, KF_j_428, KF_j_429, KF_j_430, KF_j_431, KF_j_432, KF_j_433, KF_j_434, KF_j_435, KF_j_436, KF_j_437, KF_j_438, KF_j_439, KF_j_440, KF_j_441, KF_j_442, KF_j_443, KF_j_444, KF_j_445, KF_j_446, KF_j_447, KF_j_448, KF_j_449, KF_j_450, KF_j_451, KF_j_452, KF_j_453, KF_j_454, KF_j_455, KF_j_456, KF_j_457, KF_j_458, KF_j_459, KF_j_460, KF_j_461, KF_j_462, KF_j_463, KF_j_464, KF_j_465, KF_j_466, KF_j_467, KF_j_468, KF_j_469, KF_j_470, KF_j_471, KF_j_472, KF_j_473, KF_j_474, KF_j_475, KF_j_476, KF_j_477, KF_j_478, KF_j_479, KF_j_480, KF_j_481, KF_j_482, KF_j_483, KF_j_484, KF_j_485, KF_j_486, KF_j_487, KF_j_488, KF_j_489, KF_j_490, KF_j_491, KF_j_492, KF_j_493, KF_j_494, KF_j_495, KF_j_496, KF_j_497, KF_j_498, KF_j_499, KF_j_500, KF_j_501, KF_j_502, KF_j_503, KF_j_504, KF_j_505, KF_j_506, KF_j_507, KF_j_508, KF_j_509, KF_j_510, KF_j_511⟩)
  intro h hh h0; exact hall h (Khl_j h hh h0)

/-- **V2-FLOOR, joint (JB), kernel-only**: every plan E (strict containments between subspaces of F₂⁹, dims 1..8
priced by w_θ, θ = (79793 / 1048576 : ℝ)) that realises every pair of the reference list (pairs.txt, as in V2FloorData) costs at least
987754236107 / 2^30 = 919.917818. -/
theorem v2floor_joint_kernel (E : Finset (Sub × Sub)) (hE : ∀ e ∈ E, e.1 < e.2)
    (hreal : ∀ p : Fin N_joint, Reach E (Lsub (LBj p)) (Usub (UHj p))) :
    (987754236107 : ℝ) / 2 ^ 30 ≤ ∑ e ∈ E, wcut (79793 / 1048576 : ℝ) (fdim e.1) (fdim e.2) := by
  have h := kernel_floor (TD := TD_j) (79793 / 1048576 : ℝ) KnsOK_j KltOK_j KcomplOK_j KE1_j KE2_j KFall_j T_jk_le E hE
    (fun p => by
      obtain ⟨i, hi, h1, h2⟩ := link_of KlinkOK_j p
      rw [h1, h2]; exact hreal ⟨i, hi⟩)
  rwa [Ktot_j] at h

end V2Floor

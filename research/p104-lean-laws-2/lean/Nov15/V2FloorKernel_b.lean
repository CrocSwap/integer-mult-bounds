/-
V2FloorKernel_b (lane LEAN-KERNEL, Nov 16): the beta V2-FLOOR bound for #7623's relaxed JB model, KERNEL-ONLY
(decide +kernel throughout; no native_decide / ofReduceBool / implemented_by; sorry-free). See V2FloorKernel.md.
-/
import Nov15.V2FloorKernelBase_b
import Nov15.V2FloorKernelBase1_b
import Nov15.V2FloorKernelBase2_b
import Nov15.V2FloorKernelBase3_b
import Nov15.V2FloorKernelBase4_b
import Nov15.V2FloorKernelBase5_b
import Nov15.V2FloorKernelBase6_b
import Nov15.V2FloorKernelBaseA_b
import Nov15.V2FloorKernelE_b_13_a
import Nov15.V2FloorKernelE_b_13_b
import Nov15.V2FloorKernelE_b_14_a
import Nov15.V2FloorKernelE_b_14_b
import Nov15.V2FloorKernelE_b_19_a
import Nov15.V2FloorKernelE_b_19_b
import Nov15.V2FloorKernelE_b_22_a
import Nov15.V2FloorKernelE_b_22_b
import Nov15.V2FloorKernelE_b_26_a
import Nov15.V2FloorKernelE_b_26_b
import Nov15.V2FloorKernelE_b_28_a
import Nov15.V2FloorKernelE_b_28_b
import Nov15.V2FloorKernelE_b_30_a
import Nov15.V2FloorKernelE_b_30_b
import Nov15.V2FloorKernelE_b_35_a
import Nov15.V2FloorKernelE_b_35_b
import Nov15.V2FloorKernelE_b_37_a
import Nov15.V2FloorKernelE_b_37_b
import Nov15.V2FloorKernelE_b_38_a
import Nov15.V2FloorKernelE_b_38_b
import Nov15.V2FloorKernelE_b_41_a
import Nov15.V2FloorKernelE_b_41_b
import Nov15.V2FloorKernelE_b_44_a
import Nov15.V2FloorKernelE_b_44_b
import Nov15.V2FloorKernelE_b_49_a
import Nov15.V2FloorKernelE_b_49_b
import Nov15.V2FloorKernelE_b_50_a
import Nov15.V2FloorKernelE_b_50_b
import Nov15.V2FloorKernelE_b_51_a
import Nov15.V2FloorKernelE_b_51_b
import Nov15.V2FloorKernelE_b_52_a
import Nov15.V2FloorKernelE_b_52_b
import Nov15.V2FloorKernelE_b_56_a
import Nov15.V2FloorKernelE_b_56_b
import Nov15.V2FloorKernelE_b_69_a
import Nov15.V2FloorKernelE_b_69_b
import Nov15.V2FloorKernelE_b_70_a
import Nov15.V2FloorKernelE_b_70_b
import Nov15.V2FloorKernelE_b_74_a
import Nov15.V2FloorKernelE_b_74_b
import Nov15.V2FloorKernelE_b_75_a
import Nov15.V2FloorKernelE_b_75_b
import Nov15.V2FloorKernelE_b_81_a
import Nov15.V2FloorKernelE_b_81_b
import Nov15.V2FloorKernelE_b_85_a
import Nov15.V2FloorKernelE_b_85_b
import Nov15.V2FloorKernelE_b_88_a
import Nov15.V2FloorKernelE_b_88_b
import Nov15.V2FloorKernelE_b_98_a
import Nov15.V2FloorKernelE_b_98_b
import Nov15.V2FloorKernelE_b_100_a
import Nov15.V2FloorKernelE_b_100_b
import Nov15.V2FloorKernelE_b_102_a
import Nov15.V2FloorKernelE_b_102_b
import Nov15.V2FloorKernelE_b_120_a
import Nov15.V2FloorKernelE_b_120_b
import Nov15.V2FloorKernelE_b_131_a
import Nov15.V2FloorKernelE_b_131_b
import Nov15.V2FloorKernelE_b_133_a
import Nov15.V2FloorKernelE_b_133_b
import Nov15.V2FloorKernelE_b_134_a
import Nov15.V2FloorKernelE_b_134_b
import Nov15.V2FloorKernelE_b_138_a
import Nov15.V2FloorKernelE_b_138_b
import Nov15.V2FloorKernelE_b_145_a
import Nov15.V2FloorKernelE_b_145_b
import Nov15.V2FloorKernelE_b_152_a
import Nov15.V2FloorKernelE_b_152_b
import Nov15.V2FloorKernelE_b_164_a
import Nov15.V2FloorKernelE_b_164_b
import Nov15.V2FloorKernelE_b_168_a
import Nov15.V2FloorKernelE_b_168_b
import Nov15.V2FloorKernelE_b_176_a
import Nov15.V2FloorKernelE_b_176_b
import Nov15.V2FloorKernelE_b_191_a
import Nov15.V2FloorKernelE_b_191_b
import Nov15.V2FloorKernelE_b_193_a
import Nov15.V2FloorKernelE_b_193_b
import Nov15.V2FloorKernelE_b_194_a
import Nov15.V2FloorKernelE_b_194_b
import Nov15.V2FloorKernelE_b_196_a
import Nov15.V2FloorKernelE_b_196_b
import Nov15.V2FloorKernelE_b_200_a
import Nov15.V2FloorKernelE_b_200_b
import Nov15.V2FloorKernelE_b_224_a
import Nov15.V2FloorKernelE_b_224_b
import Nov15.V2FloorKernelE_b_239_a
import Nov15.V2FloorKernelE_b_239_b
import Nov15.V2FloorKernelE_b_247_a
import Nov15.V2FloorKernelE_b_247_b
import Nov15.V2FloorKernelE_b_251_a
import Nov15.V2FloorKernelE_b_251_b
import Nov15.V2FloorKernelE_b_253_a
import Nov15.V2FloorKernelE_b_253_b
import Nov15.V2FloorKernelE_b_254_a
import Nov15.V2FloorKernelE_b_254_b
import Nov15.V2FloorKernelE_b_259_a
import Nov15.V2FloorKernelE_b_259_b
import Nov15.V2FloorKernelE_b_261_a
import Nov15.V2FloorKernelE_b_261_b
import Nov15.V2FloorKernelE_b_262_a
import Nov15.V2FloorKernelE_b_262_b
import Nov15.V2FloorKernelE_b_268_a
import Nov15.V2FloorKernelE_b_268_b
import Nov15.V2FloorKernelE_b_273_a
import Nov15.V2FloorKernelE_b_273_b
import Nov15.V2FloorKernelE_b_274_a
import Nov15.V2FloorKernelE_b_274_b
import Nov15.V2FloorKernelE_b_276_a
import Nov15.V2FloorKernelE_b_276_b
import Nov15.V2FloorKernelE_b_280_a
import Nov15.V2FloorKernelE_b_280_b
import Nov15.V2FloorKernelE_b_290_a
import Nov15.V2FloorKernelE_b_290_b
import Nov15.V2FloorKernelE_b_292_a
import Nov15.V2FloorKernelE_b_292_b
import Nov15.V2FloorKernelE_b_296_a
import Nov15.V2FloorKernelE_b_296_b
import Nov15.V2FloorKernelE_b_304_a
import Nov15.V2FloorKernelE_b_304_b
import Nov15.V2FloorKernelE_b_321_a
import Nov15.V2FloorKernelE_b_321_b
import Nov15.V2FloorKernelE_b_322_a
import Nov15.V2FloorKernelE_b_322_b
import Nov15.V2FloorKernelE_b_324_a
import Nov15.V2FloorKernelE_b_324_b
import Nov15.V2FloorKernelE_b_328_a
import Nov15.V2FloorKernelE_b_328_b
import Nov15.V2FloorKernelE_b_351_a
import Nov15.V2FloorKernelE_b_351_b
import Nov15.V2FloorKernelE_b_352_a
import Nov15.V2FloorKernelE_b_352_b
import Nov15.V2FloorKernelE_b_367_a
import Nov15.V2FloorKernelE_b_367_b
import Nov15.V2FloorKernelE_b_375_a
import Nov15.V2FloorKernelE_b_375_b
import Nov15.V2FloorKernelE_b_379_a
import Nov15.V2FloorKernelE_b_379_b
import Nov15.V2FloorKernelE_b_381_a
import Nov15.V2FloorKernelE_b_381_b
import Nov15.V2FloorKernelE_b_382_a
import Nov15.V2FloorKernelE_b_382_b
import Nov15.V2FloorKernelE_b_385_a
import Nov15.V2FloorKernelE_b_385_b
import Nov15.V2FloorKernelE_b_386_a
import Nov15.V2FloorKernelE_b_386_b
import Nov15.V2FloorKernelE_b_388_a
import Nov15.V2FloorKernelE_b_388_b
import Nov15.V2FloorKernelE_b_392_a
import Nov15.V2FloorKernelE_b_392_b
import Nov15.V2FloorKernelE_b_415_a
import Nov15.V2FloorKernelE_b_415_b
import Nov15.V2FloorKernelE_b_416_a
import Nov15.V2FloorKernelE_b_416_b
import Nov15.V2FloorKernelE_b_431_a
import Nov15.V2FloorKernelE_b_431_b
import Nov15.V2FloorKernelE_b_443_a
import Nov15.V2FloorKernelE_b_443_b
import Nov15.V2FloorKernelE_b_445_a
import Nov15.V2FloorKernelE_b_445_b
import Nov15.V2FloorKernelE_b_446_a
import Nov15.V2FloorKernelE_b_446_b
import Nov15.V2FloorKernelE_b_463_a
import Nov15.V2FloorKernelE_b_463_b
import Nov15.V2FloorKernelE_b_471_a
import Nov15.V2FloorKernelE_b_471_b
import Nov15.V2FloorKernelE_b_475_a
import Nov15.V2FloorKernelE_b_475_b
import Nov15.V2FloorKernelE_b_477_a
import Nov15.V2FloorKernelE_b_477_b
import Nov15.V2FloorKernelE_b_491_a
import Nov15.V2FloorKernelE_b_491_b
import Nov15.V2FloorKernelE_b_493_a
import Nov15.V2FloorKernelE_b_493_b
import Nov15.V2FloorKernelE_b_499_a
import Nov15.V2FloorKernelE_b_499_b
import Nov15.V2FloorKernelE_b_501_a
import Nov15.V2FloorKernelE_b_501_b
import Nov15.V2FloorKernelE_b_502_a
import Nov15.V2FloorKernelE_b_502_b
import Nov15.V2FloorKernelE_b_505_a
import Nov15.V2FloorKernelE_b_505_b
import Nov15.V2FloorKernelE_b_506_a
import Nov15.V2FloorKernelE_b_506_b
import Nov15.V2FloorKernelE_b_508_a
import Nov15.V2FloorKernelE_b_508_b
import Nov15.V2FloorKernelF_b_1
import Nov15.V2FloorKernelF_b_9
import Nov15.V2FloorKernelF_b_17
import Nov15.V2FloorKernelF_b_25
import Nov15.V2FloorKernelF_b_33
import Nov15.V2FloorKernelF_b_41
import Nov15.V2FloorKernelF_b_49
import Nov15.V2FloorKernelF_b_57
import Nov15.V2FloorKernelF_b_65
import Nov15.V2FloorKernelF_b_73
import Nov15.V2FloorKernelF_b_81
import Nov15.V2FloorKernelF_b_89
import Nov15.V2FloorKernelF_b_97
import Nov15.V2FloorKernelF_b_105
import Nov15.V2FloorKernelF_b_113
import Nov15.V2FloorKernelF_b_121
import Nov15.V2FloorKernelF_b_129
import Nov15.V2FloorKernelF_b_137
import Nov15.V2FloorKernelF_b_145
import Nov15.V2FloorKernelF_b_153
import Nov15.V2FloorKernelF_b_161
import Nov15.V2FloorKernelF_b_169
import Nov15.V2FloorKernelF_b_177
import Nov15.V2FloorKernelF_b_185
import Nov15.V2FloorKernelF_b_193
import Nov15.V2FloorKernelF_b_201
import Nov15.V2FloorKernelF_b_209
import Nov15.V2FloorKernelF_b_217
import Nov15.V2FloorKernelF_b_225
import Nov15.V2FloorKernelF_b_233
import Nov15.V2FloorKernelF_b_241
import Nov15.V2FloorKernelF_b_249
import Nov15.V2FloorKernelF_b_257
import Nov15.V2FloorKernelF_b_265
import Nov15.V2FloorKernelF_b_273
import Nov15.V2FloorKernelF_b_281
import Nov15.V2FloorKernelF_b_289
import Nov15.V2FloorKernelF_b_297
import Nov15.V2FloorKernelF_b_305
import Nov15.V2FloorKernelF_b_313
import Nov15.V2FloorKernelF_b_321
import Nov15.V2FloorKernelF_b_329
import Nov15.V2FloorKernelF_b_337
import Nov15.V2FloorKernelF_b_345
import Nov15.V2FloorKernelF_b_353
import Nov15.V2FloorKernelF_b_361
import Nov15.V2FloorKernelF_b_369
import Nov15.V2FloorKernelF_b_377
import Nov15.V2FloorKernelF_b_385
import Nov15.V2FloorKernelF_b_393
import Nov15.V2FloorKernelF_b_401
import Nov15.V2FloorKernelF_b_409
import Nov15.V2FloorKernelF_b_417
import Nov15.V2FloorKernelF_b_425
import Nov15.V2FloorKernelF_b_433
import Nov15.V2FloorKernelF_b_441
import Nov15.V2FloorKernelF_b_449
import Nov15.V2FloorKernelF_b_457
import Nov15.V2FloorKernelF_b_465
import Nov15.V2FloorKernelF_b_473
import Nov15.V2FloorKernelF_b_481
import Nov15.V2FloorKernelF_b_489
import Nov15.V2FloorKernelF_b_497
import Nov15.V2FloorKernelF_b_505
import Nov15.V2FloorKernelCost
import Nov15.V2FloorDefs_b
set_option maxRecDepth 100000
set_option maxHeartbeats 0
namespace V2Floor

theorem KE1_b : ∀ l < 512, (LT_b.get 9 l).isEmpty = true ∨ lineOK LT_b T_bk l = true := by
  have hall : ∀ l ∈ NL_b, lineOK LT_b T_bk l = true :=
    List.forall_iff_forall_mem.mp (show List.Forall _ NL_b from ⟨KL_b_13, KL_b_14, KL_b_19, KL_b_22, KL_b_26, KL_b_28, KL_b_30, KL_b_35, KL_b_37, KL_b_38, KL_b_41, KL_b_44, KL_b_49, KL_b_50, KL_b_51, KL_b_52, KL_b_56, KL_b_69, KL_b_70, KL_b_74, KL_b_75, KL_b_81, KL_b_85, KL_b_88, KL_b_98, KL_b_100, KL_b_102, KL_b_120, KL_b_131, KL_b_133, KL_b_134, KL_b_138, KL_b_145, KL_b_152, KL_b_164, KL_b_168, KL_b_176, KL_b_191, KL_b_193, KL_b_194, KL_b_196, KL_b_200, KL_b_224, KL_b_239, KL_b_247, KL_b_251, KL_b_253, KL_b_254, KL_b_259, KL_b_261, KL_b_262, KL_b_268, KL_b_273, KL_b_274, KL_b_276, KL_b_280, KL_b_290, KL_b_292, KL_b_296, KL_b_304, KL_b_321, KL_b_322, KL_b_324, KL_b_328, KL_b_351, KL_b_352, KL_b_367, KL_b_375, KL_b_379, KL_b_381, KL_b_382, KL_b_385, KL_b_386, KL_b_388, KL_b_392, KL_b_415, KL_b_416, KL_b_431, KL_b_443, KL_b_445, KL_b_446, KL_b_463, KL_b_471, KL_b_475, KL_b_477, KL_b_491, KL_b_493, KL_b_499, KL_b_501, KL_b_502, KL_b_505, KL_b_506, KL_b_508⟩)
  intro l hl; rcases Kemp_b l hl with h | h
  · exact Or.inl h
  · exact Or.inr (hall l h)

theorem KE2_b : ∀ l < 512, planeAll LT_b T_bk l = true := by
  have hall : ∀ l ∈ NL_b, planeAll LT_b T_bk l = true :=
    List.forall_iff_forall_mem.mp (show List.Forall _ NL_b from ⟨KP_b_13, KP_b_14, KP_b_19, KP_b_22, KP_b_26, KP_b_28, KP_b_30, KP_b_35, KP_b_37, KP_b_38, KP_b_41, KP_b_44, KP_b_49, KP_b_50, KP_b_51, KP_b_52, KP_b_56, KP_b_69, KP_b_70, KP_b_74, KP_b_75, KP_b_81, KP_b_85, KP_b_88, KP_b_98, KP_b_100, KP_b_102, KP_b_120, KP_b_131, KP_b_133, KP_b_134, KP_b_138, KP_b_145, KP_b_152, KP_b_164, KP_b_168, KP_b_176, KP_b_191, KP_b_193, KP_b_194, KP_b_196, KP_b_200, KP_b_224, KP_b_239, KP_b_247, KP_b_251, KP_b_253, KP_b_254, KP_b_259, KP_b_261, KP_b_262, KP_b_268, KP_b_273, KP_b_274, KP_b_276, KP_b_280, KP_b_290, KP_b_292, KP_b_296, KP_b_304, KP_b_321, KP_b_322, KP_b_324, KP_b_328, KP_b_351, KP_b_352, KP_b_367, KP_b_375, KP_b_379, KP_b_381, KP_b_382, KP_b_385, KP_b_386, KP_b_388, KP_b_392, KP_b_415, KP_b_416, KP_b_431, KP_b_443, KP_b_445, KP_b_446, KP_b_463, KP_b_471, KP_b_475, KP_b_477, KP_b_491, KP_b_493, KP_b_499, KP_b_501, KP_b_502, KP_b_505, KP_b_506, KP_b_508⟩)
  intro l hl; rcases Kemp_b l hl with h | h
  · exact planeAll_of_empty h
  · exact hall l h

theorem KFall_b : ∀ h < 512, 0 < h → hypOK NS_b T_bk (TD_b.getD (h - 1) 0) h = true := by
  have hall : ∀ h ∈ HL_b, hypOK NS_b T_bk (TD_b.getD (h - 1) 0) h = true :=
    List.forall_iff_forall_mem.mp (show List.Forall _ HL_b from ⟨KF_b_1, KF_b_2, KF_b_3, KF_b_4, KF_b_5, KF_b_6, KF_b_7, KF_b_8, KF_b_9, KF_b_10, KF_b_11, KF_b_12, KF_b_13, KF_b_14, KF_b_15, KF_b_16, KF_b_17, KF_b_18, KF_b_19, KF_b_20, KF_b_21, KF_b_22, KF_b_23, KF_b_24, KF_b_25, KF_b_26, KF_b_27, KF_b_28, KF_b_29, KF_b_30, KF_b_31, KF_b_32, KF_b_33, KF_b_34, KF_b_35, KF_b_36, KF_b_37, KF_b_38, KF_b_39, KF_b_40, KF_b_41, KF_b_42, KF_b_43, KF_b_44, KF_b_45, KF_b_46, KF_b_47, KF_b_48, KF_b_49, KF_b_50, KF_b_51, KF_b_52, KF_b_53, KF_b_54, KF_b_55, KF_b_56, KF_b_57, KF_b_58, KF_b_59, KF_b_60, KF_b_61, KF_b_62, KF_b_63, KF_b_64, KF_b_65, KF_b_66, KF_b_67, KF_b_68, KF_b_69, KF_b_70, KF_b_71, KF_b_72, KF_b_73, KF_b_74, KF_b_75, KF_b_76, KF_b_77, KF_b_78, KF_b_79, KF_b_80, KF_b_81, KF_b_82, KF_b_83, KF_b_84, KF_b_85, KF_b_86, KF_b_87, KF_b_88, KF_b_89, KF_b_90, KF_b_91, KF_b_92, KF_b_93, KF_b_94, KF_b_95, KF_b_96, KF_b_97, KF_b_98, KF_b_99, KF_b_100, KF_b_101, KF_b_102, KF_b_103, KF_b_104, KF_b_105, KF_b_106, KF_b_107, KF_b_108, KF_b_109, KF_b_110, KF_b_111, KF_b_112, KF_b_113, KF_b_114, KF_b_115, KF_b_116, KF_b_117, KF_b_118, KF_b_119, KF_b_120, KF_b_121, KF_b_122, KF_b_123, KF_b_124, KF_b_125, KF_b_126, KF_b_127, KF_b_128, KF_b_129, KF_b_130, KF_b_131, KF_b_132, KF_b_133, KF_b_134, KF_b_135, KF_b_136, KF_b_137, KF_b_138, KF_b_139, KF_b_140, KF_b_141, KF_b_142, KF_b_143, KF_b_144, KF_b_145, KF_b_146, KF_b_147, KF_b_148, KF_b_149, KF_b_150, KF_b_151, KF_b_152, KF_b_153, KF_b_154, KF_b_155, KF_b_156, KF_b_157, KF_b_158, KF_b_159, KF_b_160, KF_b_161, KF_b_162, KF_b_163, KF_b_164, KF_b_165, KF_b_166, KF_b_167, KF_b_168, KF_b_169, KF_b_170, KF_b_171, KF_b_172, KF_b_173, KF_b_174, KF_b_175, KF_b_176, KF_b_177, KF_b_178, KF_b_179, KF_b_180, KF_b_181, KF_b_182, KF_b_183, KF_b_184, KF_b_185, KF_b_186, KF_b_187, KF_b_188, KF_b_189, KF_b_190, KF_b_191, KF_b_192, KF_b_193, KF_b_194, KF_b_195, KF_b_196, KF_b_197, KF_b_198, KF_b_199, KF_b_200, KF_b_201, KF_b_202, KF_b_203, KF_b_204, KF_b_205, KF_b_206, KF_b_207, KF_b_208, KF_b_209, KF_b_210, KF_b_211, KF_b_212, KF_b_213, KF_b_214, KF_b_215, KF_b_216, KF_b_217, KF_b_218, KF_b_219, KF_b_220, KF_b_221, KF_b_222, KF_b_223, KF_b_224, KF_b_225, KF_b_226, KF_b_227, KF_b_228, KF_b_229, KF_b_230, KF_b_231, KF_b_232, KF_b_233, KF_b_234, KF_b_235, KF_b_236, KF_b_237, KF_b_238, KF_b_239, KF_b_240, KF_b_241, KF_b_242, KF_b_243, KF_b_244, KF_b_245, KF_b_246, KF_b_247, KF_b_248, KF_b_249, KF_b_250, KF_b_251, KF_b_252, KF_b_253, KF_b_254, KF_b_255, KF_b_256, KF_b_257, KF_b_258, KF_b_259, KF_b_260, KF_b_261, KF_b_262, KF_b_263, KF_b_264, KF_b_265, KF_b_266, KF_b_267, KF_b_268, KF_b_269, KF_b_270, KF_b_271, KF_b_272, KF_b_273, KF_b_274, KF_b_275, KF_b_276, KF_b_277, KF_b_278, KF_b_279, KF_b_280, KF_b_281, KF_b_282, KF_b_283, KF_b_284, KF_b_285, KF_b_286, KF_b_287, KF_b_288, KF_b_289, KF_b_290, KF_b_291, KF_b_292, KF_b_293, KF_b_294, KF_b_295, KF_b_296, KF_b_297, KF_b_298, KF_b_299, KF_b_300, KF_b_301, KF_b_302, KF_b_303, KF_b_304, KF_b_305, KF_b_306, KF_b_307, KF_b_308, KF_b_309, KF_b_310, KF_b_311, KF_b_312, KF_b_313, KF_b_314, KF_b_315, KF_b_316, KF_b_317, KF_b_318, KF_b_319, KF_b_320, KF_b_321, KF_b_322, KF_b_323, KF_b_324, KF_b_325, KF_b_326, KF_b_327, KF_b_328, KF_b_329, KF_b_330, KF_b_331, KF_b_332, KF_b_333, KF_b_334, KF_b_335, KF_b_336, KF_b_337, KF_b_338, KF_b_339, KF_b_340, KF_b_341, KF_b_342, KF_b_343, KF_b_344, KF_b_345, KF_b_346, KF_b_347, KF_b_348, KF_b_349, KF_b_350, KF_b_351, KF_b_352, KF_b_353, KF_b_354, KF_b_355, KF_b_356, KF_b_357, KF_b_358, KF_b_359, KF_b_360, KF_b_361, KF_b_362, KF_b_363, KF_b_364, KF_b_365, KF_b_366, KF_b_367, KF_b_368, KF_b_369, KF_b_370, KF_b_371, KF_b_372, KF_b_373, KF_b_374, KF_b_375, KF_b_376, KF_b_377, KF_b_378, KF_b_379, KF_b_380, KF_b_381, KF_b_382, KF_b_383, KF_b_384, KF_b_385, KF_b_386, KF_b_387, KF_b_388, KF_b_389, KF_b_390, KF_b_391, KF_b_392, KF_b_393, KF_b_394, KF_b_395, KF_b_396, KF_b_397, KF_b_398, KF_b_399, KF_b_400, KF_b_401, KF_b_402, KF_b_403, KF_b_404, KF_b_405, KF_b_406, KF_b_407, KF_b_408, KF_b_409, KF_b_410, KF_b_411, KF_b_412, KF_b_413, KF_b_414, KF_b_415, KF_b_416, KF_b_417, KF_b_418, KF_b_419, KF_b_420, KF_b_421, KF_b_422, KF_b_423, KF_b_424, KF_b_425, KF_b_426, KF_b_427, KF_b_428, KF_b_429, KF_b_430, KF_b_431, KF_b_432, KF_b_433, KF_b_434, KF_b_435, KF_b_436, KF_b_437, KF_b_438, KF_b_439, KF_b_440, KF_b_441, KF_b_442, KF_b_443, KF_b_444, KF_b_445, KF_b_446, KF_b_447, KF_b_448, KF_b_449, KF_b_450, KF_b_451, KF_b_452, KF_b_453, KF_b_454, KF_b_455, KF_b_456, KF_b_457, KF_b_458, KF_b_459, KF_b_460, KF_b_461, KF_b_462, KF_b_463, KF_b_464, KF_b_465, KF_b_466, KF_b_467, KF_b_468, KF_b_469, KF_b_470, KF_b_471, KF_b_472, KF_b_473, KF_b_474, KF_b_475, KF_b_476, KF_b_477, KF_b_478, KF_b_479, KF_b_480, KF_b_481, KF_b_482, KF_b_483, KF_b_484, KF_b_485, KF_b_486, KF_b_487, KF_b_488, KF_b_489, KF_b_490, KF_b_491, KF_b_492, KF_b_493, KF_b_494, KF_b_495, KF_b_496, KF_b_497, KF_b_498, KF_b_499, KF_b_500, KF_b_501, KF_b_502, KF_b_503, KF_b_504, KF_b_505, KF_b_506, KF_b_507, KF_b_508, KF_b_509, KF_b_510, KF_b_511⟩)
  intro h hh h0; exact hall h (Khl_b h hh h0)

/-- **V2-FLOOR, beta (JB), kernel-only**: every plan E (strict containments between subspaces of F₂⁹, dims 1..8
priced by w_θ, θ = (1 : ℝ)) that realises every pair of the reference list (pairs.txt, as in V2FloorData) costs at least
941971821916 / 2^30 = 877.279622. -/
theorem v2floor_beta_kernel (E : Finset (Sub × Sub)) (hE : ∀ e ∈ E, e.1 < e.2)
    (hreal : ∀ p : Fin N_beta, Reach E (Lsub (LBb p)) (Usub (UHb p))) :
    (941971821916 : ℝ) / 2 ^ 30 ≤ ∑ e ∈ E, wcut (1 : ℝ) (fdim e.1) (fdim e.2) := by
  have h := kernel_floor (TD := TD_b) (1 : ℝ) KnsOK_b KltOK_b KcomplOK_b KE1_b KE2_b KFall_b T_bk_le E hE
    (fun p => by
      obtain ⟨i, hi, h1, h2⟩ := link_of KlinkOK_b p
      rw [h1, h2]; exact hreal ⟨i, hi⟩)
  rwa [Ktot_b] at h

end V2Floor

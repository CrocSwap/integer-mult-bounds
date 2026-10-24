import RowEvaluation
import LinearReplay
import TreeReplay
import FramedReplay
import CoordinateSwap
import AddressPairs
import EndpointInterpretation
import FrameDatumCore
import FrameCertificateBatch00
import FrameCertificateBatch01
import FrameCertificateBatch02
import FrameCertificateBatch03
import FrameCertificateBatch04
import FrameCertificateBatch05
import FrameCertificateBatch06
import FrameCertificateBatch07
import FrameCertificateBatch08
import FrameCertificateBatch09
import FrameCertificateBatch10
import FrameCertificateBatch11
import FrameCertificateBatch12
import FrameCertificateBatch13
import FrameCertificateBatch14
import FrameLookup
import FrameTransitionBatch00
import FrameTransitionBatch01
import FrameTransitionBatch02
import FrameTransitionBatch03
import FrameTransitionBatch04
import FrameTransitionBatch05
import FrameTransitionBatch06
import FrameTransitionBatch07
import FrameTransitionBatch08
import FrameTransitionBatch09
import FrameTransitionBatch10
import FrameTransitionBatch11
import FrameTransitionBatch12
import FrameTransitionBatch13
import FrameTransitionBatch14
import FrameTransitionBatch15
import FrameTransitionBatch16
import FrameTransitionBatch17
import FrameTransitionBatch18
import FrameTransitionBatch19
import FrameTransitionBatch20
import FrameTransitionBatch21
import FrameTransitionBatch22
import FrameTransitionBatch23
import FrameTransitionBatch24
import FrameTransitionBatch25
import FrameTransitionBatch26
import FrameData
import FrameGeometry
import FrameTraceCore
import FrameTraceNodes00
import FrameTraceNodes01
import FrameTraceNodes02
import FrameTraceNodes03
import FrameTraceNodes04
import FrameTraceNodes05
import FrameTraceNodes06
import FrameTraceNodes07
import FrameTraceNodes08
import FrameTraceNodes09
import FrameTraceNodes10
import FrameTraceNodes11
import FrameTraceNodes12
import FrameTraceNodes13
import FrameTraceNodes14
import FrameTraceNodes15
import FrameTraceNodes16
import FrameTraceLiterals
import FrameLabelData
import FrameMoveData
import MatrixNodes00
import MatrixNodes01
import MatrixNodes02
import MatrixNodes03
import MatrixNodes04
import MatrixNodes05
import MatrixNodes06
import MatrixNodes07
import MatrixNodes08
import MatrixNodes09
import MatrixNodes10
import MatrixNodes11
import MatrixNodes12
import MatrixNodes13
import MatrixNodes14
import MatrixNodes15
import MatrixNodes16
import MatrixNodes17
import MatrixNodes18
import MatrixNodes19
import MatrixNodes20
import MatrixNodes21
import MatrixData
import FrameTraceCheckpoints
import FrameTraceData
import PayloadGuards
import FrameTraceRefinement
import OwnerTransport
import FrameTraceRoutes
import OwnershipDatumCore
import OwnershipCertificatePermutations
import OwnershipCertificateMasks
import OwnershipInverseTable
import OwnershipCertificateOwner
import OwnershipCertificateHelpers
import OwnershipData
import FrameTraceTables
import HelperGeometryData
import MatrixCheckpoints
import MatrixCertificate
import SourceTables
import SourceEndpoint
import SourceFramed
import SourceRaw
import MultiHosting
import Ownership
import SourceConnection
import InvocationPayload
import PortData
import PortRowData
import PortGeometry
import OwnershipGeometry
import ParentOwnershipData
import ParentOwnership
import PhysicalSourceConnection
import SelectedGeometry
import SourceLayouts
import SourceInvocationState
import SourceCommonCover
import SourceControls
import SourceInvocationComparison
import SourceDataBehavior
import SourceInitialPayload
import SourceRawGuards
import SourceNativeInvocation
import SourceMoveGeometry
import SourceInvocation

#print axioms LinearReplay.evalRow_zero
#print axioms LinearReplay.evalRow_xor
#print axioms LinearReplay.evalRow_basis
#print axioms LinearReplay.evalRow_shift_basis
#print axioms LinearReplay.map_getD
#print axioms LinearReplay.step_map
#print axioms LinearReplay.run_map
#print axioms LinearReplay.evalRows_step
#print axioms LinearReplay.evalRows_run
#print axioms LinearReplay.checked_projection
#print axioms LinearReplay.evalRows_basisRows
#print axioms LinearReplay.evalRows_getD
#print axioms LinearReplay.checks_sound
#print axioms LinearReplay.checked_flag_mono
#print axioms LinearReplay.checked_guards_sound
#print axioms TreeReplay.Tree.map_get
#print axioms TreeReplay.Tree.map_put
#print axioms TreeReplay.Tree.map_map
#print axioms TreeReplay.Tree.map_tabulate
#print axioms TreeReplay.Tree.get_tabulate
#print axioms TreeReplay.Tree.full_tabulate
#print axioms TreeReplay.Tree.full_put
#print axioms TreeReplay.Tree.get_put
#print axioms TreeReplay.step_map
#print axioms TreeReplay.run_map
#print axioms TreeReplay.evalRows_step
#print axioms TreeReplay.evalRows_run
#print axioms TreeReplay.checked_projection
#print axioms TreeReplay.evalRows_get
#print axioms TreeReplay.checks_sound
#print axioms TreeReplay.checked_flag_mono
#print axioms TreeReplay.checked_guards_sound
#print axioms TreeReplay.evalRows_basisRows
#print axioms TreeReplay.dirtyInput_get
#print axioms TreeReplay.evalPayloadRows_run
#print axioms TreeReplay.evalPayloadRows_basisRows
#print axioms FramedReplay.decode_reframe
#print axioms FramedReplay.put_get
#print axioms FramedReplay.decode_xor
#print axioms FramedReplay.decode_step
#print axioms FramedReplay.physical_blank_of_decoded_blank
#print axioms FramedReplay.erase_guard_transport
#print axioms FramedReplay.decode_run
#print axioms WholeHosting.masksDisjoint_symm
#print axioms WholeHosting.swapAddress_involution
#print axioms WholeHosting.swapAddress_commute
#print axioms WholeHosting.swapAddress_disjoint_union
#print axioms WholeHosting.bitAction_involution
#print axioms WholeHosting.bitAction_commute
#print axioms WholeHosting.bitAction_disjoint_comp
#print axioms WholeHosting.remainder_disjoint
#print axioms WholeHosting.union_remainder
#print axioms WholeHosting.bitAction_complete
#print axioms WholeHosting.bitAction_empty
#print axioms WholeHosting.bitFactors_union
#print axioms WholeHosting.bitFactors_complete
#print axioms AddressPairs.split_join
#print axioms AddressPairs.join_split
#print axioms AddressPairs.relative_gauge
#print axioms AddressPairs.join_swap
#print axioms AddressPairs.relative_coordinate
#print axioms SourceMatrix.evalRow_endpoint
#print axioms SourceMatrix.evalRows_endpoint
#print axioms SourceMatrix.evalPayloadRows_endpoint
#print axioms FrameGeometry.frame_valid
#print axioms FrameGeometry.scaled_idempotent_entries
#print axioms FrameGeometry.scaled_symmetric_entries
#print axioms FrameGeometry.scaled_stack_entries
#print axioms FrameGeometry.stack_inverse_entries
#print axioms FrameGeometry.inverse_stack_entries
#print axioms FrameGeometry.transition_absorbs
#print axioms FrameGeometry.scaled_full_entries
#print axioms FrameGeometry.scaled_zero_entries
#print axioms FrameGeometry.scaled_idempotent
#print axioms FrameGeometry.scaled_symmetric
#print axioms FrameGeometry.stack_inverse
#print axioms FrameGeometry.inverse_stack
#print axioms FrameGeometry.cast_mul_factor
#print axioms FrameGeometry.four_ne_zero
#print axioms FrameGeometry.two_fifty_six_ne_zero
#print axioms FrameGeometry.projector_idempotent
#print axioms FrameGeometry.projector_symmetric
#print axioms FrameGeometry.projector_full
#print axioms FrameGeometry.projector_zero
#print axioms FrameGeometry.scaled_stack
#print axioms FrameGeometry.cast_transpose
#print axioms FrameGeometry.cast_product
#print axioms FrameGeometry.cast_selector
#print axioms FrameGeometry.projector_stack
#print axioms FrameGeometry.transition_scaled_left
#print axioms FrameGeometry.transition_scaled_right
#print axioms FrameGeometry.normalized_absorption
#print axioms FrameGeometry.transition_projectors
#print axioms FrameGeometry.stack_right_inverse
#print axioms FrameGeometry.stack_left_inverse
#print axioms FrameGeometry.partialSwap_involution
#print axioms FrameGeometry.partialSwap_nested
#print axioms FrameGeometry.partialSwap_nested_reverse
#print axioms FrameGeometry.full_after_frame
#print axioms FrameGeometry.frame_after_full
#print axioms FrameGeometry.firstEight_replaceFirst
#print axioms FrameGeometry.replaceFirst_twice
#print axioms FrameGeometry.replaceFirst_firstEight
#print axioms FrameGeometry.liftPair_comp
#print axioms FrameGeometry.liftPair_id
#print axioms FrameGeometry.partialSwap_coordinate
#print axioms FrameGeometry.coordinate_residual
#print axioms FrameGeometry.residual_partialSwap
#print axioms FrameGeometry.full_after_frame64_coordinate
#print axioms FrameGeometry.frame_after_full64_coordinate
#print axioms FrameGeometry.coordinateSwap64_involution
#print axioms FrameGeometry.stage2_relative_transport
#print axioms FrameGeometry.stage2_helper_endpoint
#print axioms FrameTrace.flag_mono
#print axioms FrameTrace.checked_valid
#print axioms FrameTrace.scalar_projection
#print axioms SourceFrameLabels.labels_checked
#print axioms SourceFrameLabels.labels_valid
#print axioms SourceFrameLabels.label_range
#print axioms SourceFrameLabels.copy_frames
#print axioms SourceFrameLabels.erase_frames
#print axioms SourceFrameMoves.moves_checked
#print axioms SourceFrameMoves.move_pair
#print axioms SourceFrameMoves.move_range
#print axioms SourceFrameMoves.move_transition
#print axioms SourceFrameMoves.move_absorbs
#print axioms SourceFrameTrace.initial_tabulate
#print axioms SourceFrameTrace.final_tabulate
#print axioms SourceFrameTrace.project0
#print axioms SourceFrameTrace.checkpoint0
#print axioms SourceFrameTrace.project1
#print axioms SourceFrameTrace.checkpoint1
#print axioms SourceFrameTrace.project2
#print axioms SourceFrameTrace.checkpoint2
#print axioms SourceFrameTrace.project3
#print axioms SourceFrameTrace.checkpoint3
#print axioms SourceFrameTrace.project4
#print axioms SourceFrameTrace.checkpoint4
#print axioms SourceFrameTrace.project5
#print axioms SourceFrameTrace.checkpoint5
#print axioms SourceFrameTrace.project6
#print axioms SourceFrameTrace.checkpoint6
#print axioms SourceFrameTrace.project7
#print axioms SourceFrameTrace.checkpoint7
#print axioms SourceFrameTrace.project8
#print axioms SourceFrameTrace.checkpoint8
#print axioms SourceFrameTrace.project9
#print axioms SourceFrameTrace.checkpoint9
#print axioms SourceFrameTrace.project10
#print axioms SourceFrameTrace.checkpoint10
#print axioms SourceFrameTrace.project11
#print axioms SourceFrameTrace.checkpoint11
#print axioms SourceFrameTrace.project12
#print axioms SourceFrameTrace.checkpoint12
#print axioms SourceFrameTrace.project13
#print axioms SourceFrameTrace.checkpoint13
#print axioms SourceFrameTrace.project14
#print axioms SourceFrameTrace.checkpoint14
#print axioms SourceFrameTrace.project15
#print axioms SourceFrameTrace.checkpoint15
#print axioms SourceFrameTrace.project16
#print axioms SourceFrameTrace.checkpoint16
#print axioms SourceFrameTrace.project17
#print axioms SourceFrameTrace.checkpoint17
#print axioms SourceFrameTrace.project18
#print axioms SourceFrameTrace.checkpoint18
#print axioms SourceFrameTrace.project19
#print axioms SourceFrameTrace.checkpoint19
#print axioms SourceFrameTrace.project20
#print axioms SourceFrameTrace.checkpoint20
#print axioms SourceFrameTrace.project21
#print axioms SourceFrameTrace.checkpoint21
#print axioms SourceFrameTrace.project22
#print axioms SourceFrameTrace.checkpoint22
#print axioms SourceFrameTrace.project23
#print axioms SourceFrameTrace.checkpoint23
#print axioms SourceFrameTrace.project24
#print axioms SourceFrameTrace.checkpoint24
#print axioms SourceFrameTrace.project25
#print axioms SourceFrameTrace.checkpoint25
#print axioms SourceFrameTrace.project26
#print axioms SourceFrameTrace.checkpoint26
#print axioms SourceFrameTrace.project27
#print axioms SourceFrameTrace.checkpoint27
#print axioms SourceFrameTrace.project28
#print axioms SourceFrameTrace.checkpoint28
#print axioms SourceFrameTrace.project29
#print axioms SourceFrameTrace.checkpoint29
#print axioms SourceFrameTrace.project30
#print axioms SourceFrameTrace.checkpoint30
#print axioms SourceFrameTrace.project31
#print axioms SourceFrameTrace.checkpoint31
#print axioms SourceFrameTrace.project32
#print axioms SourceFrameTrace.checkpoint32
#print axioms SourceFrameTrace.project33
#print axioms SourceFrameTrace.checkpoint33
#print axioms SourceFrameTrace.project34
#print axioms SourceFrameTrace.checkpoint34
#print axioms SourceFrameTrace.project35
#print axioms SourceFrameTrace.checkpoint35
#print axioms SourceFrameTrace.project36
#print axioms SourceFrameTrace.checkpoint36
#print axioms SourceFrameTrace.project37
#print axioms SourceFrameTrace.checkpoint37
#print axioms SourceFrameTrace.project38
#print axioms SourceFrameTrace.checkpoint38
#print axioms SourceFrameTrace.project39
#print axioms SourceFrameTrace.checkpoint39
#print axioms SourceFrameTrace.project40
#print axioms SourceFrameTrace.checkpoint40
#print axioms SourceFrameTrace.project41
#print axioms SourceFrameTrace.checkpoint41
#print axioms SourceFrameTrace.project42
#print axioms SourceFrameTrace.checkpoint42
#print axioms SourceFrameTrace.project43
#print axioms SourceFrameTrace.checkpoint43
#print axioms SourceFrameTrace.project44
#print axioms SourceFrameTrace.checkpoint44
#print axioms SourceFrameTrace.project45
#print axioms SourceFrameTrace.checkpoint45
#print axioms SourceFrameTrace.project46
#print axioms SourceFrameTrace.checkpoint46
#print axioms SourceFrameTrace.project47
#print axioms SourceFrameTrace.checkpoint47
#print axioms SourceFrameTrace.project48
#print axioms SourceFrameTrace.checkpoint48
#print axioms SourceFrameTrace.project49
#print axioms SourceFrameTrace.checkpoint49
#print axioms SourceFrameTrace.project50
#print axioms SourceFrameTrace.checkpoint50
#print axioms SourceFrameTrace.project51
#print axioms SourceFrameTrace.checkpoint51
#print axioms SourceFrameTrace.project52
#print axioms SourceFrameTrace.checkpoint52
#print axioms SourceFrameTrace.project53
#print axioms SourceFrameTrace.checkpoint53
#print axioms SourceFrameTrace.project54
#print axioms SourceFrameTrace.checkpoint54
#print axioms SourceFrameTrace.project55
#print axioms SourceFrameTrace.checkpoint55
#print axioms SourceFrameTrace.project56
#print axioms SourceFrameTrace.checkpoint56
#print axioms SourceFrameTrace.project57
#print axioms SourceFrameTrace.checkpoint57
#print axioms SourceFrameTrace.project58
#print axioms SourceFrameTrace.checkpoint58
#print axioms SourceFrameTrace.project59
#print axioms SourceFrameTrace.checkpoint59
#print axioms SourceFrameTrace.project60
#print axioms SourceFrameTrace.checkpoint60
#print axioms SourceFrameTrace.project61
#print axioms SourceFrameTrace.checkpoint61
#print axioms SourceFrameTrace.project62
#print axioms SourceFrameTrace.checkpoint62
#print axioms SourceFrameTrace.project63
#print axioms SourceFrameTrace.checkpoint63
#print axioms SourceFrameTrace.project64
#print axioms SourceFrameTrace.checkpoint64
#print axioms SourceFrameTrace.project65
#print axioms SourceFrameTrace.checkpoint65
#print axioms SourceFrameTrace.project66
#print axioms SourceFrameTrace.checkpoint66
#print axioms SourceFrameTrace.project67
#print axioms SourceFrameTrace.checkpoint67
#print axioms SourceFrameTrace.project68
#print axioms SourceFrameTrace.checkpoint68
#print axioms SourceFrameTrace.project69
#print axioms SourceFrameTrace.checkpoint69
#print axioms SourceFrameTrace.project70
#print axioms SourceFrameTrace.checkpoint70
#print axioms SourceFrameTrace.project71
#print axioms SourceFrameTrace.checkpoint71
#print axioms SourceFrameTrace.project72
#print axioms SourceFrameTrace.checkpoint72
#print axioms SourceFrameTrace.project73
#print axioms SourceFrameTrace.checkpoint73
#print axioms SourceFrameTrace.project74
#print axioms SourceFrameTrace.checkpoint74
#print axioms SourceFrameTrace.project75
#print axioms SourceFrameTrace.checkpoint75
#print axioms SourceFrameTrace.project76
#print axioms SourceFrameTrace.checkpoint76
#print axioms SourceFrameTrace.project77
#print axioms SourceFrameTrace.checkpoint77
#print axioms SourceFrameTrace.project78
#print axioms SourceFrameTrace.checkpoint78
#print axioms SourceFrameTrace.project79
#print axioms SourceFrameTrace.checkpoint79
#print axioms SourceFrameTrace.project80
#print axioms SourceFrameTrace.checkpoint80
#print axioms SourceFrameTrace.project81
#print axioms SourceFrameTrace.checkpoint81
#print axioms SourceFrameTrace.project82
#print axioms SourceFrameTrace.checkpoint82
#print axioms SourceFrameTrace.project83
#print axioms SourceFrameTrace.checkpoint83
#print axioms SourceFrameTrace.project84
#print axioms SourceFrameTrace.checkpoint84
#print axioms SourceFrameTrace.project85
#print axioms SourceFrameTrace.checkpoint85
#print axioms SourceFrameTrace.project86
#print axioms SourceFrameTrace.checkpoint86
#print axioms SourceFrameTrace.project87
#print axioms SourceFrameTrace.checkpoint87
#print axioms SourceFrameTrace.project88
#print axioms SourceFrameTrace.checkpoint88
#print axioms SourceFrameTrace.project89
#print axioms SourceFrameTrace.checkpoint89
#print axioms SourceFrameTrace.project90
#print axioms SourceFrameTrace.checkpoint90
#print axioms SourceFrameTrace.project91
#print axioms SourceFrameTrace.checkpoint91
#print axioms SourceFrameTrace.project92
#print axioms SourceFrameTrace.checkpoint92
#print axioms SourceFrameTrace.project93
#print axioms SourceFrameTrace.checkpoint93
#print axioms SourceFrameTrace.project94
#print axioms SourceFrameTrace.checkpoint94
#print axioms SourceFrameTrace.project95
#print axioms SourceFrameTrace.checkpoint95
#print axioms SourceFrameTrace.combine
#print axioms SourceFrameTrace.finish96
#print axioms SourceFrameTrace.finish95
#print axioms SourceFrameTrace.finish94
#print axioms SourceFrameTrace.finish93
#print axioms SourceFrameTrace.finish92
#print axioms SourceFrameTrace.finish91
#print axioms SourceFrameTrace.finish90
#print axioms SourceFrameTrace.finish89
#print axioms SourceFrameTrace.finish88
#print axioms SourceFrameTrace.finish87
#print axioms SourceFrameTrace.finish86
#print axioms SourceFrameTrace.finish85
#print axioms SourceFrameTrace.finish84
#print axioms SourceFrameTrace.finish83
#print axioms SourceFrameTrace.finish82
#print axioms SourceFrameTrace.finish81
#print axioms SourceFrameTrace.finish80
#print axioms SourceFrameTrace.finish79
#print axioms SourceFrameTrace.finish78
#print axioms SourceFrameTrace.finish77
#print axioms SourceFrameTrace.finish76
#print axioms SourceFrameTrace.finish75
#print axioms SourceFrameTrace.finish74
#print axioms SourceFrameTrace.finish73
#print axioms SourceFrameTrace.finish72
#print axioms SourceFrameTrace.finish71
#print axioms SourceFrameTrace.finish70
#print axioms SourceFrameTrace.finish69
#print axioms SourceFrameTrace.finish68
#print axioms SourceFrameTrace.finish67
#print axioms SourceFrameTrace.finish66
#print axioms SourceFrameTrace.finish65
#print axioms SourceFrameTrace.finish64
#print axioms SourceFrameTrace.finish63
#print axioms SourceFrameTrace.finish62
#print axioms SourceFrameTrace.finish61
#print axioms SourceFrameTrace.finish60
#print axioms SourceFrameTrace.finish59
#print axioms SourceFrameTrace.finish58
#print axioms SourceFrameTrace.finish57
#print axioms SourceFrameTrace.finish56
#print axioms SourceFrameTrace.finish55
#print axioms SourceFrameTrace.finish54
#print axioms SourceFrameTrace.finish53
#print axioms SourceFrameTrace.finish52
#print axioms SourceFrameTrace.finish51
#print axioms SourceFrameTrace.finish50
#print axioms SourceFrameTrace.finish49
#print axioms SourceFrameTrace.finish48
#print axioms SourceFrameTrace.finish47
#print axioms SourceFrameTrace.finish46
#print axioms SourceFrameTrace.finish45
#print axioms SourceFrameTrace.finish44
#print axioms SourceFrameTrace.finish43
#print axioms SourceFrameTrace.finish42
#print axioms SourceFrameTrace.finish41
#print axioms SourceFrameTrace.finish40
#print axioms SourceFrameTrace.finish39
#print axioms SourceFrameTrace.finish38
#print axioms SourceFrameTrace.finish37
#print axioms SourceFrameTrace.finish36
#print axioms SourceFrameTrace.finish35
#print axioms SourceFrameTrace.finish34
#print axioms SourceFrameTrace.finish33
#print axioms SourceFrameTrace.finish32
#print axioms SourceFrameTrace.finish31
#print axioms SourceFrameTrace.finish30
#print axioms SourceFrameTrace.finish29
#print axioms SourceFrameTrace.finish28
#print axioms SourceFrameTrace.finish27
#print axioms SourceFrameTrace.finish26
#print axioms SourceFrameTrace.finish25
#print axioms SourceFrameTrace.finish24
#print axioms SourceFrameTrace.finish23
#print axioms SourceFrameTrace.finish22
#print axioms SourceFrameTrace.finish21
#print axioms SourceFrameTrace.finish20
#print axioms SourceFrameTrace.finish19
#print axioms SourceFrameTrace.finish18
#print axioms SourceFrameTrace.finish17
#print axioms SourceFrameTrace.finish16
#print axioms SourceFrameTrace.finish15
#print axioms SourceFrameTrace.finish14
#print axioms SourceFrameTrace.finish13
#print axioms SourceFrameTrace.finish12
#print axioms SourceFrameTrace.finish11
#print axioms SourceFrameTrace.finish10
#print axioms SourceFrameTrace.finish9
#print axioms SourceFrameTrace.finish8
#print axioms SourceFrameTrace.finish7
#print axioms SourceFrameTrace.finish6
#print axioms SourceFrameTrace.finish5
#print axioms SourceFrameTrace.finish4
#print axioms SourceFrameTrace.finish3
#print axioms SourceFrameTrace.finish2
#print axioms SourceFrameTrace.finish1
#print axioms SourceFrameTrace.finish0
#print axioms SourceFrameTrace.scalar_word
#print axioms SourceFrameTrace.forward_checked
#print axioms SourceFrameTrace.forward_valid
#print axioms TreeReplay.payload_checks_sound
#print axioms TreeReplay.checked_payload_guards_sound
#print axioms FrameTrace.matches_get
#print axioms FrameTrace.matches_step
#print axioms FrameTrace.add_frames_equal
#print axioms FrameTrace.matches_run
#print axioms FrameTrace.valid_step
#print axioms FrameTrace.valid_trace
#print axioms FrameTrace.decoded_run
#print axioms OwnerTransport.write_other
#print axioms OwnerTransport.gather_write
#print axioms OwnerTransport.rawXor_write
#print axioms OwnerTransport.rawTransport_write
#print axioms OwnerTransport.gather_step
#print axioms OwnerTransport.logicalStep_tree
#print axioms OwnerTransport.rawStep_other
#print axioms OwnerTransport.replace_fin_tree
#print axioms OwnerTransport.logicalStep_fin_tree
#print axioms OwnerTransport.physicalStep_full
#print axioms OwnerTransport.gather_run_framed
#print axioms OwnerTransport.runRaw_other
#print axioms OwnerTransport.extendCover_owner
#print axioms OwnerTransport.initialRaw_other
#print axioms OwnerTransport.gather_initialRaw
#print axioms OwnerTransport.route_native_address
#print axioms OwnerTransport.inverse_common_cover
#print axioms OwnerTransport.rawXor_fromNative
#print axioms OwnerTransport.rawTransport_fromNative
#print axioms OwnerTransport.rawStep_fromNative
#print axioms OwnerTransport.runRaw_fromNative
#print axioms SourceFrameTrace.indices_checked
#print axioms SourceFrameTrace.indices_bound
#print axioms SourceFrameTrace.route_projection
#print axioms SourceOwnership.perm_inverse
#print axioms SourceOwnership.inverse_perm
#print axioms SourceOwnership.perm_support
#print axioms SourceOwnership.fingerprint_injective
#print axioms SourceOwnership.owner_inverse
#print axioms SourceOwnership.family_tag_injective
#print axioms SourceOwnership.family_data
#print axioms SourceOwnership.helper_range
#print axioms SourceOwnership.helper_frame
#print axioms SourceOwnership.helper_child
#print axioms SourceFrameTrace.initial_owner_frames
#print axioms SourceFrameTrace.helper_final_frames
#print axioms SourceFrameTrace.initial_frame_range
#print axioms SourceFrameTrace.final_frame_range
#print axioms SelectedGeometry.tag_frame_bound
#print axioms SelectedGeometry.tag_residual_diagonal
#print axioms SelectedGeometry.source_mask_outside
#print axioms SourceMatrix.combine
#print axioms SourceMatrix.chunks_flatten
#print axioms SourceMatrix.checkpoint0
#print axioms SourceMatrix.checkpoint1
#print axioms SourceMatrix.checkpoint2
#print axioms SourceMatrix.checkpoint3
#print axioms SourceMatrix.checkpoint4
#print axioms SourceMatrix.checkpoint5
#print axioms SourceMatrix.checkpoint6
#print axioms SourceMatrix.checkpoint7
#print axioms SourceMatrix.checkpoint8
#print axioms SourceMatrix.checkpoint9
#print axioms SourceMatrix.checkpoint10
#print axioms SourceMatrix.checkpoint11
#print axioms SourceMatrix.checkpoint12
#print axioms SourceMatrix.checkpoint13
#print axioms SourceMatrix.checkpoint14
#print axioms SourceMatrix.checkpoint15
#print axioms SourceMatrix.checkpoint16
#print axioms SourceMatrix.checkpoint17
#print axioms SourceMatrix.checkpoint18
#print axioms SourceMatrix.checkpoint19
#print axioms SourceMatrix.checkpoint20
#print axioms SourceMatrix.checkpoint21
#print axioms SourceMatrix.checkpoint22
#print axioms SourceMatrix.checkpoint23
#print axioms SourceMatrix.checkpoint24
#print axioms SourceMatrix.checkpoint25
#print axioms SourceMatrix.checkpoint26
#print axioms SourceMatrix.checkpoint27
#print axioms SourceMatrix.checkpoint28
#print axioms SourceMatrix.checkpoint29
#print axioms SourceMatrix.checkpoint30
#print axioms SourceMatrix.checkpoint31
#print axioms SourceMatrix.checkpoint32
#print axioms SourceMatrix.checkpoint33
#print axioms SourceMatrix.checkpoint34
#print axioms SourceMatrix.checkpoint35
#print axioms SourceMatrix.checkpoint36
#print axioms SourceMatrix.checkpoint37
#print axioms SourceMatrix.checkpoint38
#print axioms SourceMatrix.checkpoint39
#print axioms SourceMatrix.checkpoint40
#print axioms SourceMatrix.checkpoint41
#print axioms SourceMatrix.checkpoint42
#print axioms SourceMatrix.checkpoint43
#print axioms SourceMatrix.checkpoint44
#print axioms SourceMatrix.checkpoint45
#print axioms SourceMatrix.checkpoint46
#print axioms SourceMatrix.checkpoint47
#print axioms SourceMatrix.checkpoint48
#print axioms SourceMatrix.checkpoint49
#print axioms SourceMatrix.checkpoint50
#print axioms SourceMatrix.checkpoint51
#print axioms SourceMatrix.checkpoint52
#print axioms SourceMatrix.checkpoint53
#print axioms SourceMatrix.checkpoint54
#print axioms SourceMatrix.checkpoint55
#print axioms SourceMatrix.checkpoint56
#print axioms SourceMatrix.checkpoint57
#print axioms SourceMatrix.checkpoint58
#print axioms SourceMatrix.checkpoint59
#print axioms SourceMatrix.checkpoint60
#print axioms SourceMatrix.checkpoint61
#print axioms SourceMatrix.checkpoint62
#print axioms SourceMatrix.checkpoint63
#print axioms SourceMatrix.checkpoint64
#print axioms SourceMatrix.checkpoint65
#print axioms SourceMatrix.checkpoint66
#print axioms SourceMatrix.checkpoint67
#print axioms SourceMatrix.checkpoint68
#print axioms SourceMatrix.checkpoint69
#print axioms SourceMatrix.checkpoint70
#print axioms SourceMatrix.checkpoint71
#print axioms SourceMatrix.checkpoint72
#print axioms SourceMatrix.checkpoint73
#print axioms SourceMatrix.checkpoint74
#print axioms SourceMatrix.checkpoint75
#print axioms SourceMatrix.checkpoint76
#print axioms SourceMatrix.checkpoint77
#print axioms SourceMatrix.checkpoint78
#print axioms SourceMatrix.checkpoint79
#print axioms SourceMatrix.checkpoint80
#print axioms SourceMatrix.checkpoint81
#print axioms SourceMatrix.checkpoint82
#print axioms SourceMatrix.checkpoint83
#print axioms SourceMatrix.checkpoint84
#print axioms SourceMatrix.checkpoint85
#print axioms SourceMatrix.checkpoint86
#print axioms SourceMatrix.checkpoint87
#print axioms SourceMatrix.checkpoint88
#print axioms SourceMatrix.checkpoint89
#print axioms SourceMatrix.checkpoint90
#print axioms SourceMatrix.checkpoint91
#print axioms SourceMatrix.checkpoint92
#print axioms SourceMatrix.checkpoint93
#print axioms SourceMatrix.checkpoint94
#print axioms SourceMatrix.checkpoint95
#print axioms SourceMatrix.finish96
#print axioms SourceMatrix.finish95
#print axioms SourceMatrix.finish94
#print axioms SourceMatrix.finish93
#print axioms SourceMatrix.finish92
#print axioms SourceMatrix.finish91
#print axioms SourceMatrix.finish90
#print axioms SourceMatrix.finish89
#print axioms SourceMatrix.finish88
#print axioms SourceMatrix.finish87
#print axioms SourceMatrix.finish86
#print axioms SourceMatrix.finish85
#print axioms SourceMatrix.finish84
#print axioms SourceMatrix.finish83
#print axioms SourceMatrix.finish82
#print axioms SourceMatrix.finish81
#print axioms SourceMatrix.finish80
#print axioms SourceMatrix.finish79
#print axioms SourceMatrix.finish78
#print axioms SourceMatrix.finish77
#print axioms SourceMatrix.finish76
#print axioms SourceMatrix.finish75
#print axioms SourceMatrix.finish74
#print axioms SourceMatrix.finish73
#print axioms SourceMatrix.finish72
#print axioms SourceMatrix.finish71
#print axioms SourceMatrix.finish70
#print axioms SourceMatrix.finish69
#print axioms SourceMatrix.finish68
#print axioms SourceMatrix.finish67
#print axioms SourceMatrix.finish66
#print axioms SourceMatrix.finish65
#print axioms SourceMatrix.finish64
#print axioms SourceMatrix.finish63
#print axioms SourceMatrix.finish62
#print axioms SourceMatrix.finish61
#print axioms SourceMatrix.finish60
#print axioms SourceMatrix.finish59
#print axioms SourceMatrix.finish58
#print axioms SourceMatrix.finish57
#print axioms SourceMatrix.finish56
#print axioms SourceMatrix.finish55
#print axioms SourceMatrix.finish54
#print axioms SourceMatrix.finish53
#print axioms SourceMatrix.finish52
#print axioms SourceMatrix.finish51
#print axioms SourceMatrix.finish50
#print axioms SourceMatrix.finish49
#print axioms SourceMatrix.finish48
#print axioms SourceMatrix.finish47
#print axioms SourceMatrix.finish46
#print axioms SourceMatrix.finish45
#print axioms SourceMatrix.finish44
#print axioms SourceMatrix.finish43
#print axioms SourceMatrix.finish42
#print axioms SourceMatrix.finish41
#print axioms SourceMatrix.finish40
#print axioms SourceMatrix.finish39
#print axioms SourceMatrix.finish38
#print axioms SourceMatrix.finish37
#print axioms SourceMatrix.finish36
#print axioms SourceMatrix.finish35
#print axioms SourceMatrix.finish34
#print axioms SourceMatrix.finish33
#print axioms SourceMatrix.finish32
#print axioms SourceMatrix.finish31
#print axioms SourceMatrix.finish30
#print axioms SourceMatrix.finish29
#print axioms SourceMatrix.finish28
#print axioms SourceMatrix.finish27
#print axioms SourceMatrix.finish26
#print axioms SourceMatrix.finish25
#print axioms SourceMatrix.finish24
#print axioms SourceMatrix.finish23
#print axioms SourceMatrix.finish22
#print axioms SourceMatrix.finish21
#print axioms SourceMatrix.finish20
#print axioms SourceMatrix.finish19
#print axioms SourceMatrix.finish18
#print axioms SourceMatrix.finish17
#print axioms SourceMatrix.finish16
#print axioms SourceMatrix.finish15
#print axioms SourceMatrix.finish14
#print axioms SourceMatrix.finish13
#print axioms SourceMatrix.finish12
#print axioms SourceMatrix.finish11
#print axioms SourceMatrix.finish10
#print axioms SourceMatrix.finish9
#print axioms SourceMatrix.finish8
#print axioms SourceMatrix.finish7
#print axioms SourceMatrix.finish6
#print axioms SourceMatrix.finish5
#print axioms SourceMatrix.finish4
#print axioms SourceMatrix.finish3
#print axioms SourceMatrix.finish2
#print axioms SourceMatrix.finish1
#print axioms SourceMatrix.finish0
#print axioms SourceMatrix.runFull_checked
#print axioms SourceMatrix.literal_word_checked
#print axioms SourceMatrix.literal_word_rows
#print axioms SourceMatrix.initial_formula
#print axioms SourceMatrix.expected_formula
#print axioms SourceMatrix.arbitrary_dirty_bools
#print axioms SourceMatrix.arbitrary_dirty_guards
#print axioms SourceMatrix.arbitrary_dirty_payloads
#print axioms SourceMatrix.actual_payload_clean
#print axioms SourceMatrix.arbitrary_dirty_temp_restored
#print axioms SourceMatrix.arbitrary_dirty_original_roles
#print axioms SourceFramed.initial_matches
#print axioms SourceFramed.initial_decoded
#print axioms SourceFramed.actual_valid
#print axioms SourceFramed.final_matches
#print axioms SourceFramed.actual_decoded_endpoint
#print axioms SourceFramed.actual_physical_endpoint
#print axioms SourceFramed.actual_temporary_restored
#print axioms SourceFramed.all_physical_endpoints
#print axioms SourceRaw.gather_initial
#print axioms SourceRaw.gather_final
#print axioms SourceRaw.actual_valid
#print axioms SourceRaw.payload_endpoint
#print axioms SourceRaw.private_restored
#print axioms SourceRaw.other_preserved
#print axioms SourceRaw.other_payload_preserved
#print axioms MultiHosting.base_commutes
#print axioms MultiHosting.runBase_commutes
#print axioms MultiHosting.delay_residuals
#print axioms MultiHosting.multi_hosting
#print axioms MultiHosting.multi_hosting_in_context
#print axioms MultiHosting.PhysicalImplementations.original_projection
#print axioms MultiHosting.PhysicalImplementations.relocated_projection
#print axioms MultiHosting.physical_multi_hosting
#print axioms MultiHosting.physical_multi_hosting_in_context
#print axioms SourceOwnership.unindex_reindex
#print axioms SourceOwnership.reindex_unindex
#print axioms SourceOwnership.residual_projector_transport
#print axioms SourceOwnership.perm_tag_injective
#print axioms SourceOwnership.unindex_tag_injective
#print axioms SourceOwnership.family_data_general
#print axioms SourceOwnership.same_family_data
#print axioms SourceOwnership.owners_injective
#print axioms SourceConnection.packed_data
#print axioms SourceConnection.packed_helper
#print axioms SourceConnection.invoke_endpoint
#print axioms SourceConnection.swap_conjugacy
#print axioms SourceConnection.host_transport
#print axioms SourceConnection.original_retained
#print axioms SourceConnection.original_bank_output
#print axioms SourceConnection.relocated_retained
#print axioms InvocationPayload.extend_owner
#print axioms InvocationPayload.extend_outside
#print axioms InvocationPayload.realize_owner
#print axioms InvocationPayload.input_realize
#print axioms InvocationPayload.input_realize_packed
#print axioms InvocationPayload.realized_gather
#print axioms InvocationPayload.realized_payload
#print axioms InvocationPayload.realized_payloads
#print axioms PortGeometry.doubled_orthogonal_entries
#print axioms PortGeometry.quarteredRoute_exact
#print axioms PortGeometry.doubled_row_orthogonal_entries
#print axioms PortGeometry.doubled_orthogonal
#print axioms PortGeometry.doubled_row_orthogonal
#print axioms PortGeometry.basis_entry
#print axioms PortGeometry.cast_orthogonal
#print axioms PortGeometry.cast_row_orthogonal
#print axioms PortGeometry.basis_transpose_mul
#print axioms PortGeometry.basis_mul_transpose
#print axioms PortGeometry.chart8_dot
#print axioms PortGeometry.firstEight_add
#print axioms PortGeometry.firstEight_smul
#print axioms PortGeometry.firstEight_extendEight
#print axioms PortGeometry.extendEight_comp
#print axioms PortGeometry.extendEight_id
#print axioms PortGeometry.chart64_firstEight
#print axioms PortGeometry.chart64_outside
#print axioms PortGeometry.chart64_bijective
#print axioms PortGeometry.chart64_add
#print axioms PortGeometry.chart64_smul
#print axioms PortGeometry.chart64_dot
#print axioms PortGeometry.chart64_symm_dot
#print axioms PortGeometry.chart64_symm_add
#print axioms PortGeometry.chart64_symm_smul
#print axioms PortGeometry.stage2Index_involutive
#print axioms PortGeometry.stage2Coordinates_dot
#print axioms PortGeometry.dataRoute64_dot
#print axioms PortGeometry.dataRoute64_add
#print axioms PortGeometry.dataRoute64_smul
#print axioms PortGeometry.dataRoute64_involutive
#print axioms PortGeometry.route15_entry
#print axioms PortGeometry.sourceRoute64_eq
#print axioms SourceOwnership.slotChart_dot
#print axioms SourceOwnership.slotChart_add
#print axioms SourceOwnership.slotChart_smul
#print axioms SourceOwnership.familyChart_dot
#print axioms SourceOwnership.familyChart_add
#print axioms SourceOwnership.familyChart_smul
#print axioms SourceOwnership.helper_sigma_dot
#print axioms SourceOwnership.helper_sigma_add
#print axioms SourceOwnership.helper_sigma_smul
#print axioms SourceOwnership.physicalOwner_formula
#print axioms SourceOwnership.physicalOwner_common
#print axioms SourceOwnership.physicalOwner_injective
#print axioms SourceOwnership.family_lt
#print axioms SourceOwnership.activeOwner_injective
#print axioms SourceOwnership.active_gather_step
#print axioms SourceOwnership.sourceActiveOwner_injective
#print axioms SourceOwnership.source_gather_run
#print axioms SourceOwnership.helper_address_forward
#print axioms SourceOwnership.helper_address_inverse
#print axioms SourceOwnership.source_address_gather_run
#print axioms SourceOwnership.source_common_cover
#print axioms SourceOwnership.source_native_run
#print axioms ParentOwnership.perm_inverse
#print axioms ParentOwnership.inverse_perm
#print axioms ParentOwnership.perm_support
#print axioms ParentOwnership.fingerprint_injective
#print axioms ParentOwnership.owner_inverse
#print axioms ParentOwnership.family_tag_injective
#print axioms ParentOwnership.family_data
#print axioms ParentOwnership.helper_range
#print axioms ParentOwnership.helper_frame
#print axioms ParentOwnership.unindex_reindex
#print axioms ParentOwnership.reindex_unindex
#print axioms ParentOwnership.residual_projector_transport
#print axioms ParentOwnership.perm_tag_injective
#print axioms ParentOwnership.unindex_tag_injective
#print axioms ParentOwnership.family_data_general
#print axioms ParentOwnership.same_family_data
#print axioms ParentOwnership.owners_injective
#print axioms ParentOwnership.slotChart_dot
#print axioms ParentOwnership.slotChart_add
#print axioms ParentOwnership.slotChart_smul
#print axioms ParentOwnership.helper_sigma_dot
#print axioms ParentOwnership.helper_sigma_add
#print axioms ParentOwnership.helper_sigma_smul
#print axioms ParentOwnership.helper_residual_transport
#print axioms ParentOwnership.physicalOwner_formula
#print axioms ParentOwnership.physicalOwner_injective
#print axioms ParentOwnership.family_lt
#print axioms ParentOwnership.sourceActiveOwner_avoids_host_families
#print axioms ParentOwnership.sourceActiveOwner_injective
#print axioms ParentOwnership.source_gather_run
#print axioms ParentOwnership.helper_address_forward
#print axioms ParentOwnership.helper_address_inverse
#print axioms ParentOwnership.source_address_gather_run
#print axioms ParentOwnership.source_common_cover
#print axioms ParentOwnership.source_native_run
#print axioms PhysicalSourceConnection.helper_endpoints
#print axioms PhysicalSourceConnection.helper_endpoint
#print axioms PhysicalSourceConnection.physical_data_endpoints
#print axioms PhysicalSourceConnection.data_independent
#print axioms PhysicalSourceConnection.data_endpoint
#print axioms PhysicalSourceConnection.hosted_endpoint
#print axioms PhysicalSourceConnection.original_retained
#print axioms PhysicalSourceConnection.relocated_retained
#print axioms PhysicalSourceConnection.tag_child_cases
#print axioms PhysicalSourceConnection.tag_pending_contains
#print axioms PhysicalSourceConnection.selected_invocation_completion
#print axioms SelectedGeometry.gauges_tag
#print axioms SelectedGeometry.helper_relative
#print axioms SourceLayouts.data_owner_eq
#print axioms SourceLayouts.data_chart_eq
#print axioms SourceLayouts.host_family
#print axioms SourceLayouts.parent_owner_ne_host
#print axioms SourceLayouts.host_ne_parent_owner
#print axioms SourceLayouts.host_chart_forward
#print axioms SourceLayouts.host_chart_inverse
#print axioms SourceInvocation.oldOwner_injective
#print axioms SourceInvocation.newOwner_injective
#print axioms SourceInvocation.hostOwner_injective
#print axioms SourceInvocation.host_not_old
#print axioms SourceInvocation.tailPayload_outside
#print axioms SourceInvocation.hostPayload_host
#print axioms SourceInvocation.hostPayload_outside
#print axioms SourceInvocation.oldPayload_host
#print axioms SourceInvocation.oldPayload_outside
#print axioms SourceInvocation.newPayload_outside
#print axioms SourceInvocation.parent_family_lt_private
#print axioms SourceInvocation.owner_overlap_data
#print axioms SourceInvocation.owner_overlap_charts
#print axioms SourceInvocation.commonNativeCover_new
#print axioms SourceInvocation.new_common_cover
#print axioms SourceInvocation.old_common_cover
#print axioms SourceControls.actual_add_event
#print axioms SourceControls.omitted_add_changes_row
#print axioms SourceControls.omitted_add_keeps_guards
#print axioms SourceControls.actual_first_copy
#print axioms SourceControls.dirty_private_copy_rejected
#print axioms SourceControls.dirty_private_copy_would_overwrite
#print axioms SourceControls.literal_helper_three_survives
#print axioms SourceControls.literal_helper_three_not_zero
#print axioms SourceInvocation.oldRaw_data
#print axioms SourceInvocation.newRaw_data
#print axioms SourceInvocation.oldRaw_bank
#print axioms SourceInvocation.oldRaw_host
#print axioms SourceInvocation.newRaw_host
#print axioms SourceInvocation.oldRaw_outside
#print axioms SourceInvocation.newRaw_outside
#print axioms SourceInvocation.oldResult_framed
#print axioms SourceInvocation.newResult_framed
#print axioms SourceDataBehavior.first_initial_frame
#print axioms SourceDataBehavior.second_initial_frame
#print axioms SourceDataBehavior.first_final_frame
#print axioms SourceDataBehavior.second_final_frame
#print axioms SourceDataBehavior.framed_first
#print axioms SourceDataBehavior.framed_second
#print axioms SourceDataBehavior.framed_data_formula
#print axioms SourceDataBehavior.old_data_formula
#print axioms SourceDataBehavior.new_data_formula
#print axioms SourceInvocation.newPayload_host
#print axioms SourceInvocation.oldPayload_data
#print axioms SourceInvocation.newPayload_data
#print axioms SourceInvocation.oldPayload_bank
#print axioms SourceInvocation.shared_host_input
#print axioms SourceInvocation.shared_data_input
#print axioms SourceRawGuards.raw_clean_of_framed
#print axioms SourceRawGuards.raw_clean_run_of_framed
#print axioms SourceRawGuards.native_clean_of_raw
#print axioms SourceRawGuards.native_clean_run_of_raw
#print axioms SourceRawGuards.actual_raw_clean
#print axioms SourceRawGuards.initial_fromNative
#print axioms SourceRawGuards.actual_native_clean
#print axioms SourceRawGuards.native_run_refines
#print axioms SourceRawGuards.native_payload_endpoint
#print axioms SourceRawGuards.native_private_restored
#print axioms SourceRawGuards.native_other_preserved
#print axioms SourceInvocation.native_payload_roundtrip
#print axioms SourceInvocation.old_native_realization
#print axioms SourceInvocation.new_native_realization
#print axioms SourceInvocation.old_native_clean
#print axioms SourceInvocation.new_native_clean
#print axioms SourceInvocation.old_native_temporary_restored
#print axioms SourceInvocation.new_native_temporary_restored
#print axioms SourceInvocation.native_shared_host_input
#print axioms SourceInvocation.native_shared_data_input
#print axioms SourceInvocation.native_shared_tail_input
#print axioms SourceInvocation.initialized_native_host_input
#print axioms SourceInvocation.initialized_native_data_input
#print axioms SourceInvocation.initialized_native_tail_input
#print axioms SourceInvocation.oldResult_native
#print axioms SourceInvocation.newResult_native
#print axioms SourceMoveGeometry.move_projectors
#print axioms SourceMoveGeometry.move_stage2_relative
#print axioms SourceMoveGeometry.move_relative
#print axioms SourceMoveGeometry.copy_stage2_relative
#print axioms SourceMoveGeometry.copy_relative
#print axioms SourceMoveGeometry.erase_relative
#print axioms SourceMoveGeometry.physicalStep_move
#print axioms SourceMoveGeometry.physicalStep_copy
#print axioms SourceMoveGeometry.matrix_run_eq
#print axioms SourceMoveGeometry.actual_matrix_run
#print axioms SourceMoveGeometry.nativeStep_move
#print axioms SourceMoveGeometry.nativeRoute_move
#print axioms SourceMoveGeometry.nativeStep_copy
#print axioms SourceInvocation.actualContract
#print axioms SourceInvocation.selected_call_completion
#print axioms SourceInvocation.selected_native_completion
#print axioms SourceInvocation.selected_data_formula
#print axioms SourceInvocation.selected_native_realization
#print axioms SourceInvocation.selected_native_clean
#print axioms SourceInvocation.selected_matrix_realization
#print axioms SourceInvocation.selected_original_matrix_realization
#print axioms SourceInvocation.selected_temporary_restoration

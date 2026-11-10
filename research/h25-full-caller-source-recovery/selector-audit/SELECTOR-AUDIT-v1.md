# Source selector fact audit

Exactly88 prior UNCLASSIFIED_SOURCE_SELECTOR rows are classified against graph SHA `388f1c2c379a718b98c1831d56796527fb9f14d85107971eb56650145415049f`. This is a source-fact delta; the frozen graph and its incomplete acceptance remain unchanged.

The token scanner overstates the number of unknown Python code selectors:15 call sites form five load pipelines, while many other rows are data reads, receiver or epoch interfaces, and latent native checks. Fixed paths and hashes do not establish actual authentication, reachability or admission.

| Source operation | Site rows |
| --- | ---: |
| AUTHENTICATED_PYTHON_SOURCE_LOAD_PIPELINE | 15 |
| CONTRACT_DATA_LOOKUP | 2 |
| DATA_READ | 15 |
| DISPATCH_FORWARDER | 1 |
| EXPORTED_AUTHORITY_INTERFACE | 11 |
| NATIVE_BINARY_CUSTODY_CHECK | 4 |
| NATIVE_EXTENSION_EXECUTION | 1 |
| ORIGINAL_EPOCH_INTERFACE | 6 |
| PINNED_FILE_CUSTODY_CHECK | 3 |
| PYTHON_SOURCE_LOAD_DISPATCH_WITH_PINNED_TARGETS | 3 |
| RECEIVER_BINDING_INTERFACE | 2 |
| RECEIVER_EXPORT_LOOKUP | 19 |
| RECEIVER_VALUE_LOOKUP | 1 |
| SOURCE_CODE_IDENTITY_CHECK | 5 |

The source-backed additional selector is significant: variant684–686 fixes `additional_source_pins` to `sealed_elf_profile_v2`, path `integration/sealed_elf_profile_v2.py`, SHA `89ed8c777e6b72af2d6a3595037e7e92385924c6087d88010a27192633391016`, before the dispatch at712. Its body and authority contract remain unresolved in the frozen pool.

| Site | Caller | Classification | Selector binding |
| --- | --- | --- | --- |
| full_driver:515 | initialize | PINNED_FILE_CUSTODY_CHECK | __file__ of selected full_driver, expected_root_sha256 passed to initialize |
| full_driver:582 | admit_provider | AUTHENTICATED_PYTHON_SOURCE_LOAD_PIPELINE | provider_path and expected_provider_sha256 from _entry argv[3]/argv[4]; selected provider pin9cbb7368... |
| full_driver:600 | admit_provider | AUTHENTICATED_PYTHON_SOURCE_LOAD_PIPELINE | provider_path and expected_provider_sha256 from _entry argv[3]/argv[4]; selected provider pin9cbb7368... |
| full_driver:602 | admit_provider | AUTHENTICATED_PYTHON_SOURCE_LOAD_PIPELINE | provider_path and expected_provider_sha256 from _entry argv[3]/argv[4]; selected provider pin9cbb7368... |
| full_driver:734 | load_control_module | NATIVE_BINARY_CUSTODY_CHECK | extension_path, expected_extension_sha256, module_name parameters of load_control_module |
| full_driver:748 | load_control_module | NATIVE_BINARY_CUSTODY_CHECK | extension_path, expected_extension_sha256, module_name parameters of load_control_module |
| full_driver:820 | _entry | AUTHENTICATED_PYTHON_SOURCE_LOAD_PIPELINE | driver_path/driver_sha from _entry argv[6]/argv[7]; selected full variant cdb14792... |
| full_driver:829 | _entry | AUTHENTICATED_PYTHON_SOURCE_LOAD_PIPELINE | driver_path/driver_sha from _entry argv[6]/argv[7]; selected full variant cdb14792... |
| full_driver:833 | _entry | AUTHENTICATED_PYTHON_SOURCE_LOAD_PIPELINE | driver_path/driver_sha from _entry argv[6]/argv[7]; selected full variant cdb14792... |
| group01_evidence_v1:94 | _read | DATA_READ | pin=copying.inspect(path,bound); callers select receipt.json,finite-controls.json,initial TCB/restoration/control receipts, group raw/validation files and build JSON |
| group01_evidence_v1:102 | _captured_call | RECEIVER_EXPORT_LOOKUP | finite callers184 restoration_contract_v1.validate_restoration and208 run_controls_v5.validate_all |
| native_packet:133 | require_execution_contract | CONTRACT_DATA_LOOKUP | literal 'status' key in SOURCE_EXECUTION_CONTRACT/FULL_EXECUTION_CONTRACT dictionaries |
| native_packet:137 | require_execution_contract | CONTRACT_DATA_LOOKUP | literal 'status' key in SOURCE_EXECUTION_CONTRACT/FULL_EXECUTION_CONTRACT dictionaries |
| native_packet:255 | prepare | PYTHON_SOURCE_LOAD_DISPATCH_WITH_PINNED_TARGETS | prepare loop251–255: areas/cache-validity/probe-native/{direct_controls.py,bootstrap_controls_v2.py,metadata_controls_v3.py}; names _h25_v2_{direct_controls,bootstrap_controls,metadata_controls} |
| original_build_provenance_v5:168 | authenticate_original_build | DATA_READ | row['original_receipt'] |
| original_build_provenance_v5:202 | authenticate_original_build | DATA_READ | row['attempt'] |
| original_build_provenance_v5:227 | authenticate_original_build | DATA_READ | row[stream] for stream in ('stdout','stderr') |
| original_build_provenance_v5:236 | authenticate_original_build | DATA_READ | row['journal'] |
| parent_closure_v1:154 | bind_receivers | SOURCE_CODE_IDENTITY_CHECK | source_policy[name] for already supplied modules[name]; exact receiver module names come from policy |
| parent_closure_v1:158 | bind_receivers | SOURCE_CODE_IDENTITY_CHECK | source_policy[name] for already supplied modules[name]; exact receiver module names come from policy |
| parent_completion_v1:121 | _receiver_gate_values | RECEIVER_VALUE_LOOKUP | seven specifications106–119: original_build_provenance_v5.{PARSER_CONFIGURATION,PARSER_EXECUTION_APPROVAL,PARSER_FUNDING}, variant_validation_v1.{VALIDATION_CONFIGURATION,VALIDATION_SOURCE_REVIEW,VALIDATION_EXECUTION,VALIDATION_FUNDING} |
| parent_completion_v1:294 | _stage | DATA_READ | plan['stage_manifest'] |
| parent_completion_v1:429 | make_parent | ORIGINAL_EPOCH_INTERFACE | epoch_parent_v5._entry_state |
| parent_completion_v1:438 | make_parent | DATA_READ | configuration['plan'] |
| parent_completion_v1:440 | make_parent | DATA_READ | configuration['receiver_policy'] |
| parent_completion_v1:444 | make_parent | RECEIVER_BINDING_INTERFACE | closure.bind_receivers(original_receivers, policy, errors); policy set equals literal REQUIRED_MODULES33 |
| parent_completion_v1:446 | make_parent | RECEIVER_EXPORT_LOOKUP | epoch_parent_v5.ParentEpoch |
| parent_completion_v1:447 | make_parent | RECEIVER_EXPORT_LOOKUP | epoch_schema_v5.need |
| parent_completion_v1:448 | make_parent | RECEIVER_EXPORT_LOOKUP | epoch_copy_v5.inspect |
| parent_completion_v1:450 | make_parent | RECEIVER_EXPORT_LOOKUP | h25_parent_supervisor.launch_contract |
| parent_completion_v1:453 | make_parent | ORIGINAL_EPOCH_INTERFACE | epoch_parent_v5._entry_state |
| parent_completion_v1:493 | make_parent | RECEIVER_EXPORT_LOOKUP | h25_parent_supervisor.install_subreaper |
| parent_completion_v1:555 | run_producer | ORIGINAL_EPOCH_INTERFACE | epoch_parent_v5.ParentEpoch.reserve_producer |
| parent_completion_v1:719 | _variant | DATA_READ | output + relative for relative in fixed VARIANT_FILES |
| parent_completion_v1:722 | _variant | RECEIVER_EXPORT_LOOKUP | variant_validation_v1.validate_variant_producer |
| parent_completion_v1:779 | accept_producer | DATA_READ | row['evidence_directory'] + '/stdout.raw' |
| parent_completion_v1:839 | accept_producer | ORIGINAL_EPOCH_INTERFACE | epoch_parent_v5.ParentCompletion |
| parent_completion_v1:842 | accept_producer | ORIGINAL_EPOCH_INTERFACE | epoch_parent_v5.ParentEpoch.accept_completed_producer |
| parent_completion_v1:862 | commit_exports | ORIGINAL_EPOCH_INTERFACE | epoch_parent_v5.ParentEpoch.commit_exports |
| probe_binding_v3:283 | _profile_files | PINNED_FILE_CUSTODY_CHECK | provider directory + RUNTIME-PROFILE.json; literal SHA ad0ec2aea01b83f97bdeafd9e9208360127fee870d024d353879b5ed99237109 |
| probe_binding_v3:292 | _audit_files | PINNED_FILE_CUSTODY_CHECK | files from _profile_files(): literal _RUNTIME_FILES plus runtime profile; load_probe also checks its binary separately |
| probe_binding_v3:471 | load_probe | NATIVE_BINARY_CUSTODY_CHECK | extension_path/expected_extension_sha256 supplied to load_probe |
| probe_binding_v3:476 | load_probe | NATIVE_EXTENSION_EXECUTION | injected _ROOT_EXEC(_BOOTSTRAP_CAPABILITY,native), native returned by _ROOT_CREATE at474 |
| probe_binding_v3:478 | load_probe | NATIVE_BINARY_CUSTODY_CHECK | extension_path/expected_extension_sha256 supplied to load_probe |
| v03_prefix_supervisor_v1:275 | _source_snapshot | DATA_READ | state['configuration']['plan'] |
| v03_prefix_supervisor_v1:310 | make_prefix_owner | DATA_READ | configuration['plan'] |
| v03_prefix_supervisor_v1:314 | make_prefix_owner | DATA_READ | configuration['receiver_policy'] |
| v03_prefix_supervisor_v1:321 | make_prefix_owner | RECEIVER_BINDING_INTERFACE | closure.bind_receivers(original_receivers, decoded configuration.receiver_policy, errors) |
| v03_prefix_supervisor_v1:323 | make_prefix_owner | RECEIVER_EXPORT_LOOKUP | v03_prefix_supervisor_v1.make_prefix_owner |
| v03_prefix_supervisor_v1:325 | make_prefix_owner | RECEIVER_EXPORT_LOOKUP | epoch_schema_v5.make_error_owner |
| v03_prefix_supervisor_v1:327 | make_prefix_owner | RECEIVER_EXPORT_LOOKUP | epoch_copy_v5.inspect |
| v03_prefix_supervisor_v1:329 | make_prefix_owner | RECEIVER_EXPORT_LOOKUP | parent_domain_v1.create_domain |
| v03_prefix_supervisor_v1:331 | make_prefix_owner | RECEIVER_EXPORT_LOOKUP | parent_completion_v1._snapshot_sources |
| v03_prefix_supervisor_v1:333 | make_prefix_owner | RECEIVER_EXPORT_LOOKUP | v03_prefix_derivation_v1.verify_configured_prefix |
| v03_prefix_supervisor_v1:342 | make_prefix_owner | RECEIVER_EXPORT_LOOKUP | h25_parent_supervisor.launch_contract |
| v03_prefix_supervisor_v1:344 | make_prefix_owner | RECEIVER_EXPORT_LOOKUP | h25_parent_supervisor.install_subreaper |
| v03_prefix_supervisor_v1:399 | make_prefix_owner | SOURCE_CODE_IDENTITY_CHECK | case['root_source'] |
| v03_prefix_supervisor_v1:401 | make_prefix_owner | SOURCE_CODE_IDENTITY_CHECK | case['driver_source'] |
| v03_prefix_supervisor_v1:403 | make_prefix_owner | SOURCE_CODE_IDENTITY_CHECK | configuration['original_variant'] |
| v03_prefix_supervisor_v1:407 | make_prefix_owner | DATA_READ | case['gate_values'] |
| v03_prefix_supervisor_v1:409 | make_prefix_owner | RECEIVER_EXPORT_LOOKUP | v03_source_refusal_observer_v1._decode |
| v03_prefix_supervisor_v1:711 | _capture | DATA_READ | copied source stdout/stderr and exact expected output receipt files |
| v03_prefix_supervisor_v1:719 | _capture | RECEIVER_EXPORT_LOOKUP | v03_source_refusal_observer_v1._decode |
| v03_prefix_supervisor_v1:736 | _capture | RECEIVER_EXPORT_LOOKUP | v03_source_refusal_observer_v1.corroborate_positive |
| v03_prefix_supervisor_v1:743 | _capture | RECEIVER_EXPORT_LOOKUP | v03_source_refusal_observer_v1.corroborate_complete_refusal |
| variant_driver_v1:390 | _initial_native_tcb | AUTHENTICATED_PYTHON_SOURCE_LOAD_PIPELINE | areas/cache-validity/probe-native/native_tcb_v1.py relative to stage; literal SHA 865943df5cfdbf9383362d7fb2b76c6d0fd895cf0a0e20d550a26b579606b5d7 |
| variant_driver_v1:397 | _initial_native_tcb | AUTHENTICATED_PYTHON_SOURCE_LOAD_PIPELINE | areas/cache-validity/probe-native/native_tcb_v1.py relative to stage; literal SHA 865943df5cfdbf9383362d7fb2b76c6d0fd895cf0a0e20d550a26b579606b5d7 |
| variant_driver_v1:399 | _initial_native_tcb | AUTHENTICATED_PYTHON_SOURCE_LOAD_PIPELINE | areas/cache-validity/probe-native/native_tcb_v1.py relative to stage; literal SHA 865943df5cfdbf9383362d7fb2b76c6d0fd895cf0a0e20d550a26b579606b5d7 |
| variant_driver_v1:407 | _initial_native_tcb | AUTHENTICATED_PYTHON_SOURCE_LOAD_PIPELINE | areas/cache-validity/probe-native/native_tcb_controls_v1.py relative to stage; literal SHA 63b1804caa7f89915662a1424f788c3becad13520e1f63212a338fb45aaa2c5a |
| variant_driver_v1:413 | _initial_native_tcb | AUTHENTICATED_PYTHON_SOURCE_LOAD_PIPELINE | areas/cache-validity/probe-native/native_tcb_controls_v1.py relative to stage; literal SHA 63b1804caa7f89915662a1424f788c3becad13520e1f63212a338fb45aaa2c5a |
| variant_driver_v1:415 | _initial_native_tcb | AUTHENTICATED_PYTHON_SOURCE_LOAD_PIPELINE | areas/cache-validity/probe-native/native_tcb_controls_v1.py relative to stage; literal SHA 63b1804caa7f89915662a1424f788c3becad13520e1f63212a338fb45aaa2c5a |
| variant_driver_v1:475 | _initial_cold_authority | AUTHENTICATED_PYTHON_SOURCE_LOAD_PIPELINE | areas/cache-validity/cold_authority_v7.py relative to stage; literal SHA 2a941111bdfd91037dfcbc5552aced004809240a7e2b43bfbce39fb35798af39 |
| variant_driver_v1:482 | _initial_cold_authority | AUTHENTICATED_PYTHON_SOURCE_LOAD_PIPELINE | areas/cache-validity/cold_authority_v7.py relative to stage; literal SHA 2a941111bdfd91037dfcbc5552aced004809240a7e2b43bfbce39fb35798af39 |
| variant_driver_v1:484 | _initial_cold_authority | AUTHENTICATED_PYTHON_SOURCE_LOAD_PIPELINE | areas/cache-validity/cold_authority_v7.py relative to stage; literal SHA 2a941111bdfd91037dfcbc5552aced004809240a7e2b43bfbce39fb35798af39 |
| variant_driver_v1:488 | _initial_cold_authority | EXPORTED_AUTHORITY_INTERFACE | cold_authority_v7.capture_authority(root,cap,api) |
| variant_driver_v1:566 | module | PYTHON_SOURCE_LOAD_DISPATCH_WITH_PINNED_TARGETS | index0; exact six EARLY_INTEGRATION_SOURCE_PINS literal at528: adapters,cold_build_evidence,native_packet,data_adapters,guarded_adapters_v4,_h25_data_cache |
| variant_driver_v1:599 | _vdispatch | DISPATCH_FORWARDER | index,*args,**kwargs; visible consumer sites605 index6,606 index1,712 index0 |
| variant_driver_v1:605 | _vinvoke | EXPORTED_AUTHORITY_INTERFACE | _vinvoke(name,export,*args): index6(handle), then index1(handle,export,*args) |
| variant_driver_v1:606 | _vinvoke | EXPORTED_AUTHORITY_INTERFACE | _vinvoke(name,export,*args): index6(handle), then index1(handle,export,*args) |
| variant_driver_v1:712 | _variant_main | PYTHON_SOURCE_LOAD_DISPATCH_WITH_PINNED_TARGETS | exact one row sealed_elf_profile_v2,integration/sealed_elf_profile_v2.py,SHA89ed8c777e6b72af2d6a3595037e7e92385924c6087d88010a27192633391016 |
| variant_driver_v1:720 | _variant_main | EXPORTED_AUTHORITY_INTERFACE | native_packet._fresh |
| variant_driver_v1:722 | _variant_main | EXPORTED_AUTHORITY_INTERFACE | native_packet._preflight |
| variant_driver_v1:726 | _variant_main | EXPORTED_AUTHORITY_INTERFACE | native_packet._dependencies |
| variant_driver_v1:754 | _variant_main | EXPORTED_AUTHORITY_INTERFACE | cold_build_evidence.run |
| variant_driver_v1:782 | _variant_main | EXPORTED_AUTHORITY_INTERFACE | sealed_elf_profile_v2.admit_service_elf |
| variant_driver_v1:788 | _variant_main | EXPORTED_AUTHORITY_INTERFACE | native_packet._preflight |
| variant_driver_v1:790 | _variant_main | EXPORTED_AUTHORITY_INTERFACE | native_packet._dependencies |
| variant_driver_v1:799 | _variant_main | EXPORTED_AUTHORITY_INTERFACE | native_packet._fresh |

All88 entries in the JSON retain exact call text, argument expressions, source hash/path, supporting source lines and a concrete remaining obligation. Known Root load edges and33 receiver requirements are reused. Missing receiver/project bodies remain missing; a receiver lookup does not import or create them. Historical prefix operations are separately marked and cannot stand in for full completion.

No source module or extracted definition was imported, compiled or executed. No control, protected run, native/compiler/decoder operation, target inspection or acquisition was performed. Original43.5%,zero added original credit,C07/fullC05/fullV03/runtime false and OPEN_NOT_ZERO costs remain unchanged.

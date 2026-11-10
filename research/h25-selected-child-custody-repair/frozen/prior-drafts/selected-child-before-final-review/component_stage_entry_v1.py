"""Fixed genuine-Root driver, before-target identity custody then unit main().

No post-fault acquisition is added. Original main/context/ports/RAW-before-ORACLE
bodies remain unchanged. The extra source prelude and its actual parent release channel
need independent configuration/profile/source/resource admission and are paid.
"""
import os
import time
import sys
import types
import epoch_schema_v5 as schema
import epoch_copy_v5 as copying
import parent_completion_v1 as parent
import h25_parent_supervisor as supervisor
import component_control_root_v1 as component

import epoch_schema_v5
import epoch_copy_v5
import epoch_parent_v5
import epoch_stop_v5
import original_build_provenance_v5
import h25_parent_supervisor
import parent_closure_v1
import parent_domain_v1
import parent_completion_v1
import group01_evidence_v1
import group01_original_predicates_v1
import receipt_contract_v1
import native_field_controls_v1
import transport_controls_v1
import collector_controls_v1
import elf_literal_fixture_v1
import elf_controls_v1
import provider_controls_v1
import run_pure_controls_v1
import elf_literal_fixture_v2
import elf_extended_controls_v2
import run_pure_controls_v2
import restoration_contract_v1
import loader_model_controls_v1
import driver_model_body_sources_v3
import root_model_body_sources_v3
import loader_model_controls_v3
import group_evidence_v5
import close_model_controls_v5
import projection_model_controls_v5
import run_controls_v5
import variant_validation_v1
import sealed_elf_profile_v2
import persistent_replay_v1
import replay_receiver_closure_v1
import policy_parent_domain_v1
import policy_receiver_closure_v1
import policy_process_domain_v1
import component_receiver_closure_v1
import component_control_root_v1
import configured_inverse_v2
import selected_child_bindings_v1 as selected_bindings

START_CONFIGURATION = None
_PRELUDE = []
_PRELUDE_ERRORS = [None]


def main():
    error_owner = schema.make_error_owner()
    guard_state = {'phase':'PRETARGET','primary':[None],'secondary':[],
                   'request':None,'request_pin':None,'ack':None,'ack_pin':None,'consume_pin':None}
    try:
        schema.need(not _PRELUDE, 'pre-target stage attempt already consumed')
        _PRELUDE.append((error_owner,guard_state))  # one shot before fallible work
        schema.need(START_CONFIGURATION is None and len(sys.argv) == 5 and
            sys.argv[1] == '--output' and sys.argv[3] == '--lanes',
            'actual fixed Root tail and unconfigured entry source required')
        modules = {name: sys.modules[name] for name in component._REQUIRED}
        schema.need(all(type(module) is types.ModuleType for module in modules.values()),
            'actual imported selected child modules required')
        c = selected_bindings.prepare_selected_child(sys.argv[4], modules)
        schema.exact(c, ('marker_path', 'case_id', 'context_id', 'unit_id', 'mode',
                        'guard', 'publication_admission', 'publication_root'))
        schema.path(c['marker_path']); schema.text(c['case_id'], 256)
        schema.label(c['context_id']); schema.text(c['unit_id'], 128)
        schema.choice(c['mode'], ('normal', 'optimized'))
        schema.blob(c['publication_admission'], schema.RECORD_BYTES)
        schema.path(c['publication_root'])
        admission_raw = copying.read_verified(c['publication_admission'],
            schema.RECORD_BYTES, error_owner=error_owner)
        admission = schema.decode(admission_raw)
        schema.need(admission['source_sha256'] == c['guard']['supervisor_source']['sha256'],
                    'child publication source is not the original fixed supervisor')
        # A fresh child needs its own actual native binding. The admission pin
        # is part of the source-authenticated entry configuration and its full
        # immutable inverse, never a replacement authority supplied by a child.
        supervisor.prepare_atomic_publication(supervisor.Path(c['publication_root']), admission)
        _PRELUDE.append(supervisor._publication_binding())
        schema.need(component.CONTEXT_CONFIGURATION['unit_id'] == c['unit_id'] and
            component.CONTEXT_CONFIGURATION['mode'] == c['mode'], 'exact configured unit context differs')
        process = supervisor.proc(os.getpid())
        schema.need(type(process) is dict and process['pid'] == os.getpid() and
            type(process['start_ticks']) is int and process['start_ticks'] > 0,
            'pre-target actual Root generation unavailable')
        marker = dict(c, schema='h25-component-pretarget-identity-v1', process=process,
                      actual_context=component.CONTEXT_CONFIGURATION, component_source_path=component.__file__)
        schema.need(type(c['guard']) is dict and
            all(type(c['guard'][k]) is str and c['guard'][k] == c[k]
                for k in ('case_id','context_id','unit_id','mode')) and
            c['guard']['marker_path'] == c['marker_path'] and
            c['guard']['component_source']['path'] == component.__file__ and
            c['guard']['entry_source']['path'] == __file__ and
            c['guard']['context_sha256'] == supervisor.hashlib.sha256(schema.canonical(component.CONTEXT_CONFIGURATION)).hexdigest(),
            'pre-target actual source/context guard binding differs')
        raw = schema.canonical(marker)
        pin = copying.write_once(c['marker_path'], raw, error_owner=error_owner)
        _PRELUDE.append((marker, pin))
        supervisor.child_guard_wait(c['guard'], pin, process, guard_state)
        schema.need(guard_state['phase'] == 'TARGET_RELEASED', 'actual parent release required before target')
    except BaseException as error:
        if guard_state['primary'][0] is None:
            guard_state['primary'][0] = error
        if parent._UNKNOWN_OWNER['primary'][0] is None:
            parent._UNKNOWN_OWNER['primary'][0] = error
        parent._UNKNOWN_OWNER['quarantine'][0] = True
        guard_state['phase'] = 'STOP'
        _PRELUDE_ERRORS[0] = error
        raise
    return component.main()


if __name__ == '__main__':
    main()

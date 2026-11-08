"""Fixed genuine-Root driver, before-target identity custody then unit main().

No post-fault acquisition is added. Original main/context/ports/RAW-before-ORACLE
bodies remain unchanged. The extra source prelude and its actual parent release channel
need independent configuration/profile/source/resource admission and are paid.
"""
import os
import time
import epoch_schema_v5 as schema
import epoch_copy_v5 as copying
import parent_completion_v1 as parent
import h25_parent_supervisor as supervisor
import component_control_root_v1 as component

START_CONFIGURATION = None
_PRELUDE = []
_PRELUDE_ERRORS = []


def main():
    error_owner = schema.make_error_owner()
    guard_state = {'phase':'PRETARGET','primary':[None],'secondary':[],
                   'request':None,'request_pin':None,'ack':None,'ack_pin':None,'consume_pin':None}
    try:
        schema.need(not _PRELUDE, 'pre-target stage attempt already consumed')
        _PRELUDE.append((error_owner,guard_state))  # one shot before fallible work
        schema.exact(START_CONFIGURATION, ('marker_path', 'case_id', 'context_id', 'unit_id', 'mode', 'guard'))
        c = START_CONFIGURATION
        schema.path(c['marker_path']); schema.text(c['case_id'], 256)
        schema.label(c['context_id']); schema.text(c['unit_id'], 128)
        schema.choice(c['mode'], ('normal', 'optimized'))
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
        _PRELUDE_ERRORS.append(error)
        if guard_state['primary'][0] is None:
            guard_state['primary'][0] = error
        guard_state['phase'] = 'STOP'
        if parent._UNKNOWN_OWNER['primary'][0] is None:
            parent._UNKNOWN_OWNER['primary'][0] = error
        parent._UNKNOWN_OWNER['quarantine'][0] = True
        raise
    return component.main()

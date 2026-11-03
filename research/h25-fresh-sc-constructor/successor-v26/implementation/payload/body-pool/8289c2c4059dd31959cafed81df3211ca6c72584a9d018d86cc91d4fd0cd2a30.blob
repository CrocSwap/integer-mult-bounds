"""Concrete source-bound receiver for actual original-parent owned child streams.

Only the parent calls this after actual domain closure, fsync and complete file
custody. This module does not accept child PASS fields, callback predicates, or a
serialized completion capability. All original return types remain exact.
"""
import ast
import re
import epoch_schema_v5 as schema
import epoch_copy_v5 as copying
import negative_wide_codec_v2 as wire
import typed_codec_v2 as codec
import run_controls_v1 as controls
import restoration_contract_v1 as restoration
import inert_byte_v2 as inert

GROUPS = ('02','03','04','07','08','09','10','11','12','13','14','15','16')
MAX_RAW = 64 * 1024 * 1024
ROOT_SHA256 = 'f5a2d33f2b4d3651f214156a0e7094c2bb516ce2d5ab7698d18c11f98f35dee0'
ERRORS = {
 '08':('Field complete source-controlled native import history differs','original-history-before-ordinary',0,0,0,(0,0)),
 '09':('unexpected/missing loaded map','original-loaded-maps',0,0,0,(1,0)),
 '10':('unexpected/missing loaded map','original-loaded-maps',0,0,0,(1,0)),
 '11':('Loaded map history changed before symbol resolution','original-symbols-history-before-resolution',0,0,0,(1,1)),
 '12':('h25-negative-original-import-audit','create_dynamic',1,0,0,(1,1)),
 '13':('H25 negative pyinit fixture: deliberate failure after module definition initialization','create_dynamic',1,0,0,(1,1)),
 '14':('H25 negative exec fixture: deliberate failure after original initialization','exec_dynamic',1,1,0,(1,1)),
 '15':('Field binding requires exact original primitive packet','first-native-bind',1,1,1,(1,1)),
 '16':('h25-negative-original-import-interruption','create_dynamic',1,0,0,(1,1)),
}
COMMON_NAMES = ('START','initial-native-tcb','initial-five-original-return','initial-restoration','cold-authority-captured',
 'claim-return','source-custody','ordinary-selected-static-elf','preordinary-import-policy','preordinary-native-tcb',
 'map-file-custody','original-preflight','actual-history-before-rejection','history-setup','actual-maps','maps-admission',
 'actual-provider-requests','actual-symbols','provider-admission','ordinary-bootstrap-close','selected-static-elf',
 'sealed-image','loader-entered','service-create-return','service-exec-return','actual-abi','actual-bound-status',
 'target-error','target-site','actual-failed-status','actual-bind-cleanup-error','actual-bind-cleanup-return',
 'import-audit-events','inert-byte-proof','actual-hardlink','same-size-mutation','actual-mutated-file',
 'path-replacement','actual-entry-after-mutation','full202-original-return','full202-actual-fixtures',
 'terminal-service-status','root-terminal-counters','END','FINAL-CUSTODY','role-header-begin','role-header-finish',
 'retained-ownership')
HISTORY_NAMES = ('authenticated-input','maps-before','maps-after','dlopen-attempt','dlopen-return','dlsym-return',
 'original-control-load-attempt','original-control-load-return','sysmodules-insert','sysmodules-remove-retained',
 'alias-retained-fd','procfd-name-witness','alias-value','soname-name-witness','soname-leaf-value','soname-middle-value',
 'global-interposition-witness','global-own-value','global-leaf-own-value','global-middle-relocation-value',
 'dependency-root-witness','actual-native-audit')


def frames(raw):
    schema.need(type(raw) is bytes and 0 < len(raw) <= MAX_RAW,'negative actual bounded raw stdout')
    cursor,rows = 0,[]
    while cursor < len(raw):
        schema.need(len(rows) < 1024 and cursor+8 <= len(raw),'negative frame capacity/truncation')
        count = int.from_bytes(raw[cursor:cursor+8],'big');cursor += 8
        schema.need(0 < count <= 32*1024*1024 and cursor+count <= len(raw),'negative raw frame bytes')
        encoded = raw[cursor:cursor+count];cursor += count
        value = wire.decode(encoded,32*1024*1024)
        schema.need(wire.encode(value,32*1024*1024) == encoded and type(value) is tuple and len(value) == 4 and
                    value[0] == 'h25-negative-raw-v2' and type(value[1]) is int and value[1] == len(rows) and
                    type(value[2]) is str,'negative exact canonical typed frame/sequence')
        name = value[2]
        schema.need(name in COMMON_NAMES or name.startswith('history.') and name[8:] in HISTORY_NAMES,
                    'negative unexpected/fatal/unknown raw topic')
        rows.append((name,value[3]))
    schema.need(rows[0][0] == 'START' and rows[-1][0] == 'FINAL-CUSTODY','negative start/final custody frame order')
    return tuple(rows)


def _one(rows,name):
    found = tuple(value for key,value in rows if key == name)
    schema.need(len(found) == 1,'negative exact singleton topic: '+name)
    return found[0]


def _absent(rows,names):
    schema.need(not any(key in names for key,value in rows),'negative forbidden operation observed')


def _before(rows,first,last):
    a = tuple(index for index,(name,value) in enumerate(rows) if name == first)
    b = tuple(index for index,(name,value) in enumerate(rows) if name == last)
    schema.need(a and b and max(a) < min(b),'negative required actual source ordering')


def _native_trace(value,message,row,group):
    schema.need(type(value) is tuple and len(value) == 2 and value[0] is True,'negative original exact exception type')
    trace = value[1]
    schema.need(type(trace) is dict and trace.get('schema') == 'h25-gap-native-error-trace-v1' and
                trace.get('complete') is True and trace.get('foreign_formatting') is False and
                type(trace.get('objects')) is tuple and len(trace['objects']) == 1,'negative full original primary graph')
    error = trace['objects'][0]
    schema.need(codec.equal(error['args'],(message,)) and error['cause_id'] is None and error['context_id'] is None and
                type(error['frames']) is tuple and error['frames'] and error['object_id'] == trace['root_object_id'],
                'negative exact first native error/args/chain')
    final = error['frames'][-1]
    if group == '08':
        schema.need(final['filename'] == row['control_port_source']['path'] and final['name'] == '_need' and
                    len(error['frames']) >= 2 and error['frames'][-2]['name'] == '_field_admit_history',
                    'negative original history predicate traceback')
    elif group in ('09','10'):
        schema.need(final['name'] == '_need' and len(error['frames']) >= 2 and
                    error['frames'][-2]['name'] == 'admit_loaded_maps','negative original loaded-map predicate traceback')
    else:
        schema.need(final['filename'] == row['runtime_source']['path'] and
                    final['name'] == ('_import_observer' if group in ('12','16') else
                                      ('bootstrap' if group == '11' else 'load_service')),
                    'negative actual original native callsite source')
    return trace


def _map_rows(raw):
    schema.need(type(raw) is bytes and len(raw) <= 8388608,'negative complete actual proc-map bytes')
    result = []
    for line in raw.splitlines():
        columns = line.split(None,5)
        schema.need(len(columns) >= 5,'negative actual proc-map row')
        extent,permissions,offset,device,inode = columns[:5]
        start,end = extent.split(b'-');major,minor = device.split(b':')
        values = (int(start,16),int(end,16),permissions,int(offset,16),int(major,16),int(minor,16),int(inode))
        schema.need(values[0] < values[1] and len(permissions) == 4,'negative actual map extent/permissions')
        result.append(values+(columns[5] if len(columns) == 6 else b'',))
    return tuple(result)


def _history(rows,group,launch,subcase):
    setup = _one(rows,'history-setup')
    schema.need(type(setup) is tuple and len(setup) == 2 and setup[0] == subcase and
                type(setup[1]) is tuple and len(setup[1]) == 8,'negative actual history setup shape')
    observed = setup[1]
    schema.need(observed[0:2] == (group,subcase) and type(observed[2]) is tuple and type(observed[3]) is tuple and
                type(observed[4]) is tuple and len(observed[4]) == 8 and
                codec.equal(observed[5],(False,)*8) and observed[6] is False and observed[7] is False,
                'negative history retained ownership/unknown handle')
    actual_records = tuple((key[8:],value) for key,value in rows if key.startswith('history.'))
    schema.need(wire.equal(actual_records,observed[2]),'negative retained history return differs from original raw chronology')
    before = _map_rows(_one(rows,'history.maps-before'))
    after = _map_rows(_one(rows,'history.maps-after'))
    schema.need(all(row in after for row in before),'negative setup removed an original mapped row')
    added = tuple(row for row in after if row not in before)
    inputs = tuple(value for key,value in rows if key == 'history.authenticated-input')
    expected_roles = {'08':('production',),'10':('global','leaf','middle'),'11':('leaf','middle','root')}.get(group,
                     ('leaf','middle') if subcase == 'soname-name' else ('alias',))
    schema.need(tuple(value[0] for value in inputs) == expected_roles,'negative actual history fixture input order')
    for role,pin in inputs:
        schema.blob(pin)
        inode = pin['identity']['inode']
        schema.need(any(row[6] == inode for row in added),'negative actual fixture inode was not newly mapped')
    if group == '08':
        load = _one(rows,'history.original-control-load-return')
        removed = _one(rows,'history.sysmodules-remove-retained')
        schema.need(type(load) is tuple and type(removed) is tuple,'negative actual retained module facts')
        _one(rows,'history.sysmodules-insert')
        _one(rows,'history.original-control-load-attempt')
        _before(rows,'history.original-control-load-return','actual-history-before-rejection')
    elif subcase == 'procfd-name':
        witness = _one(rows,'history.procfd-name-witness')
        schema.need(type(witness) is tuple and len(witness) == 5 and witness[0] == witness[1] and witness[2] == witness[3],
                    'negative actual procfd/path handle and symbol equality')
        schema.need(type(_one(rows,'history.alias-value')) is int and _one(rows,'history.alias-value') == 11,
                    'negative genuine alias native return')
    elif subcase == 'soname-name':
        witness = _one(rows,'history.soname-name-witness')
        schema.need(type(witness) is tuple and len(witness) == 5 and witness[0] == witness[1] and witness[3] == witness[4],
                    'negative actual SONAME handle and symbol equality')
        schema.need(codec.equal((_one(rows,'history.soname-leaf-value'),_one(rows,'history.soname-middle-value')),(17,17)),
                    'negative genuine SONAME/DT_NEEDED native return')
    elif group == '10':
        witness = _one(rows,'history.global-interposition-witness')
        schema.need(type(witness) is tuple and len(witness) == 4 and witness[0] == witness[2] and witness[0] != witness[1],
                    'negative actual global/leaf distinct symbol provenance')
        schema.need(codec.equal(tuple(_one(rows,name) for name in ('history.global-own-value','history.global-leaf-own-value',
                    'history.global-middle-relocation-value')),(29,17,29)),'negative actual global interposition values')
    else:
        _one(rows,'history.dependency-root-witness')
        _before(rows,'maps-admission','history.maps-before')
        _before(rows,'history.maps-after','target-error')
    return (subcase,tuple((role,pin['sha256'],pin['identity']['inode']) for role,pin in inputs),len(added))


def validate_owned_negative(raw,launch,row,terminal,receivers,error_owner):
    rows = frames(raw)
    group = launch['group'];schema.choice(group,GROUPS)
    start = _one(rows,'START')
    schema.need(type(start) is tuple and len(start) == 6 and wire.equal(start[0],launch) and
                start[1] == row['source_configuration_sha256'] and start[2] == schema.sha(schema.canonical(launch)) and
                type(start[4]) is int and start[4] == terminal['root'][0] and start[5] == ROOT_SHA256,
                'negative actual parent launch/context/PID/source binding')
    _before(rows,'initial-native-tcb','initial-five-original-return')
    _before(rows,'initial-five-original-return','initial-restoration')
    _before(rows,'initial-restoration','cold-authority-captured')
    _before(rows,'cold-authority-captured','claim-return')
    original_claim = _one(rows,'claim-return')
    schema.need(type(original_claim) is tuple and len(original_claim) == 2,'negative exact consumed claim return')
    manifest,claim = original_claim
    schema.need(claim['group'] == group and claim['generation'] == launch['generation'],'negative claim group/generation')
    initial,old_five,restored = (_one(rows,name) for name in ('initial-native-tcb','initial-five-original-return','initial-restoration'))
    child_source = copying.read_verified(row['child_source'],schema.RECORD_BYTES,error_owner=error_owner)
    child_config = next(ast.literal_eval(node.value) for node in ast.parse(child_source).body if type(node) is ast.Assign and
        len(node.targets) == 1 and type(node.targets[0]) is ast.Name and node.targets[0].id == 'CHILD_CONFIGURATION')
    restoration.validate_restoration(initial,old_five,restored,child_config['initial_native_files'],
        child_config['hashlib_origin'],ROOT_SHA256,len(child_config['initial_native_files']))
    end = _one(rows,'END')
    schema.need(type(end) is tuple and len(end) == 22 and end[0] == 'h25-negative-child-end-v2' and
                end[1:6] == (group,launch['mode'],launch['generation'],launch['launch_nonce'],terminal['root'][0]) and
                codec.equal(end[15],(False,)*32) and end[16] is False and end[17] is False and
                end[21] == 'RAW_COMPLETE_PARENT_ORACLE_REQUIRED','negative terminal source/process/ownership envelope')
    final = _one(rows,'FINAL-CUSTODY')
    schema.need(type(final) is tuple and len(final) == 5 and final[:2] == (row['source_configuration_sha256'],ROOT_SHA256) and
                type(final[2]) is int and final[2] == len(rows)-1 and final[4] is False,'negative final source raw boundary')
    _before(rows,'END','FINAL-CUSTODY')
    history = None
    if group in ERRORS:
        message,site,loads,execs,binds,helpers = ERRORS[group]
        schema.need(codec.equal(_one(rows,'target-site'),(group,site,loads,execs,binds,helpers)) and
                    end[6:12] == ('TARGET_RAISED',site,loads,execs,binds,helpers),'negative original first-stop/call census')
        _native_trace(_one(rows,'target-error'),message,row,group)
        _before(rows,'target-error','target-site')
        if group in ('08','09','10','11'):
            _absent(rows,('loader-entered','selected-static-elf','service-create-return','service-exec-return','actual-abi','actual-bound-status'))
            schema.need(end[13] is False and end[14] is False and end[20] is None,'negative history stop must precede service')
            subcase = 'retained-origin' if group == '08' else ('dependency-drift' if group == '11' else
                      ('global-interposition' if group == '10' else row['expected_subcase']))
            history = _history(rows,group,launch,subcase)
        else:
            schema.need(end[13] is True and end[14] is (group in ('14','15')) and end[20] is not None,
                        'negative actual failure module/image retention')
            _before(rows,'loader-entered','target-error')
            _one(rows,'loader-entered')
        if group == '15':
            schema.need(codec.equal(_one(rows,'actual-failed-status'),(1,4,0,1,0)),
                        'negative authentic first-bind failure state')
            cleanup = _one(rows,'actual-bind-cleanup-error')
            schema.need(type(cleanup) is tuple and cleanup[0] is True and
                        cleanup[1]['objects'][0]['args'] == ('Field close lacks the original owner token',),
                        'negative captured original partial-bind cleanup error')
    else:
        _absent(rows,('target-error','target-site','actual-failed-status','actual-bind-cleanup-error'))
        schema.need(end[8:12] == (1,1,1,(1,1)) and end[13:15] == (True,True),'negative actual successful service once-only census')
        schema.need(codec.equal(_one(rows,'actual-abi'),(1,7,0x030C03F0,8,2)) and
                    codec.equal(_one(rows,'actual-bound-status'),(1,1,0,1,0)) and
                    codec.equal(_one(rows,'terminal-service-status'),(1,3,0,1,0)),
                    'negative actual ABI/bind/terminal lifecycle')
        if group in ('02','03','04'):
            schema.need(end[6] == 'PRIVATE_MUTATION_OBSERVED' and end[12] == 1,'negative exact one real post-mutation entry')
            entry = _one(rows,'actual-entry-after-mutation')
            schema.need(type(entry) is tuple and len(entry) == 3 and type(entry[0]) is int and
                        type(entry[1]) is int and entry[0] == entry[1] and type(entry[2]) is int and entry[2] == 1,
                        'negative original getter/id entry oracle')
            production = next(copy for copy in claim['copies'] if copy['role'] == 'production')
            if group in ('02','03'):
                original = copying.read_verified(production['source'],schema.FILE_BYTES,error_owner=error_owner)
                proof = inert.derive(original,production['source']['sha256'])
                schema.need(codec.equal(_one(rows,'inert-byte-proof'),proof),'negative independent original byte layout proof')
                actual = _one(rows,'same-size-mutation')
                schema.need(actual[0] == group and type(actual[1]) is int and actual[1] == 1 and codec.equal(actual[2],proof) and
                            actual[3][:3] == actual[4][:3] and actual[3][6] == actual[4][6] == len(original),
                            'negative actual same-size same-inode single-byte write')
                changed = original[:proof['offset']]+proof['replacement_byte']+original[proof['offset']+1:]
                modified = _one(rows,'actual-mutated-file')
                schema.need(modified[0] == len(original) and modified[1] == schema.sha(changed),'negative complete changed file hash')
                if group == '03':_one(rows,'actual-hardlink')
            else:_one(rows,'path-replacement')
        else:
            schema.need(end[6] == 'FULL202_OBSERVED','negative full202 completion phase')
            result = _one(rows,'full202-original-return')
            controls.validate_all(result,launch['mode'])
            schema.need(codec.equal(_one(rows,'full202-actual-fixtures'),(41,41)),'negative complete actual fixture census')
    counters = _one(rows,'root-terminal-counters')
    schema.need(type(counters) is dict and all(type(value) is int for value in counters.values()),'negative actual original counters')
    schema.need(counters['load_calls'] == (0 if group == '08' else 1) and
                counters['control_module_creations'] == (1 if group == '08' else 0),
                'negative actual original Root load/control count')
    return ('h25-negative-source-bound-validation-v2',group,launch['mode'],schema.sha(raw),len(rows),end,
            history,169 if group == '07' else 0,33 if group == '07' else 0,
            'ELF41_66_76_AND_OTHER_NATIVE24_REQUIREMENTS_NOT_INFERRED')

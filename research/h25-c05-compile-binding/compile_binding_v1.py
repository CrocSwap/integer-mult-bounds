"""Pure source-pinned projection of the original two GCC compile bindings.

This module performs no I/O and imports/executes no original source. It does not
construct an effective GCC configuration or authenticate a parent/namespace.
Original source, separately owned output, parent cwd and compiler cwd are bound
independently. No operand spelling is normalized, rewritten or inferred from cwd.
"""
from __future__ import annotations
import ast
import hashlib
import json
import re

SOURCE_PINS = {
    'variant_driver': ('cdb1479253358508088f8aa0e1e92e6c75ffcc127e54552698598a02de061254', 41337),
    'parent_completion': ('d4ee1b7ce4a42b73261984ffb1b9ceb5bb0165223e04a253588f83b99f6981a5', 54168),
    'cold_build_evidence': ('aa0a315110e031e19291970c9611fe5e0f91465fa20eaec51e81186099563f78', 16463),
}
CAPS = {'rows': 512, 'file_bytes': 64*1024*1024, 'capture_bytes': 256*1024*1024,
        'depth': 24, 'nodes': 65536, 'string': 8192, 'text': 524288,
        'container': 1024, 'raw': 1048576}


class BindingError(ValueError):
    pass


def _need(condition, message):
    if not condition:
        raise BindingError(message)


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    nodes = text = 0
    def walk(item, depth):
        nonlocal nodes, text
        nodes += 1
        _need(depth <= CAPS['depth'] and nodes <= CAPS['nodes'], 'plain structural bound')
        if item is None or type(item) is bool:
            return
        if type(item) is int:
            _need(-(1<<64) <= item < (1<<64), 'plain integer bound')
        elif type(item) is str:
            text += len(item)
            _need(len(item) <= CAPS['string'] and text <= CAPS['text'], 'plain text bound')
        elif type(item) in (list, dict):
            _need(len(item) <= CAPS['container'], 'plain container bound')
            if type(item) is list:
                for child in item: walk(child, depth+1)
            else:
                for key, child in item.items():
                    _need(type(key) is str, 'plain key type')
                    walk(key, depth+1); walk(child, depth+1)
        else:
            raise BindingError('non-plain input')
    walk(value, 0)
    raw = (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False)+'\n').encode('ascii')
    _need(len(raw) <= CAPS['raw'], 'plain raw-record bound')
    return raw


def _same(left, right):
    return canonical(left) == canonical(right)


def _decode(raw, expected_sha256, kind):
    _need(type(raw) is bytes and 0 < len(raw) <= CAPS['raw'], kind+' raw bound/type')
    _need(type(expected_sha256) is str and re.fullmatch('[0-9a-f]{64}', expected_sha256), kind+' pin shape')
    _need(_sha(raw) == expected_sha256, kind+' byte authentication mismatch')
    def pairs(rows):
        result = {}
        for key, value in rows:
            _need(key not in result, kind+' duplicate JSON key')
            result[key] = value
        return result
    try:
        result = json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda _: (_ for _ in ()).throw(BindingError('JSON constant')))
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise BindingError(kind+' invalid bounded JSON') from error
    canonical(result)
    _need(type(result) is dict, kind+' mapping required')
    return result


def _path(value, name, printable=False):
    _need(type(value) is str and bool(value) and value.startswith('/') and '\0' not in value
          and len(value) <= CAPS['string'], name+' absolute spelling required')
    if printable:
        _need(all(32 <= ord(c) < 127 for c in value), name+' original printable path alphabet')
    return value


def _digest(value, name):
    _need(type(value) is str and re.fullmatch('[0-9a-f]{64}', value), name+' digest shape')
    return value


def _unique(items, message):
    items = list(items)
    _need(len(items) == 1, message)
    return items[0]


def _function(tree, name):
    return _unique((n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name), 'source function '+name)


def _assignment(tree, name):
    return _unique((n for n in ast.walk(tree) if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == name for t in n.targets)), 'source assignment '+name)


def _literal_assignment(tree, name):
    try:
        return ast.literal_eval(_assignment(tree, name).value)
    except (ValueError, TypeError, SyntaxError) as error:
        raise BindingError('nonliteral source assignment '+name) from error


def _expr(node):
    return ast.unparse(node)


def _anchor(source_name, node, text):
    lines = text.split('\n')
    return {'source': source_name, 'first_line': node.lineno, 'last_line': node.end_lineno,
            'text': '\n'.join(lines[node.lineno-1:node.end_lineno])}


def _native_env(value):
    _need(type(value) is dict, 'native environment mapping required')
    result = {}
    for key, item in value.items():
        _need(type(key) in (str, bytes) and type(item) in (str, bytes), 'native environment entry type')
        try:
            key = key.decode('ascii') if type(key) is bytes else key
            item = item.decode('ascii') if type(item) is bytes else item
        except UnicodeError as error:
            raise BindingError('native environment ASCII binding') from error
        _need(key not in result, 'duplicate normalized native environment key')
        result[key] = item
    return result


def _helper_launch(tree, text, parent_environment):
    """Recognize only the reviewed helper's actual Popen/cwd/env dataflow.

    Unsupported command transformations or environment dataflow fail closed;
    this function is not a generic Python evaluator.
    """
    run = _function(tree, 'run')
    popen_aliases = {'Popen'}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Attribute) and node.value.attr == 'Popen':
            popen_aliases.update(t.id for t in node.targets if isinstance(t, ast.Name))
    calls = [n for n in ast.walk(run) if isinstance(n, ast.Call) and (
        isinstance(n.func, ast.Attribute) and n.func.attr == 'Popen' or
        isinstance(n.func, ast.Name) and n.func.id in popen_aliases)]
    call = _unique(calls, 'helper must have one source-recognized Popen call')
    _need(bool(call.args), 'helper Popen command argument absent')
    command_expression = _expr(call.args[0])
    args = [x.arg for x in run.args.args]
    _need(bool(args), 'helper run command formal absent')
    command_formal = args[0]
    _need(command_expression == command_formal, 'helper command transform unsupported')
    _need(not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'chdir'
                  for n in ast.walk(tree)), 'helper chdir requires separate source derivation')
    keywords = {item.arg: item.value for item in call.keywords}
    _need(None not in keywords, 'helper expanded Popen keywords unsupported')
    cwd = keywords.get('cwd')
    if cwd is None or isinstance(cwd, ast.Constant) and cwd.value is None:
        cwd_rule = 'inherit_producer_current_cwd'
    elif len(args) > 1 and (_expr(cwd) == args[1] or _expr(cwd) == 'str('+args[1]+')'):
        cwd_rule = 'role_output_directory'
    else:
        raise BindingError('helper compiler cwd dataflow unsupported: '+_expr(cwd))
    environment = keywords.get('env')
    if environment is None or isinstance(environment, ast.Constant) and environment.value is None:
        env_rule, env = 'inherit_producer_current_environment', parent_environment
    else:
        try:
            if isinstance(environment, ast.Name):
                env = _literal_assignment(tree, environment.id)
            else:
                env = ast.literal_eval(environment)
        except BindingError:
            raise
        except (ValueError, TypeError, SyntaxError) as error:
            raise BindingError('helper native environment dataflow unsupported') from error
        _need(type(env) is dict, 'helper native environment is not a literal map')
        env_rule = 'helper_literal_environment'
    _need(_native_env(env) == parent_environment and len(env) == 6, 'helper exact six-entry native environment differs')
    return {'cwd_rule': cwd_rule, 'environment_rule': env_rule,
            'environment': dict(env), 'command_expression': command_expression,
            'run_formals': args, 'anchor': _anchor('cold_build_evidence', call, text)}


def authenticate_source_rules(corpus):
    _need(type(corpus) is dict, 'exact three-source corpus mapping required')
    # Validate keys before set construction, equality, or keyed access; a str
    # subclass can otherwise run caller callbacks during those operations.
    _need(all(type(key) is str for key in corpus), 'source corpus keys must be exact str')
    _need(set(corpus) == set(SOURCE_PINS), 'exact three-source corpus required')
    trees, texts, pins = {}, {}, []
    total = 0
    for name, (digest, size) in SOURCE_PINS.items():
        raw = corpus[name]
        _need(type(raw) is bytes and 0 < len(raw) <= CAPS['file_bytes'], 'source byte bounds/type: '+name)
        total += len(raw)
        _need(total <= CAPS['capture_bytes'], 'source corpus aggregate bound')
        _need(_sha(raw) == digest and (size is None or len(raw) == size), 'source authentication mismatch: '+name)
        try:
            texts[name] = raw.decode('utf8')
            trees[name] = ast.parse(texts[name])
        except (UnicodeError, SyntaxError, RecursionError) as error:
            raise BindingError('source AST parse failure: '+name) from error
        pins.append({'name': name, 'sha256': digest, 'bytes': len(raw)})
    producer, parent = trees['variant_driver'], trees['parent_completion']
    check, main = _function(producer, '_vcheck_literal_sources'), _function(producer, '_variant_main')
    role_pins = _literal_assignment(producer, '_VARIANT_SOURCE_PINS')
    roles = list(role_pins)
    _need(roles == ['pyinit_failure', 'exec_failure'], 'original two role literals differ')
    stage = _assignment(check, 'stage')
    source = _assignment(check, 'source_path')
    _need(_expr(stage.value) == "__file__.rsplit('/', 2)[0]", 'stage source expression differs')
    _need(_expr(source.value) == "stage + '/areas/field-negative-variants-v1/' + name + '/dict_probe_fields_v1.c'", 'source path expression differs')
    directory, target, command = (_assignment(main, name) for name in ('directory', 'target', 'command'))
    _need(_expr(directory.value) == "output + '/' + row['role']", 'output role directory expression differs')
    _need(_expr(target.value) == "directory + '/_h25_dict_probe.cpython-312-x86_64-linux-gnu.so'", 'target expression differs')
    _need(isinstance(command.value, ast.List) and len(command.value.elts) == 13, 'command AST shape differs')
    items = command.value.elts
    compiler = ast.literal_eval(items[0])
    first_options = [ast.literal_eval(item) for item in items[1:9]]
    _need(compiler == '/usr/bin/x86_64-linux-gnu-gcc-13', 'compiler source spelling differs')
    _need(first_options == ['-nostartfiles', '-shared', '-fPIC', '-O3', '-std=c11', '-Wall', '-Wextra', '-Werror'], 'eight fixed source options differ')
    _need(_expr(items[9]) == "'-I' + plan['include']" and _expr(items[10]) == "row['source_path']"
          and ast.literal_eval(items[11]) == '-o' and _expr(items[12]) == 'target', 'source operand AST differs')
    expected = _assignment(check, 'expected').value
    _need(isinstance(expected, ast.Dict), 'literal source/header dictionary absent')
    common = {}
    for key, value in zip(expected.keys, expected.values):
        key = ast.literal_eval(key)
        if isinstance(value, ast.Name) and value.id == 'header_pin':
            common[key] = None
        else:
            common[key] = ast.literal_eval(value)
    _need(set(common) == {'dict_probe_fields_v1.c','field_service_v1.h','field_loader_snapshot_v1.h'}, 'source/header filenames differ')
    modes = [value.value for node in ast.walk(check) if isinstance(node,ast.Dict)
             for key,value in zip(node.keys,node.values)
             if isinstance(key,ast.Constant) and key.value=='mode' and isinstance(value,ast.Constant)]
    source_mode = _unique(modes,'original source mode literal absent/ambiguous')
    _need(type(source_mode) is int and source_mode==292,'original source mode differs')
    source_context = _assignment(main,'context').value
    _need(isinstance(source_context,ast.Dict),'original context dictionary absent')
    context_items = {ast.literal_eval(k):v for k,v in zip(source_context.keys,source_context.values)}
    context_literals = {key:ast.literal_eval(context_items[key])
                        for key in ('source_name','no_cached_binary','module_name')}
    _need(context_literals=={'source_name':'dict_probe_fields_v1.c','no_cached_binary':True,'module_name':'_h25_dict_probe'},
          'original context literals differ')
    helper_call = _unique((node for node in ast.walk(main) if isinstance(node,ast.Call)
                         and isinstance(node.func,ast.Name) and node.func.id=='_vinvoke'
                         and len(node.args)>=2 and isinstance(node.args[0],ast.Constant)
                         and node.args[0].value=='cold_build_evidence'),'original helper invocation absent/ambiguous')
    _need(len(helper_call.args)==7 and [_expr(n) for n in helper_call.args[2:4]]==['command','directory']
          and _expr(helper_call.args[6])=='context','original helper argument bindings differ')
    helper_name,timeout = (ast.literal_eval(n) for n in helper_call.args[4:6])
    _need(helper_name=='control' and type(timeout) is int and timeout==15,'original helper name/timeout differs')
    env = _literal_assignment(parent, 'ENV')
    _need(type(env) is dict and len(env) == 6, 'parent native environment literal differs')
    flags = list(_literal_assignment(parent, 'FLAGS'))
    _need(flags == ['-S','-s','-P','-B'], 'original parent Python flags differ')
    helper_pin = _literal_assignment(producer, 'EARLY_INTEGRATION_SOURCE_PINS')['cold_build_evidence']
    _need(helper_pin == ('integration/cold_build_evidence.py', SOURCE_PINS['cold_build_evidence'][0]), 'original helper source pin differs')
    parent_validation = _function(parent, '_validate_plan')
    path_loop = _unique((node for node in ast.walk(parent_validation) if isinstance(node, ast.For)
                       and isinstance(node.target, ast.Name) and node.target.id == 'key'
                       and isinstance(node.iter, ast.Tuple)
                       and ast.literal_eval(node.iter) == ('cwd','output','evidence_directory','stage_directory')),
                      'independent parent path check source')
    parent_launch = _unique((node for node in ast.walk(_function(parent,'run_producer'))
                           if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='_POPEN'),
                          'parent actual Popen source')
    parent_kw = {item.arg:_expr(item.value) for item in parent_launch.keywords}
    _need(parent_kw.get('cwd') == "row['cwd']" and parent_kw.get('env') == 'dict(ENV)', 'parent cwd/env source differs')
    helper = _helper_launch(trees['cold_build_evidence'], texts['cold_build_evidence'], env)
    anchors = [_anchor('variant_driver', n, texts['variant_driver']) for n in (stage,source,directory,target,command,helper_call)]
    anchors.extend([_anchor('parent_completion',path_loop,texts['parent_completion']),
                    _anchor('parent_completion',parent_launch,texts['parent_completion']),helper['anchor']])
    rules = {'schema':'original-compile-source-rules-v1', 'sources':pins,
             'roles':roles, 'role_header_pins':{r:list(role_pins[r]) for r in roles},
             'common_source_pins':{k:list(v) if v is not None else None for k,v in common.items()},
             'compiler':compiler,'fixed_options':first_options+['-I/usr/include/python3.12'],
             'source_mode':source_mode,'context_literals':context_literals,'helper_name':helper_name,'timeout_seconds':timeout,
             'parent_python_flags':flags,'native_environment':dict(env),'helper_launch':helper,
             'anchors':anchors,'full_C05':False,'execution_ready':False}
    canonical(rules)
    return rules


def _file_pin(digest_size, mode):
    return {'sha256':digest_size[0], 'bytes':digest_size[1], 'mode':mode}



def _launch_projection(value):
    """Validate the entire hostile launch projection before comparing values.

    Only native environment keys/values may be exact bytes. Normalize those in
    a fresh mapping after exact type checks, then validate every other reachable
    value as bounded exact plain data. No user equality callback is needed.
    """
    _need(type(value) is list and len(value)==2, 'two exact compiler launch records required')
    result = []
    fields = {'role','command','cwd','environment','context','helper_name','timeout_seconds'}
    for row in value:
        _need(type(row) is dict, 'compiler launch must be an exact mapping')
        _need(all(type(key) is str for key in row), 'compiler launch keys must be exact str')
        _need(set(row)==fields, 'compiler launch projection shape differs')
        normalized_environment = _native_env(row['environment'])
        fresh = {key:item for key,item in row.items()}
        fresh['environment'] = normalized_environment
        canonical(fresh)
        _need(type(fresh['role']) is str and type(fresh['cwd']) is str
              and type(fresh['helper_name']) is str, 'launch role/cwd/helper must be exact str')
        _need(type(fresh['command']) is list and all(type(item) is str for item in fresh['command']),
              'compiler argv must be an exact list of exact str')
        _need(type(fresh['context']) is dict, 'compiler context must be exact mapping')
        _need(type(fresh['timeout_seconds']) is int, 'compiler timeout must be exact int')
        result.append(fresh)
    canonical(result)
    return result


def construct_original_compile_pair(corpus, *, parent_plan_raw, parent_plan_sha256,
                                    variant_configuration_raw, variant_configuration_sha256,
                                    compiler_launches):
    """Validate a source-bound projection; never admit an original parent plan.

    The two raw JSON records must be independently pinned by their caller.
    Only the query-relevant projection is checked. Full original parent,
    source currentness, initial integrity, namespace, costs and runtime admission
    remain separate. compiler_launches must contain explicit proposed per-role
    argv/env/cwd/context records, not booleans asserting those bindings.
    """
    compiler_launches = _launch_projection(compiler_launches)
    rules = authenticate_source_rules(corpus)
    plan = _decode(parent_plan_raw,parent_plan_sha256,'parent plan')
    config = _decode(variant_configuration_raw,variant_configuration_sha256,'variant configuration')
    _need(plan.get('mode') in ('normal','optimized'), 'parent mode differs')
    _need(type(plan.get('producers')) is dict and 'failure_variants' in plan['producers'], 'failure_variants parent row absent')
    row = plan['producers']['failure_variants']
    _need(type(row) is dict, 'producer row mapping required')
    try:
        stage = _path(row['stage_directory'],'stage',True)
        parent_cwd = _path(row['cwd'],'parent cwd')
        output = _path(row['output'],'producer output',True)
        evidence = _path(row['evidence_directory'],'evidence directory')
        session = _path(plan['session_directory'],'session directory')
    except KeyError as error:
        raise BindingError('parent path binding absent') from error
    _need(evidence == session+'/failure_variants' and output == evidence+'/producer-output', 'original producer output origin differs')
    root_command = row.get('command')
    _need(type(root_command) is list and all(type(x) is str and x for x in root_command), 'parent root argv shape')
    prefix = ['/usr/bin/python3.12']+rules['parent_python_flags']+(['-O'] if plan['mode']=='optimized' else [])
    _need(root_command[:len(prefix)] == prefix, 'parent root interpreter/flags/mode differ')
    _need(len(root_command)>len(prefix) and root_command[len(prefix)] == stage+'/integration/full_driver.py', 'parent stage entry differs')
    integration = stage+'/integration'
    args = root_command[len(prefix)+1:]
    _need(len(args)==17 and args[0]=='--root-sha256' and args[2]=='--provider' and args[5]=='--driver'
          and args[8]=='--integration' and args[10]=='--', 'original parent bootstrap positions differ')
    _need(args[1]=='f5a2d33f2b4d3651f214156a0e7094c2bb516ce2d5ab7698d18c11f98f35dee0'
          and args[3]==integration+'/probe_binding_v3.py'
          and args[4]=='9cbb7368f89e71d1e6cc46db5dc77efed3e03ed2a801c98c88fe316e4d9f3ef2'
          and args[6]==integration+'/variant_driver_v1.py' and args[9]==integration,
          'original parent bootstrap source paths differ')
    _digest(args[7],'selected original driver binding')
    epoch = row.get('epoch_plan')
    _need(type(epoch) is dict and type(epoch.get('generation')) is str
          and 1<=len(epoch['generation'])<=96
          and all(c in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in epoch['generation']), 'parent generation binding differs')
    nonce = _digest(row.get('launch_nonce'),'parent launch nonce')
    _need(args[11:]==['--output',output,'--generation',epoch['generation'],'--launch-nonce',nonce],
          'original parent exact variant tail differs')
    _need(root_command.count('--output')==1, 'parent output operand count differs')
    index = root_command.index('--output')
    _need(index+1<len(root_command) and root_command[index+1]==output, 'parent output operand differs')
    _need(config.get('include')=='/usr/include/python3.12', 'original include path differs')
    _digest(config.get('system_header_admission_sha256'),'header admission binding')
    roles = config.get('roles')
    _need(type(roles) is list and len(roles)==2 and all(type(r) is dict for r in roles), 'exact two original role rows required')
    _need([r.get('role') for r in roles]==rules['roles'], 'original role names/order differ')
    files = config.get('source_files')
    _need(type(files) is list and 1<=len(files)<=CAPS['rows'] and all(type(f) is dict for f in files), 'source file row bounds/type')
    by_path, declared_capture_bytes = {}, 0
    for file in files:
        path = _path(file.get('path'),'declared closure source')
        _need(path not in by_path, 'duplicate closure source path')
        _digest(file.get('sha256'),'declared closure source')
        size,mode = file.get('bytes'),file.get('mode')
        _need(type(size) is int and 0<=size<=CAPS['file_bytes'], 'declared closure per-file byte bound/type')
        _need(type(mode) is int and 0<=mode<=0o7777, 'declared closure mode bound/type')
        declared_capture_bytes += size
        _need(declared_capture_bytes<=CAPS['capture_bytes'], 'declared closure aggregate byte bound')
        by_path[path] = file
    _need(type(compiler_launches) is list and len(compiler_launches)==2, 'two compiler launch records required')
    result_rows = []
    for index, (role, launch) in enumerate(zip(roles, compiler_launches)):
        name = rules['roles'][index]
        directory = output+'/'+name
        source_path = stage+'/areas/field-negative-variants-v1/'+name+'/dict_probe_fields_v1.c'
        target = directory+'/_h25_dict_probe.cpython-312-x86_64-linux-gnu.so'
        _need(role.get('source_path')==source_path, 'role source path differs')
        pins = {filename:_file_pin(rules['role_header_pins'][name] if pin is None else pin,rules['source_mode'])
                for filename,pin in rules['common_source_pins'].items()}
        _need(_same(role.get('source'),pins['dict_probe_fields_v1.c']), 'original C source pin differs')
        headers = {k:v for k,v in pins.items() if not k.endswith('.c')}
        _need(_same(role.get('source_headers'),headers), 'original role header pins differ')
        for filename,pin in pins.items():
            path = source_path.rsplit('/',1)[0]+'/'+filename
            _need(path in by_path and _same({k:by_path[path].get(k) for k in pin},pin), 'role input omitted/changed in source closure')
        expected_command = [rules['compiler'],*rules['fixed_options'],source_path,'-o',target]
        compiler_cwd = parent_cwd if rules['helper_launch']['cwd_rule']=='inherit_producer_current_cwd' else directory
        expected_context = {'source':pins['dict_probe_fields_v1.c'],'source_name':'dict_probe_fields_v1.c',
                            'no_cached_binary':True,'module_name':'_h25_dict_probe','target':target,
                            'source_headers':headers,'system_header_admission_sha256':config['system_header_admission_sha256'],
                            'negative_variant_role':name}
        _need(type(launch) is dict and set(launch)=={'role','command','cwd','environment','context','helper_name','timeout_seconds'}, 'compiler launch projection shape differs')
        _need(launch['role']==name, 'compiler launch role/order differs')
        _need(type(launch['command']) is list and launch['command']==expected_command, 'original exact compiler command differs')
        _need(launch['cwd']==compiler_cwd, 'independently bound compiler cwd differs')
        _need(_native_env(launch['environment'])==rules['native_environment'], 'exact six-entry compiler native environment differs')
        _need(_same(launch['context'],expected_context), 'original source/header/context labels differ')
        _need(launch['helper_name']=='control' and type(launch['timeout_seconds']) is int and launch['timeout_seconds']==15,
              'original helper label/timeout differs')
        result_rows.append({'role':name,'source_path':source_path,'role_output_directory':directory,'output_path':target,
                            'compiler_cwd':compiler_cwd,'command':expected_command,
                            'command_sha256':_sha(canonical({'argv':expected_command})),
                            'native_environment':rules['native_environment'],'context':expected_context,
                            'helper_name':'control','timeout_seconds':15})
    result = {'schema':'source-pinned-original-compile-binding-v1',
              'parent_plan_sha256':parent_plan_sha256,'variant_configuration_sha256':variant_configuration_sha256,
              'stage_root':stage,'producer_output':output,'parent_cwd':parent_cwd,
              'declared_closure_rows':len(files),'declared_closure_bytes':declared_capture_bytes,
              'cwd_rule':rules['helper_launch']['cwd_rule'],'mode':plan['mode'],'compile_bindings':result_rows,
              'source_rules':rules,'projection_only':True,'parent_plan_admitted':False,
              'namespace_currentness_proven':False,'generic_any_cwd_correctness':False,
              'effective_GCC_configuration':False,'full_C05':False,'full_V03':False,'execution_ready':False,'expected_record_pin_independence_checked':False,
              'actual_compiler_cwd_environment_observed':False,
              'runtime_cwd_environment_currentness_proven':False,'compiler_binary_authenticated':False,
              'cwd_environment_premise':'unchanged original producer route retains its independently admitted cwd/environment through helper Popen'}
    canonical(result)
    return result

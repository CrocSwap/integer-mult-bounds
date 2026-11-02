"""New source/data tests only. Never import/execute the archived producer/Root.

The six-row test baseline deliberately lacks C05 and admission fields. It is
only a constructor fixture, never a configured original stage or control run.
Tracebacks below are new parser fixtures built by Python's standard formatter.
"""
import ast
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import traceback
import unittest

HERE = Path(__file__).resolve().parents[1]
WORKSPACE = HERE.parents[1]
IMPLEMENTATION = HERE / 'implementation'
ORIGINAL = HERE / 'inputs'
ROOT = HERE / 'inputs/root/full_driver.py.txt'
ROLES = ('pyinit_failure', 'exec_failure')
NAMES = ('dict_probe_fields_v1.c', 'field_service_v1.h',
         'field_loader_snapshot_v1.h')
EXPECTED_PINS = (
    ('e0188999d41a9ab26e8d3d5c37b18b2238b3af21b1db90895f01f7be76d50b65',17806),
    ('7656cd37503986459c4133643372fec13d3e5ad5553881f0bf0343a9a3e11abd',17354),
    ('bf7ab049cea89c0a882b279e35b1383ac8f99b66aa4b9b8e1ca22eb9c24c5a8d',19495),
    ('e0188999d41a9ab26e8d3d5c37b18b2238b3af21b1db90895f01f7be76d50b65',17806),
    ('f5066831bd812e7e88fb971ba0e7ca86dbef91fc40a1a68c17b040ce474cd880',17040),
    ('bf7ab049cea89c0a882b279e35b1383ac8f99b66aa4b9b8e1ca22eb9c24c5a8d',19495))
ENV = {b'PATH': b'/usr/bin:/bin', b'PYTHONHASHSEED': b'0',
       b'LANG': b'C.UTF-8', b'LC_ALL': b'C.UTF-8', b'TZ': b'UTC',
       b'PYTHONDONTWRITEBYTECODE': b'1'}


def load_new(name):
    spec = importlib.util.spec_from_file_location(name, IMPLEMENTATION/(name+'.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


constructor = load_new('v03_integrated_constructor_v1')
fixtures = load_new('v03_fixture_constructor_v1')
observer = load_new('v03_source_refusal_observer_v1')
PAYLOADS = tuple((ORIGINAL/'areas/field-negative-variants-v1'/role/(name+'.txt')).read_bytes()
                 for role in ROLES for name in NAMES)
SOURCE = (ORIGINAL/'areas/field-variant-producer-v2/variant_driver_v1.py.txt').read_bytes()
ROOT_BYTES = ROOT.read_bytes()
GENERATED = constructor.build_control_driver(SOURCE)
STAGE = '/tmp/v03-pure-fixture-stage'
DRIVER_PATH = STAGE+'/integration/v03_control_driver_v1.py'
ROOT_PATH = STAGE+'/integration/full_driver.py'


def relative(index):
    return 'areas/field-negative-variants-v1/'+ROLES[index//3]+'/'+NAMES[index%3]


def baseline(stage=STAGE):
    rows = [{'path':stage+'/'+relative(i), 'sha256':h, 'bytes':n, 'mode':0o444}
            for i,(h,n) in enumerate(EXPECTED_PINS)]
    roles = []
    for index,role in enumerate(ROLES):
        offsets = [3*index+i for i in range(3)]
        meta = [{k:rows[i][k] for k in ('sha256','bytes','mode')} for i in offsets]
        roles.append({'role':role, 'source_path':rows[3*index]['path'],
                      'source':meta[0], 'source_headers':dict(zip(NAMES[1:],meta[1:]))})
    return {'roles':roles, 'source_files':rows, 'expected_preflight':{
        'schema':'h25-public-runtime-preflight-v2', 'authenticated_files':217,
        'native_private_access':False, 'cached_admission':False}}


def independent_data_classification(case, stage=STAGE):
    """Reference predicates on DATA, not an original process or Root emulator."""
    p = case['child_configuration']
    if [r['role'] for r in p['roles']] != list(ROLES):
        return 'Variant literal configuration differs'
    rows = {r['path']:r for r in p['source_files']}
    for index,(digest,size) in enumerate(EXPECTED_PINS):
        role = p['roles'][index//3]
        if role['source_path'] != stage+'/'+relative(3*(index//3)):
            return 'Variant source role path differs'
        expected = {'sha256':digest,'bytes':size,'mode':0o444}
        current = role['source'] if index%3==0 else role['source_headers'][NAMES[index%3]]
        if current != expected:
            return 'Variant reviewed source/header differs'
        if {k:rows[stage+'/'+relative(index)][k] for k in expected} != expected:
            return 'Variant role file omitted from closure'
    if p['expected_preflight']['authenticated_files'] != 217:
        return 'Variant original preflight differs'
    for path,raw,mode in case['physical_files']:
        current = rows[path]
        if (hashlib.sha256(raw).hexdigest(),len(raw),mode) != (
                current['sha256'],current['bytes'],current['mode']):
            return 'Variant current source closure differs'
    return None


def source_function(tree,name):
    return next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)


def one_call(node,name):
    # Independent test lookup: use textual source spans for known call sites.
    lines = GENERATED.decode().split('\n') if name!='_EXEC' else ROOT_BYTES.decode().split('\n')
    candidates = [i for i in range(node.lineno,node.end_lineno+1)
                  if lines[i-1].strip().startswith(name+'(')]
    if len(candidates)!=1:
        raise RuntimeError('test fixture call site is not unique')
    return candidates[0]


def formatted_refusal(function,message):
    root_tree,tree = ast.parse(ROOT_BYTES),ast.parse(GENERATED)
    prefix = source_function(tree,'_v03_original_input_prefix')
    terminal = next(n.lineno for n in ast.walk(source_function(tree,function))
        if isinstance(n,ast.Raise) and isinstance(n.exc,ast.Call)
        and len(n.exc.args)==1 and isinstance(n.exc.args[0],ast.Constant)
        and n.exc.args[0].value==message)
    root_lines = ROOT_BYTES.decode().split('\n')
    lines = GENERATED.decode().split('\n')
    root_entry = next(i for i,l in enumerate(root_lines,1) if l=='    _entry()')
    driver_entry = next(i for i,l in enumerate(lines,1)
                        if l=='    _V03_RESULT[0] = _v03_original_input_prefix()')
    frames = [(ROOT_PATH,root_entry,'<module>',root_lines[root_entry-1]),
              (ROOT_PATH,one_call(source_function(root_tree,'_entry'),'_EXEC'),
               '_entry','    _EXEC(code, driver_namespace)'),
              (DRIVER_PATH,driver_entry,'<module>',lines[driver_entry-1])]
    if function!='_v03_original_input_prefix':
        call = one_call(prefix,function)
        frames.append((DRIVER_PATH,call,'_v03_original_input_prefix',lines[call-1]))
    frames.append((DRIVER_PATH,terminal,function,lines[terminal-1]))
    stack = traceback.StackSummary.from_list(frames)
    raw = ('Traceback (most recent call last):\n'+''.join(stack.format())+
           'RuntimeError: '+message+'\n').encode()
    return raw,terminal


class NewConstructorControls(unittest.TestCase):
    def test_source_identity_and_retained_regions(self):
        self.assertEqual(hashlib.sha256(SOURCE).hexdigest(),
                         'cdb1479253358508088f8aa0e1e92e6c75ffcc127e54552698598a02de061254')
        self.assertEqual(hashlib.sha256(ROOT_BYTES).hexdigest(),constructor.ROOT_SHA)
        tail = b'try:\n    _variant_main()\nexcept BaseException as _variant_error:\n    _VARIANT_TERMINAL_ERROR[0] = _variant_error\n    raise\n'
        self.assertEqual(GENERATED[:len(SOURCE)-len(tail)],SOURCE[:-len(tail)])
        old,new = ast.parse(SOURCE),ast.parse(GENERATED)
        original = source_function(old,'_variant_main')
        cut = next(i for i,n in enumerate(original.body) if isinstance(n,ast.Assign)
                   and any(isinstance(t,ast.Name) and t.id=='builds' for t in n.targets))
        prefix = source_function(new,'_v03_original_input_prefix')
        self.assertEqual([ast.dump(n) for n in prefix.body[:-1]],
                         [ast.dump(n) for n in original.body[:cut]])
        self.assertIsInstance(prefix.body[-1],ast.Return)
        gates = {n.targets[0].id:ast.literal_eval(n.value) for n in new.body
                 if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name)
                 and n.targets[0].id in constructor.GATES}
        self.assertEqual(gates,dict.fromkeys(constructor.GATES))
        self.assertLess(len(GENERATED),262145)

    def test_generator_refuses_changed_original(self):
        for raw in (SOURCE[:-1],b'X'+SOURCE[1:],SOURCE.decode(),b''):
            with self.assertRaises(ValueError):constructor.build_control_driver(raw)

    def test_launch_is_data_and_preserves_startup(self):
        for mode in ('normal','optimized'):
            launch = constructor.genuine_launch(STAGE,'/tmp/v03-output','gen-1',
                                                'a'*64,mode,GENERATED)
            self.assertEqual(launch['env'],ENV)
            self.assertEqual(launch['cwd'],STAGE)
            self.assertEqual(launch['command'][:5],['/usr/bin/python3.12','-S','-s','-P','-B'])
            self.assertEqual('-O' in launch['command'],mode=='optimized')
            self.assertFalse(launch['source_admitted']);self.assertFalse(launch['execution_admitted'])
            self.assertNotIn('-I',launch['command']);self.assertNotIn('-E',launch['command'])
        for path in ('relative','/a/../b','/a//b','/a\x00b'):
            with self.assertRaises(ValueError):constructor.genuine_launch(path,'/tmp/out','g','a'*64,'normal',GENERATED)

    def test_all_proposed_case_data_against_independent_predicates(self):
        for raw,(h,n) in zip(PAYLOADS,EXPECTED_PINS):
            self.assertEqual((hashlib.sha256(raw).hexdigest(),len(raw)),(h,n))
        specs = fixtures.case_specs();self.assertEqual(len(specs),89);self.assertEqual(len(set(specs)),89)
        counts = {'negative':0,'positive':0,'earlier':0}
        for spec in specs:
            case = fixtures.construct_case(baseline(),PAYLOADS,STAGE,spec)
            self.assertEqual(independent_data_classification(case),case['parent_expectation']['message'])
            if not case['parent_expectation']['v03_discriminator']:counts['earlier']+=1
            elif case['parent_expectation']['message'] is None:counts['positive']+=1
            else:counts['negative']+=1
            self.assertFalse(case['c05_completeness_established_here'])
            self.assertFalse(case['source_admitted']);self.assertFalse(case['execution_admitted'])
        self.assertEqual(counts,{'negative':68,'positive':20,'earlier':1})

    def test_actual_fresh_mode_and_byte_fixture_only(self):
        root = Path(tempfile.mkdtemp(prefix='v03-constructor-',dir='/tmp'))
        for which,spec in enumerate((('physical-mode',1,-1,''),('physical-byte',4,-1,''))):
            stage = str(root/str(which))
            case = fixtures.construct_case(baseline(stage),PAYLOADS,stage,spec)
            for path,raw,mode in case['physical_files']:
                p = Path(path);p.parent.mkdir(parents=True,exist_ok=True)
                fd = os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
                try:
                    offset=0
                    while offset<len(raw):
                        count=os.write(fd,raw[offset:])
                        if count<=0:raise RuntimeError('fixture write made no progress')
                        offset+=count
                    os.fchmod(fd,mode)
                finally:os.close(fd)
                self.assertEqual(p.read_bytes(),raw);self.assertEqual(p.stat().st_mode&0o7777,mode)
            self.assertEqual(independent_data_classification(case,stage),
                             'Variant current source closure differs')
        # Retain this newly owned fixture on success/failure; no old data touched.

    def test_full_traceback_and_retained_three_line_counterexample(self):
        function,message = '_vcheck_custody','Variant current source closure differs'
        raw,line = formatted_refusal(function,message)
        args = (GENERATED,ROOT_BYTES,DRIVER_PATH,ROOT_PATH)
        self.assertTrue(observer.corroborate_complete_refusal(*args,raw,function,message,2097152))
        short = ('Traceback (most recent call last):\n  File "'+DRIVER_PATH+'", line '+
                 str(line)+', in '+function+'\nRuntimeError: '+message+'\n').encode()
        self.assertTrue(observer.corroborate_raw_refusal(GENERATED,DRIVER_PATH,short,function,message,2097152))
        self.assertFalse(observer.corroborate_complete_refusal(*args,short,function,message,2097152))
        for changed in (raw.replace(b'    _EXEC(code, driver_namespace)\n',b'',1),
                        raw.replace(b'    _EXEC(code, driver_namespace)\n',b'    _EXEC(code, driver_namespace)\n    ^ ^\n',1),
                        raw.replace(b', in _entry\n',b', in other\n',1),
                        raw.replace(b'Traceback (most recent call last):\n',b'Traceback (most recent call last):\njunk\n',1),
                        raw.replace(b'    _EXEC(code, driver_namespace)\n',b'    wrong_source()\n',1),
                        raw[:-1],raw+raw):
            self.assertFalse(observer.corroborate_complete_refusal(*args,changed,function,message,2097152))
        for function,message in (('_vcheck_literal_sources','Variant source role path differs'),
                ('_v03_original_input_prefix','Variant literal configuration differs'),
                ('_v03_original_input_prefix','Variant original preflight differs')):
            raw,_=formatted_refusal(function,message)
            self.assertTrue(observer.corroborate_complete_refusal(*args,raw,function,message,2097152))

    def test_positive_receiver_strict_types_and_duplicate_keys(self):
        binding={'mode':'normal','generation':'g','launch_nonce':'a'*64}
        result={'schema':'h25-v03-input-prefix-result-v1','status':'ORIGINAL_INPUT_PREFIX_RETURNED',
                'binding':binding,'whole_variant_producer_completed':False,'runtime_qualified':False}
        counters=dict.fromkeys(observer.ROOT_COUNTERS,0)
        preflight=baseline()['expected_preflight']
        encode=lambda x:json.dumps(x,sort_keys=True,separators=(',',':')).encode()
        self.assertTrue(observer.corroborate_positive(encode(result),encode(counters),encode(preflight),binding,1048576))
        wrong=copy.deepcopy(counters);wrong['load_calls']=False
        self.assertFalse(observer.corroborate_positive(encode(result),encode(wrong),encode(preflight),binding,1048576))
        wrong=copy.deepcopy(result);wrong['binding']['mode']='optimized'
        self.assertFalse(observer.corroborate_positive(encode(wrong),encode(counters),encode(preflight),binding,1048576))
        for raw in (b'{"x":0,"x":1}',b'{"x":1.0}',b'{"x":NaN}'):
            with self.assertRaises(ValueError):observer.corroborate_positive(raw,encode(counters),encode(preflight),binding,1048576)


if __name__=='__main__':
    unittest.main(failfast=True)

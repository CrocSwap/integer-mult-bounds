"""NEW source and fresh owned files/literal modules only; no original body exec."""
import hashlib
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

BASE=Path('/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453/outputs/c05-v03-completion-20261102T055710Z/unit06')
spec=importlib.util.spec_from_file_location('unit06_NEW_fixture_support',BASE/'implementation/predecessor_entry.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=BASE/'fixtures');self.names=[]
    def tearDown(self):
        for name in self.names:sys.modules.pop(name,None) # fixture isolation, never runtime rollback
        self.temp.cleanup()
    def policy(self,bodies):
        owner=m.Owner();policy={};expected={};order=[]
        for index,body in enumerate(bodies):
            name='_unit06_NEW_literal_'+str(id(self))+'_'+str(index);self.names.append(name)
            path=str(Path(self.temp.name)/(str(index)+'.py'))
            policy[name]=m.write_exclusive(path,body,0o444,owner)
            expected[name]=(hashlib.sha256(body).hexdigest(),len(body));order.append(name)
        return policy,expected,tuple(order)
    def test_retained_real_module_identity_and_builtins(self):
        p,e,o=self.policy([b'answer=41\n']);owner=m.Owner()
        actual=m.load_authenticated_modules(p,e,o,owner)
        self.assertIs(actual[o[0]],owner.modules[o[0]])
        self.assertIs(actual[o[0]].__dict__['__builtins__'],__builtins__ if type(__builtins__) is dict else vars(__builtins__))
        self.assertEqual(actual[o[0]].answer,41)
    def test_bad_second_hash_precedes_any_body(self):
        p,e,o=self.policy([b'answer=1\n',b'answer=2\n']);e[o[1]]=('0'*64,e[o[1]][1]);owner=m.Owner()
        with self.assertRaises(m.Stop):m.load_authenticated_modules(p,e,o,owner)
        self.assertEqual(owner.executed,[]);self.assertEqual(owner.published,[])
        with self.assertRaises(BaseException):m.load_authenticated_modules(p,e,o,owner)
    def test_missing_project_dependency_precedes_any_body(self):
        p,e,o=self.policy([b'answer=1\n',b'import _unit06_missing_project\n']);owner=m.Owner()
        with self.assertRaises(m.Stop):m.load_authenticated_modules(p,e,o,owner)
        self.assertEqual(owner.executed,[])
    def test_ambient_project_is_not_adopted(self):
        p,e,o=self.policy([b'answer=1\n']);sys.modules[o[0]]=object();owner=m.Owner()
        with self.assertRaises(m.Stop):m.load_authenticated_modules(p,e,o,owner)
        self.assertEqual(owner.captures,[])
    def test_partial_initialization_retained_and_burned(self):
        p,e,o=self.policy([b'answer=1\n',b'partial=7\nraise RuntimeError("NEW literal failure")\n']);owner=m.Owner()
        with self.assertRaises(RuntimeError) as caught:m.load_authenticated_modules(p,e,o,owner)
        self.assertIs(owner.primary,caught.exception)
        self.assertEqual(owner.executed,[o[0]])
        self.assertEqual(owner.modules[o[1]].partial,7)
        with self.assertRaises(RuntimeError) as second:m.load_authenticated_modules(p,e,o,owner)
        self.assertIs(second.exception,caught.exception)
    def test_read_primary_and_close_secondary_same_objects(self):
        path=str(Path(self.temp.name)/'fresh');Path(path).write_bytes(b'NEW')
        own=m.Owner();A=RuntimeError('A');B=RuntimeError('B');real_close=m.os.close
        def close(fd):real_close(fd);raise B
        with patch.object(m.os,'read',side_effect=A),patch.object(m.os,'close',side_effect=close):
            with self.assertRaises(RuntimeError) as caught:m.observe_regular(path,100,own)
        self.assertIs(caught.exception,A);self.assertIs(own.primary,A);self.assertIn(B,own.secondary)
        self.assertTrue(own.quarantined);self.assertEqual(own.fd_slots,[None])
    def test_foreign_metaclass_callback_never_called(self):
        events=[]
        class Meta(type):
            def __eq__(self,other):events.append('BAD');raise RuntimeError('callback')
        class Foreign(metaclass=Meta):pass
        with self.assertRaises(m.Stop):m.plain(Foreign())
        self.assertEqual(events,[])
    def test_exact_cap_path_and_duplicate_json(self):
        for path in ('/tmp/é','/tmp/a\nb','/'+'/'.join(['a']*65)):
            with self.assertRaises(m.Stop):m.path_text(path)
        with self.assertRaises(m.Stop):m.decode(b'{"a":1,"a":2}')
        with self.assertRaises(m.Stop):m.observe_regular('/FAKE',True,m.Owner())
    def test_fixed_original_graph_is_parsed_only_and_ordered(self):
        import json
        graph=json.loads((BASE/'SOURCE-GRAPH-v1.json').read_bytes())
        buffers={row['module']:Path(row['copy_path']).read_bytes() for row in graph['modules']}
        self.assertEqual(set(buffers),set(m.PROJECT_PINS))
        for name,raw in buffers.items():self.assertEqual((hashlib.sha256(raw).hexdigest(),len(raw)),m.PROJECT_PINS[name])
        edges=m.import_edges(buffers);positions={name:n for n,name in enumerate(m.PROJECT_ORDER)}
        self.assertTrue(all(positions[dep]<positions[name] for name,deps in edges.items() for dep in deps))
    def test_invalid_mode_refuses_before_any_runtime_operation(self):
        with self.assertRaises(m.Stop):m.validate_startup('/usr/bin/python3.12',{},m.ENV,m.SYSTEM_PATH,[],{'mode':'not-a-mode'})
    def test_exact_gate_names_installed_only_in_fresh_fixture_modules(self):
        import types
        modules={name:types.ModuleType('_NEW_gate_fixture_'+name) for name in m.GATE_NAMES}
        gates={name:{key:{'NEW_LITERAL_DATA_ONLY':True} for key in keys} for name,keys in m.GATE_NAMES.items()}
        m.install_gate_data(modules,gates)
        for name,keys in m.GATE_NAMES.items():
            for key in keys:self.assertIs(modules[name].__dict__[key],gates[name][key])
        gates['epoch_copy_v5']['EXTRA']=None
        with self.assertRaises(m.Stop):m.install_gate_data(modules,gates)
    def test_new_data_write_is_exclusive_and_real_identity(self):
        path=str(Path(self.temp.name)/'receipt.json');owner=m.Owner()
        pin=m.write_exclusive(path,m.canonical({'status':'NEW_LITERAL_DATA'}),0o444,owner)
        self.assertEqual(pin['identity']['links'],1)
        self.assertEqual(m.retain_regular(pin,m.RECORD_CAP,owner)[1],Path(path).read_bytes())
        with self.assertRaises(FileExistsError):m.write_exclusive(path,b'x',0o444,owner)


if __name__=='__main__':unittest.main(verbosity=2)

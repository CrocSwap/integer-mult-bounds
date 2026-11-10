"""Execute only NEW pure constructor/verifier source; original driver is bytes."""
import ast
import builtins
import hashlib
from pathlib import Path
from types import ModuleType
import unittest

ROOT=Path('/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453')
BASE=ROOT/'outputs/c05-v03-completion-20261102T055710Z/unit05'
IMPL=BASE/'implementation'
ORIGINAL=ROOT/'outputs/resolved-questions-publication-20261102T025112Z/v03-publication/research/h25-v03-source-prerequisites/snapshot/areas/field-variant-producer-v2/variant_driver_v1.py.txt'


def load_new(name,pin,constructor=None):
    raw=(IMPL/(name+'.py')).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=pin:raise ValueError('new pure component source pin differs')
    tree=ast.parse(raw,feature_version=(3,12))
    allowed={'ast','hashlib'} if constructor is None else {'ast','v03_integrated_constructor_v2'}
    for node in ast.walk(tree):
        if isinstance(node,ast.Import) and any(x.name not in allowed for x in node.names):raise ValueError('pure import boundary')
        if isinstance(node,ast.ImportFrom) and node.module not in allowed:raise ValueError('pure from-import boundary')
    module=ModuleType(name)
    def importing(module_name,globals=None,locals=None,fromlist=(),level=0):
        if level or module_name not in allowed:raise ValueError('new component attempted unexpected import')
        if module_name=='v03_integrated_constructor_v2':return constructor
        return builtins.__import__(module_name,globals,locals,fromlist,level)
    functions=dict(vars(builtins));functions['__import__']=importing
    module.__dict__['__builtins__']=functions
    exec(compile(raw,'<pinned-new-pure-'+name+'>','exec'),module.__dict__)
    return module


class DerivationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.constructor=load_new('v03_integrated_constructor_v2','a80a60b390bc60e9bc434b79cda5ae6db88e4f0c6c7436de9adfe1f48a2045b1')
        cls.checker=load_new('v03_prefix_derivation_v1','1ed813148c10d5fbd3cd6781d51eca650a347eda7a6323f581d740e6ea9cb6e2',cls.constructor)
        cls.original=ORIGINAL.read_bytes()
        if hashlib.sha256(cls.original).hexdigest()!='cdb1479253358508088f8aa0e1e92e6c75ffcc127e54552698598a02de061254':raise ValueError('inert original pin')
        cls.rendered=cls.constructor.build_control_driver(cls.original)

    def values(self):return {name:None for name in self.constructor.GATES}

    def render(self,values,expression=None):
        raw=self.rendered;tree=ast.parse(raw,feature_version=(3,12));lines=raw.split(b'\n');spans=[]
        for node in tree.body:
            if type(node) is ast.Assign and len(node.targets)==1 and type(node.targets[0]) is ast.Name and node.targets[0].id in values:
                value=node.value
                start=sum(len(x)+1 for x in lines[:value.lineno-1])+value.col_offset
                end=sum(len(x)+1 for x in lines[:value.end_lineno-1])+value.end_col_offset
                payload=expression if expression is not None and node.targets[0].id==self.constructor.GATES[0] else repr(values[node.targets[0].id]).encode('utf8')
                spans.append((start,end,payload))
        for start,end,payload in sorted(spans,reverse=True):raw=raw[:start]+payload+raw[end:]
        return raw

    def test_unconfigured_exact_rendering(self):
        self.assertIsNone(self.checker.verify_configured_prefix(self.original,self.rendered,self.values()))

    def test_unicode_gate_literal_byte_offsets(self):
        values=self.values();values[self.constructor.GATES[0]]={'unicode':'π','nested':[1,True,None]}
        self.assertIsNone(self.checker.verify_configured_prefix(self.original,self.render(values),values))

    def test_non_gate_byte_change_rejects(self):
        with self.assertRaises(ValueError):self.checker.verify_configured_prefix(self.original,self.rendered+b'\n#NONGATE\n',self.values())

    def test_bool_is_not_integer_gate_data(self):
        actual=self.values();actual[self.constructor.GATES[0]]=True
        expected=self.values();expected[self.constructor.GATES[0]]=1
        with self.assertRaises(ValueError):self.checker.verify_configured_prefix(self.original,self.render(actual),expected)

    def test_nonliteral_call_never_executes(self):
        calls=[];self.checker.touch=lambda:calls.append('BAD')
        with self.assertRaises(ValueError):self.checker.verify_configured_prefix(self.original,self.render(self.values(),b'touch()'),self.values())
        self.assertEqual(calls,[])

    def test_duplicate_gate_rejects(self):
        extra=('\n'+self.constructor.GATES[0]+' = None\n').encode()
        with self.assertRaises(ValueError):self.checker.verify_configured_prefix(self.original,self.rendered+extra,self.values())

    def test_plain_text_container_and_depth_exhaustion(self):
        nested=None
        for n in range(26):nested=[nested]
        for bad in ('x'*8193,[None]*1025,nested):
            values=self.values();values[self.constructor.GATES[0]]=bad
            with self.assertRaises(ValueError):self.checker.verify_configured_prefix(self.original,self.render(values),values)

    def test_tuple_environment_preserves_all_six_native_pairs(self):
        self.assertIs(type(self.constructor.NATIVE_ENV),tuple)
        self.assertEqual(dict(self.constructor.NATIVE_ENV),{b'PATH':b'/usr/bin:/bin',b'PYTHONHASHSEED':b'0',b'LANG':b'C.UTF-8',b'LC_ALL':b'C.UTF-8',b'TZ':b'UTC',b'PYTHONDONTWRITEBYTECODE':b'1'})


if __name__=='__main__':unittest.main(verbosity=2)

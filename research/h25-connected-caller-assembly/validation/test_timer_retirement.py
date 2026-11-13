"""Actual timer/finalizer bodies and actual registry, with inert signal ports.

The fixture registry owns only temporary source directories and raw errors.
No genuine financial Context, guardian, native signal or science is executed.
The unchanged native verification port is explicitly inert in this control.
"""
import ast
import importlib.util
from pathlib import Path
import tempfile
import types
import unittest

D=Path(__file__).resolve().parents[1]
S_PATH=D/'implementation/source/fresh_supervisor.py'

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

class Ports:
    ITIMER_REAL=0;SIGALRM=14
    def __init__(self,errors):self.errors=errors;self.calls=[]
    def setitimer(self,kind,value):
        self.calls.append('cancel')
        if self.errors[0] is not None:raise self.errors[0]
    def signal(self,kind,value):
        self.calls.append('restore')
        if self.errors[1] is not None:raise self.errors[1]

def subject(errors):
    S=load('retirement_source_subject',S_PATH)
    R=load('retirement_actual_registry',D/'implementation/source/attempt_registry.py')
    ports=Ports(errors);S.signal=ports;S.time=types.SimpleNamespace(monotonic_ns=lambda:100)
    owner=S.DeadlineOwner(1000);owner.started=True;owner.old_handler=object()
    root=Path(tempfile.mkdtemp(prefix='timer-custody-',dir=D/'validation/tmp'))
    root.chmod(0o700)
    registry=R.AttemptRegistry(types.SimpleNamespace(source=root),object())
    registry._source_created=True;registry._selection_state='OWNED_CREATED'
    registry._source_identity=registry._dir_identity(root)
    case=root/'case'
    layout=types.SimpleNamespace(label='FixtureN',case_root=case,attempt_root=case/'attempt',
        intent_path=case/'intent/INTENT.json',supervision_root=case/'supervision',
        queue_root=case/'queue',validation_root=case/'validation')
    attempt=R.Attempt(registry,layout,1);registry._attempts[attempt.label]=attempt
    # Execute the exact source class body; only its surrounding native verify
    # port is inert. Returning at the existing finished-case guard excludes
    # unrelated native receipt synthesis while testing the real timer boundary.
    tree=ast.parse(S_PATH.read_bytes())
    enclosing=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='bind_active_run_root')
    node=next(n for n in enclosing.body if isinstance(n,ast.ClassDef) and n.name=='BoundConsumers')
    usage=types.SimpleNamespace(ru_utime=0.,ru_stime=0.)
    state={'deadlines':{'FixtureN':owner},'primary':{'FixtureN':(0,usage,usage)},
           'phase':'NESTED_RETURNED','finished':{'FixtureN'}}
    ns=dict(vars(S));ns.update(registry=registry,state=state,sentinel=object(),
        nested_label=lambda label:label,verify_native=lambda **kwargs:None)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),str(S_PATH),'exec'),ns)
    bound=object.__new__(ns['BoundConsumers']);ns['bound']=bound
    return S,owner,ports,registry,attempt,bound

def retained(registry):return [e for e in registry._errors if e is not None]

class Retirement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):(D/'validation/tmp').mkdir(exist_ok=True)
    def check_failed(self,owner,ports,registry,attempt,errors,primary=None):
        expected=([primary] if primary is not None else [])+[e for e in errors if e is not None]
        self.assertEqual(retained(registry),expected)
        for got,want in zip(retained(registry),expected):self.assertIs(got,want)
        self.assertIs(attempt.error,expected[0])
        self.assertIsNotNone(attempt.traceback)
        self.assertTrue(owner.finished);self.assertFalse(owner.retired)
        self.assertEqual(ports.calls,['cancel','restore'])
        self.assertEqual(len(attempt.uncertain),1)
        for index,error in enumerate(errors):
            self.assertIs(owner.retirement_errors[index],error)
            if error is not None:
                tb=owner.retirement_tracebacks[index];self.assertIsNotNone(tb)
                frames=[]
                while tb is not None:frames.append(tb.tb_frame.f_code);tb=tb.tb_next
                self.assertIn((Ports.setitimer if index==0 else Ports.signal).__code__,frames)
    def test_reproduce_frozen_predecessor_secondary_loss(self):
        old=load('frozen_failed_timer_subject',D.parent/'implementation/source/fresh_supervisor.py')
        E=RuntimeError('cancel');S=RuntimeError('restore');ports=Ports((E,S))
        old.signal=ports;old.time=types.SimpleNamespace(monotonic_ns=lambda:100)
        owner=old.DeadlineOwner(1000);owner.started=True
        with self.assertRaises(RuntimeError) as caught:owner.finish()
        self.assertIs(caught.exception,E);self.assertEqual(ports.calls,['cancel','restore'])
        self.assertFalse(hasattr(owner,'retirement_errors'))
    def test_actual_failure_finalizer_preserves_both_errors(self):
        errors=(RuntimeError('cancel'),RuntimeError('restore'))
        _,owner,ports,registry,attempt,bound=subject(errors)
        bound.finish_case('FixtureN');self.check_failed(owner,ports,registry,attempt,errors)
        tbs=tuple(owner.retirement_tracebacks)
        bound.finish_case('FixtureN')
        self.assertEqual(ports.calls,['cancel','restore'])
        self.assertEqual(tuple(owner.retirement_tracebacks),tbs)
    def test_supplied_working_primary_precedes_both_retirement_errors(self):
        errors=(RuntimeError('cancel'),RuntimeError('restore'))
        _,owner,ports,registry,attempt,bound=subject(errors)
        P=RuntimeError('working')
        try:raise P
        except RuntimeError:pass
        original_tb=P.__traceback__
        bound.finish_case('FixtureN',P)
        self.check_failed(owner,ports,registry,attempt,errors,P)
        self.assertIs(attempt.traceback,original_tb)
    def test_actual_primary_endpoint_forwards_order_then_raises_first(self):
        errors=(RuntimeError('cancel'),RuntimeError('restore'))
        _,owner,ports,registry,attempt,bound=subject(errors)
        with self.assertRaises(RuntimeError) as caught:bound.finish_primary('FixtureN')
        self.assertIs(caught.exception,errors[0]);self.check_failed(owner,ports,registry,attempt,errors)
        bound.finish_case('FixtureN',errors[0])
        self.assertEqual(ports.calls,['cancel','restore'])
        self.assertEqual(retained(registry),list(errors))
    def test_single_failure_flags_preserve_known_operation(self):
        for errors in ((RuntimeError('cancel'),None),(None,RuntimeError('restore'))):
            with self.subTest(errors=errors):
                _,owner,ports,registry,attempt,bound=subject(errors)
                bound.finish_case('FixtureN');self.check_failed(owner,ports,registry,attempt,errors)
                self.assertEqual(owner.timer_cancel_known,errors[0] is None)
                self.assertEqual(owner.handler_restore_known,errors[1] is None)
    def test_success_means_both_operations_known_and_no_uncertainty(self):
        _,owner,ports,registry,attempt,bound=subject((None,None))
        result=bound.finish_primary('FixtureN')
        self.assertTrue(owner.finished and owner.retired and owner.timer_cancel_known and owner.handler_restore_known)
        self.assertEqual(ports.calls,['cancel','restore']);self.assertEqual(retained(registry),[])
        self.assertEqual(attempt.uncertain,[]);self.assertEqual(result['primary_end_monotonic_ns'],100)

if __name__=='__main__':unittest.main(verbosity=2)

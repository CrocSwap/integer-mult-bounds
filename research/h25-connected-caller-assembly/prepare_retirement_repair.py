"""Version a static source repair without changing the reviewed failed subject."""
import ast
import json
from pathlib import Path

D=Path(__file__).resolve().parent
N=D/'repair-v2'
assert not N.exists()
N.mkdir()
for p in (D/'implementation').rglob('*'):
    if not p.is_file():continue
    rel=p.relative_to(D);q=N/rel;q.parent.mkdir(parents=True,exist_ok=True)
    raw=p.read_bytes()
    if '/stages/' not in str(p) and p.suffix in ('.py','.json'):
        raw=raw.replace(str(D).encode(),str(N).encode())
    q.write_bytes(raw);q.chmod(0o444)
for name in ('build_source_assembly.py','freeze_source_assembly.py'):
    text=(D/name).read_text()
    if name=='freeze_source_assembly.py':
        text=text.replace("jobs[mode].pop('bootstrap')","jobs[mode].pop('bootstrap',None)")
        text=text.replace("profile['required'].append(","profile['required'].append(")
    (N/name).write_text(text)
(N/'control').mkdir()
(N/'validation').mkdir()
test=(D/'validation/test_source_assembly.py').read_text()
test=test.replace("OLD=D.parent/'caller-proof-completion-20261107T0155Z'", "OLD=Path("+repr(str(D.parent/'caller-proof-completion-20261107T0155Z'))+")")
(N/'validation/test_source_assembly.py').write_text(test)
p=N/'implementation/source/fresh_supervisor.py';s=p.read_text()
s=s.replace('        self.poisoned = False\n','        self.poisoned = False\n        # entered-once is separate from known successful native retirement.\n        self.timer_cancel_known = self.handler_restore_known = False\n        self.retired = False\n        self.retirement_errors = [None, None]\n        self.retirement_tracebacks = [None, None]\n',1)
start=s.index('    def finish(self):\n',s.index('class DeadlineOwner:'))
end=s.index('\n\ndef pop_deadline_preserving',start)
s=s[:start]+'''    def finish(self):
        need(self.started and not self.finished, 'one timer retirement')
        self.finished = True  # Entered once; never retry an uncertain operation.
        first, tb = None, None
        try:
            signal.setitimer(signal.ITIMER_REAL, 0)
            self.timer_cancel_known = True
        except BaseException as error:
            self.retirement_errors[0] = error
            self.retirement_tracebacks[0] = BaseException.__dict__['__traceback__'].__get__(error,BaseException)
            first, tb = error, self.retirement_tracebacks[0]
        try:
            signal.signal(signal.SIGALRM, self.old_handler)
            self.handler_restore_known = True
        except BaseException as error:
            self.retirement_errors[1] = error
            self.retirement_tracebacks[1] = BaseException.__dict__['__traceback__'].__get__(error,BaseException)
            if first is None:
                first, tb = error, self.retirement_tracebacks[1]
        self.retired = self.timer_cancel_known and self.handler_restore_known
        if first is not None:
            raise BaseException.with_traceback(first,tb)


def finish_deadline_retaining(owner, registry, attempt):
    """Forward caught retirement errors in operation order, retaining raw slots."""
    first, tb = None, None
    try:
        owner.finish()
    except BaseException as error:
        first, tb = error, BaseException.__dict__['__traceback__'].__get__(error,BaseException)
    for error in owner.retirement_errors:
        if error is not None:
            registry.capture_error(attempt,error)
    if not owner.retired:
        registry.mark_uncertain(attempt,'timer cancellation or handler restoration not known complete; retirement entered once, no retry')
    if first is not None:
        raise BaseException.with_traceback(first,tb)
''' +s[end:]
s=s.replace("owner=state['deadlines'][label];owner.checkpoint();owner.finish()", "owner=state['deadlines'][label];owner.checkpoint()\n            finish_deadline_retaining(owner,registry,registry.attempt(nested_label(label)))")
old="""            owner=state['deadlines'].get(label)
            if owner is not None and owner.started and not owner.finished:
                try: owner.finish()
                except BaseException as failure:
                    registry.capture_error(registry.attempt(label),failure)
                    if error is None: error=failure
            attempt = registry.attempt(nested_label(label))
            registry.assert_open(attempt)
"""
new="""            attempt = registry.attempt(nested_label(label))
            registry.assert_open(attempt)
            if error is not None:
                registry.capture_error(attempt,error)  # Working primary precedes retirement.
            owner=state['deadlines'].get(label)
            if owner is not None and owner.started and not owner.finished:
                try: finish_deadline_retaining(owner,registry,attempt)
                except BaseException as failure:
                    registry.capture_error(attempt,failure)
                    if error is None: error=failure
"""
assert old in s;s=s.replace(old,new,1)
ast.parse(s);p.chmod(0o600);p.write_text(s);p.chmod(0o444)
(N/'control/REPAIR-SCOPE-v1.json').write_text(json.dumps({'failed_source_commit':'aa7d64cfc74c1e771054c4f17f162dd57bd38c06','change':'Retain both timer-retirement errors and tracebacks in owner slots; forward operation order at actual BoundConsumers finalizers; capture working primary first; separate entered from native retirement known.','runtime_execution':False,'original_credit_delta':0},indent=2)+'\n')
print(str(N))

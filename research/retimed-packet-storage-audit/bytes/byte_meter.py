"""Observe exact work-file byte endpoints without changing source operations."""
from contextlib import contextmanager
from pathlib import Path
import inspect
import sys


def need(ok, reason):
    if not ok:
        raise AssertionError(reason)


def aliases(old, new):
    result = []
    for module in tuple(sys.modules.values()):
        if module is None or not hasattr(module, '__dict__'):
            continue
        for name, value in tuple(vars(module).items()):
            if value is old:
                setattr(module, name, new)
                result.append((module, name))
    return result


def capacities(frame, count):
    name, loc = frame.f_code.co_name, frame.f_locals
    if name == 'quotient_right_route':
        p, t = loc['slots'] * loc['block'], loc['slots'] * loc['n']**2
        return [p, t, p, t, t, p, t, p, t, p]
    if name == 'route' and Path(frame.f_code.co_filename).name == 'receiver.py':
        return [loc['self'].volume]
    if name in ('high_packet', 'lower_tape', 'negate_tape'):
        return [loc['volume']] * count
    if name == 'affine_packet':
        return [loc['side']**loc['fields'] * loc['piece']] * count
    if name == 'unit_scale':
        return [loc['size']] * count
    if name == 'odd_step':
        return [loc['side'] * loc['branch_piece']] * count
    if name == 'carry_step':
        return [loc['base'] * loc['branch_piece']] * count
    if name == 'cold_swap_tape':
        return [loc['volume']] * 2 + [loc['volume'] // 9] * 9
    if name == 'type_route':
        padded = loc['rows'] * loc['extent'] * loc['suffix_bytes']
        return [padded] * 2 + [padded // 3] * 3
    raise AssertionError('unclassified work-file site: ' + name)


class File:
    def __init__(self, raw, meter, key, cap):
        self.raw, self.meter, self.key, self.cap = raw, meter, key, cap
        self.peak = 0
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def tell(self):
        return self.raw.tell()

    def endpoint(self):
        self.peak = max(self.peak, self.raw.tell())
        if self.peak > self.cap and self.meter.failure is None:
            self.meter.failure = 'role byte cap exceeded: ' + self.key
            raise AssertionError(self.meter.failure)

    def seek(self, *args):
        value = self.raw.seek(*args)
        self.endpoint()
        return value

    def read(self, *args):
        value = self.raw.read(*args)
        self.endpoint()
        return value

    def write(self, data):
        value = self.raw.write(data)
        self.endpoint()
        return value

    def truncate(self, size=None):
        size = self.tell() if size is None else size
        at = self.raw.tell()
        self.raw.seek(size)
        while block := self.raw.read(65536):
            if any(block):
                self.meter.failure = self.meter.failure or 'truncated a dirty byte extent'
                raise AssertionError(self.meter.failure)
        self.raw.seek(at)
        return self.raw.truncate(size)

    def close(self):
        if self.closed:
            return
        self.raw.seek(0, 2)
        if self.raw.tell() != 0:
            self.meter.failure = self.meter.failure or 'work file returned without physical erasure'
            raise AssertionError(self.meter.failure)
        self.meter.highs[self.key] = max(self.meter.highs.get(self.key, 0), self.peak)
        self.meter.limits[self.key] = max(self.meter.limits.get(self.key, 0), self.cap)
        self.meter.open_roles.remove(self.key)
        self.raw.close()
        self.closed = True


class Meter:
    def __init__(self):
        self.stage = 0
        self.allocation = []
        self.open_roles = set()
        self.highs, self.limits = {}, {}
        self.failure = None
        self.maximum_open = 0
        self.previous_calls = 0

    def bind(self):
        import streaming_routes
        self.module = streaming_routes
        self.original_work = streaming_routes.work_tapes
        self.original_file = streaming_routes.TemporaryFile

        def observed(count):
            frame = inspect.currentframe().f_back
            caps = capacities(frame, count)
            need(len(caps) == count, 'wrong role arity')
            site = str(self.stage) + ':' + Path(frame.f_code.co_filename).name + ':' + frame.f_code.co_qualname
            state = {'site': site, 'caps': caps, 'index': 0}

            @contextmanager
            def scope():
                self.allocation.append(state)
                try:
                    with self.original_work(count) as files:
                        yield files
                finally:
                    need(self.allocation.pop() is state, 'work-file scopes crossed')
            return scope()

        def factory():
            state = self.allocation[-1]
            i = state['index']
            state['index'] += 1
            key = state['site'] + ':' + str(i)
            need(key not in self.open_roles, 'same-stage role reentered while live')
            self.open_roles.add(key)
            self.maximum_open = max(self.maximum_open, len(self.open_roles))
            return File(self.original_file(), self, key, state['caps'][i])

        streaming_routes.TemporaryFile = factory
        self.changed = aliases(self.original_work, observed)
        return self

    def previous(self, source, target, digits, prefix, gap, suffix):
        from streaming_routes import cold_swap_tape
        self.previous_calls += 1
        self.stage += 1
        try:
            return cold_swap_tape(source, target, digits, prefix, gap, suffix)
        finally:
            self.stage -= 1

    def unbind(self):
        for module, name in self.changed:
            setattr(module, name, self.original_work)
        self.module.TemporaryFile = self.original_file
        if self.open_roles and self.failure:
            raise AssertionError(self.failure)
        need(not self.open_roles and not self.allocation, 'work-file ownership survived return')

    def report(self):
        return {'historical_role_bytes': self.highs, 'role_caps': self.limits,
                'local_historical_bytes': sum(v for k, v in self.highs.items() if k.startswith('0:')),
                'earlier_stage_historical_bytes': sum(v for k, v in self.highs.items() if not k.startswith('0:')),
                'maximum_open_work_files': self.maximum_open, 'earlier_stage_calls': self.previous_calls}

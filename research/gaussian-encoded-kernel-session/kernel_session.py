"""Persistent physical Gaussian setup. JoyboyBrian; OpenAI assistance; Apache-2.0.
Exact source code-object binding changes only Window.prepare_schur's inverse
site. The private cache is NOT an inverse API for arbitrary matrices.
"""
from types import FunctionType
from gaussian_sources import active
active()
from cardinal_counts import Count
from encoded import compare
from gaussian_axis import Axis
from gaussian_matrix import Matrix, inverse
from gaussian_window import Window
from records import Tape
from scratch_pool import ScratchPool
from session import OuterScope, borrowed_count, erase_marker, sealed_constructors
from ring_words import Signed
from words import BLANK, RIGHT, need


class KernelSession:
    """Frozen axis/kernel/bandwidth for the entire session; one cache entry."""
    def __init__(self, s, t, u, w, precision):
        self.pool = ScratchPool(1024)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        self.axis = self.cache = None
        self.closed = self.pending = False
        self.misses = self.hits = self.evictions = 0  # diagnostic only
        parameters = tuple(borrowed_count(x) for x in (s,t,u,w,precision))
        original = Window.prepare_schur
        namespace = dict(original.__globals__)
        namespace['inverse'] = self._old_kernel_inverse
        bound = FunctionType(original.__code__, namespace, original.__name__,
                             original.__defaults__, original.__closure__)
        # A fixed source specialization, not data-dependent code generation.
        class SessionWindow(Window):
            prepare_schur = bound
        self.window_type = SessionWindow
        try:
            with sealed_constructors(), self.scope.installed():
                self.axis = Axis(*parameters, self.pool)
        except BaseException:
            self.close()
            raise
        finally:
            for x in parameters:x.rewind()

    def _old_kernel_inverse(self, block):
        # Sole caller: unchanged source prepare_schur on this session's Axis.
        # The immutable axis kernel and bandwidth are part of the lifetime ABI.
        if self.cache is not None and compare(self.cache.rows, block.rows) == 0:
            self.hits += 1
            return Matrix(self.cache.rows, self.cache.columns, self.pool, self.cache.get)
        if self.cache is not None:
            self.cache.close()
            self.cache = None
            self.evictions += 1
        self.misses += 1
        result = inverse(block)
        try:
            self.cache = Matrix(result.rows, result.columns, self.pool, result.get)
            return result
        except BaseException:
            result.close()
            raise

    def run(self, target_start, target_length, core_start, core_length, precision):
        need(not self.closed and not self.pending, 'consume prior protected session page')
        integers = tuple(borrowed_count(x) for x in (target_length,core_length,precision))
        start_magnitude = borrowed_count(target_start.magnitude)
        core_magnitude = borrowed_count(core_start.magnitude)
        parameters = (*integers,start_magnitude,core_magnitude)
        need(all(x.tape not in (*self.pool.tapes,self.output) for x in parameters), 'external session window parameters')
        start = Signed(start_magnitude, target_start.negative)
        core = Signed(core_magnitude, core_start.negative)
        need(self.output.read() == BLANK, 'empty owned page output')
        window = None
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    window = self.window_type(self.axis,start,integers[0],core,integers[1],integers[2],self.pool)
                    window.page.rewind()
                    while window.page.read() != BLANK:
                        symbol = window.page.read()
                        need(symbol in (0,1,RIGHT), 'canonical protected page alphabet')
                        self.output.append(symbol)
                        window.page.step(1)
                finally:
                    if window is not None:window.close()
            self.output.rewind()
            self.pending = True
            return self.output
        except BaseException:
            self.output.clear()
            raise
        finally:
            for x in parameters:x.rewind()

    def consume(self):
        need(not self.closed and self.pending, 'one live protected page')
        self.output.clear()
        self.pending = False

    def close(self):
        if self.closed:return
        self.output.clear()
        with sealed_constructors(), self.scope.installed():
            if self.cache is not None:
                self.cache.close()
                self.cache = None
            if self.axis is not None:
                self.axis.close()
                self.axis = None
            self.pool.empty()
        for tape in (*self.pool.tapes,self.output):erase_marker(tape)
        self.closed = True
        self.pending = False

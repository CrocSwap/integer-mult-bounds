"""Select a compiled Compact action only at a consumed, closed boundary."""
import phase_sources
phase_sources.activate()
from compact_engine import CompactEngine
from words import BLANK,need


class PairDispatch(CompactEngine):
    def __init__(self,names,actions,default_target,native):
        actions = tuple(actions)
        self.actions = frozenset(actions)
        initial = actions[0] if actions else (None,default_target,False)
        super().__init__(names,*initial,native)

    def select(self,action):
        need(action in self.actions, "action belongs to the compiled monomial word")
        need(self.closed and self.output.read() == BLANK and not self.pool.live and
             self.binary.closed and self.binary.native.closed, "closed consumed Compact action boundary")
        self.source,self.target,self.late = action

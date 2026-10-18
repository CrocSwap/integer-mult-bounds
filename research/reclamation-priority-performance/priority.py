"""Exact retired-slot geometry and priority index for the pinned compiler.

Apache-2.0. Prepared for Peter Carpenter with substantial OpenAI Codex assistance.
The compiler and its original contributor notices are retained unchanged.
"""


class RankedSlots:
    """A set with descending-current-rank, ascending-slot iteration.

    Call move before changing a retired slot's frame. The compiler does not
    resume ordered iteration after a clearing XOR changes any frame.
    """

    def __init__(self, max_rank, state_of):
        self.members = set()
        self.masks = [0] * (max_rank + 1)
        self.core_masks = [0] * max_rank
        self.union_masks = [0] * max_rank
        self.universe = (1 << max_rank) - 1
        self.all_mask = 0
        self.state_of = state_of

    def __contains__(self, slot):
        return slot in self.members

    def __len__(self):
        return len(self.members)

    def __iter__(self):
        return iter(self.members)

    def add(self, slot):
        if slot in self.members:
            return
        rank, frame = self.state_of(slot)
        self.masks[rank] |= 1 << slot
        self.all_mask |= 1 << slot
        self._change_frame(slot, (0, 0), frame)
        self.members.add(slot)

    def remove(self, slot):
        self.members.remove(slot)
        rank, frame = self.state_of(slot)
        self.masks[rank] &= ~(1 << slot)
        self.all_mask &= ~(1 << slot)
        self._change_frame(slot, frame, (0, 0))

    def move(self, slot, new_rank, new_frame):
        if slot in self.members:
            old_rank, old_frame = self.state_of(slot)
            bit = 1 << slot
            if old_rank != new_rank:
                self.masks[old_rank] &= ~bit
                self.masks[new_rank] |= bit
            self._change_frame(slot, old_frame, new_frame)

    def _change_frame(self, slot, old, new):
        for masks, before, after in zip((self.core_masks, self.union_masks), old, new):
            changed = before ^ after
            while changed:
                bit = changed & -changed
                masks[bit.bit_length() - 1] ^= 1 << slot
                changed ^= bit

    def eligible(self, frame):
        core, union = frame
        eligible = self.all_mask
        while core:
            bit = core & -core
            eligible &= self.core_masks[bit.bit_length() - 1]
            core ^= bit
        outside = self.universe ^ union
        while outside:
            bit = outside & -outside
            eligible &= ~self.union_masks[bit.bit_length() - 1]
            outside ^= bit
        return eligible

    def ordered(self, frame):
        eligible = self.eligible(frame)
        for mask in reversed(self.masks):
            mask &= eligible
            while mask:
                bit = mask & -mask
                yield bit.bit_length() - 1
                mask ^= bit

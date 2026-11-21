"""Compare simultaneous ownership with total issuance in the real schedulers."""

from random import Random

from periodic import Job, Rule, make_planner, run
from spool import Arena
from tape_meter import Motion


class SlotProbe:
    """Hold one owner across each yield and issue one independent child."""

    def __init__(self, rule, width):
        self.rule = rule
        self.next = width
        self.live = set(range(width))
        self.vacant = []
        self.frames = self.allocations = self.leaves = 0

    def fresh(self):
        if self.vacant:
            slot = self.vacant.pop()
        else:
            slot = self.next
            self.next += 1
        assert slot not in self.live
        self.live.add(slot)
        self.allocations += 1
        return slot

    def retire(self, slot):
        self.live.remove(slot)
        self.vacant.append(slot)
        assert self.next == len(self.live) + len(self.vacant)

    def native(self, ports, columns):
        self.frames += 1
        assert len({job.owner for job in ports}) == len(ports)
        held = self.fresh()
        for paid in self.rule.paid:
            child = self.fresh()
            yield Job(child, tuple(range(columns * paid)))
            self.retire(child)
        self.retire(held)

    def zero(self, job):
        return Job(self.fresh(), job.axes)

    def retire_zero(self, job):
        self.retire(job.owner)

    def leaf(self, job):
        assert job.owner in self.live
        self.leaves += 1


def forest():
    rule, rank = Rule(6, (4, 5), (3,)), 1296
    planner = make_planner(rule)
    spec = planner(rank)
    probe = SlotProbe(rule, spec.width)
    axes = tuple(range(rank))
    run(rule, rank, [Job(i, axes) for i in range(spec.width)], probe, planner=planner)
    rounded = 16 * spec.width // 15
    slots = rounded + 2 * (spec.forest.height + 1) * rounded * 15 // 14
    assert probe.live == set(range(spec.width)) and probe.leaves == spec.leaves
    assert probe.next <= slots and probe.allocations > probe.next
    print(
        "active forest",
        spec.width,
        "restored owners",
        probe.frames,
        "frames",
        probe.allocations,
        "allocations",
        probe.next,
        "historical slots",
        flush=True,
    )


def arena():
    rng = Random(102)
    peaks = [0] * 4
    calls = [0] * 4
    motion = Motion()

    def walk(frame, depth):
        calls[depth] += 1
        fields = []
        high = 0
        for _ in range(64):
            if not fields or rng.randrange(9) < 5:
                cell = frame.field()
                cell.clear()
                fields.append(cell)
            else:
                fields.pop(rng.randrange(len(fields))).retire()
            high = max(high, len(fields))
            assert frame.live == len(fields) and frame.high == high
            if depth < 3 and rng.randrange(15) == 0:
                with frame.child(3 - depth) as child:
                    assert child.start == frame.start + high * frame.extent
                    walk(child, depth + 1)
                assert frame.high == high
        for field in fields:
            field.retire()
        assert frame.live == 0 and len(frame.free) == high
        peaks[depth] = max(peaks[depth], high * frame.extent)

    with motion.tape() as tape:
        walk(Arena(4, 1, tape=tape), 0)
        assert motion.peak <= sum(peaks)
    assert motion.live == 0
    print(
        "positive arena",
        sum(calls),
        "calls",
        motion.peak,
        "historical bytes",
        sum(peaks),
        "sum of depth maxima",
        flush=True,
    )


if __name__ == "__main__":
    forest()
    arena()

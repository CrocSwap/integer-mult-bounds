"""Independent administrative cost/rollback controls with trivial stage jobs.

These do not witness a numerical MOVE; check_move.py does that separately.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import json
from atomic_move import AtomicMove, S
from move_sources import need


class Identity:
    def run(self, field, context):
        pass


class Change:
    def run(self, field, context):
        raw = field.tape
        raw.write(1-raw.read())


class Reject:
    def run(self, field, context):
        raise S.leaf.linear.CoefficientDomainError("inexact Gaussian halving")


def block(width):
    return ([0, 0, 0]*width + [0, 1, 0])*2


def instance():
    stage, field, context = (S.codec.DenseTape(i) for i in (5, 9, 11))
    owner = object.__new__(AtomicMove)
    owner.work = (stage,)
    owner.field, owner.stage = S.abi.CodedPort(field), S.abi.CodedPort(stage)
    owner.context = S.abi.BinaryContextPort(context)
    owner.entry = owner.leaf = owner.exit = Identity()
    return owner, stage, field, context


def run(width, reject=False, reuse=None):
    owner, stage, field, context = instance() if reuse is None else reuse
    data = block(width)
    field.cells[field.origin:] = bytearray(data)
    field.head = field.origin
    owner.entry = Change() if reject else Identity()
    owner.leaf = Reject() if reject else Identity()
    before = sum(t.actions() for t in (stage, field, context))
    rejected = False
    try:
        owner.run()
    except S.leaf.linear.CoefficientDomainError:
        rejected = True
    need(rejected == reject, "expected toy administrative outcome")
    need(list(field.cells[field.origin:]) == data, "protected original or complete identity commit")
    need(all(x == 6 for x in stage.cells[stage.origin:]), "complete stage retirement")
    need(all(t.head == t.origin for t in (stage, field, context)), "returned local heads")
    actions = sum(t.actions() for t in (stage, field, context))-before
    expected = (13*len(data)+21+2) if reject else (22*len(data)+35)
    need(actions == expected, "exact administrative action formula")
    return dict(width=width, V=len(data), physical_actions=actions,
                rejected=reject, stage_backing=len(stage.cells)), (owner, stage, field, context)


def check():
    normal = [run(width)[0] for width in range(2, 26)]
    rejections = [run(width, reject=True)[0] for width in (2, 3, 8, 25)]
    large, state = run(25)
    small, _state = run(2, reuse=state)
    need(small["physical_actions"] == normal[0]["physical_actions"]
         and small["stage_backing"] == large["stage_backing"] > normal[0]["stage_backing"],
         "short-call cost and honest retained backing")
    owner, stage, field, context = instance()
    initial = block(2); field.cells[field.origin:] = bytearray(initial)
    Change().run(owner.field, owner.context)
    try:
        Reject().run(owner.field, owner.context)
    except S.leaf.linear.CoefficientDomainError:
        pass
    need(list(field.cells[field.origin:]) != initial, "unstaged composition fails whole-input rollback")
    return dict(identity_cases=normal, rejection_cases=rejections,
                shrinking_reuse=small, no_staging_mutant_rejected=True,
                numerical_move_claim=False)


if __name__ == "__main__":
    print(json.dumps(check(), sort_keys=True))

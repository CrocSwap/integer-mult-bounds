"""own16.py PLAN8 OWNERS8 OUT.json.gz [MOVES.json|858] [EXPECTED_IDLE_JSON]
Duplicate a T8 owner map into two interleaved 8-replica groups (#858 build_owners.duplicate) and apply the
explicit whole-role moves (time, helper, width, old(rep,child,port,off), new(...)). When EXPECTED_IDLE_JSON is
given, also run #858's structural audit() (cloned-window screen, whole helpers, prefix footprints, exact idle
profile), its omitted-move controls (each single omitted move must be rejected) and the exact changed-role count."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_owners as B


def build(plan8, owners8, edits):
    roles = B.duplicate(owners8)
    key = {(r['time'], r['helper']): r for r in roles}
    for t, h, w, old, new in edits:
        r = key[t, h]
        B.require(B.location(r) == tuple(old) and r['width'] == w, 'edit source mismatch %s' % ((t, h),))
        B.move(r, tuple(new), plan8)
    return roles


if __name__ == '__main__':
    plan8, owners8 = B.read(sys.argv[1]), B.read(sys.argv[2])
    edits = []
    if len(sys.argv) > 4:
        edits = B.EDITS if sys.argv[4] == '858' else json.loads(Path(sys.argv[4]).read_text())
    edits = tuple((t, h, w, tuple(o), tuple(n)) for t, h, w, o, n in edits)
    roles = build(plan8, owners8, edits)
    receipt = dict(roles=len(roles), moves=len(edits))
    if len(sys.argv) > 5:
        B.EXPECTED_IDLE = {int(k): v for k, v in json.loads(sys.argv[5]).items()}
        B.EDITS = edits
        receipt['idle_profile'] = B.audit(roles, plan8)
        receipt['omitted_move_controls_rejected'] = len(B.controls(roles, plan8))
        B.require(receipt['omitted_move_controls_rejected'] == len(edits), 'omitted-move controls')
        changed = sum(a != b for a, b in zip(B.duplicate(owners8), roles))
        B.require(changed == len(edits), 'exact changed-role count')
        receipt['changed_roles'] = changed
    Path(sys.argv[3]).write_bytes(B.portable_gzip(B.canonical(roles)))
    print(json.dumps(receipt))

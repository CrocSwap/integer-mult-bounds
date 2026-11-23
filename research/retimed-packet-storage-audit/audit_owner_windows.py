"""Check historical Gaussian owner bases with holes and changing child widths."""
from io import BytesIO
from pathlib import Path
from textwrap import dedent
import argparse
import inspect
import json
import sys


def need(ok, reason):
    if not ok:
        raise AssertionError(reason)


class ObservedTape(BytesIO):
    def __init__(self):
        super().__init__()
        self.peak = 0
        self.retired_suffixes = 0

    def write(self, data):
        count = super().write(data)
        self.peak = max(self.peak, self.tell())
        return count

    def truncate(self, size=None):
        size = self.tell() if size is None else size
        need(not any(self.getvalue()[size:]), 'truncated an unerased historical suffix')
        self.retired_suffixes += 1
        return super().truncate(size)


def contents(field):
    pos = field.stream.tell()
    field.stream.seek(0)
    data = field.stream.read(field.count * field.record)
    field.stream.seek(pos)
    return data


def fixture():
    from spool import Arena
    tape = ObservedTape()
    parent = Arena(4, 1, tape)
    roots = [parent.field() for _ in range(4)]
    for i, field in enumerate(roots):
        field.stream.write(bytes([i + 1]) * parent.extent)
    # The live fields are not a prefix: indices 1 and 3 survive.
    roots[0].retire()
    roots[2].retire()
    need((parent.live, parent.high) == (2, 4), 'fixture did not leave historical holes')
    zero = parent.field()
    zero.clear()
    need((parent.live, parent.high) == (3, 4), 'temporary zero was not an owned slot')
    expected_peak = parent.high * parent.extent
    rows = []
    for bits, count in ((3, 3), (1, 2), (2, 5), (0, 3), (3, 4)):
        with parent.child(bits) as child:
            need(child.start == parent.start + parent.high * parent.extent,
                 'child starts before historical parent end')
            fields = [child.field() for _ in range(count)]
            for i, field in enumerate(fields):
                field.stream.write(bytes([17 + i]) * child.extent)
            fields[0].retire()
            need(child.high == count and child.live == count - 1,
                 'child historical slot count changed on retirement')
            with child.child(0) as inner:
                need(inner.start == child.start + child.high * child.extent,
                     'nested child omitted a retired historical slot')
                leaves = [inner.field() for _ in range(3)]
                for field in leaves:
                    field.stream.write(b'xy')
                expected_peak = max(expected_peak, inner.start + inner.high * inner.extent)
                for field in leaves:
                    field.retire()
            for i, field in enumerate(fields[1:], 1):
                need(contents(field) == bytes([17 + i]) * child.extent,
                     'nested child changed parent owner')
                field.retire()
            rows.append({'bits': bits, 'owners_high': child.high,
                         'start': child.start, 'slot_bytes': child.extent})
        need(contents(roots[1]) == bytes([2]) * parent.extent,
             'first retained parent owner changed')
        need(contents(roots[3]) == bytes([4]) * parent.extent,
             'last retained parent owner changed')
        need(contents(zero) == bytes(parent.extent), 'temporary zero was lost')
        need(tape.peak == expected_peak, 'historical maximum differs from active-path sum')
    zero.retire()
    roots[1].retire()
    roots[3].retire()
    need(not any(tape.getvalue()), 'root dirty byte survived retirement')
    parent.close()
    return {'sibling_windows': rows, 'historical_peak': tape.peak,
            'cleared_child_suffixes': tape.retired_suffixes}


def smallest_hole_example():
    from spool import Arena
    parent = Arena(0, 1, BytesIO())
    first, retained = parent.field(), parent.field()
    first.stream.write(b'aa')
    retained.stream.write(b'bb')
    first.retire()
    with parent.child(0) as child:
        base = child.start
        field = child.field()
        field.stream.write(b'cc')
        field.retire()
    need(contents(retained) == b'bb', 'live-count base destroyed the retained parent slot')
    retained.retire()
    parent.close()
    return base


def negative_control():
    from spool import Arena
    original = Arena.child
    source = dedent(inspect.getsource(original))
    old, new = 'self.start + self.high * self.extent', 'self.start + self.live * self.extent'
    need(source.count(old) == 1, 'historical-base mutation has no unique source site')
    namespace = dict(inspect.unwrap(original).__globals__)
    exec(compile(source.replace(old, new), '<live-count-base-control>', 'exec'), namespace)
    Arena.child = namespace['child']
    try:
        try:
            smallest_hole_example()
        except AssertionError as error:
            need(str(error) == 'live-count base destroyed the retained parent slot',
                 'historical-base control failed for a different reason')
            return str(error)
        raise AssertionError('historical-base mutation survived')
    finally:
        Arena.child = original


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--runtime', type=Path, required=True)
    cli.add_argument('--output', type=Path, required=True)
    args = cli.parse_args()
    sys.path.insert(0, str(args.runtime.resolve()))
    from upstream import install
    install()
    result = fixture()
    result.update(status='passed', smallest_correct_base=smallest_hole_example(),
                  rejected_control=negative_control())
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print('PASS_HISTORICAL_OWNER_WINDOWS', result['historical_peak'])


if __name__ == '__main__':
    main()

"""Adverse current-format/source controls, independent of the source C suite.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from dataclasses import replace
import json
from pathlib import Path
import shutil
import tempfile
from check_leaf import DenseTape, body, encoded_header, fixture, load, run_case
from leaf_provider import Provider, S
from leaf_sources import HERE, authenticate, need
from selected_service import Service, source_boundary


def rejected(call, text):
    try:
        call()
    except ValueError as error:
        need(text in str(error), "expected negative-control reason: " + text + "; saw " + str(error))
        return
    raise ValueError("negative control unexpectedly accepted: " + text)


def run_controls():
    event, source = source_boundary()
    for bad in (replace(event, rank=2), replace(event, fields=(237,)),
                replace(event, token=("local", 9897, event.token[-1]))):
        rejected(lambda bad=bad: Service(bad), "exact actual current PAID")

    service = Service(event)
    work = tuple(DenseTape(4 + i % 3) for i in range(service.port_count))
    field, context = DenseTape(9), DenseTape(11)
    values, initial, expected = fixture(f=2, K=1, r=2)
    load(field, initial); header = encoded_header(values); load(context, header)
    service.bind(work, {236: S.abi.CodedPort(field)}, S.abi.BinaryContextPort(context))
    service.run()
    need(body(field) == expected and body(context) == header, "actual selected-token current leaf return")
    need(all(t.head == t.origin and all(v == 6 for v in t.cells[t.origin:]) for t in work),
         "selected-token private retirement")

    # Root/segment identities, not just virtual port object identities.
    duplicate = [DenseTape() for _ in range(Provider().port_count)]
    owner = Provider()
    duplicate[-1] = duplicate[0]
    rejected(lambda: owner.bind(duplicate), "distinct leaf inventory")
    good = tuple(DenseTape() for _ in range(owner.port_count))
    owner.bind(good)
    same = DenseTape()
    rejected(lambda: owner.run(S.abi.CodedPort(same), S.abi.BinaryContextPort(same)), "distinct current field")
    rejected(lambda: owner.run(S.abi.CodedPort(good[0]), S.abi.BinaryContextPort(DenseTape())), "distinct current field")

    original_prepare = Provider.prepare
    def wrong_offset(self, header, h, cleanup):
        from cardinal_counts import Count
        widths, rho, fields, rows = original_prepare(self, header, h, cleanup)
        wrong = Count(header["rho"]); cleanup.callback(wrong.close)
        return widths, wrong, fields, rows
    Provider.prepare = wrong_offset
    try:
        rejected(lambda: run_case(f=1, K=2, rho=0), "independent direct Gaussian tensor endpoint")
    finally:
        Provider.prepare = original_prepare

    original_axis = S.coefficient.c_axis
    def wrong_direction(*args):
        return original_axis(*args[:-1], not args[-1])
    S.coefficient.c_axis = wrong_direction
    try:
        rejected(lambda: run_case(f=1), "independent direct Gaussian tensor endpoint")
    finally:
        S.coefficient.c_axis = original_axis

    # Original bytes, complete manifest, one semantic source mutation.
    with tempfile.TemporaryDirectory(prefix="current-leaf-source-control-") as temporary:
        target = Path(temporary)
        shutil.copyfile(HERE / "DEPENDENCIES.json", target / "DEPENDENCIES.json")
        shutil.copytree(HERE / "vendor", target / "vendor")
        source_file = target / "vendor/leaf/signed_linear.py"
        source_file.write_bytes(source_file.read_bytes().replace(b"ROWS = ((1,-1,1,1)", b"ROWS = ((1,1,1,1)", 1))
        rejected(lambda: authenticate(target), "unchanged computational source")

    # No ordinary supplier is needed even at the current physical ABI.
    original_ordinary = S.base.ordinary.Ordinary.__init__
    def forbidden(*args, **kwargs):
        raise ValueError("ordinary supplier must not be constructed by direct leaf")
    S.base.ordinary.Ordinary.__init__ = forbidden
    try:
        no_ordinary = run_case(f=1, before=0, after=0, r=1)
    finally:
        S.base.ordinary.Ordinary.__init__ = original_ordinary

    return dict(
        source=source, source_token_fixture_records=values["outer"] * values["rows"] * (1 << values["within_bits"]),
        reduced_descriptor_fixture=True, full_rank9_selected_packet_executed=False,
        rejected_controls=9, ordinary_service_calls=0, direct_leaf_without_ordinary=no_ordinary)


def main():
    print("PASS_CURRENT_LEAF_CONTROLS " + json.dumps(run_controls(), sort_keys=True))


if __name__ == "__main__":
    main()

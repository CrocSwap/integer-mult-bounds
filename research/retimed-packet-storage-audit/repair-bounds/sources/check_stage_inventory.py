"""Check the allocation sites reached from the installed signed caller."""

import ast
import inspect
from importlib import import_module
from textwrap import dedent


# Include the nested event generators and the callbacks that these functions return.
BODIES = {
    "ordinary_carrier": "ordinary_swap ternary stage_body",
    "triangular_ordinary": "root_body",
    "binary_receiver": "Receiver.__init__ Receiver.weighted Receiver.compiled",
    "receiver": "Receiver.weighted Receiver.storage Receiver.transition Receiver.compensate Receiver.serve_line OwnerBanks.route",
    "same_order_body": "SameOrderBody.body_ordinary SameOrderBody.weighted",
    "five_exchange": "direct_line same_order_line",
    "growing_binary": "pipe",
    "direct_body": "direct_route scale_atom",
    "module_atoms": "lower_tape negate_tape weighted_pair",
    "quotient_route": "affine_packet high_packet sort_packets quotient_right_route",
    "limb_scale": "unit_scale",
    "raw_binary": "Banks.start Banks.zero Banks.read Banks.install Banks.retire Banks.clone Banks.swap Banks.xor BinarySource.inner",
    "strong_binary": "StrongBinarySource.raw",
    "raw_binary_stage": "BinaryWord.native run",
    "streaming_routes": "cold_swap_tape type_route negate_field shift_field integer_scale work_tapes",
    "compact_crt": "binary_swap",
    "stack_tapes": "FileHead Page PacketStack Arena",
    "transport": "Recipe.open Plan.run Plan.decode Plan.events",
    "retimed_supplier": "Raw.native Positive._run",
    "positive_dispatch": "native_h h_pack",
    "positive": "Positive.apply Positive.hadamard one_axis",
    "complex_stage": "place_and_apply",
    "raw48": "ComplexRaw.raw ComplexRaw.graph ComplexRaw.align ComplexRaw.unalign ComplexRaw.chart ComplexRaw.fresh ComplexRaw.retire",
    "compact_columns": "Columns.one Columns.row Columns.repair",
    "spool": "scratch snapshot Segment Arena Field",
}
RAW_GENERATORS = {
    "strong_binary.StrongBinarySource.raw", "raw_binary.BinarySource.inner",
    "raw_binary_stage.BinaryWord.native", "raw48.ComplexRaw.raw",
    "raw48.ComplexRaw.graph", "retimed_supplier.Raw.native", "transport.Plan.events",
}
PAGE_ARITIES = {
    "chart-line": 2, "chart-packet": 2, "compiler": 3, "direct-coordinate": 2,
    "exposed-leaf": 2, "issued-leaf": 1, "matcher": 2, "triangular-body": 2, "weighted": 2,
}


def inventory():
    import band_product
    import binary_receiver
    import complex_stage
    import direct_body
    import five_exchange
    import ordinary_carrier
    import positive
    import positive_dispatch
    import raw48
    import receiver
    import retimed_supplier
    import same_order_body
    import spool

    assert band_product.Positive is retimed_supplier.Positive
    assert band_product.ordinary_swap is ordinary_carrier.ordinary_swap
    assert band_product.h_pack is positive_dispatch.h_pack
    assert positive_dispatch.place_and_apply is complex_stage.place_and_apply
    assert binary_receiver.Receiver.__mro__[1:3] == (receiver.Receiver, same_order_body.SameOrderBody)
    assert receiver.direct_line is direct_body.direct_line is five_exchange.direct_line
    assert receiver.same_order_line is five_exchange.same_order_line
    assert retimed_supplier.ComplexRaw is raw48.ComplexRaw
    assert retimed_supplier.Positive.__base__ is positive.Positive
    assert positive.Arena is spool.Arena

    pages = set()
    work = []
    yields = set()
    calls_weighted = set()
    binds_weighted = set()
    for module, names in BODIES.items():
        source = import_module(module)
        for name in names.split():
            body = source
            for part in name.split("."):
                body = getattr(body, part)
            symbol = module + "." + name
            nodes = list(ast.walk(ast.parse(dedent(inspect.getsource(body)))))
            for node in nodes:
                if isinstance(node, ast.Call):
                    func = ast.unparse(node.func).rsplit(".", 1)[-1]
                    if func == "pipe":
                        pages.add((ast.literal_eval(node.args[1]), 2))
                    if func == "frames" and isinstance(node.args[0], ast.Constant):
                        pages.add(tuple(ast.literal_eval(arg) for arg in node.args[:2]))
                    if func == "work_tapes":
                        work.append(ast.literal_eval(node.args[0]))
                    if func == "weighted":
                        calls_weighted.add(symbol)
                    if symbol == "transport.Plan.decode":
                        assert func not in {"work_tapes", "scratch", "snapshot", "TemporaryFile"}
                if symbol in RAW_GENERATORS:
                    if isinstance(node, (ast.Yield, ast.YieldFrom)):
                        yields.add(symbol)
                    if isinstance(node, (ast.With, ast.AsyncWith)):
                        assert not any(isinstance(child, (ast.Yield, ast.YieldFrom))
                                       for child in ast.walk(node))
                if module == "five_exchange" and isinstance(node, ast.Attribute) and node.attr == "weighted":
                    binds_weighted.add(symbol)

    assert pages == set(PAGE_ARITIES.items())
    assert sum(PAGE_ARITIES.values()) + 2 == 20  # Add both packet stacks.
    assert max(work) == 22 and sum(work) == 91
    assert yields == RAW_GENERATORS
    assert calls_weighted == {"binary_receiver.Receiver.weighted", "receiver.Receiver.weighted",
                              "same_order_body.SameOrderBody.body_ordinary", "receiver.Receiver.serve_line"}
    assert binds_weighted == {"five_exchange.direct_line", "five_exchange.same_order_line"}
    return PAGE_ARITIES

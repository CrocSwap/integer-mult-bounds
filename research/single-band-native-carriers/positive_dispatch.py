"""Bind the striped numerical tensor to its installed dyadic carrier."""

from compact_columns import Columns
from complex_stage import place_and_apply
from positive import Positive
from product_path import Product as RetainedProduct
from spool import Field, transfer
from striped_tensor import hadamard_tape


def native_h(field, low, h, window, offset, precision, swap, rank_log, make_supplier):
    digits = (precision + 1).bit_length()
    digit = 4 * digits + 6
    # At equality the positive operation already consists only of primitive leaves.
    if (h - 1).bit_length() <= rank_log or window < 128 * digit:
        columns = Columns(window, offset, digit, 0, 0, 0, 0, swap)
        Positive(None, None, h).hadamard(field, low, h, columns)
        return
    supplier = make_supplier()
    carrier = supplier.carrier
    if carrier.bit_length() - 1 != rank_log or carrier & (carrier - 1):
        raise ArithmeticError("The installed numerical carrier differs from the public rank")
    layers = 2 + (h.bit_length() + rank_log - 1) // rank_log
    rows = (supplier.owners.bit_length() - 1) * layers
    place_and_apply(field, low, h, window, offset, rows, digit, digits**2, swap, supplier)


def h_pack(machine, tape, start, end, bit, rank_log, make_supplier):
    """Apply the installed numerical word to each spectator stripe, then restore it."""
    if machine.total <= 4096:
        # Every stripe here takes the source's local integer H kernel.
        return RetainedProduct.h(machine, tape, start, end, bit)
    positions = tuple(machine.starts[i] + bit for i in range(start, end))

    def apply(source, target, width, selected, record):
        if end - start != len(selected):
            raise ArithmeticError("The spectator stripe lost a selected window")
        field = Field(width, machine.wide)
        extent = (1 << width) * record
        transfer(source, field.stream, extent)
        native_h(
            field,
            selected[0] - bit,
            len(selected),
            machine.widths[start],
            bit,
            machine.P,
            machine.exchange,
            rank_log,
            make_supplier,
        )
        field.stream.seek(0)
        transfer(field.stream, target, extent)
        field.retire()

    tape.seek(0)
    hadamard_tape(tape, machine.widths, positions, machine.p, 2 * machine.wide, apply)
    machine.h_calls += 1

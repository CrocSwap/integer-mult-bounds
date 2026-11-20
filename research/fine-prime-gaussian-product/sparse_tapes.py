"""Execute each compact cyclic Gaussian boundary line on sequential word tapes."""
from contextlib import closing
from math import prod

from crt_route import Banks, export_field, import_field
from fine_ring import tz
from word_multiply import product


def transfer(source, target, count):
    for _ in range(count):
        target.append(source.read())


def move_rows(field, rows, columns, inverse, owner):
    """Transpose a complete list of rectangles with a possibly ragged last group."""
    size = len(field.cells)
    if size % (rows * columns):
        raise ValueError("incomplete sparse rectangle")
    if min(rows, columns) == 1:
        return field
    levels = range((rows - 1).bit_length())
    for k in reversed(levels) if inverse else levels:
        width = 1 << k
        out = owner.make(field.width)
        field.home()
        for _ in range(size // (rows * columns)):
            for start in range(0, rows, 2 * width):
                a = min(width, rows - start)
                b = min(width, rows - start - a)
                if not b:
                    transfer(field, out, a * columns)
                    continue
                left = owner.make(field.width)
                right = owner.make(field.width)
                if inverse:
                    for _ in range(columns):
                        transfer(field, left, a)
                        transfer(field, right, b)
                else:
                    transfer(field, left, a * columns)
                    transfer(field, right, b * columns)
                left.home()
                right.home()
                if inverse:
                    transfer(left, out, a * columns)
                    transfer(right, out, b * columns)
                else:
                    for _ in range(columns):
                        transfer(left, out, a)
                        transfer(right, out, b)
                left.release()
                right.release()
        field.release()
        field = out
    return field


def coefficient_tape(word_page, owner):
    if not word_page.width:
        raise ValueError("online Gaussian requires dyadic coefficient words")
    bank = owner.make(word_page.width * 8 + 1)
    for value in word_page:
        bank.append((value,0))
    return bank


def checked(z, width):
    if abs(z[0]).bit_length() >= width or abs(z[1]).bit_length() >= width:
        raise ArithmeticError("Gaussian sparse accumulator overflow")
    return z


def add(z, v, width):
    return checked((z[0] + v[0], z[1] + v[1]), width)


def sub(z, v, width):
    return checked((z[0] - v[0], z[1] - v[1]), width)


def scale(page, z, unit, width):
    c = page.read()[0]
    return checked((tz(product(c, z[0], page.trace), unit),
                    tz(product(c, z[1], page.trace), unit)), width)


def at(field, i):
    field.seek(i)
    return field.read()


def multiply_line(line, page, offsets, unit, owner):
    n = len(line.cells)
    width = line.width
    out = owner.make(width)
    page.home()
    for i in range(n):
        value = (0,0)
        for h in offsets:
            x = at(line, (i + h) % n)
            value = add(value, scale(page, x, unit, width), width)
        out.append(value)
    if page.head != len(page.cells):
        raise ValueError("unused band coefficients")
    return out


def solve_line(line, lower, upper, w, unit, owner):
    n = len(line.cells)
    m = n - w
    width = line.width
    z = owner.make(width)
    edge = owner.make(width)
    for _ in range(w):
        edge.append((0,0))
    line.home()
    lower.home()
    for i in range(m):
        value = line.read()
        for j in range(max(0, i - w), i):
            value = sub(value, scale(lower, at(z,j), unit, width), width)
        z.seek(i)
        z.append(value)
        edge.home()
        for j in range(w):
            previous = edge.read()
            edge.replace(j, sub(previous, scale(lower, value, unit, width), width))
    edge.home()
    for i in range(m,n):
        value = add(line.read(), edge.read(), width)
        for j in range(m,i):
            value = sub(value, scale(lower, at(z,j), unit, width), width)
        z.seek(i)
        z.append(value)
    edge.release()
    if lower.head != len(lower.cells):
        raise ValueError("unused lower coefficients")

    upper.home()
    # Keep the far border on its own tape. It is read in every core row.
    border = owner.make(width)
    core = owner.make(width)
    for i in reversed(range(m,n)):
        value = at(z,i)
        for j in range(i + 1,n):
            value = sub(value, scale(upper, at(border,n - 1 - j), unit, width), width)
        border.seek(n - 1 - i)
        border.append(scale(upper, value, unit, width))
    for i in reversed(range(m)):
        value = at(z,i)
        for j in range(i + 1, min(m, i + w + 1)):
            value = sub(value, scale(upper, at(core,m - 1 - j), unit, width), width)
        for j in range(m,n):
            value = sub(value, scale(upper, at(border,n - 1 - j), unit, width), width)
        core.seek(m - 1 - i)
        core.append(scale(upper, value, unit, width))
    if upper.head != len(upper.cells):
        raise ValueError("unused upper coefficients")
    z.release()
    out = owner.make(width)
    for bank in (core,border):
        for j in reversed(range(len(bank.cells))):
            out.append(at(bank,j))
        bank.release()
    return out


def correct_field(values, baseline, shape, axis, carve, residual, condensed, word_bits, trace):
    """Add R or -R+R F^-1 R to an independent baseline in physical tensor order."""
    size = prod(shape)
    t = shape[axis]
    suffix = prod(shape[:axis])
    prefix = prod(shape[axis + 1:])
    a = carve.boundary_size()
    if carve.target != t or residual.size != a or (condensed is not None and condensed.size != a):
        raise ValueError("inconsistent Gaussian sparse extents")
    base_bits = residual.bits
    if base_bits is None or (condensed is not None and base_bits != condensed.bits):
        raise ValueError("inconsistent Gaussian correction grids")
    unit = 1 << base_bits
    before = trace.travel
    with closing(Banks(trace)) as owner:
        source = import_field(values, size, word_bits, owner)
        base = import_field(baseline, size, word_bits, owner)
        mask = owner.make(2)
        for k in range(t):
            mask.append((int(carve.boundary(k)),0))
        compact = owner.make(word_bits)
        source.home()
        for _ in range(prefix):
            mask.home()
            for _ in range(t):
                selected = mask.read()[0]
                for _ in range(suffix):
                    z = source.read()
                    if selected:
                        compact.append(z)
        source.release()
        lines = move_rows(compact, a, suffix, False, owner)
        lines.home()
        layout_travel = trace.travel - before
        rpage = coefficient_tape(residual.coefficients, owner)
        if condensed is not None:
            lower = coefficient_tape(condensed.forward, owner)
            upper = coefficient_tape(condensed.backward, owner)
        updated = owner.make(word_bits)
        for _ in range(size // t):
            line = owner.make(word_bits)
            transfer(lines, line, a)
            first = multiply_line(line,rpage,residual.offsets,unit,owner)
            line.release()
            if condensed is None:
                first.home()
                transfer(first,updated,a)
            else:
                solved = solve_line(first,lower,upper,condensed.width,unit,owner)
                second = multiply_line(solved,rpage,residual.offsets,unit,owner)
                solved.release()
                first.home()
                second.home()
                for _ in range(a):
                    updated.append(sub(second.read(), first.read(), word_bits))
                second.release()
            first.release()
        lines.release()
        if condensed is not None:
            lower.release()
            upper.release()
        rpage.release()
        resumed = trace.travel
        returned = move_rows(updated, a, suffix, True, owner)
        returned.home()
        base.home()
        out = owner.make(word_bits)
        for _ in range(prefix):
            mask.home()
            for _ in range(t):
                selected = mask.read()[0]
                for _ in range(suffix):
                    v = base.read()
                    out.append(add(v, returned.read(), word_bits) if selected else v)
        if returned.head != len(returned.cells):
            raise ValueError("unused sparse return")
        answer = export_field(out)
    layout_travel += trace.travel - resumed
    return answer, layout_travel

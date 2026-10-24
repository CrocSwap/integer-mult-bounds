"""Independent exact endpoint oracles for inverse-dirty register programs.

The free-group oracle expands operator words literally and is limited by its
support cap. The matrix oracle checks one supplied finite-dimensional operator
assignment; neither oracle compiles or validates certificates. Witness vectors
corroborate an endpoint calculation and do not establish shortestness.

Prepared for Krzysztof Wójt with OpenAI Codex assistance. Apache-2.0.
"""

from __future__ import annotations

from typing import Any

try:
    from .fields import Field
except ImportError:  # Also support running sibling research scripts directly.
    from fields import Field


WordKey = tuple[int, tuple[int, ...]]


def _field(program: dict[str, Any]) -> Field:
    return Field(program["field"])


def _prepend(symbol: int, word: tuple[int, ...]) -> tuple[int, ...]:
    """Prepend a newly applied generator and reduce the free-group word."""
    if word and word[0] == -symbol:
        return word[1:]
    return (symbol,) + word


def _add_word_term(
    target: dict[WordKey, Any],
    key: WordKey,
    value: Any,
    field: Field,
) -> None:
    total = field.add(target.get(key, field.zero), value)
    if field.is_zero(total):
        target.pop(key, None)
    else:
        target[key] = total


def _word_endpoint_side(
    program: dict[str, Any], instructions: list[dict[str, Any]], field: Field, support_cap: int
) -> list[dict[WordKey, Any]]:
    roles = program["roles"]
    operators = {name: index for index, name in enumerate(program["operators"], start=1)}
    registers: list[dict[WordKey, Any]] = [
        {(index, ()): field.one} for index in range(len(roles))
    ]
    role_index = {role: index for index, role in enumerate(roles)}

    def check_support() -> None:
        count = sum(len(register) for register in registers)
        if count > support_cap:
            raise ValueError(
                f"literal free-group support {count} exceeds support_cap={support_cap}"
            )

    check_support()
    for instruction in instructions:
        op = instruction["op"]
        dst = role_index[instruction["dst"]]
        if op == "linear":
            updated: dict[WordKey, Any] = {}
            for source_role, raw_coefficient in instruction["terms"]:
                coefficient = field.parse(raw_coefficient)
                for key, value in registers[role_index[source_role]].items():
                    _add_word_term(
                        updated, key, field.mul(coefficient, value), field
                    )
            registers[dst] = updated
        elif op == "apply":
            symbol = operators[instruction["operator"]] * instruction["direction"]
            updated = {}
            for (input_index, word), value in registers[dst].items():
                updated[(input_index, _prepend(symbol, word))] = value
            registers[dst] = updated
        elif op == "query":
            source = role_index[instruction["src"]]
            symbol = operators[instruction["operator"]] * instruction["direction"]
            coefficient = field.parse(instruction["coefficient"])
            updated = dict(registers[dst])
            for (input_index, word), value in registers[source].items():
                key = (input_index, _prepend(symbol, word))
                _add_word_term(
                    updated, key, field.mul(coefficient, value), field
                )
            registers[dst] = updated
        else:  # The input contract says programs are already validated.
            raise ValueError(f"unknown instruction op {op!r}")
        check_support()
    return registers


def reduced_word_endpoint(
    program: dict[str, Any], support_cap: int = 100_000
) -> list[dict[WordKey, Any]]:
    """Return each left-minus-right role as an exact reduced free-group sum.

    Keys are ``(input_role_index, signed_generator_word)``. Generator indices
    follow ``program["operators"]`` starting at 1. A positive symbol means the
    named operator and a negative symbol its inverse. Every role starts as an
    independent input register. Expansion is literal and raises ``ValueError``
    if the combined live support exceeds ``support_cap``.
    """
    if support_cap < 0:
        raise ValueError("support_cap must be nonnegative")
    field = _field(program)
    left = _word_endpoint_side(program, program["left"], field, support_cap)
    right = _word_endpoint_side(program, program["right"], field, support_cap)
    result: list[dict[WordKey, Any]] = []
    for left_role, right_role in zip(left, right):
        difference = dict(left_role)
        for key, value in right_role.items():
            _add_word_term(difference, key, field.neg(value), field)
        result.append(difference)
    if sum(len(register) for register in result) > support_cap:
        raise ValueError(
            f"literal free-group support exceeds support_cap={support_cap}"
        )
    return result


def _parse_matrix(raw: list[list[Any]], field: Field, name: str) -> list[list[Any]]:
    if not isinstance(raw, list) or any(not isinstance(row, list) for row in raw):
        raise ValueError(f"operator {name!r} must be a square list matrix")
    size = len(raw)
    if any(len(row) != size for row in raw):
        raise ValueError(f"operator {name!r} must be square")
    return [[field.parse(value) for value in row] for row in raw]


def _inverse(matrix: list[list[Any]], field: Field) -> list[list[Any]]:
    """Invert a square matrix by exact Gauss-Jordan elimination."""
    size = len(matrix)
    augmented = [
        list(row)
        + [field.one if row_index == column else field.zero for column in range(size)]
        for row_index, row in enumerate(matrix)
    ]
    width = 2 * size
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if not field.is_zero(augmented[row][column])),
            None,
        )
        if pivot is None:
            raise ValueError("operator matrix is singular and cannot be inverted")
        if pivot != column:
            augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        pivot_value = augmented[column][column]
        augmented[column] = [field.div(value, pivot_value) for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            if field.is_zero(factor):
                continue
            augmented[row] = [
                field.sub(augmented[row][entry], field.mul(factor, augmented[column][entry]))
                for entry in range(width)
            ]
    return [row[size:] for row in augmented]


def _zero_matrix(size: int, field: Field) -> list[list[Any]]:
    return [[field.zero for _ in range(size)] for _ in range(size)]


def _matrix_add_scaled(
    left: list[list[Any]], right: list[list[Any]], coefficient: Any, field: Field
) -> list[list[Any]]:
    return [
        [field.add(a, field.mul(coefficient, b)) for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def _matrix_scale(
    matrix: list[list[Any]], coefficient: Any, field: Field
) -> list[list[Any]]:
    return [[field.mul(coefficient, value) for value in row] for row in matrix]


def _matrix_multiply(
    left: list[list[Any]], right: list[list[Any]], field: Field
) -> list[list[Any]]:
    size = len(left)
    return [
        [
            _dot(left[row], [right[index][column] for index in range(size)], field)
            for column in range(size)
        ]
        for row in range(size)
    ]


def _dot(left: list[Any], right: list[Any], field: Field) -> Any:
    total = field.zero
    for a, b in zip(left, right):
        total = field.add(total, field.mul(a, b))
    return total


def _matrix_is_zero(matrix: list[list[Any]], field: Field) -> bool:
    return all(field.is_zero(value) for row in matrix for value in row)


def _literal_endpoint_side(
    program: dict[str, Any],
    instructions: list[dict[str, Any]],
    matrices: dict[str, list[list[Any]]],
    inverse_cache: dict[str, list[list[Any]]],
    size: int,
    field: Field,
) -> list[dict[int, list[list[Any]]]]:
    roles = program["roles"]
    role_index = {role: index for index, role in enumerate(roles)}
    identity = [
        [field.one if row == column else field.zero for column in range(size)]
        for row in range(size)
    ]
    registers: list[dict[int, list[list[Any]]]] = [
        {index: [row[:] for row in identity]} for index in range(len(roles))
    ]

    for instruction in instructions:
        op = instruction["op"]
        dst = role_index[instruction["dst"]]
        if op == "linear":
            updated: dict[int, list[list[Any]]] = {}
            for source_role, raw_coefficient in instruction["terms"]:
                coefficient = field.parse(raw_coefficient)
                for input_index, block in registers[role_index[source_role]].items():
                    total = _matrix_add_scaled(
                        updated.get(input_index, _zero_matrix(size, field)),
                        block,
                        coefficient,
                        field,
                    )
                    if _matrix_is_zero(total, field):
                        updated.pop(input_index, None)
                    else:
                        updated[input_index] = total
            registers[dst] = updated
        elif op == "apply":
            name = instruction["operator"]
            if instruction["direction"] == 1:
                operator_matrix = matrices[name]
            else:
                if name not in inverse_cache:
                    inverse_cache[name] = _inverse(matrices[name], field)
                operator_matrix = inverse_cache[name]
            registers[dst] = {
                input_index: _matrix_multiply(operator_matrix, block, field)
                for input_index, block in registers[dst].items()
            }
        elif op == "query":
            name = instruction["operator"]
            if instruction["direction"] == 1:
                operator_matrix = matrices[name]
            else:
                if name not in inverse_cache:
                    inverse_cache[name] = _inverse(matrices[name], field)
                operator_matrix = inverse_cache[name]
            coefficient = field.parse(instruction["coefficient"])
            updated = dict(registers[dst])
            for input_index, block in registers[role_index[instruction["src"]]].items():
                transformed = _matrix_multiply(operator_matrix, block, field)
                total = _matrix_add_scaled(
                    updated.get(input_index, _zero_matrix(size, field)),
                    transformed,
                    coefficient,
                    field,
                )
                if _matrix_is_zero(total, field):
                    updated.pop(input_index, None)
                else:
                    updated[input_index] = total
            registers[dst] = updated
        else:  # The input contract says programs are already validated.
            raise ValueError(f"unknown instruction op {op!r}")
    return registers


def literal_endpoint(
    program: dict[str, Any], operators: dict[str, list[list[Any]]]
) -> list[list[list[list[Any]]]]:
    """Return all exact left-minus-right matrix blocks for one operator choice.

    The result is indexed ``[output_role][input_role][row][column]``. Missing
    blocks are returned as full zero matrices. If the program has no operators
    and ``operators`` is empty, the otherwise-undetermined matrix dimension is
    taken to be 1. Inverses use exact Gauss-Jordan elimination over the program
    field; singular matrices raise ``ValueError``.
    """
    field = _field(program)
    matrices = {
        name: _parse_matrix(raw, field, name) for name, raw in operators.items()
    }
    named_operators = program["operators"]
    missing = [name for name in named_operators if name not in matrices]
    if missing:
        raise ValueError(f"missing matrices for named operators: {missing!r}")

    dimensions = {len(matrix) for matrix in matrices.values()}
    if len(dimensions) > 1:
        raise ValueError("all operator matrices must have the same dimension")
    size = next(iter(dimensions), 1)
    inverse_cache: dict[str, list[list[Any]]] = {}
    left = _literal_endpoint_side(
        program, program["left"], matrices, inverse_cache, size, field
    )
    right = _literal_endpoint_side(
        program, program["right"], matrices, inverse_cache, size, field
    )
    zero = _zero_matrix(size, field)
    minus_one = field.neg(field.one)
    result: list[list[list[list[Any]]]] = []
    for left_blocks, right_blocks in zip(left, right):
        output: list[list[list[Any]]] = []
        for input_index in range(len(program["roles"])):
            output.append(
                _matrix_add_scaled(
                    left_blocks.get(input_index, zero),
                    right_blocks.get(input_index, zero),
                    minus_one,
                    field,
                )
            )
        result.append(output)
    return result


def unipotent_operators(
    program: dict[str, Any], word: list[str]
) -> dict[str, list[list[Any]]]:
    """Build the standard upper-shift unipotent assignment for ``word``."""
    field = _field(program)
    names = program["operators"]
    unknown = [name for name in word if name not in names]
    if unknown:
        raise ValueError(f"word contains operators absent from the program: {unknown!r}")
    size = len(word) + 1
    result: dict[str, list[list[Any]]] = {}
    for name in names:
        matrix = [
            [field.one if row == column else field.zero for column in range(size)]
            for row in range(size)
        ]
        for index, symbol in enumerate(word):
            if symbol == name:
                matrix[index][index + 1] = field.one
        result[name] = matrix
    return result


def apply_witness(
    program: dict[str, Any], word: list[str], input_role: str
) -> list[list[Any]]:
    """Apply the unipotent endpoint difference to ``e_last`` in one role.

    This is a concrete witness calculation for corroboration only; it does not
    prove a shortest witness or a universal endpoint distinction.
    """
    if input_role not in program["roles"]:
        raise ValueError(f"unknown input role {input_role!r}")
    operators = unipotent_operators(program, word)
    endpoint = literal_endpoint(program, operators)
    input_index = program["roles"].index(input_role)
    last_column = len(word)
    return [
        [endpoint[output_index][input_index][row][last_column]
         for row in range(last_column + 1)]
        for output_index in range(len(program["roles"]))
    ]


__all__ = [
    "reduced_word_endpoint",
    "literal_endpoint",
    "unipotent_operators",
    "apply_witness",
]

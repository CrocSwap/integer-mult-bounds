"""Check the input-only logger without importing its producer.

The exact forward and reverse interpreters are adapted from the prior
independent campaign review. Research used OpenAI Codex under the user's
direction.
"""

from collections import Counter
from fractions import Fraction as Q


def require(condition, message):
    if not condition:
        raise ValueError(message)


def decode(rows):
    return [{int(j): Q(value) for j, value in row.items()} for row in rows]


def plus(target, source, coefficient=1):
    for j, value in source.items():
        value = target.get(j, Q(0)) + coefficient * value
        if value:
            target[j] = value
        else:
            target.pop(j, None)


def combine(coefficients, rows):
    value = {}
    for j, coefficient in coefficients.items():
        plus(value, rows[j], coefficient)
    return value


def transpose(rows, count):
    result = [{} for _ in range(count)]
    for j, row in enumerate(rows):
        for i, value in row.items():
            result[i][j] = value
    return result


def register(token):
    require(isinstance(token, list) and len(token) == 2, "Invalid register token")
    namespace, index = token
    require(namespace in ("L", "C") and isinstance(index, int), "Invalid register")
    require(0 <= index < (704 if namespace == "L" else 8), "Register out of range")
    return index + (704 if namespace == "C" else 0)


def adjoint(events):
    columns = [{j: Q(1)} for j in range(712)]
    for event in reversed(events):
        if event[0] != "scalar":
            continue
        gate = event[1]
        target = register(gate[1])
        tag = gate[0]
        if tag == "clear":
            require(target >= 704, "A borrowed field was cleared")
            columns[target] = {}
        elif tag == "scale":
            coefficient = Q(gate[2], gate[3])
            columns[target] = {j: coefficient * value for j, value in columns[target].items()}
        else:
            require(tag in ("copy", "add"), "Unknown scalar gate")
            source = register(gate[2])
            require(source != target, "A scalar gate aliases its source")
            coefficient = 1 if tag == "copy" else Q(gate[3], gate[4])
            plus(columns[source], columns[target], coefficient)
            if tag == "copy":
                columns[target] = {}
    return columns


def forward(events, initial):
    rows = [row.copy() for row in initial]
    for event in events:
        if event[0] != "scalar":
            continue
        gate = event[1]
        target = register(gate[1])
        if gate[0] == "clear":
            require(target >= 704, "A borrowed field was cleared")
            rows[target] = {}
        elif gate[0] == "scale":
            coefficient = Q(gate[2], gate[3])
            rows[target] = {j: coefficient * value for j, value in rows[target].items()}
        elif gate[0] == "copy":
            rows[target] = rows[register(gate[2])].copy()
        else:
            require(gate[0] == "add", "Unknown scalar gate")
            plus(rows[target], rows[register(gate[2])], Q(gate[3], gate[4]))
    return rows


def scalar_cost(gate):
    if gate[0] in ("clear", "copy"):
        return 2
    value = Q(*gate[-2:])
    numerator, denominator = abs(value.numerator), value.denominator
    require(numerator > 0 and denominator & (denominator - 1) == 0,
            "A scalar coefficient is not nonzero dyadic")
    if gate[0] == "scale":
        require(numerator & (numerator - 1) == 0, "A SCALE is not a dyadic unit")
        return 2 * (abs(numerator.bit_length() - denominator.bit_length()) + (value < 0))
    require(gate[0] == "add", "Unknown scalar price")
    return 2 * (2 + numerator.bit_length() + numerator.bit_count() + denominator.bit_length() - 1)


def multiply(left, right):
    return [combine(row, right) for row in left]


def same(rows, columns):
    return rows == [{i: Q(1)} for i in range(columns)]


def frame_check_prelude(events, word, ports):
    frames = [["input_C", p] for p in range(112)] + [0] * 112 + [None] * 488
    initial = frames[:704]
    children = []
    for event in events:
        if event[0] == "phase":
            continue
        if event[0] == "input_private_C":
            _, private, port, child_rank = event
            require(private == 0 and port in ports and child_rank == 1 and frames[704] == 0,
                    "An input child has the wrong binding")
            frames[704] = ["input_C", port]
            children.append(port)
            continue
        require(event[0] == "scalar", "An input prelude has an unknown event")
        gate, common = event[1:]
        target = register(gate[1])
        if gate[0] == "clear":
            require(target >= 704 and common == 0, "The prelude can clear only private fields in frame zero")
            frames[target] = 0
            continue
        require(gate[0] == "add" and frames[target] == common, "An input ADD target has the wrong frame")
        source = register(gate[2])
        require(source != target and frames[source] == common, "An input ADD source has the wrong frame")
        require((target >= 704 and 112 <= source < 224)
                or (112 <= target < 224 and source >= 704)
                or (target < 112 and source == 704), "The prelude accesses a helper or uses an illegal private source")
    require(frames[:704] == initial and frames[704] == 0 and all(value in (0, None) for value in frames[705:]),
            "The prelude changes persistent frames or leaves a private field in an input frame")
    return children


def frame_check_core(events, word):
    frames = list(word["start"]) + [None] * 8
    profile = Counter()
    for event in events:
        if event[0] == "climb":
            _, _, target, old, new, child_rank = event
            require(frames[target] == old, "A retained child has the wrong entry frame")
            frames[target] = new
            profile[child_rank] += 1
        elif event[0] == "scalar":
            gate, common = event[1:]
            target = register(gate[1])
            if gate[0] == "clear":
                require(target >= 704, "A borrowed field was cleared")
                frames[target] = common
            else:
                require(frames[target] == common, "A retained scalar target has the wrong frame")
                if gate[0] in ("add", "copy"):
                    source = register(gate[2])
                    require(source != target and frames[source] == common, "A retained scalar source has the wrong frame")
        else:
            require(event[0] in ("phase", "adapter", "residual_adapter"), "Unknown retained event")
    require(frames == word["final"] + [0] * 8, "The retained endpoint frames changed")
    return profile


def dyadic_inverse(matrix):
    n = len(matrix)
    rows = [[matrix[i].get(j, Q(0)) for j in range(n)]
            + [Q(i == j) for j in range(n)] for i in range(n)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i][j]), None)
        require(pivot is not None, "A source parameter is singular")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        value = rows[j][j]
        rows[j] = [entry / value for entry in rows[j]]
        for i in range(n):
            if i != j:
                value = rows[i][j]
                rows[i] = [entry - value * other for entry, other in zip(rows[i], rows[j])]
    result = [{j: rows[i][n+j] for j in range(n) if rows[i][n+j]} for i in range(n)]
    require(all(value.denominator & (value.denominator - 1) == 0
                for row in result for value in row.values()), "The inverse is not dyadic")
    return result


def response(parameter, Z):
    result = multiply(parameter, Z)
    for k, row in enumerate(result):
        plus(row, {k: Q(1)})
    return result


def expected_source(Z, parameter):
    result = [{p: Q(1)} for p in range(112)]
    for p, row in enumerate(multiply(Z, parameter)):
        plus(result[p], row)
    return result


def expected_prelude(Z, parameter, JZ, private_count):
    rows = [{i: Q(1)} for i in range(712)]
    for p, row in enumerate(multiply(JZ, parameter)):
        plus(rows[p], {112 + j: value for j, value in row.items()})
    for p, row in enumerate(expected_source(Z, parameter)):
        rows[112 + p] = {112 + j: value for j, value in row.items()}
    for private in range(private_count):
        rows[704 + private] = {}
    return rows


def source_snapshots(events, initial, parameter, streamed):
    require(events and events[0][0] == "phase", "The source update lacks its phase marker")
    current = [row.copy() for row in initial]
    seen, scatter_active = [], False
    private_seen, peak = set(), 0
    for event in events[1:]:
        if event[0] == "phase":
            continue
        require(event[0] == "scalar" and event[2] == 0, "A source update leaves frame zero")
        gate = event[1]
        require(gate[0] in ("add", "clear"), "The source update has an unknown scalar gate")
        if gate[0] == "clear":
            private = register(gate[1]) - 704
            require(0 <= private < (1 if streamed else 8), "The source update clears an unexpected buffer")
            if streamed:
                scatter_active = False
        elif gate[1][0] == "L":
            require(112 <= gate[1][1] < 224 and gate[2][0] == "C", "A source scatter has an illegal field")
            if not scatter_active:
                if streamed:
                    k = len(seen)
                    require(k < 8 and current[704] == {112+p: value for p, value in parameter[k].items()},
                            "A streamed snapshot contains an earlier source update")
                    seen.append(k)
                else:
                    require(not seen and all(current[704+k] == {112+p: value for p, value in parameter[k].items()}
                                             for k in range(8)), "A buffered snapshot contains an earlier source update")
                    seen = list(range(8))
                scatter_active = True
        else:
            require(gate[1][0] == "C" and gate[2][0] == "L" and 112 <= gate[2][1] < 224,
                    "A source query has an illegal read")
            require(not scatter_active, "A source scatter starts before its query snapshots are complete")
        current = forward([event], current)
        if gate[1][0] == "C":
            private_seen.add(gate[1][1])
        peak = max(peak, sum(bool(current[704+k]) for k in private_seen))
    require(seen == list(range(8)) and private_seen == set(range(1 if streamed else 8)),
            "The source query inventory changed")
    require(peak == (1 if streamed else 8) and all(not current[704+k] for k in private_seen),
            "The source snapshot lifetime changed")
    return current, peak


def verify(data, certificate, payload):
    word, R, J = data["word"], data["R"], data["J"]
    alpha = Q(certificate["alpha"])
    A, T = certificate["compensation_ports"], certificate["query_ports"]
    require(A == [0, 7, 20, 27, 36, 46, 57, 111]
            and T == [21, 37, 47, 76, 81, 87, 92, 110] and not set(A) & set(T),
            "The two disjoint selected minors changed")
    require(alpha == 14 and len(R) == 8 and len(J) == 112, "The actual dimensions or alpha changed")
    K = [{k: R[k][p] / 4 for k in range(8) if p in R[k]} for p in range(112)]
    require(multiply(R, K) == [{k: alpha} for k in range(8)], "RK is not alpha I")
    P = [row.copy() if p in A else {} for p, row in enumerate(K)]
    L = [{p: value for p, value in row.items() if p in T} for row in R]
    require(same(multiply(R, P), 8) and same(multiply(L, K), 8), "A selected minor is not a right inverse")
    Z = [row.copy() for row in K]
    for p, row in enumerate(P):
        plus(Z[p], row, 1-alpha)
    query = [row.copy() for row in R]
    for k, row in enumerate(L):
        plus(query[k], row, -1)
    JZ = multiply(J, Z)
    require(same(multiply(R, Z), 8) and same(multiply(L, Z), 8), "A complete or selected response is not identity")
    require(not any(multiply(query, Z)), "The logger query is not invariant under the source update")
    require(JZ == [{k: (1-alpha)*value for k, value in row.items()} for row in P],
            "JZ is not supported on the eight compensation ports")
    require(decode(payload["K_rows"]) == K and decode(payload["Z_rows"]) == Z
            and decode(payload["query_rows"]) == query and decode(payload["JZ_rows"]) == JZ,
            "A producer matrix differs from the independent source derivation")
    for p in range(112):
        require(word["start"][112+p] == 0 and word["frames"][word["start"][p]] == [word["ports"][p]],
                "The retained input convention changed")
    core = data["clean_programs"]["backward"]
    base_profile = frame_check_core(core, word)
    require(base_profile == Counter({1:2412, 2:418, 3:432, 4:142, 5:82}), "The retained native invoice changed")
    initial = [{i: Q(1)} for i in range(712)]
    base = forward(core, initial)
    expected_base = [row.copy() if i < 704 else {} for i, row in enumerate(initial)]
    for p, row in enumerate(J):
        plus(expected_base[p], {112+j: value for j, value in row.items()}, -1)
    require(base == expected_base and transpose(adjoint(core), 712) == base, "The retained arbitrary-input map changed")
    base_cost = sum(scalar_cost(event[1]) for event in core if event[0] == "scalar")
    require(base_cost == 202138, "The retained scalar invoice changed")
    mixed = [row.copy() for row in R]
    plus(mixed[1], R[0])
    small_mixed = [{k: Q(2)} for k in range(8)]
    small_mixed[1][0] = Q(1)
    require(response(mixed, Z) == small_mixed, "The mixed response is not 2I+E_10")
    mixed_inverse = [{j: -value for j, value in row.items()}
                     for row in multiply(dyadic_inverse(small_mixed), mixed)]
    parameters = {"query_log": query, "query_unlog": [{j:-value for j,value in row.items()} for row in query],
                  "non_diagonal": mixed, "non_diagonal_inverse": mixed_inverse}
    examples = payload["examples"]
    require(set(examples) == set(parameters), "The four-example inventory changed")
    receipts = {}
    for name, example in examples.items():
        parameter = parameters[name]
        streamed = name in ("query_log", "query_unlog")
        private_count = 1 if streamed else 8
        require(decode(example["B_rows"]) == parameter and example["streamed"] == streamed,
                "An example parameter or snapshot schedule changed")
        dyadic_inverse(response(parameter, Z))
        compensation = multiply(JZ, parameter)
        require([p for p,row in enumerate(compensation) if row] == A, "The input compensation does not use exactly eight rows")
        prelude, program = example["prelude"], example["program"]
        require(prelude == example["input_compensation"] + example["source_update"]
                and program == prelude + core, "A retained event or the input placement changed")
        require(frame_check_prelude(prelude, word, A) == A, "The input native child count or order changed")
        prep = forward(prelude, initial)
        require(prep == expected_prelude(Z, parameter, JZ, private_count)
                and transpose(adjoint(prelude), 712) == prep, "The input prelude map differs")
        after_compensation = forward(example["input_compensation"], initial)
        expected_compensation = [row.copy() for row in initial]
        expected_compensation[704] = {}
        for p,row in enumerate(compensation):
            plus(expected_compensation[p], {112+j:value for j,value in row.items()})
        require(after_compensation == expected_compensation, "The input compensation changes the source or other private fields")
        after_source, peak = source_snapshots(example["source_update"], after_compensation, parameter, streamed)
        require(after_source == prep, "The checked source snapshots do not reproduce the prelude")
        wanted = [row.copy() for row in base]
        for p,row in enumerate(expected_source(Z, parameter)):
            wanted[112+p] = {112+j:value for j,value in row.items()}
        require(transpose(adjoint(program), 712) == wanted, "A full word differs on an arbitrary input column")
        require(all(wanted[p] == {p:Q(1)} for p in range(224,704)) and all(not row for row in wanted[704:]),
                "A helper or private output differs")
        if name == "query_log":
            for p in T:
                require(wanted[112+p] == {112+j:value for j,value in combine(K[p], R).items()},
                        "A selected field does not contain K_T RY")
            require(multiply(L, expected_source(Z, parameter)) == R, "The selected query is not the original full query")
        read_cost = sum(scalar_cost(["add",["C",0],["L",j],value.numerator,value.denominator])
                        for row in compensation + parameter + Z for j,value in row.items())
        added = sum(scalar_cost(event[1]) for event in prelude if event[0] == "scalar")
        require(added == 8*12 + 8*4 + read_cost, "The derived scalar invoice differs from the literal word")
        if streamed:
            require(base_cost + added == 218794, "The reviewed logger scalar invoice changed")
        require(transpose(adjoint(example["source_update"] + core),712) != wanted,
                "Missing input compensation was not detected")
        first_child = next(i for i,event in enumerate(prelude) if event[0] == "input_private_C")
        rejected = False
        try:
            frame_check_prelude(prelude[:first_child] + prelude[first_child+1:], word, A)
        except ValueError:
            rejected = True
        require(rejected, "A missing input child was not detected")
        receipts[name] = {"formal_input_columns":712, "borrowed_helpers_restored":480, "private_outputs_zero":8,
                          "private_fields_used":private_count, "peak_live_source_snapshots":peak,
                          "added_rank_one_children":8, "added_address_maps":16,
                          "complete_native_profile":dict(sorted((base_profile+Counter({1:8})).items())),
                          "complete_native_rank_mass":5530, "complete_scalar_real_primitives":base_cost+added,
                          "added_scalar_real_primitives":added, "scalar_formula_fixed_term":128,
                          "missing_input_compensation_rejected":True, "missing_input_child_rejected":True}
    for first, second, private_count in (("query_log","query_unlog",1), ("non_diagonal","non_diagonal_inverse",8)):
        plus_pre, minus_pre = examples[first]["prelude"], examples[second]["prelude"]
        clear_private = [row.copy() for row in initial]
        for k in range(private_count):
            clear_private[704+k] = {}
        require(transpose(adjoint(plus_pre+minus_pre),712) == clear_private
                and transpose(adjoint(minus_pre+plus_pre),712) == clear_private,
                "The two inverse prelude orders fail")
    plus_pre = examples["query_log"]["prelude"]
    double_query = [{j:2*value for j,value in row.items()} for row in query]
    require(transpose(adjoint(plus_pre+plus_pre),712) == expected_prelude(Z,double_query,JZ,1),
            "Repeated input preparation does not add its parameter")
    combined = [row.copy() for row in query]
    source_after_log = expected_source(Z,query)
    for k,row in enumerate(multiply(mixed,source_after_log)):
        plus(combined[k],row)
    require(transpose(adjoint(plus_pre+examples["non_diagonal"]["prelude"]),712)
            == expected_prelude(Z,combined,JZ,8), "The source-family composition law fails")
    require(adjoint(examples["query_log"]["program"]+examples["query_unlog"]["program"])
            != [{j:Q(1)} if j<704 else {} for j in range(712)], "The full backward words were treated as inverses")
    example = examples["non_diagonal"]
    source = example["source_update"]
    positions = {i for i,event in enumerate(source) if event[0] == "scalar" and event[1][0] == "add"
                 and event[1][1][0] == "L" and event[1][2] == ["C",0]}
    first_column = [source[i] for i in sorted(positions)]
    require(len(first_column) == sum(0 in row for row in Z), "The mixed timing control lacks the first source column")
    remaining = [event for i,event in enumerate(source) if i not in positions]
    second_snapshot = remaining.index(["scalar",["clear",["C",1]],0])
    interleaved = remaining[:second_snapshot]+first_column+remaining[second_snapshot:]
    require(Counter(map(repr,interleaved)) == Counter(map(repr,source)), "The timing control changes the event inventory")
    bad_prelude = example["input_compensation"]+interleaved
    require(frame_check_prelude(bad_prelude,word,A) == A, "The timing control changes native access")
    predicted = transpose(adjoint(example["program"]),712)
    errors = [{112+j:row.get(1,Q(0))*value for j,value in R[0].items() if row.get(1,Q(0))*value} for row in Z]
    for p,row in enumerate(errors):
        plus(predicted[112+p],row)
    for p,row in enumerate(multiply(J,errors)):
        plus(predicted[p],row,-1)
    bad_full = transpose(adjoint(bad_prelude+core),712)
    require(any(errors) and bad_full == predicted
            and bad_full != transpose(adjoint(example["program"]),712),
            "The input-route timing error is not Delta Y=Z_1 R_0 Y and Delta X=-J Z_1 R_0 Y")
    for coefficient in (-1,2):
        parameter = [{j:coefficient*value for j,value in row.items()} for row in R]
        rejected = False
        try:
            dyadic_inverse(response(parameter,Z))
        except ValueError:
            rejected = True
        require(rejected, "A singular or non-dyadic inverse was admitted")
    wrong_Z = [row.copy() for row in K]
    for p,row in enumerate(P):
        plus(wrong_Z[p],row,2-alpha)
    require(any(multiply(query,wrong_Z)), "The missing unit in alpha-1 was not detected")
    return {"status":"PASS_INPUT_ONLY_SOURCE_CODES", "alpha":str(alpha),
            "premises":["RK=14I","RP_A=I","L_T K=I","RZ=I","L_T Z=I","QZ=0","JZ=-13P_A"],
            "examples":receipts, "both_inverse_prelude_orders":True, "repeated_parameter_addition":True,
            "source_family_composition":True, "full_backward_words_are_not_inverses":True,
            "interleaved_snapshot_control":{"equal_cost_and_native_access":True,"source_error":"Z_1 R_0 Y",
                                            "target_error":"-J Z_1 R_0 Y","nonzero_rank":1},
            "singular_and_non_dyadic_inverse_controls":True, "wrong_response_coefficient_rejected":True,
            "scope":"Local input-only source preparation. Global query access, restoration, recursive hosting and kappa remain open."}

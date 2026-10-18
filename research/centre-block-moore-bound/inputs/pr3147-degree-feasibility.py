def check_c4_free_degree_feasibility(max_deg3_6cycles: int, m_range: range) -> dict[int, int]:
    counts: dict[int, int] = {}
    for m in m_range:
        feasible = 0
        max_pairs = m * (m - 1) // 2

        def gen_b_parts(total: int, count: int, min_v: int, max_v: int):
            if count == 1:
                if min_v <= total <= max_v:
                    yield (total,)
                return
            for v in range(min_v, min(max_v, total - min_v * (count - 1)) + 1):
                for rest in gen_b_parts(total - v, count - 1, v, max_v):
                    yield (v,) + rest

        def gen_d_parts(total: int, count: int, min_v: int, max_v: int, rem_e2: int):
            if count == 1:
                if min_v <= total <= max_v and total * (total - 1) // 2 <= rem_e2:
                    yield (total,)
                return
            for v in range(min_v, min(max_v, total - min_v * (count - 1)) + 1):
                c2 = v * (v - 1) // 2
                if c2 * count > rem_e2:
                    break
                for rest in gen_d_parts(total - v, count - 1, v, max_v, rem_e2 - c2):
                    yield (v,) + rest

        for E in range(3 * m, 2 * max_pairs + 1):
            valid_d = [
                d_part
                for r in range(1, min(E // 3, max_pairs // 3) + 1)
                for d_part in gen_d_parts(E, r, 3, m, max_pairs)
            ]
            if not valid_d:
                continue
            b_parts = list(gen_b_parts(E, m, 3, m))
            if not b_parts:
                continue
            for d_part in valid_d:
                e2 = sum(k * (k - 1) // 2 for k in d_part)
                claw_tri = sum(k * (k - 1) * (k - 2) // 6 for k in d_part)
                U = max_pairs - e2
                q_u, rem_u = divmod(2 * U, m)
                sum_c2_nondeg = rem_u * ((q_u + 1) * q_u // 2) + (m - rem_u) * (
                    q_u * (q_u - 1) // 2
                )
                min_tri_g2 = (m * (m - 1) * (m - 2) // 6) - U * (m - 2) + sum_c2_nondeg
                forced_6cycles = max(0, min_tri_g2 - claw_tri)
                max_by_d = (
                    sum(max_deg3_6cycles if k == 3 else (k * k // 4) for k in d_part) // 3
                )
                for b_part in b_parts:
                    if sum(2 * g for g in b_part) > 2 * e2:
                        continue
                    max_by_b = (
                        sum(max_deg3_6cycles if g == 3 else (g * g // 4) for g in b_part) // 3
                    )
                    if forced_6cycles <= min(max_by_b, max_by_d):
                        feasible += 1
        counts[m] = feasible
    return counts

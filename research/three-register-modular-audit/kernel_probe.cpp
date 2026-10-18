// SPDX-License-Identifier: Apache-2.0
// Directly probe the pinned implementation; the oracle uses integer determinants.
#define main audited_search_main
#include "audited_f101.cpp"
#undef main

using IntegerRow = std::array<int, 8>;
using Matrix = std::vector<std::vector<int>>;

void require(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}

// Leibniz expansion, independent of the production elimination routines.
int determinant(const Matrix& a) {
    int n = int(a.size()), result = 0;
    std::vector<int> permutation(n);
    std::iota(permutation.begin(), permutation.end(), 0);
    do {
        int term = 1;
        for (int i = 0; i < n; ++i) {
            term *= a[i][permutation[i]];
            for (int j = 0; j < i; ++j)
                if (permutation[j] > permutation[i]) term = -term;
        }
        result += term;
    } while (std::next_permutation(permutation.begin(), permutation.end()));
    return result;
}

int residue(int a) { return (a % 101 + 101) % 101; }

Basis production_basis(const Matrix& a) {
    Basis b;
    for (const auto& row : a) {
        Row r{};
        for (int j = 0; j < int(row.size()); ++j) r[j] = residue(row[j]);
        b = insert(b, r);
    }
    return b;
}

// First n columns form an invertible square B. Cramer's rule gives
// det(B) times each rational RREF row, without rational elimination.
std::vector<IntegerRow> cramer_rows(const Matrix& a) {
    int n = int(a.size());
    Matrix square(n, std::vector<int>(n));
    for (int i = 0; i < n; ++i)
        std::copy_n(a[i].begin(), n, square[i].begin());
    int d = determinant(square);
    require(d != 0, "singular oracle pivot");
    std::vector<IntegerRow> rows(n);
    for (int i = 0; i < n; ++i) {
        rows[i][i] = d;
        for (int j = n; j < int(a[0].size()); ++j) {
            Matrix changed = square;
            for (int k = 0; k < n; ++k) changed[k][i] = a[k][j];
            rows[i][j] = determinant(changed);
        }
    }
    return rows;
}

int oracle_parity(const IntegerRow& r) {
    int divisor = 0, result = 0;
    for (int x : r) divisor = std::gcd(divisor, std::abs(x));
    require(divisor > 0, "zero oracle row");
    for (int j = 0; j < 8; ++j)
        result |= (std::abs(r[j] / divisor) % 2) << j;
    return result;
}

void check_basis(const Basis& b, const std::vector<IntegerRow>& rows) {
    require(b.n == int(rows.size()), "basis rank mismatch");
    for (int i = 0; i < b.n; ++i) {
        require(b.p[i] == i, "basis pivot mismatch");
        for (int j = 0; j < 8; ++j)
            require(residue(int(b.a[i][j]) * rows[i][i]) == residue(rows[i][j]),
                    "Cramer entry mismatch");
        require(primitive_parity(b.a[i]) == oracle_parity(rows[i]),
                "primitive parity mismatch");
    }
}

IntegerRow quotient(int mask, const std::vector<IntegerRow>& rows) {
    IntegerRow q{};
    int d = rows[0][0];
    for (int j = 0; j < 8; ++j) q[j] = ((mask >> j) & 1) * d;
    for (int i = 0; i < int(rows.size()); ++i)
        if ((mask >> i) & 1)
            for (int j = 0; j < 8; ++j) q[j] -= rows[i][j];
    return q;
}

// Membership in a span of at most two vectors, using 2x2/3x3 minors only.
bool span_two(IntegerRow a, IntegerRow b, const IntegerRow& c) {
    auto nonzero = [](const IntegerRow& x) {
        return std::any_of(x.begin(), x.end(), [](int v) { return v != 0; });
    };
    if (!nonzero(a)) std::swap(a, b);
    if (!nonzero(a)) return !nonzero(c);
    for (int i = 0; i < 8; ++i) {
        for (int j = i + 1; j < 8; ++j) {
            if (a[i] * b[j] == a[j] * b[i]) continue;
            for (int k = 0; k < 8; ++k) {
                int det = a[i] * (b[j] * c[k] - b[k] * c[j])
                        - a[j] * (b[i] * c[k] - b[k] * c[i])
                        + a[k] * (b[i] * c[j] - b[j] * c[i]);
                if (det) return false;
            }
            return true;
        }
    }
    int i = 0;
    while (!a[i]) ++i;
    for (int j = 0; j < 8; ++j)
        if (a[i] * c[j] != a[j] * c[i]) return false;
    return true;
}

void check_wide(const Matrix& a, uint64_t& collisions, uint64_t& targets,
                uint64_t& rejected_targets) {
    auto rows = cramer_rows(a);
    Basis b = production_basis(a);
    check_basis(b, rows);
    std::array<IntegerRow, 256> exact{};
    std::array<Row, 256> modular{};
    for (int mask = 0; mask < 256; ++mask) {
        exact[mask] = quotient(mask, rows);
        modular[mask] = residual(subset(mask), b);
        for (int other = 0; other < mask; ++other) {
            require((exact[mask] == exact[other]) == (modular[mask] == modular[other]),
                    "subset collision mismatch");
            ++collisions;
        }
    }
    for (int mask = 0; mask < 256; ++mask) {
        bool small = false;
        for (int i = 0; i < 8; ++i)
            for (int j = i + 1; j < 8; ++j)
                small |= span_two(exact[1 << i], exact[1 << j], exact[mask]);
        require(target_small(mask, b) == small, "target span mismatch");
        ++targets;
        rejected_targets += !small;
    }
    // Reordered generators represent exactly the same relation subspace.
    Matrix reversed = a;
    std::reverse(reversed.begin(), reversed.end());
    require(production_basis(reversed) == b, "canonical basis mismatch");
}

int main() {
    try {
        setup();
        uint64_t square_counts[3]{}, extended_counts[3]{};
        for (int n = 1; n <= 3; ++n) {
            int squares = 1, columns = 1;
            for (int i = 0; i < n * n; ++i) squares *= 3;
            for (int i = 0; i < n; ++i) columns *= 3;
            for (int code = 0; code < squares; ++code) {
                Matrix square(n, std::vector<int>(n));
                int rest = code;
                for (auto& row : square)
                    for (int& x : row) { x = rest % 3 - 1; rest /= 3; }
                if (!determinant(square)) continue;
                ++square_counts[n - 1];
                for (int col = 0; col < columns; ++col) {
                    Matrix a = square;
                    rest = col;
                    for (auto& row : a) { row.push_back(rest % 3 - 1); rest /= 3; }
                    check_basis(production_basis(a), cramer_rows(a));
                    ++extended_counts[n - 1];
                }
            }
        }
        // Bounded, deterministic integration probes; not an exhaustive 3x8 census.
        uint32_t state = 66;
        auto next = [&]() { state = 1664525u * state + 1013904223u; return state; };
        uint64_t collisions = 0, targets = 0, rejected_targets = 0;
        int wide = 0;
        for (int attempt = 0; wide < 192 && attempt < 10000; ++attempt) {
            int n = wide % 3 + 1;
            Matrix a(n, std::vector<int>(8)), square(n, std::vector<int>(n));
            for (int i = 0; i < n; ++i) {
                for (int j = 0; j < 8; ++j) a[i][j] = int(next() % 3) - 1;
                std::copy_n(a[i].begin(), n, square[i].begin());
            }
            if (!determinant(square)) continue;
            check_wide(a, collisions, targets, rejected_targets);
            ++wide;
        }
        require(wide == 192, "wide probe stopping rule incomplete");
        require(rejected_targets > 0 && rejected_targets < targets,
                "target membership probes need both outcomes");
        std::cout << "{\"nonsingular_squares\":[" << square_counts[0] << ','
                  << square_counts[1] << ',' << square_counts[2]
                  << "],\"extended_cube_matrices\":[" << extended_counts[0] << ','
                  << extended_counts[1] << ',' << extended_counts[2]
                  << "],\"wide_matrices\":" << wide
                  << ",\"subset_pair_checks\":" << collisions
                  << ",\"target_checks\":" << targets
                  << ",\"targets_outside_every_two_frame_span\":" << rejected_targets
                  << "}\n";
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}

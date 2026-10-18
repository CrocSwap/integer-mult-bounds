// SPDX-License-Identifier: Apache-2.0
// Two explicit raw6 snapshot slots, checked at every ERASE. This is formal F2
// bank-column execution, NOT address-transform or physical-workspace admission.
// Bank schedule: DaysSky's PR363 / Dylan Crow's columns_k.cpp lineage.
// Separate implementation by Adam Gall with substantial OpenAI Codex assistance.
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
constexpr int v = 111, r = 439, local = 2 * v + r, slots = 2;
using Record = std::array<int, 6>;

void need(bool condition, const char* reason) {
    if (!condition) throw std::runtime_error(reason);
}

std::vector<Record> load(const char* path) {
    std::ifstream input(path, std::ios::binary | std::ios::ate);
    need(bool(input), "open input");
    const auto size = input.tellg();
    need(size > 0 && size % 24 == 0, "stream alignment");
    input.seekg(0);
    std::vector<Record> result(static_cast<std::size_t>(size) / 24);
    for (auto& rec : result) {
        std::array<unsigned char, 24> bytes{};
        input.read(reinterpret_cast<char*>(bytes.data()), bytes.size());
        need(bool(input), "short record");
        for (int i = 0; i < 6; ++i) {
            const std::uint32_t u = std::uint32_t(bytes[4*i]) |
                (std::uint32_t(bytes[4*i+1]) << 8) |
                (std::uint32_t(bytes[4*i+2]) << 16) |
                (std::uint32_t(bytes[4*i+3]) << 24);
            rec[i] = int(u < 0x80000000U ? std::int64_t(u) : std::int64_t(u) - 0x100000000LL);
        }
    }
    return result;
}

struct Matrix {
    const int columns;
    const std::size_t width;
    std::vector<std::uint64_t> values;
    explicit Matrix(int n) : columns(n), width((n + 63) / 64), values((n + slots) * width) {
        for (int i = 0; i < n; ++i) row(i)[i / 64] = std::uint64_t(1) << (i % 64);
    }
    std::uint64_t* row(int i) { return values.data() + i * width; }
    const std::uint64_t* row(int i) const { return values.data() + i * width; }
    void add(int d, int s) {
        auto* a = row(d); const auto* b = row(s);
        for (std::size_t k = 0; k < width; ++k) a[k] ^= b[k];
    }
    void copy(int d, int s) { std::copy_n(row(s), width, row(d)); }
    void clear(int d) { std::fill_n(row(d), width, 0); }
    bool equal_rows(int a, int b) const { return std::equal(row(a), row(a) + width, row(b)); }
    bool zero(int a) const { return std::all_of(row(a), row(a) + width, [](auto x) { return x == 0; }); }
    bool identity() const {
        for (int i = 0; i < columns + slots; ++i)
            for (std::size_t k = 0; k < width; ++k) {
                const auto expected = i < columns && k == std::size_t(i/64)
                    ? std::uint64_t(1) << (i%64) : 0;
                if (row(i)[k] != expected) return false;
            }
        return true;
    }
};

using Bridge = std::array<int, 2>;
std::vector<std::vector<Bridge>> bridges(int pairs) {
    std::vector<std::vector<Bridge>> result(2 * pairs + 1);
    for (int p = 2; p <= pairs; ++p) {
        const int xp = 2 * (p - 1), yp = xp + 1, prevx = xp - 2, prevy = xp - 1;
        result[2*p-3].push_back({prevx, xp});
        result[2*p-3].push_back({yp, prevy});
        result[2*p-2].push_back({yp, prevy});
        result[2*p-2].push_back({prevx, xp});
    }
    for (int p = pairs; p >= 2; --p) {
        result.back().push_back({2*p-3, 2*p-1});
        result.back().push_back({2*p-2, 2*p-4});
    }
    return result;
}

int bridge_controls(int pairs, const std::vector<std::vector<Bridge>>& after) {
    const int count = 6 * (pairs - 1);
    for (int skip = -1; skip < count; ++skip) {
        std::vector<unsigned> rows(2 * pairs);
        for (int i = 0; i < 2*pairs; ++i) rows[i] = 1U << i;
        int index = 0;
        for (int stage = 0; stage < 2*pairs+1; ++stage) {
            const int p = stage < 3 ? 0 : (stage - 1) / 2;
            const bool rev = stage % 2;
            rows[2*p + (rev ? 0 : 1)] ^= rows[2*p + (rev ? 1 : 0)];
            for (auto edge : after[stage]) if (index++ != skip) rows[edge[0]] ^= rows[edge[1]];
        }
        need(index == count, "bridge count");
        for (int p = 0; p < pairs; ++p) std::swap(rows[2*p], rows[2*p+1]);
        bool same = true;
        for (int i = 0; i < 2*pairs; ++i) same &= rows[i] == (1U << i);
        need(same == (skip == -1), "bridge omission control");
    }
    return count;
}
}  // namespace

int main(int argc, char** argv) {
    try {
        need(argc == 3, "usage: bank-columns RAW6 KPAIRS");
        const int pairs = std::stoi(argv[2]);
        need(pairs == 2 || pairs == 4 || pairs == 5, "bank pair domain");
        const auto records = load(argv[1]);
        const int stages = 2*pairs+1;
        // Every stage gets R INDEPENDENT dirty helpers, not one correlated bank.
        const int columns = 2*pairs*v + stages*r;
        Matrix actual(columns), expected(columns);
        const auto after = bridges(pairs);
        long long adds = 0, copies = 0, erases = 0, peak = 0;
        for (int stage = 0; stage < stages; ++stage) {
            const int p = stage < 3 ? 0 : (stage - 1) / 2;
            const bool reverse = stage % 2;
            auto map_role = [&](int role) {
                need(role >= 0 && role < local+slots, "role range");
                if (role >= local) return columns + role-local;
                if (role >= 2*v) return 2*pairs*v + stage*r + role-2*v;
                const int side = role/v;
                return (2*p + (reverse ? 1-side : side))*v + role%v;
            };
            std::array<int, slots> active{{-1, -1}};
            long long stage_copies = 0;
            for (std::size_t i = 0; i < records.size(); ++i) {
                const auto& q = records[reverse ? records.size()-1-i : i];
                const int op = q[0], a = q[1], b = q[2];
                need(op >= 0 && op <= 3, "unknown opcode");
                if (op == 0) continue; // Geometry is checked separately, never called address replay.
                const int ma = map_role(a), mb = map_role(b);
                if (op == 1) {
                    need(a != b && (q[3] == 1 || q[3] == -1), "ADD operands");
                    need((a < local || active[a-local] >= 0) &&
                         (b < local || active[b-local] >= 0), "inactive slot");
                    for (int center : active) need(center != a, "mutated COPY center");
                    actual.add(ma, mb); // Both signs have coefficient one over F2.
                    ++adds;
                } else {
                    need(a < local && b >= local, "COPY roles");
                    const int slot = b-local;
                    const bool opening = op == (reverse ? 3 : 2);
                    if (opening) {
                        need(active[slot] == -1 && actual.zero(mb), "occupied slot");
                        active[slot] = a;
                        actual.copy(mb, ma);
                        ++copies; ++stage_copies;
                        peak = std::max(peak, static_cast<long long>((active[0] >= 0) + (active[1] >= 0)));
                    } else {
                        need(active[slot] == a, "ERASE source binding");
                        need(actual.equal_rows(mb, ma), "ERASE snapshot mismatch");
                        actual.clear(mb);
                        active[slot] = -1;
                        ++erases;
                    }
                }
            }
            need(active[0] == -1 && active[1] == -1 && stage_copies == 9, "stage lifecycle closure");
            for (int j = 0; j < v; ++j)
                expected.add((2*p+(reverse ? 0 : 1))*v+j, (2*p+(reverse ? 1 : 0))*v+j);
            need(actual.values == expected.values, "stage full dirty boundary");
            for (auto edge : after[stage]) for (int j = 0; j < v; ++j) {
                actual.add(edge[0]*v+j, edge[1]*v+j);
                expected.add(edge[0]*v+j, edge[1]*v+j);
            }
        }
        // a+=b; b-=a; a+=b has signed lift (b,-a) and is a swap over F2.
        // Execute and charge the three ADDs, rather than making exchange free.
        for (int p = 0; p < pairs; ++p) for (int j = 0; j < v; ++j) {
            const int a = 2*p*v+j, b = (2*p+1)*v+j;
            actual.add(a, b); actual.add(b, a); actual.add(a, b);
        }
        need(actual.identity(), "complete bank identity");
        const int controls = bridge_controls(pairs, after);
        std::cout << "{\"status\":\"PASS_TWO_SLOT_FORMAL_BANK_COLUMNS\",\"stages\":" << stages
            << ",\"columns\":" << columns << ",\"independent_helper_columns\":" << stages*r
            << ",\"stage_ADDs\":" << adds << ",\"COPYs\":" << copies
            << ",\"checked_ERASEs\":" << erases << ",\"peak_slots\":" << peak
            << ",\"bridge_ADDs\":" << 6*(pairs-1)*v
            << ",\"terminal_exchange_pairs\":" << pairs*v
            << ",\"terminal_exchange_ADDs\":" << 3*pairs*v
            << ",\"bridge_omission_controls\":" << controls
            << ",\"formal_matrix_bytes\":" << actual.values.size()*sizeof(std::uint64_t)
            << "}\n";
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 2;
    }
}

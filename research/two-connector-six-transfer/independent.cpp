// Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
// Separate chronological generator and full dirty/source-vector interpreter.
// Does not include, import, or call census.cpp.
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>

namespace {
int n, limit, occurrence[5] = {}, port[5] = {};
uint64_t leaves = 0, restored = 0;
uint64_t histogram[6][33] = {};

struct Observations {
    uint64_t low = 0, high = 0;
    void insert(int expression) {
        if (expression < 64) low |= uint64_t(1) << expression;
        else high |= uint64_t(1) << (expression - 64);
    }
};

int coverage(Observations observations) {
    int values[128], size = 0;
    while (observations.low) {
        values[size++] = __builtin_ctzll(observations.low);
        observations.low &= observations.low - 1;
    }
    while (observations.high) {
        values[size++] = 64 + __builtin_ctzll(observations.high);
        observations.high &= observations.high - 1;
    }
    uint32_t masks = 1;
    for (int i = 0; i < size; ++i) {
        for (int j = 0; j < i; ++j) {
            const int difference = values[i] ^ values[j];
            // Keep only differences with BOTH independent dirt bits absent.
            if (difference < (1 << n)) masks |= uint32_t(1) << difference;
        }
    }
    return __builtin_popcount(masks);
}

void visit(int introduced, int completed, int used_transfers,
           int row0, int row1, int on_row1, Observations observations) {
    if (completed == n && used_transfers == limit) {
        ++leaves;
        if (row0 == (1 << n) && row1 == (2 << n)) {
            ++restored;
            ++histogram[on_row1][coverage(observations)];
        }
        return;
    }
    // The next chronological instruction is a transfer, a second occurrence,
    // or the first occurrence of the next canonical source label.
    if (used_transfers < limit) {
        auto next = observations;
        next.insert(row0 ^ row1);
        visit(introduced, completed, used_transfers + 1,
              row0 ^ row1, row1, on_row1, next);
    }
    for (int source = 0; source < introduced; ++source) {
        if (occurrence[source] != 1) continue;
        occurrence[source] = 2;
        int a = row0, b = row1;
        (port[source] ? b : a) ^= 1 << source;
        auto next = observations;
        next.insert(a);
        next.insert(b);
        visit(introduced, completed + 1, used_transfers, a, b, on_row1, next);
        occurrence[source] = 1;
    }
    if (introduced < n) {
        occurrence[introduced] = 1;
        for (int p = 0; p < 2; ++p) {
            port[introduced] = p;
            int a = row0, b = row1;
            (p ? b : a) ^= 1 << introduced;
            auto next = observations;
            next.insert(a);
            next.insert(b);
            visit(introduced + 1, completed, used_transfers,
                  a, b, on_row1 + p, next);
        }
        occurrence[introduced] = 0;
    }
}
} // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 3) throw std::runtime_error("usage: independent SOURCES TRANSFERS");
        n = std::stoi(argv[1]);
        limit = std::stoi(argv[2]);
        if (n < 1 || n > 5 || limit < 0 || limit > 6 || limit % 2)
            throw std::runtime_error("domain: 1..5 sources, 0/2/4/6 transfers");
        Observations initial;
        initial.insert(1 << n);
        initial.insert(2 << n);
        visit(0, 0, 0, 1 << n, 2 << n, 0, initial);
        std::cout << "{\"sources\":" << n << ",\"transfers\":" << limit
                  << ",\"candidates\":" << leaves << ",\"restored\":" << restored
                  << ",\"histograms\":[";
        for (int r = 0; r <= n; ++r) {
            if (r) std::cout << ',';
            std::cout << '[';
            for (int c = 0; c <= (1 << n); ++c) {
                if (c) std::cout << ',';
                std::cout << histogram[r][c];
            }
            std::cout << ']';
        }
        std::cout << "]}\n";
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}

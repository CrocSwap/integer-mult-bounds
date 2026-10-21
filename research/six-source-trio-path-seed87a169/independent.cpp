// Independent direct-pair-difference census for the registered Python result.
// Build: g++ -O3 -std=c++17 independent.cpp -o /tmp/trio-census
// Run:   /tmp/trio-census
#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <vector>

static constexpr int N = 13;
std::array<int, 6> counts{};
std::array<int, N> word{};
std::uint64_t nodes = 0, complete = 0, eligible = 0;
std::array<std::uint64_t, 64> histogram{};

bool allowed_profile() {
    auto c = counts;
    std::sort(c.begin(), c.end());
    return c == std::array<int, 6>{1, 2, 2, 2, 3, 3}
        || c == std::array<int, 6>{1, 1, 2, 2, 2, 5};
}

void visit(int depth, int used) {
    ++nodes;
    if (depth == N) {
        if (used != 6) return;
        ++complete;
        if (!allowed_profile()) return;
        ++eligible;
        std::array<int, N + 1> prefix{};
        for (int i = 0; i < N; ++i) prefix[i + 1] = prefix[i] ^ (1 << word[i]);
        std::array<bool, 64> covered{};
        for (int i = 0; i <= N; ++i)
            for (int j = i + 1; j <= N; ++j)
                covered[prefix[i] ^ prefix[j]] = true;
        int size = 0;
        for (int mask = 1; mask < 64; ++mask) size += covered[mask];
        ++histogram[size];
        return;
    }
    const int limit = std::min(used, 5);
    for (int label = 0; label <= limit; ++label) {
        word[depth] = label;
        ++counts[label];
        visit(depth + 1, std::max(used, label + 1));
        --counts[label];
    }
}

int main() {
    visit(0, 0);
    int maximum = 0;
    for (int k = 1; k < 64; ++k) if (histogram[k]) maximum = k;
    std::cout << "CPP nodes=" << nodes << " complete=" << complete
              << " eligible=" << eligible << " max=" << maximum
              << " at_max=" << histogram[maximum] << " histogram={";
    bool first = true;
    for (int k = 1; k < 64; ++k) if (histogram[k]) {
        if (!first) std::cout << ',';
        first = false;
        std::cout << '"' << k << "\":" << histogram[k];
    }
    std::cout << "}\n";
}

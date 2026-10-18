// Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
// Enumerate source matchings, transfer cuts, and all fixed source ports.
#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>

namespace {
int n, transfers;
std::array<int, 10> word;
std::array<int, 6> cuts;
uint64_t candidates = 0, restored = 0;
uint64_t histogram[6][33] = {};

uint32_t differences(uint32_t values) {
    uint32_t result = 1; // The zero difference is always present.
    while (values) {
        const unsigned x = __builtin_ctz(values);
        values &= values - 1;
        uint32_t remaining = values;
        while (remaining) {
            const unsigned y = __builtin_ctz(remaining);
            remaining &= remaining - 1;
            result |= uint32_t(1) << (x ^ y);
        }
    }
    return result;
}

void evaluate() {
    for (unsigned ports = 0; ports < (1u << n); ++ports) {
        ++candidates;
        int z0 = 0, z1 = 0, phase = 0, next_transfer = 0;
        // Source masks grouped by dirt markers e0, e0+e1, and e1.
        uint32_t seen[3] = {1, 0, 1};
        for (int cut = 0; cut <= 2 * n; ++cut) {
            while (next_transfer < transfers && cuts[next_transfer] == cut) {
                z0 ^= z1;
                phase ^= 1;
                ++next_transfer;
                seen[phase] |= uint32_t(1) << z0;
            }
            if (cut < 2 * n) {
                const int source = word[cut];
                if (ports & (1u << source)) {
                    z1 ^= 1 << source;
                    seen[2] |= uint32_t(1) << z1;
                } else {
                    z0 ^= 1 << source;
                    seen[phase] |= uint32_t(1) << z0;
                }
            }
        }
        if (z0 || z1 || phase) continue;
        ++restored;
        const auto masks = differences(seen[0]) | differences(seen[1]) |
                           differences(seen[2]);
        ++histogram[__builtin_popcount(ports)][__builtin_popcount(masks)];
    }
}

void place_transfers(int index, int first_cut) {
    if (index == transfers) {
        evaluate();
        return;
    }
    for (int cut = first_cut; cut <= 2 * n; ++cut) {
        cuts[index] = cut;
        place_transfers(index + 1, cut);
    }
}

void pair_positions(int first, int label) {
    while (first < 2 * n && word[first] >= 0) ++first;
    if (first == 2 * n) {
        place_transfers(0, 0);
        return;
    }
    word[first] = label;
    for (int second = first + 1; second < 2 * n; ++second) {
        if (word[second] >= 0) continue;
        word[second] = label;
        pair_positions(first + 1, label + 1);
        word[second] = -1;
    }
    word[first] = -1;
}

void emit() {
    std::cout << "{\"sources\":" << n << ",\"transfers\":" << transfers
              << ",\"candidates\":" << candidates << ",\"restored\":" << restored
              << ",\"histograms\":[";
    for (int r = 0; r <= n; ++r) {
        if (r) std::cout << ',';
        std::cout << '[';
        for (int coverage = 0; coverage <= (1 << n); ++coverage) {
            if (coverage) std::cout << ',';
            std::cout << histogram[r][coverage];
        }
        std::cout << ']';
    }
    std::cout << "]}\n";
}
} // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 3) throw std::runtime_error("usage: census SOURCES TRANSFERS");
        n = std::stoi(argv[1]);
        transfers = std::stoi(argv[2]);
        if (n < 1 || n > 5 || transfers < 0 || transfers > 6 || transfers % 2)
            throw std::runtime_error("domain: 1..5 sources, 0/2/4/6 transfers");
        word.fill(-1);
        pair_positions(0, 0);
        emit();
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}

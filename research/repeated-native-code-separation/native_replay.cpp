// Exact modular moments of two repeated native projections.
// Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <vector>

constexpr int owners = 112;
constexpr int modes = 8;
constexpr int volume = 1 << 17;
int prime;
int coeff[modes][owners];
int mapped[owners][512];
int sign_at[owners][512];

int reduce(int x) {
    x %= prime;
    return x < 0 ? x + prime : x;
}

void project(std::vector<int>& state, int stage) {
    std::vector<int> tmp(modes * volume, 0);
    int shift = 1 + 8 * stage;
    int mask = 1 | (255 << shift);
    for (int owner = 0; owner < owners; ++owner) {
        const int* src = state.data() + owner * volume;
        for (int x = 0; x < volume; ++x) {
            int local = (x & 1) | (((x >> shift) & 255) << 1);
            int y0 = mapped[owner][local];
            int y = (x & ~mask) | (y0 & 1) | ((y0 >> 1) << shift);
            int v = sign_at[owner][local] * src[x];
            for (int a = 0; a < modes; ++a)
                tmp[a * volume + y] += coeff[a][owner] * v;
        }
    }
    for (int& v : tmp) v = reduce(v);
    for (int owner = 0; owner < owners; ++owner) {
        int* dst = state.data() + owner * volume;
        for (int x = 0; x < volume; ++x) {
            int local = (x & 1) | (((x >> shift) & 255) << 1);
            int y0 = mapped[owner][local];
            int y = (x & ~mask) | (y0 & 1) | ((y0 >> 1) << shift);
            int v = 0;
            for (int a = 0; a < modes; ++a)
                v += coeff[a][owner] * tmp[a * volume + y];
            dst[x] = reduce(sign_at[owner][local] * v);
        }
    }
}

int main(int argc, char** argv) {
    if (argc != 4) throw std::runtime_error("Use source.txt prime count");
    prime = std::stoi(argv[2]);
    int count = std::stoi(argv[3]);
    if (prime <= 2 || prime > 65521 || count < 1 || count > 1000)
        throw std::runtime_error("Invalid prime or count");
    std::ifstream src(argv[1]);
    for (auto& row : coeff) for (int& x : row) src >> x;
    for (int i = 0; i < owners; ++i)
        for (int x = 0; x < 512; ++x) src >> mapped[i][x] >> sign_at[i][x];
    if (!src) throw std::runtime_error("Invalid source file");
    std::vector<int> state(owners * volume, 0);
    state[1] = 1;
    for (int n = 0; n < count; ++n) {
        std::cout << n;
        for (int owner = 0; owner < owners; ++owner)
            std::cout << ' ' << state[owner * volume + 1];
        std::cout << '\n' << std::flush;
        if (n + 1 < count) {
            project(state, 1 - (n % 2));
        }
    }
}

// Complete two-flat coverage census for the explicitly supplied finite domain.
// Nick Petalas. Apache-2.0.
#include <bit>
#include <cstdint>
#include <exception>
#include <iostream>
#include <stdexcept>
#include <vector>

struct Mask {
    std::uint64_t lo;
    std::uint64_t hi;
};

void require(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}

Mask read_mask() {
    Mask result{};
    require(bool(std::cin >> result.lo >> result.hi), "missing mask");
    require(result.hi < (std::uint64_t{1} << 48), "mask exceeds 112 bits");
    return result;
}

std::vector<Mask> read_masks(std::size_t expected) {
    std::size_t count = 0;
    require(bool(std::cin >> count) && count == expected, "domain size mismatch");
    std::vector<Mask> result(count);
    for (auto& mask : result) mask = read_mask();
    return result;
}

int size(Mask mask) {
    return std::popcount(mask.lo) + std::popcount(mask.hi);
}

Mask unite(Mask a, Mask b) {
    return {a.lo | b.lo, a.hi | b.hi};
}

Mask difference(Mask a, Mask b) {
    return {a.lo & ~b.lo, a.hi & ~b.hi};
}

void scan(const std::vector<Mask>& flats, const std::vector<Mask>& firsts,
          const std::vector<Mask>& supports) {
    for (std::size_t f = 0; f < firsts.size(); ++f) {
        int maximum_union = 0;
        for (Mask second : flats) {
            const int current = size(unite(firsts[f], second));
            if (current > maximum_union) maximum_union = current;
        }
        std::cout << "F " << f << ' ' << maximum_union << '\n';
        std::size_t entries = 0;
        for (std::size_t h = 0; h < supports.size(); ++h) {
            // Every successful pair covers all but at most five support lines.
            if (size(supports[h]) > maximum_union + 5) continue;
            for (std::size_t k = 0; k < flats.size(); ++k) {
                const Mask cut = difference(supports[h], unite(firsts[f], flats[k]));
                if (size(cut) <= 5) {
                    ++entries;
                    require(entries <= 2048, "cut inventory capacity exceeded");
                    std::cout << "C " << h << ' ' << k << ' '
                              << cut.lo << ' ' << cut.hi << '\n';
                }
            }
        }
    }
    require(bool(std::cout), "census output failed");
}

int main() {
    try {
        const auto flats = read_masks(43435);
        const auto firsts = read_masks(121);
        const auto supports = read_masks(1200);
        std::cin >> std::ws;
        require(std::cin.eof(), "unexpected trailing input");
        scan(flats, firsts, supports);
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
    return 0;
}

// Exact reduced clean-workspace census. Apache-2.0. Nick Petalas.
#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <stdexcept>

using Matrix = std::uint32_t; // Four rows, four bits each.
using Word = std::array<unsigned, 5>;
struct Relation {
    std::array<unsigned, 32> representative{};
    std::array<bool, 32> high_rank_possible{};
};
using Relations = std::array<Relation, 117>;
using Polynomial = std::array<Matrix, 32>;

void need(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}

unsigned rank(Word columns) {
    std::array<unsigned, 4> basis{};
    unsigned result = 0;
    for (unsigned value : columns) {
        for (int bit = 3; bit >= 0; --bit) {
            const auto index = static_cast<unsigned>(bit);
            if (((value >> index) & 1U) == 0) continue;
            if (basis[index] != 0) value ^= basis[index];
            else { basis[index] = value; ++result; break; }
        }
    }
    return result;
}

bool canonical_rows(unsigned encoded, unsigned dimension, Word& columns) {
    std::array<unsigned, 4> rows{};
    unsigned pivots = 0;
    unsigned previous = 0;
    for (unsigned i = 0; i < dimension; ++i) {
        rows[i] = (encoded >> (5U * i)) & 31U;
        if (rows[i] == 0) return false;
        const unsigned pivot = static_cast<unsigned>(std::countr_zero(rows[i]));
        if (i != 0 && pivot <= previous) return false;
        previous = pivot;
        pivots |= 1U << pivot;
    }
    for (unsigned i = 0; i < dimension; ++i) {
        if (std::popcount(rows[i] & pivots) != 1) return false;
    }
    columns.fill(0);
    for (unsigned j = 0; j < 5; ++j) {
        for (unsigned i = 0; i < dimension; ++i)
            columns[j] |= ((rows[i] >> j) & 1U) << i;
        if (columns[j] == 0) return false;
    }
    for (unsigned j = 0; j < 5; ++j) {
        Word removed = columns;
        removed[j] = 0;
        if (rank(removed) != dimension) return false;
    }
    return true;
}

Relation make_relation(const std::array<int, 5>& direction) {
    Relation result;
    for (unsigned mask = 0; mask < 32; ++mask) {
        result.representative[mask] = mask;
        unsigned minimum_support = 5;
        for (int lambda = -1; lambda <= 1; ++lambda) {
            unsigned support = 0;
            int other = 0;
            bool binary = true;
            for (unsigned j = 0; j < 5; ++j) {
                const int entry = static_cast<int>((mask >> j) & 1U)
                                  + lambda * direction[j];
                support += static_cast<unsigned>(entry != 0);
                if (entry < 0 || entry > 1) binary = false;
                if (entry == 1) other |= 1 << j;
            }
            if (support < minimum_support) minimum_support = support;
            if (binary && static_cast<unsigned>(other) < result.representative[mask])
                result.representative[mask] = static_cast<unsigned>(other);
        }
        result.high_rank_possible[mask] = minimum_support >= 3;
    }
    return result;
}

Relations make_relations() {
    Relations result;
    result[0] = make_relation({0, 0, 0, 0, 0});
    unsigned count = 1;
    for (unsigned code = 0; code < 243; ++code) {
        unsigned rest = code;
        std::array<int, 5> direction{};
        unsigned support = 0;
        int first = 0;
        for (unsigned j = 0; j < 5; ++j) {
            direction[j] = static_cast<int>(rest % 3U) - 1;
            rest /= 3;
            if (direction[j] == 0) continue;
            ++support;
            if (first == 0) first = direction[j];
        }
        if (support < 2 || first != 1) continue;
        need(count < result.size(), "too many relations");
        result[count++] = make_relation(direction);
    }
    need(count == result.size(), "missing relation");
    return result;
}

Matrix left_rank_one(Matrix matrix, unsigned x, unsigned y) {
    unsigned row = 0;
    for (unsigned i = 0; i < 4; ++i)
        if (((y >> i) & 1U) != 0) row ^= (matrix >> (4U * i)) & 15U;
    Matrix result = 0;
    for (unsigned i = 0; i < 4; ++i)
        if (((x >> i) & 1U) != 0) result |= row << (4U * i);
    return result;
}

Polynomial expand(const Word& x, const Word& y, unsigned dimension) {
    Polynomial result{};
    for (unsigned i = 0; i < dimension; ++i) result[0] |= 1U << (5U * i);
    for (unsigned j = 0; j < 5; ++j) {
        need((std::popcount(x[j] & y[j]) & 1) == 1, "nonidempotent call");
        for (unsigned mask = 0; mask < (1U << j); ++mask) {
            const Matrix update = left_rank_one(result[mask], x[j], y[j]);
            result[mask] ^= update;
            result[mask | (1U << j)] = update;
        }
    }
    return result;
}

unsigned apply(Matrix matrix, unsigned vector) {
    unsigned result = 0;
    for (unsigned i = 0; i < 4; ++i)
        result |= static_cast<unsigned>(std::popcount(((matrix >> (4U*i)) & 15U)
                                                     & vector) & 1) << i;
    return result;
}

// Return the unique monomial exponent, or 32 if this is not an eigenvector.
unsigned eigen_exponent(const Polynomial& grouped, unsigned vector) {
    unsigned exponent = 32;
    for (unsigned mask = 0; mask < 32; ++mask) {
        const unsigned output = apply(grouped[mask], vector);
        if (output == 0) continue;
        if (output != vector || exponent != 32) return 32;
        exponent = mask;
    }
    return exponent;
}

struct Counts {
    std::array<std::uint64_t, 16> histogram{};
    std::uint64_t monomial_vectors = 0;
    std::uint64_t candidates = 0;
};

void inspect(const Polynomial& polynomial, unsigned dimension,
             const Relations& relations, Counts& counts, bool probe) {
    for (unsigned index = 0; index < relations.size(); ++index) {
        const Relation& relation = relations[index];
        Polynomial grouped{};
        for (unsigned mask = 0; mask < 32; ++mask)
            grouped[relation.representative[mask]] ^= polynomial[mask];
        unsigned high = 0;
        if (probe) std::cout << "E " << index;
        for (unsigned vector = 1; vector < (1U << dimension); ++vector) {
            const unsigned exponent = eigen_exponent(grouped, vector);
            if (exponent == 32) continue;
            ++counts.monomial_vectors;
            high += static_cast<unsigned>(relation.high_rank_possible[exponent]);
            if (probe) std::cout << ' ' << vector << ':' << exponent;
        }
        if (probe) std::cout << '\n';
        ++counts.histogram[high];
        if (high >= 2) ++counts.candidates;
    }
}

void self_test(const Relations& relations) {
    Polynomial positive{};
    positive[7] = 1U;       // e0 is an eigenvector at a three-frame sum.
    positive[25] = 1U << 5; // e1 is an independent such eigenvector.
    need(eigen_exponent(positive, 1) == 7, "positive e0 rejected");
    need(eigen_exponent(positive, 2) == 25, "positive e1 rejected");
    need(eigen_exponent(positive, 3) == 32, "non-eigenvector accepted");
    need(relations[0].high_rank_possible[7], "rank-three support rejected");
    need(!relations[0].high_rank_possible[3], "rank-two support accepted");
    Counts counts;
    inspect(positive, 2, relations, counts, false);
    need(counts.candidates != 0, "acceptance branch not exercised");
    positive[25] ^= 1U;
    need(eigen_exponent(positive, 1) == 32, "leaking vector accepted");
}

void census(unsigned dimension, const Relations& relations) {
    std::uint64_t spaces = 0;
    std::uint64_t words = 0;
    Counts counts;
    const unsigned choices = 1U << (dimension - 1U);
    unsigned combinations = 1;
    for (unsigned j = 0; j < 5; ++j) combinations *= choices;
    for (unsigned encoded = 0; encoded < (1U << (5U * dimension)); ++encoded) {
        Word x{};
        if (!canonical_rows(encoded, dimension, x)) continue;
        ++spaces;
        std::array<std::array<unsigned, 8>, 5> allowed{};
        for (unsigned j = 0; j < 5; ++j) {
            unsigned count = 0;
            for (unsigned y = 1; y < (1U << dimension); ++y)
                if ((std::popcount(x[j] & y) & 1) != 0) allowed[j][count++] = y;
            need(count == choices, "wrong covector alphabet");
        }
        for (unsigned code = 0; code < combinations; ++code) {
            unsigned rest = code;
            Word y{};
            for (unsigned j = 0; j < 5; ++j) {
                y[j] = allowed[j][rest % choices];
                rest /= choices;
            }
            const bool probe = dimension == 2 || code == 0 || words % 997U == 0;
            if (probe) {
                std::cout << "P " << dimension;
                for (unsigned value : x) std::cout << ' ' << value;
                for (unsigned value : y) std::cout << ' ' << value;
                std::cout << '\n';
            }
            inspect(expand(x, y, dimension), dimension, relations, counts, probe);
            ++words;
        }
    }
    std::cout << "R " << dimension << ' ' << spaces << ' ' << words << ' '
              << counts.monomial_vectors << ' ' << counts.candidates;
    for (auto value : counts.histogram) std::cout << ' ' << value;
    std::cout << '\n';
    need(counts.candidates == 0, "candidate needs investigation");
}

int main() {
    try {
        const Relations relations = make_relations();
        self_test(relations);
        for (unsigned dimension = 2; dimension <= 4; ++dimension)
            census(dimension, relations);
        std::cout << "PASS_CLEAN_REDUCED_CENSUS\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}

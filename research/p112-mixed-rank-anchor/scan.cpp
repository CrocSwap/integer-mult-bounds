// Mixed residual-rank anchor census. Nick Petalas. Apache-2.0.
// The frozen predecessor supplies flat/orbit enumeration and rank-six oracle.
#define main retained_predecessor_main
#include "vendor/census.cpp"
#undef main

bool anchor(const Data &data, Mask rest, int budget, Mask *cut = nullptr) {
  if (budget < 0 || budget > 12) throw std::runtime_error("anchor budget capacity");
  const int size = count(rest);
  if (size > budget + 8) return false;
  std::array<int, 20> labels{};
  std::array<int, 512> position{};
  position.fill(-1);
  int n = 0;
  for (int i = 0; i < 112; ++i) if (has(rest, i)) {
    if (n >= 20) throw std::runtime_error("anchor label capacity");
    const int x = data.labels[static_cast<std::size_t>(i)];
    labels[static_cast<std::size_t>(n++)] = x;
    position[static_cast<std::size_t>(x)] = i;
  }
  if (size <= budget + 4) {
    Mask kept{};
    for (int i = 0; i < std::min(n, 4); ++i)
      set(kept, position[static_cast<std::size_t>(labels[static_cast<std::size_t>(i)])]);
    if (cut) *cut = minus(rest, kept);
    return true;
  }
  for (int a = 0; a < n; ++a) for (int b = a + 1; b < n; ++b)
    for (int c = b + 1; c < n; ++c) for (int d = c + 1; d < n; ++d) {
      const int x = labels[static_cast<std::size_t>(a)], y = labels[static_cast<std::size_t>(b)];
      const int z = labels[static_cast<std::size_t>(c)], w = labels[static_cast<std::size_t>(d)];
      if ((x ^ y ^ z) == w) continue;
      Mask kept{};
      for (int value : {x, y, z, w, x ^ y ^ z, x ^ y ^ w, x ^ z ^ w, y ^ z ^ w}) {
        const int i = position[static_cast<std::size_t>(value)];
        if (i >= 0) set(kept, i);
      }
      if (size - count(kept) <= budget) {
        if (cut) *cut = minus(rest, kept);
        return true;
      }
    }
  return false;
}

struct Candidate {
  int direction = 0;
  Mask rest{};
};

std::size_t anchor_candidates(const Data &data, Mask first,
                             std::array<Candidate, 120> &active) {
  std::size_t n = 0;
  for (int h = 0; h < 248; ++h) {
    if (count(data.off[static_cast<std::size_t>(h)]) > 60) continue;
    const Mask rest = minus(data.off[static_cast<std::size_t>(h)], first);
    if (count(rest) > 40) continue;
    if (n >= active.size()) throw std::runtime_error("root anchor inventory");
    active[n++] = {h, rest};
  }
  return n;
}

int emit_positive(const Data &data, Mask first, Mask second, U &calls) {
  Found found{};
  int n = 0;
  std::array<Mask, 248> cuts{};
  for (int h = 0; h < 248; ++h) {
    const Mask rest = minus(data.off[static_cast<std::size_t>(h)], first | second);
    if (count(rest) > 32) continue;
    ++calls;
    Mask cut{};
    if (deletable(data, rest, 12, &cut)) {
      found[static_cast<std::size_t>(n)] = h;
      cuts[static_cast<std::size_t>(n++)] = cut;
    }
  }
  std::cout << "POS " << n;
  for (int i = 0; i < n; ++i) {
    const Mask cut = cuts[static_cast<std::size_t>(i)];
    std::cout << ' ' << found[static_cast<std::size_t>(i)] << ' ' << cut.lo << ' ' << cut.hi;
  }
  std::cout << '\n';
  return rational_rank(data, found, n);
}

void mixed_census(const Data &data, const std::vector<Mask> &space,
                  const std::vector<std::size_t> &reps) {
  U pairs = 0, tests = 0, positives = 0, calls = 0;
  int global = 0;
  std::cout << "COVER " << space.size() << ' ' << reps.size() << '\n';
  for (std::size_t ri = 0; ri < reps.size(); ++ri) {
    const Mask first = space[reps[ri]];
    std::array<Candidate, 120> active{};
    const std::size_t n = anchor_candidates(data, first, active);
    U row_tests = 0, row_positives = 0;
    int maximum = 0;
    for (std::size_t j = 0; j < space.size(); ++j) {
      ++pairs;
      for (std::size_t a = 0; a < n; ++a) {
        const Mask rest = minus(active[a].rest, space[j]);
        if (count(rest) > 20) continue;
        ++row_tests;
        Mask cut{};
        const bool answer = anchor(data, rest, 12, &cut);
        std::cout << "ANCHOR " << ri << ' ' << j << ' ' << first.lo << ' ' << first.hi
                  << ' ' << space[j].lo << ' ' << space[j].hi << ' ' << active[a].direction
                  << ' ' << answer << ' ' << cut.lo << ' ' << cut.hi << '\n';
        if (!answer) continue;
        ++row_positives;
        maximum = std::max(maximum, emit_positive(data, first, space[j], calls));
        break;
      }
    }
    tests += row_tests;
    positives += row_positives;
    global = std::max(global, maximum);
    std::cout << "ROW " << ri << ' ' << reps[ri] << ' ' << count(first) << ' '
              << maximum << ' ' << row_tests << ' ' << row_positives << '\n';
  }
  std::cout << "TOTAL " << pairs << ' ' << tests << ' ' << positives << ' ' << calls << ' ' << global << '\n';
}

std::vector<int> best_retained(const Data &data, const std::array<int, 20> &indices,
                               int bits, int target) {
  if (bits < 1 || bits > 20 || target < 0 || target > 9)
    throw std::runtime_error("exhaustive oracle capacity");
  const unsigned capacity = 1U << bits;
  std::vector<int> best(capacity);
  for (unsigned code = 0; code < capacity; ++code) {
    Mask mask{};
    for (int bit = 0; bit < bits; ++bit)
      if ((code >> bit) & 1U) set(mask, indices[static_cast<std::size_t>(bit)]);
    if (binary_rank(data, mask) <= target) best[code] = __builtin_popcount(code);
  }
  for (int bit = 0; bit < bits; ++bit) for (unsigned code = 0; code < capacity; ++code)
    if ((code >> bit) & 1U) best[code] = std::max(best[code], best[code ^ (1U << bit)]);
  return best;
}

void check_oracle(const Data &data, const std::array<int, 20> &indices,
                  unsigned code, int target, const std::vector<int> &best, U &checks) {
  Mask mask{};
  for (int bit = 0; bit < 20; ++bit)
    if ((code >> bit) & 1U) set(mask, indices[static_cast<std::size_t>(bit)]);
  const int minimum = __builtin_popcount(code) - best[code];
  for (int budget = 0; budget <= 12; ++budget) {
    Mask cut{};
    const bool answer = target == 4 ? anchor(data, mask, budget, &cut)
                                   : deletable(data, mask, budget, &cut);
    if (answer != (minimum <= budget) ||
        (answer && (count(cut) > budget || count(minus(cut, mask)) ||
                    binary_rank(data, minus(mask, cut)) > target)))
      throw std::runtime_error("oracle disagrees with exhaustive retained-subset optimum");
    ++checks;
  }
}

void oracle_controls(const Data &data) {
  std::array<int, 20> indices{};
  Mask selected{};
  int n = 0;
  for (int i = 0; i < 112; ++i) {
    Mask trial = selected;
    set(trial, i);
    if (binary_rank(data, trial) > binary_rank(data, selected)) {
      indices[static_cast<std::size_t>(n++)] = i;
      selected = trial;
    }
  }
  if (n != 9) throw std::runtime_error("full binary rank control");
  for (int i = 0; i < 112 && n < 20; ++i) if (!has(selected, i)) {
    indices[static_cast<std::size_t>(n++)] = i;
    set(selected, i);
  }
  if (n != 20) throw std::runtime_error("oracle fixture capacity");
  U checks = 0;
  for (int target : {4, 6}) {
    const auto best = best_retained(data, indices, 12, target);
    for (unsigned code = 0; code < 4096; ++code)
      check_oracle(data, indices, code, target, best, checks);
  }
  const auto best = best_retained(data, indices, 20, 4);
  constexpr unsigned full = (1U << 20) - 1;
  check_oracle(data, indices, full, 4, best, checks);
  for (int a = 0; a < 20; ++a) {
    check_oracle(data, indices, full ^ (1U << a), 4, best, checks);
    for (int b = a + 1; b < 20; ++b)
      check_oracle(data, indices, full ^ (1U << a) ^ (1U << b), 4, best, checks);
  }
  std::cout << "PASS_ORACLES " << checks << " exhaustive20 1048576\n";
}

int main(int argc, char **argv) {
  try {
    if (argc < 2 || argc > 3) throw std::runtime_error("usage: scan FIXTURE [--self-test]");
    const Data data = read_data(argv[1]);
    for (int label : data.labels) if (!(label & 1)) throw std::runtime_error("labels must be odd");
    if (argc == 3) {
      if (std::string(argv[2]) != "--self-test") throw std::runtime_error("unknown mode");
      oracle_controls(data);
    } else {
      const auto space = flats(data);
      const auto reps = representatives(data, space);
      mixed_census(data, space, reps);
    }
    return 0;
  } catch (const std::exception &error) {
    std::cerr << error.what() << '\n';
    return 2;
  }
}

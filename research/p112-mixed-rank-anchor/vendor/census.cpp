// Rank-six ten-deletion census. Apache-2.0.
// Flat/orbit enumeration and the dual-code oracle descend from Nick Petalas,
// PR3161 a1aba8389b87412e6f72ccf4d11f31e0ea232327. Rational-span accounting
// and the E7/D7 direction fixture are added in this successor.
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstddef>
#include <fstream>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

using U = std::uint64_t;
using Vector = std::array<std::int64_t, 8>;
using Basis = std::array<Vector, 8>;
using Found = std::array<int, 248>;
struct Mask {
  U lo = 0, hi = 0;
  bool operator==(const Mask &x) const { return lo == x.lo && hi == x.hi; }
  bool operator<(const Mask &x) const { return lo < x.lo || (lo == x.lo && hi < x.hi); }
};
Mask operator|(Mask a, Mask b) { return {a.lo | b.lo, a.hi | b.hi}; }
Mask operator&(Mask a, Mask b) { return {a.lo & b.lo, a.hi & b.hi}; }
Mask operator^(Mask a, Mask b) { return {a.lo ^ b.lo, a.hi ^ b.hi}; }
Mask minus(Mask a, Mask b) { return {a.lo & ~b.lo, a.hi & ~b.hi}; }
int count(Mask a) { return __builtin_popcountll(a.lo) + __builtin_popcountll(a.hi); }
bool has(Mask a, int i) { return i < 64 ? ((a.lo >> i) & 1U) : ((a.hi >> (i - 64)) & 1U); }
void set(Mask &a, int i) { if (i < 64) a.lo |= U{1} << i; else a.hi |= U{1} << (i - 64); }
constexpr Mask ALL{~U{0}, (U{1} << 48) - 1};
struct Data {
  std::array<int, 112> labels{};
  std::array<Vector, 248> vectors{};
  std::array<Mask, 248> off{};
  std::array<std::array<int, 112>, 12> generators{};
  std::array<Mask, 512> parity{};
};

Data read_data(const char *path) {
  std::ifstream input(path);
  if (!input) throw std::runtime_error("cannot read fixture");
  Data data;
  std::array<bool, 512> used{};
  for (int &x : data.labels) {
    if (!(input >> x) || x < 1 || x > 511 || used[static_cast<std::size_t>(x)])
      throw std::runtime_error("invalid label");
    used[static_cast<std::size_t>(x)] = true;
  }
  for (Vector &v : data.vectors) {
    std::int64_t norm = 0;
    for (auto &x : v) {
      if (!(input >> x) || x < -3 || x > 3) throw std::runtime_error("invalid coordinate");
      norm += x * x;
    }
    if (norm < 1 || norm > 16) throw std::runtime_error("invalid direction norm");
  }
  for (Mask &m : data.off) {
    if (!(input >> m.lo >> m.hi) || (m.hi >> 48) || (count(m) != 53 && count(m) != 56 && count(m) != 70))
      throw std::runtime_error("invalid support");
  }
  for (auto &g : data.generators) {
    std::array<bool, 112> seen{};
    for (int &x : g) {
      if (!(input >> x) || x < 0 || x >= 112 || seen[static_cast<std::size_t>(x)])
        throw std::runtime_error("invalid permutation");
      seen[static_cast<std::size_t>(x)] = true;
    }
  }
  std::string trailing;
  if (input >> trailing) throw std::runtime_error("trailing fixture input");
  for (int x = 0; x < 512; ++x)
    for (int i = 0; i < 112; ++i)
      if (__builtin_parity(static_cast<unsigned>(x & data.labels[static_cast<std::size_t>(i)])))
        set(data.parity[static_cast<std::size_t>(x)], i);
  return data;
}

void sort_masks(Mask *rows, Mask *scratch, std::size_t n) {
  if (n > 788035) throw std::runtime_error("sort capacity");
  std::size_t width = 1;
  for (int pass = 0; pass < 20; ++pass) {
    if (width >= n) return;
    for (std::size_t start = 0; start < n; start += 2 * width) {
      const std::size_t middle = std::min(start + width, n);
      const std::size_t end = std::min(start + 2 * width, n);
      std::size_t left = start, right = middle;
      for (std::size_t out = start; out < end; ++out) {
        if (left < middle && (right == end || !(rows[right] < rows[left]))) scratch[out] = rows[left++];
        else scratch[out] = rows[right++];
      }
    }
    for (std::size_t i = 0; i < n; ++i) rows[i] = scratch[i];
    width *= 2;
  }
  if (width < n) throw std::runtime_error("sort pass bound");
}

std::vector<Mask> flats(const Data &data) {
  std::vector<Mask> result;
  result.reserve(788035);
  std::size_t matrices = 0;
  for (int p = 0; p < 7; ++p) for (int q = p + 1; q < 8; ++q)
    for (int r = q + 1; r < 9; ++r) {
      std::array<int, 3> pivot{p, q, r};
      std::array<std::array<int, 6>, 3> free{};
      std::array<int, 3> lengths{};
      int nfree = 0;
      for (int i = 0; i < 3; ++i) for (int c = 0; c < pivot[static_cast<std::size_t>(i)]; ++c)
        if (c != p && c != q && c != r) {
          free[static_cast<std::size_t>(i)][static_cast<std::size_t>(lengths[static_cast<std::size_t>(i)]++)] = c;
          ++nfree;
        }
      if (nfree > 18) throw std::runtime_error("RREF capacity");
      for (unsigned code = 0; code < (1U << nfree); ++code) {
        unsigned bits = code;
        Mask excluded{};
        for (int i = 0; i < 3; ++i) {
          int row = 1 << pivot[static_cast<std::size_t>(i)];
          for (int j = 0; j < lengths[static_cast<std::size_t>(i)]; ++j) {
            if (bits & 1U) row |= 1 << free[static_cast<std::size_t>(i)][static_cast<std::size_t>(j)];
            bits >>= 1;
          }
          excluded = excluded | data.parity[static_cast<std::size_t>(row)];
        }
        ++matrices;
        const Mask mask = minus(ALL, excluded);
        if (count(mask)) result.push_back(mask);
      }
    }
  if (matrices != 788035) throw std::runtime_error("RREF coverage");
  std::vector<Mask> scratch(result.size());
  sort_masks(result.data(), scratch.data(), result.size());
  result.erase(std::unique(result.begin(), result.end()), result.end());
  for (Mask m : result) if (count(m) > 20) throw std::runtime_error("six-flat cap");
  return result;
}

std::size_t root(std::vector<std::size_t> &parent, std::size_t i) {
  for (std::size_t step = 0; step < parent.size(); ++step) {
    if (parent[i] == i) return i;
    parent[i] = parent[parent[i]];
    i = parent[i];
  }
  throw std::runtime_error("union-find cycle");
}

using Tables = std::array<std::array<std::array<Mask, 256>, 14>, 12>;
Tables permutation_tables(const Data &data) {
  Tables tables{};
  for (int g = 0; g < 12; ++g) for (int byte = 0; byte < 14; ++byte)
    for (int v = 0; v < 256; ++v) for (int bit = 0; bit < 8; ++bit)
      if ((v >> bit) & 1) set(tables[static_cast<std::size_t>(g)][static_cast<std::size_t>(byte)][static_cast<std::size_t>(v)],
                             data.generators[static_cast<std::size_t>(g)][static_cast<std::size_t>(byte * 8 + bit)]);
  return tables;
}

std::vector<std::size_t> representatives(const Data &data, const std::vector<Mask> &space) {
  const Tables tables = permutation_tables(data);
  std::vector<std::size_t> parent(space.size());
  std::iota(parent.begin(), parent.end(), std::size_t{0});
  for (std::size_t i = 0; i < space.size(); ++i) for (int g = 0; g < 12; ++g) {
    Mask image{};
    for (int byte = 0; byte < 14; ++byte) {
      const U value = byte < 8 ? space[i].lo >> (8 * byte) : space[i].hi >> (8 * (byte - 8));
      image = image | tables[static_cast<std::size_t>(g)][static_cast<std::size_t>(byte)][static_cast<std::size_t>(value & 255)];
    }
    const auto found = std::lower_bound(space.begin(), space.end(), image);
    if (found == space.end() || !(*found == image)) throw std::runtime_error("orbit leaves flats");
    const std::size_t j = static_cast<std::size_t>(found - space.begin());
    const std::size_t a = root(parent, i), b = root(parent, j);
    if (a != b) parent[a] = b;
  }
  std::vector<std::size_t> reps;
  for (std::size_t i = 0; i < space.size(); ++i) if (root(parent, i) == i) reps.push_back(i);
  if (reps.size() != 159) throw std::runtime_error("orbit coverage");
  return reps;
}

int binary_rank(const Data &data, Mask mask) {
  std::array<int, 9> basis{};
  int rank = 0;
  for (int i = 0; i < 112; ++i) if (has(mask, i)) {
    int x = data.labels[static_cast<std::size_t>(i)];
    for (int bit = 8; bit >= 0; --bit) if ((x >> bit) & 1) {
      if (basis[static_cast<std::size_t>(bit)]) x ^= basis[static_cast<std::size_t>(bit)];
      else { basis[static_cast<std::size_t>(bit)] = x; ++rank; break; }
    }
  }
  return rank;
}

bool deletable(const Data &data, Mask mask, int budget, Mask *cut = nullptr) {
  const int need = binary_rank(data, mask) - 6;
  if (need <= 0) { if (cut) *cut = {}; return true; }
  std::array<Mask, 511> words{};
  std::size_t n = 0;
  for (int x = 1; x < 512; ++x) {
    const Mask word = mask & data.parity[static_cast<std::size_t>(x)];
    if (count(word) > 0 && count(word) <= budget) words[n++] = word;
  }
  std::array<Mask, 511> scratch{};
  sort_masks(words.data(), scratch.data(), n);
  n = static_cast<std::size_t>(std::unique(words.begin(), words.begin() + static_cast<std::ptrdiff_t>(n)) - words.begin());
  if (need == 1) { if (n && cut) *cut = words[0]; return n > 0; }
  for (std::size_t a = 0; a < n; ++a) for (std::size_t b = a + 1; b < n; ++b) {
    const Mask joined = words[a] | words[b];
    if (count(joined) > budget) continue;
    if (need == 2) { if (cut) *cut = joined; return true; }
    for (std::size_t c = b + 1; c < n; ++c)
      if (!(words[c] == (words[a] ^ words[b])) && count(joined | words[c]) <= budget) {
        if (cut) *cut = joined | words[c];
        return true;
      }
  }
  return false;
}

bool insert_vector(Basis &basis, Vector row) {
  for (std::size_t col = 0; col < 8; ++col) {
    if (!row[col]) continue;
    if (!basis[col][col]) { basis[col] = row; return true; }
    const auto a = basis[col][col], b = row[col];
    // Every stored entry has absolute value <= 10^9. Thus each intermediate
    // is <= 2*10^18 in absolute value, strictly inside signed 64-bit range.
    for (std::size_t j = col; j < 8; ++j) row[j] = a * row[j] - b * basis[col][j];
    std::int64_t divisor = 0;
    for (auto x : row) divisor = std::gcd(divisor, x);
    if (divisor) for (auto &x : row) x /= divisor;
    for (auto x : row) if (x > 1000000000LL || x < -1000000000LL)
      throw std::runtime_error("rational-rank capacity");
  }
  return false;
}

int rational_rank(const Data &data, const Found &found, int n) {
  if (n < 0 || n > 248) throw std::runtime_error("direction-count capacity");
  Basis basis{};
  int rank = 0;
  for (int i = 0; i < n; ++i) {
    const int h = found[static_cast<std::size_t>(i)];
    if (h < 0 || h >= 248) throw std::runtime_error("direction index");
    if (insert_vector(basis, data.vectors[static_cast<std::size_t>(h)])) ++rank;
  }
  return rank;
}

void emit_witness(const Data &data, Mask first, Mask second,
                  const Found &found, int n, int budget) {
  Basis basis{};
  Found independent{};
  int rank = 0;
  for (int i = 0; i < n; ++i) {
    const int h = found[static_cast<std::size_t>(i)];
    if (insert_vector(basis, data.vectors[static_cast<std::size_t>(h)]))
      independent[static_cast<std::size_t>(rank++)] = h;
  }
  std::cout << "WITNESS " << first.lo << ' ' << first.hi << ' ' << second.lo << ' ' << second.hi << ' ' << rank;
  for (int i = 0; i < rank; ++i) {
    const int h = independent[static_cast<std::size_t>(i)];
    Mask cut{};
    if (!deletable(data, minus(minus(data.off[static_cast<std::size_t>(h)], first), second), budget, &cut))
      throw std::runtime_error("lost deletion witness");
    std::cout << ' ' << h << ' ' << cut.lo << ' ' << cut.hi;
  }
  std::cout << '\n';
}

void census(const Data &data, const std::vector<Mask> &space,
            const std::vector<std::size_t> &reps, int budget, std::size_t limit) {
  std::cout << "flats " << space.size() << " reps " << reps.size() << " budget " << budget << '\n';
  int global_max = 0, global_span = 0;
  U calls = 0, positives = 0;
  bool have_witness = false;
  for (std::size_t ri = 0; ri < std::min(limit, reps.size()); ++ri) {
    const Mask first = space[reps[ri]];
    std::array<Mask, 248> residual{};
    std::array<int, 248> directions{};
    std::size_t nactive = 0;
    for (int h = 0; h < 248; ++h) {
      const Mask rest = minus(data.off[static_cast<std::size_t>(h)], first);
      if (count(rest) <= 40 + budget) { directions[nactive] = h; residual[nactive++] = rest; }
    }
    int maximum = 0, maxspan = 0;
    U hits = 0;
    for (std::size_t j = 0; j < space.size(); ++j) {
      int qualifying = 0;
      Found found{};
      for (std::size_t a = 0; a < nactive; ++a) {
        const Mask rest = minus(residual[a], space[j]);
        if (count(rest) > 20 + budget) continue;
        ++calls;
        if (deletable(data, rest, budget)) found[static_cast<std::size_t>(qualifying++)] = directions[a];
      }
      maximum = std::max(maximum, qualifying);
      const int span = rational_rank(data, found, qualifying);
      maxspan = std::max(maxspan, span);
      if (qualifying) ++hits;
      if (!have_witness && span >= (budget == 8 ? 3 : 4)) {
        have_witness = true;
        emit_witness(data, first, space[j], found, qualifying, budget);
      }
    }
    global_max = std::max(global_max, maximum);
    global_span = std::max(global_span, maxspan);
    positives += hits;
    std::cout << "rep " << ri << " flat " << reps[ri] << " lines " << count(first)
              << " maxspan " << maxspan << " active " << nactive << " maxdirs " << maximum << " positive_pairs " << hits << '\n';
    std::cout.flush();
  }
  std::cout << "TOTAL maxdirs " << global_max << " maxspan " << global_span << " positive_pairs " << positives << " oracle_calls " << calls << '\n';
}

void self_test(const Data &data) {
  std::array<int, 12> indices{};
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
  if (n != 9) throw std::runtime_error("label rank control");
  for (int i = 0; i < 112 && n < 12; ++i) if (!has(selected, i)) {
    indices[static_cast<std::size_t>(n++)] = i;
    set(selected, i);
  }
  if (n != 12) throw std::runtime_error("test capacity");
  std::array<Mask, 4096> masks{};
  std::array<int, 4096> ranks{};
  for (unsigned code = 0; code < 4096; ++code) {
    for (int bit = 0; bit < 12; ++bit) if ((code >> bit) & 1U)
      set(masks[code], indices[static_cast<std::size_t>(bit)]);
    ranks[code] = binary_rank(data, masks[code]);
  }
  U checks = 0;
  for (unsigned code = 0; code < 4096; ++code) {
    int minimum = 12;
    for (unsigned keep = 0; keep < 4096; ++keep)
      if (!(keep & ~code) && ranks[keep] <= 6)
        minimum = std::min(minimum, __builtin_popcount(code) - __builtin_popcount(keep));
    for (int p = 0; p <= 10; ++p) {
      Mask cut{};
      const bool answer = deletable(data, masks[code], p, &cut);
      if (answer != (minimum <= p) || (answer && (count(cut) > p || binary_rank(data, minus(masks[code], cut)) > 6)))
        throw std::runtime_error("dual-code oracle disagrees with exhaustive deletions");
      ++checks;
    }
  }
  std::cout << "PASS_ORACLE " << checks << " subsets 4096 budgets 11\n";
}

int parse_integer(const char *argument) {
  const std::string text(argument);
  std::size_t used = 0;
  const int value = std::stoi(text, &used);
  if (used != text.size()) throw std::runtime_error("invalid integer");
  return value;
}

int main(int argc, char **argv) {
  try {
    if (argc < 3 || argc > 11) throw std::runtime_error("usage: census FIXTURE BUDGET [LIMIT] | --rank INDEX...");
    const Data data = read_data(argv[1]);
    if (std::string(argv[2]) == "--self-test" && argc == 3) { self_test(data); return 0; }
    if (std::string(argv[2]) == "--rank" && argc >= 4) {
      Found found{};
      for (int i = 3; i < argc; ++i) found[static_cast<std::size_t>(i - 3)] = parse_integer(argv[i]);
      std::cout << "RANK " << rational_rank(data, found, argc - 3) << '\n';
      return 0;
    }
    if (argc > 4) throw std::runtime_error("too many census arguments");
    const int budget = parse_integer(argv[2]);
    if (budget != 8 && budget != 10) throw std::runtime_error("budget must be 8 or 10");
    const int parsed_limit = argc == 4 ? parse_integer(argv[3]) : 159;
    if (parsed_limit < 1 || parsed_limit > 159) throw std::runtime_error("invalid orbit limit");
    const auto space = flats(data);
    const auto reps = representatives(data, space);
    census(data, space, reps, budget, static_cast<std::size_t>(parsed_limit));
    return 0;
  } catch (const std::exception &error) {
    std::cerr << error.what() << '\n';
    return 2;
  }
}

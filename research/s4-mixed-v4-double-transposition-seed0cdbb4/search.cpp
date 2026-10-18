#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <map>
#include <numeric>
#include <string>
#include <utility>
#include <vector>

using Perm = std::array<int, 4>;
using State = std::array<std::uint32_t, 9>;

struct Factor {
  int label;
  int idem;
  State matrix;
};

struct PairWord {
  int first;
  int second;
};

static std::array<std::array<int, 24>, 24> group_product{};
static std::array<Perm, 24> group_elements{};

static Perm compose(const Perm& a, const Perm& b) {
  Perm c{};
  for (int i = 0; i < 4; ++i) c[i] = a[b[i]];
  return c;
}

static int gid(const Perm& p) {
  for (int i = 0; i < 24; ++i) if (group_elements[i] == p) return i;
  return -1;
}

static std::uint32_t group_mul(std::uint32_t x, std::uint32_t y) {
  std::uint32_t out = 0;
  while (x) {
    int a = __builtin_ctz(x);
    x &= x - 1;
    std::uint32_t yy = y;
    while (yy) {
      int b = __builtin_ctz(yy);
      yy &= yy - 1;
      out ^= (std::uint32_t(1) << group_product[a][b]);
    }
  }
  return out;
}

static State multiply(const State& a, const State& b) {
  State c{};
  for (int i = 0; i < 3; ++i)
    for (int j = 0; j < 3; ++j)
      for (int k = 0; k < 3; ++k)
        c[3 * i + j] ^= group_mul(a[3 * i + k], b[3 * k + j]);
  return c;
}

static State identity_state(int e) {
  State s{};
  for (int i = 0; i < 3; ++i) s[3 * i + i] = std::uint32_t(1) << e;
  return s;
}

static State target_state(int p, int q, int e) {
  State s{};
  s[0] = std::uint32_t(1) << p;
  s[4] = std::uint32_t(1) << q;
  s[8] = std::uint32_t(1) << e;
  return s;
}

static std::vector<std::pair<int, int>> idempotents() {
  std::vector<std::pair<int, int>> ns;
  for (int x = 1; x < 8; ++x)
    for (int y = 1; y < 8; ++y)
      if (__builtin_parity(unsigned(x & y))) ns.emplace_back(x, y);
  return ns;
}

static std::vector<Factor> make_factors(const std::array<int, 3>& labels,
                                       const std::vector<std::pair<int, int>>& ns,
                                       int e) {
  std::vector<Factor> fs;
  for (int li = 0; li < 3; ++li) {
    for (int ni = 0; ni < int(ns.size()); ++ni) {
      auto [x, y] = ns[ni];
      State s{};
      for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
          bool nij = ((x >> i) & 1) && ((y >> j) & 1);
          if (i == j) s[3 * i + j] ^= (std::uint32_t(1) << e);
          if (nij) {
            s[3 * i + j] ^= (std::uint32_t(1) << e);
            s[3 * i + j] ^= (std::uint32_t(1) << labels[li]);
          }
        }
      }
      fs.push_back(Factor{li, ni, s});
    }
  }
  return fs;
}

static State translate_left_diagonal(const State& diagonal_target,
                                     const State& right) {
  State out{};
  for (int i = 0; i < 3; ++i) {
    int g = __builtin_ctz(diagonal_target[3 * i + i]);
    for (int j = 0; j < 3; ++j) {
      std::uint32_t cell = right[3 * i + j];
      while (cell) {
        int h = __builtin_ctz(cell);
        cell &= cell - 1;
        out[3 * i + j] ^= (std::uint32_t(1) << group_product[g][h]);
      }
    }
  }
  return out;
}

struct SearchResult {
  bool found = false;
  std::array<int, 4> word{};
  std::size_t lookups = 0;
};

static SearchResult search_four(const State& target,
                                const std::vector<Factor>& fs,
                                const std::vector<State>& pair_states,
                                const std::map<State, PairWord>& pair_index) {
  SearchResult result;
  const int n = int(fs.size());
  for (int f4 = 0; f4 < n; ++f4) {
    for (int f3 = 0; f3 < n; ++f3) {
      ++result.lookups;
      const State& inverse_suffix = pair_states[f4 * n + f3];
      State needed_prefix = translate_left_diagonal(target, inverse_suffix);
      auto hit = pair_index.find(needed_prefix);
      if (hit != pair_index.end()) {
        result.found = true;
        result.word = {hit->second.first, hit->second.second, f3, f4};
        return result;
      }
    }
  }
  return result;
}

static bool is_direct(const std::vector<Factor>& fs,
                      const std::vector<int>& word,
                      const State& target) {
  State acc = identity_state(0);
  for (int f : word) acc = multiply(acc, fs[f].matrix);
  return acc == target;
}

static bool is_four_word(const std::vector<Factor>& fs,
                         const std::array<int, 4>& word,
                         const State& target) {
  State acc = identity_state(0);
  for (int f : word) acc = multiply(acc, fs[f].matrix);
  return acc == target;
}

static std::string word_text(const std::vector<Factor>& fs,
                             const std::array<int, 4>& word) {
  std::string out;
  const char* label_names[] = {"s1", "s2", "s3"};
  for (int i = 0; i < 4; ++i) {
    if (i) out += ",";
    const Factor& f = fs[word[i]];
    out += label_names[f.label];
    out += ":N" + std::to_string(f.idem);
  }
  return out;
}

int main() {
  Perm p{0, 1, 2, 3};
  int k = 0;
  do { group_elements[k++] = p; } while (std::next_permutation(p.begin(), p.end()));
  if (k != 24) return 2;
  for (int a = 0; a < 24; ++a)
    for (int b = 0; b < 24; ++b)
      group_product[a][b] = gid(compose(group_elements[a], group_elements[b]));

  int e = gid(Perm{0, 1, 2, 3});
  int s1 = gid(Perm{1, 0, 2, 3});
  int s2 = gid(Perm{0, 2, 1, 3});
  int s3 = gid(Perm{0, 1, 3, 2});
  int p13p24 = gid(Perm{2, 3, 0, 1});
  int p12p34 = gid(Perm{1, 0, 3, 2});
  int p14p23 = gid(Perm{3, 2, 1, 0});
  int p_word = group_product[group_product[group_product[s2][s1]][s3]][s2];
  int q_word = group_product[s1][s3];
  if (p_word != p13p24 || q_word != p12p34 ||
      group_product[p13p24][p12p34] != p14p23) return 3;

  const std::array<int, 3> labels{s1, s2, s3};
  auto ns = idempotents();
  auto fs = make_factors(labels, ns, e);
  if (ns.size() != 28 || fs.size() != 84) return 4;
  auto idem_id = [&](int x, int y) {
    for (int i = 0; i < int(ns.size()); ++i)
      if (ns[i] == std::make_pair(x, y)) return i;
    return -1;
  };
  const int e00 = idem_id(1, 1);
  const int e11 = idem_id(2, 2);
  if (e00 < 0 || e11 < 0) return 6;

  std::vector<State> pair_states;
  pair_states.reserve(fs.size() * fs.size());
  std::map<State, PairWord> pair_index;
  for (int f1 = 0; f1 < int(fs.size()); ++f1) {
    for (int f2 = 0; f2 < int(fs.size()); ++f2) {
      State state = multiply(fs[f1].matrix, fs[f2].matrix);
      pair_states.push_back(state);
      pair_index.emplace(state, PairWord{f1, f2});
    }
  }

  State mixed = target_state(p13p24, p12p34, e);
  State repeated = target_state(p13p24, p13p24, e);
  State easy = target_state(p12p34, p12p34, e);
  SearchResult mixed_result = search_four(mixed, fs, pair_states, pair_index);
  SearchResult repeated_result = search_four(repeated, fs, pair_states, pair_index);
  SearchResult easy_result = search_four(easy, fs, pair_states, pair_index);
  bool mixed_witness_ok = !mixed_result.found || is_four_word(fs, mixed_result.word, mixed);
  bool repeated_witness_ok = !repeated_result.found || is_four_word(fs, repeated_result.word, repeated);
  bool easy_witness_ok = easy_result.found && is_four_word(fs, easy_result.word, easy);

  std::vector<int> direct_mixed{
      28 * 1 + e00, 28 * 0 + e00, 28 * 2 + e00, 28 * 1 + e00,
      28 * 0 + e11, 28 * 2 + e11};
  bool direct_ok = is_direct(fs, direct_mixed, mixed);
  std::vector<int> direct_easy{28 * 0 + e00, 28 * 2 + e00,
                               28 * 0 + e11, 28 * 2 + e11};
  bool easy_direct_ok = is_direct(fs, direct_easy, easy);

  std::cout << "RESULT group_order=24 idempotents=" << ns.size()
            << " factors=" << fs.size()
            << " pair_words=" << pair_states.size()
            << " unique_pair_states=" << pair_index.size()
            << " four_call_words=" << (std::size_t(fs.size()) * fs.size() * fs.size() * fs.size())
            << " mixed=" << (mixed_result.found ? "hit" : "none")
            << " mixed_lookups=" << mixed_result.lookups
            << " repeated=" << (repeated_result.found ? "hit" : "none")
            << " easy_positive=" << (easy_result.found ? "hit" : "none")
            << " witnesses=" << ((mixed_witness_ok && repeated_witness_ok && easy_witness_ok) ? "pass" : "FAIL")
            << " easy_direct=" << (easy_direct_ok ? "pass" : "FAIL")
            << " direct_mixed_six=" << (direct_ok ? "pass" : "FAIL") << "\n";
  if (mixed_result.found)
    std::cout << "MIXED_WITNESS " << word_text(fs, mixed_result.word) << "\n";
  if (easy_result.found)
    std::cout << "EASY_WITNESS " << word_text(fs, easy_result.word) << "\n";
  return (!direct_ok || !easy_direct_ok || !easy_result.found ||
          !mixed_witness_ok || !repeated_witness_ok || !easy_witness_ok) ? 5 : 0;
}

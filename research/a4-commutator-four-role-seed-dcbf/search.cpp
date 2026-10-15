#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
constexpr int kRoles = 4;
constexpr int kGroup = 12;
constexpr int kFactors = 240;
constexpr int kAlgebraMaskCount = 1 << kGroup;
using Mask = uint16_t;

struct Perm {
  std::array<int, 4> p{};
  bool operator==(const Perm& other) const { return p == other.p; }
  bool operator<(const Perm& other) const { return p < other.p; }
};

struct Mat {
  std::array<Mask, 16> v{};
};

struct Key {
  std::array<uint64_t, 3> w{};
};

struct Record {
  Key key;
  std::array<uint8_t, 3> path{};
  uint8_t len = 0;
  uint8_t exponent = 0;
};

struct Node2 {
  Mat matrix;
  std::array<uint8_t, 2> path{};
  uint8_t exponent = 0;
};

struct Gate {
  uint8_t id = 0;
  uint8_t group = 0;
  uint8_t inverse_group = 0;
  uint8_t x = 0;
  uint8_t y = 0;
  uint8_t exponent = 0;
};

struct GroupData {
  std::array<Perm, kGroup> elements{};
  std::array<std::array<uint8_t, kGroup>, kGroup> product{};
  std::array<uint8_t, kGroup> inverse{};
  std::array<std::array<Mask, kAlgebraMaskCount>, kGroup> left_shift{};
  std::array<std::array<Mask, kAlgebraMaskCount>, kGroup> right_shift{};
  std::vector<Gate> gates;
  uint8_t identity = 0;
  uint8_t a = 0;
  uint8_t b = 0;
  uint8_t commutator = 0;
  uint8_t ab = 0;
  std::array<uint8_t, kGroup> quotient_exponent{};
};

Perm compose(const Perm& p, const Perm& q) {
  Perm out;
  for (int i = 0; i < 4; ++i) out.p[i] = p.p[q.p[i]];
  return out;
}

Perm inverse(const Perm& p) {
  Perm out;
  for (int i = 0; i < 4; ++i) out.p[p.p[i]] = i;
  return out;
}

Perm cycle3(int x, int y, int z) {
  Perm out{{0, 1, 2, 3}};
  out.p[x - 1] = y - 1;
  out.p[y - 1] = z - 1;
  out.p[z - 1] = x - 1;
  return out;
}

int find_element(const std::array<Perm, kGroup>& elements, const Perm& p) {
  for (int i = 0; i < kGroup; ++i) if (elements[i] == p) return i;
  return -1;
}

GroupData make_group() {
  GroupData d;
  std::vector<Perm> elements;
  std::array<int, 4> p{0, 1, 2, 3};
  do {
    int inversions = 0;
    for (int i = 0; i < 4; ++i)
      for (int j = i + 1; j < 4; ++j) inversions += p[i] > p[j];
    if ((inversions & 1) == 0) elements.push_back(Perm{p});
  } while (std::next_permutation(p.begin(), p.end()));
  if (elements.size() != kGroup) throw std::runtime_error("A4 enumeration did not have order 12");
  std::sort(elements.begin(), elements.end());
  std::copy(elements.begin(), elements.end(), d.elements.begin());

  d.identity = static_cast<uint8_t>(find_element(d.elements, Perm{{0, 1, 2, 3}}));
  d.a = static_cast<uint8_t>(find_element(d.elements, cycle3(1, 2, 3)));
  d.b = static_cast<uint8_t>(find_element(d.elements, cycle3(1, 2, 4)));
  if (d.identity >= kGroup || d.a >= kGroup || d.b >= kGroup)
    throw std::runtime_error("missing A4 generator");

  for (int i = 0; i < kGroup; ++i) {
    const int ii = find_element(d.elements, inverse(d.elements[i]));
    if (ii < 0) throw std::runtime_error("missing group inverse");
    d.inverse[i] = static_cast<uint8_t>(ii);
    for (int j = 0; j < kGroup; ++j) {
      const int k = find_element(d.elements, compose(d.elements[i], d.elements[j]));
      if (k < 0) throw std::runtime_error("A4 multiplication is not closed");
      d.product[i][j] = static_cast<uint8_t>(k);
    }
  }

  d.commutator = d.product[d.product[d.product[d.a][d.b]][d.inverse[d.a]]][d.inverse[d.b]];
  d.ab = d.product[d.a][d.b];
  const uint8_t a2 = d.product[d.a][d.a];
  // V4 is the identity together with the three elements of order two.
  std::array<bool, kGroup> in_v4{};
  for (int g = 0; g < kGroup; ++g)
    in_v4[g] = g == d.identity || d.product[g][g] == d.identity;
  const uint8_t a_inverse = d.inverse[d.a];
  const uint8_t a2_inverse = d.inverse[a2];
  for (int g = 0; g < kGroup; ++g) {
    const uint8_t g_a_inv = d.product[g][a_inverse];
    const uint8_t g_a2_inv = d.product[g][a2_inverse];
    if (in_v4[g]) d.quotient_exponent[g] = 0;
    else if (in_v4[g_a_inv]) d.quotient_exponent[g] = 1;
    else if (in_v4[g_a2_inv]) d.quotient_exponent[g] = 2;
    else throw std::runtime_error("failed to classify A4/V4 coset");
  }
  if (d.quotient_exponent[d.a] != 1 || d.quotient_exponent[d.b] != 2 ||
      d.quotient_exponent[d.commutator] != 0 || d.quotient_exponent[d.ab] != 0)
    throw std::runtime_error("unexpected A4/V4 generator classes");

  for (int g = 0; g < kGroup; ++g) {
    for (int mask = 0; mask < kAlgebraMaskCount; ++mask) {
      Mask left = 0, right = 0;
      for (int h = 0; h < kGroup; ++h) if (mask & (1 << h)) {
        left ^= static_cast<Mask>(1 << d.product[g][h]);
        right ^= static_cast<Mask>(1 << d.product[h][g]);
      }
      d.left_shift[g][mask] = left;
      d.right_shift[g][mask] = right;
    }
  }

  std::vector<std::pair<uint8_t, uint8_t>> idempotents;
  for (int x = 1; x < (1 << kRoles); ++x) {
    for (int y = 1; y < (1 << kRoles); ++y) {
      if ((__builtin_popcount(static_cast<unsigned>(x & y)) & 1) != 1) continue;
      idempotents.emplace_back(static_cast<uint8_t>(x), static_cast<uint8_t>(y));
    }
  }
  if (idempotents.size() != 120) throw std::runtime_error("rank-one idempotent count is not 120");
  for (uint8_t g : {d.a, d.b}) {
    for (auto [x, y] : idempotents) {
      Gate gate;
      gate.id = static_cast<uint8_t>(d.gates.size());
      gate.group = g;
      gate.inverse_group = d.inverse[g];
      gate.x = x;
      gate.y = y;
      gate.exponent = d.quotient_exponent[g];
      d.gates.push_back(gate);
    }
  }
  if (d.gates.size() != kFactors) throw std::runtime_error("paid alphabet is not size 240");
  return d;
}

Mat identity_matrix(const GroupData& d) {
  Mat m;
  const Mask one = static_cast<Mask>(1 << d.identity);
  for (int i = 0; i < kRoles; ++i) m.v[i * kRoles + i] = one;
  return m;
}

Mat target_matrix(const GroupData& d) {
  Mat m;
  m.v[0] = static_cast<Mask>(1 << d.a);
  m.v[5] = static_cast<Mask>(1 << d.b);
  m.v[10] = static_cast<Mask>(1 << d.commutator);
  m.v[15] = static_cast<Mask>(1 << d.ab);
  return m;
}

void right_factor(Mat& m, const GroupData& d, const Gate& f, uint8_t group_element) {
  std::array<Mask, kRoles> v{};
  for (int i = 0; i < kRoles; ++i) {
    for (int k = 0; k < kRoles; ++k) if (f.x & (1 << k)) {
      const Mask current = m.v[i * kRoles + k];
      v[i] ^= d.right_shift[group_element][current] ^ current;
    }
  }
  for (int i = 0; i < kRoles; ++i)
    for (int j = 0; j < kRoles; ++j) if (f.y & (1 << j))
      m.v[i * kRoles + j] ^= v[i];
}

void left_factor(Mat& m, const GroupData& d, const Gate& f, uint8_t group_element) {
  std::array<Mask, kRoles> v{};
  for (int j = 0; j < kRoles; ++j) {
    for (int k = 0; k < kRoles; ++k) if (f.y & (1 << k)) {
      const Mask current = m.v[k * kRoles + j];
      v[j] ^= d.left_shift[group_element][current] ^ current;
    }
  }
  for (int i = 0; i < kRoles; ++i) if (f.x & (1 << i))
    for (int j = 0; j < kRoles; ++j) m.v[i * kRoles + j] ^= v[j];
}

Key key_of(const Mat& m) {
  Key key;
  for (int i = 0; i < 16; ++i) {
    const uint64_t value = static_cast<uint64_t>(m.v[i] & 0x0fff);
    const int bit = i * kGroup;
    const int word = bit / 64;
    const int shift = bit % 64;
    key.w[word] |= value << shift;
    if (shift + kGroup > 64) key.w[word + 1] |= value >> (64 - shift);
  }
  return key;
}

bool key_less(const Key& a, const Key& b) {
  if (a.w[2] != b.w[2]) return a.w[2] < b.w[2];
  if (a.w[1] != b.w[1]) return a.w[1] < b.w[1];
  return a.w[0] < b.w[0];
}

bool key_equal(const Key& a, const Key& b) { return a.w == b.w; }

Record make_record(const Mat& m, const std::array<uint8_t, 3>& path, uint8_t len,
                   uint8_t exponent) {
  Record r;
  r.key = key_of(m);
  r.path = path;
  r.len = len;
  r.exponent = exponent;
  return r;
}

bool record_less(const Record& a, const Record& b) {
  if (key_less(a.key, b.key)) return true;
  if (key_less(b.key, a.key)) return false;
  if (a.len != b.len) return a.len < b.len;
  return a.path < b.path;
}

std::array<std::vector<Record>, 3> build_right_states(const GroupData& d,
                                                       std::array<uint64_t, 4>& raw_by_len,
                                                       std::array<uint64_t, 3>& raw_by_exp) {
  std::array<std::vector<Record>, 3> buckets;
  const uint64_t raw = 1ULL + kFactors + uint64_t(kFactors) * kFactors +
                       uint64_t(kFactors) * kFactors * kFactors;
  for (auto& b : buckets) b.reserve(raw / 3 + 8);
  raw_by_len = {1, 0, 0, 0};
  raw_by_exp = {0, 0, 0};
  Mat id = identity_matrix(d);
  std::array<uint8_t, 3> empty{};
  buckets[0].push_back(make_record(id, empty, 0, 0));

  struct Node1 { Mat m; uint8_t path; uint8_t exponent; };
  std::vector<Node1> level1;
  level1.reserve(kFactors);
  for (const Gate& f : d.gates) {
    Mat m = id;
    right_factor(m, d, f, f.group);
    std::array<uint8_t, 3> path{f.id, 0, 0};
    buckets[f.exponent].push_back(make_record(m, path, 1, f.exponent));
    level1.push_back(Node1{m, f.id, f.exponent});
  }
  raw_by_len[1] = kFactors;

  std::vector<Node2> level2;
  level2.reserve(uint64_t(kFactors) * kFactors);
  for (const Node1& n : level1) {
    for (const Gate& f : d.gates) {
      Mat m = n.m;
      right_factor(m, d, f, f.group);
      const uint8_t exponent = static_cast<uint8_t>((n.exponent + f.exponent) % 3);
      std::array<uint8_t, 3> path{n.path, f.id, 0};
      buckets[exponent].push_back(make_record(m, path, 2, exponent));
      level2.push_back(Node2{m, {n.path, f.id}, exponent});
    }
  }
  raw_by_len[2] = uint64_t(kFactors) * kFactors;

  for (const Node2& n : level2) {
    for (const Gate& f : d.gates) {
      Mat m = n.matrix;
      right_factor(m, d, f, f.group);
      const uint8_t exponent = static_cast<uint8_t>((n.exponent + f.exponent) % 3);
      std::array<uint8_t, 3> path{n.path[0], n.path[1], f.id};
      buckets[exponent].push_back(make_record(m, path, 3, exponent));
    }
  }
  raw_by_len[3] = uint64_t(kFactors) * kFactors * kFactors;
  for (int e = 0; e < 3; ++e) {
    raw_by_exp[e] = buckets[e].size();
    auto& b = buckets[e];
    std::sort(b.begin(), b.end(), record_less);
    auto end = std::unique(b.begin(), b.end(), [](const Record& a, const Record& c) {
      return key_equal(a.key, c.key);
    });
    b.erase(end, b.end());
  }
  return buckets;
}

const Record* lookup(const std::array<std::vector<Record>, 3>& buckets, uint8_t exponent,
                     const Key& key) {
  const auto& b = buckets[exponent];
  auto it = std::lower_bound(b.begin(), b.end(), key,
      [](const Record& r, const Key& k) { return key_less(r.key, k); });
  if (it != b.end() && key_equal(it->key, key)) return &*it;
  return nullptr;
}

bool verify_word(const GroupData& d, const std::vector<uint8_t>& word, const Mat& target) {
  Mat m = identity_matrix(d);
  for (uint8_t id : word) right_factor(m, d, d.gates[id], d.gates[id].group);
  return m.v == target.v;
}

bool planted_join_control(const GroupData& d,
                          const std::array<std::vector<Record>, 3>& buckets) {
  const std::array<uint8_t, 6> word{0, 121, 17, 239, 3, 130};
  Mat planted = identity_matrix(d);
  for (uint8_t id : word) right_factor(planted, d, d.gates[id], d.gates[id].group);
  Mat desired = planted;
  std::array<uint8_t, 3> left{word[0], word[1], word[2]};
  uint8_t left_exp = 0;
  for (uint8_t id : left) {
    const Gate& f = d.gates[id];
    left_factor(desired, d, f, f.inverse_group);
    left_exp = static_cast<uint8_t>((left_exp + f.exponent) % 3);
  }
  const uint8_t required_right_exp = static_cast<uint8_t>((3 - left_exp) % 3);
  const Record* found = lookup(buckets, required_right_exp, key_of(desired));
  if (found == nullptr) return false;
  std::vector<uint8_t> reconstructed(left.begin(), left.end());
  for (int i = 0; i < found->len; ++i) reconstructed.push_back(found->path[i]);
  return verify_word(d, reconstructed, planted);
}

std::string vector_bits(uint8_t bits) {
  std::string s;
  for (int i = 0; i < 4; ++i) s.push_back((bits & (1 << i)) ? '1' : '0');
  return s;
}

void report_word(const GroupData& d, const std::vector<uint8_t>& word) {
  std::cout << "WORD_LEN=" << word.size() << "\nWORD_FACTORS=";
  for (size_t i = 0; i < word.size(); ++i) {
    if (i) std::cout << ',';
    std::cout << static_cast<int>(word[i]);
  }
  std::cout << "\nWORD_DETAIL=";
  for (size_t i = 0; i < word.size(); ++i) {
    if (i) std::cout << ';';
    const Gate& g = d.gates[word[i]];
    std::cout << (g.group == d.a ? 'a' : 'b') << ':' << vector_bits(g.x) << ':' << vector_bits(g.y);
  }
  std::cout << '\n';
}

void direct_only(const GroupData& d) {
  Mat target = target_matrix(d);
  auto find_gate = [&](uint8_t group, uint8_t x, uint8_t y) -> uint8_t {
    for (const Gate& g : d.gates) if (g.group == group && g.x == x && g.y == y) return g.id;
    throw std::runtime_error("direct coordinate projector missing");
  };
  std::vector<uint8_t> word;
  word.push_back(find_gate(d.a, 1, 1));
  word.push_back(find_gate(d.b, 2, 2));
  for (uint8_t g : {d.a, d.b, d.b, d.a})
    word.push_back(find_gate(g, 4, 4));
  for (uint8_t g : {d.a, d.b})
    word.push_back(find_gate(g, 8, 8));
  if (word.size() != 8 || !verify_word(d, word, target))
    throw std::runtime_error("direct eight-call target control failed");
  Mat wrong_target = target;
  wrong_target.v[15] = static_cast<Mask>(1 << d.identity);
  if (verify_word(d, word, wrong_target))
    throw std::runtime_error("missing fourth output control failed");
  for (size_t omitted = 0; omitted < word.size(); ++omitted) {
    std::vector<uint8_t> short_word;
    for (size_t i = 0; i < word.size(); ++i) if (i != omitted) short_word.push_back(word[i]);
    if (verify_word(d, short_word, target))
      throw std::runtime_error("omitted direct factor control failed");
  }
  std::cout << "PASS_A4_DIRECT_CONTROL order=12 roles=4 idempotents=120 factors=240 target_calls=8\n";
  std::cout << "quotient_exponents a=" << static_cast<int>(d.quotient_exponent[d.a])
            << " b=" << static_cast<int>(d.quotient_exponent[d.b])
            << " c=" << static_cast<int>(d.quotient_exponent[d.commutator])
            << " d=" << static_cast<int>(d.quotient_exponent[d.ab]) << "\n";
  report_word(d, word);
  std::cout << "direct_missing_fourth_output=reject omitted_factors=8/8\n";
}

bool search(const GroupData& d) {
  std::array<uint64_t, 4> raw_by_len{};
  std::array<uint64_t, 3> raw_by_exp{};
  const auto started = std::chrono::steady_clock::now();
  std::cout << "building_all_right_prefixes_through_length3\n";
  auto buckets = build_right_states(d, raw_by_len, raw_by_exp);
  uint64_t distinct = 0;
  for (const auto& b : buckets) distinct += b.size();
  if (raw_by_len != std::array<uint64_t, 4>{1, 240, 57600, 13824000})
    throw std::runtime_error("right prefix coverage count mismatch");
  if (!planted_join_control(d, buckets))
    throw std::runtime_error("planted six-call join positive control failed");
  std::cout << "PASS_PLANTED_SIX_CALL_JOIN_CONTROL\n";
  std::cout << "right_raw_by_length=1,240,57600,13824000 right_raw_total=13881841\n";
  std::cout << "right_raw_by_quotient_exponent=" << raw_by_exp[0] << ',' << raw_by_exp[1] << ',' << raw_by_exp[2]
            << " right_distinct_states=" << distinct << "\n";

  const Mat target = target_matrix(d);
  std::array<uint8_t, 3> left_path{};
  uint64_t checked_by_len[4] = {0, 0, 0, 0};
  auto check = [&](const Mat& desired, uint8_t left_len, uint8_t left_exp) -> bool {
    ++checked_by_len[left_len];
    const uint8_t right_exp = static_cast<uint8_t>((3 - left_exp) % 3);
    const Record* found = lookup(buckets, right_exp, key_of(desired));
    if (found == nullptr) return false;
    std::vector<uint8_t> word(left_path.begin(), left_path.begin() + left_len);
    for (int i = 0; i < found->len; ++i) word.push_back(found->path[i]);
    if (word.size() > 6 || !verify_word(d, word, target))
      throw std::runtime_error("joined word failed exact coefficient replay");
    std::cout << "PASS_A4_FOUR_ROLE_CONSTRUCTION\n";
    report_word(d, word);
    return true;
  };

  if (check(target, 0, 0)) return true;
  for (const Gate& f1 : d.gates) {
    Mat desired1 = target;
    left_factor(desired1, d, f1, f1.inverse_group);
    left_path[0] = f1.id;
    const uint8_t exp1 = f1.exponent;
    if (check(desired1, 1, exp1)) return true;
    for (const Gate& f2 : d.gates) {
      Mat desired2 = desired1;
      left_factor(desired2, d, f2, f2.inverse_group);
      left_path[1] = f2.id;
      const uint8_t exp2 = static_cast<uint8_t>((exp1 + f2.exponent) % 3);
      if (check(desired2, 2, exp2)) return true;
      for (const Gate& f3 : d.gates) {
        Mat desired3 = desired2;
        left_factor(desired3, d, f3, f3.inverse_group);
        left_path[2] = f3.id;
        const uint8_t exp3 = static_cast<uint8_t>((exp2 + f3.exponent) % 3);
        if (check(desired3, 3, exp3)) return true;
      }
    }
  }
  const auto ended = std::chrono::steady_clock::now();
  const auto seconds = std::chrono::duration_cast<std::chrono::seconds>(ended - started).count();
  std::cout << "PASS_A4_NO_WORD_THROUGH_SIX\n";
  std::cout << "left_prefixes_checked=" << checked_by_len[0] << ',' << checked_by_len[1] << ','
            << checked_by_len[2] << ',' << checked_by_len[3] << " total=13881841\n";
  std::cout << "scope=target_diag_a_b_commutator_ab; no_length7_or_supplier_claim\n";
  std::cout << "elapsed_seconds=" << seconds << "\n";
  return false;
}
}  // namespace

int main(int argc, char** argv) {
  try {
    std::cout << std::unitbuf;
    GroupData d = make_group();
    if (argc > 1 && std::string(argv[1]) == "--direct-only") {
      direct_only(d);
      return 0;
    }
    direct_only(d);
    search(d);
    return 0;
  } catch (const std::exception& e) {
    std::cerr << "FAIL_A4_SEARCH: " << e.what() << '\n';
    return 2;
  }
}

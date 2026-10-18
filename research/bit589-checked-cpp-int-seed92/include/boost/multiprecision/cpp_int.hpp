// Checked 128-bit stand-in for the subset of boost::multiprecision::cpp_int used by
// research/e8-bit-carrier-skeleton/code/bit/checkers/{legality_h,columns_h,columns_k}.cpp,
// the only native code in the selected record's cold replay (bit589 step 4).
//
// Exact or refuse: every arithmetic operation is overflow-checked on __int128. A value
// outside [-2^127, 2^127) aborts with a message instead of wrapping, so a run that
// completes computed exactly the integers Boost's unbounded cpp_int would. Operations
// outside the subset do not compile. Opt in with BOOST_INCLUDE=<this include directory>;
// real Boost remains the default and the reference. Requires GCC or Clang (__int128).
//
// Sagar Thakrar with substantial Anthropic Claude assistance. Apache-2.0.
#ifndef INTEGER_MULT_CHECKED_CPP_INT_HPP
#define INTEGER_MULT_CHECKED_CPP_INT_HPP
#define INTEGER_MULT_CHECKED_CPP_INT_STANDIN 1
#include <cstddef>
#include <cstdio>
#include <cstdlib>
#include <ios>
#include <ostream>
#include <stdexcept>
#include <string>
#include <type_traits>

namespace boost { namespace multiprecision {

class cpp_int {
  __int128 v_;
  [[noreturn]] static void refuse(const char* op) {
    std::fprintf(stderr, "checked cpp_int stand-in: 128-bit range exceeded in %s; use real Boost headers\n", op);
    std::abort();
  }
  template <class T>
  using if_int = typename std::enable_if<std::is_integral<T>::value && !std::is_same<T, bool>::value, int>::type;

 public:
  cpp_int() : v_(0) {}
  template <class T, if_int<T> = 0>
  cpp_int(T x) : v_(static_cast<__int128>(x)) {
    static_assert(sizeof(T) <= 8, "checked cpp_int stand-in: built-in integers up to 64 bits only");
  }
  explicit operator bool() const { return v_ != 0; }

  cpp_int& operator+=(const cpp_int& o) { if (__builtin_add_overflow(v_, o.v_, &v_)) refuse("+"); return *this; }
  cpp_int& operator-=(const cpp_int& o) { if (__builtin_sub_overflow(v_, o.v_, &v_)) refuse("-"); return *this; }
  cpp_int& operator*=(const cpp_int& o) { if (__builtin_mul_overflow(v_, o.v_, &v_)) refuse("*"); return *this; }
  // The count is range-checked in its own type before any narrowing.
  template <class T, if_int<T> = 0>
  cpp_int& operator<<=(T s) {
    if (s < static_cast<T>(0)) refuse("<< by a negative count");
    if (v_ < 0) refuse("<< of a negative value");
    if (v_ == 0) return *this;
    if (static_cast<unsigned long long>(s) >= 127 || (v_ >> (127 - static_cast<int>(s))) != 0) refuse("<<");
    v_ <<= static_cast<int>(s);
    return *this;
  }
  cpp_int operator-() const {
    cpp_int r;
    if (__builtin_sub_overflow(static_cast<__int128>(0), v_, &r.v_)) refuse("unary -");
    return r;
  }
  friend cpp_int operator+(cpp_int a, const cpp_int& b) { return a += b; }
  friend cpp_int operator-(cpp_int a, const cpp_int& b) { return a -= b; }
  friend cpp_int operator*(cpp_int a, const cpp_int& b) { return a *= b; }
  template <class T, if_int<T> = 0>
  friend cpp_int operator<<(cpp_int a, T s) { return a <<= s; }
  friend bool operator==(const cpp_int& a, const cpp_int& b) { return a.v_ == b.v_; }
  friend bool operator!=(const cpp_int& a, const cpp_int& b) { return a.v_ != b.v_; }
  friend bool operator<(const cpp_int& a, const cpp_int& b) { return a.v_ < b.v_; }
  friend bool operator>(const cpp_int& a, const cpp_int& b) { return a.v_ > b.v_; }
  friend bool operator<=(const cpp_int& a, const cpp_int& b) { return a.v_ <= b.v_; }
  friend bool operator>=(const cpp_int& a, const cpp_int& b) { return a.v_ >= b.v_; }

  int sign() const { return (v_ > 0) - (v_ < 0); }
  unsigned __int128 magnitude() const {
    return v_ < 0 ? static_cast<unsigned __int128>(0) - static_cast<unsigned __int128>(v_)
                  : static_cast<unsigned __int128>(v_);
  }
  std::string str() const {
    unsigned __int128 m = magnitude();
    std::string s;
    do { s.insert(s.begin(), static_cast<char>('0' + static_cast<int>(m % 10))); m /= 10; } while (m);
    if (v_ < 0) s.insert(s.begin(), '-');
    return s;
  }
  template <class T>
  T convert_to() const {
    static_assert(std::is_same<T, std::string>::value, "checked cpp_int stand-in: only convert_to<std::string>");
    return str();
  }
  // Default decimal formatting only; Boost would honour hex, oct and showpos.
  friend std::ostream& operator<<(std::ostream& os, const cpp_int& x) {
    const std::ios_base::fmtflags base = os.flags() & std::ios_base::basefield;
    if ((base != std::ios_base::dec && base != std::ios_base::fmtflags(0)) || (os.flags() & std::ios_base::showpos))
      refuse("stream output with non-default format flags");
    return os << x.str();
  }
};

// Index of the most significant set bit. Like Boost, refuses operands <= 0.
inline std::size_t msb(const cpp_int& x) {
  if (x.sign() <= 0) throw std::domain_error("No bits were set in the operand.");
  unsigned __int128 m = x.magnitude();
  std::size_t i = 0;
  while (m >>= 1) ++i;
  return i;
}

}}  // namespace boost::multiprecision
#endif

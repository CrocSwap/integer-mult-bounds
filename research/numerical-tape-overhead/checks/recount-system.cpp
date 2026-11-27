// Exact fixed-grid replay. This is a functional oracle, not a multitape timing oracle.
#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
#include <gmpxx.h>

struct Value {
    mpz_class re = 0;
    mpz_class im = 0;
};

struct Gate {
    char op;
    std::vector<int> data;
};

static mpz_class sqrt_floor(const mpz_class& x) {
    mpz_class z;
    mpz_sqrt(z.get_mpz_t(), x.get_mpz_t());
    return z;
}

static mpz_class rounded_shift(const mpz_class& x, unsigned bits) {
    if (x == 0 || !bits) return x;
    mpz_class v = abs(x);
    // The bit below the cut decides rounding toward the more distant magnitude.
    bool up = mpz_tstbit(v.get_mpz_t(), bits - 1);
    v >>= bits;
    if (up) ++v;
    return x < 0 ? -v : v;
}

static Value product(const Value& x, const Value& y, unsigned bits) {
    mpz_class real = x.re * y.re - x.im * y.im;
    mpz_class imag = x.re * y.im + x.im * y.re;
    return {rounded_shift(real, bits), rounded_shift(imag, bits)};
}

struct Replay {
    unsigned phase_frac, root_frac;
    mpz_class phase_one, inv_root_two;
    std::vector<Value> phases;
    std::vector<std::array<int,2>> special;
    std::vector<Gate> gates;
    std::uint64_t nperm = 0, ndiag = 0, nwalsh = 0;

    mpz_class half(const mpz_class& x) const {
        if (x == 0) return 0;
        const mpz_class a = abs(x);
        mpz_class j = rounded_shift(a * inv_root_two, root_frac);
        const mpz_class midpoint = 2*j + 1;
        if (2*a*a >= midpoint*midpoint) ++j;
        return x < 0 ? -j : j;
    }

    void run(const std::vector<int>& seq, std::vector<Value>& data) {
        std::vector<Value> temp(data.size());
        for (int id : seq) {
            const Gate& g = gates.at(id);
            if (g.op == 'P') {
                ++nperm;
                for (size_t i = 0; i < data.size(); ++i) temp[i] = data[g.data[i]];
                data.swap(temp);
            } else if (g.op == 'D') {
                ++ndiag;
                for (size_t i = 0; i < data.size(); ++i) {
                    int p = g.data[i];
                    auto [unit, sign] = special[p];
                    auto& z = data[i];
                    if (unit == 1) {
                        if (sign < 0) {
                            z.re = -z.re;
                            z.im = -z.im;
                        }
                    } else if (unit == 2) {
                        z.re.swap(z.im);
                        if (sign > 0) z.re = -z.re;
                        else z.im = -z.im;
                    } else {
                        z = product(z, phases[p], phase_frac);
                    }
                }
            } else if (g.op == 'W') {
                ++nwalsh;
                for (size_t i = 0; i < data.size(); i += 2) {
                    const Value& a = data[i];
                    const Value& b = data[i+1];
                    Value sum{half(a.re+b.re), half(a.im+b.im)};
                    Value dif{half(a.re-b.re), half(a.im-b.im)};
                    data[i] = std::move(sum);
                    data[i+1] = std::move(dif);
                }
            } else {
                throw std::runtime_error("unexpected gate");
            }
        }
    }
};

int main() {
    if (std::string(gmp_version) != TAPE_EXPECTED_GMP) {
        std::cerr << "Expected GMP " << TAPE_EXPECTED_GMP << ", found " << gmp_version << "\n";
        return 1;
    }
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    Replay r;
    unsigned n, k, width, phase_width, digits, b, modulus, volume;
    std::cin >> n >> k >> width >> phase_width >> digits >> b >> modulus >> volume;
    r.phase_frac = phase_width;
    r.phase_one = mpz_class(1) << phase_width;
    r.root_frac = 2*width + 4*k + 32;
    r.inv_root_two = sqrt_floor(mpz_class(1) << (2*r.root_frac-1));
    unsigned phase_count = 0;
    std::cin >> phase_count;
    for (unsigned i = 0; i < phase_count; ++i) {
        Value p;
        std::cin >> p.re >> p.im;
        int unit = 0, sign = 0;
        if (p.im == 0 && abs(p.re) == r.phase_one) {
            unit = 1;
            sign = sgn(p.re);
        }
        if (p.re == 0 && abs(p.im) == r.phase_one) {
            unit = 2;
            sign = sgn(p.im);
        }
        r.phases.push_back(std::move(p));
        r.special.push_back({unit, sign});
    }
    unsigned gate_count = 0;
    std::cin >> gate_count;
    for (unsigned j = 0; j < gate_count; ++j) {
        Gate g;
        std::cin >> g.op;
        if (g.op != 'W') {
            g.data.resize(volume);
            for (int& x : g.data) std::cin >> x;
        }
        r.gates.push_back(std::move(g));
    }
    std::array<std::vector<int>, 2> seq;
    for (auto& s : seq) {
        size_t length;
        std::cin >> length;
        s.resize(length);
        for (int& id : s) std::cin >> id;
    }
    std::vector<int> addr(modulus);
    for (int& j : addr) std::cin >> j;
    mpz_class x, y;
    std::cin >> x >> y;
    if (!std::cin) throw std::runtime_error("truncated fixed-grid fixture");

    std::vector<Value> a(volume), c(volume);
    const mpz_class digitmask = (mpz_class(1) << b) - 1;
    for (unsigned i = 0; i < digits; ++i) {
        a[addr[i]].re = ((x >> (b*i)) & digitmask) << width;
        c[addr[i]].re = ((y >> (b*i)) & digitmask) << width;
    }
    r.run(seq[0], a);
    r.run(seq[0], c);
    for (unsigned i = 0; i < volume; ++i) a[i] = product(a[i], c[i], width);
    r.run(seq[1], a);
    auto scale = sqrt_floor(mpz_class(modulus) << (2*phase_width));
    mpz_class recovered = 0, carry = 0, max_error = 0, max_im = 0;
    unsigned bad_without_inverse_crt = 0;
    for (unsigned i = 0; i < modulus; ++i) {
        const auto& z = a[addr[i]];
        mpz_class real = rounded_shift(z.re * scale, phase_width);
        mpz_class imag = rounded_shift(z.im * scale, phase_width);
        mpz_class expected = 0;
        for (unsigned j = 0; j < digits; ++j) {
            if (i >= j && i-j < digits) {
                expected += ((x >> (j*b)) & digitmask) * ((y >> ((i-j)*b)) & digitmask);
            }
        }
        mpz_class error = abs(real - (expected << width));
        if (error > max_error) max_error = error;
        if (abs(imag) > max_im) max_im = abs(imag);
        auto zint = rounded_shift(real, width);
        if (zint != expected) throw std::runtime_error("coefficient mismatch");
        const auto wrong = rounded_shift(a[i].re * scale, phase_width + width);
        if (wrong != expected) ++bad_without_inverse_crt;
        carry += zint;
        recovered += (carry & digitmask) << (b*i);
        carry >>= b;
    }
    const mpz_class reference = x*y;
    const std::string ordinary = recovered == 0 ? "" : recovered.get_str(2);
    if (carry != 0 || recovered != reference || ordinary.size() > 2*n)
        throw std::runtime_error("full carry or output-length mismatch");
    const std::size_t leading = 2*n - ordinary.size();
    const std::string output = std::string(leading, '0') + ordinary;
    if (output.size() != 2*n || mpz_class(output, 2) != reference)
        throw std::runtime_error("padded MSB-first raw output mismatch");
    if (reference != 0 && bad_without_inverse_crt == 0)
        throw std::runtime_error("inverse-CRT negative control did not discriminate");
    std::cout << "{\"n\":" << n << ",\"address_bits\":" << k
        << ",\"data_fraction\":" << width << ",\"phase_fraction\":" << phase_width
        << ",\"recovered_coefficients\":" << modulus << ",\"output_bits\":" << output.size()
        << ",\"leading_output_zeros\":" << leading
        << ",\"max_real_error_ulp_bits\":" << mpz_sizeinbase(max_error.get_mpz_t(),2)
        << ",\"max_imag_error_ulp_bits\":" << mpz_sizeinbase(max_im.get_mpz_t(),2)
        << ",\"wrong_without_inverse_crt\":" << bad_without_inverse_crt
        << ",\"permutation_slots\":" << r.nperm << ",\"phase_slots\":" << r.ndiag
        << ",\"walsh_slots\":" << r.nwalsh << "}\n";
}

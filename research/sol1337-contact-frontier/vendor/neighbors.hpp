#ifndef CANONICAL_TRANSVECTION_AXES_HPP
#define CANONICAL_TRANSVECTION_AXES_HPP
#include <bit>
#include <cstdint>
#include <stdexcept>
#include <vector>
#include <utility>

// Exact neighbor enumeration; coordinates are x | (z << n).
inline std::vector<unsigned> canonical_transvection_axes(const std::vector<unsigned>& lag, unsigned n=9) {
    if (lag.size()!=n || n==0 || n>15) throw std::invalid_argument("Lagrangian dimension");
    const unsigned mask=(1u<<n)-1;
    std::vector<std::uint64_t> rows(n);
    for(unsigned i=0;i<n;i++) rows[i]=(lag[i]>>n)|((lag[i]&mask)<<n)|(std::uint64_t(1)<<(2*n+i));
    std::vector<unsigned> piv;
    unsigned k=0;
    for(unsigned j=0;j<2*n && k<n;j++) {
        unsigned z=k;
        while(z<n && !(rows[z]>>j&1)) z++;
        if(z==n) continue;
        std::swap(rows[k],rows[z]);
        for(unsigned i=0;i<n;i++) if(i!=k && (rows[i]>>j&1)) rows[i]^=rows[k];
        piv.push_back(j); k++;
    }
    if(k!=n) throw std::invalid_argument("Dependent Lagrangian basis");
    std::vector<unsigned> dual(n);
    for(unsigned j=0;j<n;j++) for(unsigned i=0;i<n;i++) if(rows[i]>>(2*n+j)&1) dual[j]|=1u<<piv[i];
    std::vector<unsigned> base(1u<<n), out;
    out.reserve(2*((1u<<n)-1));
    for(unsigned b=1;b<(1u<<n);b++) {
        const unsigned j=std::countr_zero(b);
        base[b]=base[b&(b-1)]^dual[j];
        out.push_back(base[b]);
        out.push_back(base[b]^lag[j]);
    }
    return out;
}
#endif

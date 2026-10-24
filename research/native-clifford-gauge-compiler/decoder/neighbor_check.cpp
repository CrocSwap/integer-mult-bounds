#include "neighbors.hpp"
#include <algorithm>
#include <fstream>
#include <iostream>
#include <map>
#include <random>
#include <set>
using V=std::vector<unsigned>;
unsigned omega(unsigned a,unsigned b,unsigned n){unsigned m=(1u<<n)-1;return (std::popcount((a&m)&(b>>n))+std::popcount((a>>n)&(b&m)))&1;}
V canonical(V a,unsigned n){V piv(2*n);for(auto x:a)while(x){unsigned j=31-std::countl_zero(x);if(piv[j])x^=piv[j];else{piv[j]=x;break;}}for(unsigned j=0;j<2*n;j++)if(piv[j])for(unsigned k=j+1;k<2*n;k++)if(piv[k]>>j&1)piv[k]^=piv[j];V out;for(auto x:piv)if(x)out.push_back(x);return out;}
V moved(V u,unsigned a,unsigned n){for(auto& x:u)if(omega(x,a,n))x^=a;return canonical(u,n);}
int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream small(argv[1]);unsigned n,k;unsigned long long cases=0,lags=0;
while(small>>n>>k){for(unsigned c=0;c<k;c++){V u(n);for(auto&x:u)small>>x;u=canonical(u,n);std::map<V,unsigned> all;for(unsigned a=1;a<(1u<<(2*n));a++){auto v=moved(u,a,n);if(v!=u)all[v]++;}auto axes=canonical_transvection_axes(u,n);std::set<V> reduced;for(auto a:axes)reduced.insert(moved(u,a,n));if(reduced.size()!=axes.size()||all.size()!=axes.size())return 3;for(auto&[v,count]:all)if(!reduced.count(v)||count!=(1u<<(n-1)))return 4;cases+=(1u<<(2*n))-1;lags++;}std::cout<<"PASS_SMALL n="<<n<<" lagrangians="<<k<<"\n";}
std::ifstream g(argv[2]);unsigned nodes,frames,maps,edges;g>>nodes>>frames>>maps>>edges;unsigned discard;for(unsigned i=0;i<2*nodes;i++)g>>discard;std::vector<V> fs(frames,V(9));for(auto&u:fs)for(auto&x:u)g>>x;std::mt19937 rng(20261022);unsigned checked=0;for(unsigned j=0;j<32;j++){auto u=canonical(fs[rng()%frames],9);auto axes=canonical_transvection_axes(u,9);if(axes.size()!=1022)return 5;for(unsigned b=1;b<512;b++)for(int t=0;t<2;t++){unsigned a=axes[2*(b-1)+t],f=0;for(unsigned i=0;i<9;i++)if(omega(u[i],a,9))f|=1u<<i;if(f!=b)return 6;}for(unsigned z=0;z<4096;z++){unsigned a=1+rng()%262143,b=0;for(unsigned i=0;i<9;i++)if(omega(u[i],a,9))b|=1u<<i;if(!b)continue;unsigned rep=axes[2*(b-1)];if(omega(a^rep,rep,9))rep=axes[2*(b-1)+1];if(moved(u,a,9)!=moved(u,rep,9))return 7;checked++;}}
std::cout<<"PASS_COMPLETE_TRANSVECTION_NEIGHBORS small_lagrangians="<<lags<<" small_axis_cases="<<cases<<" actual_n9_axes="<<checked<<"\n";
}

// Cached-matrix drop-in acceleration of references/frame-compiler/pr67/research/slot-cost-rank-pair/profile_oracle.cpp
// Preserves exact 3-prime CRT pivot profiles; verified against the original oracle in test_controls.py.
// Apache-2.0.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <vector>
#include <map>
#include <unordered_map>
#include <cmath>
#include <iomanip>
#include <cstdlib>
using U=uint32_t;using V=uint64_t;
#include "binary_io.hpp"
int main(int argc,char**argv){
std::ios::sync_with_stdio(false);
std::cin.tie(nullptr);
assert(argc==2);std::ifstream f(argv[1],std::ios::binary);U hdr[6];read_array(f,hdr);
U h=hdr[0],v=hdr[1],R=hdr[2],nf=hdr[3],nt=hdr[4];int64_t singles=hdr[5];assert(h==23||h==25);
V sum,loss;f.read(reinterpret_cast<char*>(&sum),8);f.read(reinterpret_cast<char*>(&loss),8);
struct Frame{V core,cover;U rank;};std::vector<Frame>frames;frames.reserve(nf);
for(U i=0;i<nf;i++){Frame a;f.read(reinterpret_cast<char*>(&a.core),8);f.read(reinterpret_cast<char*>(&a.cover),8);f.read(reinterpret_cast<char*>(&a.rank),4);frames.push_back(a);}
for(U i=0;i<nt;i++){U a,b;int64_t count;f.read(reinterpret_cast<char*>(&a),4);f.read(reinterpret_cast<char*>(&b),4);f.read(reinterpret_cast<char*>(&count),8);}
assert(f);assert(sum==h*V(R)+loss);
constexpr V PRIMES[3] = {2305843009213693951ULL, 2147483647ULL, 524287ULL};
V p=PRIMES[0];
auto mul=[&](V a,V b)->V{return (__uint128_t)a*b%p;};
auto power=[&](V a,V b)->V{V r=1;for(;b;b>>=1,a=mul(a,a))if(b&1)r=mul(r,a);return r;};
auto sub=[&](V a,V b)->V{return (a+p-b)%p;};
std::vector<std::vector<V>>matrix_cache[3];
for(int pid=0;pid<3;pid++) matrix_cache[pid].resize(frames.size());
auto compute_matrix=[&](U id)->std::vector<V>{
 std::vector<V> A(h*h,0);if(id==0)return A;if(id==1){for(U i=0;i<h;i++)A[i*h+i]=1;return A;}
 auto f=frames[id];U c=popcount64(f.core);V out=f.cover&~f.core;U nn=popcount64(out);
 if(c==3){V factor=power(6*(h+1),p-2);for(U i=0;i<h;i++)for(U j=0;j<h;j++){V wi=3+((f.core>>i)&1);V zj=((f.core>>j)&1)?3*(h+1)-10:p-10;A[i*h+j]=mul(mul(wi,zj),factor);}return A;}
 assert(c==1||c==2);V s=3-c,d=s*s+(c-1)*nn,den=3*(h+1)*d,inv=power(den,p-2);
 for(U i=0;i<h;i++)for(U j=0;j<h;j++){V oi=(out>>i)&1,oj=(out>>j)&1,wi=3+((f.core>>i)&1),zj=((f.core>>j)&1)?3*(h+1)-10:p-10;
  V num=(mul(s*oi,zj)+3*(h+1)*s*wi*oj+mul(nn*wi,zj))%p;num=sub(num,3*(h+1)*(c-1)*oi*oj);A[i*h+j]=(V(i==j&&oi)+mul(num,inv))%p;
 }return A;};
auto matrix=[&](int pid, U id)->const std::vector<V>&{p=PRIMES[pid];auto&A=matrix_cache[pid][id];if(A.empty())A=compute_matrix(id);return A;};

std::vector<int64_t>blocks(h+1);
U aa,bb;
while(std::cin>>aa>>bb){
 assert(aa<frames.size()&&bb<frames.size());
 int64_t count=1;std::fill(blocks.begin(),blocks.end(),0);
 U rr=frames[bb].rank-frames[aa].rank;
 assert(frames[bb].rank>=frames[aa].rank);
 if(rr<=2){blocks[1]=rr; for(U t=0;t<=h;t++)std::cout<<blocks[t]<<" ";std::cout<<"\n"<<std::flush;continue;}
 if(aa==0&&bb==1){blocks[h]=1;for(U t=0;t<=h;t++)std::cout<<blocks[t]<<" ";std::cout<<"\n"<<std::flush;continue;}
 if(aa>1&&bb>1){
  assert(!(frames[bb].core&~frames[aa].core));
  assert(!(frames[aa].cover&~frames[bb].cover));
  U ca=popcount64(frames[aa].core),cb=popcount64(frames[bb].core);
  assert(ca==3||frames[aa].core==frames[bb].core||(ca==2&&cb==1));
 }
 const auto&A=matrix(0,aa);const auto&B=matrix(0,bb);std::vector<V>M(h*h);for(U x=0;x<h*h;x++)M[x]=sub(B[x],A[x]);std::vector<std::pair<U,U>>pivots;
 for(U i=0;i<h;i++){int j=h-1;while(j>=0&&!M[i*h+j])j--;if(j<0)continue;pivots.push_back({i,U(j)});if(pivots.size()==rr)break;V inv=power(M[i*h+j],p-2);for(U k=i+1;k<h;k++){V z=mul(M[k*h+j],inv);if(z)for(U col=0;col<=U(j);col++)M[k*h+col]=sub(M[k*h+col],mul(z,M[i*h+col]));}}
 assert(pivots.size()==rr);
if(aa>1&&bb>1&&(popcount64(frames[aa].core)==3||(popcount64(frames[aa].core)==2&&popcount64(frames[bb].core)==1))){
 assert(h==23||h==25);std::vector<std::vector<std::pair<U,U>>> all{pivots};
 for(int pid=1;pid<=2;pid++){const auto&C=matrix(pid,aa);const auto&D=matrix(pid,bb);std::vector<V>Y(h*h);for(U z=0;z<h*h;z++)Y[z]=sub(D[z],C[z]);std::vector<std::pair<U,U>> pp;
  for(U i=0;i<h;i++){int j=h-1;while(j>=0&&!Y[i*h+j])j--;if(j<0)continue;pp.push_back({i,U(j)});if(pp.size()==rr)break;V inv=power(Y[i*h+j],p-2);for(U k=i+1;k<h;k++){V z=mul(Y[k*h+j],inv);if(z)for(U col=0;col<=U(j);col++)Y[k*h+col]=sub(Y[k*h+col],mul(z,Y[i*h+col]));}}
  all.push_back(std::move(pp));
 }
 p=PRIMES[0];
 std::vector<int> corner((h+1)*(h+1));for(U i=0;i<h;i++)for(U j=0;j<h;j++){int best=0;for(auto&pp:all){int rank=0;for(auto [row,col]:pp)rank+=row<=i&&col>=j;best=std::max(best,rank);}corner[(i+1)*(h+1)+j]=best;}
 pivots.clear();for(U i=0;i<h;i++)for(U j=0;j<h;j++){int z=corner[(i+1)*(h+1)+j]-corner[i*(h+1)+j]-corner[(i+1)*(h+1)+j+1]+corner[i*(h+1)+j+1];assert(z==0||z==1);if(z)pivots.push_back({i,j});}assert(pivots.size()==rr);
}
U run=0;for(U j=0;j<pivots.size();j++){if(j&&pivots[j].first==pivots[j-1].first+1&&pivots[j].second==pivots[j-1].second + 1)run++;else{if(run){blocks[run]+=count;}run=1;}}if(run){blocks[run]+=count;}
 for(U t=0;t<=h;t++)std::cout<<blocks[t]<<" ";
 std::cout<<"\n"<<std::flush;
}
}

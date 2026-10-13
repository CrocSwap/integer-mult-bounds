// Optimal-matching variant of research/copied-fixed/profiles.cpp (PR #43, Chafik
// Boukhalfa), itself adapted from Dominik Scholz PR35 and icekylinx PR32.
// Change: with LINKS_IN=<file>, the carrier matching is read from a pinned file
// instead of Hopcroft-Karp. Every pinned edge must lie in the same admissible
// adjacency (causal order and frame inclusion); donors and uses are distinct.
// DUMP_EDGES=<file> writes every admissible edge with its exact signed block
// change, used only by optimize_matching.py. All profile code is unchanged.
// Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
// Adapted at h=23,25; original PR35 by Dominik Scholz, PR32 by icekylinx.
// Dimension adaptation at 45/47; extra primes for all source-growth cases.
// Exact bounded-minor inequalities are checked by verify.py. Original credit below.
// Copyright 2026 icekylinx. Apache-2.0; AI-assisted handoff integration.
// Original round3_rankone_profiles.cpp. Requires GCC/Clang unsigned __int128.
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
#include <cstdlib>
using U=uint32_t;using V=uint64_t;
#include "binary_io.hpp"
int main(int argc,char**argv){assert(argc==2||argc==3);std::ifstream f(argv[1],std::ios::binary);U hdr[4];read_array(f,hdr);U h=hdr[0],v=hdr[1],n=hdr[2],q=hdr[3];assert(h==23||h==25);
std::vector<std::array<U,2>>args(n);std::vector<V>core(n),cover(n);std::vector<U>roots(q),kind(q);std::vector<uint8_t>active(n);readv(f,args);readv(f,core);readv(f,cover);readv(f,roots);readv(f,kind);readv(f,active);
std::vector<U>ranks(n),degree(n),begin(n+1);V c=0,inputs=0,loss=0;
for(U x=1;x<n;x++)if(active[x]){if(args[x][0]){c++;assert(args[x][0]<x&&args[x][1]<x);ranks[x]=popcount64(cover[x])-popcount64(core[x]);for(U y:args[x])degree[y]++;}else{ranks[x]=1;inputs++;}}
assert(inputs==v);for(U x:roots)degree[x]++;for(U x=1;x<n;x++)begin[x+1]=begin[x]+degree[x];
std::vector<U>uses(begin.back()),cursor(begin.begin(),begin.end()-1);for(U x=1;x<n;x++)if(active[x]&&args[x][0]){uses[cursor[args[x][0]]++]=2*x;uses[cursor[args[x][1]]++]=2*x+1;}for(U j=0;j<q;j++)uses[cursor[roots[j]]++]=(1U<<31)|j;
auto nd=[&](U e)->U{return e>>31?roots[e&0x7fffffff]:e/2;};
auto before=[&](U a,U b){U x=nd(a),y=nd(b);if(ranks[x]!=ranks[y])return ranks[x]<ranks[y];V ox=a>>31?V(n)+(a&0x7fffffff):x,oy=b>>31?V(n)+(b&0x7fffffff):y;return ox<oy;};
auto incl=[&](U a,U b){U x=nd(a),y=nd(b);return !(core[y]&~core[x])&&!(cover[x]&~cover[y]);};
auto adjacency=[&](U donor,auto&& action){for(U value:args[donor])for(U j=begin[value];j<begin[value+1];j++)if(before(donor*2,uses[j])&&incl(donor*2,uses[j]))if(action(j))return true;return false;};
std::vector<U>donors;for(U x=1;x<n;x++)if(active[x]&&args[x][0]&&adjacency(x,[](U){return true;}))donors.push_back(x);
// Descending donor order changes the retained-carrier network while preserving
// the exhaustive admissibility checks and maximum matching cardinality.
const char* rev=getenv("DONOR_REVERSE"); if(!rev||rev[0]!='0') std::reverse(donors.begin(),donors.end());
std::vector<U>leftmatch(n),rightmatch(uses.size()),distance(n,UINT32_MAX),queue;V matches=0;U phase=0,inf=UINT32_MAX,shortest=inf;
const char* lin=getenv("LINKS_IN");
if(lin){std::ifstream lf(lin,std::ios::binary);U hd[2];read_array(lf,hd);assert(hd[0]==n);std::vector<U>isdonor(n);for(U x:donors)isdonor[x]=1;for(U i=0;i<hd[1];i++){U ed[2];read_array(lf,ed);U x=ed[0],e=ed[1];assert(isdonor[x]&&!leftmatch[x]);U jj=UINT32_MAX;for(U value:args[x])for(U j=begin[value];j<begin[value+1];j++)if(uses[j]==e)jj=j;assert(jj!=UINT32_MAX);bool ok=false;adjacency(x,[&](U j){if(j==jj)ok=true;return ok;});assert(ok);assert(!rightmatch[jj]);leftmatch[x]=jj+1;rightmatch[jj]=x;matches++;}}
else while(true){queue.clear();shortest=inf;for(U x:donors){if(!leftmatch[x]){distance[x]=0;queue.push_back(x);}else distance[x]=inf;}for(U at=0;at<queue.size();at++){U x=queue[at];if(distance[x]>=shortest)continue;adjacency(x,[&](U j){U y=rightmatch[j];if(!y)shortest=distance[x]+1;else if(distance[y]==inf){distance[y]=distance[x]+1;queue.push_back(y);}return false;});}if(shortest==inf)break;
auto aug=[&](auto&&self,U x)->bool{bool ok=adjacency(x,[&](U j){U y=rightmatch[j];if((!y&&distance[x]+1==shortest)||(y&&distance[y]==distance[x]+1&&self(self,y))){leftmatch[x]=j+1;rightmatch[j]=x;return true;}return false;});if(!ok)distance[x]=inf;return ok;};V gained=0;for(U x:donors)if(!leftmatch[x]&&aug(aug,x)){matches++;gained++;}std::cerr<<"h="<<h<<" phase "<<++phase<<" length "<<shortest<<" gained "<<gained<<" total "<<matches<<"\n";assert(gained);}
std::vector<int64_t>hist(h+1);for(U x=1;x<n;x++)if(active[x]){assert(degree[x]);U r=ranks[x];if(args[x][0]){hist[r]+=degree[x]-1;hist[h-r]++;for(U y:args[x]){assert(r>=ranks[y]);hist[r-ranks[y]]++;}}else hist[1]+=degree[x];}
for(U j=0;j<q;j++){U r=ranks[roots[j]];if(kind[j]){hist[r]++;hist[h]++;loss+=r;}else{assert(r<=h-1);hist[h-1-r]++;hist[1]++;}}
V changed=0;for(U donor:donors)if(leftmatch[donor]){U e=uses[leftmatch[donor]-1],target=nd(e),value=e>>31?target:args[target][e&1];assert(value==args[donor][0]||value==args[donor][1]);if(value==args[donor][0])changed++;U ru=ranks[donor],rv=ranks[value],rt=ranks[target];assert(rt>=ru&&ru>=rv);hist[h-ru]--;hist[rv]--;hist[rt-rv]--;hist[rt-ru]++;}
V R=c+q-matches,sum=0;for(U r=0;r<=h;r++){assert(hist[r]>=0);sum+=r*hist[r];}assert(sum==h*R+2*loss);
if(argc==3){std::ofstream out(argv[2],std::ios::binary);U header[2]={n,U(matches)};write_array(out,header);for(U donor:donors)if(leftmatch[donor]){U edge[2]={donor,uses[leftmatch[donor]-1]};write_array(out,edge);}assert(out);}
std::cout<<"{\"h\":"<<h<<",\"v\":"<<v<<",\"c\":"<<c<<",\"q\":"<<q<<",\"baseline_R\":"<<c+q<<",\"matched\":"<<matches<<",\"R\":"<<R<<",\"orientation_changes\":"<<changed<<",\"rank_sum\":"<<sum<<",\"loss\":"<<loss<<",\"histogram\":[";for(U r=0;r<=h;r++){if(r)std::cout<<",";std::cout<<hist[r];}std::cout<<"]}"<<std::endl;
// Reconstruct the actual transition multiset before changing the common basis.
struct Frame{V core,cover;U rank;};std::vector<Frame>frames{{0,0,0},{0,0,h}};std::map<std::pair<V,V>,U>frame_lookup;std::vector<U>fi(n);
for(U x=1;x<n;x++)if(active[x]){auto key=std::make_pair(core[x],cover[x]);auto z=frame_lookup.find(key);if(z==frame_lookup.end()){U id=frames.size();frames.push_back({core[x],cover[x],ranks[x]});frame_lookup[key]=id;fi[x]=id;}else fi[x]=z->second;}
std::map<std::pair<U,U>,int64_t>transitions;int64_t singles=0;
auto edge=[&](U a,U b,int64_t count){if(a==b)return;transitions[{a,b}]+=count;};
for(U x=1;x<n;x++)if(active[x]){U r=ranks[x];if(args[x][0]){edge(0,fi[x],degree[x]-1);edge(fi[x],1,1);for(U y:args[x])edge(fi[y],fi[x],1);}else edge(0,fi[x],degree[x]);}
for(U j=0;j<q;j++){U r=ranks[roots[j]];if(kind[j]){edge(0,fi[roots[j]],1);edge(0,1,1);}else singles+=h-r;}
for(U donor:donors)if(leftmatch[donor]){U e=uses[leftmatch[donor]-1],target=nd(e),value=e>>31?target:args[target][e&1];edge(fi[donor],1,-1);edge(0,fi[value],-1);edge(fi[value],fi[target],-1);edge(fi[donor],fi[target],1);}
V p=2305843009213693951ULL;
auto mul=[&](V a,V b)->V{return (__uint128_t)a*b%p;};
auto power=[&](V a,V b)->V{V r=1;for(;b;b>>=1,a=mul(a,a))if(b&1)r=mul(r,a);return r;};
auto sub=[&](V a,V b)->V{return (a+p-b)%p;};
std::vector<std::vector<V>>matrix_cache(frames.size());
auto matrix=[&](U id)->const std::vector<V>&{auto&A=matrix_cache[id];if(!A.empty())return A;A.assign(h*h,0);if(id==0)return A;if(id==1){for(U i=0;i<h;i++)A[i*h+i]=1;return A;}
 auto f=frames[id];U c=popcount64(f.core);V out=f.cover&~f.core;U nn=popcount64(out);
 if(c==3){V factor=power(6*(h+1),p-2);for(U i=0;i<h;i++)for(U j=0;j<h;j++){V wi=3+((f.core>>i)&1);V zj=((f.core>>j)&1)?3*(h+1)-10:p-10;A[i*h+j]=mul(mul(wi,zj),factor);}return A;}
 assert(c==1||c==2);V s=3-c,d=s*s+(c-1)*nn,den=3*(h+1)*d,inv=power(den,p-2);
 for(U i=0;i<h;i++)for(U j=0;j<h;j++){V oi=(out>>i)&1,oj=(out>>j)&1,wi=3+((f.core>>i)&1),zj=((f.core>>j)&1)?3*(h+1)-10:p-10;
  V num=(mul(s*oi,zj)+3*(h+1)*s*wi*oj+mul(nn*wi,zj))%p;num=sub(num,3*(h+1)*(c-1)*oi*oj);A[i*h+j]=(V(i==j&&oi)+mul(num,inv))%p;
 }return A;};

auto prof_pair=[&](U aa,U bb)->std::vector<U>{std::vector<U> out;if(aa==bb)return out;assert(frames[bb].rank>=frames[aa].rank);U rr=frames[bb].rank-frames[aa].rank;if(!rr)return out;
 if(rr<=2){for(U k=0;k<rr;k++)out.push_back(1);return out;}if(aa==0&&bb==1){out.push_back(h);return out;}
 const auto&A=matrix(aa);const auto&B=matrix(bb);std::vector<V>M(h*h);for(U x=0;x<h*h;x++)M[x]=sub(B[x],A[x]);std::vector<std::pair<U,U>>pivots;
 for(U i=0;i<h;i++){int j=h-1;while(j>=0&&!M[i*h+j])j--;if(j<0)continue;pivots.push_back({i,U(j)});V inv=power(M[i*h+j],p-2);for(U k=i+1;k<h;k++){V z=mul(M[k*h+j],inv);if(z)for(U col=0;col<=U(j);col++)M[k*h+col]=sub(M[k*h+col],mul(z,M[i*h+col]));}}
 assert(pivots.size()==rr);
 if(aa>1&&bb>1&&(popcount64(frames[aa].core)==3||(popcount64(frames[aa].core)==2&&popcount64(frames[bb].core)==1))){
  matrix_cache[aa].clear();matrix_cache[bb].clear();std::vector<std::vector<std::pair<U,U>>> all{pivots};
  for(V extra:{2147483647ULL,524287ULL}){p=extra;matrix_cache[aa].clear();matrix_cache[bb].clear();const auto&C=matrix(aa);const auto&D=matrix(bb);std::vector<V>Y(h*h);for(U z=0;z<h*h;z++)Y[z]=sub(D[z],C[z]);std::vector<std::pair<U,U>> pp;
   for(U i=0;i<h;i++){int j=h-1;while(j>=0&&!Y[i*h+j])j--;if(j<0)continue;pp.push_back({i,U(j)});V inv=power(Y[i*h+j],p-2);for(U k=i+1;k<h;k++){V z=mul(Y[k*h+j],inv);if(z)for(U col=0;col<=U(j);col++)Y[k*h+col]=sub(Y[k*h+col],mul(z,Y[i*h+col]));}}
   all.push_back(std::move(pp));}
  p=2305843009213693951ULL;matrix_cache[aa].clear();matrix_cache[bb].clear();
  std::vector<int> corner((h+1)*(h+1));for(U i=0;i<h;i++)for(U j=0;j<h;j++){int best=0;for(auto&pp:all){int rank=0;for(auto [row,col]:pp)rank+=row<=i&&col>=j;best=std::max(best,rank);}corner[(i+1)*(h+1)+j]=best;}
  pivots.clear();for(U i=0;i<h;i++)for(U j=0;j<h;j++){int z=corner[(i+1)*(h+1)+j]-corner[i*(h+1)+j]-corner[(i+1)*(h+1)+j+1]+corner[i*(h+1)+j+1];assert(z==0||z==1);if(z)pivots.push_back({i,j});}assert(pivots.size()==rr);}
 U run=0;for(U j=0;j<pivots.size();j++){if(j&&pivots[j].first==pivots[j-1].first+1&&pivots[j].second==pivots[j-1].second+1)run++;else{if(run)out.push_back(run);run=1;}}if(run)out.push_back(run);
 matrix_cache[aa].clear();matrix_cache[bb].clear();return out;};
if(const char* dp=getenv("DUMP_EDGES")){
 std::map<std::pair<U,U>,std::vector<U>> pc;auto get=[&](U a,U b)->const std::vector<U>&{auto k=std::make_pair(a,b);auto it=pc.find(k);if(it!=pc.end())return it->second;return pc[k]=prof_pair(a,b);};
 std::ofstream de(dp);V ne=0;
 for(U x:donors){adjacency(x,[&](U j){U e=uses[j],target=nd(e),value=e>>31?target:args[target][e&1];
   // signed multiset of block widths: +(x,t) -(x,1) -(0,value) -(value,target)
   std::map<U,int64_t> d;for(U t:get(fi[x],fi[target]))d[t]++;for(U t:get(fi[x],1))d[t]--;for(U t:get(0,fi[value]))d[t]--;for(U t:get(fi[value],fi[target]))d[t]--;
   de<<x<<' '<<e<<' '<<j;for(auto&[t,c]:d)if(c)de<<' '<<t<<':'<<c;de<<'\n';ne++;return false;});}
 std::cerr<<"dumped edges "<<ne<<" pairs "<<pc.size()<<"\n";return 0;}
std::vector<int64_t>blocks(h+1);blocks[1]=singles;V done=0,matrices=0,crt_matrices=0,crt_disagreements=0;U longest=0;std::map<U,V>correction_hist;
for(auto&[key,count]:transitions){if(!count)continue;assert(count>0);U aa=key.first,bb=key.second;U rr=frames[bb].rank-frames[aa].rank;assert(frames[bb].rank>=frames[aa].rank);if(!rr)continue;
 if(rr<=2){blocks[1]+=count*rr;continue;}if(aa==0&&bb==1){blocks[h]+=count;continue;}
 if(aa>1&&bb>1){
  assert(!(frames[bb].core&~frames[aa].core));
  assert(!(frames[aa].cover&~frames[bb].cover));
  U ca=popcount64(frames[aa].core),cb=popcount64(frames[bb].core);
  assert(ca==3||frames[aa].core==frames[bb].core||(ca==2&&cb==1));
 }
 const auto&A=matrix(aa);const auto&B=matrix(bb);std::vector<V>M(h*h);for(U x=0;x<h*h;x++)M[x]=sub(B[x],A[x]);std::vector<std::pair<U,U>>pivots;
 for(U i=0;i<h;i++){int j=h-1;while(j>=0&&!M[i*h+j])j--;if(j<0)continue;pivots.push_back({i,U(j)});V inv=power(M[i*h+j],p-2);for(U k=i+1;k<h;k++){V z=mul(M[k*h+j],inv);if(z)for(U col=0;col<=U(j);col++)M[k*h+col]=sub(M[k*h+col],mul(z,M[i*h+col]));}}
 assert(pivots.size()==rr);
// All minors have numerator bounded independently of matrix size, since the
// matrix is a 0/1 diagonal mask plus a correction of rank at most four.
// Source growth and core-two -> core-one use all three primes at these dimensions.
if(aa>1&&bb>1&&(popcount64(frames[aa].core)==3||(popcount64(frames[aa].core)==2&&popcount64(frames[bb].core)==1))){
 assert(h==23||h==25);crt_matrices++;matrix_cache[aa].clear();matrix_cache[bb].clear();std::vector<std::vector<std::pair<U,U>>> all{pivots};
 for(V extra:{2147483647ULL,524287ULL}){p=extra;matrix_cache[aa].clear();matrix_cache[bb].clear();const auto&C=matrix(aa);const auto&D=matrix(bb);std::vector<V>Y(h*h);for(U z=0;z<h*h;z++)Y[z]=sub(D[z],C[z]);std::vector<std::pair<U,U>> pp;
  for(U i=0;i<h;i++){int j=h-1;while(j>=0&&!Y[i*h+j])j--;if(j<0)continue;pp.push_back({i,U(j)});V inv=power(Y[i*h+j],p-2);for(U k=i+1;k<h;k++){V z=mul(Y[k*h+j],inv);if(z)for(U col=0;col<=U(j);col++)Y[k*h+col]=sub(Y[k*h+col],mul(z,Y[i*h+col]));}}
  if(pp!=pivots)crt_disagreements++;all.push_back(std::move(pp));
 }
 p=2305843009213693951ULL;matrix_cache[aa].clear();matrix_cache[bb].clear();
 std::vector<int> corner((h+1)*(h+1));for(U i=0;i<h;i++)for(U j=0;j<h;j++){int best=0;for(auto&pp:all){int rank=0;for(auto [row,col]:pp)rank+=row<=i&&col>=j;best=std::max(best,rank);}corner[(i+1)*(h+1)+j]=best;}
 pivots.clear();for(U i=0;i<h;i++)for(U j=0;j<h;j++){int z=corner[(i+1)*(h+1)+j]-corner[i*(h+1)+j]-corner[(i+1)*(h+1)+j+1]+corner[i*(h+1)+j+1];assert(z==0||z==1);if(z)pivots.push_back({i,j});}assert(pivots.size()==rr);
}
U run=0;for(U j=0;j<pivots.size();j++){if(j&&pivots[j].first==pivots[j-1].first+1&&pivots[j].second==pivots[j-1].second+1)run++;else{if(run){blocks[run]+=count;longest=std::max(longest,run);}run=1;}}if(run){blocks[run]+=count;longest=std::max(longest,run);}matrices++;matrix_cache[aa].clear();matrix_cache[bb].clear();
 if(++done%10000==0)std::cerr<<"profiles "<<done<<" of "<<transitions.size()<<"\n";
}
V mass=0;for(U t=1;t<=h;t++){assert(blocks[t]>=0);mass+=t*blocks[t];}assert(mass==sum);
std::string target=std::string(argv[1])+".round3_rankone_certified_profiles.json";std::ofstream out(target);assert(out);out<<"{\"h\":"<<h<<",\"v\":"<<v<<",\"R\":"<<R<<",\"loss\":"<<loss<<",\"rank_sum\":"<<mass<<",\"field_prime\":"<<p<<",\"frames\":"<<frames.size()<<",\"distinct_matrices\":"<<matrices<<",\"crt_matrices\":"<<crt_matrices<<",\"crt_disagreements\":"<<crt_disagreements<<",\"blocks\":[";for(U t=0;t<=h;t++){if(t)out<<",";out<<blocks[t];}out<<"]}\n";std::cerr<<"CRT matrices "<<crt_matrices<<" differing modular profiles "<<crt_disagreements<<"\n";std::cerr<<"RANKONE h "<<h<<" longest "<<longest<<" output "<<target<<"\n";

}

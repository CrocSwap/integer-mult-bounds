// RaD: complete fixed-basis profiles of actual signed positive-frame projectors.
// This is newly authored code. Binary I/O uses the credited Apache-2.0 helper.
// Every NE rank is certified from a prime-product integer-minor bound;
// no diagonal-mask or correction-rank shortcut is assumed.
#include <algorithm>
#include <array>
#include <cassert>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <numeric>
#include <string>
#include <vector>
using U=uint32_t;using V=uint64_t;using I=int64_t;
#include "binary_io.hpp"


struct Frame {V forced=0;U rank=0;std::vector<int8_t> symbols;};
static inline U mulm(U a,U b,U p){return V(a)*b%p;}
static inline U powm(U a,V b,U p){U o=1;for(;b;b>>=1,a=mulm(a,a,p))if(b&1)o=mulm(o,a,p);return o;}
static inline U subm(U a,U b,U p){return a>=b?a-b:a+p-b;}
static inline U addm(U a,U b,U p){U s=a+b;return s>=p?s-p:s;}
static inline U modi(I x,U p){I r=x%I(p);return U(r<0?r+p:r);}
static inline U inv(U a,U p){assert(a%p);return powm(a,p-2,p);}
// projector of frame F in basis L=I+cJ, c=cn/cd, mod p
std::vector<U> projector(const Frame&F,U h,U id,I cn,I cd,U p){
 std::vector<U>M(h*h,0);if(id==0)return M;if(id==1){for(U i=0;i<h;i++)M[i*h+i]=1;return M;}
 U c=mulm(modi(cn,p),inv(modi(cd,p),p),p);
 U one=1, hh=h%p;
 U mu=mulm(c,inv(addm(one,mulm(c,hh,p),p),p),p);                 // c/(1+ch)
 U lam=mulm(subm(0,addm(one,mulm(mu,modi(9-I(h),p),p),p),p),inv(3,p),p); // -(1+mu(9-h))/3
 U c3=mulm(3,c,p);
 U f=popcount64(F.forced);
 std::vector<U>w(h),z(h);for(U i=0;i<h;i++){U fi=(F.forced>>i)&1;w[i]=addm(fi,c3,p);z[i]=addm(fi,lam,p);}
 if(f==3){U i2=inv(2,p);for(U i=0;i<h;i++)for(U j=0;j<h;j++)M[i*h+j]=mulm(mulm(w[i],z[j],p),i2,p);return M;}
 assert(f==1||f==2);I s=3-f;
 std::map<U,std::pair<I,I>>cls;for(I x:F.symbols)if(std::abs(x)>1){auto&q=cls[std::abs(x)];q.first++;q.second+=x>0?1:-1;}
 std::vector<U>u(h,0);U v=0;
 for(auto&[k,q]:cls)v=addm(v,mulm(modi(q.second*q.second,p),inv(modi(q.first,p),p),p),p);
 for(U i=0;i<h;i++)if(std::abs(F.symbols[i])>1){auto q=cls[std::abs(F.symbols[i])];u[i]=mulm(modi((F.symbols[i]>0?1:-1)*q.second,p),inv(modi(q.first,p),p),p);}
 U d=addm(modi(s*s,p),mulm(modi(f-1,p),v,p),p);U di=inv(d,p);U sp=modi(s,p),fm=modi(f-1,p);
 for(U i=0;i<h;i++)for(U j=0;j<h;j++){U val=0;
  if(std::abs(F.symbols[i])>1&&std::abs(F.symbols[i])==std::abs(F.symbols[j])){I sign=(F.symbols[i]>0?1:-1)*(F.symbols[j]>0?1:-1);val=mulm(modi(sign,p),inv(modi(cls[std::abs(F.symbols[i])].first,p),p),p);}
  U t=addm(addm(mulm(sp,mulm(u[i],z[j],p),p),mulm(sp,mulm(w[i],u[j],p),p),p),mulm(v,mulm(w[i],z[j],p),p),p);
  t=subm(t,mulm(fm,mulm(u[i],u[j],p),p),p);
  M[i*h+j]=addm(val,mulm(t,di,p),p);}
 return M;
}
int main(int argc,char**argv){
 // usage: cprof dag uses cn cd out.json
 assert(argc==6);I cn=std::stoll(argv[3]),cd=std::stoll(argv[4]);
 std::ifstream input(argv[1],std::ios::binary);U header[4];read_array(input,header);U h=header[0],v=header[1],n=header[2],q=header[3];
 std::vector<std::array<U,2>>args(n);std::vector<V>core(n),cover(n);std::vector<U>roots(q),kind(q);std::vector<uint8_t>active(n);
 readv(input,args);readv(input,core);readv(input,cover);readv(input,roots);readv(input,kind);readv(input,active);
 std::ifstream labels(std::string(argv[1])+".positive",std::ios::binary);U lh[2];read_array(labels,lh);assert(lh[0]==h&&lh[1]==n);
 std::vector<U>rank(n),degree(n);std::vector<V>forced(n);std::vector<int8_t>symbols(n*h);readv(labels,rank);readv(labels,forced);readv(labels,symbols);
 V c=0,loss=0;for(U x=1;x<n;x++)if(active[x]&&args[x][0]){c++;for(U y:args[x])degree[y]++;}for(U x:roots)degree[x]++;
 for(U j=0;j<q;j++)if(kind[j])loss+=rank[roots[j]];
 std::ifstream usesfile(argv[2],std::ios::binary);U uh[2];read_array(usesfile,uh);assert(uh[0]==n);U matches=uh[1];std::vector<std::array<U,2>>links(matches);readv(usesfile,links);
 std::vector<Frame>frames(2);frames[1].rank=h;std::map<std::pair<V,std::vector<int8_t>>,U>lk;std::vector<U>fi(n);
 for(U x=1;x<n;x++)if(active[x]){std::vector<int8_t>sy(symbols.begin()+x*h,symbols.begin()+(x+1)*h);auto key=std::make_pair(forced[x],sy);auto z=lk.find(key);
  if(z==lk.end()){U id=frames.size();Frame F;F.forced=forced[x];F.rank=rank[x];F.symbols=std::move(sy);frames.push_back(std::move(F));lk.emplace(std::move(key),id);fi[x]=id;}else fi[x]=z->second;}
 std::map<std::pair<U,U>,I>tc;I singles=0;auto edge=[&](U a,U b,I k){if(a!=b)tc[{a,b}]+=k;};
 for(U x=1;x<n;x++)if(active[x]){if(args[x][0]){edge(0,fi[x],degree[x]-1);edge(fi[x],1,1);for(U y:args[x])edge(fi[y],fi[x],1);}else edge(0,fi[x],degree[x]);}
 for(U j=0;j<q;j++){if(kind[j]){edge(0,fi[roots[j]],1);edge(0,1,1);}else singles+=h-rank[roots[j]];}
 for(auto [donor,use]:links){U target=use>>31?roots[use&0x7fffffff]:use/2,value=use>>31?target:args[target][use&1];edge(fi[donor],1,-1);edge(0,fi[value],-1);edge(fi[value],fi[target],-1);edge(fi[donor],fi[target],1);}
 const U P[3]={2147483647u,2147483629u,2147483587u};
 std::vector<std::array<std::vector<U>,3>> pcache(frames.size());
 auto pair_blocks=[&](U a,U b)->std::vector<U>{std::vector<U>out;if(a==b)return out;U r=frames[b].rank-frames[a].rank;if(!r)return out;if(r==1){out.push_back(1);return out;}if(a==0&&b==1){out.push_back(h);return out;}
  std::vector<uint8_t>C((h+1)*(h+1),0);
  for(U pi=0;pi<3;pi++){U p=P[pi];for(U id:{a,b})if(pcache[id][pi].empty())pcache[id][pi]=projector(frames[id],h,id<2?id:2,cn,cd,p);
   auto&A=pcache[a][pi];auto&B=pcache[b][pi];std::vector<U>M(h*h);for(U z=0;z<h*h;z++)M[z]=subm(B[z],A[z],p);
   std::vector<std::pair<U,U>>pv;for(U i=0;i<h;i++){int j=h-1;while(j>=0&&!M[i*h+j])j--;if(j<0)continue;pv.emplace_back(i,U(j));U iv=inv(M[i*h+j],p);
    for(U k=i+1;k<h;k++){U sc=mulm(M[k*h+j],iv,p);if(sc)for(U col=0;col<=U(j);col++)M[k*h+col]=subm(M[k*h+col],mulm(sc,M[i*h+col],p),p);}}
   std::vector<uint8_t>cc((h+1)*(h+1));U at=0;for(U i=0;i<h;i++){int col=at<pv.size()&&pv[at].first==i?int(pv[at++].second):-1;for(U j=0;j<h;j++)cc[(i+1)*(h+1)+j]=cc[i*(h+1)+j]+(int(j)<=col);}
   for(U z=0;z<C.size();z++)C[z]=std::max(C[z],cc[z]);}
  std::vector<std::pair<U,U>>piv;for(U i=0;i<h;i++)for(U j=0;j<h;j++){int z=C[(i+1)*(h+1)+j]-C[i*(h+1)+j]-C[(i+1)*(h+1)+j+1]+C[i*(h+1)+j+1];if(z==1)piv.emplace_back(i,j);}
  U run=0;for(U k=0;k<piv.size();k++){if(k&&piv[k].first==piv[k-1].first+1&&piv[k].second==piv[k-1].second+1)run++;else{if(run)out.push_back(run);run=1;}}if(run)out.push_back(run);return out;};
 if(const char*dp=getenv("DUMP_EDGES")){
  std::vector<U>oldrank(n);for(U x=1;x<n;x++)if(active[x])oldrank[x]=args[x][0]?popcount64(cover[x])-popcount64(core[x]):1;
  std::vector<U>begin(n+1);for(U x=1;x<n;x++)begin[x+1]=begin[x]+degree[x];std::vector<U>uses(begin.back()),cur(begin.begin(),begin.end()-1);
  for(U x=1;x<n;x++)if(active[x]&&args[x][0]){uses[cur[args[x][0]]++]=2*x;uses[cur[args[x][1]]++]=2*x+1;}for(U j=0;j<q;j++)uses[cur[roots[j]]++]=(1U<<31)|j;
  auto nd=[&](U e)->U{return e>>31?roots[e&0x7fffffff]:e/2;};
  auto before=[&](U a,U b){U x=nd(a),y=nd(b);if(rank[x]!=rank[y])return rank[x]<rank[y];V ox=a>>31?V(n)+(a&0x7fffffff):x,oy=b>>31?V(n)+(b&0x7fffffff):y;return ox<oy;};
  auto incl=[&](U a,U b){U x=nd(a),y=nd(b);if(forced[y]&~forced[x])return false;int expect[66]{};bool seen[66]{};
   for(U i=0;i<h;i++){int sx=symbols[V(x)*h+i],sy=symbols[V(y)*h+i];if(!sy){if(sx)return false;}else if(sy==1){if(sx!=1)return false;}else{int k=sy<0?-sy:sy,z=sy<0?-sx:sx;if(seen[k]){if(expect[k]!=z)return false;}else{seen[k]=true;expect[k]=z;}}}return true;};
  std::ofstream de(dp);V ne=0;std::map<std::pair<U,U>,std::vector<U>>pc;auto get=[&](U a,U b)->const std::vector<U>&{auto k=std::make_pair(a,b);auto it=pc.find(k);if(it!=pc.end())return it->second;return pc[k]=pair_blocks(a,b);};
  for(U x=1;x<n;x++)if(active[x]&&args[x][0])for(U value:args[x])for(U j=begin[value];j<begin[value+1];j++){U e=uses[j];if(!(before(x*2,e)&&incl(x*2,e)))continue;
   U target=nd(e),val=e>>31?target:args[target][e&1];std::map<U,int64_t>d;
   for(U t:get(fi[x],fi[target]))d[t]++;for(U t:get(fi[x],1))d[t]--;for(U t:get(0,fi[val]))d[t]--;for(U t:get(fi[val],fi[target]))d[t]--;
   de<<x<<' '<<e<<' '<<j;for(auto&[t,cc]:d)if(cc)de<<' '<<t<<':'<<cc;de<<'\n';ne++;}
  std::cerr<<"dumped "<<ne<<" edges\n";return 0;}

 std::vector<I>blocks(h+1);blocks[1]=singles;V mass=0,bad=0;
 std::map<std::pair<U,U>,U> dummy;
 std::vector<std::array<std::vector<U>,3>> cache(frames.size());
 for(auto&[key,count]:tc)if(count){U a=key.first,b=key.second;U r=frames[b].rank-frames[a].rank;if(!r)continue;if(r==1){blocks[1]+=count;continue;}if(a==0&&b==1){blocks[h]+=count;continue;}
  std::vector<uint8_t>C((h+1)*(h+1),0);
  for(U pi=0;pi<3;pi++){U p=P[pi];for(U id:{a,b})if(cache[id][pi].empty())cache[id][pi]=projector(frames[id],h,id<2?id:2,cn,cd,p);
   auto&A=cache[a][pi];auto&B=cache[b][pi];std::vector<U>M(h*h);for(U z=0;z<h*h;z++)M[z]=subm(B[z],A[z],p);
   std::vector<std::pair<U,U>>pv;for(U i=0;i<h;i++){int j=h-1;while(j>=0&&!M[i*h+j])j--;if(j<0)continue;pv.emplace_back(i,U(j));U iv=inv(M[i*h+j],p);
    for(U k=i+1;k<h;k++){U sc=mulm(M[k*h+j],iv,p);if(sc)for(U col=0;col<=U(j);col++)M[k*h+col]=subm(M[k*h+col],mulm(sc,M[i*h+col],p),p);}}
   std::vector<uint8_t>cc((h+1)*(h+1));U at=0;for(U i=0;i<h;i++){int col=at<pv.size()&&pv[at].first==i?int(pv[at++].second):-1;for(U j=0;j<h;j++)cc[(i+1)*(h+1)+j]=cc[i*(h+1)+j]+(int(j)<=col);}
   for(U z=0;z<C.size();z++)C[z]=std::max(C[z],cc[z]);}
  std::vector<std::pair<U,U>>piv;for(U i=0;i<h;i++)for(U j=0;j<h;j++){int z=C[(i+1)*(h+1)+j]-C[i*(h+1)+j]-C[(i+1)*(h+1)+j+1]+C[i*(h+1)+j+1];if(z==1)piv.emplace_back(i,j);else if(z!=0)bad++;}
  if(piv.size()!=r){bad++;}
  U run=0;for(U k=0;k<piv.size();k++){if(k&&piv[k].first==piv[k-1].first+1&&piv[k].second==piv[k-1].second+1)run++;else{if(run)blocks[run]+=count;run=1;}}if(run)blocks[run]+=count;}
 for(U t=1;t<=h;t++)mass+=t*blocks[t];
 V R=c+q-matches;std::ofstream out(argv[5]);out<<"{\"h\":"<<h<<",\"v\":"<<v<<",\"R\":"<<R<<",\"matched\":"<<matches<<",\"loss\":"<<loss<<",\"rank_sum\":"<<mass<<",\"cn\":"<<cn<<",\"cd\":"<<cd<<",\"rank_defects\":"<<bad<<",\"blocks\":[";for(U t=0;t<=h;t++){if(t)out<<",";out<<blocks[t];}out<<"]}\n";
}

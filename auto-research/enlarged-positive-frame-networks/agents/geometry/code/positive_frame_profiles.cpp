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
#include <boost/multiprecision/cpp_int.hpp>
using U=uint32_t;using V=uint64_t;using I=int64_t;
using boost::multiprecision::cpp_int;
#include "binary_io.hpp"

struct Frame {V forced=0,den=1;U rank=0;std::vector<int8_t> symbols;std::vector<I> numerator;};
struct Transition {U a,b,r,primes=0;I count;cpp_int denominator,entry_bound,minor_bound;std::vector<uint8_t> corner;std::vector<std::pair<U,U>> pivots;};
U multiply(U a,U b,U p){return V(a)*b%p;}
U power(U a,U b,U p){U out=1;for(;b;b>>=1,a=multiply(a,a,p))if(b&1)out=multiply(out,a,p);return out;}
U subtract(U a,U b,U p){return a>=b?a-b:a+p-b;}
bool prime(U p){if(p<2)return false;if(!(p&1))return p==2;for(U d=3;V(d)*d<=p;d+=2)if(p%d==0)return false;return true;}
cpp_int ipower(cpp_int a,U n){cpp_int z=1;for(;n;n>>=1,a*=a)if(n&1)z*=a;return z;}
unsigned bits(const cpp_int&x){assert(x>0);return boost::multiprecision::msb(x)+1;}

void make_matrix(Frame&F,U h,bool negative,U special){
 F.numerator.assign(h*h,0);if(special==0)return;
 if(special==1){for(U i=0;i<h;i++)F.numerator[i*h+i]=1;return;}
 U f=popcount64(F.forced);
 if(f==3){
  assert(F.rank==1);F.den=negative?2*(h+3):6*(h+1);
  for(U i=0;i<h;i++)for(U j=0;j<h;j++){
   I fi=(F.forced>>i)&1,fj=(F.forced>>j)&1;
   F.numerator[i*h+j]=negative?((h+3)*fi-4)*(1+fj):(fi+3)*(3*(h+1)*fj-10);
  }
 }else{
  assert(f==1||f==2);I s=3-f;
  std::map<U,std::pair<I,I>> classes;
  for(I x:F.symbols)if(std::abs(x)>1){auto&c=classes[std::abs(x)];c.first++;c.second+=x>0?1:-1;}
  assert(classes.size()==F.rank);V K=1;
  for(auto&[id,c]:classes)K=std::lcm(K,V(c.first));
  assert(K<=ipower(cpp_int(3),(h+1)/3));
  I vn=0;for(auto&[id,c]:classes)vn+=c.second*c.second*(K/c.first);
  I dn=s*s*K+(f-1)*vn;assert(dn>0);
  V base=negative?h+3:3*(h+1);F.den=base*K*dn;
  std::vector<I>u(h);for(U i=0;i<h;i++)if(std::abs(F.symbols[i])>1){auto c=classes[std::abs(F.symbols[i])];u[i]=(F.symbols[i]>0?1:-1)*c.second*(K/c.first);}
  for(U i=0;i<h;i++)for(U j=0;j<h;j++){
   I fi=(F.forced>>i)&1,fj=(F.forced>>j)&1,num=0;
   if(std::abs(F.symbols[i])>1&&std::abs(F.symbols[i])==std::abs(F.symbols[j])){
    I sign=(F.symbols[i]>0?1:-1)*(F.symbols[j]>0?1:-1);
    num=sign*I(F.den/classes[std::abs(F.symbols[i])].first);
   }
   if(negative){I wi=(h+3)*fi-4,zj=1+fj;
    num+=I(h+3)*I(K)*s*u[i]*zj+I(K)*s*wi*u[j]+I(K)*vn*wi*zj-I(h+3)*(f-1)*u[i]*u[j];
   }else{I wi=fi+3,zj=3*(h+1)*fj-10;
    num+=I(K)*s*u[i]*zj+I(base)*I(K)*s*wi*u[j]+I(K)*vn*wi*zj-I(base)*(f-1)*u[i]*u[j];
   }
   F.numerator[i*h+j]=num;
  }
 }
 V g=F.den;for(I x:F.numerator)g=std::gcd(g,V(std::abs(x)));assert(g);
 F.den/=g;for(I&x:F.numerator)x/=I(g);
 assert(F.den>0);I trace=0;for(U i=0;i<h;i++)trace+=F.numerator[i*h+i];assert(trace==I(F.rank*F.den));
 for(I x:F.numerator)assert(cpp_int(std::abs(x))<=cpp_int(F.den)*(negative?2*h+8:20*h+100));
}

int main(int argc,char**argv){
 assert(argc==5||argc==6);auto start=std::chrono::steady_clock::now();std::string basis=argv[3];assert(basis=="negative"||basis=="fixed");bool negative=basis=="negative";
 std::ifstream input(argv[1],std::ios::binary);U header[4];read_array(input,header);U h=header[0],v=header[1],n=header[2],q=header[3];assert(h>=10&&h<=35);
 std::vector<std::array<U,2>>args(n);std::vector<V>core(n),cover(n);std::vector<U>roots(q),kind(q);std::vector<uint8_t>active(n);
 readv(input,args);readv(input,core);readv(input,cover);readv(input,roots);readv(input,kind);readv(input,active);
 std::ifstream labels(std::string(argv[1])+".positive",std::ios::binary);U lh[2];read_array(labels,lh);assert(lh[0]==h&&lh[1]==n);
 std::vector<U>rank(n),degree(n),oldrank(n);std::vector<V>forced(n);std::vector<int8_t>symbols(n*h);readv(labels,rank);readv(labels,forced);readv(labels,symbols);
 V c=0,inputs=0,loss=0;std::vector<int64_t>hist(h+1);
 for(U x=1;x<n;x++)if(active[x]){if(args[x][0]){c++;assert(args[x][0]<x&&args[x][1]<x);oldrank[x]=popcount64(cover[x])-popcount64(core[x]);for(U y:args[x])degree[y]++;}else{oldrank[x]=1;inputs++;}}
 assert(inputs==v);for(U x:roots)degree[x]++;
 for(U x=1;x<n;x++)if(active[x]){assert(degree[x]);U r=rank[x];if(args[x][0]){hist[r]+=degree[x]-1;hist[h-r]++;for(U y:args[x]){assert(r>=rank[y]);hist[r-rank[y]]++;}}else{assert(r==1);hist[1]+=degree[x];}}
 for(U j=0;j<q;j++){U r=rank[roots[j]];if(kind[j]){assert(r==h-1);hist[r]++;hist[h]++;loss+=r;}else{assert(r<=h-1);hist[h-1-r]++;hist[1]++;}}
 std::ifstream usesfile(argv[2],std::ios::binary);U uh[2];read_array(usesfile,uh);assert(uh[0]==n);U matches=uh[1];
 std::vector<std::array<U,2>>links(matches);readv(usesfile,links);std::vector<uint8_t>used_donor(n);std::map<U,U>used_use;
 for(auto [donor,use]:links){assert(donor<n&&active[donor]&&args[donor][0]&&!used_donor[donor]);used_donor[donor]=1;assert(used_use.emplace(use,donor).second);
  U target,value;V order;if(use>>31){U j=use&0x7fffffff;assert(j<q);target=value=roots[j];order=V(n)+j;}else{target=use/2;assert(target<n&&active[target]&&args[target][0]);value=args[target][use&1];order=target;}
  assert(value==args[donor][0]||value==args[donor][1]);assert(std::make_tuple(rank[donor],oldrank[donor],V(donor))<std::make_tuple(rank[target],oldrank[target],order));
  U rd=rank[donor],rv=rank[value],rt=rank[target];assert(rt>=rd&&rd>=rv);hist[h-rd]--;hist[rv]--;hist[rt-rv]--;hist[rt-rd]++;
 }
 V R=c+q-matches,rank_mass=0;for(U r=0;r<=h;r++){assert(hist[r]>=0);rank_mass+=r*hist[r];}assert(rank_mass==h*R+2*loss);
 std::vector<Frame>frames(2);frames[1].rank=h;std::map<std::pair<V,std::vector<int8_t>>,U>frame_lookup;std::vector<U>fi(n);
 for(U x=1;x<n;x++)if(active[x]){std::vector<int8_t>sy(symbols.begin()+x*h,symbols.begin()+(x+1)*h);auto key=std::make_pair(forced[x],sy);auto z=frame_lookup.find(key);
  if(z==frame_lookup.end()){U id=frames.size();Frame F;F.forced=forced[x];F.rank=rank[x];F.symbols=std::move(sy);frames.push_back(std::move(F));frame_lookup.emplace(std::move(key),id);fi[x]=id;}else{fi[x]=z->second;assert(frames[fi[x]].rank==rank[x]);}}
 for(U id=0;id<frames.size();id++)make_matrix(frames[id],h,negative,id<2?id:2);
 std::map<std::pair<U,U>,I>transition_counts;I singles=0;auto edge=[&](U a,U b,I count){if(a!=b)transition_counts[{a,b}]+=count;};
 for(U x=1;x<n;x++)if(active[x]){if(args[x][0]){edge(0,fi[x],degree[x]-1);edge(fi[x],1,1);for(U y:args[x])edge(fi[y],fi[x],1);}else edge(0,fi[x],degree[x]);}
 for(U j=0;j<q;j++){if(kind[j]){edge(0,fi[roots[j]],1);edge(0,1,1);}else singles+=h-rank[roots[j]];}
 for(auto [donor,use]:links){U target=use>>31?roots[use&0x7fffffff]:use/2,value=use>>31?target:args[target][use&1];edge(fi[donor],1,-1);edge(0,fi[value],-1);edge(fi[value],fi[target],-1);edge(fi[donor],fi[target],1);}
 std::vector<I>blocks(h+1);blocks[1]=singles;std::vector<Transition>transitions;cpp_int largest=1;unsigned largest_entry_bits=0,largest_bound_bits=0;
 for(auto&[key,count]:transition_counts)if(count){assert(count>0);U a=key.first,b=key.second;assert(frames[b].rank>=frames[a].rank);U r=frames[b].rank-frames[a].rank;
  if(!r){for(U z=0;z<h*h;z++)assert((__int128)frames[b].numerator[z]*frames[a].den==(__int128)frames[a].numerator[z]*frames[b].den);continue;}
  if(r==1){blocks[1]+=count;continue;}if(a==0&&b==1){blocks[h]+=count;continue;}
  cpp_int den=cpp_int(frames[a].den/std::gcd(frames[a].den,frames[b].den))*frames[b].den;
  cpp_int af=den/frames[a].den,bf=den/frames[b].den,Z=0;
  for(U z=0;z<h*h;z++){cpp_int entry=bf*frames[b].numerator[z]-af*frames[a].numerator[z];if(entry<0)entry=-entry;if(entry>Z)Z=entry;}
  assert(Z>0);cpp_int bound=ipower(cpp_int(r),(r+1)/2)*ipower(Z,r);largest=std::max(largest,bound);
  largest_entry_bits=std::max(largest_entry_bits,bits(Z));largest_bound_bits=std::max(largest_bound_bits,bits(bound));
  transitions.push_back({a,b,r,0,count,den,Z,bound,std::vector<uint8_t>((h+1)*(h+1)),{}});
 }
 // Distinct primes are proved by trial division, and denominator factors are checked.
 std::vector<U>primes;std::vector<cpp_int>products;cpp_int product=1;
 for(U candidate=2147483647;product<=largest;candidate-=2)if(prime(candidate)){for(auto&F:frames)assert(F.den%candidate);primes.push_back(candidate);product*=candidate;products.push_back(product);}
 std::map<U,V>prime_hist;V field_replays=0;
 for(auto&T:transitions){while(T.primes<products.size()&&products[T.primes]<=T.minor_bound)T.primes++;T.primes++;assert(T.primes<=products.size());prime_hist[T.primes]++;field_replays+=T.primes;}
 std::cerr<<"frames "<<frames.size()<<" matrices "<<transitions.size()<<" primes "<<primes.size()<<" replays "<<field_replays<<" bound_bits "<<largest_bound_bits<<"\n";
 V differing_profiles=0;std::vector<std::vector<U>>matrices(frames.size());
 for(U pi=0;pi<primes.size();pi++){U p=primes[pi];std::vector<uint8_t>needed(frames.size());for(auto&T:transitions)if(pi<T.primes){needed[T.a]=needed[T.b]=1;}
  for(U id=0;id<frames.size();id++){matrices[id].clear();if(!needed[id])continue;auto&F=frames[id];U inv=power(F.den%p,p-2,p);auto&M=matrices[id];M.resize(h*h);
   for(U z=0;z<h*h;z++){I residue=F.numerator[z]%I(p);if(residue<0)residue+=p;M[z]=multiply(residue,inv,p);}}
  V done=0;for(auto&T:transitions)if(pi<T.primes){auto&A=matrices[T.a];auto&B=matrices[T.b];std::vector<U>M(h*h);for(U z=0;z<h*h;z++)M[z]=subtract(B[z],A[z],p);
   std::vector<std::pair<U,U>>pivots;
   for(U i=0;i<h;i++){int j=h-1;while(j>=0&&!M[i*h+j])j--;if(j<0)continue;pivots.emplace_back(i,U(j));U inv=power(M[i*h+j],p-2,p);
    for(U k=i+1;k<h;k++){U scale=multiply(M[k*h+j],inv,p);if(scale)for(U col=0;col<=U(j);col++)M[k*h+col]=subtract(M[k*h+col],multiply(scale,M[i*h+col],p),p);}}
   assert(pivots.size()<=T.r);if(pi==0)T.pivots=pivots;else if(pivots!=T.pivots)differing_profiles++;
   std::vector<uint8_t>corner((h+1)*(h+1));U at=0;
   for(U i=0;i<h;i++){int col=at<pivots.size()&&pivots[at].first==i?int(pivots[at++].second):-1;for(U j=0;j<h;j++)corner[(i+1)*(h+1)+j]=corner[i*(h+1)+j]+(int(j)<=col);}
   for(U z=0;z<corner.size();z++)T.corner[z]=std::max(T.corner[z],corner[z]);
   done++;
  }
  std::cerr<<"prime "<<pi+1<<" / "<<primes.size()<<" matrices "<<done<<" seconds "<<std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()<<"\n";
 }
 V mass=0;U longest=0;
 for(auto&T:transitions){T.pivots.clear();auto&C=T.corner;for(U i=0;i<h;i++)for(U j=0;j<h;j++){int z=C[(i+1)*(h+1)+j]-C[i*(h+1)+j]-C[(i+1)*(h+1)+j+1]+C[i*(h+1)+j+1];assert(z==0||z==1);if(z)T.pivots.emplace_back(i,j);}
  assert(T.pivots.size()==T.r);U run=0;for(U at=0;at<T.pivots.size();at++){if(at&&T.pivots[at].first==T.pivots[at-1].first+1&&T.pivots[at].second==T.pivots[at-1].second+1)run++;else{if(run){blocks[run]+=T.count;longest=std::max(longest,run);}run=1;}}if(run){blocks[run]+=T.count;longest=std::max(longest,run);}}
 for(U t=1;t<=h;t++){assert(blocks[t]>=0);mass+=t*blocks[t];}assert(mass==rank_mass);
 std::ofstream out(argv[4]);assert(out);out<<"{\"status\":\"PASS EXACT SIGNED POSITIVE-FRAME PHYSICAL PROFILES\",\"basis\":\""<<basis<<"\",\"h\":"<<h<<",\"v\":"<<v<<",\"R\":"<<R<<",\"matched\":"<<matches<<",\"loss\":"<<loss<<",\"rank_sum\":"<<mass<<",\"frames\":"<<frames.size()<<",\"distinct_matrices\":"<<transitions.size()<<",\"field_replays\":"<<field_replays<<",\"different_modular_profiles\":"<<differing_profiles<<",\"maximum_entry_bound_bits\":"<<largest_entry_bits<<",\"maximum_minor_bound_bits\":"<<largest_bound_bits<<",\"prime_product_bits\":"<<bits(product)<<",\"longest_block\":"<<longest<<",\"seconds\":"<<std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()<<",\"primes\":[";
 for(U i=0;i<primes.size();i++){if(i)out<<",";out<<primes[i];}out<<"],\"prime_count_histogram\":{";bool first=true;for(auto&[pc,num]:prime_hist){if(!first)out<<",";first=false;out<<"\""<<pc<<"\":"<<num;}out<<"},\"blocks\":[";
 for(U t=0;t<=h;t++){if(t)out<<",";out<<blocks[t];}out<<"],\"rank_histogram\":[";for(U t=0;t<=h;t++){if(t)out<<",";out<<hist[t];}out<<"]}\n";
 if(argc==6){std::ofstream audit(argv[5]);assert(audit);audit<<"{\"h\":"<<h<<",\"basis\":\""<<basis<<"\",\"transitions\":[";first=true;
  for(auto&T:transitions){if(!first)audit<<",";first=false;audit<<"{\"a\":"<<T.a<<",\"b\":"<<T.b<<",\"rank\":"<<T.r<<",\"count\":"<<T.count<<",\"integer_denominator\":\""<<T.denominator<<"\",\"entry_bound\":\""<<T.entry_bound<<"\",\"minor_bound\":\""<<T.minor_bound<<"\",\"prime_count\":"<<T.primes<<",\"pivots\":[";
   for(U k=0;k<T.pivots.size();k++){if(k)audit<<",";audit<<"["<<T.pivots[k].first<<","<<T.pivots[k].second<<"]";}audit<<"]}";}audit<<"]}\n";}
 std::cout<<"h="<<h<<" basis="<<basis<<" R="<<R<<" exact_rank_mass="<<mass<<" matrices="<<transitions.size()<<"\n";
}

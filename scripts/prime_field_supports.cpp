// Exact global support merging and dead-node pruning for the F3 five-set motif.
// Exact producer audit; the rational-frame and tape-transfer proof is separate.
#include <algorithm>
#include <array>
#include <cassert>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <unordered_map>
#include <vector>
#include <set>
#include <map>
using U=uint32_t; using V=uint64_t;
struct Record {U id,a,b,core;std::vector<U> vars;};
struct Key {std::array<V,7> x{}; bool operator==(Key const& y)const{return x==y.x;}};
struct Hash {size_t operator()(Key const& k)const {V h=0x9e3779b97f4a7c15ULL;for(V x:k.x){x^=x>>30;x*=0xbf58476d1ce4e5b9ULL;x^=x>>27;x*=0x94d049bb133111ebULL;x^=x>>31;h^=x+0x9e3779b97f4a7c15ULL+(h<<6)+(h>>2);}return h;}};
U choose(U n,U r){V x=1; if(r>n)return 0;for(U j=1;j<=r;j++)x=x*(n+1-j)/j;return U(x);}
U rank5(U mask){U r=0,j=1;while(mask){U b=__builtin_ctz(mask);mask&=mask-1;r+=choose(b,j++);}assert(j==6);return r+1;}
U read(std::ifstream& f){U x;f.read(reinterpret_cast<char*>(&x),4);assert(f);return x;}
int main(int argc,char** argv){
 assert(argc>=2);auto start=std::chrono::steady_clock::now();
 std::ifstream f(argv[1],std::ios::binary);assert(f);
 U n=read(f),ni=read(f),nn=read(f),na=read(f),no=read(f),h=n+2;assert(h<=28 && h%2==0);assert(ni==choose(n,3));
 std::vector<Record> records;for(U j=0;j<na;j++){Record r; r.id=read(f);r.a=read(f);r.b=read(f);r.core=read(f);U nv=read(f);for(U k=0;k<nv;k++)r.vars.push_back(read(f));records.push_back(std::move(r));}
 std::vector<std::array<U,4>> outputs(no);for(auto& r:outputs)for(auto& x:r)x=read(f);
 U v=choose(h,5);std::vector<std::array<U,2>> args(v+1,{0,0});std::vector<U> cores(v+1),starmasks(v+1);std::vector<U> roots;roots.reserve(10*v);
 std::unordered_map<Key,U,Hash> map3;std::unordered_map<V,U> map4;map3.reserve(6000000);map4.reserve(3500000);
 U pairindex[32][32]{};U ix=0;for(U a=0;a<h;a++)for(U b=a+1;b<h;b++)pairindex[a][b]=pairindex[b][a]=ix++;
 V generic=0;U contexts=0;
 for(U ca=0;ca<h;ca++)for(U cb=ca+1;cb<h;cb++){
  U common=(1U<<ca)|(1U<<cb);std::vector<U> order;
  for(U x=0;x<h;x+=2)if(!(common&(3U<<x))){order.push_back(x);order.push_back(x+1);}
  for(U x=0;x<h;x++)if(!(common&(1U<<x))&&(common&(1U<<(x^1))))order.push_back(x);
  assert(order.size()==n);std::vector<U> ids(nn);
  for(auto const& r:records){
   U core=common,m=r.core;while(m){U i=__builtin_ctz(m);m&=m-1;core|=1U<<order[i];}
   if(!r.a){ids[r.id]=rank5(core);cores[ids[r.id]]=core;continue;}
   U a=ids[r.a],b=ids[r.b];assert(a&&b);U id=0;int nc=__builtin_popcount(core);
   if(nc==2){id=args.size();args.push_back({a,b});generic++;}
   else if(nc==3){Key key;key.x[0]=core;for(U edge:r.vars){U i=pairindex[order[edge/32]][order[edge%32]];key.x[1+i/64]|=V(1)<<(i%64);}auto [it,inserted]=map3.emplace(key,args.size());id=it->second;if(inserted)args.push_back({a,b});}
   else {assert(nc==4);U mask=0;for(U i:r.vars)mask|=1U<<order[i];V key=(V(core)<<32)|mask;auto [it,inserted]=map4.emplace(key,args.size());id=it->second;if(inserted)args.push_back({a,b});}
   if(cores.size()<args.size()){
    U mask=0;if(nc==4)for(U i:r.vars)mask|=1U<<order[i];
    cores.push_back(core);starmasks.push_back(mask);
   }
   assert(cores.size()==args.size());assert(id<args.size());ids[r.id]=id;
  }
  for(auto const& o:outputs){U id=ids[o[3]];assert(id);roots.push_back(id);}
  if(++contexts%50==0)std::cerr<<"contexts "<<contexts<<", unique additions "<<args.size()-v-1<<"\n";
 }
 assert(roots.size()==10*v || roots.size()==10*v+choose(h,2));
 V total=args.size()-v-1;map3.clear();map3.rehash(0);map4.clear();map4.rehash(0);
 std::vector<uint8_t> active(args.size());std::vector<U> stack(roots);V activecount=0,inputs=0;
 while(!stack.empty()){U x=stack.back();stack.pop_back();if(active[x])continue;active[x]=1;if(args[x][0]){assert(args[x][0]<x&&args[x][1]<x);activecount++;stack.push_back(args[x][0]);stack.push_back(args[x][1]);}else inputs++;}
 assert(inputs==v);double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
 std::cout<<"{\"h\":"<<h<<",\"local_inputs\":"<<ni<<",\"unique_additions\":"<<total<<",\"pruned_additions\":"<<activecount<<",\"removed_after_merging\":"<<total-activecount<<",\"outputs\":"<<roots.size()<<",\"roles\":"<<activecount+roots.size()<<",\"seconds\":"<<seconds<<",\"exact_support_keys\":true,\"topological_order_checked\":true,\"all_inputs_active\":true}"<<std::endl;
 if(argc>=4){
  std::unordered_map<U,std::vector<U>> demand;std::unordered_map<U,U> sizes;
  std::vector<uint8_t> needed(args.size());
  for(U x=1;x<args.size();x++)if(active[x]&&args[x][0]){
   int nc=__builtin_popcount(cores[x]);if(nc==4)sizes[cores[x]]++;
   for(U a:args[x])if(__builtin_popcount(cores[a])==4 && cores[a]!=cores[x])needed[a]=1;
  }
  for(U x:roots)if(__builtin_popcount(cores[x])==4)needed[x]=1;
  for(U x=1;x<args.size();x++)if(needed[x])demand[cores[x]].push_back(starmasks[x]);
  std::vector<U> keys;for(auto& [key,masks]:demand)keys.push_back(key);std::sort(keys.begin(),keys.end());
  if(argc>=5){
   std::ifstream tf(argv[4],std::ios::binary);assert(read(tf)==h);U nt=read(tf);
   std::map<std::vector<U>,U> templates;
   for(U t=0;t<nt;t++){
    U nout=read(tf),ng=read(tf);std::vector<U> target(nout);for(U& x:target)x=read(tf);
    std::set<U> computed;for(U i=0;i<h-4;i++)computed.insert(1U<<i);
    for(U j=0;j<ng;j++){U a=read(tf),b=read(tf);assert(a&&b&&!(a&b));assert(computed.count(a)&&computed.count(b));assert(computed.insert(a|b).second);}
    for(U x:target)assert(computed.count(x));assert(templates.emplace(target,ng).second);
   }
   V oldstars=0,newstars=0;
   for(U key:keys){
    std::vector<U> order;
    for(U x=0;x<h;x++)if(!(key&(1U<<x))&&!(key&(1U<<(x^1))))order.push_back(x);
    for(U x=0;x<h;x++)if(!(key&(1U<<x))&&(key&(1U<<(x^1))))order.push_back(x);
    assert(order.size()==h-4);std::vector<U> target;
    for(U mask:demand[key]){U z=0;assert(!(mask&key));for(U j=0;j<order.size();j++)if(mask&(1U<<order[j]))z|=1U<<j;target.push_back(z);}
    std::sort(target.begin(),target.end());target.erase(std::unique(target.begin(),target.end()),target.end());
    auto it=templates.find(target);assert(it!=templates.end());oldstars+=sizes[key];newstars+=it->second;
   }
   std::cout<<"{\"optimized_stars\":"<<keys.size()<<",\"verified_templates\":"<<nt<<",\"old_star_additions\":"<<oldstars<<",\"new_star_additions\":"<<newstars<<",\"optimized_additions\":"<<activecount-oldstars+newstars<<",\"role_upper_bound\":"<<activecount-oldstars+newstars+roots.size()<<",\"every_boundary_sum_verified\":true,\"every_template_addition_disjoint\":true}"<<std::endl;
  }
  std::ofstream out(argv[3]);
  for(U key:keys){auto& masks=demand[key];std::sort(masks.begin(),masks.end());masks.erase(std::unique(masks.begin(),masks.end()),masks.end());out<<key<<" "<<sizes[key];for(U x:masks)out<<" "<<x;out<<"\n";}
 }
 if(argc>=3 && std::string(argv[2])!="-"){std::ofstream out(argv[2],std::ios::binary);U size=args.size(),nr=roots.size();out.write(reinterpret_cast<char*>(&v),4);out.write(reinterpret_cast<char*>(&size),4);out.write(reinterpret_cast<char*>(&nr),4);out.write(reinterpret_cast<char*>(args.data()),args.size()*8);out.write(reinterpret_cast<char*>(roots.data()),roots.size()*4);out.write(reinterpret_cast<char*>(active.data()),active.size());assert(out);}
}

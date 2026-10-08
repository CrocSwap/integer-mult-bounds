// Exploratory only: 256-bit fingerprints are NOT exact support certificates.
#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <unordered_map>
#include <utility>
#include <vector>

using U=uint32_t;
using Key=std::array<uint64_t,4>;
uint64_t splitmix(uint64_t x) {
  x+=0x9e3779b97f4a7c15ULL;x=(x^(x>>30))*0xbf58476d1ce4e5b9ULL;
  x=(x^(x>>27))*0x94d049bb133111ebULL;return x^(x>>31);
}
struct Hash {size_t operator()(const Key&k)const{return splitmix(k[0]^k[1]^k[2]^k[3]);}};
U read(std::ifstream& f){U x;f.read(reinterpret_cast<char*>(&x),4);if(!f)throw std::runtime_error("Short plan");return x;}
std::vector<U> reads(std::ifstream& f,size_t n){std::vector<U> x(n);f.read(reinterpret_cast<char*>(x.data()),4*n);if(!f)throw std::runtime_error("Short vector");return x;}
struct Template {U ni;std::vector<std::pair<U,U>> gates;std::vector<U> outputs;};
#ifdef TERNARY_EXACT_SUPPORT
struct ZKey {U var,lo,hi;bool operator==(const ZKey&o)const{return var==o.var&&lo==o.lo&&hi==o.hi;}};
struct ZHash {size_t operator()(const ZKey&x)const{return splitmix((uint64_t(x.lo)<<32)|x.hi)^splitmix(x.var);}};
struct ZNode {U var,lo,hi,count,core;};
struct ZDD {
  U h;std::vector<ZNode> nodes;
  std::unordered_map<ZKey,U,ZHash> unique;
  std::unordered_map<uint64_t,U> unions;
  explicit ZDD(U ground):h(ground){nodes.push_back({h,0,0,0,0});nodes.push_back({h,0,0,1,0});}
  U make(U var,U lo,U hi){
    if(!hi)return lo;ZKey key{var,lo,hi};auto found=unique.find(key);if(found!=unique.end())return found->second;
    U id=nodes.size();U core=lo?(nodes[lo].core&nodes[hi].core):(nodes[hi].core|(U(1)<<var));
    nodes.push_back({var,lo,hi,nodes[lo].count+nodes[hi].count,core});unique.emplace(key,id);return id;
  }
  U unite(U a,U b){
    if(!a)return b;if(!b||a==b)return a;if(a>b)std::swap(a,b);
    uint64_t key=(uint64_t(a)<<32)|b;auto found=unions.find(key);if(found!=unions.end())return found->second;
    ZNode x=nodes[a],y=nodes[b];U result;
    if(x.var==y.var)result=make(x.var,unite(x.lo,y.lo),unite(x.hi,y.hi));
    else if(x.var<y.var)result=make(x.var,unite(x.lo,b),x.hi);
    else result=make(y.var,unite(a,y.lo),y.hi);
    if(unions.size()>=4000000)unions.clear();unions.emplace(key,result);return result;
  }
  U singleton(U mask){U root=1;for(U i=h;i>0;i--)if(mask&(U(1)<<(i-1)))root=make(i-1,0,root);return root;}
  U intersection_family(U target,U wanted){
    std::vector<U> memo((h+1)*6*6,UINT32_MAX);
    std::function<U(U,int,int)> visit=[&](U var,int k,int j)->U{
      if(k<0||j<0||j>k||int(h-var)<k)return 0;
      if(!k)return j?0:1;
      if(var==h)return 0;
      U index=(var*6+U(k))*6+U(j);if(memo[index]!=UINT32_MAX)return memo[index];
      U lo=visit(var+1,k,j),hi=visit(var+1,k-1,j-int((target>>var)&1));
      return memo[index]=make(var,lo,hi);
    };
    return visit(0,5,wanted);
  }
};
struct Circuit {
  U inputs;ZDD families;
  std::vector<U> keys;
  std::vector<std::pair<U,U>> parents;
  std::unordered_map<U,U> lookup;
  explicit Circuit(U n,U h):inputs(n),families(h){
    keys.push_back(0);parents.emplace_back(0,0);lookup.emplace(0,0);
    for(U a=0;a<h;a++)for(U b=a+1;b<h;b++)for(U d=b+1;d<h;d++)for(U e=d+1;e<h;e++)for(U f=e+1;f<h;f++){
      U key=families.singleton((U(1)<<a)|(U(1)<<b)|(U(1)<<d)|(U(1)<<e)|(U(1)<<f));
      U id=keys.size();keys.push_back(key);parents.emplace_back(0,0);lookup.emplace(key,id);
    }
    if(keys.size()!=n+1)throw std::runtime_error("Bad source enumeration");
  }
  U add(U a,U b){
    if(!a)return b;if(!b)return a;
    U key=families.unite(keys[a],keys[b]);
    if(families.nodes[key].count!=families.nodes[keys[a]].count+families.nodes[keys[b]].count)
      throw std::runtime_error("Overlapping source supports");
    auto found=lookup.find(key);if(found!=lookup.end())return found->second;
    U id=keys.size();keys.push_back(key);parents.emplace_back(a,b);lookup.emplace(key,id);return id;
  }
#else
struct Circuit {
  U inputs;
  std::vector<Key> keys;
  std::vector<std::pair<U,U>> parents;
  std::unordered_map<Key,U,Hash> lookup;
  explicit Circuit(U n,U h):inputs(n){
    keys.push_back({0,0,0,0});parents.emplace_back(0,0);lookup.emplace(keys[0],0);
    for(U i=1;i<=n;i++){
      Key key;for(U j=0;j<4;j++)key[j]=splitmix(uint64_t(i)+uint64_t(j+1)*0xd6e8feb86659fd93ULL);
      keys.push_back(key);parents.emplace_back(0,0);lookup.emplace(key,i);
    }
  }
  U add(U a,U b){
    if(!a)return b;if(!b)return a;
    Key key;for(U j=0;j<4;j++)key[j]=keys[a][j]+keys[b][j];
    auto found=lookup.find(key);if(found!=lookup.end())return found->second;
    U id=keys.size();keys.push_back(key);parents.emplace_back(a,b);lookup.emplace(key,id);return id;
  }
#endif
  U total(const std::vector<U>& xs,size_t begin,size_t end){
    if(begin==end)return 0;if(end-begin==1)return xs[begin];size_t middle=(begin+end)/2;
    return add(total(xs,begin,middle),total(xs,middle,end));
  }
  std::vector<U> apply(const Template&t,const std::vector<U>& inputs){
    if(inputs.size()!=t.ni)throw std::runtime_error("Input width mismatch");
    std::vector<U> map(1,0);map.insert(map.end(),inputs.begin(),inputs.end());
    map.reserve(t.ni+t.gates.size()+1);
    for(auto [a,b]:t.gates)map.push_back(add(map[a],map[b]));
    std::vector<U> out;out.reserve(t.outputs.size());for(U n:t.outputs)out.push_back(map[n]);return out;
  }
};
#ifndef TERNARY_NO_MAIN
int main(int argc,char**argv){
  if(argc!=2&&argc!=3)return 2;
  auto start=std::chrono::steady_clock::now();std::ifstream f(argv[1],std::ios::binary);
  U h=read(f),v=read(f),nt=read(f),ns=read(f);std::vector<Template> templates;
  for(U k=0;k<nt;k++){
    auto key=reads(f,4);Template t;t.ni=read(f);U ng=read(f),no=read(f);
    for(U j=0;j<ng;j++){U a=read(f),b=read(f);t.gates.emplace_back(a,b);}
    t.outputs=reads(f,no);templates.push_back(std::move(t));
  }
  Circuit c(v,h);uint64_t outputs=0;std::vector<U> roots;
  for(U stage=0;stage<ns;stage++){
    U no=read(f),nc=read(f);outputs+=no;std::vector<std::vector<U>> pieces(no);
    for(U step=0;step<nc;step++){
      U lt=read(f),rt=read(f),il=read(f),ir=read(f),tl=read(f),tr=read(f),left_first=read(f);
      auto source=reads(f,size_t(il)*ir),target=reads(f,size_t(tl)*tr);
      std::vector<U> result(size_t(tl)*tr);
      if(left_first){
        std::vector<U> temp(size_t(tl)*ir),in(il);
        for(U j=0;j<ir;j++){
          for(U i=0;i<il;i++)in[i]=source[size_t(i)*ir+j];
          auto out=c.apply(templates[lt],in);if(out.size()!=tl)throw std::runtime_error("Left width");
          for(U i=0;i<tl;i++)temp[size_t(i)*ir+j]=out[i];
        }
        in.resize(ir);
        for(U i=0;i<tl;i++){
          for(U j=0;j<ir;j++)in[j]=temp[size_t(i)*ir+j];
          auto out=c.apply(templates[rt],in);if(out.size()!=tr)throw std::runtime_error("Right width");
          for(U j=0;j<tr;j++)result[size_t(i)*tr+j]=out[j];
        }
      }else{
        std::vector<U> temp(size_t(il)*tr),in(ir);
        for(U i=0;i<il;i++){
          for(U j=0;j<ir;j++)in[j]=source[size_t(i)*ir+j];
          auto out=c.apply(templates[rt],in);if(out.size()!=tr)throw std::runtime_error("Right width");
          for(U j=0;j<tr;j++)temp[size_t(i)*tr+j]=out[j];
        }
        in.resize(il);
        for(U j=0;j<tr;j++){
          for(U i=0;i<il;i++)in[i]=temp[size_t(i)*tr+j];
          auto out=c.apply(templates[lt],in);if(out.size()!=tl)throw std::runtime_error("Left width");
          for(U i=0;i<tl;i++)result[size_t(i)*tr+j]=out[i];
        }
      }
      for(size_t i=0;i<target.size();i++)pieces[target[i]].push_back(result[i]);
      if(step%10==0)std::cerr<<"stage "<<stage<<" case "<<step<<"/"<<nc<<" nodes "<<c.keys.size()<<'\n';
    }
    for(const auto&values:pieces)roots.push_back(c.total(values,0,values.size()));
    std::cerr<<"stage "<<stage<<" finished; nodes "<<c.keys.size()<<'\n';
  }
  uint64_t additions=c.keys.size()-v-1;
#ifdef TERNARY_EXACT_SUPPORT
  U checked=0;
  for(U a=0;a<h;a++)for(U b=a+1;b<h;b++)for(U d=b+1;d<h;d++)for(U e=d+1;e<h;e++)for(U f=e+1;f<h;f++){
    U mask=(U(1)<<a)|(U(1)<<b)|(U(1)<<d)|(U(1)<<e)|(U(1)<<f);
    if(c.keys[roots[checked++]]!=c.families.intersection_family(mask,2))throw std::runtime_error("Wrong full side coefficient family");
  }
  for(U a=0;a<h;a++)for(U b=a+1;b<h;b++){
    U mask=(U(1)<<a)|(U(1)<<b);
    if(c.keys[roots[checked++]]!=c.families.intersection_family(mask,2))throw std::runtime_error("Wrong pair-total coefficient family");
  }
  if(checked!=roots.size())throw std::runtime_error("Output count mismatch");
#endif
  std::vector<uint8_t> active(c.keys.size(),0);std::vector<U> pending=roots;uint64_t retained=0;
  while(!pending.empty()){
    U node=pending.back();pending.pop_back();if(!node||active[node])continue;active[node]=1;
    if(node>v){retained++;auto [a,b]=c.parents[node];pending.push_back(a);pending.push_back(b);}
  }
  if(argc==3){
    std::ofstream dump(argv[2],std::ios::binary);U n=c.keys.size(),q=roots.size();
    for(U word:{h,v,n,q})dump.write(reinterpret_cast<char*>(&word),4);
    dump.write(reinterpret_cast<char*>(c.parents.data()),8*c.parents.size());
    dump.write(reinterpret_cast<char*>(roots.data()),4*roots.size());
    dump.write(reinterpret_cast<char*>(active.data()),active.size());
#ifdef TERNARY_EXACT_SUPPORT
    for(U key:c.keys){U core=c.families.nodes[key].core;dump.write(reinterpret_cast<char*>(&core),4);}
#endif
  }
  double elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
#ifdef TERNARY_EXACT_SUPPORT
  std::cout<<"{\"status\":\"EXACT ZDD SUPPORT COUNT; FRAME AUDIT STILL REQUIRED\",\"h\":"<<h
           <<",\"inputs\":"<<v<<",\"unpruned_additions\":"<<additions<<",\"outputs\":"<<outputs
           <<",\"retained_additions\":"<<retained<<",\"roles\":"<<retained+outputs
           <<",\"every_output_family_independently_checked\":true"
           <<",\"zdd_nodes\":"<<c.families.nodes.size()<<",\"seconds\":"<<elapsed<<"}\n";
#else
  std::cout<<"{\"status\":\"FINGERPRINT SCREEN ONLY; NOT EXACT SUPPORT CERTIFICATE\",\"h\":"<<h
           <<",\"inputs\":"<<v<<",\"unpruned_additions\":"<<additions<<",\"outputs\":"<<outputs
           <<",\"retained_additions_if_no_collision\":"<<retained
           <<",\"roles_if_no_collision\":"<<retained+outputs<<",\"seconds\":"<<elapsed<<"}\n";
#endif
}
#endif

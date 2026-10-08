// Independently re-evaluate a saved five-set producer after local rewrites.
#define TERNARY_EXACT_SUPPORT
#define TERNARY_NO_MAIN
#include "ternary_target_fingerprint.cpp"
int main(int argc,char**argv){
  if(argc!=2)return 2;
  std::ifstream f(argv[1],std::ios::binary);
  U h=read(f),v=read(f),n=read(f),q=read(f);
  if(h<8||h>28||n<=v)throw std::runtime_error("Unsupported DAG dimensions");
  std::vector<std::pair<U,U>> parents(n);f.read(reinterpret_cast<char*>(parents.data()),8*n);
  auto roots=reads(f,q);std::vector<uint8_t> active(n);f.read(reinterpret_cast<char*>(active.data()),n);
  auto cores=reads(f,n);ZDD families(h);std::vector<U> keys(n);U input=0;
  for(U a=0;a<h;a++)for(U b=a+1;b<h;b++)for(U c=b+1;c<h;c++)for(U d=c+1;d<h;d++)for(U e=d+1;e<h;e++){
    U mask=(1U<<a)|(1U<<b)|(1U<<c)|(1U<<d)|(1U<<e);
    if(++input>v||cores[input]!=mask||!active[input])throw std::runtime_error("Incorrect input enumeration");
    keys[input]=families.singleton(mask);
  }
  if(input!=v)throw std::runtime_error("Incorrect input count");
  uint64_t additions=0;
  for(U node=v+1;node<n;node++)if(active[node]){
    auto [a,b]=parents[node];
    if(!a||!b||a>=node||b>=node||!active[a]||!active[b])throw std::runtime_error("Invalid active DAG");
    U key=families.unite(keys[a],keys[b]);
    if(families.nodes[key].count!=families.nodes[keys[a]].count+families.nodes[keys[b]].count)
      throw std::runtime_error("Overlapping source supports");
    if(families.nodes[key].core!=cores[node])throw std::runtime_error("Incorrect source core");
    keys[node]=key;additions++;
  }
  U checked=0;
  auto check=[&](U mask){
    if(checked>=q)throw std::runtime_error("Missing output");
    U node=roots[checked++];
    if(node>=n||!active[node]||keys[node]!=families.intersection_family(mask,2))
      throw std::runtime_error("Incorrect output coefficient family");
  };
  for(U a=0;a<h;a++)for(U b=a+1;b<h;b++)for(U c=b+1;c<h;c++)for(U d=c+1;d<h;d++)for(U e=d+1;e<h;e++)
    check((1U<<a)|(1U<<b)|(1U<<c)|(1U<<d)|(1U<<e));
  for(U a=0;a<h;a++)for(U b=a+1;b<h;b++)check((1U<<a)|(1U<<b));
  if(checked!=q)throw std::runtime_error("Extra output");
  std::cout<<"{\"h\":"<<h<<",\"inputs\":"<<v<<",\"outputs\":"<<q
    <<",\"retained_additions\":"<<additions<<",\"roles\":"<<additions+q
    <<",\"every_addition_disjoint\":true,\"every_source_core_checked\":true"
    <<",\"every_output_family_independently_checked\":true,\"zdd_nodes\":"<<families.nodes.size()<<"}\n";
}

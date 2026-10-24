#define main original_discovery_main
#include "dynamic_neighbors.cpp"
#undef main
int main(int argc,char** argv){
 if(argc!=3)return 2;std::ifstream in(argv[1]);int n,k;unsigned long long count=0,zero=0;
 while(in>>n>>k){std::vector<V> lags(k,V(9));for(auto& l:lags)for(auto& x:l)in>>x;
  for(auto u:lags)for(auto v:lags){V both=u;both.insert(both.end(),v.begin(),v.end());int before=basis(both).size()-9;auto loc=make_local(u,v,before,1);auto own=ann(u);
   for(unsigned a=1;a<(1u<<(2*n));a++){unsigned axis=(a&((1u<<n)-1))|((a>>n)<<9);if(contains(own,axis)){zero++;continue;}
    int predicted=change(loc,axis);auto changed=u;turn(changed,axis);changed.insert(changed.end(),v.begin(),v.end());int actual=(int)basis(changed).size()-9-before;
    if(predicted!=actual){std::cerr<<"CODE FORMULA MISMATCH";return 4;}count++;
   }
  }
 }
 std::ifstream g(argv[2]);int nodes,frames,maps,edges;g>>nodes>>frames>>maps>>edges;int discard;for(int i=0;i<2*nodes+9*frames;i++)g>>discard;
 for(int j=0;j<maps;j++){V cols(18);for(auto& x:cols)g>>x;auto inverted=inverse(cols);for(int i=0;i<18;i++)if(mv(cols,inverted[i])!=(1u<<i)||mv(inverted,cols[i])!=(1u<<i)){std::cerr<<"CODE INVERSE MISMATCH";return 5;}}
 std::cout<<"PASS_ROOT_CPP_CROSS_REVIEW nonfixed_axis_cases="<<count<<" fixed_axis_controls="<<zero<<" inverse_maps="<<maps<<"\n";
}

#include <omp.h>
#include <iostream>
int main(){int count=0;
#pragma omp parallel reduction(+:count)
{count+=1;}
std::cout<<count<<" OpenMP workers\n";return count==4?0:1;}

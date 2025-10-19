#include <iostream>
#include <omp.h>

int main(int argc, char** argv) {

    #ifdef _OPENMP
    std::cout << "OpenMP is supported! Version: "
        << _OPENMP
        << std::endl;
    #else
    std::cout << "OpenMP is not supported!"
        << std::endl;

    #endif

    system("pause");

    return 0;
}
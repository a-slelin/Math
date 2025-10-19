#include <iostream>
#include <omp.h>

int main(int argc, char** argv) {

    omp_set_num_threads(4);

    #pragma omp parallel
    {
        std::cout << "Hello, World!\n";
    }

    system("pause");

    return 0;
}
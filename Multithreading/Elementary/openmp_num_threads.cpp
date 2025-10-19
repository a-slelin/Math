#include <iostream>
#include <omp.h>

int main(int argc, char** argv) {

    #pragma omp parallel
	{
	    std::cout << "Parallel region 1\n";
	}

    omp_set_num_threads(2);

    #pragma omp parallel num_threads(3)
	{
		std::cout << "Parallel region 2\n";
	}

    #pragma omp parallel
	{
		std::cout << "Parallel region 3\n";
	}

	system("pause");

	return 0;
}
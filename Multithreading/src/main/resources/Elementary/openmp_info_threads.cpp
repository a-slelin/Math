#include <iostream>
#include <omp.h>

int main(int argc, char** argv) {

    #pragma omp parallel
	{
		int rank = omp_get_thread_num();
		int size = omp_get_num_threads();

		printf("Thread %d out of %d\n", rank, size);
	}

	system("pause");

	return 0;
}
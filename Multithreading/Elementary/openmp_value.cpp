#include <iostream>
#include <omp.h>

int main(int argc, char** argv) {

	int a_shared = 5;

    #pragma omp parallel
	{
		int rank = omp_get_thread_num();

		printf("Thread %d sees a_shared = %d\n", rank, a_shared);

		a_shared = 5 * rank;
	}

	system("pause");

	return 0;
}
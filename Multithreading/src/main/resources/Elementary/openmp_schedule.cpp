#include <iostream>
#include <omp.h>

int main(int argc, char** argv) {

	const int N = INT_MAX / 10;

	double* a = new double[N];
	double* b = new double[N];
	double* c = new double[N];

    #pragma omp for schedule(auto)
	for (int i = 0; i < N; ++i) {
		a[i] = i;
	}

	double static_time = omp_get_wtime();

    #pragma omp parallel
	{
        #pragma omp for schedule(static, 20)
		for (int i = 0; i < N; ++i) {
			b[i] = a[i] * a[i];
		}
	}

	std::cout << "Static time: "
		<< (omp_get_wtime() - static_time)
		<< std::endl;

	double dynamic_time = omp_get_wtime();

    #pragma omp parallel
	{
        #pragma omp for schedule(dynamic, 20)
		for (int i = 0; i < N; ++i) {
			c[i] = a[i] * a[i];
		}
	}

	std::cout << "Dynamic time: "
		<< (omp_get_wtime() - dynamic_time)
		<< std::endl;

	system("pause");

	return 0;
}
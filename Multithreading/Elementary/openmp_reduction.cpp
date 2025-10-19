#include <iostream>
#include <omp.h>

int main(int argc, char** argv) {

	int count = 0;

    #pragma omp parallel reduction(+:count)
	{
		++count;
	}

	std::cout << count << std::endl;

	system("pause");

	return 0;
}
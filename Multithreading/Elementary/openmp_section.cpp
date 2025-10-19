#include <iostream>
#include <omp.h>

void func1() {
	std::cout << "A\n";
}

void func2() {
	std::cout << "B\n";
}

int main(int argc, char** argv) {

    #pragma omp parallel sections 
	{

        #pragma omp section
		func1();

        #pragma omp section 
		func2();

	}
	
	system("pause");

	return 0;
}
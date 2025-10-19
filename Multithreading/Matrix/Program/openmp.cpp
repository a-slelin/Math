#include "general.h"
#include <vector>
#include <omp.h>
#include <chrono>
#include <iostream>

int main(int argc, char** argv) {

    // Засекаем время выполнения
    auto startProgram = std::chrono::high_resolution_clock::now();

	std::vector<std::vector<int>> c(N + 1, std::vector<int>(N + 1, 0));

    // Распаралеливаем подсчёт по строкам
    #pragma omp parallel for
    for (int row = 1; row <= N; ++row) {
        for (int i = 1; i <= N; ++i) {
            int sum = 0;
            for (int j = 1; j <= N; ++j) {
                sum += a(row, j) * b(j, i);
            }
            c[row][i] = sum;
        }
    }
	
    // Записываем матрицу в файл
    print_matrix(openmp_file_name, c);

    // Останавливаем время выполнения
    auto endProgram = std::chrono::high_resolution_clock::now();

    // Подсчитываем время выполнения
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(endProgram - startProgram)

    // Записываем время в файл
    print_time(openmp_time_file_name, duration.count());

	return 0;
}
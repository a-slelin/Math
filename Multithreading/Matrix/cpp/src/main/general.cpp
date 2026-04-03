#include "general.h"
#include <fstream>
#include <cmath>
#include <vector>

const int N = 1000;

const std::string single_file_name = "single_matrix.txt";

const std::string mpi_file_name = "mpi_matrix.txt";

const std::string openmp_file_name = "openmp_matrix.txt";

const std::string single_time_file_name = "single_time.txt";

const std::string mpi_time_file_name = "mpi_time.txt";

const std::string openmp_time_file_name = "openmp_time.txt";

// Подсчёт элемента в матрице A с индексами i и j
int a(int i, int j)
{
    return pow(2 * i + 1, 2) + pow(2 * j + 1, 2);
}

// Подсчёт элемента в матрице B с индексами i и j
int b(int i, int j)
{
    return -i * j;
}

// Запись матрицы в файл
void print_matrix(std::string file_name, std::vector<std::vector<int>> matrix)
{
    std::ofstream file(file_name);

    for (int i = 1; i <= N; i++) {
        for (int j = 1; j <= N; j++) {
            file << matrix[i][j];
            if (j < N) file << " ";
        }
        file << std::endl;
    }

    file.close();
}

// Запись времени в файл
void print_time(std::string file_name, long long time) {

    std::ofstream file(file_name);

    file << time << " microseconds." << std::endl;

    file.close();
}
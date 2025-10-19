#include <string>
#include <vector>

// Размер матрицы
extern const int N;

// Имена файлов для вывода
extern const std::string single_file_name;
extern const std::string mpi_file_name;
extern const std::string openmp_file_name;
extern const std::string single_time_file_name;
extern const std::string mpi_time_file_name;
extern const std::string openmp_time_file_name;

// Функции для вычисления элементов матриц
int a(int i, int j);
int b(int i, int j);

// Функция для записи матрицы в файл
void print_matrix(std::string file_name, std::vector<std::vector<int>> matrix);

// Функция для записи времени в файл
void print_time(std::string file_name, long long time);

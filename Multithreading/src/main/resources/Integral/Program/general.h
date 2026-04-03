#define _CRT_SECURE_NO_WARNINGS
#define _USE_MATH_DEFINES
#include<string>

// Выбор задачи
enum TASK {
    A_SQUARE,
    A_TRAPEZIOD,
    A_SIMPSON,
    B_SQUARE,
    B_TRAPEZIOD,
    B_SIMPSON,
    C_SQUARE,
    C_TRAPEZIOD,
    C_SIMPSON,
    D_SQUARE,
    D_TRAPEZIOD,
    D_SIMPSON
};

// Текущая задача
extern const TASK current_task;

// Выходные файлы
extern const std::string single_file_name;
extern const std::string single_time_file_name;
extern const std::string openmp_file_name;
extern const std::string openmp_time_file_name;
extern const std::string mpi_file_name;
extern const std::string mpi_time_file_name;

// Параметры численного интегрирования
extern const double eps;
extern const long long startN;
extern const long long max_iteration;

// Границы интегрирования
extern const double a_start;
extern const double a_finish;
extern const double b_start;
extern const double b_finish;
extern const double c_start;
extern const double c_finish;
extern const double d_start;
extern const double d_finish;

// Функции под интегралами
double a_fun(double x);
double b_fun(double x);
double c_fun(double x);
double d_fun(double x);

// Функции записи данных в файл 
void print_time(std::string file_name, long long time);
void print_integral(std::string file_name, double result);


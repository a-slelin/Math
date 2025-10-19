#include "general.h"
#define _CRT_SECURE_NO_WARNINGS
#define _USE_MATH_DEFINES
#include <cmath>
#include <fstream>
#include <cstdlib>

// Интеграл под буквой а)

const double a_start = 0;

const double a_finish = 1;

double a_fun(double x) 
{
	return exp(x) * sin(x);
}

// Интеграл под буквой b)

const double b_start = M_PI / 4;

const double b_finish = 3 * M_PI / 4;

double b_fun(double x) 
{
	return cos(pow(x, 0.5)) / pow(x, 0.5);
}

// Интеграл под буквой c)

const double c_start = 0.1;

const double c_finish = 0.3;

double c_fun(double x) 
{
	return x * log((1 + x) / (1 - x));
}

// Интеграл под буквой d)

const double d_start = M_PI;

const double d_finish = 3 * M_PI;

double d_fun(double x)
{
	return (x * cos(x)) / (pow(sin(x), 3) + 2);
}

// Параметры численного интегрирования

const double eps = pow(10, -6);

const long long startN = 100;

const long long max_iteration = 100000000000;

// Выходные файлы

const std::string single_file_name = "single_integral.txt";

const std::string single_time_file_name = "single_time.txt";

const std::string openmp_file_name = "openmp_integral.txt";

const std::string openmp_time_file_name = "openmp_time.txt";

const std::string mpi_file_name = "mpi_integral.txt";

const std::string mpi_time_file_name = "mpi_time.txt";

// Функции записи данных в файл

const int precision = 15;

void print_time(std::string file_name, long long time)
{
	std::ofstream file(file_name);
	file << time << " microseconds." << std::endl;
	file.close();
}

void print_integral(std::string file_name, double result)
{
	std::ofstream file(file_name);

	file.precision(precision);
	file << result << std::endl;

	file.close();
}

// Определение текущей задачи

TASK get_task_from_env() {
	char* buffer = nullptr;
	size_t size = 0;

	if (_dupenv_s(&buffer, &size, "INTEGRAL_TASK") == 0 && buffer != nullptr) {
		try {
			int task_num = std::stoi(buffer);
			if (task_num >= 0 && task_num <= 11) {
				free(buffer);
				return static_cast<TASK>(task_num);
			}
		}
		catch (...) {
			// Игнорируем ошибки преобразования
		}
		free(buffer);
	}
	return A_SQUARE;
}

const TASK current_task = get_task_from_env();
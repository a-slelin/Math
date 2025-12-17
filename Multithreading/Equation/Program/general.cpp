#include "general.h"
#define _CRT_SECURE_NO_WARNINGS
#define _USE_MATH_DEFINES
#include <cmath>
#include <fstream>
#include <vector>
#include <cstdlib>

// Переменные для уравнения теплопроводности

const double alpha = 1.0;

const double L = 1.0;

int get_n_from_env() {
	char* buffer = nullptr;
	size_t size = 0;

	if (_dupenv_s(&buffer, &size, "THERMAL_CONDUCTIVITY_N") == 0 && buffer != nullptr) {
		try {
			int n = std::stoi(buffer);
			free(buffer);
			if (n <= 1)
			{
				exit(1);
			}
			return n;
		}
		catch (...) {
			free(buffer);
		}
	}
	return 1000;
}

const int N = get_n_from_env();

const double h = L / (N - 1);

double get_t_from_env() {
	char* buffer = nullptr;
	size_t size = 0;

	if (_dupenv_s(&buffer, &size, "THERMAL_CONDUCTIVITY_T") == 0 && buffer != nullptr) {
		try {
			double t = std::stod(buffer);
			free(buffer);
			if (t <= pow(10, -12))
			{
				exit(1);
			}
			return t;
		}
		catch (...) {
			free(buffer);
		}
	}
	return 1.0;
}

const double T = get_t_from_env();

int compute_m()
{
	int M = 100;
	double tau = T / (double)M;
	while (tau > (h * h) / 2)
	{
		M *= 2;
		tau = T / M;
	}

	return M;
}

const int M = compute_m();

const double tau = T / M;

double f(double x, double t)
{
	return -M_PI * M_PI * cos(M_PI * x);
}

double phi(double x)
{
	return cos(M_PI * x);
}

double expected_u(double x, double t)
{
	return (2 * exp(-M_PI * M_PI * t) - 1) * cos(M_PI * x);
}

// Переменные для записи в файл

const std::string single_filename = "single_value.txt";

const std::string single_time_filename = "single_time.txt";

const std::string openmp_filename = "openmp_value.txt";

const std::string openmp_time_filename = "openmp_time.txt";

const std::string mpi_filename = "mpi_value.txt";

const std::string mpi_time_filename = "mpi_time.txt";

const int precision = 15;

const bool debug = false;

void print_value(std::string filename, std::vector<double> value) 
{
	std::ofstream file(filename);
	file.precision(precision);
	for (int i = 0; i < value.size(); ++i) {
		if (debug)
		{
			file << i * h << "\t" << value[i] << "\t" << expected_u(i * h, T) << std::endl;
		}
		else
		{
			file << i * h << "\t" << value[i] << std::endl;
		}
	}
	file.close();
}

void print_time(std::string filename, long long time)
{
	std::ofstream file(filename);
	file << time << " microseconds." << std::endl;
	file.close();
}
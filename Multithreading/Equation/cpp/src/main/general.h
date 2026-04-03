#define _USE_MATH_DEFINES
#include <cmath>
#include <fstream>
#include <vector>
#include <string>

// Переменные для уравнения теплопроводности

extern const double alpha;
extern const double L;
extern const int N;
extern const double h;
extern const double T;
extern const int M;
extern const double tau;

double f(double x, double t);
double phi(double x);
double expected_u(double x, double t);

// Переменные для записи в файл

extern const std::string single_filename;
extern const std::string single_time_filename;
extern const std::string openmp_filename;
extern const std::string openmp_time_filename;
extern const std::string mpi_filename;
extern const std::string mpi_time_filename;

void print_value(std::string filename, std::vector<double> value);
void print_time(std::string filename, long long time);

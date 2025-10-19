#include "general.h"
#include <chrono>

// Подсчёт интеграла методом прямоугольника
double static square(double start, double finish, long long N, double (*func)(double)) {
    double result = 0.0;
    double h = (finish - start) / N;

    for (long long i = 0; i < N; ++i) {
        result += func(start + i * h - h / 2);
    }

    return result * h;
}

// Подсчёт интеграла методом трапеции
double static trapeziod(double start, double finish, long long N, double (*func)(double)) {
    double result = 0.0;
    double h = (finish - start) / N;

    for (long long i = 1; i < N - 1; ++i) {
        result += func(start + i * h);
    }

    result += (func(start) + func(finish)) / 2.0;
    return result * h;
}

// Подсчёт интеграла методом симпсона
double static simpson(double start, double finish, long long N, double (*func)(double)) {
    if (N % 2 != 0) N++;

    double h = (finish - start) / N;
    double sum = func(start) + func(finish);

    for (long long i = 1; i < N; i += 2) {
        sum += 4.0 * func(start + i * h);
    }

    for (long long i = 2; i < N; i += 2) {
        sum += 2.0 * func(start + i * h);
    }

    return sum * h / 3.0;
}

// Подсчёт интеграла с точностью eps
double static compute(double start, double finish, double (*func)(double),
    double (*method)(double, double, long long, double (*)(double))) {

    long long N = startN;
    double prev_result = 0.0;
    double current_result = method(start, finish, N, func);

    do {
        if (N > max_iteration) {
            break;
        }

        prev_result = current_result;

        N *= 10;

        current_result = method(start, finish, N, func);

    } while (fabs(current_result - prev_result) >= eps);

    return current_result;
}

int main(int argc, char* argv[]) {

    // Засекаем время
    auto startProgram = std::chrono::high_resolution_clock::now();

    double result = 0.0;

    // В зависимости от задачи выполняем нужные действия
    switch (current_task) {
        case A_SQUARE:
            result = compute(a_start, a_finish, a_fun, square);
            break;
        case B_SQUARE:
            result = compute(b_start, b_finish, b_fun, square);
            break;
        case C_SQUARE:
            result = compute(c_start, c_finish, c_fun, square);
            break;
        case D_SQUARE:
            result = compute(d_start, d_finish, d_fun, square);
            break;
        case A_TRAPEZIOD:
            result = compute(a_start, a_finish, a_fun, trapeziod);
            break;
        case B_TRAPEZIOD:
            result = compute(b_start, b_finish, b_fun, trapeziod);
            break;
        case C_TRAPEZIOD:
            result = compute(c_start, c_finish, c_fun, trapeziod);
            break;
        case D_TRAPEZIOD:
            result = compute(d_start, d_finish, d_fun, trapeziod);
            break;
        case A_SIMPSON:
            result = compute(a_start, a_finish, a_fun, simpson);
            break;
        case B_SIMPSON:
            result = compute(b_start, b_finish, b_fun, simpson);
            break;
        case C_SIMPSON:
            result = compute(c_start, c_finish, c_fun, simpson);
            break;
        case D_SIMPSON:
            result = compute(d_start, d_finish, d_fun, simpson);
            break;
    }

    // Записываем значение интеграла в файл
    print_integral(single_file_name, result);

    // Останавливаем время
    auto endProgram = std::chrono::high_resolution_clock::now();

    // Подсчитываем время в мкс
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(endProgram - startProgram);

    // Записываем время выполнения программы
    print_time(single_time_file_name, duration.count());

	return 0;
}
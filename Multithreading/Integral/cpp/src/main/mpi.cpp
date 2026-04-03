#include "general.h"
#include <mpi.h>
#include <cmath>
#include <chrono>
#include <iostream>

// Подсчёт интеграла методом прямоугольника
double static square(double start, double finish, long long N, double(*func)(double)) {

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    double local_result = 0.0;
    double h = (finish - start) / N;

    // Распределяем итерации по процессам
    long long chunk_size = N / size;
    long long start_idx = rank * chunk_size;
    long long end_idx = (rank == size - 1) ? N : start_idx + chunk_size;

    // Каждый процесс считает свою часть
    for (long long i = start_idx; i < end_idx; ++i) {
        local_result += func(start + i * h - h / 2);
    }

    // Собираем результаты на процессе 0
    double global_result = 0.0;
    MPI_Reduce(&local_result, &global_result, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);

    return global_result * h;
}

// Подсчёт интеграла методом трапеции
double static trapeziod(double start, double finish, long long N, double(*func)(double)) {
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    double local_result = 0.0;
    double h = (finish - start) / N;

    long long chunk_size = (N - 1) / size;  // Только внутренние точки!
    long long start_idx = rank * chunk_size + 1;  // Начинаем с 1
    long long end_idx = (rank == size - 1) ? N : start_idx + chunk_size;

    // Только внутренние точки (1..N-1)
    for (long long i = start_idx; i < end_idx; ++i) {
        local_result += func(start + i * h);
    }

    // Граничные точки (только процесс 0)
    if (rank == 0) {
        local_result += (func(start) + func(finish)) / 2.0;
    }

    double global_result = 0.0;
    MPI_Reduce(&local_result, &global_result, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);

    return global_result * h;
}

// Подсчёт интеграла методом симпсона
double static simpson(double start, double finish, long long N, double(*func)(double)) {
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (N % 2 != 0) N++;
    double h = (finish - start) / N;
    double local_sum = 0.0;

    long long odd_chunk = (N / 2) / size;
    long long odd_start = rank * odd_chunk;
    long long odd_end = (rank == size - 1) ? (N / 2) : odd_start + odd_chunk;

    for (long long j = odd_start; j < odd_end; ++j) {
        long long i = 2 * j + 1;
        local_sum += 4.0 * func(start + i * h);
    }

    long long even_chunk = ((N - 2) / 2) / size;
    long long even_start = rank * even_chunk;
    long long even_end = (rank == size - 1) ? ((N - 2) / 2) : even_start + even_chunk;

    for (long long j = even_start; j < even_end; ++j) {
        long long i = 2 * j + 2;
        local_sum += 2.0 * func(start + i * h);
    }

    if (rank == 0) {
        local_sum += func(start) + func(finish);
    }

    double global_sum = 0.0;
    MPI_Reduce(&local_sum, &global_sum, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);

    return global_sum * h / 3.0;
}

// Подсчёт интеграла с точностью eps
double static compute(double start, double finish, double(*func)(double),
    double(*method)(double, double, long long, double(*)(double))) {

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    long long N = startN;
    double prev_result = 0.0;
    double current_result = 0.0;

    if (rank == 0) 
    {
        current_result = method(start, finish, N, func);
        // Отправляем всем процессам
        for (int i = 1; i < size; i++) {
            MPI_Send(&current_result, 1, MPI_DOUBLE, i, 0, MPI_COMM_WORLD);
        }
    }
    else 
    {
        method(start, finish, N, func);
        MPI_Recv(&current_result, 1, MPI_DOUBLE, 0, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    }
    MPI_Barrier(MPI_COMM_WORLD);

    
    do {
        if (N > max_iteration) break;

        prev_result = current_result;

        N *= 10;

        if (rank == 0)
        {
            current_result = method(start, finish, N, func);
            // Отправляем всем процессам
            for (int i = 1; i < size; i++) {
                MPI_Send(&current_result, 1, MPI_DOUBLE, i, 0, MPI_COMM_WORLD);
            }
        }
        else
        {
            method(start, finish, N, func);
            MPI_Recv(&current_result, 1, MPI_DOUBLE, 0, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        }

        MPI_Barrier(MPI_COMM_WORLD);

    } while (fabs(current_result - prev_result) >= eps);

    return current_result;
}

int main(int argc, char* argv[]) {
    MPI_Init(&argc, &argv);

    int rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

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

    if (rank == 0)
    {
        // Записываем значение интеграла в файл
        print_integral(mpi_file_name, result);

        // Останавливаем время
        auto endProgram = std::chrono::high_resolution_clock::now();

        // Подсчитываем время в мкс
        auto duration = std::chrono::duration_cast <std::chrono::microseconds> (endProgram - startProgram);

        // Записываем время выполнения программы
        print_time(mpi_time_file_name, duration.count());
    }

    MPI_Finalize();

    return 0;
}
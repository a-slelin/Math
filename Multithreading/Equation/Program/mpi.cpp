#include "general.h"
#include <cmath>
#include <vector>
#include <chrono>
#include <iostream>
#include <mpi.h>

int main(int argc, char* argv[]) {

    // Инициализируем MPI
    MPI_Init(&argc, &argv);

    // Получаем ранк и количество процессов
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (size > N) {
        if (rank != 0) {

            MPI_Finalize();

            return 0;
        }

        size = 1;
    }

    // Засекаем время
    auto startProgram = std::chrono::high_resolution_clock::now();

    // Разделение отрезка равномерно между введенными процессами
    int chunk_size = N / size;
    int start = rank * chunk_size + 1;
    int end = (rank == size - 1) ? N - 2 : start + chunk_size - 1;
    int local_size = end - start + 1;

    // Добавление памяти под соседей
    int expended_size = local_size + 2;
    int meta[2] = { start, end };

    std::vector<double> u_curr_local(expended_size, 0.0);
    std::vector<double> u_next_local(expended_size, 0.0);

    // Инициализация локальных данных вместе с соседями
    for (int i = 0; i < expended_size; ++i) {
        u_curr_local[i] = phi((start + i - 1) * h);
    }

    // Основной цикл по времени
    for (int m = 0; m < M; ++m) {

        MPI_Request requests[4];
        int request_count = 0;

        if (rank != size - 1) 
        {
            // Все, кроме последнего, принимают левую границу в правую границу
            MPI_Irecv(&u_curr_local[local_size + 1], 1, MPI_DOUBLE, rank + 1, 0, MPI_COMM_WORLD, &requests[request_count++]);
        }


        if (rank != 0)
        {
            // Все, кроме 0, принимают правую границу в левую границу
            MPI_Irecv(&u_curr_local[0], 1, MPI_DOUBLE, rank - 1, 0, MPI_COMM_WORLD, &requests[request_count++]);
        }

        if (rank != 0)
        {
            // Все, кроме 0, отправляют левую границу
            MPI_Isend(&u_curr_local[1], 1, MPI_DOUBLE, rank - 1, 0, MPI_COMM_WORLD, &requests[request_count++]);

        }

        if (rank != size - 1)
        {
            // Все, кроме последнего, отправляют правую границу
            MPI_Isend(&u_curr_local[local_size], 1, MPI_DOUBLE, rank + 1, 0, MPI_COMM_WORLD, &requests[request_count++]);
        }

        // Ждем пока пересылка границами закончится
        MPI_Waitall(request_count, requests, MPI_STATUSES_IGNORE);

        for (int i = 1; i <= local_size; ++i) {
            u_next_local[i] = u_curr_local[i] + (alpha * tau) / (h * h) * (u_curr_local[i - 1] - 2 * u_curr_local[i] + u_curr_local[i + 1]) + tau * f((start + i - 1) * h, m * tau);
        }

        // Граничные условия Неймана на глобальных границах
        if (rank == 0) {
            u_next_local[0] = u_next_local[1]; // Левая граница
        }

        if (rank == size - 1) {
            u_next_local[local_size + 1] = u_next_local[local_size]; // Правая граница
        }

        // Обмен массивами для следующей итерации
        swap(u_curr_local, u_next_local);
    }

    if (rank != 0)
    {
        MPI_Send(meta, 2, MPI_INT, 0, 1, MPI_COMM_WORLD);
        MPI_Send(&u_curr_local[0], expended_size, MPI_DOUBLE, 0, 2, MPI_COMM_WORLD);
    }


    // Запись результатов и времени
    if (rank == 0) {

        std::vector<double> global_result(N);

        for (int i = 0; i <= local_size; ++i)
        {
            global_result[i] = u_curr_local[i];
        }

        if (size == 1) {
            global_result[local_size + 1] = u_curr_local[local_size + 1];
        }

        for (int ps = 1; ps < size; ++ps)
        {
            int ps_meta[2];
            MPI_Recv(ps_meta, 2, MPI_INT, ps, 1, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            int ps_start = ps_meta[0];
            int ps_end = ps_meta[1];
            int ps_size = ps_end - ps_start + 1;

            std::vector<double> buffer(ps_size + 2);
            MPI_Recv(&buffer[0], ps_size + 2, MPI_DOUBLE, ps, 2, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            for (int i = 1; i < buffer.size() - (ps == size - 1 ? 0 : 1); ++i)
            {
                global_result[ps_start + i - 1] = buffer[i];
            }
        }

        // Записываем значение интеграла в файл
        print_value(mpi_filename, global_result);

        // Останавливаем время
        auto endProgram = std::chrono::high_resolution_clock::now();

        // Подсчитываем время в мкс
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(endProgram - startProgram);

        // Записываем время выполнения программы
        print_time(mpi_time_filename, duration.count());
    }

    // Закрываем MPI
    MPI_Finalize();

    return 0;
}
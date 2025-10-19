#include "general.h"
#include <vector>
#include <mpi.h>
#include <chrono>
#include <iostream>

const int root = 0;

const int matrix_tag = 1;

const int meta_tag = 0;

int main(int argc, char** argv) {

    // Засекаем время выполнения
    auto startProgram = std::chrono::high_resolution_clock::now();

    // Инициализируем MPI
    MPI_Init(&argc, &argv);

    // Получаем rank процесса, а также их количество
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    // Разделение строк матрицы равномерно между введенными процессами
    int chunk_size = N / size;
    int start = rank * chunk_size + 1;
    int end = (rank == size - 1) ? N : start + chunk_size - 1;
    int row_size = end - start + 1;
    int meta[2] = { start, end };

    // Создаем часть матрицы C на каждый процесс для заполнения 
    // конкретно его строк данными
    std::vector<std::vector<int>> local_c(row_size + 1, std::vector<int>(N + 1));

    // Алгоритм для каждого процесса по подсчёту конкретно своих строк в матрице.
    for (int local_row = 1; local_row <= row_size; ++local_row) {
        int global_row = start + local_row - 1;
        for (int i = 1; i <= N; ++i) {
            for (int j = 1; j <= N; ++j) {
                local_c[local_row][i] += a(global_row, j) * b(j, i);
            }
        }
    }

    if (rank != root) {

        // Скидываем мета-данные
        MPI_Send(meta, 2, MPI_INT, root, meta_tag, MPI_COMM_WORLD);

        // Отправка данных построчно
        for (int i = 1; i <= row_size; ++i) {
            MPI_Send(&local_c[i][1], N, MPI_INT, root, matrix_tag, MPI_COMM_WORLD);
        }
    }
    else {
        // Создаем глобальную матрицу C в главном процессе
        std::vector<std::vector<int>> c(N + 1, std::vector<int>(N + 1));

        if (size == 1) {
            // Если работает один процесс, то просто берём локальную матрицу
            c = local_c;
        }
        else {

            // Если же у нас несколько процессов, то принимаем от них локальные матрицы
            // и записываем в нашу глобальную матрицу в главном процессе
            for (int ps = 0; ps < size; ++ps) {
                if (ps == root) continue;

                int ps_meta[2];
                MPI_Recv(ps_meta, 2, MPI_INT, ps, meta_tag, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
                int ps_start = ps_meta[0];
                int ps_end = ps_meta[1];
                int ps_row = ps_end - ps_start + 1;

                for (int i = 1; i <= ps_row; ++i) {
                    MPI_Recv(&c[ps_start + i - 1][1], N, MPI_INT, ps, matrix_tag, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
                }
            }

            // Записываем локальную матрицу из root в глобальную матрицу
            for (int i = 1; i <= row_size; ++i) {
                c[start + i - 1] = local_c[i];
            }
        }

        // Записываем матрицу в файл
        print_matrix(mpi_file_name, c);
    }

    // Закрываем MPI
    MPI_Finalize();

    // Останавливаем время выполнения
    auto endProgram = std::chrono::high_resolution_clock::now();

    // Подсчёт времени выполнения
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(endProgram - startProgram);

    // Записываем время в файл
    print_time(mpi_time_file_name, duration.count());

    return 0;
}
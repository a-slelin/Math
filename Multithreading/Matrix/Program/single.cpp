#include "general.h"
#include <vector>
#include <chrono>

int main(int argc, char** argv) {

    // Засекаем время выполнения
    auto start = std::chrono::high_resolution_clock::now();

    std::vector<std::vector<int>> c(N + 1, std::vector<int>(N + 1));

    // Стандартный алгоритм перемножения матриц
    for (int i = 1; i <= N; ++i) {
        for (int j = 1; j <= N; ++j) {
            for (int k = 1; k <= N; ++k) {
                c[i][j] += a(i, k) * b(k, j);
            }
        }
    }

    // Записываем матрицу в файл
    print_matrix(single_file_name, c);

    // Останавливаем время выполнения
    auto end = std::chrono::high_resolution_clock::now();

    // Подсчёт времени выполнения
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

    // Записываем время в файл
    print_time(single_time_file_name, duration.count());

    return 0;
}
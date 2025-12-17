#include "general.h"
#include <cmath>
#include <vector>
#include <iostream>
#include <chrono>

int main(int argc, char* argv[]) {

    // Засекаем время
    auto startProgram = std::chrono::high_resolution_clock::now();

    std::vector<double> u_curr(N, 0.0);   // Текущий временной слой (m)
    std::vector<double> u_next(N, 0.0);   // Следующий временной слой (m+1)

    // Записываем начальное условие
    for (int i = 0; i < N; ++i) {
        u_curr[i] = phi(i * h);
    }

    // Основной цикл по времени
    for (int m = 1; m < M; ++m) {

        // Внутренние точки
        for (int i = 1; i < N - 1; ++i) {
            u_next[i] = u_curr[i] + (alpha * tau) / (h * h) * (u_curr[i - 1] - 2 * u_curr[i] + u_curr[i + 1]) + tau * f(i * h, m * tau);
        }

        // Граничные условия
        /*
        * u(0, t) - u(маленькое, t) = 0 и u(1, t) - u(1-маленькое, t) = 0
        */
        u_next[0] = u_next[1];
        u_next[N - 1] = u_next[N - 2];

        // Обмен массивов
        swap(u_curr, u_next);
    }

    // Записываем значение интеграла в файл
    print_value(single_filename, u_curr);

    // Останавливаем время
    auto endProgram = std::chrono::high_resolution_clock::now();

    // Подсчитываем время
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(endProgram - startProgram);

    // Записываем время выполнения программы
    print_time(single_time_filename, duration.count());

    return 0;
}
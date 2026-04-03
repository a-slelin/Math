import matplotlib.pyplot as plt
import numpy as np
from const import *


# Функция чтения результатов из файла
def read_results(filename):
    threads = []
    times = []

    # Флаг для отслеживания, находимся ли мы в разделе итоговых данных
    in_final_section = False

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()

            # Если находим заголовок "Итоговое время:", включаем флаг
            if line.startswith('Итоговое время:'):
                in_final_section = True
                continue

            # Если находим следующий заголовок, выключаем флаг
            if in_final_section and (line.startswith('Метод') or line.startswith('Интеграл')):
                break

            # Если мы в разделе итоговых данных и строка содержит данные
            if in_final_section and line:
                parts = line.split()
                if len(parts) >= 2:
                    # Проверяем, что первый элемент - число
                    if parts[0].isdigit():
                        threads.append(int(parts[0]))
                        # Извлекаем время
                        time_str = parts[1].replace(' мкс', '')
                        if time_str.isdigit():
                            times.append(int(time_str))

    return threads, times


# Функция для получения оптимального количества потоков
def calculate_optimal_threads(threads, speedup, threshold=0.95):
    max_speedup = max(speedup)
    for i, s in enumerate(speedup):
        if s >= max_speedup * threshold:
            return threads[i]
    return threads[-1]


# Функция отрисовки графиков
def plot_graph(threads, times, output_file, single_time):
    plt.figure(figsize=(14, 10))

    # График времени выполнения
    plt.subplot(2, 1, 1)

    # Основной график времени
    plt.plot(threads, times, 'bo-', linewidth=2, markersize=6, label='Время выполнения')

    # Линия однопоточного времени
    plt.axhline(y=single_time, color='r', linestyle='--', linewidth=2,
                label=f'Однопоточное время ({single_time} мкс)')

    # Среднее время
    avg_time = np.mean(times)
    plt.axhline(y=avg_time, color='orange', linestyle='-.', linewidth=2,
                label=f'Среднее время ({avg_time:.0f} мкс)')

    plt.xlabel('Количество потоков')
    plt.ylabel('Время (микросекунды)')
    plt.title('Зависимость времени выполнения от количества потоков')
    plt.grid(True, alpha=0.3)
    plt.legend()

    # График ускорения
    plt.subplot(2, 1, 2)
    speedup = [times[0] / t for t in times]

    # Основной график ускорения
    plt.plot(threads, speedup, 'ro-', linewidth=2, markersize=6, label='Ускорение')
    plt.plot(threads, threads, 'g--', alpha=0.7, label='Идеальное ускорение')

    # Находим точку оптимальности
    optimal_threads = calculate_optimal_threads(threads, speedup)
    optimal_speedup = speedup[threads.index(optimal_threads)]

    # Вертикальная линия оптимальности
    plt.axvline(x=optimal_threads, color='purple', linestyle=':', linewidth=2,
                label=f'Оптимум ({optimal_threads} потоков)')

    # Горизонтальная линия достигнутого ускорения
    plt.axhline(y=optimal_speedup, color='purple', linestyle=':', linewidth=2,
                label=f'Макс. ускорение ({optimal_speedup:.2f}x)')

    # Аннотация
    plt.annotate(f'Оптимум: {optimal_threads} потоков\nУскорение: {optimal_speedup:.2f}x',
                 xy=(optimal_threads, optimal_speedup),
                 xytext=(optimal_threads + 1, optimal_speedup - 0.5),
                 arrowprops=dict(arrowstyle='->', color='purple'))

    plt.xlabel('Количество потоков')
    plt.ylabel('Коэффициент ускорения')
    plt.title('Ускорение относительно однопоточного выполнения')
    plt.grid(True, alpha=0.3)
    plt.legend()

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.show()

    print(f'График сохранен как {output_file}')

    print(f'Статистика для {output_file}:')
    print(f'  - Минимальное время: {min(times)} мкс ({threads[times.index(min(times))]} потоков)')
    print(f'  - Среднее время: {avg_time:.0f} мкс')
    print(f'  - Оптимальное количество потоков: {optimal_threads}')
    print(f'  - Максимальное ускорение: {max(speedup):.2f}x')
    print(f'  - Эффективность алгоритма: {optimal_speedup / optimal_threads:.2f}')


def draw(integral='a'):
    check_integral(integral)

    # Читаем однопоточное время
    _, single_times = read_results(f'single_{integral}.txt')
    single_time = single_times[0]

    print('=' * 50)
    print('АНАЛИЗ OPENMP')
    print('=' * 50)

    # OpenMP график
    threads_omp, times_omp = read_results(f'openmp_{integral}.txt')
    plot_graph(threads_omp, times_omp, f'openmp_{integral}.png', single_time)

    print('\n' + '=' * 50)
    print('АНАЛИЗ MPI')
    print('=' * 50)

    # MPI график
    threads_mpi, times_mpi = read_results(f'mpi_{integral}.txt')
    plot_graph(threads_mpi, times_mpi, f'mpi_{integral}.png', single_time)


def graph(integral='a'):
    check_integral(integral)

    _, single_times = read_results(f'single_{integral}.txt')
    single_time = single_times[0]
    threads_omp, times_omp = read_results(f'openmp_{integral}.txt')
    threads_mpi, times_mpi = read_results(f'mpi_{integral}.txt')

    omp_speedup = [single_time / t for t in times_omp]
    mpi_speedup = [single_time / t for t in times_mpi]

    plt.figure(figsize=(10, 6))
    plt.plot(threads_omp, omp_speedup, 'o-', label='OpenMP', color='r')
    plt.plot(threads_mpi, mpi_speedup, 's-', label='MPI', color='b')
    plt.xlabel('Количество потоков/процессов')
    plt.ylabel('Ускорение')
    plt.title('График ускорения параллельного алгоритма')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'graph_{integral}.png', dpi=300)
    plt.show()

def graph_general():
    _, a_single_times = read_results(f'single_a.txt')
    a_single_time = a_single_times[0]
    a_threads_omp, a_times_omp = read_results(f'openmp_a.txt')
    a_threads_mpi, a_times_mpi = read_results(f'mpi_a.txt')

    _, b_single_times = read_results(f'single_b.txt')
    b_single_time = b_single_times[0]
    b_threads_omp, b_times_omp = read_results(f'openmp_b.txt')
    b_threads_mpi, b_times_mpi = read_results(f'mpi_b.txt')

    _, c_single_times = read_results(f'single_c.txt')
    c_single_time = c_single_times[0]
    c_threads_omp, c_times_omp = read_results(f'openmp_c.txt')
    c_threads_mpi, c_times_mpi = read_results(f'mpi_c.txt')

    _, d_single_times = read_results(f'single_d.txt')
    d_single_time = d_single_times[0]
    d_threads_omp, d_times_omp = read_results(f'openmp_d.txt')
    d_threads_mpi, d_times_mpi = read_results(f'mpi_d.txt')

    single_time = a_single_time + b_single_time + c_single_time + d_single_time
    threads_omp = range(1, 29)
    threads_mpi = range(1, 29)
    times_omp = [a_times_omp[i] + b_times_omp[i] + c_times_omp[i] + d_times_omp[i] for i in range(0, 28)]
    times_mpi = [a_times_mpi[i] + b_times_mpi[i] + c_times_mpi[i] + d_times_mpi[i] for i in range(0, 28)]

    omp_speedup = [single_time / t for t in times_omp]
    mpi_speedup = [single_time / t for t in times_mpi]

    plt.figure(figsize=(10, 6))
    plt.plot(threads_omp, omp_speedup, 'o-', label='OpenMP', color='r')
    plt.plot(threads_mpi, mpi_speedup, 's-', label='MPI', color='b')
    plt.xlabel('Количество потоков/процессов')
    plt.ylabel('Ускорение')
    plt.title('График ускорения параллельного алгоритма')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'graph.png', dpi=300)
    plt.show()


if __name__ == '__main__':
    # Выбери интеграл из ('a', 'b', 'c', 'd')
    draw('a')

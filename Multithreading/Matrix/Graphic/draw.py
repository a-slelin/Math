import matplotlib.pyplot as plt
import numpy as np


# Функция для чтения результатов из файла
def read_results(filename):
    threads = []
    times = []

    with open(filename, 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            if parts[0].isdigit() and parts[1].isdigit():
                threads.append(int(parts[0]))
                times.append(int(parts[1]))

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

    print(f'Статист ика для {output_file}:')
    print(f'  - Минимальное время: {min(times)} мкс ({threads[times.index(min(times))]} потоков)')
    print(f'  - Среднее время: {avg_time:.0f} мкс')
    print(f'  - Оптимальное количество потоков: {optimal_threads}')
    print(f'  - Максимальное ускорение: {max(speedup):.2f}x')
    print(f'  - Эффективность алгоритма: {optimal_speedup / optimal_threads:.2f}')


def draw():
    # Читаем однопоточное время
    _, single_times = read_results('single.txt')
    single_time = single_times[0]

    print('=' * 50)
    print('АНАЛИЗ OPENMP')
    print('=' * 50)

    # OpenMP график
    threads_omp, times_omp = read_results('openmp.txt')
    plot_graph(threads_omp, times_omp, 'openmp.png', single_time)

    print('\n' + '=' * 50)
    print('АНАЛИЗ MPI')
    print('=' * 50)

    # MPI график
    threads_mpi, times_mpi = read_results('mpi.txt')
    plot_graph(threads_mpi, times_mpi, 'mpi.png', single_time)


if __name__ == '__main__':
    draw()

import subprocess
import os
import time
import re
from const import *


# Функция считает интеграл с помощью инструмента
def compute(tool, integral='a'):
    # Проверяем верный ли ввод
    check_tool(tool)
    check_integral(integral)

    if tool == 'single':
        print(f'\nЗапуск однопоточной программы для интеграла под буквой {integral})...\n')
    else:
        print(f'Запуск с многопоточной программы с {tools_name.get(tool)} для интеграла под буквой {integral})...\n')

    results = []

    tasks = range_integral(integral)

    # Запускаем под каждую задачу нужное количество потоков
    for task in tasks:
        for threads in (range(1, 2) if tool == 'single' else range(start_thread, end_thread + 1)):
            if tool == 'single':
                print(f'Запуск задачи {tasks_name.get(task)}...')
            else:
                print(f'Запуск задачи {tasks_name.get(task)} с {threads} потоками...')

            value, exec_time = start_program(tool, task, threads)
            results.append((task, threads, value, exec_time))

            print(f'Задача отработала за {exec_time} мкс.')
            time.sleep(1)
        print()

    output = f'{tool}_{integral}.txt'

    # Записываем результаты в файл
    with open(output, 'w') as f:
        f.write(f'Интеграл под буквой {integral})\n')
        f.write('\nМетод прямоугольника:\n')
        f.write('Потоки\tЗначение\tВремя\n')
        for result in results:
            if result[0] % 3 == 0:
                f.write(f'{result[1]}\t{result[2]}\t{result[3]} мкс\n')

        f.write('\nМетод трапеции:\n')
        f.write('Потоки\tЗначение\tВремя\n')
        for result in results:
            if result[0] % 3 == 1:
                f.write(f'{result[1]}\t{result[2]}\t{result[3]} мкс\n')

        f.write('\nМетод симпсона:\n')
        f.write('Потоки\tЗначение\tВремя\n')
        for result in results:
            if result[0] % 3 == 2:
                f.write(f'{result[1]}\t{result[2]}\t{result[3]} мкс\n')

        f.write('\nИтоговое время:\n')
        f.write('Потоки\tВремя\n')
        for i in (range(1, 2) if tool == 'single' else all_threads):
            summ = 0
            for result in results:
                if result[1] == i:
                    summ += result[3]

            f.write(f'{i}\t{summ} мкс\n')

    print(f'Результаты сохранены в {output}.')


# Функция запускает программу на C++
def start_program(tool, task, threads):
    # Проверяем верный ли ввод
    check_tool(tool)
    check_task(task)
    check_thread(threads)

    value, exec_time = 0, 0

    # Задаем параметры запуска процесса
    env = os.environ.copy()
    env[task_env] = str(task)

    if tool != 'mpi':
        env[omp_env] = str(threads)
        command = [path]
    else:
        command = [mpi_comm, mpi_arg, str(threads), path]

    # Запускаем сам процесс
    subprocess.run(command, env=env, capture_output=True, text=True)

    # Читаем полученные данные
    with open(f'{tool}_integral.txt', 'r') as f:
        content = f.read().strip()
        value = float(content)

    with open(f'{tool}_time.txt', 'r') as f:
        content = f.read().strip()
        match = re.search(r'(\d+)', content)
        exec_time = int(match.group(1))

    return value, exec_time


if __name__ == '__main__':
    # Выбери инструмент из ('single', 'openmp', 'mpi')
    # Выбери интеграл из ('a', 'b', 'c', 'd')
    compute('mpi','d')

import subprocess
import os
import time
import re
from const import *


# Функция считает матрицу с помощью инструмента
def compute(tool):
    # Проверяем верный ли ввод
    check_tool(tool)

    if tool == 'single':
        print(f'Запуск однопоточной программы...\n')
    else:
        print(f'Запуск многопоточной программы с {tools_name.get(tool)}...\n')

    results = []

    # Запускаем под каждую задачу нужное количество потоков
    for threads in (range(1, 2) if tool == 'single' else all_threads):
        if tool == 'single':
            print(f'Запуск программы...')
        else:
            print(f'Запуск программы с {threads} потоками...')

        exec_time = start_program(tool, threads)
        results.append((threads, exec_time))

        print(f'Задача отработала за {exec_time} мкс.')
        time.sleep(1)

    output = f'{tool}.txt'

    # Записываем результаты в файл
    with open(output, 'w') as f:
        f.write('Поток\tВремя\n')
        for threads, exec_time in results:
            f.write(f'{threads}\t{exec_time}\n')

    print(f'\nРезультаты сохранены в {output}.')


# Функция запускает программу на C++
def start_program(tool, threads):
    # Проверяем верный ли ввод
    check_tool(tool)
    check_thread(threads)

    # Задаем параметры запуска процесса
    env = os.environ.copy()

    if tool != 'mpi':
        env[omp_env] = str(threads)
        command = [path]
    else:
        command = [mpi_comm, mpi_arg, str(threads), path]

    # Запускаем сам процесс
    subprocess.run(command, env=env, capture_output=True, text=True)

    # Читаем полученные данные
    with open(f'{tool}_time.txt', 'r') as f:
        content = f.read().strip()
        match = re.search(r'(\d+)', content)
        exec_time = int(match.group(1))
        return exec_time


if __name__ == '__main__':
    # Выбери инструмент из ('single', 'openmp', 'mpi')
    compute('mpi')

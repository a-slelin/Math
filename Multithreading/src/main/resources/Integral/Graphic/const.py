# Путь до исполняемого файла

abs_path = 'C:\\Users\\admin\\source\\repos\\Integral\\x64\\Debug\\'
file_name = 'Integral.exe'
path = abs_path + file_name

# Название переменных окружения

task_env = 'INTEGRAL_TASK'
omp_env = 'OMP_NUM_THREADS'
mpi_comm = 'mpiexec'
mpi_arg = '-n'

# Потоки для подсчёта в лабораторной работе

start_thread = 1
end_thread = 28
all_threads = range(start_thread, end_thread + 1)

# Инструменты

tools = ('openmp', 'mpi', 'single')
tools_name = {
    'openmp': 'OpenMP',
    'mpi': 'MPI',
    'single': 'Single'
}

# Интегралы

integrals = ('a', 'b', 'c', 'd')

# Задачи

tasks_name = {
    0: 'A_SQUARE', 1: 'A_TRAPEZIOD', 2: 'A_SIMPSON',
    3: 'B_SQUARE', 4: 'B_TRAPEZIOD', 5: 'B_SIMPSON',
    6: 'C_SQUARE', 7: 'C_TRAPEZIOD', 8: 'C_SIMPSON',
    9: 'D_SQUARE', 10: 'D_TRAPEZIOD', 11: 'D_SIMPSON'
}
tasks_value = range(0, 12)


# Вспомогательные функции


def check_tool(tool):
    if tool not in tools:
        exit(f'Tool must be in {tools}')


def check_integral(integral):
    if integral not in integrals:
        exit(f'Integral must be in {integrals}')


def range_integral(integral):
    check_integral(integral)

    if integral == 'a':
        return range(0, 3)

    if integral == 'b':
        return range(3, 6)

    if integral == 'c':
        return range(6, 9)

    return range(9, 12)


def check_task(task):
    if task not in tasks_value:
        exit(f'Task must be in {tasks_value}')


def check_thread(thread):
    if thread not in all_threads:
        exit(f'Thread must be in {all_threads}')

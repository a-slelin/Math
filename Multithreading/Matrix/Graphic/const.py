# Путь до исполняемого файла

abs_path = 'C:\\Users\\admin\\source\\repos\\Matrix\\x64\\Debug\\'
file_name = 'Matrix.exe'
path = abs_path + file_name

# Название переменных окружения

omp_env = 'OMP_NUM_THREADS'
mpi_comm = 'mpiexec'
mpi_arg = '-n'

# Инструменты

tools = ('openmp', 'mpi', 'single')
tools_name = {
    'openmp': 'OpenMP',
    'mpi': 'MPI',
    'single': 'Single'
}

# Потоки для подсчёта в лабораторной работе

start_thread = 1
end_thread = 28
all_threads = range(start_thread, end_thread + 1)


# Вспомогательные функции


def check_tool(tool):
    if tool not in tools:
        exit(f'Tool must be in {tools}')


def check_thread(thread):
    if thread not in all_threads:
        exit(f'Thread must be in {all_threads}')

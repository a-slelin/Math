# Путь до исполняемого файла

abs_path = 'C:\\Users\\admin\\source\\repos\\Equation\\x64\\Debug\\'
file_name = 'Equation.exe'
path = abs_path + file_name

# Название переменных окружения

N_env = 'THERMAL_CONDUCTIVITY_N'
T_env = 'THERMAL_CONDUCTIVITY_T'
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


# Вспомогательные функции


def check_tool(tool):
    if tool not in tools:
        exit(f'Tool must be in {tools}')


def check_thread(thread):
    if thread not in all_threads:
        exit(f'Thread must be in {all_threads}')


def check_N(N):
    if not isinstance(N, int):
        exit('N must be an integer')

    if N <= 1:
        exit('N must be greater than 1')


def check_T(T):
    if not isinstance(T, float):
        exit('T must be an float')

    if T <= 10 ** -12:
        exit('T must be greater than zero')

#include <iostream>
#include <mpi.h>

int main(int argc, char** argv) {

    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    const int64_t N = static_cast<int64_t>(INT_MAX);
    int64_t local_sum = 0;

    int64_t chunk_size = N / size;
    int64_t start = rank * chunk_size + 1;
    int64_t end = (rank == size - 1) ? N : start + chunk_size - 1;

    for (int64_t i = start; i <= end; ++i) {
        local_sum += i;
    }

    int64_t global_sum = 0;

    MPI_Reduce(&local_sum, &global_sum, 1, MPI_LONG_LONG, MPI_SUM, 0, MPI_COMM_WORLD);

    if (rank == 0) {
        std::cout << "The sum of numbers from 1 to "
            << N
            << " is "
            << global_sum
            << std::endl;
        system("pause");
    }

    MPI_Finalize();

    return 0;
}
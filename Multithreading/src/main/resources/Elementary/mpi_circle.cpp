#include <iostream>
#include <mpi.h>

int main(int argc, char** argv) {

    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    char buff[100];
    snprintf(buff, sizeof(buff), "Hello from %d", rank);

    MPI_Send(buff, 100, MPI_CHAR, (rank + 1) % size, 0, MPI_COMM_WORLD);
    MPI_Recv(buff, 100, MPI_CHAR, (rank - 1 + size) % size, 0, MPI_COMM_WORLD, MPI_STATUSES_IGNORE);

    std::cout << "Process "
        << rank
        << " received: "
        << buff
        << std::endl;

    MPI_Finalize();

    if (rank == 0) {
        system("pause");
    }

    return 0;
}
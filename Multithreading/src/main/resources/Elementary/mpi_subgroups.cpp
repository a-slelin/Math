#include <iostream>
#include <mpi.h>

int main(int argc, char** argv) {

    MPI_Init(&argc, &argv);

    MPI_Comm parent_comm = MPI_COMM_WORLD;
    int world_rank, world_size;
    MPI_Comm_rank(parent_comm, &world_rank);
    MPI_Comm_size(parent_comm, &world_size);

    int color = world_rank % 3;

    MPI_Comm new_comm;

    MPI_Comm_split(parent_comm, color, world_rank, &new_comm);

    int new_rank, new_size;

    MPI_Comm_rank(new_comm, &new_rank);
    MPI_Comm_size(new_comm, &new_size);

    std::cout << "Global rank "
        << world_rank
        << " -> New group "
        << color
        << ", rank in group "
        << new_rank
        << ", group size "
        << new_size
        << std::endl;

    MPI_Comm_free(&new_comm);

    MPI_Finalize();

    if (world_rank == 0) {
        system("pause");
    }

    return 0;
}
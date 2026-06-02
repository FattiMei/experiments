import numpy as np
import scipy.sparse as sp
import matplotlib.pyplot as plt


def assemble_laplacian(n: int,
                       left_boundary_value: float,
                       right_boundary_value: float) -> tuple["SparseMatrix", np.array]:
    A = sp.diags(
        diagonals=(
            -1.0 * np.ones(n-1),
             2.0 * np.ones(n),
            -1.0 * np.ones(n-1),
        ),
        offsets=(-1,0,1)
    )

    # manually edit the first and last row for Dirichlet boundary conditions
    A = A.tolil()
    A[0,:] = 0
    A[0,0] = 1
    A[-1,:] = 0
    A[-1,-1] = 1

    b = np.zeros(n)
    b[0]  = left_boundary_value
    b[-1] = right_boundary_value

    return A, b


def assemble_laplacian_symmetric(n: int,
                                 left_boundary_value: float,
                                 right_boundary_value: float) -> tuple["SparseMatrix", np.array]:
    A, b = assemble_laplacian(n, left_boundary_value, right_boundary_value)

    block_A = A[1:n-1, 1:n-1]

    # implicitly perform the gaussian elimination on the first and last rows of A
    block_b = b[1:n-1]
    block_b[0]  += b[0]
    block_b[-1] += b[-1]

    return block_A, block_b


class IterationCounter:
    def __init__(self):
        self.it = 0

    def count(self, arr):
        self.it += 1


if __name__ == '__main__':
    DISCRETIZATIONS = {
        'asymmetric': assemble_laplacian,
        'symmetric' : assemble_laplacian_symmetric
    }

    NODES = [10, 20, 50, 100, 200, 500, 1000]
    LEFT_BOUNDARY = 1.0
    RIGHT_BOUNDARY = 1.0

    for name, disc in DISCRETIZATIONS.items():
        iters = []

        for n in NODES:
            A, b = disc(n, LEFT_BOUNDARY, RIGHT_BOUNDARY)
            counter = IterationCounter()

            sol = sp.linalg.cg(A, b, callback=counter.count)
            iters.append(counter.it)

        plt.loglog(NODES, iters, label=name)

    plt.title("Iterations of CG for Poisson problem with Dirichlet conditions")
    plt.legend()
    plt.show()

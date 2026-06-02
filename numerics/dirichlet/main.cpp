#include <deal.II/grid/tria.h>
#include <deal.II/dofs/dof_handler.h>
#include <deal.II/grid/grid_generator.h>
#include <deal.II/fe/fe_q.h>
#include <deal.II/dofs/dof_tools.h>
#include <deal.II/fe/fe_values.h>
#include <deal.II/base/quadrature_lib.h>
#include <deal.II/base/function.h>
#include <deal.II/numerics/vector_tools.h>
#include <deal.II/numerics/matrix_tools.h>
#include <deal.II/lac/vector.h>
#include <deal.II/lac/full_matrix.h>
#include <deal.II/lac/sparse_matrix.h>
#include <deal.II/lac/dynamic_sparsity_pattern.h>
#include <deal.II/lac/solver_cg.h>
#include <deal.II/numerics/data_out.h>

#include <string>
#include <fstream>
#include <iostream>


using namespace dealii;


template <int dim>
class Poisson {
	public:
		// I don't care about polynomial interpolation
		// I just want to examine the matrix before and after
		// the application of Dirichlet boundary conditions
		Poisson(int n) : fe(1), dof_handler(mesh) {
			GridGenerator::subdivided_hyper_cube(mesh, n);

			dof_handler.distribute_dofs(fe);

			DynamicSparsityPattern dsp(dof_handler.n_dofs());
			DoFTools::make_sparsity_pattern(dof_handler, dsp);
			sparsity_pattern.copy_from(dsp);

			system_matrix.reinit(sparsity_pattern);
			system_rhs.reinit(dof_handler.n_dofs());
			solution.reinit(dof_handler.n_dofs());
		}

		void assemble() {
			const QGauss<dim> quadrature_formula(fe.degree + 1);
			FEValues<dim> fe_values(
				fe,
				quadrature_formula,
				update_values | update_gradients | update_JxW_values
			);

			const unsigned int dofs_per_cell = fe.n_dofs_per_cell();
			FullMatrix<double> cell_matrix(dofs_per_cell, dofs_per_cell);
			Vector<double>     cell_rhs(dofs_per_cell);

			std::vector<types::global_dof_index> local_dof_indices(dofs_per_cell);

			for (const auto &cell : dof_handler.active_cell_iterators()) {
				fe_values.reinit(cell);

				cell_matrix = 0;
				cell_rhs = 0;

				for (const unsigned int q_index : fe_values.quadrature_point_indices()) {
					for (const unsigned int i : fe_values.dof_indices()) {
						for (const unsigned int j : fe_values.dof_indices()) {
							cell_matrix(i, j) += (
								fe_values.shape_grad(i, q_index) *
								fe_values.shape_grad(j, q_index) *
								fe_values.JxW(q_index)
							);
						}
					}
				}

				cell->get_dof_indices(local_dof_indices);

				for (const unsigned int i : fe_values.dof_indices()) {
					for (const unsigned int j : fe_values.dof_indices()) {
						system_matrix.add(
							local_dof_indices[i],
							local_dof_indices[j],
							cell_matrix(i, j)
						);
					}
				}
			}
		}

		void apply_boundary_conditions() {
			std::map<types::global_dof_index, double> boundary_values;
			VectorTools::interpolate_boundary_values(
				dof_handler,
				types::boundary_id(0),
				Functions::ConstantFunction<dim>(69),
				boundary_values
			);

			// this uses the solution! Maybe it already writes the
			// constrained dofs inside the solution
			MatrixTools::apply_boundary_values(
				boundary_values,
				system_matrix,
				solution,
				system_rhs
			);
		}

		void dump_state(const std::string& generation) {
			{
				std::ofstream out("A_" + generation + ".txt");
				system_matrix.print(out);
			}
			{
				std::ofstream out("b_" + generation + ".txt");
				system_rhs.print(out);
			}
			{
				std::ofstream out("sol_" + generation + ".txt");
				solution.print(out);
			}
		}

	private:
		Triangulation<dim> mesh;
		const FE_Q<dim>    fe;
		DoFHandler<dim>    dof_handler;

		SparsityPattern      sparsity_pattern;
		SparseMatrix<double> system_matrix;
		Vector<double>       system_rhs;
		Vector<double>       solution;
};


int main(void) {
	SparseMatrix<double> A;
	Vector<double> rhs;
	Vector<double> solution;

	Poisson<2> problem(5);
	problem.dump_state("init");

	problem.assemble();
	problem.dump_state("after_assembly");

	problem.apply_boundary_conditions();
	problem.dump_state("after_boundary_conditions");

	return 0;
}

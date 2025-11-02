#include "quasim_core.h"
#include <iostream>

int main() {
    std::cout << "QuASIM Master Demo (Phases I-XII)" << std::endl;
    std::cout << "==================================" << std::endl;
    
    quasim::TensorSolver solver;
    int iterations = solver.solve(100);
    double residual = solver.get_residual();
    
    std::cout << "TensorSolver completed in " << iterations << " iterations" << std::endl;
    std::cout << "Final residual: " << residual << std::endl;
    std::cout << "Status: " << (residual < 1e-6 ? "CONVERGED" : "NOT CONVERGED") << std::endl;
    
    return 0;
}

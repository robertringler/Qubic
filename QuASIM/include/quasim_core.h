#ifndef QUASIM_CORE_H
#define QUASIM_CORE_H

namespace quasim {

class TensorSolver {
public:
    TensorSolver();
    ~TensorSolver();
    
    int solve(int max_iterations);
    double get_residual() const;
    
private:
    double residual_;
};

} // namespace quasim

#endif // QUASIM_CORE_H

/**
 * QuASIM Abaqus UMAT - User Material Subroutine
 * 
 * UMAT/UEL-style hook that offloads constitutive updates to QuASIM
 * material micro-solver (JAX or CUDA path).
 * 
 * Compilation:
 *   abaqus make library=quasim_umat.for
 * 
 * Usage:
 *   *Material, name=QuASIM_Material
 *   *User Material, constants=3
 *   <material parameters>
 */

#include <cmath>
#include <cstdio>

// Abaqus UMAT interface (Fortran calling convention)
extern "C" {

void umat_(
    double* stress,      // Stress tensor
    double* statev,      // State variables
    double* ddsdde,      // Tangent stiffness matrix
    double* sse,         // Specific strain energy
    double* spd,         // Specific plastic dissipation
    double* scd,         // Specific creep dissipation
    double* rpl,         // Volumetric heat generation
    double* ddsddt,      // Stress/temp derivative
    double* drplde,      // Heat gen/strain derivative
    double* drpldt,      // Heat gen/temp derivative
    double* stran,       // Strain tensor at t
    double* dstran,      // Strain increment
    double* time,        // Step and total time
    double* dtime,       // Time increment
    double* temp,        // Temperature at t
    double* dtemp,       // Temperature increment
    double* predef,      // Predefined field variables
    double* dpred,       // Predefined field increments
    char*   cmname,      // Material name
    int*    ndi,         // Direct stress components
    int*    nshr,        // Shear stress components
    int*    ntens,       // Total stress components
    int*    nstatv,      // State variable count
    double* props,       // Material properties
    int*    nprops,      // Property count
    double* coords,      // Integration point coords
    double* drot,        // Rotation increment matrix
    double* pnewdt,      // Time step multiplier
    double* celent,      // Characteristic element length
    double* dfgrd0,      // Deformation gradient at t
    double* dfgrd1,      // Deformation gradient at t+dt
    int*    noel,        // Element number
    int*    npt,         // Integration point
    int*    layer,       // Layer number (composites)
    int*    kspt,        // Section point
    int*    kstep,       // Step number
    int*    kinc         // Increment number
) {
    // QuASIM UMAT implementation
    // In production, would invoke QuASIM material micro-solver
    
    printf("QuASIM UMAT: Element %d, Point %d\n", *noel, *npt);
    
    // Simple linear elastic response for demonstration
    double E = props[0];  // Young's modulus
    double nu = props[1]; // Poisson's ratio
    
    double lambda = E * nu / ((1.0 + nu) * (1.0 - 2.0 * nu));
    double mu = E / (2.0 * (1.0 + nu));
    
    // Update stress (simplified)
    for (int i = 0; i < *ntens; ++i) {
        stress[i] += 2.0 * mu * dstran[i];
    }
    
    // Update tangent stiffness (simplified)
    for (int i = 0; i < *ndi; ++i) {
        for (int j = 0; j < *ndi; ++j) {
            ddsdde[i * (*ntens) + j] = lambda;
        }
        ddsdde[i * (*ntens) + i] += 2.0 * mu;
    }
    
    for (int i = *ndi; i < *ntens; ++i) {
        ddsdde[i * (*ntens) + i] = mu;
    }
}

} // extern "C"

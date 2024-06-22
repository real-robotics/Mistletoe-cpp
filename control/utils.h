#include <cmath>
#include <Eigen/Dense>

using namespace Eigen;
using namespace std;

Matrix calculate_jacobian(double l1, double l2, double theta_1, double theta_2, double theta_3, double x_offset, double *out_2505264937674718270) {
    Matrix<double, 3, 3> J;

    J(0,0) = (pow(l1, 2)*sin(theta_1)*cos(theta_1) + l1*l2*sin(theta_1)*cos(theta_1 + theta_2) + l1*l2*sin(theta_1 + theta_2)*cos(theta_1) + pow(l2, 2)*sin(theta_1 + theta_2)*cos(theta_1 + theta_2))*sin(theta_3)*cos(theta_3)/sqrt(pow(l1, 2)*pow(sin(theta_1), 2) + 2*l1*l2*sin(theta_1)*sin(theta_1 + theta_2) + pow(l2, 2)*pow(sin(theta_1 + theta_2), 2) + pow(x_offset, 2));
    J(0,1) = (l1*l2*sin(theta_1)*cos(theta_1 + theta_2) + pow(l2, 2)*sin(theta_1 + theta_2)*cos(theta_1 + theta_2))*sin(theta_3)*cos(theta_3)/sqrt(pow(l1, 2)*pow(sin(theta_1), 2) + 2*l1*l2*sin(theta_1)*sin(theta_1 + theta_2) + pow(l2, 2)*pow(sin(theta_1 + theta_2), 2) + pow(x_offset, 2));
    J(0,2) = -sqrt(pow(l1, 2)*pow(sin(theta_1), 2) + 2*l1*l2*sin(theta_1)*sin(theta_1 + theta_2) + pow(l2, 2)*pow(sin(theta_1 + theta_2), 2) + pow(x_offset, 2))*pow(sin(theta_3), 2) + sqrt(pow(l1, 2)*pow(sin(theta_1), 2) + 2*l1*l2*sin(theta_1)*sin(theta_1 + theta_2) + pow(l2, 2)*pow(sin(theta_1 + theta_2), 2) + pow(x_offset, 2))*pow(cos(theta_3), 2);
    J(1,0) = -l1*sin(theta_1) - l2*sin(theta_1 + theta_2);
    J(1,1) = -l2*sin(theta_1 + theta_2);
    J(1,2) = 0;
    J(2,0) = (pow(l1, 2)*sin(theta_1)*cos(theta_1) + l1*l2*sin(theta_1)*cos(theta_1 + theta_2) + l1*l2*sin(theta_1 + theta_2)*cos(theta_1) + pow(l2, 2)*sin(theta_1 + theta_2)*cos(theta_1 + theta_2))*sin(theta_3)/sqrt(pow(l1, 2)*pow(sin(theta_1), 2) + 2*l1*l2*sin(theta_1)*sin(theta_1 + theta_2) + pow(l2, 2)*pow(sin(theta_1 + theta_2), 2) + pow(x_offset, 2));
    J(2,1) = (l1*l2*sin(theta_1)*cos(theta_1 + theta_2) + pow(l2, 2)*sin(theta_1 + theta_2)*cos(theta_1 + theta_2))*sin(theta_3)/sqrt(pow(l1, 2)*pow(sin(theta_1), 2) + 2*l1*l2*sin(theta_1)*sin(theta_1 + theta_2) + pow(l2, 2)*pow(sin(theta_1 + theta_2), 2) + pow(x_offset, 2));
    J(2,2) = sqrt(pow(l1, 2)*pow(sin(theta_1), 2) + 2*l1*l2*sin(theta_1)*sin(theta_1 + theta_2) + pow(l2, 2)*pow(sin(theta_1 + theta_2), 2) + pow(x_offset, 2))*cos(theta_3);

    return J;
}
#include <iostream>
#include <random>
#include <limits>
#include <stdlib.h>
#include <mpi.h>

#define POINTS_PER_CPU 100

class Point {
    double x, y, z;
public:
    Point(double x = 0, double y = 0, double z = 0):
        x(x), y(y), z(z)
        {}
    
    Point(double vars[3]):
        x(vars[0]), y(vars[1]), z(vars[2])
        {}

    Point(std::uniform_real_distribution<> &dis,  std::mt19937 &gen) {
        x = dis(gen);
        y = dis(gen);
        z = dis(gen);
    }

    double operator[](int index) {
        if (index == 0) return x;
        else if (index == 1) return y;
        else if (index == 2) return z;
        else return 0;
    }

};

int size, rank;

double func(Point point) {
    return point[0] * point[0] * point[0] *
           point[1] * point[1] * point[2];
}

std::pair<double, int64_t>  monte_carlo(std::mt19937 &gen, std::uniform_real_distribution<> &dis, 
        double eps, double solution, double volume, double (*func)(Point)) {
    double integ = 0.0;
    double err = std::abs(integ - solution);
    double global_sum = 0.0;
    int64_t point_counter = 0;

    while (err > eps) {
        double local_sum = 0;//global_sum;
        
        for (int i = 0; i < POINTS_PER_CPU; i++) {
            local_sum += func(Point(dis, gen));
        }
        
        double now_sum = 0.0;
        MPI_Allreduce(&local_sum, &now_sum, 1, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
        global_sum += now_sum;
        
        point_counter += POINTS_PER_CPU * size;
        integ = volume * global_sum / (point_counter + 0.0);
        err = std::abs(integ - solution);
    
    }

    return {integ, point_counter}; 
}

int main(int argc, char *argv[]) {
    std::random_device rd;  // Will be used to obtain a seed for the random number engine

    auto seed = rd();

    double solution = 1.0 / 24.0;
    double volume = 1.0;
    if (argc < 2) {
        std::cerr << "Wrong args count <eps> <seed (optional)>" << std::endl;
        return 0;
    }
    double eps = std::atof(argv[1]);
    if (argc > 2) {
        seed = std::atoi(argv[2]);
    }
    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    std::mt19937 gen(seed + rank); // Standard mersenne_twister_engine seeded with rd()
    std::uniform_real_distribution<> dis(-1.0, 0.0);

    double start_time = MPI_Wtime();

    std::pair<double, int64_t> ans = monte_carlo(gen, dis, eps, solution, volume, func);
    double el_time = MPI_Wtime() - start_time;

    double value = ans.first;
    int64_t counter = ans.second;
    if (rank == 0) {
        std::cout.precision(std::numeric_limits<double>::max_digits10);
        std::cout << "Solution   error:  : " << std::abs(solution - value) << std::endl;
        std::cout << "Compute    solution: " << value << std::endl;
        std::cout << "Points     elapsed:  " << counter << std::endl;
        std::cout << "Time       elapsed:  " << el_time << "sec." << std::endl;
        std::cout << "Time per point elap: " << el_time / counter << "sec." << std::endl;
    }
    MPI_Finalize();
}

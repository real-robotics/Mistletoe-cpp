#include <vector>
#include <iostream>
#include <chrono>
#include <thread>
#include <signal.h>
#include <atomic> // For atomic flags

#include <lcm/lcm-cpp.hpp>
#include "exlcm/quad_command_t.hpp"
#include "exlcm/quad_state_t.hpp"
#include "exlcm/enabled_t.hpp"

#include <Eigen/Dense>
#include "utils.hpp"

#include "moteus.h"
#include "pi3hat_moteus_transport.h"

using namespace mjbots;

#define NUM_MOTORS 12

const int IDS[] = {
    11, 12, 13, // front left
    21, 22, 23, // front right
    31, 32, 33, // back left
    41, 42, 43  // back right
};

std::vector<moteus::Controller> controllers;

// Global flag to signal exit
std::atomic<bool> exit_requested(false);

class LCMHandler {
  public:
    bool enabled = false;
    double commanded_position[12] = {0};

    LCMHandler() {
        enabled = false;
    }

    void handleControlCommand(const lcm::ReceiveBuffer *rbuf, const std::string &chan,
                       const exlcm::quad_command_t *msg)
    {
        if (enabled) {
            std::cout << "Received Message on Channel: " << chan << std::endl;
            std::cout << "    timestamp = " << msg->timestamp << std::endl;
            std::copy(msg->position, msg->position + 12, commanded_position);
        }
    }

    void handleEnable(const lcm::ReceiveBuffer *rbuf, const std::string &chan,
                       const exlcm::enabled_t *msg)
    {
        enabled = msg->enabled;
        std::cout << "Current enabled status:" << enabled << std::endl;
    }
};

void handle_lcm(lcm::LCM *lcm) {
    while (!exit_requested) {
        lcm->handleTimeout(100);
    }
}

void handle_exit(int s) {
    std::cout << "Exit signal received. Stopping motors and waiting for main loop to finish..." << std::endl;
    exit_requested = true; // Set the flag
}

void setup_signal_handler() {
    struct sigaction sigIntHandler;

    sigIntHandler.sa_handler = handle_exit;
    sigemptyset(&sigIntHandler.sa_mask);
    sigIntHandler.sa_flags = 0;

    sigaction(SIGINT, &sigIntHandler, nullptr);
    // sigaction(SIGTERM, &sigIntHandler, nullptr);
    sigaction(SIGABRT, &sigIntHandler, nullptr);
    // sigaction(SIGFPE, &sigIntHandler, nullptr);
    // sigaction(SIGILL, &sigIntHandler, nullptr);
    // sigaction(SIGSEGV, &sigIntHandler, nullptr);
}

int main(int argc, char** argv) {
    // MOTEUS Initialization
    mjbots::pi3hat::Pi3HatMoteusFactory::Register();
    moteus::Controller::DefaultArgProcess(argc, argv);

    for (int i = 0; i < NUM_MOTORS; i++) {
        int id = IDS[i];
        moteus::Controller::Options options;
        options.id = id;
        std::cout << "controller " << id << std::endl;
        moteus::Query::Format query_format;
        query_format.voltage = moteus::Resolution::kFloat;
        options.query_format = query_format;

        controllers.push_back(moteus::Controller(options));
    }

    // Set up signal handler
    setup_signal_handler();

    // Stop all motors initially
    for (moteus::Controller controller : controllers) {
        controller.SetStop();
    }

    // LCM Initialization with config to ensure packets published will enter local network
    lcm::LCM *lcm = new lcm::LCM("udpm://239.255.77.67:7667?ttl=1");

    if (!lcm->good())
        return 1;

    LCMHandler lcmHandler;
    lcm->subscribe("COMMAND", &LCMHandler::handleControlCommand, &lcmHandler);
    lcm->subscribe("ENABLED", &LCMHandler::handleEnable, &lcmHandler);

    // Launch LCM handler thread
    std::thread lcm_thread(handle_lcm, lcm);

    exlcm::quad_state_t state = {
        .timestamp = std::chrono::system_clock::now().time_since_epoch().count()
    };

    while (!exit_requested) { // Main loop continues until exit is requested
        for (int i = 0; i < NUM_MOTORS; i++) {
            moteus::Controller controller = controllers.at(i);
            auto maybe_state = controller.SetQuery();
            double position = -1;
            double velocity = -1;
            double torque = -1;
            double bus_voltage = -1;
            if (maybe_state) {
                moteus::Query::Result state;
                state = maybe_state->values;
                position = state.position;
                velocity = state.velocity;
                bus_voltage = state.voltage;
            }
            state.position[i] = position;
            state.velocity[i] = velocity;

            state.timestamp = std::chrono::system_clock::now().time_since_epoch().count();

            // TODO: make real
            if (i == 0) {
                state.bus_voltage = bus_voltage;
            }
        }

        double commanded_position = lcmHandler.commanded_position[2];
        moteus::PositionMode::Command position_cmd;
        position_cmd.position = commanded_position;
        position_cmd.velocity = 0;
        position_cmd.velocity_limit = 0.5;
        position_cmd.accel_limit = 2; 
        controllers.at(2).SetPosition(position_cmd);


        // Publish the state over LCM
        lcm->publish("STATE_C2C", &state);

        usleep(10000); // sleep for 10ms
    }

    // Clean up after main loop exits
    std::cout << "Stopping all motors." << std::endl;
    for (moteus::Controller controller : controllers) {
        controller.SetStop();
    }

    // Ensure LCM handler thread finishes before exiting
    std::cout << "Waiting for LCM handler thread to finish." << std::endl;
    lcm_thread.join();

    std::cout << "Exiting program." << std::endl;
    return 0;
}

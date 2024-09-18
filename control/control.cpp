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

const int NUM_SERVOS = 12;
const int NUM_SERVOS_PER_BUS = 3;
const int NUM_BUSSES = 4;

const int IDS[] = {
    11, 12, 13, // front left
    21, 22, 23, // front right
    31, 32, 33, // back left
    41, 42, 43  // back right
};

const int NUM_JOINTS = 12;

// position limits are set within the moteus configs as well, but these are here just in case. 
const std::array<std::array<float, 2>, NUM_JOINTS> joint_limits = {
    std::array<float, 2>{-0.15f, 0.15f},  // Joint 11
    std::array<float, 2>{-0.5f, 0.5f},    // Joint 12
    std::array<float, 2>{-0.5f, 0.5f},    // Joint 13
    std::array<float, 2>{-0.15f, 0.15f},  // Joint 21
    std::array<float, 2>{-0.5f, 0.5f},    // Joint 22
    std::array<float, 2>{-0.5f, 0.5f},    // Joint 23
    std::array<float, 2>{-0.15f, 0.15f},  // Joint 31
    std::array<float, 2>{-0.5f, 0.5f},    // Joint 32
    std::array<float, 2>{-0.5f, 0.5f},    // Joint 33
    std::array<float, 2>{-0.15f, 0.15f},  // Joint 41
    std::array<float, 2>{-0.5f, 0.5f},    // Joint 42
    std::array<float, 2>{-0.5f, 0.5f}     // Joint 43
};

bool is_within_joint_limit(int joint_index, float value) {
    // Check if the joint index is valid
    if (joint_index < 0 || joint_index >= NUM_JOINTS) {
        std::cerr << "Invalid joint index: " << joint_index << std::endl;
        return false;
    }

    // Get the joint limit for the corresponding index
    const auto& limit = joint_limits[joint_index];

    // Check if the value is within the joint limit range
    return (value >= limit[0] && value <= limit[1]);
}

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
        bool all_joints_within_limit = true;
        // std::cout << "Received Message on Channel: " << chan << std::endl;
        // std::cout << "    timestamp = " << msg->timestamp << std::endl;

        // TODO: sub with near max/min for joints that go over? or retrain rl model to have heavy penalties when commands are above thresholds. 

        for (int i = 0; i < 12; i++) {
            if (!is_within_joint_limit(i, msg->position[i])) {
                std::cout << "position on joint " << i << " not within bounds." << std::endl;
                std::cout << "position on joint " << i << msg->position[i] << std::endl;
                all_joints_within_limit = false;
            }
        }

        // there are numerous software software checks on position limits, so this is just in case somewhere else screws up somehow.
        if (all_joints_within_limit) {
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
    std::cout << "Exit signal received. Stopping servos and waiting for main loop to finish..." << std::endl;
    exit_requested = true; // Set the flag
}

void setup_signal_handler() {
    struct sigaction sigIntHandler;

    sigIntHandler.sa_handler = handle_exit;
    sigemptyset(&sigIntHandler.sa_mask);
    sigIntHandler.sa_flags = 0;

    sigaction(SIGINT, &sigIntHandler, nullptr);
    sigaction(SIGTERM, &sigIntHandler, nullptr);
    sigaction(SIGABRT, &sigIntHandler, nullptr);
    // sigaction(SIGFPE, &sigIntHandler, nullptr);
    // sigaction(SIGILL, &sigIntHandler, nullptr);
    // sigaction(SIGSEGV, &sigIntHandler, nullptr);
}

int main(int argc, char** argv) {
    // MOTEUS Initialization

    // construct transport with correct servo map
    pi3hat::Pi3HatMoteusTransport::Options pi3hat_options;
    std::map<int, int> servo_map;

    servo_map.insert({11,1});
    servo_map.insert({12,1});
    servo_map.insert({13,1});
    
    servo_map.insert({21,2});
    servo_map.insert({22,2});
    servo_map.insert({23,2});

    servo_map.insert({31,3});
    servo_map.insert({32,3});
    servo_map.insert({33,3});
    
    servo_map.insert({41,4});
    servo_map.insert({42,4});
    servo_map.insert({43,4});
    
    pi3hat_options.servo_map = servo_map;
    auto transport = std::make_shared<pi3hat::Pi3HatMoteusTransport>(pi3hat_options);

    std::map<int, std::shared_ptr<moteus::Controller>> controllers;
    std::map<int, moteus::Query::Result> servo_data;

    int servo_count = 0;

    for (int bus = 1; bus <= 4; bus++) {
        for (int i = 1; i <= 3; i++) {
            // controller ids have the format of [bus number][controller # on bus] ie. 31
            int id = bus * 10 + i;
            std::cout << "controller " << id << " initialized." << std::endl;
            moteus::Controller::Options options;
            moteus::Query::Format query_format;
            query_format.voltage = moteus::Resolution::kFloat;
            options.query_format = query_format;
            options.bus = bus;
            options.id = id;
            options.transport = transport;
            controllers[servo_count] = std::make_shared<moteus::Controller>(options);
            servo_count++;
        }
    }

    // Set up signal handler
    setup_signal_handler();

    // Stop all servos initially
    for (const auto& pair : controllers) {
        pair.second->SetStop();
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

    bool controllers_stopped = true;
    
    std::cout << "Main Loop Started" << std::endl;
    int step = 0;

    bool first_pos = true;

    auto start = std::chrono::high_resolution_clock::now();

    while (!exit_requested) { // Main loop continues until exit is requested

        std::vector<moteus::CanFdFrame> command_frames;

        // stop controllers if robot is disabled
        if (!lcmHandler.enabled && !controllers_stopped) {

            std::cout << "Controllers stopped." << std::endl;

            std::vector<moteus::CanFdFrame> replies;

            // Accumulate all of our command CAN frames.
            for (const auto& pair : controllers) {
                command_frames.push_back(pair.second->MakeStop());
            }
  
            transport->BlockingCycle(&command_frames[0], command_frames.size(), &replies);

            controllers_stopped = true;

            for (const auto& frame : replies) {
                servo_data[frame.source] = moteus::Query::Parse(frame.data, frame.size);
            }

            int i = 0;

            for (const auto& pair : servo_data) {
                const auto r = pair.second;
                state.position[i] = r.position;
                state.velocity[i] = r.velocity;
                state.bus_voltage = r.voltage;
                state.timestamp = std::chrono::system_clock::now().time_since_epoch().count();
                i++;
            }
        }

        // still query info when disabled

        if (!lcmHandler.enabled) {
            // Accumulate all of our command CAN frames.
            for (const auto& pair : controllers) {
                command_frames.push_back(pair.second->MakeQuery());
            }

            // std::cout << "queried controller" << std::endl;
            
        } else {
            // Accumulate all of our command CAN frames.

            for (const auto& pair : controllers) {
                command_frames.push_back(pair.second->MakeQuery());
            }

            // std::cout << "Position command sent" << std::endl;
            int j = 0;
            for (const auto& pair : controllers) {
                moteus::PositionMode::Command position_command;
                position_command.position = lcmHandler.commanded_position[j];
                position_command.velocity = 0;
                position_command.velocity_limit = 0.5;
                position_command.accel_limit = 2; 
                command_frames.push_back(pair.second->MakePosition(position_command));
                j++;
            }
            if (first_pos == true) {
                start = std::chrono::high_resolution_clock::now();
                first_pos = false;
            }

            // controllers are no longer stopped when position commanded
            controllers_stopped = false;
        }

        std::vector<moteus::CanFdFrame> replies;

        transport->BlockingCycle(&command_frames[0], command_frames.size(), &replies);

        // We parse these into a map to both sort and de-duplicate them,
        // and persist data in the event that any are missing.
        for (const auto& frame : replies) {
            servo_data[frame.source] = moteus::Query::Parse(frame.data, frame.size);
        }

        int i = 0;

        for (const auto& pair : servo_data) {
            const auto r = pair.second;
            state.position[i] = r.position;
            state.velocity[i] = r.velocity;
            state.bus_voltage = r.voltage;
            // std::cout << "Voltage on controller "  << i << " : " << r.voltage << std::endl;
            state.fault_code = r.fault;

            int mode = static_cast<int>(r.mode);
            int fault = static_cast<int>(r.fault);
            if (fault > 0) {
                std::cout << "detected fault on controller " << i << " fault " << fault << std::endl;
            }
            if (mode > 10) {
                std::cout << "detected mode on controller " << i << " mode " << mode << std::endl;
            }
            state.timestamp = std::chrono::system_clock::now().time_since_epoch().count();
            i++;
        }

        // Publish the state over LCM
        lcm->publish("STATE_C2C", &state);

        usleep(10000); // sleep for 10ms
    }

    // Clean up after main loop exits
    std::cout << "Stopping all servos." << std::endl;
    std::vector<moteus::CanFdFrame> stop_command_frames;
    std::vector<moteus::CanFdFrame> replies;

    // Accumulate all of our command CAN frames.
    for (const auto& pair : controllers) {
        stop_command_frames.push_back(pair.second->MakeStop());
    }

    transport->BlockingCycle(&stop_command_frames[0], stop_command_frames.size(), &replies);

    // Ensure LCM handler thread finishes before exiting
    std::cout << "Waiting for LCM handler thread to finish." << std::endl;
    lcm_thread.join();

    std::cout << "Exiting program." << std::endl;
    return 0;
}

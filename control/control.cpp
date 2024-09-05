// TODO: update bus voltage

#include <vector>
#include <iostream>
#include <chrono>
#include <thread>
#include <signal.h>

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
// units in m and N and N-m

// TODO: Use real values from the CAD

const double l1 = 3;
const double l2 = 3;
const double x_offset = 3;

const double contact_force_threshold = 1;


std::vector<moteus::Controller> controllers;

class Handler {
  public:
    bool enabled = false;

    Handler() {
        enabled = false;
    }
    void handleControlCommand(const lcm::ReceiveBuffer *rbuf, const std::string &chan,
                       const exlcm::quad_command_t *msg)
    {
        std::cout << enabled;
        if (enabled == true) {
            std::cout << "Received Message on Channel: " << chan << std::endl;
            std::cout << "    timestamp = " << msg->timestamp << std::endl;
            // for (int i = 0; i < NUM_MOTORS; i++) {
            //     double position = msg->position[i];
            //     moteus::PositionMode::Command position_cmd;
            //     position_cmd.position = position;
            //     position_cmd.velocity = 0;
            //     controllers.at(i).SetPosition(position_cmd);
            // }

            int i = 2;
            std::cout << IDS[i];

            // double position = msg->position[i];
            // moteus::PositionMode::Command position_cmd;
            // position_cmd.position = position;
            // position_cmd.velocity = 0;
            // position_cmd.velocity_limit = 0.5;
            // position_cmd.accel_limit = 2; 
            // controllers.at(i).SetPosition(position_cmd);
            
            std::cout << std::endl;
        }
    }

    void handleEnable(const lcm::ReceiveBuffer *rbuf, const std::string &chan,
                       const exlcm::enabled_t *msg)
    {
        std::cout << "Received Message on Channel: " << chan << std::endl;

        // TODO: msg.enabled status is not printed (only the string part)
        std::cout << "Current enabled status:" << msg->enabled << std::endl;

        enabled = msg->enabled;
    }
};

void handle_lcm(lcm::LCM *lcm) {
    while (true) {
        lcm->handle();
    }
}

void handle_exit(int s) {
    std::cout << "Stopping all motors." << std::endl;
    // TODO: change to use moteus tool stop all
    for (moteus::Controller controller : controllers) {
        controller.SetStop();
    }
    std::cout << "Exiting program with code " << s << std::endl;
    exit(s);
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

        controllers.push_back(
            moteus::Controller(options)
        );
    }

    // Make sure that all motors stop when the program is killed
    // TODO: change to use sigactions instead
    signal(SIGINT, handle_exit);

    // Make sure motors stop for other types of exits
    // signal(SIGABRT, handle_exit);
    signal(SIGFPE, handle_exit);
    signal(SIGILL, handle_exit);
    signal(SIGSEGV, handle_exit);
    // signal(SIGTERM, handle_exit);

    for (moteus::Controller controller : controllers) {
        controller.SetStop();
    }

    // LCM Initialization with config to ensure packets published will enter local network

    lcm::LCM *lcm = new lcm::LCM(
        "udpm://239.255.77.67:7667?ttl=1"
        );

    if (!lcm->good())
        return 1;

    Handler handlerObject;
    lcm->subscribe("COMMAND", &Handler::handleControlCommand, &handlerObject);
    lcm->subscribe("ENABLED", &Handler::handleEnable, &handlerObject);

    std::thread thread(handle_lcm, lcm);
    thread.detach();


    exlcm::quad_state_t state = {
        .timestamp = std::chrono::system_clock::now().time_since_epoch().count()
    };

    // commented out because contact is currently not needed for the observation space of the policy

    // std::vector<double> joint_torques;
    // std::vector<double> joint_positions;

    while (true) {
        // joint_torques.clear();

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

            // TODO: make real
            if (i == 0) {
                state.bus_voltage = bus_voltage; 
            }
            state.timestamp = std::chrono::system_clock::now().time_since_epoch().count();
            
            // joint_torques.push_back(torque);
        }
      
        // std::vector<bool> contacts = detect_contact(
        //     l1, l2, x_offset, joint_positions, joint_torques, contact_force_threshold 
        // );

        // // copy over the values of contacts into the lcm state array
        // std::copy(contacts.begin(), contacts.end(), state.contacts)

        // update the state
        lcm->publish("STATE_C2C", &state);

        usleep(10000); // sleep for 10ms
    }

    thread.join();

    return 0;
}

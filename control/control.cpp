#include <vector>
#include <iostream>
#include <chrono>
#include <thread>

#include <lcm/lcm-cpp.hpp>
#include "exlcm/quad_command_t.hpp"
#include "exlcm/quad_state_t.hpp"

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

class Handler {
  public:
    ~Handler() {}
    void handleMessage(const lcm::ReceiveBuffer *rbuf, const std::string &chan,
                       const exlcm::quad_command_t *msg)
    {
        std::cout << "Received Message on Channel: " << chan << std::endl;
        std::cout << "    timestamp = " << msg->timestamp << std::endl;
        
        // for (int i = 0; i < NUM_MOTORS; i++) {
        //     double position = msg->position[i];
        //     moteus::PositionMode::Command position_cmd;
        //     position_cmd.position = position;
        //     position_cmd.velocity = 0;
        //     controllers.at(i).SetPosition(position_cmd);
        // }
        
        std::cout << std::endl;
    }
};

void handle_lcm(lcm::LCM *lcm) {
    while (true) {
        lcm->handle();
    }
}

int main(int argc, char** argv) {
    // MOTEUS Initialization

    mjbots::pi3hat::Pi3HatMoteusFactory::Register();

    moteus::Controller::DefaultArgProcess(argc, argv);


    for (int i = 0; i < NUM_MOTORS; i++) {
        int id = IDS[i];

        moteus::Controller::Options options;
        options.id = id;

        controllers.push_back(
            moteus::Controller(options)
        );
    }

    for (moteus::Controller controller : controllers) {
        controller.SetStop();
    }

    // LCM Initialization

    lcm::LCM *lcm = new lcm::LCM();

    if (!lcm->good())
        return 1;

    Handler handlerObject;
    lcm->subscribe("COMMAND", &Handler::handleMessage, &handlerObject);

    std::thread thread(handle_lcm, lcm);
    thread.detach();

    exlcm::quad_state_t state = {
        .timestamp = std::chrono::system_clock::now().time_since_epoch().count()
    };

    while (true) {
        for (int i = 0; i < NUM_MOTORS; i++) {
            moteus::Controller controller = controllers.at(i);
            auto maybe_state = controller.SetQuery();
            double position = -1;
            double velocity = -1;
            if (maybe_state) {
                moteus::Query::Result state;
                state = maybe_state->values;
                position = state.position;
                velocity = state.velocity;
            }
            state.position[i] = position;
            state.velocity[i] = velocity;
        }

        // update the state
        lcm->publish("STATE", &state);

        usleep(10000); // sleep for 10ms
    }

    thread.join();

    return 0;
}

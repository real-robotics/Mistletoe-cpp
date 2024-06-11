#include <stdio.h>
#include <unistd.h>
#include <iostream>
#include <chrono>

#include <lcm/lcm-cpp.hpp>

#include "exlcm/quad_command_t.hpp"
#include "exlcm/quad_state_t.hpp"

#include <thread>

class Handler {
  public:
    ~Handler() {}
    void handleMessage(const lcm::ReceiveBuffer *rbuf, const std::string &chan,
                       const exlcm::quad_command_t *msg)
    {
        int i;
        printf("Received message on channel \"%s\":\n", chan.c_str());
        printf("  timestamp   = %lld\n", (long long) msg->timestamp);

        std::cout << "Position: ";
        for (int i = 0; i < 12; i++) {
            std::cout << msg->position[i];
            if (i != 11) std::cout << ", ";
        }
        std::cout << std::endl;
    }
};

void handle_lcm(lcm::LCM *lcm) {
    while (true) {
        lcm->handle();
    }
}

int main(int argc, char **argv)
{
    lcm::LCM *lcm = new lcm::LCM();

    if (!lcm->good())
        return 1;

    Handler handlerObject;
    lcm->subscribe("COMMAND", &Handler::handleMessage, &handlerObject);

    std::thread thread(handle_lcm, lcm);
    thread.detach();

    while (true) {
        exlcm::quad_state_t fake_state = {
            .timestamp = std::chrono::system_clock::now().time_since_epoch().count(),
            .position = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12}
        };

        // update the state
        lcm->publish("STATE", &fake_state);

        usleep(250000); // sleep for 250ms
    }

    thread.join();

    return 0;
}

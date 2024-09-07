#include <vector>
#include <iostream>
#include <chrono>

#include "moteus.h"
#include "pi3hat_moteus_transport.h"
#include "pi3hat.h"

using namespace mjbots;

std::vector<moteus::Controller> controllers;

int main(int argc, char** argv) {

    // construct transport with correct servo map
    pi3hat::Pi3HatMoteusTransport::Options pi3hat_options;
    std::map<int, int> servo_map;
    servo_map.insert({13,1});
    pi3hat_options.servo_map = servo_map;
    auto transport = std::make_shared<pi3hat::Pi3HatMoteusTransport>(pi3hat_options);

    std::map<int, std::shared_ptr<moteus::Controller>> controllers;
    std::map<int, moteus::Query::Result> servo_data;

    // controller ids have the format of [bus number][controller # on bus] ie. 31
    int id = 13;
    moteus::Controller::Options options;

    // higher voltage res
    moteus::Query::Format query_format;
    query_format.voltage = moteus::Resolution::kFloat;
    options.query_format = query_format;
    options.id = 13;
    options.bus = 1;
    options.transport = transport;
    controllers[0] = std::make_shared<moteus::Controller>(options);

    // Stop all servos initially
    for (const auto& pair : controllers) {
        pair.second->SetStop();
    }
    
    while (true) { 

        std::vector<moteus::CanFdFrame> command_frames;

        // Accumulate all of our command CAN frames.
        for (const auto& pair : controllers) {
            moteus::PositionMode::Command position_command;
            position_command.position = 0;
            position_command.velocity = 0;
            position_command.velocity_limit = 0.5;
            position_command.accel_limit = 2; 
            command_frames.push_back(pair.second->MakePosition(position_command));
        }
        std::vector<moteus::CanFdFrame> replies;

        transport->BlockingCycle(&command_frames[0], command_frames.size(), &replies);

        // We parse these into a map to both sort and de-duplicate them,
        // and persist data in the event that any are missing.
        for (const auto& frame : replies) {
            servo_data[frame.source] = moteus::Query::Parse(frame.data, frame.size);
            std::cout << "data parsed" << std::endl;
        }

        int i = 0;

        for (const auto& pair : servo_data) {
            const auto r = pair.second;
            std::cout << i << std::endl;
            std::cout << r.position << std::endl;
            std::cout << r.velocity << std::endl;
            std::cout << r.voltage << std::endl;
            
            i++;
        }

        // Publish the state over LCM
        usleep(10000); // sleep for 10ms
    }
}

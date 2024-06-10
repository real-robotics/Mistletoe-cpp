// file: send_message.cpp
//
// LCM example program.
//
// compile with:
//  $ g++ -o send_message send_message.cpp -llcm
//
// On a system with pkg-config, you can also use:
//  $ g++ -o send_message send_message.cpp `pkg-config --cflags --libs lcm`

#include <lcm/lcm-cpp.hpp>

#include "exlcm/quad_command_t.hpp"
#include "exlcm/quad_state_t.hpp"

int main(int argc, char **argv)
{
    lcm::LCM lcm;
    if (!lcm.good())
        return 1;

    exlcm::quad_command_t my_data;
    my_data.timestamp = 0;

    my_data.position[0] = 1;
    my_data.position[1] = 2;
    my_data.position[2] = 3;
    my_data.position[3] = 4;
    my_data.position[4] = 5;
    my_data.position[5] = 6;
    my_data.position[6] = 7;
    my_data.position[7] = 8;
    my_data.position[8] = 9;
    my_data.position[9] = 10;
    my_data.position[10] = 11;
    my_data.position[11] = 12;

    lcm.publish("EXAMPLE", &my_data);

    return 0;
}

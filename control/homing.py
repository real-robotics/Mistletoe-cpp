#!/usr/bin/python3 -B

import asyncio
import moteus
import time
import moteus_pi3hat
import argparse
import traceback

'''
Homing procedure for quadruped. Works by assigning a small torque until the hardstops are reached.
Should be run every power cycle. 
'''

controllers = []

servo_bus_map = {
    1 : [11, 12], 
    2 : [21, 22],
    3 : [31, 32],
    4 : [41, 42]
}

can_cfg = moteus_pi3hat.CanConfiguration()
can_cfg.slow_bitrate = 1_000_000
can_cfg.fast_bitrate = 5_000_000
can_cfg.fdcan_frame = False
can_cfg.bitrate_switch = False
can_cfg.automatic_retransmission = True
can_cfg.restricted_mode = False
can_cfg.bus_monitor = False

# If buses are not listed, then they default to the parameters
# necessary to communicate with a moteus controller.
can_config = {
    1: can_cfg,
    2: can_cfg,
    3: can_cfg,
    4: can_cfg
}

# Command Transport
transport = moteus_pi3hat.Pi3HatRouter(can=can_config, servo_bus_map=servo_bus_map)
          

DEFAULT_BOUNDS = {
    11: [],
    12: [],
    13: [],

    21: [],
    22: [],
    23: [],

    31: [],
    32: [],
    33: [],

    41: [],
    42: [],
    43: [],
}

controllers = []
 
# TODO: find these values empircally

VELOCITY_TOLERANCE = 0.01 #rev/s
HOMING_VELOCITY = 0.1 #rev/s
COMMAND_TORQUE = 0.1 # Nm


async def main():
    global controllers

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--id",
        type=str,
        help="Comma-separated list of IDs to run (e.g. --id=1,3,4)",
    )
    args = parser.parse_args()

    if args.id:
        ids = [int(x) for x in args.id.split(",")]

        if ids not in DEFAULT_BOUNDS.keys():
            print("Commanding invalid ID. Please check ID conventions in documentation.")
            return

        bounds = {i: [] for i in ids}
        print(f"Setting zero for controllers: {bounds.keys()}")
    else:
        bounds = DEFAULT_BOUNDS.copy()
        print("Setting zero for controllers:", bounds.keys())

    for id in bounds.keys():
        print(f'homing controller {id}')
        asyncio.sleep(1)

        qr = moteus.QueryResolution()
        qr._extra = {
            moteus.Register.CONTROL_POSITION : moteus.F32,
            moteus.Register.CONTROL_VELOCITY : moteus.F32,
            moteus.Register.CONTROL_TORQUE : moteus.F32,
            moteus.Register.POSITION_ERROR : moteus.F32,
            moteus.Register.VELOCITY_ERROR : moteus.F32,
            moteus.Register.TORQUE_ERROR : moteus.F32,
            }

        c = moteus.Controller(id=id, transport=transport, query_resolution = qr)

        controllers.append(c)

        # Clear any faults.
        await transport.cycle([c.make_stop()])

        while True:
            position_command = c.make_position(
                position=None,
                velocity=HOMING_VELOCITY,
                accel_limit=1.0,
                velocity_limit=HOMING_VELOCITY,
                maximum_torque=COMMAND_TORQUE,
                query=True,
            )

            # grab the only result that should be returned (we only command one controller)
            result = await transport.cycle([position_command])[0]

            joint_vel = result[moteus.Register.VELOCITY]
            joint_pos = result[moteus.Register.POSITION]

            # value should be determined empircally
            if abs(joint_vel) < VELOCITY_TOLERANCE:
                print('motor stopped, recording upper limit position')
                bounds[id][0] = joint_pos
                break

            await asyncio.sleep(0.02)

        while True:
            position_command = c.make_position(
                position=None,
                velocity=-1 * HOMING_VELOCITY,
                accel_limit=1.0,
                velocity_limit=HOMING_VELOCITY,
                maximum_torque=COMMAND_TORQUE,
                query=True,
            )

            # grab the only result that should be returned (we only command one controller)
            result = await transport.cycle([position_command])[0]

            joint_vel = result[moteus.Register.VELOCITY]
            joint_pos = result[moteus.Register.POSITION]

            # value should be determined empircally
            if abs(joint_vel) < VELOCITY_TOLERANCE:
                print('motor stopped, recording lower limit position')
                bounds[id][1] = joint_pos
                zero_pos = (bounds[id][0] + bounds[id][1])/2
                
                new_current_pos = joint_pos - zero_pos
                
                # update the current position to be w.r.t the new zero point
                set_zero_command = c.make_set_output_exact(new_current_pos)

                result = await transport.cycle([set_zero_command])

                break

            await asyncio.sleep(0.02)

        print(f'Limits determined for controller {id}')

        await asyncio.sleep(0.1)

async def clean_exit():
    time.sleep(0.1)
    for controller in controllers:
        await transport.cycle([controller.make_stop()])

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as error:
        print(traceback.format_exc())
        asyncio.run(clean_exit())
    except KeyboardInterrupt:
        print('\nExit motor testing')
        asyncio.run(clean_exit())
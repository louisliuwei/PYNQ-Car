#   Copyright (c) 2019, Xilinx, Inc.
#   All rights reserved.
# 
#   Redistribution and use in source and binary forms, with or without 
#   modification, are permitted provided that the following conditions are met:
#
#   1.  Redistributions of source code must retain the above copyright notice, 
#       this list of conditions and the following disclaimer.
#
#   2.  Redistributions in binary form must reproduce the above copyright 
#       notice, this list of conditions and the following disclaimer in the 
#       documentation and/or other materials provided with the distribution.
#
#   3.  Neither the name of the copyright holder nor the names of its 
#       contributors may be used to endorse or promote products derived from 
#       this software without specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
#   THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
#   PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
#   EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
#   PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#   OR BUSINESS INTERRUPTION). HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
#   WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
#   OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
#   ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from . import Arduino
from . import MOTOR_DIRECTION
from . import TIMER
from . import MOTOR_PINS


__author__ = "zou cong"
__copyright__ = "Copyright 2019, Xilinx"


ARDUINO_AUTOMOTO_PROGRAM = "arduino_4wdmoto.bin"

CONFIG_IOP_SWITCH = 0x1
STOP = 0x3
MOVE = 0x5
DISTANCE = 0x7
PWM_CONTROL = 0x9

'''
PINS[0:4] is set the pins to control
the pwm generate io for motor a,b,c,d in sequence

 * auotmoto a: right front
 * auotmoto b: right rear
 * automoto c: left sacro-anterior / left front
 * auotmoto d: left rear
 
PINS[4:8] is to set the pin to control the direction of motor
1 normal, 0 reverse

PINS[8:12] is to set the pins to record the velocity
'''

def _reg2int(reg):
    """Converts 32-bit register value to signed integer in Python.

    Parameters
    ----------
    reg: int
        A 32-bit register value read from the mailbox.

    Returns
    -------
    int
        A signed integer translated from the register value.

    """
    result = -(reg >> 31 & 0x1) * (1 << 31)
    for i in range(31):
        result += (reg >> i & 0x1) * (1 << i)
    return result

class Automoto(object):
    """This class controls the Automoto. 
    
    Each automoto has five io control the power and direction of motor
    Model: FIT0441. Hardware version: v2.2.
    
    Attributes
    ----------
    microblaze : Arduino
        Microblaze processor instance used by this module.
        
    """
    def __init__(self, mb_info, pin = MOTOR_PINS):
        """Return a new instance of an Grove LEDbar object. 
        
        Parameters
        ----------
        mb_info : dict
            A dictionary storing Microblaze information, such as the
            IP name and the reset name.
        instruction: list
           instruction to controll the car

        """
        if len(pin) != 12:
            raise ValueError("the number of pin should be set exactly 12.")
        
        if int(max(pin)) > 19 or int(min(pin)) < 0:
            raise ValueError("the value of pin should not be bigger than 19 or smaller than 0")

        self.microblaze = Arduino(mb_info, ARDUINO_AUTOMOTO_PROGRAM)
        self.microblaze.write_mailbox(0, pin)
        self.microblaze.write_blocking_command(CONFIG_IOP_SWITCH)

    def stop(self):
        """stop the car

        Returns
        -------
        None

        """
        self.microblaze.write_blocking_command(STOP)

    def move(self, instruction, speed = 50):
        """control the car to move
        Parameters
        ----------
        instruction is a string defined to instruct the direction
        speed is a int to control the speed

        Returns
        -------
        None

        """
        data_in = []
        if instruction not in MOTOR_DIRECTION.keys():
            raise ValueError("please input valid direction!")
        if speed not in range(101):
            raise ValueError("velocity should be in the range from 0 to 100")
        data_in.append(MOTOR_DIRECTION[instruction])
        data_in.append(speed)
        self.microblaze.write_mailbox(0, data_in)
        self.microblaze.write_blocking_command(MOVE)

    def distance(self, opt = 0, which = 1):
        """
        return the average of the four motor distance
        
        Parameters
        ----------
        int -> float

        Returns
        -------
        distance of the whole car
        """
        self.microblaze.write_mailbox(0, [opt, which])
        self.microblaze.write_blocking_command(DISTANCE)
        value = _reg2int(self.microblaze.read_mailbox(0))
        return value * (0.08*3.14159/2.0/1920.0)

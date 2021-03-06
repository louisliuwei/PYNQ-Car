#   Copyright (c) 2016, Xilinx, Inc.
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


import math
from . import Arduino
from . import MOTOR_DIRECTION
from . import MOTOR_PINS


__author__ = "Junhong Lin"
__copyright__ = "Copyright 2019, Xilinx"


ARDUINO_RUN_IMU_PROGRAM = "arduino_run_IMU.bin"
PAGE = 0xF

CONFIG_IOP_SWITCH = 0x1
GET_AXIS_DATA = 0x3
GET_EUL_DATA = 0x5
GET_QUA_DATA = 0x7
GET_TEMPERATURE = 0xB
GET_PRESSURE = 0xD

STOP = 0x3
MOVE = 0x5
DISTANCE = 0x7

def _reg2float(reg):
    """Converts 32-bit register value to floats in Python.

    Parameters
    ----------
    reg: int
        A 32-bit register value read from the mailbox.

    Returns
    -------
    float
        A float number translated from the register value.

    """
    if reg == 0:
        return 0.0
    sign = (reg & 0x80000000) >> 31 & 0x01
    exp = ((reg & 0x7f800000) >> 23) - 127
    if exp == 0:
        man = (reg & 0x007fffff) / pow(2, 23)
    else:
        man = 1 + (reg & 0x007fffff) / pow(2, 23)
    result = pow(2, exp) * man * ((sign * -2) + 1)
    return float("{0:.2f}".format(result))


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


class RUN_IMU(object):
    """This class controls the 10DOF IIC IMU. 
    
    Attributes
    ----------
    microblaze : Arduino
        Microblaze processor instance used by this module.
        
    """
    def __init__(self, mb_info, channel, pin = MOTOR_PINS):
        """Return a new instance of an 10DOF IMU object. 
        
        Parameters
        ----------
        mb_info : dict
            A dictionary storing Microblaze information, such as the
            IP name and the reset name.

        """

        self.microblaze = Arduino(mb_info, ARDUINO_RUN_IMU_PROGRAM)
        self.microblaze.write_mailbox(0, 0)
        self.microblaze.write_blocking_command(PAGE) #Choose IMU device
        self.microblaze.write_mailbox(0, channel)
        self.microblaze.write_blocking_command(CONFIG_IOP_SWITCH)
        data = self.microblaze.read_mailbox(0, 3)
        
        if not data[0]:
            raise ValueError("I2C Multiplexer failed.")
        
        if not data[1]:
            raise ValueError("IMU initialization failed.")
        
        if not data[2]:
            raise ValueError("Pressure sensor initialization failed.")


        if len(pin) != 12:
            raise ValueError("the number of pin should be set exactly 12.")
        
        if int(max(pin)) > 19 or int(min(pin)) < 0:
            raise ValueError("the value of pin should not be bigger than 19 or smaller than 0")
        self.microblaze.write_mailbox(0, 1)
        self.microblaze.write_blocking_command(PAGE) #Choose automoto device
        self.microblaze.write_mailbox(0, pin)
        self.microblaze.write_blocking_command(CONFIG_IOP_SWITCH)
        
    def get_axis(self):
        """Get the data from the accelerometer, gyroscope and magnetometer.
        
        Returns
        -------
        list
            A list of the acceleration data along X-axis, Y-axis, and Z-axis.
            A list of the gyro data along X-axis, Y-axis, and Z-axis.
            A list of the compass data along X-axis, Y-axis, and Z-axis.
        
        """
        self.microblaze.write_mailbox(0, 0)
        self.microblaze.write_blocking_command(PAGE) #Choose IMU device
        self.microblaze.write_blocking_command(GET_AXIS_DATA)
        data = self.microblaze.read_mailbox(0, 9)
        [ax, ay, az, gx, gy, gz, mx, my, mz] = [_reg2float(i) for i in data]
        return [ax, ay, az, gx, gy, gz, mx, my, mz]
        """return [float("{0:.2f}".format(ax / 16384)),
                float("{0:.2f}".format(ay / 16384)),
                float("{0:.2f}".format(az / 16384))]
        """
        
    def get_eul(self):
        """Get the euler angle data.
        
        Returns
        -------
        list
            A list of the euler angle data.
        
        """
        self.microblaze.write_mailbox(0, 0)
        self.microblaze.write_blocking_command(PAGE) #Choose IMU device
        self.microblaze.write_blocking_command(GET_EUL_DATA)
        data = self.microblaze.read_mailbox(0, 3)
        [head, roll, pitch] = [_reg2float(i) for i in data]
        return [head, roll, pitch]
        """return [float("{0:.2f}".format(gx * 250 / 32768)),
                float("{0:.2f}".format(gy * 250 / 32768)),
                float("{0:.2f}".format(gz * 250 / 32768))]
        """

    def get_qua(self):
        """Get the quaternion data.
        
        Returns
        -------
        list
            A list of the quaternion data.
        
        """
        self.microblaze.write_mailbox(0, 0)
        self.microblaze.write_blocking_command(PAGE) #Choose IMU device
        self.microblaze.write_blocking_command(GET_QUA_DATA)
        data = self.microblaze.read_mailbox(0, 4)
        [w, x, y, z] = [_reg2float(i) for i in data]
        return [w, x, y, z]
        """return [float("{0:.2f}".format(mx * 1200 / 4096)),
                float("{0:.2f}".format(my * 1200 / 4096)),
                float("{0:.2f}".format(mz * 1200 / 4096))]
        """

    def get_heading(self):
        """Get the value of the heading.
        
        Returns
        -------
        float
            The angle deviated from the X-axis, toward the positive Y-axis.
        
        """
        [_, _, _, _, _, _, mx, my, _] = self.get_axis()
        heading = 180 * math.atan2(my, mx) / math.pi
        if heading < 0:
            heading += 360
        return float("{0:.2f}".format(heading))

    def get_tilt_heading(self):
        """Get the value of the tilt heading.
        
        Returns
        -------
        float
            The tilt heading value.
        
        """
        [ax, ay, _, _, _, _, mx, my, mz] = self.get_axis()

        try:
            pitch = math.asin(-ax)
            roll = math.asin(ay / math.cos(pitch))
        except ZeroDivisionError:
            raise RuntimeError("Value out of range or device not connected.")

        xh = mx * math.cos(pitch) + mz * math.sin(pitch)
        yh = mx * math.sin(roll) * math.sin(pitch) + \
            my * math.cos(roll) - mz * math.sin(roll) * math.cos(pitch)
        _ = -mx * math.cos(roll) * math.sin(pitch) + \
            my * math.sin(roll) + mz * math.cos(roll) * math.cos(pitch)
        tilt_heading = 180 * math.atan2(yh, xh) / math.pi
        if yh < 0:
            tilt_heading += 360
        return float("{0:.2f}".format(tilt_heading))
        
    def get_temperature(self):
        """Get the current temperature in degree C.
        
        Returns
        -------
        float
            The temperature value.
        
        """
        self.microblaze.write_mailbox(0, 0)
        self.microblaze.write_blocking_command(PAGE) #Choose IMU device
        self.microblaze.write_blocking_command(GET_TEMPERATURE)
        value = self.microblaze.read_mailbox(0)
        return _reg2float(value)
        
    def get_pressure(self):
        """Get the current pressure in Pa.
        
        Returns
        -------
        float
            The pressure value.
        
        """
        self.microblaze.write_mailbox(0, 0)
        self.microblaze.write_blocking_command(PAGE) #Choose IMU device
        self.microblaze.write_blocking_command(GET_PRESSURE)
        value = self.microblaze.read_mailbox(0)
        return _reg2int(value)
        
    def get_atm(self):
        """Get the current pressure in relative atmosphere.

        Returns
        -------
        float
            The related atmosphere.
        
        """
        return float("{0:.2f}".format(self.get_pressure() / 101325))
        
    def get_altitude(self):
        """Get the current altitude.
        
        Returns
        -------
        float
            The altitude value.
        
        """
        pressure = self.get_pressure()
        a = pressure / 101325
        b = 1 / 5.255
        c = 1 - pow(a, b)
        altitude = 44300 * c
        return float("{0:.2f}".format(altitude))

    def stop(self):
        """stop the car

        Returns
        -------
        None

        """
        self.microblaze.write_mailbox(0, 1)
        self.microblaze.write_blocking_command(PAGE) #Choose automoto device
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
        self.microblaze.write_mailbox(0, 1)
        self.microblaze.write_blocking_command(PAGE) #Choose automoto device
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
        self.microblaze.write_mailbox(0, 1)
        self.microblaze.write_blocking_command(PAGE) #Choose automoto device
        self.microblaze.write_mailbox(0, [opt, which])
        self.microblaze.write_blocking_command(DISTANCE)
        value = _reg2int(self.microblaze.read_mailbox(0))
        return value * (0.08*3.14159/2.0/1920.0)
        
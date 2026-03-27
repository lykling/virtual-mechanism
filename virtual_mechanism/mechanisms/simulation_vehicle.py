#!/usr/bin/env python
# ****************************************************************************
# Copyright 2025 Pride Leong. All Rights Reserved.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ****************************************************************************
"""Simulation Vehicle Module
"""
import enum
import math


class MotionMode(enum.Enum):
    """MotionMode
    """
    UNDEFINED = 0
    ACKERMANN = 1
    SPOT_TURN = 2
    CRAB = 3
    SIDEWAY = 4
    MINIMAL_TURN_RADIUS = 5


class ControlMode(enum.Enum):
    """ControlMode
    """
    THROTTLE_AND_BRAKE = 1
    VELOCITY = 2
    ACCELERATION = 3
    WHEELSPEED = 4


class GearLocation(enum.Enum):
    """GearLocation
    """
    NEUTRAL = 0
    DRIVE = 1
    REVERSE = 2
    PARKING = 3
    LOW = 4
    INVALID = 5
    NONE = 6


# MotionMode = enum.Enum('MotionMode', [('ACKERMANN', 1), ('SPOT_TURN', 2),
#                                       ('CRAB', 3), ('SIDEWAY', 4),
#                                       ('MINIMAL_TURN_RADIUS', 5)])

# ControlMode = enum.Enum('ControlMode', [
#     ('THROTTLE_AND_BRAKE', 1),
#     ('VELOCITY', 2),
#     ('ACCELERATION', 3),
#     ('WHEELSPEED', 4),
# ])

# GearLocation = enum.Enum('GearLocation', [
#     ('NEUTRAL', 0),
#     ('DRIVE', 1),
#     ('REVERSE', 2),
#     ('PARKING', 3),
#     ('LOW', 4),
#     ('INVALID', 5),
#     ('NONE', 6),
# ])


def clamp(value, min_value, max_value):
    """clamp a value within a specified range
    """
    if min_value > max_value:
        return clamp(value, max_value, min_value)
    return max(min_value, min(value, max_value))


class SimulationVehicle():
    """SimulationVehicle
    """

    def __init__(self, params=None, state=None):
        """__init__
        """
        if params is None:
            params = {}
        default_params = {
            'length': 4.5,  # meters
            'width': 1.8,  # meters
            'height': 1.5,  # meters
            'max_steering_angle': 0.5235987755982988,  # radians
            'max_acceleration': 3.0,  # m/s^2
            'max_deceleration': -6.0,  # m/s^2
            'max_throttle_force': 4000.0,  # Newtons
            'max_brake_force': 8000.0,  # Newtons
            'max_speed': 20.0,  # m/s (120 km/h)
            'wheelbase': 2.7,  # meters
            'wheeltrack': 1.5,  # meters
            'mass': 1500.0,  # kg
            'drag_coefficient': 0.3,
            'frontal_area': 2.2,  # m^2
            'rolling_resistance_coefficient': 0.015,
        }
        self.params = {**default_params, **params}
        if state is None:
            state = {}
        default_state = {
            's': 0.0,
            't': 0.0,
            'x': 0.0,
            'y': 0.0,
            'z': 0.0,
            'yaw': 0.0,
            'pitch': 0.0,
            'roll': 0.0,
            'throttle': 0.0,
            'brake': 0.0,
            'linear_velocity': 0.0,
            'linear_acceleration': 0.0,
            'angular_velocity': 0.0,
            'angular_acceleration': 0.0,
            'steering_angle': 0.0,
            'steering_rate': 0.0,
            'epb': 0,
            'gear': GearLocation.NEUTRAL,
            'control_mode': ControlMode.VELOCITY,
            'motion_mode': MotionMode.ACKERMANN
        }
        self.state = {**default_state, **state}

    @property
    def s(self):
        """s
        """
        return self.state['s']

    @s.setter
    def s(self, value):
        """s
        """
        self.state['s'] = value

    @property
    def t(self):
        """t
        """
        return self.state['t']

    @t.setter
    def t(self, value):
        """t
        """
        self.state['t'] = value

    @property
    def x(self):
        """x
        """
        return self.state['x']

    @x.setter
    def x(self, value):
        """x
        """
        self.state['x'] = value

    @property
    def y(self):
        """y
        """
        return self.state['y']

    @y.setter
    def y(self, value):
        """y
        """
        self.state['y'] = value

    @property
    def z(self):
        """z
        """
        return self.state['z']

    @z.setter
    def z(self, value):
        """z
        """
        self.state['z'] = value

    @property
    def yaw(self):
        """yaw
        """
        return self.state['yaw']

    @yaw.setter
    def yaw(self, value):
        """yaw
        """
        self.state['yaw'] = value

    @property
    def pitch(self):
        """pitch
        """
        return self.state['pitch']

    @pitch.setter
    def pitch(self, value):
        """pitch
        """
        self.state['pitch'] = value

    @property
    def roll(self):
        """roll
        """
        return self.state['roll']

    @roll.setter
    def roll(self, value):
        """roll
        """
        self.state['roll'] = value

    @property
    def throttle(self):
        """throttle
        """
        return self.state['throttle']

    @throttle.setter
    def throttle(self, value):
        """throttle
        """
        self.state['throttle'] = clamp(value, 0.0, 1.0)

    @property
    def brake(self):
        """brake
        """
        return self.state['brake']

    @brake.setter
    def brake(self, value):
        """brake
        """
        self.state['brake'] = clamp(value, 0.0, 1.0)

    @property
    def linear_velocity(self):
        """linear_velocity
        """
        return self.state['linear_velocity']

    @linear_velocity.setter
    def linear_velocity(self, value):
        """linear_velocity
        """
        self.state['linear_velocity'] = clamp(value, -self.params['max_speed'],
                                              self.params['max_speed'])

    @property
    def linear_acceleration(self):
        """linear_acceleration
        """
        return self.state['linear_acceleration']

    @linear_acceleration.setter
    def linear_acceleration(self, value):
        """linear_acceleration
        """
        self.state['linear_acceleration'] = clamp(
            value, self.params['max_deceleration'],
            self.params['max_acceleration'])

    @property
    def angular_velocity(self):
        """angular_velocity
        """
        return self.state['angular_velocity']

    @angular_velocity.setter
    def angular_velocity(self, value):
        """angular_velocity
        """
        self.state['angular_velocity'] = value

    @property
    def angular_acceleration(self):
        """angular_acceleration
        """
        return self.state['angular_acceleration']

    @angular_acceleration.setter
    def angular_acceleration(self, value):
        """angular_acceleration
        """
        self.state['angular_acceleration'] = value

    @property
    def steering_angle(self):
        """steering_angle
        """
        return self.state['steering_angle']

    @steering_angle.setter
    def steering_angle(self, value):
        """steering_angle
        """
        self.state['steering_angle'] = clamp(
            value, -self.params['max_steering_angle'],
            self.params['max_steering_angle'])

    @property
    def steering_rate(self):
        """steering_rate
        """
        return self.state['steering_rate']

    @steering_rate.setter
    def steering_rate(self, value):
        """steering_rate
        """
        self.state['steering_rate'] = value

    @property
    def epb(self):
        """epb
        """
        return self.state['epb']

    @epb.setter
    def epb(self, value):
        """epb
        """
        self.state['epb'] = int(value)

    @property
    def gear(self):
        """gear
        """
        return self.state['gear']

    @gear.setter
    def gear(self, value):
        """gear
        """
        if isinstance(value, GearLocation):
            self.state['gear'] = value
        elif isinstance(value, int) and value in [
                member.value for member in GearLocation
        ]:
            self.state['gear'] = GearLocation(value)
        else:
            raise ValueError("Invalid gear location")

    @property
    def control_mode(self):
        """control_mode
        """
        return self.state['control_mode']

    @control_mode.setter
    def control_mode(self, value):
        """control_mode
        """
        if isinstance(value, ControlMode):
            self.state['control_mode'] = value
        elif isinstance(value, int) and value in [
                member.value for member in ControlMode
        ]:
            self.state['control_mode'] = ControlMode(value)
        else:
            raise ValueError("Invalid control mode")

    @property
    def motion_mode(self):
        """motion_mode
        """
        return self.state['motion_mode']

    @motion_mode.setter
    def motion_mode(self, value):
        """motion_mode
        """
        if isinstance(value, MotionMode):
            self.state['motion_mode'] = value
        elif isinstance(value, int) and value in [
                member.value for member in MotionMode
        ]:
            self.state['motion_mode'] = MotionMode(value)
        else:
            raise ValueError("Invalid motion mode")

    def update_linear_velocity(self, dt):
        """update_linear_velocity
        """
        direction = 1.0
        if self.gear == GearLocation.REVERSE:
            direction = -1.0
        # calculate new state by delta time based on control mode
        if self.control_mode == ControlMode.ACCELERATION:
            # change speed based on acceleration
            acceleration = self.linear_acceleration
            if self.gear not in [GearLocation.DRIVE, GearLocation.REVERSE]:
                # acceleartion take effect only in drive or reverse
                acceleration = 0.0
            self.linear_velocity += self.linear_acceleration * dt
        elif self.control_mode == ControlMode.VELOCITY:
            # noop for now
            pass
        elif self.control_mode == ControlMode.WHEELSPEED:
            # TODO(leafyleong): implement wheel speed control
            pass
        elif self.control_mode == ControlMode.THROTTLE_AND_BRAKE:
            # Physics model: throttle provides drive force, brake provides braking force, 
            # while considering damping forces
            # Drive force (only effective in drive or reverse gear)
            drive_force = 0.0
            if self.gear in [GearLocation.DRIVE, GearLocation.REVERSE] and self.throttle > 0:
                drive_force = self.throttle * self.params['max_throttle_force']
            
            # Brake force (always effective)
            brake_force = self.brake * self.params['max_brake_force']
            
            # Air resistance (F_drag = 0.5 * ρ * Cd * A * v², simplified to Cd * v²)
            air_resistance = self.params['drag_coefficient'] * self.linear_velocity**2
            
            # Rolling resistance (F_roll = Crr * m * g)
            rolling_resistance = (self.params['rolling_resistance_coefficient'] * 
                               self.params['mass'] * 9.81)
            
            # Total resistance always opposes the direction of velocity
            total_resistance = air_resistance + rolling_resistance
            
            # Calculate net force and acceleration
            if self.linear_velocity != 0:
                # Resistance direction opposes velocity when moving
                resistance_direction = -1 if self.linear_velocity > 0 else 1
                total_resistance *= resistance_direction
            else:
                # When stationary, resistance direction is determined by drive force
                total_resistance *= -direction if drive_force > 0 else 0
            
            net_force = direction * drive_force - brake_force + total_resistance
            acceleration = net_force / self.params['mass']
            
            # If vehicle is stationary and drive force is less than static friction, keep stationary
            if abs(self.linear_velocity) < 0.1 and abs(net_force) < self.params['mass'] * 0.5:
                acceleration = 0
                self.linear_velocity = 0
            
            self.linear_acceleration = acceleration
            self.linear_velocity += self.linear_acceleration * dt

        if direction * self.linear_velocity < 0.0:
            # prevent going backward in drive or forward in reverse
            self.linear_velocity = 0.0
        # print("Update linear velocity", f'gear={self.gear}',
        #       f'control_mode={self.control_mode}', f'throttle={self.throttle}',
        #       f'brake={self.brake}',
        #       f'linear_acceleration={self.linear_acceleration}',
        #       f'linear_velocity={self.linear_velocity}')

    def update_ackermann(self, dt):
        """on_update_ackermann
        """
        self.update_linear_velocity(dt)
        tan_delta = math.tan(self.steering_angle)
        omega = 0.0
        if math.fabs(tan_delta) > 1e-6:
            omega = self.linear_velocity * tan_delta / self.params['wheelbase']
        heading = math.fmod(self.yaw + omega * dt, 2 * math.pi)
        ds = self.linear_velocity * dt
        dx = ds * math.cos((self.yaw + heading) / 2)
        dy = ds * math.sin((self.yaw + heading) / 2)
        self.x += dx
        self.y += dy
        self.yaw = heading
        self.angular_velocity = omega
        self.s += math.fabs(ds)

    def update_minimal_turn_radius(self, dt):
        """update_minimal_turn_radius
        """
        self.update_linear_velocity(dt)
        tan_delta = math.tan(self.steering_angle)
        omega = 0.0
        if math.fabs(tan_delta) > 1e-6:
            omega = self.linear_velocity * tan_delta / (
                self.params['wheelbase'] / 2.0)
        heading = math.fmod(self.yaw + omega * dt, 2 * math.pi)
        ds = self.linear_velocity * dt
        dx = ds * math.cos((self.yaw + heading) / 2)
        dy = ds * math.sin((self.yaw + heading) / 2)
        self.x += dx
        self.y += dy
        self.yaw = heading
        self.angular_velocity = omega
        self.s += math.fabs(ds)

    def update_spot_turn(self, dt):
        """update_spot_turn
        """
        angular_delta = self.angular_velocity * dt
        radius = self.params['wheelbase'] / 2.0
        self.linear_velocity = self.angular_velocity * radius
        if math.fabs(self.angular_velocity) < 1e-3:
            self.linear_velocity = 0.0
            self.angular_velocity = 0.0
            return
        heading = math.fmod(self.yaw + angular_delta, 2 * math.pi)
        dx = radius * (math.cos(self.yaw) - math.cos(heading))
        dy = radius * (math.sin(self.yaw) - math.sin(heading))
        self.yaw = heading
        self.x += dx
        self.y += dy
        ds = math.fabs(self.linear_velocity) * dt
        self.s += ds

    def update_crabwalk(self, dt):
        """update_crabwalk
        """
        self.update_linear_velocity(dt)
        if math.fabs(self.linear_velocity) < 1e-3:
            self.linear_velocity = 0.0
            return
        augular = math.fmod(self.yaw + self.steering_angle, 2 * math.pi)
        dx = self.linear_velocity * math.cos(augular) * dt
        dy = self.linear_velocity * math.sin(augular) * dt
        self.x += dx
        self.y += dy
        ds = math.fabs(self.linear_velocity) * dt
        self.s += ds

    def update_sideway(self, dt):
        """update_sideway
        """
        self.update_linear_velocity(dt)
        if math.fabs(self.linear_velocity) < 1e-3:
            self.linear_velocity = 0.0
            return
        augular = math.fmod(self.yaw + math.pi / 2.0, 2 * math.pi)
        dx = self.linear_velocity * math.cos(augular) * dt
        dy = self.linear_velocity * math.sin(augular) * dt
        self.x += dx
        self.y += dy
        ds = math.fabs(self.linear_velocity) * dt
        self.s += ds

    def update(self, dt):
        """update
        """
        if self.epb:
            # stop the vehicle immediately
            self.throttle = 0
            self.linear_velocity = 0.0
            self.linear_acceleration = 0.0
            self.angular_velocity = 0.0
            self.angular_acceleration = 0.0
            return
        if self.motion_mode == MotionMode.ACKERMANN:
            self.update_ackermann(dt)
        elif self.motion_mode == MotionMode.SPOT_TURN:
            self.update_spot_turn(dt)
        elif self.motion_mode == MotionMode.CRAB:
            self.update_crabwalk(dt)
        elif self.motion_mode == MotionMode.SIDEWAY:
            self.update_sideway(dt)
        elif self.motion_mode == MotionMode.MINIMAL_TURN_RADIUS:
            self.update_minimal_turn_radius(dt)
        else:
            # invalid mode, do nothing
            pass

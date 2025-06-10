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
"""Simple Clamp
"""
import math
import pathlib
import time
import types
from importlib import resources as impresources
import can
import cantools
import cantools.database
from virtual_mechanism.mechanisms import mechanism
from virtual_mechanism import dbc


class SimpleClamp(mechanism.Mechanism):
    """SimpleClamp
    """

    def __init__(self, dbc_file: str = '', device: str = 'can0', state=None):
        """__init__
        """

        self.dbc_file = dbc_file
        if not dbc_file:
            self.dbc_file = impresources.files(dbc).joinpath('clamp.dbc')
        self.db = self.dbc_file
        self.device = device
        if not isinstance(self.db, cantools.database.Database):
            raise TypeError(
                f"Expected cantools.database.Database, got {type(self.db)}")

        self.canbus = can.Bus(
            interface='socketcan',
            channel=device,
            bitrate=500000,
        )

        default_state = {
            'enable_position': 0,
            'enable_descent': 0,
            'enable_extend': 0,
            'loaded': 1,
            'error_code': 0,
            'fixed_front': 0,
            'fixed_rear': 1,
            'position_front': 0.0,
            'position_rear': 0.0,
            'descent_height': 0.0,
            'extend_length_fl': 0.0,
            'extend_length_fr': 0.0,
            'extend_length_rl': 0.0,
            'extend_length_rr': 0.0,
        }
        if state is None:
            state = {}
        custom_state_keys = set(default_state) - (set(default_state) -
                                                  set(state.keys()))
        initial_state = {
            **default_state,
            **({
                key: state[key]
                for key in custom_state_keys
            })
        }
        super().__init__(state=initial_state)

        self.control_target = types.SimpleNamespace(
            enable_position=0,
            enable_descent=0,
            enable_extend=0,
            position_front=0.0,
            position_rear=0.0,
            descent_height=0.0,
            extend_length_fl=0.0,
            extend_length_fr=0.0,
            extend_length_rl=0.0,
            extend_length_rr=0.0,
        )

        self.report_messages = [
            self.db.get_message_by_name('CLAMP_Clamping_Position_Report'),
            self.db.get_message_by_name('CLAMP_Clamping_Operation_Report'),
        ]
        self.report_messages_last_send_time = {
            self.db.get_message_by_name('CLAMP_Clamping_Position_Report'): 0.0,
            self.db.get_message_by_name('CLAMP_Clamping_Operation_Report'):
            0.0,
        }
        self.bind_report_messages()

    @property
    def db(self):
        """db
        """
        return self._db

    @db.setter
    def db(self, value):
        """db
        """
        if isinstance(value, (str, pathlib.PosixPath)):
            result = cantools.database.load_file(value)
            if not isinstance(result, cantools.database.Database):
                raise TypeError(
                    f"Expected cantools.database.Database, got {type(value)}")
            self._db = result
            return
        if not isinstance(value, cantools.database.Database):
            raise TypeError(
                f"Expected cantools.database.Database, got {type(value)}")
        self._db = value

    def on_control(self):
        """on_control
        """
        while self.running():
            message = self.canbus.recv(timeout=1)
            if message is None:
                continue
            if message.arbitration_id == self.db.get_message_by_name(
                    'ADAS_Clamping_Position_Command').frame_id:
                data = self.db.get_message_by_name(
                    'ADAS_Clamping_Position_Command').decode(message.data)
                self.control_target.enable_position = data[
                    'Clamping_Position_CTRL'].value
                self.control_target.enable_descent = data[
                    'Clamping_Descent_CTRL'].value
                self.control_target.enable_extend = data[
                    'Clamping_Extend_CTRL'].value
                self.control_target.position_front = data[
                    'Clamping_Position_Front_Target']
                self.control_target.position_rear = data[
                    'Clamping_Position_Rear_Target']
                self.control_target.descent_height = data[
                    'Clamping_DescentHeight_Target']
            elif message.arbitration_id == self.db.get_message_by_name(
                    'ADAS_Clamping_Operation_Command').frame_id:
                data = self.db.get_message_by_name(
                    'ADAS_Clamping_Operation_Command').decode(message.data)
                self.control_target.extend_length_fl = data[
                    'Clamping_ExtLength_FL_Target']
                self.control_target.extend_length_fr = data[
                    'Clamping_ExtLength_FR_Target']
                self.control_target.extend_length_rl = data[
                    'Clamping_ExtLength_RL_Target']
                self.control_target.extend_length_rr = data[
                    'Clamping_ExtLength_RR_Target']

    def bind_report_messages(self):
        """bind_report_messages
        """
        self.report_getters = {}
        clamp_clamping_position_report = self.db.get_message_by_name(
            'CLAMP_Clamping_Position_Report')
        self.report_getters[clamp_clamping_position_report.get_signal_by_name(
            'Clamping_Position_STATE')] = lambda: self.state.enable_position
        self.report_getters[clamp_clamping_position_report.get_signal_by_name(
            'Clamping_Descent_STATE')] = lambda: self.state.enable_descent
        self.report_getters[clamp_clamping_position_report.get_signal_by_name(
            'Clamping_Extend_STATE')] = lambda: self.state.enable_extend
        self.report_getters[clamp_clamping_position_report.get_signal_by_name(
            'Clamping_Fixed_Front')] = lambda: self.state.fixed_front
        self.report_getters[clamp_clamping_position_report.get_signal_by_name(
            'Clamping_Fixed_Rear')] = lambda: self.state.fixed_rear
        self.report_getters[clamp_clamping_position_report.get_signal_by_name(
            'Clamping_Load_STATE')] = lambda: self.state.loaded
        self.report_getters[clamp_clamping_position_report.get_signal_by_name(
            'Clamping_Position_Front')] = lambda: self.state.position_front
        self.report_getters[clamp_clamping_position_report.get_signal_by_name(
            'Clamping_Position_Rear')] = lambda: self.state.position_rear
        self.report_getters[clamp_clamping_position_report.get_signal_by_name(
            'Clamping_DescentHeight')] = lambda: self.state.descent_height
        self.report_getters[clamp_clamping_position_report.get_signal_by_name(
            'Clamping_ErrorCode')] = lambda: self.state.error_code

        clamp_clamping_operation_report = self.db.get_message_by_name(
            'CLAMP_Clamping_Operation_Report')
        self.report_getters[clamp_clamping_operation_report.get_signal_by_name(
            'Clamping_ExtLength_FL')] = lambda: self.state.extend_length_fl
        self.report_getters[clamp_clamping_operation_report.get_signal_by_name(
            'Clamping_ExtLength_FR')] = lambda: self.state.extend_length_fr
        self.report_getters[clamp_clamping_operation_report.get_signal_by_name(
            'Clamping_ExtLength_RL')] = lambda: self.state.extend_length_rl
        self.report_getters[clamp_clamping_operation_report.get_signal_by_name(
            'Clamping_ExtLength_RR')] = lambda: self.state.extend_length_rr

    def on_report(self):
        """on_report
        """
        # Report logic for the clamp mechanism
        while self.running():
            now = time.time() * 1000
            for message in self.report_messages:
                if message.cycle_time is None:
                    continue
                if now - self.report_messages_last_send_time[message] < float(
                        message.cycle_time):
                    continue
                data = {}
                for sig in message.signals:
                    if sig in self.report_getters:
                        value = self.report_getters[sig]()
                        if value is not None:
                            data[sig.name] = value
                buffer = message.encode(data)
                msg = can.Message(arbitration_id=message.frame_id,
                                  data=buffer,
                                  is_extended_id=False)
                # print(data, msg, buffer)
                self.canbus.send(msg)
                self.report_messages_last_send_time[message] = now
            time.sleep(0.001)

    def on_update_field(self, exp, exp_field, src, src_field, step=0.1):
        """on_update_field
        """
        if not hasattr(src, src_field) or not hasattr(exp, exp_field):
            raise AttributeError(
                r'Source or expected object does not have the field'
                f" '{src_field}' or '{exp_field}'")
        if isinstance(getattr(self.state, src_field), bool):
            # For boolean fields, we do not update them based on error
            if getattr(exp, exp_field) != getattr(src, src_field):
                setattr(src, src_field, getattr(exp, exp_field))
            return
        err = getattr(exp, exp_field) - getattr(src, src_field)
        if math.fabs(err) > 1e-2:
            setattr(src, src_field,
                    getattr(src, src_field) + math.fabs(err) / err * step)

    def on_update_position(self, dt):
        """on_update_position
        """
        if not self.state.enable_position:
            return
        step = 10.0 * dt * 10.0
        self.on_update_field(self.control_target,
                             'position_front',
                             self.state,
                             'position_front',
                             step=step)
        self.on_update_field(self.control_target,
                             'position_rear',
                             self.state,
                             'position_rear',
                             step=step)

    def on_update_descent(self, dt):
        """on_update_descent
        """
        if not self.state.enable_descent:
            return
        step = 10.0 * dt * 10.0
        self.on_update_field(self.control_target,
                             'descent_height',
                             self.state,
                             'descent_height',
                             step=step)

    def on_update_extend(self, dt):
        """on_update_extend
        """

        if not self.state.enable_extend:
            return
        step = 10.0 * dt * 2.0
        self.on_update_field(self.control_target,
                             'extend_length_fl',
                             self.state,
                             'extend_length_fl',
                             step=step)
        self.on_update_field(self.control_target,
                             'extend_length_fr',
                             self.state,
                             'extend_length_fr',
                             step=step)
        self.on_update_field(self.control_target,
                             'extend_length_rl',
                             self.state,
                             'extend_length_rl',
                             step=step)
        self.on_update_field(self.control_target,
                             'extend_length_rr',
                             self.state,
                             'extend_length_rr',
                             step=step)

    def on_update(self):
        """on_update
        """
        # Update logic for the clamp mechanism
        dt = 0.001
        while self.running():
            self.state.enable_position = self.control_target.enable_position
            self.state.enable_descent = self.control_target.enable_descent
            self.state.enable_extend = self.control_target.enable_extend

            self.on_update_position(dt)
            self.on_update_descent(dt)
            self.on_update_extend(dt)

            time.sleep(dt)

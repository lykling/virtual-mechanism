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
"""mechanism
"""
import types
import threading


class Mechanism:
    """Mechanism
    """

    def __init__(self, state=None):
        """__init__
        :param dbc_file: dbc file
        :param device: can device
        """
        if state is None:
            state = {}
        if isinstance(state, dict):
            self.state = types.SimpleNamespace(**state)

        self._stop_event = threading.Event()

    def on_control(self):
        """on_control
        """
        raise NotImplementedError("on_control method must be implemented")

    def on_report(self):
        """on_report
        """
        raise NotImplementedError("on_report method must be implemented")

    def on_update(self):
        """on_update
        """
        raise NotImplementedError("on_update method must be implemented")

    def running(self):
        """running
        """
        return not self._stop_event.is_set()

    def run(self):
        """run
        """
        self.control_thread = threading.Thread(target=self.on_control)
        self.control_thread.daemon = True
        self.control_thread.start()

        self.report_thread = threading.Thread(target=self.on_report)
        self.report_thread.daemon = True
        self.report_thread.start()

        self.update_thread = threading.Thread(target=self.on_update)
        self.update_thread.daemon = True
        self.update_thread.start()

    def shutdown(self):
        """stop
        """
        self._stop_event.set()

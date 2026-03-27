#!/usr/bin/env python3
# Copyright 2025 Pride Leong <lykling.lyk@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Simple Light
"""
import enum


class SimpleLight():
    """Simple Light
    """

    class State(enum.Enum):
        """Light State
        """
        OFF = 0
        ON = 1
        BLINKING = 2

    def __init__(self):
        self.state = self.State.OFF

    def on(self):
        """Turn on the light
        """
        self.state = self.State.ON

    def off(self):
        """Turn off the light
        """
        self.state = self.State.OFF

    def blink(self):
        """Check if the light is on
        """
        self.state = self.State.BLINKING

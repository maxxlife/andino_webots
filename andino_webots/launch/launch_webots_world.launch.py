# BSD 3-Clause License

# Copyright (c) 2023, Ekumen Inc.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import launch
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.substitutions.path_join_substitution import PathJoinSubstitution
from webots_ros2_driver.webots_launcher import WebotsLauncher
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    andino_webots_pkg_dir = get_package_share_directory("andino_webots")
    world = LaunchConfiguration("world")
    remove_nodes_arg = DeclareLaunchArgument(
        "remove_nodes",
        default_value="false",
        description="Enable NodeRemover robot spawning.",
    )
    world_arg = DeclareLaunchArgument(
        "world",
        default_value="room.wbt",
        description="Choose one of the world files from `/andino_webots/worlds` directory",
    )
    webots = WebotsLauncher(
        world=PathJoinSubstitution([andino_webots_pkg_dir, "worlds", world]),
        ros2_supervisor=True,
    )

    # Include nbode remover supervisor plugin launch file
    include_supervisor = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(andino_webots_pkg_dir, "launch", "remove_nodes.launch.py"),
        ),
        # Define what world will be spawning
        launch_arguments={
            "remove_nodes": LaunchConfiguration("remove_nodes"),
        }.items(),
    )

    return LaunchDescription(
        [
            remove_nodes_arg,
            world_arg,
            webots,
            webots._supervisor,
            include_supervisor,
            # This action will kill all nodes once the Webots simulation has exited
            launch.actions.RegisterEventHandler(
                event_handler=launch.event_handlers.OnProcessExit(
                    target_action=webots,
                    on_exit=[launch.actions.EmitEvent(event=launch.events.Shutdown())],
                )
            ),
        ]
    )

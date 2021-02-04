#!/usr/bin/env python2

# Copyright (c) 2017, CATIE, All Rights Reserved
# SPDX-License-Identifier: Apache-2.0
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import argparse

# Check args
parser = argparse.ArgumentParser(description='Program ELF file to board')
parser.add_argument("device", help="Reference of the device to flash")
parser.add_argument("elf_file", help="Path to the ELF file")
parser.add_argument("--probe", default="j-link", help="The programming method to use: st-link or j-link")
args = parser.parse_args()

script_dirname = os.path.dirname(os.path.abspath(__file__))

if args.probe == "j-link":
    elf_path = os.path.abspath(args.elf_file).replace("\\","/").replace(".elf",".bin")

    #create the JLink command file
    command_file_content = ("si 1\n"
                            "speed 4000\n"
                            "r\n"
                            "h\n"
                            "loadfile {},0x08000000\n"
                            "r\n"
                            "q\n").format(elf_path)
    command_file = open(os.path.join(script_dirname, "jlink_command_file.jlink").replace("\\", "/"), 'w')
    command_file.write(command_file_content)
    command_file.close()

    command_path = os.path.join(script_dirname, "jlink_command_file.jlink").replace("\\", "/")

    # Flash target
    if os.name == 'nt':
        executable = 'JLink.exe'
    else:
        executable = 'JLinkExe'
    cmd = executable + ' -Device {} -if JTAG -CommanderScript {} '.format(args.device, command_path)
    ret = os.system(cmd)
    if ret != 0:
        if os.name == 'nt':
            print "Error when calling J-Link executable. Please verify that JLink.exe has been added to the PATH"
        elif os.name == 'posix':
            print "Error when calling J-Link executable. Please verify that JLinkEXE has been added to the PATH"

    os.remove(command_path)

if args.probe == "st-link":
    elf_path = os.path.abspath(args.elf_file).replace("\\","/")

    if "STM32L4" in args.device:
        openocd_cli_args = " -f interface/stlink-v2-1.cfg -c \"transport select hla_swd\"\
                -f target/stm32l4x.cfg -c \"reset_config srst_only srst_nogate\""
        
        # Flash target
        cmd = "openocd" + openocd_cli_args + ' -c "program {} verify reset exit"'.format(elf_path)
        ret = os.system(cmd)
        if ret != 0:
            if os.name == 'nt':
                print "Error when calling OpenOCD executable. Please verify that openocd.exe has been added to the PATH"
            elif os.name == 'posix':
                print "Error when calling OpenOCD executable. Please verify that openocd has been added to the PATH"

    else:  # use the config file of the project
        print "Unknown device, using openocd.cfg configuration file of the project"

        # Flash target
        cmd = 'openocd -f openocd.cfg -c "program {} verify reset exit"'.format(elf_path)
        ret = os.system(cmd)
        if ret != 0:
            if os.name == 'nt':
                print "Error when calling OpenOCD executable. Please verify that openocd.exe has been added to the PATH"
            elif os.name == 'posix':
                print "Error when calling OpenOCD executable. Please verify that openocd has been added to the PATH"
       	print



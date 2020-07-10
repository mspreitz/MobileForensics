#!/usr/bin/python3

#############################################################################################
# Copyright (C) 2020 Michael Spreitzenbarth (research@spreitzenbarth.de)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#############################################################################################

import hashlib, sqlite3, os, sys, subprocess, struct
from binascii import hexlify


SQLITE_DB = "GestureRainbowTable.db"


def crack(backup_dir):

    # dumping the system file containing the hash
    print("[i] dumping gesture.key ...")
    gesture = subprocess.run(['adb', 'pull', '/data/system/gesture.key', backup_dir], 
        stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

    if gesture.returncode == 0:
        gesturehash = open(backup_dir + "/gesture.key", "rb").readline()
        lookuphash = hexlify(gesturehash).decode()
        print("[i] found hash: \033[0;32m" + lookuphash + "\033[m")

        conn = sqlite3.connect(SQLITE_DB)
        cur = conn.cursor()
        cur.execute("SELECT pattern FROM RainbowTable WHERE hash = ?", (lookuphash,))
        gesture = cur.fetchone()[0]

        return gesture
    else:
        print("[!] " + gesture.stdout.decode("utf-8").split("\n")[0])
        print("[!] exiting...")
        sys.exit(2)


if __name__ == '__main__':
    print("[i] starting...")

    # check if device is connected and adb is running as root
    deviceAvailable = subprocess.run(['adb', 'get-state'], 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if deviceAvailable.returncode != 0:
        print("[!] " + deviceAvailable.stderr.decode("utf-8").split("\n")[0])
        print("[!] exiting...")
        sys.exit(2)

    # starting to create the output directory and the crack file used for hashcat
    backup_dir = sys.argv[1]

    try:
        os.stat(backup_dir)
    except:
        os.mkdir(backup_dir)

    gesture = crack(backup_dir)
    print("[i] screenlock gesture: \033[0;32m" + gesture + "\033[m")
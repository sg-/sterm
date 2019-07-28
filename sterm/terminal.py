# STERM, a serial communication terminal with server capabilities        #
# Copyright (C) 2013-2019  Ralf Stemmer (ralf.stemmer@gmx.net)           #
#                                                                        #
# This program is free software: you can redistribute it and/or modify   #
# it under the terms of the GNU General Public License as published by   #
# the Free Software Foundation, either version 3 of the License, or      #
# (at your option) any later version.                                    #
#                                                                        #
# This program is distributed in the hope that it will be useful,        #
# but WITHOUT ANY WARRANTY; without even the implied warranty of         #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
# GNU General Public License for more details.                           #
#                                                                        #
# You should have received a copy of the GNU General Public License      #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.  #

import sys
import tty
import termios


# TODO: In unbuffered mode, the input gets not echoed - this in intentional but implicit.
#       An option to change this behavior would be nice

class Terminal(object):
    """
    This class handles the Terminal setup and access for seamless read/write access to remote shells.

    This class switches the terminal into *raw mode*!

    When ``echo`` is ``True``, then all entered character will be printed to *stdout*.
    Otherwise entering a character will be invisible when not echoed by the connected device.
    """
    def __init__(self, *, echo=True, escape="\033"):
        self.echo   = echo
        self.escape = escape

        # Setup local terminal
        self.stdinfd          = sys.stdin.fileno()
        self.oldstdinsettings = termios.tcgetattr(self.stdinfd)
        tty.setraw(self.stdinfd) # from now on, end-line must be "\r\n"



    def __del__(self):
        termios.tcsetattr(self.stdinfd, termios.TCSADRAIN, self.oldstdinsettings)



    def ReadLine(self):
        r"""
        This method reads a whole line and returns it.
        The end-of-line character (``\n``, ``\r``, ``\r\n``) are not included.
        """
        string = ""

        while True:
            char = self.ReadCharacter()
            if char == "\n":  # Ignore \n - should never appear in raw mode
                continue
            elif char == "\r":
                break
            else:
                string += char

        return string


    def ReadCharacter(self):
        r"""
        This method returns one single character of the users input.
        In raw (``echo = False``) mode, enter only produces an \r, not an \n

        If echo mode is enabled, the entered character gets printed to *stdout*.
        """
        char = sys.stdin.read(1)
        if self.echo:
            if char == self.escape:
                self.Write("␛") # Print ESC Unicode character then user hits escape key
            else:
                self.Write(char)
        return char



    def Write(self, string):
        r"""
        This method handles the output and adopts the line ending to the terminal configuration

        In raw mode line ending must be ``\r\n``.
        When an input of an enter (only ``\r``) shall be echoed, an additional ``\n`` needs to be written.

        This method takes care that there is always ``\r\n``, independent if only ``\r`` or ``\n`` is used as line break.
        """
        # In the raw input mode (no echo), the output also expects an explicit \r
        # This is because of the changed, none-default settings of the TTY
        # Here I take care that the \r\n sequence is correct
        string = string.replace("\n", "\r\n").replace("\r\r", "\r")
        string = string.replace("\r", "\r\n").replace("\n\n", "\n")

        sys.stdout.write(string)
        sys.stdout.flush()
        return



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4


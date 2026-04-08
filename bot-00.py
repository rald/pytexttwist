#!/usr/bin/env python3

import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr

import sys
import time
import logging

from game import Game

GAME_TITLE="TEXTTWIST"

channel=None
COMMAND_PREFIX='.'

def chunkstring(string, length):
    """Generate fixed-length chunks from a string."""
    return (string[0+i:length+i] for i in range(0, len(string), length))

class TestBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.game = Game()

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments[0])

    def on_pubmsg(self, c, e):
        """
        a = e.arguments[0].split(":", 1)
        if len(a) > 1 and irc.strings.lower(a[0]) == irc.strings.lower(
            self.connection.get_nickname()
        ):
            self.do_command(e, a[1].strip())
        return
        """

        a = e.arguments[0]
        if a[0]==COMMAND_PREFIX:
            self.do_command(e,a[1:])

    def do_command(self, e, cmd):
        nick = e.source.nick
        c = self.connection
        a=cmd.split(" ",1)

        if len(a)==1 and a[0]=="start":
            if self.game.state == Game.State.INIT:
                print(f"{nick}: {self.game.shuffled_word}")
                print(f"{nick}: {self.game.anagrams}")

                c.privmsg(self.channel, f"{GAME_TITLE}: {nick}: {self.game.shuffled_word}")
def main():

    logging.basicConfig(level=logging.DEBUG)

    if len(sys.argv) != 4:
        print("Usage: tt.py <server[:port]> <channel> <nickname>")
        sys.exit(1)

    s = sys.argv[1].split(":", 1)
    server = s[0]
    if len(s) == 2:
        try:
            port = int(s[1])
        except ValueError:
            print("Error: Erroneous port.")
            sys.exit(1)
    else:
        port = 6667
    channel = sys.argv[2]
    nickname = sys.argv[3]

    bot = TestBot(channel, nickname, server, port)
    bot.start()

if __name__ == "__main__":
    main()

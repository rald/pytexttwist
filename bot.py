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
        nick = e.source.nick
        c = self.connection
        a = e.arguments[0]

        if a[0]==COMMAND_PREFIX:
            cmd=a[1:].strip()
            if cmd=="start":
                if self.game.state == Game.State.INIT:

                    self.game.start(self.time_up,c,e)

                    print(f"{nick}: {self.game.shuffled_word}")
                    print(f"{nick}: {self.game.anagrams}")

                    c.privmsg(self.channel, f"{GAME_TITLE}: {nick}: {self.game.shuffled_word}")
                else:
                    c.privmsg(self.channel, f"{GAME_TITLE}: {nick}: game is already started.")
            elif cmd=="twist":
                if self.game.state == Game.State.BEGIN:
                    self.game.shuffle_word()
                    c.privmsg(self.channel, f"{GAME_TITLE}: {nick}: {self.game.shuffled_word}")
                else:
                    c.privmsg(self.channel, f"{GAME_TITLE}: {nick}: game not started.")
            elif cmd=="top":
                self.game.load_scores(self.game.score_file)
                sorted_scores = dict(sorted(self.game.scores.items(), key=lambda item: item[1], reverse=True))
    
                msg=""
                begin=True
                for i, key in enumerate(sorted_scores, 1):
                    if begin:
                        begin=False
                    else:
                        msg+=", "
                    msg+=f"{i}. {key} {sorted_scores[key]}"
                    if i == 10:
                        break
                
                c.privmsg(self.channel, f"{GAME_TITLE}: {nick}: TOP 10: {msg}")

            elif cmd.startswith("score"):

                b=a[1:].split(" ",1)
                if len(b)==2 and b[1].strip():
                    n=b[1].strip()
                else:
                    n=nick

                self.game.load_scores(self.game.score_file);

                if n in self.game.scores:
                    if n==nick:
                        c.privmsg(self.channel, f"{GAME_TITLE}: {nick}: your score is {self.game.scores[nick]}.")
                    else:
                        c.privmsg(self.channel, f"{GAME_TITLE}: {nick}: {n}'s score is {self.game.scores[n]}.")
                else:
                    c.privmsg(self.channel, f"{GAME_TITLE}: {nick}: player {n} not found.")

        elif    self.game.state==Game.State.BEGIN and \
                len(a.split(" "))==1 and \
                a in self.game.anagrams:
            word = a
            guess_state = self.game.guess(nick,word)
            if guess_state == Game.GuessState.FOUND:
                c.privmsg(self.channel, f"{GAME_TITLE}: {nick}: '{word}' found plus {self.game.points} points.")
                if self.game.nguessed == len(self.game.anagrams):
                    c.privmsg(self.channel, f"{GAME_TITLE}: {nick}: you finished the game.")
                    self.game.timer.stop()
                    self.game.state = Game.State.INIT

            elif guess_state == Game.GuessState.NOT_FOUND:
                c.privmsg(self.channel, f"{GAME_TITLE}: {nick}: '{word}' not found.")
            elif guess_state == Game.GuessState.GUESSED:
                c.privmsg(self.channel, f"{GAME_TITLE}: {nick}: '{word}' already guessed.")
    def time_up(self,c,e):
        nick = e.source.nick
        c = self.connection
        c.privmsg(self.channel, f"{GAME_TITLE}: Time Up!")
        self.game.state=Game.State.INIT


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

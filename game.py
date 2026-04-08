from enum import Enum
from player import Player

import random
import threading



class Game:

    class State(Enum):
        INIT = 0
        BEGIN = 1

    class GuessState(Enum):
        NOT_FOUND = 0
        FOUND = 1
        GUESSED = 2

    def __init__(self):
        self.state = Game.State.INIT
        self.random_word_file = "random_words.txt"
        self.dict_word_file = "dict_words.txt"
        self.score_file = "scores.txt"
        self.random_word = None
        self.shuffled_word = None
        self.anagrams = None
        self.guessed = None
        self.score = 0
        self.nguessed = 0
        self.points = 0

        self.scores = None

    def start(self,cb,c,e):
        self.state = Game.State.BEGIN

        self.load_scores(self.score_file)

        self.random_word = Game.random_line(self.random_word_file)

        self.shuffle_word()
        while self.shuffled_word == self.random_word:
            self.shuffle_word()

        self.anagrams = Game.get_anagrams(self.random_word, self.dict_word_file)
        self.anagrams = sorted(self.anagrams, key=lambda x: (len(x), x))
        self.guessed = [False] * len(self.anagrams)
        self.nguessed = 0
        self.score = 0

        self.timer = threading.Timer(180, cb, args=[c,e])
        self.timer.start()

    def shuffle_word(self):
        self.shuffled_word = "".join(random.sample(self.random_word, len(self.random_word)))

    def random_line(path):
        result = None
        with open(path, "r", encoding="utf-8") as file:
            for i, line in enumerate(file, 1):
                if random.randrange(i) == 0:
                    result = line.strip()
        return result

    def get_anagrams(w1,path):
        anagrams = []
        with open(path, "r", encoding="utf-8") as file:
            for line in file:
                w2=line.strip()
                if Game.is_anagram(w1,w2):
                   anagrams.append(w2)
        return anagrams

    def freq(w):
        f=[0]*26
        for l in w.lower():
            f[ord(l)-ord('a')]+=1
        return f

    def all_zero(f):
        for i in range(26):
            if f[i] != 0:
                return False
        return True

    def is_anagram(w1,w2):
        f1 = Game.freq(w1)
        f2 = Game.freq(w2)
        if Game.all_zero(f1) or Game.all_zero(f2):
            return False
        for i in range(26):
            if f1[i]<f2[i]:
                return False
        return True

    def guess(self, nick, word):
        self.points = 0

        i = -1
        try:
            i = self.anagrams.index(word)
        except ValueError:
            i = -1

        if i == -1:
            return Game.GuessState.NOT_FOUND

        if not self.guessed[i]:

            self.load_scores(self.score_file)

            self.points = len(word)

            if nick in self.scores:
                self.scores[nick]+=self.points
            else:
                self.scores[nick]=self.points

            self.save_scores(self.score_file)

            self.guessed[i] = True
            self.nguessed += 1

            return Game.GuessState.FOUND
        else:
            return Game.GuessState.GUESSED

    def load_scores(self,path):
        self.scores = {}
        with open(path, "r", encoding="utf-8") as file:
            for line in file:
                a=line.strip()
                b=a.split(" ",1)
                self.scores[b[0]]=int(b[1])


    def save_scores(self,path):
        with open(path, "w", encoding="utf-8") as file:
            for key in self.scores:
                file.write(f"{key} {self.scores[key]}\n")

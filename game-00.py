from enum import Enum

import random



class Game:

    class State(Enum):
        INIT = 0
        BEGIN = 1
        END = 2


    def __init__(self):
        self.state = Game.State.INIT
        self.random_word_file = "random_words.txt"
        self.dict_word_file = "dict_words.txt"
        self.random_word = None
        self.shuffled_word = None
        self.anagrams = None
        self.guessed = None
        self.score = 0
        self.nguessed = 0;

    def start(self):
        self.state = Game.State.BEGIN
        self.random_word = Game.random_line(self.random_word_file)
        self.shuffled_word = "".join(random.sample(self.random_word, len(self.random_word)))
        self.anagrams = Game.get_anagrams(self.random_word, self.dict_word_file)
        self.anagrams = sorted(self.anagrams, key=lambda x: (len(x), x))
        self.guessed = [False] * len(self.anagrams)
        self.nguessed = 0
        self.score = 0

    def guess(self, word):
        i=self.anagrams.find(word)
        if i != -1 and not self.guessed[i]:
            self.score += len(word)
            self.guessed[i] = True
            self.nguessed += 1
            if self.nguessed == len(self.anagrams):
                self.state = Game.State.END

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

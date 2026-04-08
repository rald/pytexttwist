#!/usr/bin/env python3

path="enable1.txt"
with open(path, "r", encoding="utf-8") as file:
    for line in file:
        w = line.strip()
        l = len(w)
        if l>=6 and l<=8:
            print(w)

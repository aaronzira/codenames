# Codenames

A simple implementation of my favorite multiplayer board game.
With a chosen grid size and provided text file of words to use,
a randomized legend will be created, and the option to replace
any words will be given before starting the game.

### Usage

**1. Print legend to the terminal**
  - good for playing on one computer with multiple screens

```
# 5x5 grid
python codenames.py 5 words_file.txt
```

**2. Email the legend to one or more codemasters**
  - good for playing over video calls, or to avoid accidentally having the wrong players see the legend

```
# 6x6 grid
python codenames.py 6 words_file.txt --codemasters <<codemaster1@....com>> <<codemaster2@....com>>
```

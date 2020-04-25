import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import random
import re
import tkinter as tk
from PIL import Image, ImageTk


class Codenames(tk.Tk):
    def __init__(self, size, words_file, button_height, button_width):
        super().__init__()
        self.container = tk.Frame(self, borderwidth=2)
        self.container.pack(side='top', fill='both', expand=True)
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

        self.button_height = button_height
        self.button_width = button_width
        self.n_cells = size * size
        self.size = size

        # ensure consistent order of placement and retrieval to/from self.cmap
        colors = ['yellow', 'red', 'blue', 'black']
        self.cmap = {color: idx for idx,color in enumerate(colors)}

        self.generate_legend()
        words = self.get_words(words_file)
        self.words_file = words_file
        self.vocab, self.remaining_words = self.generate_vocab(words)

        # create the replacements board first
        self.frames = {}
        self.frame_board(ReplacementBoard)
        self.show_frame(ReplacementBoard, title='Change Words')

        #image = Image.open('...png').resize((self.button_width * 20,
        #                                     self.button_height * 20))
        #self.photo = ImageTk.PhotoImage(image)

    def frame_board(self, board):
        '''Create a window of the given board'''

        frame = board(self.container, self)
        self.frames[board] = frame
        frame.grid(row=0, column=0, sticky='nsew')

        return

    def show_frame(self, page, title):
        '''Bring a given board with its title to the top,
        creating it if necessary.'''

        if page not in self.frames:
            self.frame_board(page)
        frame = self.frames[page]
        frame.tkraise()
        self.title(title)

        return

    def show_legend(self):
        '''Print the hidden legend to the console'''

        legend = []
        for label in self.legend:
            if label in ['blue', 'red']:
                legend.append(label[0].upper())
            elif label == 'yellow':
                legend.append('O')
            else:
                legend.append('X')

        legend = np.asarray(legend).reshape(self.size, self.size)
        for row in legend:
            print(' '.join(row))

        return

    def create_legend_img(self):
        '''Create and save an image of the hidden legend'''

        legend = [self.cmap[color] for color in self.legend]
        legend = np.asarray(legend).reshape(self.size, self.size)
        cmap = mpl.colors.ListedColormap(self.cmap.keys())
        img = plt.imshow(legend, cmap=cmap, alpha=.9)
        ax = plt.gca()
        ax.set_xticks(np.arange(-.5, self.size + .5, 1))
        ax.set_yticks(np.arange(-.5, self.size + .5, 1))
        ax.tick_params(axis='x', bottom=False, labelbottom=False)
        ax.tick_params(axis='y', left=False, labelleft=False)
        ax.grid(color='k', linestyle='-', linewidth=4.5)
        for loc in ['top', 'bottom', 'left', 'right']:
            ax.spines[loc].set_color(self.first_team)
            ax.spines[loc].set_linewidth(2)
        plt.savefig('./legend.png', bbox_inches='tight')

        return

    def get_words(self, words_file):
        '''Read words from a text file to use in the game'''

        with open(words_file) as f:
            all_words = f.read()
        all_words = re.sub('[,.?!]', '', all_words)
        # ignore words with dashes, numbers, etc. and long words
        words = [word.upper() for word in all_words.split()
                 if word.isalpha() and len(word) < 14]
        return words

    def generate_vocab(self, words):
        '''Randomly assign vocabulary words to colors and locations'''

        wordset = set(words)
        if len(wordset) < self.n_cells:
            raise ValueError((f'Not enough unique words in {self.words_file} '
                              f'for {self.size}x{self.size} game board'))
        vocab = [(wordset.pop(), self.legend[i], i // self.size, i % self.size)
                      for i in range(self.n_cells)]
        remaining_words = wordset

        return vocab, remaining_words

    def generate_legend(self):
        '''Determine an appropriate distribution of colors, and randomly
        determine the order to be used when assigning colors to words.'''

        teams = set(['red', 'blue'])
        first, second = (self.size - 2) * 3, ((self.size - 2) * 3) - 1
        neutral = self.n_cells - first - second - 1
        first_team, second_team = teams.pop(), teams.pop()
        print(f'{first_team.upper()} team goes first!')
        cells = [first_team] * first + [second_team] * second + \
                 ['yellow'] * neutral + ['black']
        random.shuffle(cells)
        self.first_team = first_team
        self.legend = cells
        self.count = {first_team: first,
                      second_team: second,
                      'yellow': float('inf')}

        return


class GameBoard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ##self.controller.geometry('1355x554')# exploring title display issue
        self.generate_board()
        self.color_map = {'red': 'red3', 'blue': 'blue3',
                          'yellow': 'yellow4', 'black': 'black'}

    def generate_button(self, word, color, row, col):
        '''Create an individual button and pack it into the grid'''

        cmd = lambda w=word: self.choose(w)
        self.buttons[word] = tk.Button(self,
                                       font='Helvetica 28',
                                       width=self.controller.button_width,
                                       height=self.controller.button_height,
                                       highlightbackground='light gray',
                                       text=word, command=cmd)
                                       ##, image=self.controller.photo)
        self.buttons[word].grid(row=row, column=col, sticky='nsew',
                                padx=1, pady=1)

        return

    def generate_board(self):
        '''Create a resizable game board'''

        self.buttons = {}
        for (word, color, row, col) in self.controller.vocab:
            self.rowconfigure(row, weight=1)
            self.columnconfigure(col, weight=1)
            self.generate_button(word, color, row, col)        

        return

    def choose(self, word):
        '''Display a word's hidden color, the current score, and
        game over message, if necessary, upon clicking that word'''

        index = [w for w, *_ in self.controller.vocab].index(word)
        color = self.controller.legend[index]
        ##highlightcolor=color doesn't work
        ##self.buttons[word].configure(font='Helvetica 24 bold', image=self.photo, compound="center", highlightbackground=color, width=15, height=2)
        self.buttons[word].configure(font='Helvetica 28 bold',
                                     highlightbackground=self.color_map[color],
                                     state='disabled')

        if color == 'black':
            self.controller.title('ASSASSINATED! -- GAME OVER!!!')
            print('ASSASSINATED!')
            self.end_game()
            return

        self.controller.count[color] -= 1
        score = (f"RED: {self.controller.count['red']} | "
                 f"BLUE: {self.controller.count['blue']}")
        self.controller.title(score)
        ##self.controller.geometry('1355x555')# won't work because it'll reset a resized window
        #look into -- https://stackoverflow.com/questions/27574854/passing-variables-to-tkinter-geometry-method
        # this works, but is ridiculous
        #geom = self.controller.geometry().split('+')[0]
        #w, h = geom.split('x')
        #w = int(w) + 1
        #self.controller.geometry('{}x{}'.format(w,h))
        if self.controller.count[color] <= 0:
            msg = f'{color.upper()} WINS!'
            self.controller.title(msg)
            print(msg)
            self.end_game()

        return

    def end_game(self):
        for word in self.buttons:
            self.buttons[word].configure(state='disabled')
        ##new_game = tk.Button(self, text='Play again?', highlightbackground='dark gray', cmd=None)
        ##new_game.grid(row=self.controller.size + 1, columnspan=self.controller.size)

        return


class ReplacementBoard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        desc = ('You can click on any words you\'d like to replace. '
                'Once you\'re done, click "Let\'s Play!" to begin!')
        instructions = tk.Label(self, text=desc, height=2, bg='darkgray')
        instructions.grid(row=0,
                          column=0,
                          columnspan=self.controller.size - 1,
                          sticky='we')

        start_button = tk.Button(self,
                                 font='TimesNewRoman 16 bold',
                                 width=int(self.controller.button_width * .75),
                                 height=1,
                                 text='Let\'s Play!',
                                 highlightbackground='purple',
                                 command=lambda:
                    self.controller.show_frame(GameBoard, title='Codenames!'))
        start_button.grid(row=0, column=self.controller.size - 1)
        self.gen_subs()

    def generate_button(self, word, row, col):
        button = tk.Button(self,
                           font='TimesNewRoman 16',
                           width=int(self.controller.button_width * .9),
                           height=self.controller.button_height // 2,
                           text=word,
                           highlightbackground='light gray',
                           command=lambda w=word: self.change_word(w))
                           ##image=...
        self.sub_buttons[word] = button

        self.sub_buttons[word].grid(row=row + 1, column=col)

        return

    def gen_subs(self):
        self.sub_buttons = {}
        for (word, _, row, col) in self.controller.vocab:
            self.generate_button(word, row, col)

        return

    def change_word(self, word):
        '''Replace this word with another, if there's one available'''

        word = word.upper()
        wordlist, label_list, row_list, col_list = \
            list(zip(*self.controller.vocab))
        idx = wordlist.index(word)
        try:
            new_word = self.controller.remaining_words.pop()
        except KeyError:
            for word in self.sub_buttons:
                self.sub_buttons[word].configure(state='disabled')
            msg = 'No more replacement words available. Time to play!'
            no_more_vocab = tk.Label(self,
                                     text=msg,
                                     height=2,
                                     bg='darkgray')
            no_more_vocab.grid(row=0,
                               column=0,
                               columnspan=self.controller.size - 1,
                               sticky='we')
        else:
            self.controller.vocab[idx] = (new_word,
                                          label_list[idx],
                                          row_list[idx],
                                          col_list[idx])
            self.gen_subs()

        return


if __name__ == '__main__':

    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('size', type=int, default=5, help='Number of rows/columns to use in a square gameboard')
    parser.add_argument('words_file', help='Text file from which to take words to use in the game')
    parser.add_argument('--height', type=int, default=3, choices=range(2, 8), help='Button height to use')
    parser.add_argument('--width', type=int, default=15, choices=range(15, 30), help='Button width to use')
    parser.add_argument('--codemasters', type=str, nargs='+', help='Email address(es) to which to send the legend')
    args = parser.parse_args()

    game = Codenames(size=args.size, words_file=args.words_file, button_height=args.height, button_width=args.width)

    if args.codemasters:
        game.create_legend_img()
        from email.message import EmailMessage
        import os
        import smtplib

        EMAIL_ADDR = os.environ.get('EMAIL_ADDR')
        EMAIL_PW = os.environ.get('EMAIL_PW')

        msg = EmailMessage()
        msg['Subject'] = 'Codenames legend'
        msg['From'] = f'Codemaster HQ <{EMAIL_ADDR}>'
        msg['To'] = args.codemasters
        msg.set_content('The legend is attached. Border color indicates which team goes first. Good luck!')

        with open('./legend.png', 'rb') as f:
            img_data = f.read()

        msg.add_attachment(img_data, filename='legend.png', maintype='image', subtype='png')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDR, EMAIL_PW)
            smtp.send_message(msg)
        os.remove('./legend.png')

    else:
        game.show_legend()
    game.mainloop()
    sys.exit()

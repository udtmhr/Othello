import tkinter as tk
from tkinter import messagebox
from board import Board
from computer import Com
from globalvar import *

WIDTH = 840
HEIGHT = 640
CANVAS_SIZE = 640
FONT = ("MEゴシック", "35", "bold")

class Othello():
    def __init__(self):
        super().__init__()
        self.board = Board()
        self.com = Com(self.board)

        self.create_root()
        self.create_menu()
        self.create_canvas()
        self.create_widget()
        self.init_board()

        self.event()

    def create_root(self):
        self.root = tk.Tk()
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.title("オセロ")

    def create_canvas(self):
        frame_canvas = tk.Frame(
            self.root,
            height=CANVAS_SIZE,
            width=CANVAS_SIZE,
        )

        frame_canvas.propagate(False)
        frame_canvas.pack(side=tk.RIGHT)

        self.canvas = tk.Canvas(
                frame_canvas,
                width=CANVAS_SIZE, 
                height=CANVAS_SIZE,
                bg = "green",
                bd=5,
                relief="raised",
        )
        self.canvas.pack()

    def create_widget(self):
        frame_widget = tk.Frame(
            self.root,
            height=HEIGHT,
            width=WIDTH - CANVAS_SIZE,
            bg="green"
        )

        frame_widget.propagate(False)
        frame_widget.pack(side=tk.LEFT)

        self.black_var = tk.StringVar(frame_widget)
        self.black_var.set(f"黒:2")
        black_label = tk.Label(
            frame_widget,
            textvariable=self.black_var,
            fg="black",
            bg="green",
            font=FONT,
        )

        self.white_var = tk.StringVar(frame_widget)
        self.white_var.set(f"白:2")
        white_label = tk.Label(
            frame_widget,
            textvariable=self.white_var,
            fg="white",
            bg="green",
            font=FONT,
        )

        self.turn_var = tk.StringVar(frame_widget)
        self.turn_var.set(f"黒の手番")
        turn_label = tk.Label(
            frame_widget,
            textvariable=self.turn_var,
            fg="black",
            bg="white",
            font=FONT,
        )

        white_label.pack(side=tk.TOP)
        turn_label.pack(side=tk.TOP, pady=200)
        black_label.pack(side=tk.BOTTOM)
    
    def create_menu(self):
        menu = tk.Menu(self.root, tearoff=False)
        self.root.config(menu=menu)
        diff = tk.Menu(self.root, tearoff=False)
        re = tk.Menu(self.root, tearoff=False)
        menu.add_cascade(label="難易度", menu=diff)
        menu.add_cascade(label="再戦", menu=re)
        re.add_command(label="再戦", command=self.rematch)
        diff.add_radiobutton(label="簡単", command=lambda : self.select_com(1))
        diff.add_radiobutton(label="普通", command=lambda : self.select_com(3))
        diff.add_radiobutton(label="難しい", command=lambda : self.select_com(6))
    
    def select_color(self, color):
        self.player_color = color
        self.com_color = color * -1

    def init_board(self):
        mass_size = CANVAS_SIZE / SIZE
        for i in range(SIZE * SIZE):
            h = i // SIZE
            w = i - h * SIZE
            h *= mass_size
            w *= mass_size
            self.canvas.create_rectangle(w, h, w + mass_size, h + mass_size, fill="green", tags=f"mass_{i}", outline="black")
            if i == 19 or i == 26 or i == 37 or i == 44:
                self.canvas.itemconfig(f"mass_{i}", fill="spring green", stipple="gray25")
            self.canvas.create_oval(w, h, w + mass_size, h + mass_size, fill="black", tags=f"stone_{i}", width=0, state=tk.HIDDEN) 
            self.canvas.scale(f"stone_{i}", w + mass_size / 2, h + mass_size / 2, 0.8, 0.8 )
            if i == 27 or i == 36:
                self.canvas.itemconfig(f"stone_{i}", fill="white", state=tk.NORMAL)
            elif i == 28 or i == 35:
                self.canvas.itemconfig(f"stone_{i}", state=tk.NORMAL)     
       
    def disp_board(self):
        mass_size = CANVAS_SIZE / SIZE
        legal = self.board.legal_board(self.board.ob, self.board.pb)
        for i in range(SIZE * SIZE):
            if legal & (0x8000000000000000 >> i):
                self.canvas.itemconfig(f"mass_{i}", fill="spring green", stipple="gray25")
            else:
                self.canvas.itemconfig(f"mass_{i}", fill="green")
            pcolor, ocolor = ("black", "white") if self.board.turn == BLACK else ("white", "black")
            if self.board.pb & (0x8000000000000000 >> i):
                self.canvas.itemconfig(f"stone_{i}", fill=pcolor, state=tk.NORMAL)
            elif self.board.ob & (0x8000000000000000 >> i):
                self.canvas.itemconfig(f"stone_{i}", fill=ocolor, state=tk.NORMAL)
    
    def next_player(self):
        if (next := self.board.next_player()) == 0:
            pass
        elif next == 1:
            player = "黒" if self.board.turn * -1 == BLACK else "白"
            messagebox.showinfo(message=f"{player}のおける場所がありません。スキップします。")
        else:
            self.gameset()
            self.board.turn = 0
        
    def gameset(self):
        if self.black > self.white:
            massage = "勝者:黒！"
        elif self.black < self.white:
            massage = "勝者:白！"
        else:
            massage = "引き分け！"
        messagebox.showinfo(
            title="結果",
            message=f"ゲーム終了！\n黒{self.black}:白{self.white}\n{massage}"
        )
    
    def change_disp(self):
        self.disp_board()
        self.black_var.set(f"黒:{self.board.black}")
        self.white_var.set(f"白:{self.board.white}")
        self.next_player()
        turn = "黒" if self.board.turn == BLACK else "白"
        self.turn_var.set(f"{turn}の手番")
     
    def select_com(self, d):
        self.com = Com(self.board, d)
    
    def com_turn(self):
        pos = self.com.search(self.com.d)
        rev = self.board.reverse(pos)
        self.board.put(pos, rev)
        self.board.white = self.board.pb.bit_count()
        self.board.black = self.board.ob.bit_count()
        self.change_disp()

        if self.board.turn == WHITE:
            self.canvas.after(1000, self.com_turn)
    
    def click(self, event):
        mass_size = CANVAS_SIZE / SIZE
        x = int(event.x / mass_size)
        y = int(event.y / mass_size)
        pos = self.board.to_bin(x, y)
        if self.board.check_put(pos):
            rev = self.board.reverse(pos)
            self.board.put(pos, rev)
            self.board.black = self.board.pb.bit_count()
            self.board.white = self.board.ob.bit_count()
            self.change_disp()

        if self.board.turn == WHITE:
            self.canvas.after(1000, self.com_turn)

    def event(self):
        self.canvas.bind("<Button-1>", self.click)
    
    def rematch(self):
        self.board.init()
        for i in range(SIZE * SIZE):
            self.canvas.itemconfig(f"stone_{i}", fill="black", state=tk.HIDDEN)
            if i == 19 or i == 26 or i == 37 or i == 44:
                self.canvas.itemconfig(f"mass_{i}", fill="spring green", stipple="gray25")
            elif i == 27 or i == 36:
                self.canvas.itemconfig(f"stone_{i}", fill="white", state=tk.NORMAL)
            elif i == 28 or i == 35:
                self.canvas.itemconfig(f"stone_{i}", state=tk.NORMAL) 
            else:
                self.canvas.itemconfig(f"mass_{i}", fill="green")



if __name__ == "__main__":
    othello = Othello()
    othello.root.mainloop()

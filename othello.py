import tkinter as tk
from tkinter import messagebox
from board import Board
from computer import Com
from globalvar import *

WIDTH = 840
HEIGHT = 640
CANVAS_SIZE = 640
FONT = ("MEゴシック", "35", "bold")
COLOR = {BLACK: "黒", WHITE: "白"}

class Othello():
    def __init__(self):
        super().__init__()
        self.board = Board()
        self.com = Com(self.board)
        self.click_interval = 1000
        self.last_click_time = 0

        self.create_root()
        self.create_menu()
        self.create_canvas()
        self.create_widget()
        self.init_board()

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
                state=tk.DISABLED,
        )

        self.canvas.pack(side=tk.RIGHT)

    def create_widget(self):
        frame_widget = tk.Frame(
            self.root,
            height=HEIGHT,
            width=WIDTH - CANVAS_SIZE,
            bg="green"
        )

        frame_widget.propagate(False)
        frame_widget.pack(side=tk.LEFT)

        start_button = tk.Button(
            frame_widget,
            text="ゲーム開始",
            width=10, 
            height=2,
            font=("MEゴシック", "20", "bold"),
            relief="raised",
            command=self.start_game
        )

        black_var = tk.StringVar(frame_widget)
        black_var.set(f"黒:2")
        black_label = tk.Label(
            frame_widget,
            textvariable=black_var,
            fg="black",
            bg="green",
            font=FONT,
        )

        white_var = tk.StringVar(frame_widget)
        white_var.set(f"白:2")
        white_label = tk.Label(
            frame_widget,
            textvariable=white_var,
            fg="white",
            bg="green",
            font=FONT,
        )

        turn_var = tk.StringVar(frame_widget)
        turn_var.set(f"黒の手番")
        turn_label = tk.Label(
            frame_widget,
            textvariable=turn_var,
            fg="black",
            bg="white",
            font=FONT,
        )

        white_label.place(x=50, y=10)
        turn_label.place(x=0, y=200)
        start_button.place(x=12, y=350)
        black_label.place(x=50, y=570)

        self.var_lst = [turn_var, black_var, white_var]
    
    def create_menu(self):
        menu = tk.Menu(self.root, tearoff=False)
        self.root.config(menu=menu)
        diff = tk.Menu(self.root, tearoff=False)
        menu.add_cascade(label="難易度", menu=diff)
        diff.add_radiobutton(label="簡単", command=lambda: self.select_com(1))
        diff.add_radiobutton(label="普通", command=lambda: self.select_com(3))
        diff.add_radiobutton(label="難しい", command=lambda: self.select_com(6))

        rematch = tk.Menu(self.root, tearoff=False)
        menu.add_cascade(label="再戦", menu=rematch)
        rematch.add_command(label="再戦", command=self.rematch)

        color = tk.Menu(self.root, tearoff=False)
        menu.add_cascade(label="手番", menu=color)
        color.add_radiobutton(label="先手", command=lambda: self.select_color(BLACK))
        color.add_radiobutton(label="後手", command=lambda: self.select_color(WHITE))
        
    
    def select_color(self, color):
        self.board.player_color = color
        self.board.com_color = color * -1

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
            player = COLOR[self.board.turn * -1] 
            messagebox.showinfo(message=f"{player}のおける場所がありません。スキップします。")
        else:
            self.gameset()
            self.board.turn = self.board.player_color
        
    def gameset(self):
        if self.board.player_score > self.board.com_score:
            massage = "勝者:黒！"
        elif self.board.player_score < self.board.com_score:
            massage = "勝者:白！"
        else:
            massage = "引き分け！"
        messagebox.showinfo(
            title="結果",
            message=f"ゲーム終了！\n{COLOR[self.board.player_color]}{self.board.player_score}:\
            {COLOR[self.board.com_color]}{self.board.com_score}\
            {massage}"
        )
    
    def change_disp(self):
        self.disp_board()
        self.var_lst[self.board.player_color].set(f"{COLOR[self.board.player_color]}:{self.board.player_score}")
        self.var_lst[self.board.com_color].set(f"{COLOR[self.board.com_color]}:{self.board.com_score}")
        self.next_player()
        self.var_lst[0].set(f"{COLOR[self.board.turn]}の手番")
     
    def select_com(self, d):
        self.com = Com(self.board, d)
    
    def com_turn(self):
        pos = self.com.search(self.com.d)
        rev = self.board.reverse(pos)
        self.board.put(pos, rev)
        self.board.com_score = self.board.pb.bit_count()
        self.board.player_score = self.board.ob.bit_count()
        self.change_disp()
        if self.board.turn == self.board.com_color:
            self.canvas.after(1000, self.com_turn)
        else:
            self.canvas["state"] = tk.NORMAL
    
    def click(self, event):
        mass_size = CANVAS_SIZE / SIZE
        x = int(event.x / mass_size)
        y = int(event.y / mass_size)
        pos = self.board.to_bin(x, y)
        if self.board.check_put(pos) and self.canvas["state"] == tk.NORMAL:
            self.canvas["state"] = tk.DISABLED
            rev = self.board.reverse(pos)
            self.board.put(pos, rev)
            self.board.player_score = self.board.pb.bit_count()
            self.board.com_score = self.board.ob.bit_count()
            self.change_disp()

            if self.board.turn == self.board.com_color:
                self.canvas.after(1000, self.com_turn)
            else:
                self.canvas["state"] = tk.NORMAL

    def event(self):
        self.canvas.bind("<Button-1>", self.click)

    def start_game(self):
        if self.board.player_color is None:
            messagebox.showinfo(message="先手か後手を選択してください。")
        else:
            messagebox.showinfo(message="ゲーム開始！")
            if self.board.player_color == WHITE:
                self.canvas.after(500, self.com_turn())
            else:
                self.canvas["state"] = tk.NORMAL
            self.event()

    def rematch(self):
        self.canvas.delete("all")
        self.canvas["state"] = tk.DISABLED
        self.init_board()
        self.board.init()
        self.start_game()
        

if __name__ == "__main__":
    othello = Othello()
    othello.start_game()
    othello.root.mainloop()

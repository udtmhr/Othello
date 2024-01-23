import tkinter as tk
from tkinter import messagebox
from board import Board, SIZE, BLACK, WHITE
from board_env import Othello
from player.computer import Com
from player.CNN_com import CNNCom
from player.mcs import MCS, MCTS


WIDTH = 840
HEIGHT = 640
CANVAS_SIZE = 640
FONT = ("MEゴシック", "35", "bold")
COLOR = {BLACK: "黒", WHITE: "白"}

class OthelloApp:
    def __init__(self):
        self.board = Othello()
        self.com = None

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

        self.start_button = tk.Button(
            frame_widget,
            text="ゲーム開始",
            width=10, 
            height=2,
            font=("MEゴシック", "20", "bold"),
            relief="raised",
            command=self.start_game,
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
        self.start_button.place(x=12, y=350)
        black_label.place(x=50, y=570)

        self.var_lst = [turn_var, black_var, white_var]
    
    def create_menu(self):
        menu = tk.Menu(self.root, tearoff=False)
        self.root.config(menu=menu)
        diff = tk.Menu(self.root, tearoff=False)
        menu.add_cascade(label="難易度", menu=diff)
        diff.add_radiobutton(label="超簡単", command=lambda: self.select_com(1))
        diff.add_radiobutton(label="簡単", command=lambda: self.select_com(3))
        diff.add_radiobutton(label="普通", command=lambda: self.select_com(6))
        diff.add_radiobutton(label="難しい", command=lambda: self.select_com(-1))
        diff.add_radiobutton(label="最難", command=lambda: self.select_com(0))

        rematch = tk.Menu(self.root, tearoff=False)
        menu.add_cascade(label="再戦", menu=rematch)
        rematch.add_command(label="再戦", command=self.rematch)

        color = tk.Menu(self.root, tearoff=False)
        menu.add_cascade(label="手番", menu=color)
        color.add_radiobutton(label="先手", command=lambda: self.board.set_color(BLACK))
        color.add_radiobutton(label="後手", command=lambda: self.board.set_color(WHITE))

    def select_com(self, d):
        if d == -1:
            self.com = MCTS(self.board, 1000, 50)
        elif d:
            self.com = Com(self.board, d)
        else:
            self.com = CNNCom(self.board)
        
    def init_board(self):
        mass_size = CANVAS_SIZE / SIZE
        for i in range(SIZE * SIZE):
            h = i // SIZE
            w = i - h * SIZE
            h *= mass_size
            w *= mass_size
            self.canvas.create_rectangle(w, h, w + mass_size, h + mass_size, fill="green", tags=f"mass_{i}", outline="black", activefill="spring green", activestipple="gray25")
            if i == 19 or i == 26 or i == 37 or i == 44:
                self.canvas.itemconfig(f"mass_{i}", fill="green yellow", stipple="gray25")
            self.canvas.create_oval(w, h, w + mass_size, h + mass_size, fill="black", tags=f"stone_{i}", width=0, state=tk.HIDDEN) 
            self.canvas.scale(f"stone_{i}", w + mass_size / 2, h + mass_size / 2, 0.8, 0.8 )
            if i == 27 or i == 36:
                self.canvas.itemconfig(f"stone_{i}", fill="white", state=tk.NORMAL)
            elif i == 28 or i == 35:
                self.canvas.itemconfig(f"stone_{i}", state=tk.NORMAL)     
       
    def update_board(self):
        legal = self.board.legal_board(self.board.ob, self.board.pb)
        for i in range(SIZE * SIZE):
            mask = 0x8000000000000000 >> i
            if legal & mask:
                self.canvas.itemconfig(f"mass_{i}", fill="green yellow", stipple="gray25")
            else:
                self.canvas.itemconfig(f"mass_{i}", fill="green")
            colors = ["", "black", "white"]
            if self.board.pb & mask:
                self.canvas.itemconfig(f"stone_{i}", fill=colors[self.board.turn], state=tk.NORMAL)
            elif self.board.ob & mask:
                self.canvas.itemconfig(f"stone_{i}", fill=colors[self.board.turn * -1], state=tk.NORMAL)
    
    def next_player(self):
        if (next_player := self.board.next_player()) == self.board.turn * -1:
            self.board.change_turn()        
        elif next_player == self.board.turn:
            messagebox.showinfo(message=f"{COLOR[self.board.turn * -1]}のおける場所がありません。スキップします。")
        else:
            self.gameset()
            self.board.turn = self.board.player_color

    def gameset(self):
        if (winner := self.board.get_winner()):
            massage = f"勝者:{COLOR[winner]}!"
        else:
            massage = "引き分け！"
        self.canvas["state"] = tk.DISABLED
        messagebox.showinfo(
            title="結果",
            message=f"ゲーム終了！\n黒　{self.board.score[BLACK]}:"\
            f"白{self.board.score[WHITE]}\n"\
            f"{massage}"
        )
    
    def update_disp(self):
        self.update_board()
        self.var_lst[self.board.player_color].set(f"{COLOR[self.board.player_color]}:{self.board.score[self.board.player_color]}")
        self.var_lst[self.board.com_color].set(f"{COLOR[self.board.com_color]}:{self.board.score[self.board.com_color]}")
        self.next_player()
        self.var_lst[0].set(f"{COLOR[self.board.turn]}の手番")
    
    def com_turn(self):
        pos = self.com.search()
        rev = self.board.reverse(pos)
        self.board.put(pos, rev)
        self.update_disp()
        if self.board.turn == self.board.com_color:
            self.canvas.after(1500, self.com_turn)
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
            self.update_disp()

            if self.board.turn == self.board.com_color:
                self.canvas.after(1000, self.com_turn)
            else:
                self.canvas["state"] = tk.NORMAL

    def event(self):
        self.canvas.bind("<Button-1>", self.click)

    def start_game(self):
        if self.board.player_color == 0 or self.com is None:
            messagebox.showinfo(message="先手か後手、難易度を選択してください。")
        else:
            messagebox.showinfo(message="ゲーム開始！")
            self.start_button["state"] = tk.DISABLED
            if self.board.player_color == WHITE:
                self.canvas.after(500, self.com_turn())
            else:
                self.canvas["state"] = tk.NORMAL
            self.event()

    def rematch(self):
        self.canvas.delete("all")
        self.canvas["state"] = tk.DISABLED
        self.start_button["state"] = tk.NORMAL
        self.init_board()
        self.board.__init__()

if __name__ == "__main__":
    othello = OthelloApp()
    othello.start_game()
    othello.root.mainloop()

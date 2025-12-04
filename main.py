import sys
import os

# Add src to python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from othello.gui.app import OthelloApp

if __name__ == "__main__":
    othello = OthelloApp()
    othello.start_game()
    othello.root.mainloop()

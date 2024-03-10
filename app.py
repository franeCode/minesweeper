import tkinter as tk
from minesweeper import Minesweeper

def main():
    root = tk.Tk()
    root.title("Minesweeper")
 
    rows = 8
    cols = 8
    mines = 10

    minesweeper_game = Minesweeper(root, rows, cols, mines)

    root.mainloop()

if __name__ == "__main__":
    main()
import tkinter as tk
import random
from PIL import Image, ImageTk, ImageFilter

class Minesweeper:
    def __init__(self, master, rows, cols, mines):
        self.master = master
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.board = [[0 for _ in range(cols)] for _ in range(rows)]
        self.buttons = [[None for _ in range(cols)] for _ in range(rows)]

        self.create_widgets()

    def create_widgets(self):
        # Initialize the game board and place mines
        self.initialize_board()

        # Create a frame for the game board
        self.board_frame = tk.Frame(self.master)
        self.board_frame.grid(row=0, column=0, rowspan=self.rows, columnspan=self.cols)

        for row in range(self.rows):
            for col in range(self.cols):
                # Create buttons or labels for each cell in the grid
                button = tk.Button(self.board_frame, text="", width=3, height=1)
                button.grid(row=row, column=col)

                # Store the button reference in the 2D list
                self.buttons[row][col] = button

                # Bind left-click event
                button.bind("<Button-1>", lambda event, r=row, c=col: self.on_left_click(r, c))
                # Bind right-click event
                button.bind("<Button-2>", lambda event, r=row, c=col: self.on_right_click(r, c))


        # Set weights for rows and columns
        for i in range(self.rows):
            self.master.grid_rowconfigure(i, weight=1)  # Adjust weight to your preference

        for j in range(self.cols):
            self.master.grid_columnconfigure(j, weight=1)

        print("Buttons:")
        print(self.buttons)
        print("Board:")
        print(self.board)

    def initialize_board(self):
        # Place mines randomly on the game board
        mine_positions = random.sample(range(self.rows * self.cols), self.mines)
        for position in mine_positions:
            row = position // self.cols
            col = position % self.cols
            self.board[row][col] = "M"
            
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] != "M":
                    self.board[i][j] = str(int(self.board[i][j]) + 1)



        print("Initialized Board:")
        print(self.board)

    def on_left_click(self, row, col):
        # Check if the clicked cell is a mine
        if self.board[row][col] == "M":
            self.reveal_all_mines()
            self.game_over()
        else:
            # Check and reveal the number of adjacent mines
            adjacent_mines = self.count_adjacent_mines(row, col)
            self.update_cell(row, col, str(adjacent_mines))

            # If no adjacent mines, recursively reveal neighboring cells
            if adjacent_mines == 0:
                self.reveal_empty_cells(row, col)

    def on_right_click(self, row, col):
        # Check if the clicked cell is not revealed
        if not self.is_cell_revealed(row, col):
            # Check if the cell is flagged, if so, unflag it
            if self.buttons[row][col]['text'] == "F":
                self.buttons[row][col].config(text="")
            else:
                # If the cell contains a mine, mark it with "M", else, flag it with "F"
                if self.board[row][col] == "M":
                    self.buttons[row][col].config(text="M", state=tk.DISABLED)
                else:
                    self.buttons[row][col].config(text="F")

    def count_adjacent_mines(self, row, col):
        # Count the number of adjacent mines to a cell
        count = 0
        for i in range(max(0, row - 1), min(self.rows, row + 2)):
            for j in range(max(0, col - 1), min(self.cols, col + 2)):
                if self.board[i][j] == "M":
                    count += 1
        return count

    def update_cell(self, row, col, value):
        button = self.buttons[row][col] 
        
        color_dict = {
            "1": "#0000FF",  # blue
            "2": "#008000",  # green
            "3": "#FF0000",  # red
            "4": "#000080",  # navy
            "5": "#800000",  # maroon
            "6": "#800080"   # purple
        }

        button_color = color_dict.get(value, "#000000")
        print(f"Updating cell at ({row}, {col}) with value {value} and color {button_color}")

        button.config(text=value, fg=button_color)

    def reveal_empty_cells(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols and not self.is_cell_revealed(row, col):
            # Check if the cell is within the grid bounds and is not already revealed
            self.update_cell(row, col, " ")

            for i in range(max(0, row - 1), min(self.rows, row + 2)):
                for j in range(max(0, col - 1), min(self.cols, col + 2)):
                    if self.board[i][j] == 0 and not self.is_cell_revealed(i, j):
                        self.reveal_empty_cells(i, j)
                    elif self.board[i][j] != "M" and not self.is_cell_revealed(i, j):
                        self.update_cell(i, j, str(self.board[i][j]))

    def reveal_all_mines(self):
        # Reveal all mines on the game board
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] == "M":
                    self.update_cell(i, j, "X")

    def is_cell_revealed(self, row, col):
        return self.buttons[row][col]['text'] != " "

    def game_over(self):
        # Create a "Game Over" label
        game_over_label = tk.Label(self.master, text="Game Over!", font=("Helvetica", 16), bg="lightgray")
        game_over_label.grid(row=0, column=0, rowspan=self.rows, columnspan=self.cols, sticky="nsew")
        
        # Create emoji label
        sad_emoji_image = Image.open("media/sad_emoji.png")
        sad_emoji_image = sad_emoji_image.resize((50, 50), Image.LANCZOS)

        emoji_image = ImageTk.PhotoImage(sad_emoji_image)
        emoji_label = tk.Label(self.master, image=emoji_image, bg="lightgray")
        emoji_label.image = emoji_image
        emoji_label.grid(row=self.rows, column=0, rowspan=1, columnspan=self.cols, sticky="nsew")

        # Create a "Play Again" button
        play_again_button = tk.Button(self.master, text="Play Again", command=self.reset_game, bg="lightgray")
        play_again_button.grid(row=self.rows+1, column=0, rowspan=1, columnspan=self.cols, sticky="nsew")

        # Disable resizing of the rows and columns
        for i in range(self.rows + 1):
            self.master.grid_rowconfigure(i, weight=0)

        for j in range(self.cols + 1):
            self.master.grid_columnconfigure(j, weight=0)


    def reset_game(self):
        # Destroy the game over frame
        for widget in self.master.winfo_children():
            widget.destroy()

        # Recreate the game board and start a new game
        self.create_widgets()


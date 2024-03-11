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
        self.emoji_path = "media/happy_emoji.png"

        self.create_widgets()

    def create_widgets(self):
        # Initialize the game board and place mines
        self.initialize_board()

        # Create a label to display the number of mines left
        self.mines_left_label = tk.Label(self.master, text=f"Mines Left: {self.mines}", font=("Helvetica", 14), bg="lightgray")
        self.mines_left_label.grid(row=0, column=self.cols + 1, sticky="nsew")
    
        # Create a frame for the emoji grid
        self.emoji_frame = tk.Frame(self.master)
        self.emoji_frame.grid(row=0, column=0, rowspan=1, columnspan=self.cols)

        # Load the happy emoji image
        self.load_emoji()

        # Create a label for the emoji
        self.emoji_label = tk.Label(self.emoji_frame, image=self.emoji_image, bg="lightgray")
        self.emoji_label.image = self.emoji_image
        self.emoji_label.grid(row=0, column=0, rowspan=1, columnspan=self.cols, sticky="nsew")

        # Create a frame for the game board
        self.board_frame = tk.Frame(self.master)
        self.board_frame.grid(row=1, column=0, rowspan=self.rows, columnspan=self.cols)

        for row in range(self.rows):
            for col in range(self.cols):
                # Create buttons or labels for each cell in the grid
                button = tk.Button(self.board_frame, text="", width=1, height=1)
                button.grid(row=row, column=col)

                # Store the button reference in the 2D list
                self.buttons[row][col] = button

                # Bind left-click event
                button.bind("<Button-1>", lambda event, r=row, c=col: self.on_left_click(r, c))
                # Bind right-click event
                button.bind("<Button-2>", lambda event, r=row, c=col: self.on_right_click(r, c))

        # Set weights for rows and columns
        for i in range(2):
            self.master.grid_rowconfigure(i, weight=1)

        for j in range(self.cols):
            self.master.grid_columnconfigure(j, weight=1)

        print("Buttons:")
        print(self.buttons)
        print("Board:")
        print(self.board)

    def load_emoji(self):
        # Load the emoji image
        self.emoji_image = ImageTk.PhotoImage(Image.open(self.emoji_path).resize((50, 50), Image.LANCZOS))

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
                    self.board[i][j] = "0"  # Make sure it's a string "0", not an integer

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
            if adjacent_mines == 0 and not self.is_cell_revealed(row, col):
                # If no adjacent mines, recursively reveal neighboring cells
                self.reveal_empty_cells(row, col)
            else:
                self.update_cell(row, col, str(adjacent_mines))
                self.check_game_won()

    def on_right_click(self, row, col):
        # Check if the clicked cell is not revealed
        if not self.is_cell_revealed(row, col):
            # Check if the cell is flagged, if so, unflag it
            if self.buttons[row][col]['text'] == "F":
                self.buttons[row][col].config(text="")
                self.update_mines_left(1)
            else:
                # If the cell contains a mine, mark it with "M", else, flag it with "F"
                if self.board[row][col] == "M":
                    self.buttons[row][col].config(text="M", state=tk.DISABLED)
                    self.update_mines_left(-1)
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

    def update_mines_left(self, increment):
        # Update the mines left count and update the label
        self.mines += increment
        self.mines_left_label.config(text=f"Mines Left: {self.mines}")
        
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
            button = self.buttons[row][col]
            button.config(text="", bg="#404040", bd=1)  # Darker background for cells with 0 value

            for i in range(max(0, row - 1), min(self.rows, row + 2)):
                for j in range(max(0, col - 1), min(self.cols, col + 2)):
                    if not self.is_cell_revealed(i, j) and self.buttons[i][j]['state'] != tk.DISABLED:
                        if self.board[i][j] == "0":
                            self.reveal_empty_cells(i, j)
                        elif self.board[i][j] != "M":
                            adjacent_mines = self.count_adjacent_mines(i, j)
                            self.buttons[i][j].config(text=str(adjacent_mines), bg="#D3D3D3", bd=1)  # Light gray background with black borders

    def reveal_all_mines(self):
        # Reveal all mines on the game board
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] == "M":
                    self.update_cell(i, j, "X")

    def is_cell_revealed(self, row, col):
        return self.buttons[row][col]['text'] != " "

    def game_over(self):
        # Change the emoji to sad
        self.emoji_path = "media/sad_emoji.png"
        self.load_emoji()

        # Update the emoji label to display the sad emoji
        self.emoji_label.config(image=self.emoji_image)
        
        # Reset the game after clicking on the sad emoji
        self.emoji_label.bind("<Button-1>", lambda event: self.reset_game())


    def reset_game(self):
        # Change the emoji back to happy
        self.emoji_path = "media/happy_emoji.png"
        self.load_emoji()

        # Destroy the game over frame and recreate the game board
        for widget in self.master.winfo_children():
            widget.destroy()

        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.buttons = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.initialize_board()
        self.create_widgets()
        self.update_mines_left(0)




import tkinter as tk
import random
from PIL import Image, ImageTk, ImageFilter

class Minesweeper:
    def __init__(self, master, rows, cols, mines):
        self.master = master
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.total_mines = 10
        self.flagged_cells = 0
        self.board = [[0 for _ in range(cols)] for _ in range(rows)]
        self.buttons = [[None for _ in range(cols)] for _ in range(rows)]
        self.emoji_path = "media/smiley.png"
        self.time = 0
        self.is_game_over = False

        self.create_widgets()

    def create_widgets(self):
        print("Binding right-click event")
        # Initialize the game board and place mines
        self.initialize_board()

        # Create a label to display the number of mines left
        self.mines_left_label = tk.Label(self.master, text=self.mines, bd=2, bg="#500028", fg="red", font=("Fixedsys", 24), relief="ridge", highlightbackground="black")
        self.mines_left_label.grid(row=0, column=1, sticky="w")
        
        # Create a frame for the emoji grid
        self.emoji_frame = tk.Frame(self.master)
        self.emoji_frame.grid(row=0, column=0, rowspan=1, columnspan=self.cols)

        # Load the happy emoji image
        self.load_emoji()
        
        self.mine_image = ImageTk.PhotoImage(Image.open("media/mine.png").resize((30,30), Image.NEAREST))
        self.flag_image = ImageTk.PhotoImage(Image.open("media/flag.png").resize((30,30), Image.NEAREST))

        # Create a label for the emoji
        self.emoji_label = tk.Label(self.emoji_frame, image=self.emoji_image, bg="lightgray", bd=2, relief="ridge", highlightbackground="black")
        self.emoji_label.image = self.emoji_image
        self.emoji_label.grid(row=0, column=0, rowspan=1, columnspan=self.cols)
        
        # Create a label to display the time
        self.time_label = tk.Label(self.master, text="000", bd=2, bg="#500028", fg="red", font=("Fixedsys", 24), relief="ridge", highlightbackground="black")
        self.time_label.grid(row=0, column=6, sticky="e")

        # Set minimum size for the columns
        self.master.grid_columnconfigure(1, minsize=200)  
        self.master.grid_columnconfigure(6, minsize=200)

        # Create a frame for the game board
        self.board_frame = tk.Frame(self.master)
        self.board_frame.grid(row=1, column=0, rowspan=self.rows, columnspan=self.cols)
        
        self.update_time()

        for row in range(self.rows):
            for col in range(self.cols):
                # Create buttons or labels for each cell in the grid
                button = tk.Button(self.board_frame, text="", compound=tk.CENTER, width=1, height=1)
                button.grid(row=row, column=col,sticky="news")
                # button.config(compound=tk.CENTER, width=25, height = 25)

                self.buttons[row][col] = button

                button.bind("<Button-1>", lambda event, r=row, c=col: self.on_left_click(r, c))
                button.bind("<Button-3>", lambda event, r=row, c=col: self.on_right_click(r, c))

        # Set weights for rows and columns
        for i in range(self.rows):
            self.master.grid_rowconfigure(i, weight=1)

        for j in range(self.cols):
            self.master.grid_columnconfigure(j, weight=1)

    def load_emoji(self):
        # Load the emoji image
        self.emoji_image = ImageTk.PhotoImage(Image.open(self.emoji_path).resize((50, 50), Image.LANCZOS))

    def initialize_board(self):
        # Place mines randomly on the game board
        mine_positions = random.sample(range(self.rows * self.cols), self.mines)
        
        print(self.mines)
        for position in mine_positions:
            row = position // self.cols
            col = position % self.cols
            self.board[row][col] = "M"

        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] != "M":
                    
                    self.board[i][j] = self.count_adjacent_mines(i, j) 
                
                           

        print("Initialized Board:")
        for p in self.board:
            print (p)

    def on_left_click(self, row, col):
        if self.is_game_over:
            return
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
                self.update_cell(row, col, adjacent_mines)
        
        # Update the mines left count and check if the game is won
        self.update_mines_left(0)
    
    def on_right_click(self, row, col):
        if self.is_game_over:
            return
        # Check if the clicked cell is not revealed and the number of flagged cells is less than 10
        if not self.is_cell_revealed(row, col) and self.flagged_cells < self.total_mines:
            # Check if the cell already has a flag image
            if self.buttons[row][col]['image']:
                # Remove the flag image
                self.buttons[row][col].config(image="", text="")
                self.update_mines_left(1)
                self.flagged_cells -= 1  
            else:
                # Add the flag image
                self.buttons[row][col].config(image=self.flag_image, compound=tk.CENTER)
                self.update_mines_left(-1)
                self.flagged_cells += 1 
        # in this function, check if the last mine is flagged, if so, call game_won
        self.game_won()

    def count_adjacent_mines(self, row, col):
        # Count the number of adjacent mines to a cell
        count = 0
        for i in range(max(0, row - 1), min(self.rows, row + 2)):
            for j in range(max(0, col - 1), min(self.cols, col + 2)):
                if self.board[i][j] == "M":
                    count += 1
        return count

    def update_time(self):
        if not self.is_game_over:
            self.time += 1
            
            # Format the time into minutes and seconds
            # minutes = self.time // 60
            # seconds = self.time % 60
            # time_str = f"{seconds:003}"
            
            time_str = f"{self.time:03}"
            
            # Update the time label text
            self.time_label.config(text=time_str)
        
        # Schedule the update_time method to be called again after 1000 milliseconds (1 second)
        self.master.after(1000, self.update_time)
        
    def reset_time(self):
        # Reset the time counter to 0
        self.time = 0
        
    def update_mines_left(self, increment):
        # print(f"Updating mines left by {increment}")
        self.mines += increment
        self.mines_left_label.config(text=self.mines)
        
    def update_cell(self, row, col, value):
        button = self.buttons[row][col]

        color_dict = {
            1: "#0000FF",  # blue
            2: "#008000",  # green
            3: "#FF0000",  # red
            4: "#000080",  # navy
            5: "#800000",  # maroon
            6: "#800080"   # purple
        }

        button_color = color_dict.get(value, "#000000")
        # print(f"Updating cell at ({row}, {col}) with value {value} and color {button_color}")

        if value == "M":
            # self.mine_image = Image.open("media/mine.png")
            button.config(image=self.mine_image, compound=tk.CENTER)
            
        else:
            button.config(text=value, fg=button_color)
            
            
    def reveal_empty_cells(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols and not self.is_cell_revealed(row, col):
            # Check if the cell is within the grid bounds and is not already revealed
            button = self.buttons[row][col]

            # Check if the cell is not revealed, then reveal it
            if button['text'] != " "  and self.board[row][col] == 0:
                
                button.config(text=" ", bg="#FFFFFF", bd=1)  # White background for cells with 0 value

                for offset in [(-1, 0),(0,-1), (0,1), (1,0)]:
                    nextCell = (row + offset[0], col + offset[1])
                    inBounds = 0 <= nextCell[0] < self.rows and 0 <= nextCell[1] < self.cols
                    if inBounds and not self.is_cell_revealed(nextCell[0], nextCell[1]):
                        
                        self.reveal_empty_cells(nextCell[0], nextCell[1])
                    # for i in range(max(0, row - 1), min(self.rows, row + 2)):
                    #     for j in range(max(0, col - 1), min(self.cols, col + 2)):
                    #         if not self.is_cell_revealed(i, j) and self.buttons[i][j]['state'] != tk.DISABLED:
                    #             if (i, j) != (row, col):  
                    #                 print(i, j)
                    #                 self.reveal_empty_cells(i, j)
                    #         elif self.board[i][j] != "M":
                    #             adjacent_mines = self.count_adjacent_mines(i, j)
                    #             self.buttons[i][j].config(text=str(adjacent_mines), bg="#D3D3D3", bd=1)
            elif self.board[row][col] != "M":
                self.update_cell(row, col, self.board[row][col])


    def reveal_all_mines(self):
        self.emoji_path = "media/mine.png"
        self.load_emoji()

        # Reveal all mines on the game board
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] == "M":
                    self.update_cell(i, j, "M")

    def is_cell_revealed(self, row, col):
        return self.buttons[row][col]['text'] == " " or self.buttons[row][col]['bg'] == "red"

    # def disable_all_buttons(self):
    #     for row in range(self.rows):
    #         for col in range(self.cols):
    #             self.buttons[row][col].config(state=tk.DISABLED)

    def disable_all_buttons(self):
        for row in range(self.rows):
            for col in range(self.cols):
                self.buttons[row][col].config(state=tk.DISABLED)

    # Write me function to check if the game is won, all mines are flagged
    def game_won(self):
        if self.flagged_cells == self.total_mines:
            self.emoji_path = "media/happy_emoji.png"
            self.load_emoji()
            self.emoji_label.config(image=self.emoji_image)
            self.disable_all_buttons()
            self.reset_time()
    
    def game_over(self):
        self.is_game_over = True
        # Change the emoji to sad
        self.emoji_path = "media/sad_emoji.png"
        self.load_emoji()

        self.disable_all_buttons()
        # Update the emoji label to display the sad emoji
        self.emoji_label.config(image=self.emoji_image)
        
        # self.disable_all_buttons()
        
        # Reset the game after clicking on the sad emoji
        self.emoji_label.bind("<Button-1>", lambda event: self.reset_game())

        self.reset_time()

    def reset_game(self):
        self.is_game_over = False
        # Change the emoji back to happy
        self.emoji_path = "media/smiley.png"
        self.load_emoji()

        # Destroy the game over frame and recreate the game board
        for widget in self.master.winfo_children():
            widget.destroy()

        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.buttons = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.flagged_cells = 0
        self.total_mines  = 10
        self.mines  = 10
        #self.initialize_board()
        self.create_widgets()
        self.update_mines_left(0)




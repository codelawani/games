import tkinter as tk

# Create a new root window
root = tk.Tk()

# Create a new text widget with a custom background and font
text = tk.Text(root, bg='blue', fg='white', font=('Arial', 16))

# Add some text to the widget
text.insert('end', 'Hello, world!\n')

# Display the widget in the window
text.pack()

# Start the main event loop
root.mainloop()

if self.check_win(self.current_player):
    # Create a new custom message box
    message_box = CustomMessageBox("Tic Tac Toe", f"Player {self.current_player} wins!",
                                   bg_color="green", fg_color="white")
    # Make the message box modal
    message_box.grab_set()
    message_box.focus_set()

    # Wait for the message box to close
    message_box.wait_window()

    # Set the game over flag
    self.game_over = True

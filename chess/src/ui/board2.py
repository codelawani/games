import customtkinter

class Board(customtkinter.CTkFrame):
	def __init__(self, master):
		super().__init__(master)

		self.canvas = customtkinter.CTkCanvas(self, width=800, height=600, bg="white")
		self.canvas.pack()

		self.canvas.create_line(0, 0, 800, 600, fill="black", width=5)
		self.canvas.create_line(800, 0, 0, 600, fill="black", width=5)

class App(customtkinter.CTk):
	def __init__(self):
		super().__init__()
		self.title("Board 2")
		self.geometry("800x600")
		self.resizable(False, False)
		# self.iconbitmap("src/assets/icon.ico")

		self.board = Board(self)
		self.board.pack()

if __name__ == "__main__":
	app = App()
	app.mainloop()
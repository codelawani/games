try:
	import textual
except ImportError:
	print("'textual' not found, install using 'pip install textual'")

try:
	import rich
except ImportError:
	print("'rich' not found, install using 'pip install rich'")



from src.ui.app import ChessApp


def main():
	app = ChessApp()
	app.run()

if __name__ == "__main__":
	main()
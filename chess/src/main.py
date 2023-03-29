try:
	import textual
except ImportError:
    print("'textual' not found, install using 'pip install textual'")
    exit(1)

try:
	import rich
except ImportError:
	print("'rich' not found, install using 'pip install rich'")
	exit(1)



from src.ui.app import ChessApp


def main():
	app = ChessApp()
	app.run()

if __name__ == "__main__":
	main()

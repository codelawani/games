import pygame
import random

# Initialize Pygame
pygame.init()

# Set up the display
width = 400
height = 400
screen = pygame.display.set_mode((width, height))

# Define colors
black = (0, 0, 0)
white = (255, 255, 255)
gray = (192, 192, 192)

# Set up the grid
grid_size = 4
grid = [[0 for x in range(grid_size)] for y in range(grid_size)]

# Add a starting tile
start_tiles = 2
for i in range(start_tiles):
    x = random.randint(0, grid_size-1)
    y = random.randint(0, grid_size-1)
    grid[x][y] = 2

# Function to draw the grid on the screen
def draw_grid():
    for x in range(grid_size):
        for y in range(grid_size):
            if grid[x][y] == 0:
                color = gray
            else:
                color = white
            pygame.draw.rect(screen, color, (x*100, y*100, 100, 100), 0)
            if grid[x][y] != 0:
                font = pygame.font.Font(None, 36)
                text = font.render(str(grid[x][y]), 1, black)
                screen.blit(text, (x*100+50-text.get_width()/2, y*100+50-text.get_height()/2))

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill(gray)

    # Draw the grid
    draw_grid()

    # Update the display
    pygame.display.update()

# Quit Pygame
pygame.quit()

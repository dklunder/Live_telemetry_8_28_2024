# Live racing simulator throttle and brake telemetry display with full history
# By: David Klunder 
# Date: 8/27/24
import pygame
from datetime import datetime, timedelta
import threading
import matplotlib.pyplot as plt

# Establishes variables
BRAKE = 3
THROTTLE = 1
LINE_WIDTH = 4
SAMPLE_RATE = 10
LINE_SPEED = 2
READ_LOCATION = 0

# The following 3 arrays store the live graphing data used to plot the lines 
# The reason they are seperate from the full arrays under it, is because the live plotting draws a new line from start to finish each refresh
# With lots of data this is not ideal and so the data is erased from these arrays after a specified time 
brake_data = []
throttle_data = []
time_data = []

# These 3 arrays store all of the throttle and brake data from the whole run and plot when the pygame window is closed using matplotlib
brake_data_FULL = []
time_data_FULL = []
throttle_data_FULL = []

# Initializes pygame and the connected joystick
pygame.init()
pygame.joystick.init()

# Detects and reports the joystick if there is one connected
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Initialized joystick: {joystick.get_name()}")
else:
    print("No joystick found. Exiting...")
    pygame.quit()
    exit()

# This funciton populates the arrays by starting the time and waiting the sample rate before appending the current reading to each of the respective arrays
def PEDAL_POSITION():
    global BRAKE_VALUE, THROTTLE_VALUE
    run = True
    start_time = datetime.now() # Starts the time
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # If the X in the pygame window is clicked the window will close and the function will stop
                run = False

        # Sample the pedal values every 
        pygame.time.wait(SAMPLE_RATE)

        # Gets the current time
        current_time = datetime.now()

        # Reads pedal values
        brake_value = -joystick.get_axis(BRAKE)  # Invert brake axis
        throttle_value = -joystick.get_axis(THROTTLE)  # Invert throttle axis

        # Append to data arrays
        brake_data.append(brake_value)
        throttle_data.append(throttle_value)
        time_data.append(current_time)
        
        # Appends to full data arrays
        brake_data_FULL.append((brake_value+1)*50) # Converts to percentage
        time_data_FULL.append(current_time)
        throttle_data_FULL.append((throttle_value+1)*50) # Converts to percentage

        # Remove data points older than 10 seconds
        while time_data and time_data[0] < current_time - timedelta(seconds=1000):
            time_data.pop(0)
            brake_data.pop(0)
            throttle_data.pop(0)

# Run the PEDAL_POSITION function in a separate thread
pygame_thread = threading.Thread(target=PEDAL_POSITION)
pygame_thread.start()

# Pygame screen setup
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Throttle and Brake Positions')

# Establishes colors
GREY = (155, 155, 155)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill(GREY)

    # Calculate the number of data points to draw based on the screen width
    num_points = min(len(time_data), width // 2)

    # Plots the live throttle data
    for i in range(num_points - 1):
        pygame.draw.line(screen, GREEN, (i*LINE_SPEED+ READ_LOCATION, height - throttle_data[-num_points + i] * height),
                         ((i + 1)*LINE_SPEED+ READ_LOCATION, height - throttle_data[-num_points + i + 1] * height), LINE_WIDTH)

    # Plots the live brake data
    for i in range(num_points - 1):
        pygame.draw.line(screen, RED, (i*LINE_SPEED+READ_LOCATION, height - brake_data[-num_points + i] * height),
                         ((i + 1)*LINE_SPEED+READ_LOCATION, height - brake_data[-num_points + i + 1] * height), LINE_WIDTH)

    # Refresh the screen
    pygame.display.flip()

# Quit Pygame properly after closing the window
pygame.quit()

# Uses matplotlib with the full arrays to create a full graph from the session
plt.plot(time_data_FULL,brake_data_FULL, color = 'r', label = 'Brake')
plt.plot(time_data_FULL,throttle_data_FULL,color = 'g', label = 'Throttle')
plt.xlabel('Time (pst)')
plt.ylabel('Pressure (%)')
plt.title('THROTTLE/BRAKE PRESSURE FULL TELEMETRY')
plt.legend()
plt.show()



import serial
import time
import curses

# Open serial port
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
ser.flush()

def send_command(command):
    if command in ['U', 'D', 'L', 'R', 'S']:
        ser.write(command.encode())
    else:
        print("Invalid command. Please use 'U', 'D', 'L', 'R', or 'S'.")

def main(stdscr):
    # stdscr.nodelay(1)
    stdscr.timeout(50)  # Set a timeout for getch
    current_command = 'S'
    
    while True:
        key = stdscr.getch()
        
        if key == curses.KEY_UP:
            current_command = 'U'
        elif key == curses.KEY_DOWN:
            current_command = 'D'
        elif key == curses.KEY_LEFT:
            current_command = 'L'
        elif key == curses.KEY_RIGHT:
            current_command = 'R'
        elif key == ord('q'):
            break
        else:
            current_command = 'S'
        
        send_command(current_command)
        time.sleep(0.05)  # Adjust delay if necessary

    ser.close()

curses.wrapper(main)

import os
import msvcrt
import multiprocessing
import time
import sys
import engine  # <-- CRITICAL CHANGE: Importing engine.py

# We need to set the path for 'auto-py-to-exe' to find the 'components'
# when running as a compiled .exe
if getattr(sys, 'frozen', False):
    # If running as a .exe, the path is relative to the .exe
    bundle_dir = sys._MEIPASS
    # <-- CRITICAL CHANGE: Pointing to the app object in engine.py
    engine.app.template_folder = os.path.join(bundle_dir, 'components')
    engine.app.static_folder = os.path.join(bundle_dir, 'components')

# This will hold our server process
server_process = None
status = "STOPPED"
error_msg = ""

def draw_menu():
    """Draws the TUI menu using simple print statements."""
    os.system('cls')  # Clear the console
    
    print("=========================================================")
    print("          ZORAH WEB SPIDER - CONTROL PANEL")
    print("=========================================================")
    print("\n")
    
    # Status
    if status == "RUNNING":
        os.system('color 0A') 
        print(f"  SERVER STATUS: RUNNING (http://127.0.0.1:8080)")
    else:
        os.system('color 0C')
        print(f"  SERVER STATUS: STOPPED")
        
    # Reset color
    os.system('color 07') 
    
    print("\n")
    print("  CONTROLS:")
    print("  [ S ] - Start Server")
    print("  [ T ] - Stop Server")
    print("  [ Q ] - Quit")
    print("\n")
    print("=========================================================")
    
    if error_msg:
        print(f"\n  INFO: {error_msg}")
    else:
        print(f"\n  Press a key...")

def main_loop():
    """Main TUI application loop."""
    global server_process, status, error_msg
    
    draw_menu() # Initial draw

    while True:
        # Check if server process has stopped on its own
        if server_process and not server_process.is_alive():
            status = "STOPPED"
            error_msg = "Server process terminated unexpectedly."
            server_process = None
            draw_menu()

        # Check for a key press
        if msvcrt.kbhit():
            key = msvcrt.getch()
            error_msg = "" # Clear error on new keypress

            # --- [ S ] Start ---
            if key == b's' or key == b'S':
                if not server_process or not server_process.is_alive():
                    try:
                        # <-- CRITICAL CHANGE: Calling engine.start_server
                        server_process = multiprocessing.Process(target=engine.start_server, daemon=True)
                        server_process.start()
                        status = "RUNNING"
                        error_msg = "Server started. Browser should open."
                    except Exception as e:
                        error_msg = f"Failed to start: {e}"
                else:
                    error_msg = "Server is already running."
                draw_menu()

            # --- [ T ] Stop ---
            elif key == b't' or key == b'T':
                if server_process and server_process.is_alive():
                    server_process.terminate()
                    server_process.join()
                    server_process = None
                    status = "STOPPED"
                    error_msg = "Server stopped successfully."
                else:
                    error_msg = "Server is not running."
                draw_menu()

            # --- [ Q ] Quit ---
            elif key == b'q' or key == b'Q':
                if server_process and server_process.is_alive():
                    print("Stopping server before quitting...")
                    server_process.terminate()
                    server_process.join()
                print("Exiting. Goodbye!")
                break # Exit the loop
            else:
                pass 
                
        time.sleep(0.1) # Prevent high CPU usage

# This wrapper is required to safely initialize
def run_tui():
    multiprocessing.freeze_support() 
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\nQuitting...")
        if server_process and server_process.is_alive():
            server_process.terminate()
            server_process.join()

if __name__ == "__main__":
    run_tui()
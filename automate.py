import cv2
import numpy as np
import pyautogui
import time
import keyboard
import threading
import sys
import random
import math
from screeninfo import get_monitors  # Add this import

# === Add this global variable for the keep going feature ===
KEEP_GOING_KEY = 'num lock'  # Num Lock key for "keep it going"
skip_wait_now = False        # Flag to signal skipping current wait

# Configuration
POSTS_TO_PROCESS = 50  # Change this number as needed
EXIT_KEY = 'esc'       # Press ESC to stop the script
PAUSE_KEY = 'f2'       # Press F2 to pause for manual intervention  
is_paused = False      # Flag to track if script is paused
MIN_CONFIDENCE = 0.7 # Minimum confidence for image match (0.0-1.0)
MIN_FOLLOW_CONFIDENCE = 0.65  # Slightly lower confidence for Follow button
MIN_DISTANCE = 35      # Minimum pixel distance between matches

# List of message variations
MESSAGE_VARIATIONS = [
    "yo your music is actually fire, been playing it all day",
    "damn your music slaps, you got something real here fr",
    "ngl your music goes hard, keep grinding!!",
    "just found your music and it's honestly amazing, mad respect"
]

def get_random_message():
    """Get a random message from the variations list"""
    return random.choice(MESSAGE_VARIATIONS)

# Add a new global variable to track manual closing
SKIP_KEY = 'f3'        # Press F2 to skip current tab
tab_manually_closed = False  # Flag 2to track if tab was manually closed

# Add monitor selection variables
selected_monitor = None  # Will store the selected monitor information

def select_monitor():
    """Display available monitors and let user choose which one to use"""
    monitors = get_monitors()
    
    if not monitors:
        print("No monitors detected. Using full screen.")
        return None
    
    if len(monitors) == 1:
        print(f"Only one monitor detected: {monitors[0].width}x{monitors[0].height}")
        return monitors[0]
    
    print("\n===== Available Monitors =====")
    for i, m in enumerate(monitors, 1):
        print(f"{i}. Monitor {i}: {m.width}x{m.height} at position ({m.x}, {m.y})")
    
    while True:
        try:
            choice = int(input(f"\nSelect monitor (1-{len(monitors)}): "))
            if 1 <= choice <= len(monitors):
                print(f"Selected Monitor {choice}: {monitors[choice-1].width}x{monitors[choice-1].height}")
                return monitors[choice-1]
            else:
                print(f"Invalid choice. Please enter a number between 1 and {len(monitors)}.")
        except ValueError:
            print("Please enter a valid number.")

def on_keep_going_key_press(e):
    """Handler for the keep going (Num Lock) key"""
    global skip_wait_now
    if e.name == KEEP_GOING_KEY:
        print("\n=== KEEP GOING: Skipping current wait ===")
        skip_wait_now = True

def random_wait(min_time=0.0, max_time=0.01):
    """Wait a random amount of time but check for pause during the wait and allow skipping with Num Lock"""
    global is_paused, skip_wait_now

    wait_time = random.uniform(min_time, max_time)
    end_time = time.time() + wait_time

    # Wait in small increments to be responsive to pause and keep going
    while time.time() < end_time:
        # Check if paused
        if is_paused:
            print("Script paused during wait. Waiting for resume...")
            while is_paused:
                time.sleep(0.1)  # Small sleep while waiting for pause to end
            # Reset end time to give full wait after resuming
            end_time = time.time() + wait_time

        # === Check for keep going (Num Lock) ===
        if skip_wait_now:
            skip_wait_now = False  # Reset flag for next wait
            print("Keep going triggered, skipping remaining wait.")
            break

        # Sleep in small increments
        time.sleep(0.1)

def distance(p1, p2):
    """Calculate distance between two points"""
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def find_element_on_screen(template_path, confidence=MIN_CONFIDENCE, region=None):
    """
    Find an element on screen matching the template image
    Optional region parameter allows limiting the search area (x, y, width, height)
    """
    global selected_monitor
    
    # If a specific monitor is selected and no region is specified, use the monitor bounds
    if selected_monitor and not region:
        monitor_region = (selected_monitor.x, selected_monitor.y, 
                          selected_monitor.width, selected_monitor.height)
        screenshot = pyautogui.screenshot(region=monitor_region)
    # Otherwise use specified region or full screen
    else:
        screenshot = pyautogui.screenshot(region=region)
    
    screenshot_np = np.array(screenshot)
    screenshot_rgb = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

    # Load the template
    template = cv2.imread(template_path)
    if template is None:
        print(f"Error: Could not load template image at {template_path}")
        return None

    # Get dimensions of template
    h, w = template.shape[:2]

    # Perform template matching
    result = cv2.matchTemplate(screenshot_rgb, template, cv2.TM_CCOEFF_NORMED)

    # Find position with maximum confidence
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # Check if match exceeds confidence threshold
    if max_val >= confidence:
        # Calculate actual coordinates based on monitor/region offset
        if region:
            return (region[0] + max_loc[0] + w//2, region[1] + max_loc[1] + h//2)
        elif selected_monitor:
            return (selected_monitor.x + max_loc[0] + w//2, selected_monitor.y + max_loc[1] + h//2)
        else:
            return (max_loc[0] + w//2, max_loc[1] + h//2)
    else:
        return None

def find_all_at_symbols(template_path="image.png"):
    """Find all @ symbols on screen matching the template image"""
    global selected_monitor
    
    # Take a screenshot of the selected monitor if one is chosen
    if selected_monitor:
        screenshot = pyautogui.screenshot(region=(selected_monitor.x, selected_monitor.y, 
                                                 selected_monitor.width, selected_monitor.height))
    else:
        screenshot = pyautogui.screenshot()
        
    screenshot_np = np.array(screenshot)
    screenshot_rgb = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

    # Load the @ symbol template
    template = cv2.imread(template_path)
    if template is None:
        print(f"Error: Could not load template image at {template_path}")
        return []

    # Get dimensions of template
    h, w = template.shape[:2]

    # Perform template matching
    result = cv2.matchTemplate(screenshot_rgb, template, cv2.TM_CCOEFF_NORMED)

    # Find positions where match exceeds threshold
    locations = np.where(result >= MIN_CONFIDENCE)
    all_matches = []

    # Store coordinates of all matches
    for pt in zip(*locations[::-1]):
        # Add center point of the match with monitor offset if needed
        if selected_monitor:
            all_matches.append((selected_monitor.x + pt[0] + w//2, 
                               selected_monitor.y + pt[1] + h//2))
        else:
            all_matches.append((pt[0] + w//2, pt[1] + h//2))

    # Filter out matches that are too close to each other
    filtered_matches = []
    for match in all_matches:
        # Check if this match is far enough from all filtered matches
        if all(distance(match, existing) > MIN_DISTANCE for existing in filtered_matches):
            filtered_matches.append(match)

    print(f"Found {len(filtered_matches)} unique @ symbols (filtered from {len(all_matches)} total matches)")
    return filtered_matches

def check_and_close_dupes():
    """Check for closedupe buttons and click if found"""
    dupe_templates = ["closedupe1.PNG", "closedupe2.PNG", "closedupe3.PNG"]
    
    for template in dupe_templates:
        dupe_pos = find_element_on_screen(template, confidence=0.7)
        if dupe_pos:
            print(f"Found {template}, clicking to close")
            pyautogui.moveTo(dupe_pos[0], dupe_pos[1], duration=0.1)
            pyautogui.click()
            random_wait(0.3, 0.5)
            return True
    
    return False

def stop_listener():
    """Monitor for exit key press"""
    print(f"Script running. Press '{EXIT_KEY}' to stop.")
    keyboard.wait(EXIT_KEY)
    print("Exit key pressed. Stopping script...")
    sys.exit()

# Update the key handler
def on_skip_key_press(e):
    global tab_manually_closed
    if e.name == SKIP_KEY:
        print("\n=== SKIP TAB: Closing current tab and moving to next ===")
        # Close current tab
        pyautogui.hotkey('ctrl', 'w')
        print("Tab closed, jumping directly to next tab processing...")
        # Set flag that tab was manually closed
        tab_manually_closed = True
        # Add a small delay to ensure tab closes properly
        time.sleep(0.1)

# Change the pause key handler to instantly skip the current tab
def on_pause_key_press(e):
    global is_paused
    if e.name == PAUSE_KEY:
        print("\n=== SKIP TAB: Closing current tab and moving to next ===")
        # Close current tab
        pyautogui.hotkey('ctrl', 'w')
        print("Tab closed, continuing with next tab...")
        # Add a small delay to ensure tab closes properly
        time.sleep(0.02)

# Add this function to select the processing mode
def select_processing_mode():
    """Allow user to select which processing mode to use"""
    print("\n===== Select Processing Mode =====")
    print("1. Standard Mode: Message existing followers, follow + message others")
    print("2. Follow All Mode: Follow everyone first, then message them")
    
    while True:
        try:
            choice = int(input("\nSelect mode (1-2): "))
            if choice in [1, 2]:
                return choice
            else:
                print("Invalid choice. Please enter 1 or 2.")
        except ValueError:
            print("Please enter a valid number.")

# Modify the process_open_tabs function to accept a mode parameter
def process_open_tabs(mode=1):
    """
    Process open tabs - follow, message, close
    
    Mode 1: Standard - Message existing followers, follow + message others
    Mode 2: Follow All - Follow everyone first, then message them
    """
    print("\n--- Starting to process open tabs ---")
    if mode == 1:
        print("Using Standard Mode: Message existing followers, follow + message others")
    else:
        print("Using Follow All Mode: Follow everyone first, then message them")
    
    # Add a counter to avoid infinite loops
    max_tabs = 100  # Safety limit
    tabs_processed = 0
    
    try:
        while tabs_processed < max_tabs:
            global tab_manually_closed
            tabs_processed += 1
            print(f"Processing tab {tabs_processed}")
            
            # Check if tab was manually closed with F3
            if tab_manually_closed:
                # Reset the flag and move directly to processing the next tab
                tab_manually_closed = False
                print("Detected manual tab skip, moving to next tab...")
                continue
                
            # Wait for page to load - reduced wait time
            random_wait(0.5, 0.8)
            
            # First check if profile doesn't exist
            profile_not_found = find_element_on_screen("profile_doesnt_exist.PNG")
            if profile_not_found:
                print("Profile doesn't exist, closing tab")
                pyautogui.hotkey('ctrl', 'w')
                random_wait(0.2, 0.4)
                continue
            
            # Check for F3 press
            if tab_manually_closed:
                tab_manually_closed = False
                print("F3 pressed during processing, skipping to next tab...")
                continue
                
            # Look for Follow button first regardless of mode
            follow_pos = find_element_on_screen("Follow.PNG", confidence=MIN_FOLLOW_CONFIDENCE)
            
            # Look for Message button
            message_pos = find_element_on_screen("Message.PNG")
            
            # Check for F3 press
            if tab_manually_closed:
                tab_manually_closed = False
                print("F3 pressed during processing, skipping to next tab...")
                continue
            
            # Process based on mode
            if mode == 1:
                # Mode 1: Standard processing (current behavior)
                if message_pos:
                    # Can already message, proceed with messaging
                    print(f"Found Message button, clicking it")
                    pyautogui.click(message_pos)
                    print("Waiting for message dialog to open...")
                    random_wait(5.0, 7.5)
                elif follow_pos:
                    # Need to follow first
                    print(f"Found Follow button, clicking it")
                    pyautogui.click(follow_pos)
                    print("Waiting after clicking Follow...")
                    random_wait(5.0, 7.5)
                    
                    # Check for F3 press
                    if tab_manually_closed:
                        tab_manually_closed = False
                        print("F3 pressed during processing, skipping to next tab...")
                        continue
                    
                    # Look for Message button again after following
                    message_pos = find_element_on_screen("Message.PNG")
                    if message_pos:
                        print(f"Found Message button after following, clicking it")
                        pyautogui.click(message_pos)
                        print("Waiting for message dialog to open...")
                        random_wait(5.0, 7.5)
                    else:
                        print("Message button still not found after following, closing tab")
                        pyautogui.hotkey('ctrl', 'w')
                        random_wait(0.2, 0.4)
                        continue
                else:
                    print("Neither Follow nor Message button found, closing tab")
                    pyautogui.hotkey('ctrl', 'w')
                    random_wait(0.2, 0.4)
                    continue
            
            else:
                # Mode 2: Follow everyone first, then message
                if follow_pos:
                    # Follow first if possible
                    print(f"Found Follow button, clicking it")
                    pyautogui.click(follow_pos)
                    print("Waiting after clicking Follow...")
                    random_wait(5.0, 7.5)
                    
                    # Check for F3 press
                    if tab_manually_closed:
                        tab_manually_closed = False
                        print("F3 pressed during processing, skipping to next tab...")
                        continue
                    
                    # Look for Message button again after following
                    message_pos = find_element_on_screen("Message.PNG")
                
                # If no Follow button or we just followed, try to message
                if message_pos:
                    print(f"Found Message button, clicking it")
                    pyautogui.click(message_pos)
                    print("Waiting for message dialog to open...")
                    random_wait(5.0, 7.5)
                else:
                    print("Message button not found after checking/following, closing tab")
                    pyautogui.hotkey('ctrl', 'w')
                    random_wait(0.2, 0.4)
                    continue
            
            # Check for F3 press
            if tab_manually_closed:
                tab_manually_closed = False
                print("F3 pressed during processing, skipping to next tab...")
                continue
            
            # At this point we should have clicked the message button
            # Look for message placeholder to click in
            message_placeholder = find_element_on_screen("message_placeholder.PNG")
            if message_placeholder:
                print("Found message input, clicking it")
                pyautogui.click(message_placeholder)
                random_wait(0.2, 0.4)
                
                # Check for F3 press
                if tab_manually_closed:
                    tab_manually_closed = False
                    print("F3 pressed during processing, skipping to next tab...")
                    continue
                
                # Type the message
                message_text = get_random_message()
                print(f"Typing message: '{message_text}'")
                pyautogui.typewrite(message_text)
                random_wait(1.3, 1.5)
                
                # Check for F3 press
                if tab_manually_closed:
                    tab_manually_closed = False
                    print("F3 pressed during processing, skipping to next tab...")
                    continue
                
                # Press Enter to send
                pyautogui.press('enter')
                print("Message sent successfully")
                random_wait(1.5, 2.8)
            else:
                print("Could not find message input field")
            
            # Final check for F3 press before closing tab
            if tab_manually_closed:
                tab_manually_closed = False
                print("F3 pressed during processing, skipping to next tab...")
                continue
            
            # Close the tab and move to next one
            print("Closing current tab")
            pyautogui.hotkey('ctrl', 'w')
            random_wait(0.3, 0.5)
    
    except Exception as e:
        print(f"Error in tab processing: {e}")

def open_profiles_from_posts():
    """Phase 1: Find and click @ symbols in posts"""
    print("\n--- Phase 1: Finding @ symbols in posts ---")
    
    # Get screen dimensions to know where to move cursor
    screen_width, screen_height = pyautogui.size()
    
    # Click on the screen first to ensure focus
    pyautogui.click()
    random_wait(0.2, 0.3)  # Reduced from 0.5-0.8
    
    for i in range(POSTS_TO_PROCESS):
        print(f"\nProcessing post {i+1}/{POSTS_TO_PROCESS}")
        
        # Start timer for this post
        post_start_time = time.time()
        
        # Find all @ symbols on the screen
        at_symbols = find_all_at_symbols()
        
        # Fast clicking on each @ symbol found
        for idx, (x, y) in enumerate(at_symbols):
            print(f"Middle-clicking @ symbol {idx+1} at position ({x}, {y})")
            # Faster mouse movement (reduced duration)
            pyautogui.moveTo(x, y, duration=0.1)  # Reduced from 0.3
            random_wait(0.05, 0.1)  # Reduced from 0.3-0.5
            pyautogui.middleClick()
            random_wait(0.05, 0.1)  # Reduced from 0.5-0.8
            
            # Quick cursor movement to top
            pyautogui.moveTo(screen_width // 2, 10, duration=0.05)  # Reduced from 0.2
            
            # Ensure we don't spend more than 3 seconds on this post
            if time.time() - post_start_time > 3.0:
                print("Reached maximum time for this post, moving on...")
                break
        
        # Check for and close any dupes before moving to next post
        print("Checking for close dupe buttons...")
        check_and_close_dupes()
        
        # Move to next post if needed - faster transition
        if i < POSTS_TO_PROCESS - 1:
            print("Moving to next post")
            pyautogui.press('right')  
            random_wait(0.3, 0.5)  # Reduced from 0.8-1.2

def start_processing_tabs():
    """Phase 2: Process open tabs"""
    print("\n--- Phase 2: Processing open tabs ---")
    # Switch to the first opened tab

    #random_wait(0.5, 0.8)  # Reduced from 1.0-1.5
    
    # Select processing mode
    mode = select_processing_mode()
    random_wait(1.0, 1.8) 
    pyautogui.hotkey('ctrl', '1')  # Go to first tab
    # Process all open tabs
    random_wait(0.2, 0.3) 
    process_open_tabs(mode)

def verify_required_images():
    """Verify that all required template images exist"""
    required_images = [
        "image.png", 
        "Message.PNG", 
        "Follow.PNG", 
        "message_placeholder.PNG", 
        "profile_doesnt_exist.PNG"
    ]
    missing_images = []

    for img in required_images:
        try:
            if cv2.imread(img) is None:
                missing_images.append(img)
        except:
            missing_images.append(img)

    if missing_images:
        print(f"Error: The following required images are missing: {', '.join(missing_images)}")
        print("Please make sure all template images are in the same directory as this script")
        return False
        
    return True

def show_menu():
    """Display menu options and get user choice"""
    print("\n===== Instagram Automation Menu =====")
    print("1. Open profiles from posts (find @ symbols)")
    print("2. Process open tabs (follow, message, close)")
    print("3. Exit")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (1-3): "))
            if 1 <= choice <= 3:
                return choice
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        except ValueError:
            print("Please enter a valid number.")

def main():
    print("Starting Instagram automation script")

    # Add monitor selection
    global selected_monitor
    selected_monitor = select_monitor()

    # Verify template images exist
    if not verify_required_images():
        return

    # Start the keyboard listener in a separate thread
    stop_thread = threading.Thread(target=stop_listener)
    stop_thread.daemon = True
    stop_thread.start()

    # Add a listener for the pause key
    keyboard.on_press(on_pause_key_press)
    keyboard.on_press(on_skip_key_press)
    # === Add a listener for the keep going (Num Lock) key ===
    keyboard.on_press(on_keep_going_key_press)

    try:
        while True:
            choice = show_menu()

            if choice == 1:
                # Option 1: Open profiles from posts
                print("You selected: Open profiles from posts")
                print("Switch to Instagram within 3 seconds...")
                time.sleep(3)
                open_profiles_from_posts()
                print("Finished opening profiles")
                
            elif choice == 2:
                # Option 2: Process open tabs
                print("You selected: Process open tabs")
                print("Switch to browser with open tabs within 3 seconds...")
                start_processing_tabs()
                time.sleep(3)

                print("Finished processing tabs")
                
            else:
                # Option 3: Exit
                print("Exiting program...")
                break

    except Exception as e:
        print(f"Error occurred: {e}")

    print("Script completed")

if __name__ == "__main__":
    main()

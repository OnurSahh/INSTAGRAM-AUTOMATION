# Instagram Automation Script

## Overview
This script automates various tasks on Instagram, such as opening profiles from posts, following users, sending messages, and closing tabs. It is designed to streamline repetitive actions and improve efficiency when interacting with Instagram profiles.

## Features
- **Open Profiles from Posts**: Automatically find and click on `@` symbols in posts to open user profiles.
- **Process Open Tabs**: Follow users, send messages, and close tabs based on predefined actions.
- **Customizable Message Variations**: Send personalized messages to users with random selection from a list.
- **Pause and Skip Functionality**: Pause the script or skip tabs manually using hotkeys.
- **Monitor Selection**: Choose which monitor to use for automation tasks.
- **Template Matching**: Detect and interact with UI elements like buttons and input fields using image templates.

## Requirements
- Python 3.8 or higher
- Required Python libraries:
  - `pyautogui`
  - `keyboard`
  - `cv2` (OpenCV)
  - `numpy`
  - `screeninfo`
- Template images:
  - `image.png`
  - `Message.PNG`
  - `Follow.PNG`
  - `message_placeholder.PNG`
  - `profile_doesnt_exist.PNG`

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo-name/insta-automation.git
   cd insta-automation
   ```
2. Set up a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Place the required template images in the same directory as the script.

## Usage
1. Run the script:
   ```bash
   python automate.py
   ```
2. Select the desired monitor for automation tasks.
3. Choose an option from the menu:
   - **Open Profiles from Posts**: Switch to Instagram and let the script find and open profiles.
   - **Process Open Tabs**: Switch to your browser with open tabs and let the script follow, message, and close tabs.
   - **Exit**: Stop the script.

## Hotkeys
- **ESC**: Stop the script.
- **F2**: Pause the script for manual intervention.
- **F3**: Skip the current tab.
- **Num Lock**: Skip the current wait and proceed.

## Customization
- Modify the `MESSAGE_VARIATIONS` list in the script to change the messages sent to users.
- Adjust configuration variables:
  - `POSTS_TO_PROCESS`: Number of posts to process.
  - `MIN_CONFIDENCE`: Confidence threshold for image matching.
  - `MIN_DISTANCE`: Minimum pixel distance between matches.

## Notes
- Ensure the required template images are accurate and match the UI elements on Instagram.
- Use responsibly and adhere to Instagram's terms of service.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Disclaimer
This script is provided for educational purposes only. The author is not responsible for any misuse or violations of Instagram's policies. Use at your own risk.
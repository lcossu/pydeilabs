# PyDEILabs
![pydeilabs.png](pydeilabs.png)

## Overview
**PyDEILabs** is a simple application for authenticating and automatically checking in to a lab on the **deilabs** site. It allows you to save login credentials and lab name, making the login and lab check-in process fast and repeatable.

## Features

- Automatic login and lab check-in on deilabs.
- Save credentials and lab name for repeated use.

## How to Use

### Pre-Built Application
1. Download the correct executable from the latest release for your OS.
2. Launch the application: a simple form will be displayed.
3. Enter your username, password, and lab name. **Note:** The lab name must match exactly with the name on the deilabs website.
4. Click "Save" to save the configuration. This will automatically attempt to log in and check in to the lab.
5. On subsequent runs, the app will use the saved credentials to log in and check in to the lab automatically.
6. Add the application to your startup applications, so it runs on system boot (if needed, follow instructions below).
7. Profit!

### Running the Python Script Manually
If you prefer to run the Python script manually:
- Choose between the default version (with GUI) and the noconfig version.
  - **Default (with GUI)**: launches the application as described in the pre-built version.
  - **Noconfig**: enter the required information directly at the top of the script.

## Configuration File Location
The configuration file is saved to a system-specific directory to ensure data persistence:

- **Windows**: `AppData\Roaming\pydeilabs`
- **MacOS**: `~/Library/Application Support/pydeilabs`
- Linux: `~/.config/pydeilabs`

Note that the password is currently saved without encryption.


## Adding the Application to Startup

### Windows

1.	Press Win + R, type shell:startup, and press Enter.
2.	Copy the PyDEILabs executable or a shortcut to it into the opened folder.
3.	The application will now launch automatically when you start your computer.

### macOS

1.	Open System Preferences → Users & Groups → Login Items.
2.	Click the + button, navigate to the location of the PyDEILabs executable, and add it to the list.
3.	Ensure it’s checked to enable automatic startup.

### Linux (using GNOME)

1.	Open Startup Applications from your system settings or search menu.
2.	Click Add and fill in
  - Name: PyDEILabs
  -	Command: Path to the executable (e.g., /home/user/pydeilabs)
  -	Comment: (Optional) Auto-check-in for deilabs.
3.	Save and ensure the app is listed.

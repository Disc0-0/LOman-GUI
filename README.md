# LOmanGUI - Last Oasis Server Manager GUI

A graphical user interface for managing Last Oasis dedicated servers, with automated mod management and server monitoring.

## Description

LOmanGUI provides a user-friendly interface for Last Oasis server administrators to manage their dedicated server instances. It handles server startup, monitoring, mod management, and automatic updates through a simple GUI interface.

## Features

- **Server Management**
  - Start, stop, and restart server instances
  - Automate server restarts after mod updates
  - Monitor server status and crashes
  - Track tile names across server instances
  
- **Mod Management**
  - Add, update, and remove Steam Workshop mods
  - Automatic detection of mod updates
  - One-click mod installation
  - Discord notifications for mod updates
  
- **Automation**
  - Scheduled checks for mod updates
  - Configurable restart warnings
  - Discord webhook integration for status notifications

## Components

The application consists of several integrated components:

- **main_gui.py**: Main entry point for the GUI application
- **LastOasisManager.py**: Core server management functionality
- **mod_checker.py**: Steam Workshop integration for tracking and updating mods
- **TileTracker.py**: Component for tracking tile names and server status
- **DiscordProcessor.py**: Discord webhook integration for notifications
- **LogMonitor.py**: Server log monitoring functionality
- **lo_server_query.py**: Server query tool for monitoring server status
- **admin_writer.py**: Tool for communicating with server admin interfaces

## Prerequisites

- Windows operating system
- Python 3.7 or higher
- SteamCMD installed
- Last Oasis dedicated server installation
- Administrative privileges (for server management)

### Required Python Packages

- PyQt5 (for the GUI)
- requests (for Steam Workshop API interactions)
- beautifulsoup4 (for parsing Steam Workshop content)
- psutil (for process management)

## Installation

1. **Clone or download the repository**
   ```
   git clone <repository-url>
   ```
   or download and extract the ZIP archive

2. **Install required Python packages**
   ```
   pip install PyQt5 requests beautifulsoup4 psutil
   ```

3. **Configure your environment**
   - Make sure SteamCMD is installed and accessible
   - Ensure your Last Oasis dedicated server is installed

4. **Edit the configuration file**
   - Create or modify `config.json` to match your server setup

## Configuration

Create a `config.json` file in the main directory with the following structure:

```json
{
  "folder_path": "C:/path/to/LastOasis/server/Binaries/Win64/",
  "steam_cmd_path": "C:/path/to/steamcmd/",
  "backend": "https://lastovoy.backends.frikk.online",
  "customer_key": "your_customer_key",
  "provider_key": "your_provider_key",
  "connection_ip": "your_server_ip",
  "slots": 50,
  "identifier": "your_server_identifier",
  "start_port": 5000,
  "start_query_port": 6000,
  "tile_num": 1,
  "mod_check_interval": 600,
  "restart_time": 300,
  "server_status_webhook": "https://discord.com/api/webhooks/your_webhook_url",
  "mods": "mod_id_1,mod_id_2,mod_id_3"
}
```

### Configuration Fields Explained:

- `folder_path`: Directory containing the Last Oasis server executable
- `steam_cmd_path`: Directory containing SteamCMD
- `backend`: Last Oasis backend API URL
- `customer_key`: Your Last Oasis customer key
- `provider_key`: Your Last Oasis provider key
- `connection_ip`: Your server's public IP address
- `slots`: Maximum player slots per tile
- `identifier`: Base identifier for your server tiles
- `start_port`: Starting port number for server instances
- `start_query_port`: Starting query port for server instances
- `tile_num`: Number of tile instances to run
- `mod_check_interval`: Time between mod update checks (in seconds)
- `restart_time`: Warning time before server restart (in seconds)
- `server_status_webhook`: Discord webhook URL for status notifications
- `mods`: Comma-separated list of Steam Workshop mod IDs

## Usage

### Starting the Application

Run the main application:

```
python main_gui.py
```

### Server Management

The GUI provides buttons and controls for managing your Last Oasis server:

- **Start Servers**: Launches all configured server instances
- **Stop Servers**: Gracefully stops all running server instances
- **Restart Servers**: Stops and restarts all server instances
- **Update Game**: Updates the Last Oasis dedicated server installation

### Mod Management

The Mod Management panel allows you to:

- **Add Mod**: Enter the Steam Workshop ID of a mod to add it to your server
- **Remove Mod**: Select a mod from the list and remove it
- **Check for Updates**: Manually check for mod updates
- **Update Mods**: Apply available mod updates (restarts servers if necessary)
- **View on Steam**: Opens the Steam Workshop page for the selected mod

## Mod Management Details

LOmanGUI makes it easy to manage Steam Workshop mods for your Last Oasis server:

1. **Adding Mods**:
   - Click "Add Mod" button
   - Enter the Steam Workshop ID (the numeric ID from the mod's URL)
   - The mod will be downloaded and installed on next server restart

2. **Automatic Updates**:
   - LOmanGUI periodically checks for mod updates
   - When updates are detected, a notification is sent to your Discord webhook
   - Servers are restarted automatically after the configured warning time

3. **Mod Information**:
   - Mod IDs and update information are stored in `mods_info.json`
   - This file is automatically maintained by the application

## Troubleshooting

### Common Issues

#### "Error loading mods: str Object has no attribute get"
- This usually indicates an issue with the `mods_info.json` file format
- Solution: Ensure `mods_info.json` exists and contains valid JSON
- If the problem persists, delete `mods_info.json` to regenerate it

#### "Unable to start server instances"
- Check if the paths in `config.json` are correct
- Verify that SteamCMD is installed and functioning
- Ensure you have the correct permissions to run the server executables

#### "Discord notifications not working"
- Verify that your webhook URL is correct in `config.json`
- Check your internet connection
- Ensure the webhook hasn't been deleted or rate-limited on Discord

#### "Mod doesn't appear in game after installation"
- Verify the mod ID is correct
- Check the Last Oasis server logs for mod loading errors
- Some mods may require additional configuration or dependencies

### Log Files

- The main application log is stored in `loman.log`
- Server logs are stored in the Last Oasis server's log directory

## Contributing

Contributions to LOmanGUI are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code follows the existing style and includes appropriate documentation.

## License

This project is distributed under the MIT License. See the LICENSE file for details.

## Acknowledgements

- Last Oasis game and dedicated server by Donkey Crew
- Steam Workshop for mod distribution platform

*LOmanGUI is not affiliated with Donkey Crew or Last Oasis. All trademarks are the property of their respective owners.*

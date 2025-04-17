# LOMan (Last Oasis Manager)

A comprehensive management system for Last Oasis dedicated servers. This tool suite provides automated server management, monitoring, mod updates, and Discord integration.

[![Python 3.x](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Based on [LastOasisServerManager](https://github.com/BrettMeirhofer/LastOasisServerManager) by Brett Meirhofer.

## Table of Contents
- [System Requirements and Prerequisites](#system-requirements-and-prerequisites)
- [Core Components](#core-components)
- [Installation and Setup](#installation-and-setup)
- [Configuration](#configuration)
- [Usage Instructions](#usage-instructions)
  - [Server Management](#server-management)
  - [Discord Integration](#discord-integration)
  - [Server Queries](#server-queries)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)


## System Requirements and Prerequisites

- Windows operating system
- Python 3.x
- Last Oasis Dedicated Server installed
- SteamCMD installed
- Discord webhook URLs (for notifications)
- Required Python packages:
  - requests
  - beautifulsoup4
  - psutil
  - watchdog (for LogMonitor)
  - python-a2s (for server queries)


## Core Components

LOMan consists of several integrated components that work together:

1. **LastOasisManager.py** - Core server management with automated startup, monitoring, crash recovery, and mod update coordination
   - Multi-tile management for running multiple servers
   - Automated crash detection and recovery
   - Discord status notifications
   - Dynamic tile name tracking

2. **mod_checker.py** - Steam Workshop integration for tracking and updating mods
   - Monitors Steam Workshop for mod updates
   - Smart rate limiting and retry logic
   - Local caching to minimize Steam queries
   - Robust error handling

3. **DiscordProcessor.py** - Discord webhook integration for server status and chat relay
   - Real-time chat relay with color-coded messages
   - Player join/leave event tracking
   - Kill feed monitoring
   - Uses Discord embeds for better formatting

4. **LogMonitor.py** & **TileTracker** - Log file monitoring and tile name tracking
   - Real-time log monitoring with watchdog integration
   - Extracts and processes various log events
   - Reliable tile name detection

5. **lo_server_query.py** - Server query tool supporting Steam and Unreal Engine protocols
   - Multiple output formats (JSON, CSV, text)
   - Port scanning capabilities
   - Multithreaded for efficient parallel queries
   - Retrieves player and server information


## Installation and Setup

1. Clone or download the LOMan repository to your server
2. Install required Python dependencies:
   ```bash
   pip install requests beautifulsoup4 psutil watchdog python-a2s
   ```
3. Create a config.json file in the LOMan directory (see Configuration section)
4. Ensure SteamCMD is installed and properly configured
5. Set up Discord webhooks for notifications


## Configuration

The system uses a `config.json` file to configure various aspects of operation. Here's a sample configuration with explanations:

```json
{
  "folder_path": "C:/lastoasis/Binaries/Win64/",
  "steam_cmd_path": "C:/SteamCMD/",
  "backend": "https://backend-url.lastoasis.com",
  "customer_key": "your-customer-key",
  "provider_key": "your-provider-key",
  "connection_ip": "your-server-ip",
  "slots": 50,
  "identifier": "LO_Server",
  "start_port": 8000,
  "start_query_port": 27015,
  "tile_num": 3,
  "server_status_webhook": "https://discord.com/api/webhooks/your-webhook-url",
  "mods": "123456789,987654321",
  "mod_check_interval": 3600,
  "restart_time": 300
}
```

Configuration keys:

| **Key**                              | **Description**                                      |
|-------------------------------------|------------------------------------------------------|
| `folder_path`                       | Path to Last Oasis server binaries                   |
| `steam_cmd_path`                    | Path to SteamCMD installation                        |
| `backend`, `customer_key`, `provider_key` | Last Oasis server configuration               |
| `connection_ip`                     | Server's public IP address                           |
| `slots`                             | Maximum player slots per tile                        |
| `identifier`                        | Server identifier prefix                             |
| `start_port` & `start_query_port`   | Starting ports for multiple tiles                    |
| `tile_num`                          | Number of tiles to run                               |
| `server_status_webhook`             | Discord webhook URL for server status notifications  |
| `mods`                              | Comma-separated list of Steam Workshop mod IDs       |
| `mod_check_interval`                | Time between mod update checks (in seconds)          |
| `restart_time`                      | Warning time before server restart (in seconds)      |


## Usage Instructions

### Server Management

To start the server management system:

```bash
python LastOasisManager.py
```

This will:
1. Initialize tile name tracking

2. Update the game files using SteamCMD

3. Check for mod updates

4. Download and install mods

5. Start server instances for each tile

6. Begin monitoring for crashes and mod updates

The manager will continuously run, monitoring server health and checking for mod updates based on the configured interval.

### Discord Integration

The Discord integration runs automatically when started:

```bash
python DiscordProcessor.py
```

This will monitor server logs and forward various messages to Discord:

- Chat messages (blue)
- Player join events (green)
- Tile ready notifications (green)
- Kill feed (yellow)

You can configure the log files to monitor by editing the `logs_to_monitor` list in DiscordProcessor.py.

### Server Queries

To query your servers for information:

```bash
python lo_server_query.py --server your-ip:query-port
```

Additional options:

| **Option**                      | **Description**                                 |
|--------------------------------|-----------------------------------------------|
| `--servers file.txt`           | Query multiple servers listed in a file       |
| `--scan-ports ip:start-end`    | Scan IP address for Steam query ports         |
| `--output result.json`         | Specify output file for results               |
| `--format json\|csv\|txt`      | Specify output format                         |
| `--protocol steam\|unreal\|both` | Choose query protocol                       |


## Troubleshooting

### Common Issues

| **Issue**                                   | **Troubleshooting Steps**                      |
|--------------------------------------------|--------------------------------------------|
| **Server crashes immediately after startup** | - Check server log files for error messages<br>- Verify correct paths in config.json<br>- Ensure mod IDs are valid and properly formatted |
| **Mod updates not detecting**               | - Check network connectivity to Steam<br>- Verify mod IDs in config.json<br>- Check mod_checker.py logs for rate limiting issues |
| **Discord notifications not working**       | - Verify webhook URL is valid and correctly formatted<br>- Check network connectivity to Discord<br>- Ensure proper permissions for the webhook |
| **Game updates failing**                    | - Verify SteamCMD is properly installed<br>- Check network connectivity to Steam<br>- Ensure sufficient disk space for updates |

### Log Files

| **Log File**            | **Description**                           |
|------------------------|-------------------------------------------|
| **loman.log**          | Main log file for the server manager      |
| **mod_checker.log**    | Log file for mod update checks            |
| **log_monitor.log**    | Log file for the log monitoring system    |
| **lo_server_query.log**| Log file for server queries               |


## Contributing

Contributions to LOMan are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code follows the existing style and includes appropriate documentation.


## License

This project is available under the MIT License. See the LICENSE file for details.

*LOMan (Last Oasis Manager) is not affiliated with Donkey Crew or Last Oasis. All trademarks are the property of their respective owners.*

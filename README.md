# CURE Ground Station

CU Rocketry Ground Station Software - A command-line interface for communicating with MARTHA-1.3 flight computer.

## Features

- Ping test for basic connectivity
- Version information retrieval
- Flash memory dump with CSV export and data visualization
- Rich command-line interface with progress tracking

## Installation

1. Clone the repository:
```bash
git clone https://github.com/CURocketEngineering/Ground-Station.git
cd Ground-Station
```

2. Install the package:
```bash
pip install -e .
```

## Usage

The Ground-Station can be run by typing the command `cure-ground` in the
terminal. Use the `--help` argument to get a list of all the available commands

```bash
cure-ground --help
```

```txt
❯ cure-ground --help

 Usage: cure-ground [OPTIONS] COMMAND [ARGS]...

 Ground Station CLI

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                              │
│ --show-completion             Show completion for the current shell, to copy it or customize the     │
│                               installation.                                                          │
│ --help                        Show this message and exit.                                            │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────╮
│ ping          Test connection to MARTHA device                                                       │
│ versions      Get version information from MARTHA device                                             │
│ flash-dump    Download and save flash memory contents                                                │
│ post-flight   Run the post-flight data collection & processing flow                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### GUI

To run the telemetry GUI, you'll first need to install some assets.

Download everything in [this assets folder](https://clemson.sharepoint.com/:f:/r/teams/ClemsonUniversityRocketEngineering/Shared%20Documents/CURE/Engineering%20Division/Subteams/Software/Ground-Station-Assets?csf=1&web=1&e=NV0l7o) and place it in `cure_ground/gui/resources`

You can then the run the GUI with:

```bash
cure-ground gui
```


### Post Flight

Run the post flight CLI flow to get data off of the connect flight computer
and then plot the data for quick analysis


### Ping Test

Test basic connectivity with the MARTHA device:
```bash
cure-ground ping /dev/ttyACM0
```

### Version Information

Get version information from all system components:
```bash
cure-ground versions /dev/ttyACM0
```

### Flash Memory Dump

Download and save flash memory contents with optional graph generation:
```bash
cure-ground flash-dump /dev/ttyACM0 --output flight_data.csv
```

Common options for all commands:
- `--baudrate`: Set serial communication speed (default: 115200)
- `--timeout`: Set operation timeout in seconds

## Development

The project follows a modular architecture with clear separation of concerns:

- `core/protocols/`: Communication protocol specifications
- `core/functions/`: Main functionality implementations
- `cli/`: Command-line interface

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Authors

Clemson University Rocket Engineering

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

The ground station provides three main commands:

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

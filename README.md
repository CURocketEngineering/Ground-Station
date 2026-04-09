# CURE Ground Station

CU Rocketry Ground Station software for communicating with MARTHA flight computers.

## What You Need

- A laptop with terminal access
- Python 3.9+ installed
- `uv` installed (instructions below)

If you are new to Python tooling: `uv` replaces most day-to-day `pip` and virtual environment setup steps.

## Install `uv` (One Time Per Laptop)

Choose your OS:

### macOS and Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows PowerShell

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After install, open a new terminal and verify:

```bash
uv --version
```

## First-Time Project Setup

From your terminal:

```bash
git clone https://github.com/CURocketEngineering/Ground-Station.git
cd Ground-Station
uv sync --dev
```

What this does:

- Creates a local virtual environment in `.venv`
- Installs all runtime dependencies
- Installs developer tools (like `ruff`, `pre-commit`)
- Uses the lockfile to keep installs consistent across the team

## Trouble Shooting:

If you are on a mac (or you are Stephanie), attempt the following command to run the gui
QT_PLUGIN_PATH=$VIRTUAL_ENV/lib/python3.14/site-packages/PyQt6/Qt6/plugins uv run cure-ground gui

## Run Commands (No Manual Activation Needed)

Use `uv run` so you can run commands directly from the repo root:

```bash
uv run cure-ground --help
uv run cure-ground gui
uv run cure-ground post-flight
uv run cure-ground regenerate-graphs /path/to/data.csv
```

## GUI Setup

Before launching the GUI, download the shared GUI assets and place them in:

- Linux/macOS: `cure_ground/gui/resources`
- Windows (same path from repo root): `cure_ground\gui\resources`

Assets folder:
[Ground-Station-Assets (SharePoint)](https://clemson.sharepoint.com/:f:/r/teams/ClemsonUniversityRocketEngineering/Shared%20Documents/CURE/Engineering%20Division/Subteams/Software/Ground-Station-Assets?csf=1&web=1&e=NV0l7o)

Then launch:

```bash
uv run cure-ground gui
```

## Optional: Activate The Environment

Most users should keep using `uv run ...`, but if you want direct command access:

- Linux/macOS: `source .venv/bin/activate`
- Windows PowerShell: `.\.venv\Scripts\Activate.ps1`
- Windows CMD: `.\.venv\Scripts\activate.bat`

Then you can run:

```bash
cure-ground --help
```

## Development

Useful commands:

```bash
uv run ruff check .
uv run pre-commit run --all-files
```

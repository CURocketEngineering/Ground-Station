# Winning Live Telemetry at IREC
## Purpose
This document is meant as a guide for the rules and regulations for the live video category at IREC so we can show off our live-telemetry and win awards.

## Links for Live-Video Category
- [IREC Rules and Regulations](https://static1.squarespace.com/static/687d3841f7d71450d1ba824d/t/68e1df27e7a32c225ccc7a98/1759633192115/IREC+Rules+and+Requirements+Document+2026+v.1.0.pdf) 
- [IREC Master Schedule](https://static1.squarespace.com/static/687d3841f7d71450d1ba824d/t/69bb0bf731bfc0438d97a5b1/1773865975905/2026+IREC+IMS+2026+V1.2.pdf)
- [IREC Live Video Challenge](https://www.esrarocket.org/live-rocket-video-challenge)

## What needs to happen before Launch?
Sometime, prior to lauch on June, Monday 15th and/or Tuesday 16th, you'll need to check in with the Media Team. They will have you demonstrate the telemetry function of MARTHA works in person. To do this you will have to get MARTHA up and running with Ground Station. 
### Below are simplified steps to do so:
#### Install git 

Windows (Powershell):
```bash
winget install --id Git.Git -e --source winget
```

Linux: 
```bash
sudo apt-get install git
```
See [Git Installation Guide](https://git-scm.com/install/windows) for addtional help

### Install uv (this will manage all Python stuff)
Windows: 
```bash 
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
For MacOS/Linux: 
```bash 
curl -LsSf https://astral.sh/uv/install.sh | sh
```
To verify installation: 
```bash
uv --version
```
### Install Ground Station
- Open terminal and move to desired directory (file) location
- Run:
```bash 
git clone https://github.com/CURocketEngineering/Ground-Station.git
cd Ground-Station
uv sync --dev
```
### Setup Ground Station
- Run:
```bash 
uv run cure-ground --help
uv run cure-ground gui
```

#### Lastly, run:
```bash
uv run cure-ground gui
```
This should start the ground station

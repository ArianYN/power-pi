# PowerPi - Smart Electricity Price Monitor

## What This Program Does

PowerPi is a Python application that monitors electricity prices and automatically enables a charger when prices are low.

### How It Works:

1. **Fetches Electricity Prices**: Every 5 minutes, the program connects to a Danish electricity price API to get the current electricity price per kWh.

2. **Retrieves Configuration**: It gets your personal settings from Boardom Dashboard. These settings are Electricity Company and Max Price/kwh

3. **Compares Prices**: It compares the current electricity price against your configured maximum price.

4. **Controls the Charger**: If the electricity price is below your threshold, it enables the charger. Otherwise, it keeps it disabled.

5. **Caches Data**: It stores the latest price information in a cache file for reference.

6. **Logs Everything**: The program provides detailed logs of what it's doing, so you can monitor its activity.

## Setup Requirements

### You Need a `config.py` File

This program **requires** a `config.py` file in the same directory with the following:

```python
USER_ID = "your_user_id_here"
```

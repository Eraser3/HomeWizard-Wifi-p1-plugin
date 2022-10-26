# HomeWizard-Wifi-p1-plugin
A Python plugin for Domoticz that creates several devices for the HomeWizard Wifi p1 meter.

![HomeWizard Wi-Fi P1 meter](https://www.homewizard.com/wp-content/uploads/2021/11/P1_meter_front-400x400.png)

The [HomeWizard Wi-Fi P1 meter](https://www.homewizard.com/nl/p1-meter/) is a little device that can be plugged into the P1 port of your smart energy meter. By default it sends all of its data to the HomeWizard servers but thanks to its local API you can read the device locally too. With this plugin you can use Domoticz to read the meter and store the data without using your internet connection.

# Devices

The plugin creates a total of 7 devices. Some may not be usefull for everyone but you can safely ignore those.
 1. An energy meter that shows your daily power draw and feed back on the grid
 2. An energy meter that shows your current power usage
 3. A gas meter that shows your daily and total usage
 4. A switch that will turn on once you start feeding back energy to the grid
 5. A switch that will turn on once you start feeding back a specific amount of energy to the grid
 6. A switch that will turn on once you draw a specific amount of energy from the grid
 7. A Wi-Fi signal strength meter that shows the current signal strength from the Wi-Fi P1 meter

# Configuration

The configuration is pretty self explaining. You just need the IP address of your Wi-Fi P1 meter. Make sure the IP address is static DHCP so it won't change over time.

| Configuration | Explanation |
|--|--|
| IP address | The IP address of the Wi-Fi P1 meter |
| Port | The port on which to connect (80 is default) |
| Data interval | The interval for the data devices to be refreshed |
| Switch interval | The interval for the switches to check for updated values |
| Usage value | The energy usage (in watts) on which the usage value switch will turn on |
| Production value | The energy feed back (in watts) on which the production value switch will turn on |
| Debug | Used by the developer to test stuff |

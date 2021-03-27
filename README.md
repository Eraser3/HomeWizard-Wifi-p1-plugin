# HomeWizard-Wifi-p1-plugin
A Python plugin for Domoticz that creates several devices for the HomeWizard Wifi p1 meter.

![HomeWizard Wi-Fi P1 meter](https://www.homewizard.nl/media/catalog/product/cache/ce597f02fc80ed34f99a6a3b0759b2b4/p/1/p1_meter.png)

The [HomeWizard Wi-Fi P1 meter](http://www.homewizard.nl/p1-meter) is a little device that can be plugged into the P1 port of your smart energy meter. By default it sends all of its data to the HomeWizard servers but thanks to its local API you can read the device locally too. With this plugin you can use Domoticz to read the meter and store the data without using your internet connection.

The plugin creates a total of 7 devices. Some may not be usefull for everyone but you can safely ignore those.
 1. An energy meter that shows your daily power draw and feed back on the grid
 2. An energy meter that shows your current power usage
 3. A gas meter that shows your daily and total usage
 4. A switch that will turn on once you start feeding back energy to the grid
 5. A switch that will turn on once you start feeding back a specific amount of energy to the grid
 6. A switch that will turn on once you draw a specific amount of energy from the grid
 7. A Wi-Fi signal strength meter that shows the current signal strength from the Wi-Fi P1 meter

The configuration is pretty self explaining. You just need the IP address of your Wi-Fi P1 meter. Make sure the IP address is static DHCP so it won't change over time.

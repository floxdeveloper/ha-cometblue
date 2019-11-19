
_Component to integrate with a German Eurotronic Comet Blue thermostat._
They are identical to the THERMy Blue (Aldi) Bluetooth thermostats

This is a modified version of neffs ha-cometblue integration. 
I just adapted the handles for the pin and the temperature.

This version is based on the bluepy library and works on hass.io. 
Currently only current and target temperature in manual mode is supported, nothing else. 


{% if not installed %}
## Installation

1. Click install.
1. Add mac address and pin to your HA configuration.

{% endif %}
## Example configuration.yaml

```yaml
climate cometblue:
  platform: cometblue
  devices:
    thermostat1:
      mac: 11:11:11:11:11:11
      pin: 000000
```

***

[ha-cometblue]: https://github.com/floxdeveloper/ha-cometblue

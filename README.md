# sfpmon
Python module that can be used to get SFP info from Cisco Switches

Usage:

Sample Code:
```
from sfpmon import Switch

if __name__ ==  "__main__":
switch = Switch('switchip',  username='username',  password='password')
for interface in switch.getSfpdetails():
	print(f"Name: {interface['name']}, Temperature: {interface['temperature']}, Voltage: {interface['voltage']}, TX Power: {interface['txpower']}, RX Power: {interface['rxpower']}")
```

Sample Code Output:
```
Name: Gi1/13, Temperature: 39.2, Voltage: 3.20, TX Power: -5.7, RX Power: -7.3
Name: Gi1/14, Temperature: 39.9, Voltage: 3.20, TX Power: -5.8, RX Power: -14.1
Name: Gi1/27, Temperature: 40.5, Voltage: 3.19, TX Power: -5.7, RX Power: -6.3
Name: Gi1/28, Temperature: 40.3, Voltage: 3.19, TX Power: -5.9, RX Power: -7.2
```

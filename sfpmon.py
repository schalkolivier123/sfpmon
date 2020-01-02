'''Author: Schalk Olivier
   Description: This module can be used to gather information about all the SFP modules that are connected to a cisco switch.
   Recommended Use: 1. Use portCheck to see if the telnet/ssh port is open to the switch.
                    2. Use sshConnect/telnetConnect to connect to the switch and get the output from the "show interface transceiver" command as a list of lines
                    3. Use getValues to go through the output from the switch and return all the info of the SFP Modules in a list.
                       Each interface will be a list entry represented as a dictionary containing: name, temperature, voltage, txpower, rxpower
   Example Output (getValues): [{'name': 'Gi1/13', 'temperature': '39.1', 'voltage': '3.20', 'txpower': '-5.7', 'rxpower': '-7.3'},
                                {'name': 'Gi1/14', 'temperature': '39.8', 'voltage': '3.20', 'txpower': '-5.8', 'rxpower': '-14.1'},
                                {'name': 'Gi1/27', 'temperature': '40.4', 'voltage': '3.19', 'txpower': '-5.7', 'rxpower': '-6.3'},
                                {'name': 'Gi1/28', 'temperature': '40.2', 'voltage': '3.19', 'txpower': '-5.9', 'rxpower': '-7.2'}]
   Requirements: The user used for login to the switch has to be priviledge level 15
'''

import paramiko
from socket import socket, AF_INET, SOCK_STREAM
from time import sleep
from telnetlib import Telnet
from getpass import getpass
from prettytable import PrettyTable
from os import name as osname
from os import system

def portCheck(ip, port):
  s = socket(AF_INET, SOCK_STREAM)
  try:
    s.connect((ip, int(port)))
    s.shutdown(2)
    return True
  except:
    return False

def sshConnect(ip, username, password):
  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  ssh.connect(ip, username=username, password=password, banner_timeout=10)
  _, commandoutput, _ = ssh.exec_command('show interface transceiver')
  return commandoutput

def telnetConnect(ip, username, password):
  with Telnet(ip, 23, timeout=10) as cw:
    cw.write(username.encode() + b'\n')
    cw.write(password.encode() + b'\n')
    cw.write(b'terminal length 0\n')
    cw.write(b'show interface transceiver\n')
    cw.write(b'exit\n')
    return cw.read_all().decode().splitlines()

def getValues(commandoutput):
  interfaces = []
  for line in commandoutput:
    line = line.rstrip()
    try:
      if (line[0:2] == 'Gi') or (line[0:2] == 'Te') or (line[0:2] == 'Fa'):
        interface = {}
        if len(line.split()) == 5: #Does not include Current (mA)
          interface['name'], interface['temperature'], interface['voltage'], interface['txpower'], interface['rxpower'] = line.split()
        elif len(line.split()) == 6: #Includes Current (mA)
          interface['name'], interface['temperature'], interface['voltage'], _, interface['txpower'], interface['rxpower'] = line.split()
        interfaces.append(interface)
    except Exception as e:
      print(e)
      continue
  return interfaces

if __name__ == '__main__':
  '''This main thread is only used to demonstrate how the sfpmon module can be used 
  for the gathering of SFP information from Cisco Switches and should not be used in any production environment'''

  def clearcli():
    '''Locally defined function to clear the CLI'''

    if osname == 'posix':
      system('clear')
    elif osname == 'nt':
      system('cls')
  
  def getInput():
    '''Locally defined function to get user input'''
    
    clearcli()
    print(f'Enter below info to get details of SFP Modules\n')
    userinput = []
    userinput.append(input('IP Address: '))
    userinput.append(input('Username: '))
    userinput.append(getpass('Password: '))
    return userinput

  def continueCli():
    '''Locally defined function to exit the CLI and clear the CLI'''
    
    input("\nPress any key to continue")
    clearcli()

  def updateTable(table, sfpValues):
    for interface in getValues(sfpValues):
      table.add_row([f'{interface["name"]}', f'{interface["temperature"]} \u00b0C', f'{interface["voltage"]} V', f'{interface["txpower"]} dBm', f'{interface["rxpower"]} dBm'])
    print(table)
  
  clearcli()
  print(f'This is an example to show how the sfpmon.py module can be used to gather info about SFP modules on cisco switches.\n')
  continueCli()

  ip, username, password = getInput()
  clearcli()

  print(f'\nSFP Details for {ip}:\n')
  table = PrettyTable(['Port', 'Temperature', 'Voltage', 'RX Power', 'TX Power'])

  if portCheck(ip, 22):
    commandoutput = sshConnect(ip, username, password)
    updateTable(table, commandoutput)
  elif portCheck(ip, 23):
    commandoutput = telnetConnect(ip, username, password)
    updateTable(table, commandoutput)
  else:
    print(f'{ip} is not responding to SSH or Telnet')
  
  continueCli()
  

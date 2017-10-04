from bluezero import adapter
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


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
    logger = logging.getLogger('adapter')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(NullHandler())
    main()

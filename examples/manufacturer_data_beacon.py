from bluezero import broadcaster


def main():
    alt = broadcaster.Beacon()
    alt.add_manufacturer_data(
        'ffff',  # Manufacturer ID (0xffff = Not for production)
        b'\xBE\xAC'   # beacon code for Alt Beacon
        + 16 * b'\xbe'   # Beacon UUID
        + 4 * b'\x00'  # Free
        + b'\x01')  # Transmit power

    alt.start_beacon()


if __name__ == '__main__':
    main()

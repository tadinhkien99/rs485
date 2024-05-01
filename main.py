import serial
import yaml

from utils import getversion, takephoto, getbufferlength, readbuffer, setup_logger



if __name__ == '__main__':

    # Setup logger
    logger = setup_logger()

    # config.yaml path
    config_path = "config.yaml"
    with open(config_path, "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.Loader)
        cameraConfigs = cfg.get('cameras')
        PORT = cfg['serial']['port']
        BAUD = cfg['serial']['baud']
        TIMEOUT = cfg['serial']['timeout']

    for cameraConfig in cameraConfigs:
        # Set the camera address
        camera_address = cameraConfig.get('camera').get('address')
        SERIALNUM = camera_address
        logger.info(f"Camera address: {camera_address}")
        # Creating a session
        s = serial.Serial(PORT, baudrate=BAUD, timeout=TIMEOUT)
        if not getversion(s, logger):
            print("Camera", camera_address, "not found")
            continue
        if takephoto(s, logger):
            print("Snap!")
        bytes_buffer = getbufferlength(s, logger)
        photo_data = readbuffer(s, bytes_buffer, logger)

        # Save picture with names from config
        with open(cameraConfig.get('camera').get('name'), 'wb') as f:
            f.write(photo_data)

        print("Photo has been taken from Camera", camera_address)
        print(f"Photo has been save to {cameraConfig.get('camera').get('name')}")

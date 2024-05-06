import time

from serial_operation import SerialOperation
from config import Config


if __name__ == '__main__':
    config = Config("config.yaml")
    camera_configs, port, baud, timeout,SN = config.camera_config()
    azure_config = config.azure_config()
    logger = config.setup_logger()
    internet_status = False

    for camera_config in camera_configs:
        camera_address = camera_config.get('camera').get('address')
        try:
         worker = SerialOperation(camera_address, port, baud, timeout, logger)
        except:
          print("cannot Open Com")
          exit(1)
        try:
            version_status = worker.get_version()
        except:
            print("cannot connect to camera",camera_address)
            worker.disconnect()
            continue
        if not version_status:
            worker.disconnect()
            continue

        if worker.take_photo():
            print("take picture from camera ",camera_address)
            buffer_length, hex_reply = worker.get_buffer_length()
            photo_data = worker.read_buffer_photo(buffer_length, hex_reply)
            with open(camera_config.get('camera').get('name'), 'wb') as f:
                f.write(photo_data)
            print("Photo has been taken from Camera", camera_address)
        else:
            print("Failed to take photo for camera",camera_address)
            continue

        worker.disconnect()

    # i=0
    # while not internet_status:
    #     time.sleep(1)
    #     i += 1
    #     logger.info("waiting for internet connection {}seconds".format(i))
    #     internetstatus = connect()
    #
    #     if i > 200:
    #         logger.info("internet connection timeout")
    #         break
    #
    # if internetstatus:
    #     logger.info(" connection to internet successful ")

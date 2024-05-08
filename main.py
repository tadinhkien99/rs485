import os
from datetime import datetime

from config import Config
from operation import SerialOperation, AzureOperation
from utils import create_directory

if __name__ == '__main__':
    config = Config("config.yaml")
    camera_configs, port, baud, timeout = config.camera_config()
    azure_config = config.azure_config()
    azure_worker = AzureOperation(azure_config[0], azure_config[1])
    logger = config.setup_logger()
    internet_status = False

    cargo_serial, base_path = config.cargo_config()

    current_date = datetime.now().strftime("%Y-%m-%d-%H-%M")
    datapath = os.path.join(base_path, cargo_serial, current_date)
    create_directory(datapath)

    for camera_config in camera_configs:
        address = camera_config.get('camera').get('address')

        try:
            worker = SerialOperation(address, port, baud, timeout, logger)
        except:
            print("cannot Open Com")
            exit(1)
        try:
            version_status = worker.get_version()
        except:
            print("cannot connect to camera", address)
            worker.disconnect()
            continue
        if not version_status:
            worker.disconnect()
            continue

        if worker.take_photo():
            print("take picture from camera ", address)
            buffer_length, hex_reply = worker.get_buffer_length()
            photo_data = worker.read_buffer_photo(buffer_length, hex_reply)

            image_name = f"{camera_config.get('camera').get('name')}.jpg"
            image_path = os.path.join(datapath, image_name)
            with open(image_path, 'wb') as f:
                f.write(photo_data)
            print("Photo has been taken from Camera", address)

            azure_worker.upload_blob(image_path, image_name)
        else:
            print("Failed to take photo for camera", address)
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

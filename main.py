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

    for camera_config in camera_configs:

        serial_number = camera_config.get('camera').get('address')
        current_date = datetime.now().strftime("%Y-%m-%d")
        create_directory(os.path.join(serial_number, current_date))

        try:
            worker = SerialOperation(serial_number, port, baud, timeout, logger)
        except:
            print("cannot Open Com")
            exit(1)
        try:
            version_status = worker.get_version()
        except:
            print("cannot connect to camera", serial_number)
            worker.disconnect()
            continue
        if not version_status:
            worker.disconnect()
            continue

        if worker.take_photo():
            print("take picture from camera ", serial_number)
            buffer_length, hex_reply = worker.get_buffer_length()
            photo_data = worker.read_buffer_photo(buffer_length, hex_reply)

            image_name = f"{serial_number}_{current_date}_{camera_config.get('camera').get('name')}.jpg"
            image_path = os.path.join(serial_number, current_date, image_name)
            with open(image_path, 'wb') as f:
                f.write(photo_data)
            print("Photo has been taken from Camera", serial_number)

            azure_worker.upload_blob(image_path, image_name)
        else:
            print("Failed to take photo for camera", serial_number)
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

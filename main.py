from serial_operation import SerialOperation
from config import Config


if __name__ == '__main__':
    config = Config("config.yaml")
    camera_configs, port, baud, timeout = config.config()
    logger = config.setup_logger()
    for camera_config in camera_configs:
        camera_address = camera_config.get('camera').get('address')

        worker = SerialOperation(camera_address, port, baud, timeout, logger)
        version_status = worker.get_version()
        if not version_status:
            continue

        if worker.take_photo():
            print("Snap!")
            buffer_length, hex_reply = worker.get_buffer_length()
            photo_data = worker.read_buffer_photo(buffer_length, hex_reply)
            with open(camera_config.get('camera').get('name'), 'wb') as f:
                f.write(photo_data)
            print("Photo has been taken from Camera", camera_address)
        else:
            print("Failed to take photo")
            continue


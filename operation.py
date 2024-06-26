#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    serial_operation.py
# @Author:      kien.tadinh
# @Time:        5/4/2024 10:56 AM

import serial
from azure.storage.blob import ContainerClient


class SerialOperation:
    def __init__(self, serial_num, port, baud, timeout, loger):
        self.logger = loger
        self.serial_worker = serial.Serial(port, baudrate=baud, timeout=timeout)
        self.command_send = 0x56
        self.command_reply = 0x76
        self.command_read = 0x32

        self.serial_num = serial_num

        self.command_take_photo = 0x36
        self.command_get_buffer_length = 0x34
        self.command_end = 0x00

        self.command_get_version = 0x11
        self.command_begin_photo = [0xFF, 0xD8]
        self.command_end_photo = [0xFF, 0xD9]

    def disconnect(self):
        self.serial_worker.close()

    def concatenate_buffer_length(self, bytes_buffer):
        begin_bytes_buffer = bytes(
            [self.command_send, self.serial_num, self.command_read, 0x0C, 0x00, 0x0A, 0x00, 0x00, 0x00, 0x00])
        end_bytes_buffer = bytes([0x00, 0xFF])
        return begin_bytes_buffer + bytes_buffer + end_bytes_buffer

    def check_reply(self, reply, check_command):
        if reply[0] == self.command_reply and reply[1] == self.serial_num and reply[2] == check_command and reply[3] == 0x00:
            return True
        return False

    def get_version(self):
        get_version_command = bytes([self.command_send, self.serial_num, self.command_get_version, self.command_end])
        self.serial_worker.write(get_version_command)
        reply = self.serial_worker.read(18)
        return self.check_reply(reply, self.command_get_version)

    def take_photo(self):
        take_photo_command = bytes(
            [self.command_send, self.serial_num, self.command_take_photo, 0x01, self.command_end])
        self.serial_worker.write(take_photo_command)
        reply = self.serial_worker.read(12)
        if self.check_reply(reply, self.command_take_photo):
            return True
        return False

    def get_buffer_length(self):
        get_buffer_length_command = bytes(
            [self.command_send, self.serial_num, self.command_get_buffer_length, 0x01, self.command_end])
        self.serial_worker.write(get_buffer_length_command)
        reply = self.serial_worker.read(9)
        if self.check_reply(reply, self.command_get_buffer_length) and reply[4] == 0x04:
            length = reply[5]
            length <<= 8
            length += reply[6]
            length <<= 8
            length += reply[7]
            length <<= 8
            length += reply[8]
            return length, reply[5:9]
        else:
            return 0, 0

    def read_buffer_photo(self, total_bytes, bytes_buffer):
        read_photo_command = self.concatenate_buffer_length(bytes_buffer)
        self.serial_worker.write(read_photo_command)
        bytes_read = 0
        photo_buffer = bytearray()
        end_marker = bytes(self.command_end_photo)
        start_marker = bytes(self.command_begin_photo)

        start_found = False  # Track if start marker is already detected

        while bytes_read < total_bytes:
            to_read = min(128, total_bytes - bytes_read)
            data = self.serial_worker.read(to_read)
            if not data:
                break
            bytes_read += len(data)
            if not start_found:
                start_index = data.find(start_marker)
                if start_index != -1:
                    data = data[start_index:]  # Remove the start marker
                    start_found = True
                else:
                    continue  # Start marker not found, skip this part

            if start_found:
                end_index = data.find(end_marker)
                if end_index == -1:
                    photo_buffer.extend(data)

                else:
                    photo_buffer.extend(data[:end_index + 2])
                    break  # Found the end marker, stop reading

        return bytes(photo_buffer)


class AzureOperation:
    def __init__(self, connection_string, container_name, logger=None):
        self.logger = logger
        self.connection_string = connection_string
        self.container_name = container_name
        self.container_client = ContainerClient.from_connection_string(self.connection_string, container_name)

    def upload_blob(self, file_path, blob_name):
        try:
            blob_client = self.container_client.get_blob_client(blob=blob_name)
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data)
            print("Upload blob successfully")
        except Exception as e:
            print("Upload blob failed")
            print(e)

    def delete_blob(self, blob_name):
        try:
            blob_client = self.container_client.get_blob_client(blob=blob_name)
            blob_client.delete_blob()
            print("Delete blob successfully")
        except Exception as e:
            print("Delete blob failed")
            print(e)

    def list_blobs(self):
        try:
            return [blob.name for blob in self.container_client.list_blobs()]
        except Exception as e:
            print("List blobs failed")
            return []

    def download_blob(self, blob_name, download_file_path):
        try:
            blob_client = self.container_client.get_blob_client(blob=blob_name)
            with open(download_file_path, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())
            print("Download blob successfully")
        except Exception as e:
            print("Download blob failed")
            print(e)

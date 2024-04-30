import logging


SERIALNUM = 1  # start with 0, each camera should have a unique ID.

COMMANDSEND = 0x56
COMMANDREPLY = 0x76
COMMANDEND = 0x00

CMD_GETVERSION = 0x11
CMD_RESET = 0x26
CMD_TAKEPHOTO = 0x36
CMD_READBUFF = 0x32
CMD_GETBUFFLEN = 0x34

FBUF_CURRENTFRAME = 0x00
FBUF_NEXTFRAME = 0x01

FBUF_STOPCURRENTFRAME = 0x00

getversioncommand = [COMMANDSEND, SERIALNUM, CMD_GETVERSION, COMMANDEND]
resetcommand = [COMMANDSEND, SERIALNUM, CMD_RESET, COMMANDEND]
takephotocommand = [COMMANDSEND, SERIALNUM, CMD_TAKEPHOTO, 0x01, FBUF_STOPCURRENTFRAME]  # 56, 01, 36, 01, 00
getbufflencommand = [COMMANDSEND, SERIALNUM, CMD_GETBUFFLEN, 0x01, FBUF_CURRENTFRAME]
readphotocommand = [COMMANDSEND, SERIALNUM, CMD_READBUFF, 0x0c, FBUF_CURRENTFRAME, 0x0a]

# Set up logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Print to console
console = logging.StreamHandler()
logger.addHandler(console)


def checkreply(r, b):
    if r[0] == COMMANDREPLY and r[1] == SERIALNUM and r[2] == b and r[3] == 0x00:
        return True
    return False


def getversion(s):
    cmd = bytes(getversioncommand)
    s.write(cmd)
    reply = s.read(18)
    logger.info(f"Version: {reply}")
    r = list(reply)
    if checkreply(r, CMD_GETVERSION):
        print("Camera Found:", r)
        return True
    return False


def takephoto(s):
    cmd = bytes(takephotocommand)
    s.write(cmd)
    reply = s.read(12)
    logger.info(f"Take photo: {reply}")
    r = list(reply)
    if checkreply(r, CMD_TAKEPHOTO) and r[3] == chr(0x0):
        return True
    return False


def getbufferlength(s):
    cmd = bytes(getbufflencommand)
    s.write(cmd)
    reply = s.read(9)
    logger.info(f"Buffer length: {reply}")
    r = list(reply)
    if r[4] == 0x4:
        l = r[6]
        l <<= 8
        l += r[7]
        l <<= 8
        l += r[8]
        return l
    return 0


def readbuffer(s, total_bytes):
    addr = 0  # the initial offset into the frame buffer
    photo = bytearray()  # Using bytearray for efficient data appending
    inc = 8192  # Bytes to read each time (must be a multiple of 4)
    while addr < total_bytes:
        chunk = min(total_bytes - addr, inc)  # On the last read, adjust chunk size

        # Construct command
        command = readphotocommand + [
            (addr >> 24) & 0xff, (addr >> 16) & 0xff,
            (addr >> 8) & 0xff, addr & 0xff,
            (chunk >> 24) & 0xff, (chunk >> 16) & 0xff,
            (chunk >> 8) & 0xff, chunk & 0xff,
            1, 0  # Append any command delay or additional bytes
        ]
        cmd = bytes(command)
        s.write(cmd)
        reply = s.read(5 + chunk + 5)
        if len(reply) != 5 + chunk + 5:
            print(f"Read {len(reply)} bytes, retrying.")
            continue

        r = list(reply)
        if not checkreply(r[1:5], CMD_READBUFF):
            print("ERROR READING PHOTO")
            return None

        photo.extend(r[5:-5])
        addr += chunk
    return photo

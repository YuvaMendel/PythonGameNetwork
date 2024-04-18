size_header_size = 5
DEBUG_FLAG = False


def __log(prefix, data, max_to_print=100):
    if not DEBUG_FLAG:
        return
    data_to_log = data[:max_to_print]
    if type(data_to_log) == bytes:
        try:
            data_to_log = data_to_log.decode()
        except (UnicodeDecodeError, AttributeError):
            pass
    print(f"\n{prefix}({len(data)})>>>{data_to_log}")


def __recv_amount(sock, size=4):
    buffer = b''
    while size:
        new_bufffer = sock.recv(size)
        if not new_bufffer:
            return b''
        buffer += new_bufffer
        size -= len(new_bufffer)
    return buffer


def recv_by_size(sock, return_type="bytes"):
    try:
        data = b''
        data_len = int(__recv_amount(sock, size_header_size))
        # code handle the case of data_len 0
        data = __recv_amount(sock, data_len)
        __log("Receive", data)
        if return_type == "string":
            return data.decode()
    except OSError:
        data = '' if return_type == "string" else b''
    return data


def send_with_size(sock, data):
    if len(data) == 0:
        return
    try:
        if type(data) != bytes:
            data = data.encode()
        len_data = str(len(data)).zfill(size_header_size).encode()
        data = len_data + data
        sock.sendall(data)
        __log("Sent", data)
    except OSError:
        print('ERROR: send_with_size with except OSError')
import struct

BIG_ENDIAN = 0
LITTLE_ENDIAN = 1


class BytesReader:
    """
    字节流读取类
    """
    by: memoryview = None
    endian = 0
    offset = 0

    def __init__(self, by):
        self.by = memoryview(by)

    @property
    def endian_str(self):
        if self.endian == 0:
            # 大端
            return '>'
        else:
            # 小端
            return '<'

    def read_short(self):
        res = struct.unpack_from(self.endian_str + 'h', self.by, self.offset)[0]
        self.offset += 2
        return res

    def read_ushort(self):
        res = struct.unpack_from(self.endian_str + 'H', self.by, self.offset)[0]
        self.offset += 2
        return res

    def read_byte(self):
        res = struct.unpack_from(self.endian_str + 'b', self.by, self.offset)[0]
        self.offset += 1
        return res

    def read_ubyte(self):
        res = struct.unpack_from(self.endian_str + 'B', self.by, self.offset)[0]
        self.offset += 1
        return res

    def read_bool(self):
        res = struct.unpack_from(self.endian_str + '?', self.by, self.offset)[0]
        self.offset += 1
        return res

    def read_int(self):
        res = struct.unpack_from(self.endian_str + 'i', self.by, self.offset)[0]
        self.offset += 4
        return res

    def read_uint(self):
        res = struct.unpack_from(self.endian_str + 'I', self.by, self.offset)[0]
        self.offset += 4
        return res

    def read_long(self):
        res = struct.unpack_from(self.endian_str + 'l', self.by, self.offset)[0]
        self.offset += 4
        return res

    def read_ulong(self):
        res = struct.unpack_from(self.endian_str + 'L', self.by, self.offset)[0]
        self.offset += 4
        return res

    def read_longlong(self):
        res = struct.unpack_from(self.endian_str + 'q', self.by, self.offset)[0]
        self.offset += 8
        return res

    def read_ulonglong(self):
        res = struct.unpack_from(self.endian_str + 'Q', self.by, self.offset)[0]
        self.offset += 8
        return res

    def read_float(self):
        res = struct.unpack_from(self.endian_str + 'f', self.by, self.offset)[0]
        self.offset += 4
        return res

    def read_double(self):
        res = struct.unpack_from(self.endian_str + 'd', self.by, self.offset)[0]
        self.offset += 8
        return res

    def read_utf(self):
        count = struct.unpack_from(self.endian_str + 'H', self.by, self.offset)[0]
        tby = self.by[self.offset + 2:self.offset + 2 + count]
        res = tby.tobytes().decode('utf-8', errors='ignore')
        self.offset += 2 + count
        return res


"""
默认的编码方式 默认值为大端
"""
default_endian = 0


def get_endian_str():
    if default_endian == 0:
        # 大端
        return '>'
    else:
        # 小端
        return '<'


def write_short(val):
    return struct.pack(get_endian_str() + 'h', val)


def write_ushort(val):
    return struct.pack(get_endian_str() + 'H', val)


def write_byte(val):
    return struct.pack(get_endian_str() + 'b', val)


def write_ubyte(val):
    return struct.pack(get_endian_str() + 'B', val)


def write_bool(val):
    return struct.pack(get_endian_str() + '?', val)


def write_int(val):
    return struct.pack(get_endian_str() + 'i', val)


def write_uint(val):
    return struct.pack(get_endian_str() + 'I', val)


def write_long(val):
    return struct.pack(get_endian_str() + 'l', val)


def write_ulong(val):
    return struct.pack(get_endian_str() + 'L', val)


def write_longlong(val):
    return struct.pack(get_endian_str() + 'q', val)


def write_ulonglong(val):
    return struct.pack(get_endian_str() + 'Q', val)


def write_float(val):
    return struct.pack(get_endian_str() + 'f', val)


def write_double(val):
    return struct.pack(get_endian_str() + 'd', val)


def write_utf(val: str):
    sby = val.encode()
    count = len(sby)
    return struct.pack('{0}H{1}s'.format(get_endian_str(), count), count, sby)

import re



class AsyncType:
    def __init__(self):
        self.gdb_symbol = None
        self.type_name = None
        self.full_type_name = None
        self.short_name = None

    def get_type_name(self):
        return self.type_name

    def get_full_type_name(self):
        return self.full_type_name

    def set_gdb_symbol(self, sym):
        self.gdb_symbol = sym

    @classmethod
    def handles_type_string(cls, s):
        if cls.type_match:
            return re.match(cls.type_match, s)

        return None

    @classmethod
    def instantiate(cls, s):
        m = cls.handles_type_string(s)
        if not m:
            return None

        return cls(m)
        
        

class CTString (AsyncType):
    type_match = re.compile(r"stdx::v1::ct_string<(\d+)ul>{std::__1::array<char, (\d+)ul>{(.+)}}")

    def __init__(self, matched):
        super(AsyncType, self).__init__()
        self.type_name = "ct_string"
        str_elements = re.compile(r"\(char\)(\d+)")
        chars = re.findall(str_elements, matched.group(3))
        self.short_name = "".join(chr(int(m)) for m in chars)
        self.full_type_name = '{}<"{}">'.format(self.type_name, self.short_name)
        


ctstring_test = "stdx::v1::ct_string<7ul>{std::__1::array<char, 7ul>{char [7]{(char)67, (char)104, (char)97, (char)105, (char)110, (char)65}}}"

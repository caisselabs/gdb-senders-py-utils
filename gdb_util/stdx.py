import re
import cxxfilt


ct_type_split_re = re.compile(r"stdx::v1::ct_string<\d+ul>{std::__1::array<char, \d+ul>{.+?}}}")
ct_type_name_re = re.compile(r"stdx::v1::ct_string<\d+ul>{std::__1::array<char, \d+ul>{char \[\d+\]{(.+?)}}}")


def prettify_ct_string(s):
    str_elements = re.compile(r"\(char\)(\d+)")
    chars = re.findall(str_elements, s)
    return "".join(chr(int(m)) for m in chars)
     

def prettify_ct_strings(s, pre=None, post=None):
    if pre is None:
        pre = ""
    if post is None:
        post = ""

    # get all ct_string matches
    ct_matches = re.findall(ct_type_name_re, s)
    ct_raw_strings = [prettify_ct_string(m) for m in ct_matches]

    # split on the ct_strings
    other_info = re.split(ct_type_split_re, s)

    # put back together
    r = "".join(f'{v[0]}{pre}"{v[1]}"{post}' for v in zip(other_info, ct_raw_strings))
    r += other_info[-1]
    return r

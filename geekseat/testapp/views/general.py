import re

from testapp.models.raw_model import RawModel


def check_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    res = True

    if re.fullmatch(regex, email):
        res = False
    else:
        res = True

    return res


def gen_bcrypt(string):
    rows = RawModel.objects.raw("select 1 as id, crypt(%s, gen_salt('bf')) as bcrypt;", [string])

    res = None
    for row in rows:
        res = row.bcrypt

    return res


def gen_token(key, string):
    if len(key) > 8:
        key = key[:8]

    value = key + string
    rows = RawModel.objects.raw("select 1 as id, md5(%s) as md5", [value])
    res = None
    for row in rows:
        res = row.md5

    return res


# def check_bcrypt(table, string):
#     row = RawModel.objects.raw("select 1 as id, crypt(%s, gen_salt('bf')) as bcrypt;", [string])
#
#     res = None
#     for p in row:
#         res = p.bcrypt
#
#     return res

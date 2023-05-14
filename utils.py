from uuid import uuid4


def create_uuid():
    """This uses uuid python module to return a Universally Unique IDentifier
    which is a 36-character alphanumeric string that can be used to identify tables"""
    return uuid4().hex

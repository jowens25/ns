from dbus_next.signature import Variant

def formatListToString(elements: list[str]) -> str:
    if len(elements) == 0:
        return None
    return ', '.join(elements) if elements else ''


def formatStringToList(my_string: str) -> list[str]:

    return [item.strip() for item in my_string.split(',')]



def var_get(_dic: dict, _val:str) -> str:
    return _dic.get(_val, Variant('s', "NA")).value

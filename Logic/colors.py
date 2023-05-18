###############################################################################

def red(txt: str):
    """
    It takes a string as input and returns the same string with red text

    :param txt: str - the text to be colored
    :type txt: str
    :return: the string with the color code.
    """
    return '\033[1;31;48m' + txt + '\033[1;37;0m'


def green(txt: str):
    """
    It takes a string as input and returns a string with the string in green

    :param txt: str - the text to be colored
    :type txt: str
    :return: the string with the color code.
    """
    return '\033[1;32;48m' + txt + '\033[1;37;0m'

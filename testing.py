import inspect
from pprint import pformat

def fp(*args):
    frame = inspect.currentframe().f_back
    code_context = inspect.getframeinfo(frame).code_context[0]

    name = inspect.stack()[0][3]

    start = code_context.find(name+"(") + len(name+")")
    end = code_context.find(")")

    var_names = [arg.strip() for arg in code_context[start:end].split(',')]

    print(*(f"{text} = {pformat(arg_value)}" for text, arg_value in zip(var_names, args)), sep=" | ")
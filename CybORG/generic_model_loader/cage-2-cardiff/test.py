import inspect

def wrap():
    print("In inspection")
    pass

lines = inspect.getsource(wrap)
print(lines)


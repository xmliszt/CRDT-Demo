import commands


def get_operations():
    print('''
  Choose an operation from below to perform:
  I1: Increment counter by 1
  D1: Decrement counter by 1
  M1: Multiply counter by 1
  L1: Divide counter by 1
  In: Increment counter by n, n is a custom integer
  Dn: Decrement counter by n, n is a custom integer
  Mn: Multiply counter by n, n is a custom integer
  Ln: Divide counter by n, n is a custom integer
  ''')
    ops = []
    choice = input(
        "Enter a serires of operations separated by space or <Enter> to quit: \n"
    )
    if choice == "":
        return []
    try:
        choices = choice.split(" ")
        for c in choices:
            o = c.lower()[0]
            n = int(c.strip(" ")[1:])
            if o not in ['i', 'd', 'm', 'l']:
                raise Exception
            ops.append((o, n))
        return ops
    except Exception:
        print("Invalid operation format!")
        return False


def merge_operations(operations, data):
    if commands.INCREMENT in data:
        operations.append(data)
    elif commands.DECREMENT in data:
        operations.append(data)
    elif commands.MULTIPLY in data:
        operations.insert(0, data)
    elif commands.DIVIDE in data:
        operations.insert(0, data)
    return operations

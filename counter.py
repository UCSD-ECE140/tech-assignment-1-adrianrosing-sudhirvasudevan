def add():
    try:
        with open("counter.txt", "r") as file:
            counter = int(file.read())
    except FileNotFoundError:
        counter = 0

    counter += 1
    with open("counter.txt", "w") as file:
        file.write(str(counter))
    return counter

def subtract():
    try:
        with open("counter.txt", "r") as file:
            counter = int(file.read())
    except FileNotFoundError:
        counter = 0

    counter -= 1
    with open("counter.txt", "w") as file:
        file.write(str(counter))
    return counter


def get():
    with open("counter.txt", "r") as file:
        counter = int(file.read())
    return counter

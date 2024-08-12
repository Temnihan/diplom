import random
def generate_task():
    num1 = random.randint(10, 99)
    num2 = random.randint(10, 99)
    example = f"{num1} + {num2}"
    answer = num1 + num2

    return example, answer
import random
def generate_task():
    num1 = random.randint(10, 99)
    num2 = random.randint(10, 99)
    example = f"{num1} + {num2}"
    answer = num1 + num2

    if num1+num2 <11:
        category = 'To_easy'
    elif  num1%10 +num2%10 <10:
        if num2 or num1 <10:
            category = 'easy'
        else:
            category = 'to_medium'
    elif abs(num1 -num2)<10:
        category = 'medium'
    elif abs(num2 - num1)<50:
        category = 'hard'
    else:
        category = 'v_hard'

    return example, answer,num1,num2
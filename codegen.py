import random


def generate_code(number=1, length=20):

    chars = '+-/*!&$#?=@<>abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'

    for n in range(number):
        password = ''
        for i in range(length):
            password += random.choice(chars)
        return password

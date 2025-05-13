import string
import random
from zxcvbn import zxcvbn


def generate_password(size=20):
    if size < 20:
        print("You picked a size smaller than 20 characters...\n Automatically set to 20.")
        size = 20
    lowercase_chars = list(string.ascii_lowercase)
    uppercase_chars = list(string.ascii_uppercase)
    digits_chars = list(string.digits)
    symbols_chars = list(string.punctuation)

    random.shuffle(lowercase_chars)
    random.shuffle(uppercase_chars)
    random.shuffle(digits_chars)
    random.shuffle(symbols_chars)

    symbol_digit_ratio = round(size * (20 / 100))
    letter_ratio = round(size * (30 / 100))

    passw = []

    for i in range(letter_ratio):
        passw.append(lowercase_chars[i])
        passw.append(uppercase_chars[i])

    for i in range(symbol_digit_ratio):
        passw.append(symbols_chars[i])
        passw.append(digits_chars[i])

    random.shuffle(passw)

    return ''.join(passw)


def check_password(password):
    result = zxcvbn(password)
    # print(f"Value: {result['password']}")
    # print(f"Password Score: {result['score']}/4")
    # print(f"Crack Time: {result['crack_times_display']['offline_slow_hashing_1e4_per_second']}")
    # print(f"Feedback: {result['feedback']['suggestions']}")
    return result['score'], result['feedback']['suggestions']






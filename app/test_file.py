# test_file.py

API_KEY = "dummy-key"
API_URL = "https://example.com"


def greet():
    print("Hello")


def greet_again():
    print("Hello")


def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


class Calculator:
    def multiply(self, a, b):
        return a * b

    def divide(self, a, b):
        return a / b


if __name__ == "__main__":
    print("Program started")

    result1 = add(5, 3)
    result2 = subtract(10, 4)

    print("Result:", result1)
    print("Result:", result2)

    greet()
    greet_again()
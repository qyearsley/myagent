#!/usr/bin/env python3

from functions.get_file_content import get_file_content


def main():
    get_file_content("calculator", "lorem.txt")
    get_file_content("calculator", "main.py")
    get_file_content("calculator", "pkg/calculator.py")
    get_file_content("calculator", "/bin/cat")  # (this should return an error string)
    get_file_content(
        "calculator", "pkg/does_not_exist.py"
    )  # (this should return an error string)


if __name__ == "__main__":
    main()

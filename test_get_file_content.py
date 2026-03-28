#!/usr/bin/env python3

from functions.get_file_content import get_file_content


def main():
    print(get_file_content("calculator", "lorem.txt"))
    print(get_file_content("calculator", "main.py"))
    print(get_file_content("calculator", "pkg/calculator.py"))
    print(get_file_content("calculator", "/bin/cat"))  # (this should return an error string)
    print(
        get_file_content("calculator", "pkg/does_not_exist.py")
    )  # (this should return an error string)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

from functions.write_file import write_file


def main():
    write_file("calculator", "lorem.txt", "wait, this isn't lorem ipsum")
    write_file("calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet")
    write_file("calculator", "/tmp/temp.txt", "this should not be allowed")


if __name__ == "__main__":
    main()


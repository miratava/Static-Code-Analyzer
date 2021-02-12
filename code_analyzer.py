import enum
from abc import ABC
import re
import sys
import os
import re


class Status(enum.Enum):
    ok = 1
    error = 2


class Message(str, enum.Enum):
    too_long = "S001"
    not_four = "S002"
    semicolon = "S003"
    two_space = "S004"
    todo = "S005"
    two_blank = "S006"


class Input(ABC):
    def get_input_path_to_file(self):
        pass


class Arg(Input):
    def get_input_path_to_file(self):
        return sys.argv[0]


class CLI(Input):
    def get_input_path_to_file(self):
        return input()


class Analyzer:

    messages = {Message.too_long: "S001 Too long",
                Message.not_four: "S002 Indentation is not a multiple of four",
                Message.semicolon: "S003 Unnecessary semicolon",
                Message.two_space: "S004 At least two spaces before inline comments required",
                Message.todo: "S005 TODO found",
                Message.two_blank: "S006 More than two blank lines used before this line"
                }
    errors = {}

    lines_with_message = {}

    def __init__(self):
        self.files = []

    def get_file_path(self):
        path = Arg().get_input_path_to_file()
        if os.path.isfile(path):
            self.files.append(os.path.basename(path))
        elif os.path.isdir(path):
            self.files = os.listdir(path)

    def is_file_belong_python(self):
        for file_name in self.files:
            if not re.search("\.py$", file_name):
                files.remove(file_name)
            else:
                files.replace(file_name, path + file_name)

    def validate_lines(self):
        for file_path in self.files:
            line_number = 1
            empty_lines = []
            with open(file_path, "r") as f:
                for line in f:
                    if self.is_line_empty_blanks(line, file_path):
                        empty_lines.append(line_number)
                    self.validate_length(line, line_number, file_path)
                    self.validate_indentation(line, line_number, file_path)
                    self.validate_semicolon(line, line_number, file_path)
                    self.validate_two_space_before_comments(line, line_number, file_path)
                    self.validate_is_todo(line, line_number, file_path)
                    self.validate_for_more_than_two_blanks(empty_lines, file_path)
                    line_number += 1
        return Status.ok

    def validate_length(self, line, number, file_path):
        chars_amount = 79
        if len(line) - 1 > chars_amount:
            self.add_new_error(file_path, Message.too_long, str(number))

    @staticmethod
    def find_last_space_index(line):
        space = " "
        for char in line:
            if char == space:
                continue
            else:
                return line.index(char) - 1

    def validate_indentation(self, line, number, file_path):
        regex = "^\s+."
        if re.match(regex, line):
            if len(line[:self.find_last_space_index(line) + 1]) % 4 != 0:
                self.add_new_error(file_path, Message.not_four, str(number))

    def validate_semicolon(self, line, number, file_path):
        comment_symbol = "#"
        semicolon = ";"
        if comment_symbol in line:
            line_tmp = line[:line.index(comment_symbol)]
        else:
            line_tmp = line
        if semicolon in line_tmp:
            if line_tmp.strip()[-1] == semicolon:
                self.add_new_error(file_path, Message.semicolon, str(number))

    def validate_two_space_before_comments(self, line, number, file_path):
        comment_symbol = "#"
        two_space = "  "
        if comment_symbol in line:
            if line.strip().startswith(comment_symbol):
                return
            tmp_line = line[:line.index(comment_symbol)]
            if not tmp_line.endswith(two_space):
                self.add_new_error(file_path, Message.two_space, str(number))

    def validate_is_todo(self, line, number, file_path):
        comment_symbol = "#"
        todo = "todo"
        if comment_symbol in line:
            tmp_line = line[line.index(comment_symbol):]
            if todo in tmp_line.lower():
                self.add_new_error(file_path, Message.todo, str(number))

    @staticmethod
    def is_line_empty_blanks(line):
        empty = "\n"
        if line == empty:
            return True
        return False

    def validate_for_more_than_two_blanks(self, numbers: list, file_path):
        if not numbers:
            return
        smaller_number = numbers[0]
        count = 0
        for number in numbers:
            if number - smaller_number == 1:
                count += 1
            if count > 2:
                self.add_new_error(file_path, Message.two_blank, str(number + 1))
            smaller_number = number

    def add_new_error(self, file_path, message, line_number: str):
        if file_path not in self.lines_with_message:
            self.lines_with_message[file_path] = []
        if line_number not in self.lines_with_message.get(file_path):
            self.lines_with_message[file_path][line_number] = []
        if message not in self.lines_with_message.get(file_path).get(line_number):
            self.lines_with_message[file_path][line_number].append(message)

    def get_error_messages(self):
        for file, lines in self.lines_with_message.values():
            numbers = [int(x) for x in lines.keys()].sort()
            [lines.get(str(number)).sort() for number in numbers]

            yield [f'{file}: Line {number}: {self.messages.get(message)}'
                   for number in numbers for message in self.lines_with_message.get(str(number))]


def main():
    analyzer = Analyzer()
    analyzer.validate_lines()
    while True:
        [print(x) for x in analyzer.get_error_messages()]


main()

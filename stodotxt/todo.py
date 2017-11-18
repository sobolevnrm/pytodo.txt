""" todo.txt container class """
from datetime import datetime
from operator import attrgetter
import re

DATE_FORMAT = "%Y-%m-%d"
MAIN_REGEX = re.compile("(^x)?\s*(\([A-Z]\))?\s*([0-9]{4}-[0-9]{2}-[0-9]{2})?\s*([0-9]{4}-[0-9]{2}-[0-9]{2})?\s*(.*)")
TAG_REGEX = re.compile("([\+\@]\S*)")
META_REGEX = re.compile("\s(\S*):(\S*)")
DUE_KEY = "due"
START_KEY = "t"


class Todo:
    """ A class for containing todo items """
    @staticmethod
    def sorted_todos(todo_list, keys, reverses=None):
        """ Sort an array of todos (return sorted array).  The keys parameter is an ordered list that determines what is
        sorted and the reverses parameter is a list (same length as keys) that determines the direction of sorting. If
        skipped, reverses defaults to False """
        if not reverses:
            reverses = [False] * len(keys)
        sorted_todos = todo_list
        for ikey, key in enumerate(keys):
            sorted_todos = sorted(sorted_todos, key=attrgetter(key), reverse=reverses[ikey])
        return sorted_todos

    def __init__(self, todo_str=None):
        """ Initialize a todo item with a specific string """
        self.completed = False
        self.priority = None
        self.completion_date = None
        self.creation_date = None
        self.description = None
        self.projects = set()
        self.contexts = set()
        self.due_date = None
        self.start_date = None
        if todo_str:
            self.parse_string(todo_str)

    def parse_completed(self, in_str):
        """ Parse completed status from string """
        if not in_str:
            self.completed = False
        elif in_str.lower() == "x":
            self.completed = True
        else:
            self.completed = False

    def parse_priority(self, in_str):
        """ Parse priority """
        if not in_str:
            self.priority = None
        else:
            self.priority = in_str[1].upper()

    def parse_completion_date(self, in_str):
        """ Parse completion date from string """
        if in_str:
            try:
                self.completion_date = datetime.strptime(in_str, DATE_FORMAT)
            except ValueError:
                self.completion_date = None
        else:
            self.completion_date = None

    def parse_creation_date(self, in_str):
        """ Parse creation date from string """
        if in_str:
            try:
                self.creation_date = datetime.strptime(in_str, DATE_FORMAT)
            except ValueError:
                self.creation_date = None
        else:
            self.creation_date = None

    def parse_tags(self, in_str):
        """ Parse the description field for tags. Return a string with tags removed. """
        self.projects = []
        self.contexts = []
        for match in TAG_REGEX.finditer(in_str):
            tag_str = match.group(1)
            if tag_str[0] == "+":
                self.projects.append(tag_str[1:])
            elif tag_str[0] == "@":
                self.contexts.append(tag_str[1:])
            else:
                err_str = "Unable to parse tag: %s" % tag_str
                raise ValueError(err_str)
        words = re.sub(TAG_REGEX, "", in_str).split()
        return " ".join(words)

    def parse_metadata(self, in_str):
        """ Parse the description field for metadata. Return a string with metadata removed. """
        for match in META_REGEX.finditer(in_str):
            key_str = match.group(1)
            val_str = match.group(2)
            if key_str == DUE_KEY:
                self.due_date = datetime.strptime(val_str, DATE_FORMAT)
            elif key_str == START_KEY:
                self.start_date = datetime.strptime(val_str, DATE_FORMAT)
            else:
                errstr = "Unknown metadata key (%s)" % key_str
                raise AttributeError(errstr)
        words = re.sub(META_REGEX, "", in_str).split()
        return " ".join(words)

    def parse_description(self, in_str):
        """ Parse the description field for the task, separating out tags and metadata """
        in_str = self.parse_tags(in_str)
        self.description = self.parse_metadata(in_str)

    def parse_string(self, in_str):
        """ Parse a string in todo.txt format and store in current todo object """
        match = MAIN_REGEX.search(in_str)
        if not match:
            err_str = "Unable to parse string: %s" % in_str
            raise ValueError(err_str)
        self.parse_completed(match.group(1))
        self.parse_priority(match.group(2))
        if match.group(3) and match.group(4):
            self.parse_completion_date(match.group(3))
            self.parse_creation_date(match.group(4))
        else:
            self.parse_creation_date(match.group(3))
        self.parse_description(match.group(5))

    def __repr__(self):
        words = []
        if self.completed:
            words.append("x")
        if self.priority:
            words.append("(%s)" % self.priority)
        if self.completion_date:
            words.append("%s %s" % (self.completion_date.strftime(DATE_FORMAT),
                                    self.creation_date.strftime(DATE_FORMAT)))
        elif self.creation_date:
            words.append(self.creation_date.strftime(DATE_FORMAT))
        words.append(self.description)
        words = words + ["+%s" % project for project in self.projects]
        words = words + ["@%s" % context for context in self.contexts]
        if self.due_date:
            words.append(DUE_KEY + ":" + self.due_date.strftime(DATE_FORMAT))
        if self.start_date:
            words.append(START_KEY + ":" + self.start_date.strftime(DATE_FORMAT))
        return " ".join(words)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

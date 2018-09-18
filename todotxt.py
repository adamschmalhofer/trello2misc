''' todotxt.py
Contains the TodotxtTask class plus methods related to todo.txt.
'''

import re
import datetime
import utils


# A todo.txt task contains the text entry, the priority, the project,
# the context, and the due date of the task.
class TodotxtTask:

    # The constructor.
    def __init__(self, entry, priority, project, context, due):
        self.entry = re.sub("^\\(\d+\\)\s+", "", entry).strip()
        self.priority = priority.strip()
        self.project = project.title().replace(" ", "").strip()
        self.context = context.replace(" ", "").lower().strip()
        self.due = due
        if len(self.due) > 0:
            try:
                input_format = ("%Y-%m-%dT%H:%M:%S.%fZ"
                                if "-" in self.due else "%dT%H:%M:%S.%fZ")
                self.due = datetime.datetime.strptime(self.due, input_format
                                                      ).strftime("%Y-%m-%d")
            except ValueError:
                self.due = ""

    # The one line string representation of a task.
    def __repr__(self):
        string = ""
        if len(self.priority) > 0:
            string += "(%s) " % (self.priority)
        string += "%s" % (self.entry)
        if len(self.project) > 0:
            string += " +%s" % (self.project)
        if len(self.context) > 0:
            string += " @%s" % (self.context)
        if len(self.due) > 0:
            string += " due:%s" % (self.due)
        return string

    # Two tasks are equal if the text entry is the same.
    # This enables other things, such as priorities and due dates,
    # to be updated.
    def __eq__(self, other):
        return self.entry == other.entry


# Returns a list of tasks read from the current todo.txt file.
def read_todotxtfile():
    config = utils.readconfig("trello2misc.ini")
    fileName = config.get("todotxt", "fileName")
    theFile = open(fileName, "r")
    lines = theFile.readlines()
    theFile.close()
    tasks = [parse_todotxtline(line) for line in lines]
    return tasks


# Returns a task object from a one line string representation.
def parse_todotxtline(line):
    entry_words = []
    priority = ""
    project = ""
    context = ""
    due = ""
    tokens = re.split(r'\s+', line)
    index = 0
    if (len(tokens[index]) == 3
            and tokens[index].startswith('(') and tokens[index].endswith(')')):
        priority = tokens[index][1:-1]
        index = 1
    for i in range(index, len(tokens)):
        token = tokens[i]
        if token.startswith('+'):
            project = token[1:]
        elif token.startswith('@'):
            context = token[1:]
        elif token.startswith('due:'):
            due = token[4:] + "T11:00:00.000Z"
        else:
            entry_words.append(token)
    entry = ' '.join(entry_words)
    task = TodotxtTask(entry, priority, project, context, due)
    return task


# Writes a list of tasks to the todo.txt file.
def write_tasks(tasks):
    config = utils.readconfig("trello2misc.ini")
    fileName = config.get("todotxt", "fileName")
    theFile = open(fileName, "w")
    for task in tasks:
        theFile.write(repr(task) + "\n")
    theFile.close()

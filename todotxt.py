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
    def __init__(self, entry, priority, project, context, due, as_str=None):
        self.entry = re.sub("^\\(\d+\\)\s+", "", entry).strip()
        self.priority = priority.strip()
        self.project = [p.replace(" ", "").strip() for p in project]
        self.context = [c.replace(" ", "").lower().strip() for c in context]
        self.due = due
        if len(self.due) > 0:
            try:
                input_format = ("%Y-%m-%dT%H:%M:%S.%fZ"
                                if "-" in self.due else "%dT%H:%M:%S.%fZ")
                self.due = datetime.datetime.strptime(self.due, input_format
                                                      ).strftime("%Y-%m-%d")
            except ValueError:
                self.due = ""
        self.as_str=as_str

    # The one line string representation of a task.
    def __repr__(self):
        if self.as_str is not None:
            return self.as_str
        priority = ("(%s) " % (self.priority)
                    if len(self.priority) > 0 else "")
        projects = [" +%s" % p for p in self.project]
        contexts = [" @%s" % c for c in self.context]
        due = " due:%s" % (self.due) if len(self.due) > 0 else ""
        string = ''.join([priority, self.entry, *projects, *contexts, due])
        return string

    # Two tasks are equal if the text entry is the same.
    # This enables other things, such as priorities and due dates,
    # to be updated.
    def __eq__(self, other):
        return self.entry == other.entry

    def update(self, priority, due):
        self.as_str = None
        self.priority = priority
        self.due = due


# Returns a list of tasks read from the current todo.txt file.
def read_todotxtfile():
    config = utils.readconfig("trello2misc.ini")
    fileName = config.get("todotxt", "fileName")
    with open(fileName, "r") as theFile:
        lines = theFile.readlines()
    tasks = [parse_todotxtline(line) for line in lines]
    return tasks


# Returns a task object from a one line string representation.
def parse_todotxtline(line):
    entry_words = []
    priority = ""
    project = []
    context = []
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
            project.append(token[1:])
        elif token.startswith('@'):
            context.append(token[1:])
        elif token.startswith('due:'):
            due = token[4:] + "T11:00:00.000Z"
        else:
            entry_words.append(token)
    entry = ' '.join(entry_words)
    task = TodotxtTask(entry, priority, project, context, due, line)
    return task


# Writes a list of tasks to the todo.txt file.
def write_tasks(tasks):
    config = utils.readconfig("trello2misc.ini")
    fileName = config.get("todotxt", "fileName")
    with open(fileName, "w") as theFile:
        for task in tasks:
            theFile.write(repr(task) + "\n")

#!/usr/bin/python3

"""trello2misc.py
Pulls your cards from Trello to your console or your local todo.txt-file.
Broadly speaking, one card corresponds to one entry. Boards correspond to
contexts, lists to priorities, and labels to projects. See the README.md and
trello2misc.ini files for more information.

Author: André Bergholz
Version: 1.0
"""

import string
import sys
import configparser
import datetime
import trello
import todotxt
import utils

__version__ = "1.0"
__date__ = "2013/02/28"
__updated__ = "2014/08/15"
__author__ = "André Bergholz (bergholz@gmail.com)"
__license__ = "GPL3"


# Returns the list of todo.txt tasks generated from
# the information contained in the Trello cards.
def generate_todotxttasks(cards, lists, boards, allCardsBoardNames):
    tasks = []
    priority_dict = listname_to_priority_dict()
    for card in cards.values():
        if not card.closed and card.board in boards:
            priority = generate_priority(card, lists, priority_dict)
            label = card.labels
            context = ("trello"
                       if boards[card.board].name in allCardsBoardNames
                       else boards[card.board].name)
            due = (card.due if card.due is not None else "")
            task = todotxt.TodotxtTask(card.name, priority, label, [context],
                                       due)
            tasks.append(task)
    return tasks


def listname_to_priority_dict():
    config = utils.readconfig("trello2misc.ini")
    ret = {}
    for priority in string.ascii_uppercase[:26]:
        config_key = "%sLists" % priority.lower()
        try:
            lists = config.get("trello", config_key)
        except configparser.NoOptionError:
            break
        ret.update({name.replace("\"", "").strip(): priority
                   for name in lists.split(",")})
    return ret


# Returns a priority for a given Trello card
def generate_priority(card, lists, priority_dict):
    listName = lists[card.list]
    priority = ""
    try:
        priority = priority_dict[listName]
    except KeyError:
        pass
    return priority


# Returns a list of merged todo.txt tasks
# from the base tasks (which existed previously)
# and the newly generated tasks from the Trello cards.
# For base tasks, priority and due date are updated.
def merge_tasks(newTasks, baseTasks):
    tasks = baseTasks
    for task in newTasks:
        try:
            index = tasks.index(task)
        except ValueError:
            tasks.append(task)
        else:
            tasks[index].update(task.priority, task.due)
    return tasks


# Prints the current card dictionary to screen.
def print_oneliner(cards, lists):
    for card in cards:
        due = (" " + datetime.datetime.strptime(card.due,
                                                "%Y-%m-%dT%H:%M:%S.%fZ"
                                                ).strftime("%Y-%m-%d")
               if card.due is not None
               else "")
        labels = (" (%s)" % " ".join(card.labels[0:2])
                  if len(card.labels) > 0
                  else "")
        string = "%s%s%s: %s" % (lists[card.list], due, labels, card.name)
        print(string)


def load_from_trello():
    config = utils.readconfig("trello2misc.ini")
    allCardsBoards = config.get("trello", "allCardsBoards")
    myCardsBoards = config.get("trello", "myCardsBoards")
    allCardsBoardNames = [name.replace("\"", "").strip()
                          for name in allCardsBoards.split(",")]
    myCardsBoardNames = [name.replace("\"", "").strip()
                         for name in myCardsBoards.split(",")]
    boardNames = allCardsBoardNames + myCardsBoardNames
    boards = trello.read_my_trello_boards()
    boards = trello.filter_trello_boards(boardNames, boards)
    lists = trello.read_trello_lists(boards)
    cards = trello.read_all_trello_cards(allCardsBoardNames, boards)
    cards.update(trello.read_my_trello_cards(myCardsBoardNames, boards))
    cards = trello.filter_cards(cards, lists)
    return {'cards': cards, 'lists': lists, 'boards': boards,
            'allCardsBoardNames': allCardsBoardNames}


def format_as_todotxt(cards, lists, boards, allCardsBoardNames):
    todotxtTasks = todotxt.read_todotxtfile()
    trelloTasks = generate_todotxttasks(cards, lists, boards,
                                        allCardsBoardNames)
    tasks = merge_tasks(trelloTasks, todotxtTasks)
    todotxt.write_tasks(tasks)


def format_as_txt(cards, lists, **rest):
    sortedCards = trello.sort_cards(cards, lists)
    print_oneliner(sortedCards, lists)


# The main method processes the given command.
def main(command):
    if command == "todotxt":
        format_as_todotxt(**load_from_trello())
    elif command == "stdout":
        format_as_txt(**load_from_trello())
    else:
        if command not in ["help", "usage"]:
            print("Unsupported command: " + command)
        print("Usage: ./trello2misc.py [stdout|todotxt|help]?")


# The main program.
if __name__ == '__main__':
    command = (sys.argv[1].lower().strip() if len(sys.argv) >= 2 else "help")
    main(command)

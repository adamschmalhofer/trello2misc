#!/usr/bin/python3

"""trello2misc.py
Pulls your cards from Trello to your console or your local todo.txt-file.
Broadly speaking, one card corresponds to one entry. Boards correspond to
contexts, lists to priorities, and labels to projects. See the README.md and
trello2misc.ini files for more information.

Author: André Bergholz
Version: 1.0
"""

import sys
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
    for card in cards.values():
        if not card.closed and card.board in boards:
            priority = generate_priority(card, lists)
            label = ""
            if len(card.labels) > 0:
                label = card.labels[0]
            if boards[card.board].name in allCardsBoardNames:
                context = "trello"
            else:
                context = boards[card.board].name
            if card.due is None:
                due = ""
            else:
                due = card.due
            task = todotxt.TodotxtTask(card.name, priority, label, context,
                                       due)
            tasks.append(task)
    return tasks


# Returns a priority for a given Trello card
def generate_priority(card, lists):
    config = utils.readconfig("trello2misc.ini")
    aLists = config.get("trello", "aLists")
    bLists = config.get("trello", "bLists")
    cLists = config.get("trello", "cLists")
    aList = []
    bList = []
    cList = []
    for name in aLists.split(","):
        aList.append(name.replace("\"", "").strip())
    for name in bLists.split(","):
        bList.append(name.replace("\"", "").strip())
    for name in cLists.split(","):
        cList.append(name.replace("\"", "").strip())
    listName = lists[card.list]
    if listName in aList:
        priority = "A"
    elif listName in bList:
        priority = "B"
    elif listName in cList:
        priority = "C"
    else:
        priority = ""
    return priority


# Returns a list of merged todo.txt tasks
# from the base tasks (which existed previously)
# and the newly generated tasks from the Trello cards.
# For base tasks, priority and due date are updated.
def merge_tasks(newTasks, baseTasks):
    tasks = baseTasks
    for task in newTasks:
        if task in tasks:
            index = tasks.index(task)
            tasks[index].priority = task.priority
            tasks[index].due = task.due
        else:
            tasks.append(task)
    return tasks


# Prints the current card dictionary to screen.
def print_oneliner(cards, lists):
    for card in cards:
        string = "%s" % (lists[card.list])
        if card.due is not None:
            stripped = datetime.datetime.strptime(card.due,
                                                  "%Y-%m-%dT%H:%M:%S.%fZ"
                                                  ).strftime("%Y-%m-%d")
            string += " %s" % (stripped)
        string += ": %s" % (card.name)
        if len(card.labels) > 0:
            string += " ("
            for label in card.labels[0:2]:
                string += "%s " % (label)
            string = string.strip()
            string += ")"
        print(string)


def format_as_todotxt():
    config = utils.readconfig("trello2misc.ini")
    todotxtTasks = todotxt.read_todotxtfile()
    allCardsBoards = config.get("trello", "allCardsBoards")
    myCardsBoards = config.get("trello", "myCardsBoards")
    allCardsBoardNames = []
    myCardsBoardNames = []
    for name in allCardsBoards.split(","):
        allCardsBoardNames.append(name.replace("\"", "").strip())
    for name in myCardsBoards.split(","):
        myCardsBoardNames.append(name.replace("\"", "").strip())
    boardNames = allCardsBoardNames + myCardsBoardNames
    boards = trello.read_my_trello_boards()
    boards = trello.filter_trello_boards(boardNames, boards)
    lists = trello.read_trello_lists(boards)
    cards = trello.read_all_trello_cards(allCardsBoardNames, boards)
    cards.update(trello.read_my_trello_cards(myCardsBoardNames, boards))
    cards = trello.filter_cards(cards, lists)
    trelloTasks = generate_todotxttasks(cards, lists, boards,
                                        allCardsBoardNames)
    tasks = merge_tasks(trelloTasks, todotxtTasks)
    todotxt.write_tasks(tasks)


def format_as_txt():
    config = utils.readconfig("trello2misc.ini")
    allCardsBoards = config.get("trello", "allCardsBoards")
    myCardsBoards = config.get("trello", "myCardsBoards")
    allCardsBoardNames = []
    myCardsBoardNames = []
    for name in allCardsBoards.split(","):
        allCardsBoardNames.append(name.replace("\"", "").strip())
    for name in myCardsBoards.split(","):
        myCardsBoardNames.append(name.replace("\"", "").strip())
    boardNames = allCardsBoardNames + myCardsBoardNames
    boards = trello.read_my_trello_boards()
    boards = trello.filter_trello_boards(boardNames, boards)
    lists = trello.read_trello_lists(boards)
    cards = trello.read_all_trello_cards(allCardsBoardNames, boards)
    cards.update(trello.read_my_trello_cards(myCardsBoardNames, boards))
    cards = trello.filter_cards(cards, lists)
    sortedCards = trello.sort_cards(cards, lists)
    print_oneliner(sortedCards, lists)


# The main method processes the given command.
def main(command):
    if command == "todotxt":
        format_as_todotxt()
    elif command == "stdout":
        format_as_txt()
    elif command == "help" or command == "usage":
        print("Usage: ./trello2misc.py [stdout|todotxt|help]?")
    else:
        print("Unsupported command: " + command)
        print("Usage: ./trello2misc.py [stdout|todotxt|help]?")


# The main program.
if __name__ == '__main__':
    if (len(sys.argv) < 2):
        command = "help"
    else:
        command = sys.argv[1].lower().strip()
    main(command)

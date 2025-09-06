import os,sqlite3;
from rich.console import Console;
console = Console()
from langs import manager;

class reg:
    def __init__(self):
        self.campos = ['id',"service",'password']
        pass

def help():
    console.print(manager.getWord("header"), justify="center")
    console.print(manager.getHelpMenu(3))
def add():
    return
help()

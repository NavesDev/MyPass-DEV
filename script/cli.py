import os,sqlite3,cryptography, typer,rich,math;
from typing_extensions import Annotated;
from typing import Optional;
from rich.console import Console;
from rich.table import Table;
console = Console()
from script.langs import manager;
os.makedirs("data",exist_ok=True)
database = sqlite3.connect("data/user.db")
cursor = database.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")
cursor.execute("""
CREATE TABLE IF NOT EXISTS Accounts(
    id integer primary key AUTOINCREMENT,            
    email text,
    name text default '<unknown>'
);

""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS Services(
    id integer primary key AUTOINCREMENT,
    accountId integer not null ,           
    service text default '<default-service>',
    password text not null,
    FOREIGN KEY (accountId) REFERENCES Accounts(id)
);
""")

database.commit()
database.close()

app = typer.Typer(help = manager.getWord('header'))
add_app = typer.Typer(help = "ADD METHOD")
list_app = typer.Typer(help = "LIST METHOD")
edit_app = typer.Typer(help = "EDIT METHOD")
app.add_typer(add_app,name='add')
app.add_typer(list_app,name='list')
app.add_typer(edit_app,name='edit')

@app.callback()
def main(
    ajuda: Annotated[
        Optional[bool],
        typer.Option(
            "--help", "-h",
            help="Mostra este manual de ajuda super personalizado e sai.",
           
            callback=lambda valor: manager.getHelpMenu() if valor else None,
            is_eager=True 
        )
    ] = None,
):
    pass


@app.command()
def help(
    page:Annotated[int,typer.Option("--page",'-p')] = 1
):
    console.print(manager.getWord("header"), justify="center")
    console.print(manager.getHelpMenu(page))

@app.command()
def version():
    console.print(manager.getWord("header"))

@add_app.command()
def account(
    name:Annotated[str,typer.Argument(help=manager.getWord("cmd_desc_add_account"))],
    email:Annotated[Optional[str],typer.Option("--email","-e", help=manager.getWord("cmd_desc_add_account_email"))] = None
):    
    try:
        database = sqlite3.connect("data/user.db")
        cursor = database.cursor()
        cursor.execute("SELECT id FROM Accounts WHERE name=?",(name,))
        valid = cursor.fetchall()
        if(len(valid)>0):
            choose = ''
            while choose!='n' and choose!='y':
                console.print(manager.getWord('double_account'))
                choose = input().strip()
                choose = choose.lower()
            if(choose=='n'):
                return
        cursor.execute("INSERT INTO Accounts(email,name) VALUES(?,?)",(email,name))
        message = manager.getWord("success_account_create").format(account=name,email=email or manager.getWord("no_email"))
        console.print(message,highlight=False)
        
    except Exception as ex:
        print(ex)
        console.print(manager.getWord("error_general"))
    finally:
        if(database):
            database.commit()
            database.close()
    
@list_app.command()
def account(
    page : Annotated[
        Optional[int],
        typer.Option('--page','-p',help='')
        ] = 1,
    
):    
    
    try:
        database = sqlite3.connect("data/user.db")
        cursor = database.cursor()
        cursor.execute("SELECT Count(*) FROM Accounts")
        count = cursor.fetchall()[0][0]
        maxpage = math.ceil(count/10) if count>0 else 0
        
        if((page>maxpage and maxpage>0) or page<=0):
            message = manager.getWord("error_no_page")
            message = message.format(max_page=maxpage)
            console.print(message)
            return
        elif(maxpage==0):
            console.print(manager.getWord("error_no_account_listed"),highlight=False)
            return
        cursor.execute("SELECT id,name,email FROM Accounts ORDER BY id LIMIT ? OFFSET ?",(10,(page-1)*10 ))
        data = cursor.fetchall()
        
        output = Table(
            title=f"Lista de contas - Página {page} ... 1",
            box=rich.box.ROUNDED,
            header_style="bold bright_blue", 
            row_styles=["none"],
            caption="Use 'mypass add' para adicionar novas contas.",
            show_lines=True,
            padding=(0,3))
        output.add_column(manager.getWord("id_word").upper(), style="dim", width=6, justify="center")
        output.add_column(manager.getWord("name_word").upper(), style="white")
        output.add_column(manager.getWord("email_word").upper(), style="white")
        for line in data:
            output.add_row(str(line[0]),str(line[1]),str(line[2]))
        console.print(output,highlight=False) 
    except Exception as ex:
        print(ex)
        console.print(manager.getWord("error_general"))
    finally:
        if(database):
            database.commit()
            database.close()

@edit_app.command()
def account(
    ID_OR_NAME:Annotated[str,typer.Argument(help=manager.getWord("cmd_desc_edit_account_idname"))],
    name:Annotated[Optional[str],typer.Option("--name","-n", help=manager.getWord("cmd_desc_edit_account_name"))] = None,
    email:Annotated[Optional[str],typer.Option("--email","-e", help=manager.getWord("cmd_desc_edit_account_email"))] = None
):    
    try:
        database = sqlite3.connect("data/user.db")
        cursor = database.cursor()
        cursor.execute("SELECT id FROM Accounts WHERE name=?",(name,))
        valid = cursor.fetchall()
        if(len(valid)>0):
            choose = ''
            while choose!='n' and choose!='y':
                console.print(manager.getWord('double_account'))
                choose = input().strip()
                choose = choose.lower()
            if(choose=='n'):
                return
        cursor.execute("INSERT INTO Accounts(email,name) VALUES(?,?)",(email,name))
        message = manager.getWord("success_account_create").format(account=name,email=email or manager.getWord("no_email"))
        console.print(message,highlight=False)
        
    except Exception as ex:
        print(ex)
        console.print(manager.getWord("error_general"))
    finally:
        if(database):
            database.commit()
            database.close()
    
if __name__ == "__main__":
    app()
   


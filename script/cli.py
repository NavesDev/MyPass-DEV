import os,sqlite3,cryptography, typer,rich,math;
from typing_extensions import Annotated;
from typing import Optional;
from rich.console import Console;
from rich.table import Table;
console = Console()
from script.langs import manager;
from script.funcs import db,forceInput;


app = typer.Typer(help = manager.getWord('header'))
add_app = typer.Typer(help = "ADD METHOD")
list_app = typer.Typer(help = "LIST METHOD")
edit_app = typer.Typer(help = "EDIT METHOD")
app.add_typer(add_app,name='add')
app.add_typer(list_app,name='list')
app.add_typer(edit_app,name='edit')

@app.command()
def version():
    console.print(manager.getWord("header"))

# ROTA PARA ADICIONAR NOVA CONTA NO SISTEMA
@add_app.command()
def account(
    name:Annotated[str,typer.Argument(help=manager.getWord("cmd_desc_add_account"))],
    email:Annotated[Optional[str],typer.Option("--email","-e", help=manager.getWord("cmd_desc_add_account_email"))] = None
):    
    try:
        db.load()
        cursor = db.database.cursor()
        cursor.execute("SELECT id FROM Accounts WHERE name=?",(name,))
        valid = cursor.fetchall()
        if(len(valid)>0):
            choose = forceInput(manager.getWord('double_account'),['n','y'])
            if(choose=='n'):
                return
        cursor.execute("INSERT INTO Accounts(email,name) VALUES(?,?)",(email,name))
  
        message = manager.getWord("success_account_create").format(account=name,email=email or manager.getWord("no_email"))
        console.print(message,highlight=False)
        
    except Exception as ex:
        print(ex)
        console.print(manager.getWord("error_general"))
    finally:
        cursor.close()
        db.close()

# ROTA PARA LISTAR AS CONTAS DO SISTEMA
@list_app.command()
def account(
    page : Annotated[
        Optional[int],
        typer.Option('--page','-p',help=manager.getWord("cmd_desc_edit_account_page"))
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
            output.add_row(str(line[0]),str(line[1]),str(line[2] if line[2] else manager.getWord("notFoundEmail")))
        console.print(output,highlight=False) 
    except Exception as ex:
        print(ex)
        console.print(manager.getWord("error_general"))
    finally:
        if(database):
            database.commit()
            database.close()

# COMANDO PARA EDITAR CONTAS DO SISTEMA
@edit_app.command()
def account(
    identifier:Annotated[str,typer.Argument(help=manager.getWord("cmd_desc_edit_account_idname"))],
    name:Annotated[Optional[str],typer.Option("--name","-n", help=manager.getWord("cmd_desc_edit_account_name"))] = None,
    email:Annotated[Optional[str],typer.Option("--email","-e", help=manager.getWord("cmd_desc_edit_account_email"))] = None
):    
    cursor = None
    # EDITAR ISSO DEPOIS
    if(not email and not name):
         console.print(manager.getWord("error_no_edit_data"),highlight=False)
         return
    try:
        # database = sqlite3.connect("data/user.db")
        # cursor = database.cursor()
        # cursor.execute("SELECT id,name,email FROM Accounts WHERE id=? or name=? or email=? ORDER BY CASE WHEN id=? THEN 1 WHEN name=? THEN 2 WHEN email=? THEN 3 END; ",
        # (identifier,identifier,identifier,identifier,identifier,identifier))
        # valid = cursor.fetchall()
        selected = db.search("SELECT id,name,email FROM Accounts WHERE id=? or name=? or email=? ORDER BY CASE WHEN id=? THEN 1 WHEN name=? THEN 2 WHEN email=? THEN 3 END; ",
                  (identifier,identifier,identifier,identifier,identifier,identifier),identifier)
        if(db):
        
            newlist = list(selected)
            edits = {}
        
            newlist[1] = name if name else newlist[1]
            newlist[2] = email if email else newlist[2]
            word = manager.getWord("generic_edit_quest").format(
                last_data=f"({', '.join([str(i) for i in selected])})",
                new_data = f"({', '.join([str(i) for i in newlist])})"
            )
          
            choose = forceInput(word,['y','n'])
            if(choose == 'y'):
                cursor = db.database.cursor()
                cursor.execute(f'UPDATE Accounts SET name = ? , email = ? WHERE id = ?',(newlist[1],newlist[2],newlist[0]))
                word = manager.getWord("success_edit")
                console.print(word)
                
    except Exception as ex:
        console.print(manager.getWord("error_general"))
        raise ex
    finally:
        if(cursor):
            cursor.close()
        db.close()
    
    
if __name__ == "__main__":
    app()
   


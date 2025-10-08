import os,sqlite3,cryptography, typer,rich,math;
from typing_extensions import Annotated;
from typing import Optional;
from rich.console import Console;
from rich.table import Table;

console = Console()
from script.langs import manager;
from script.funcs import db,Secret,forceInput,FIRules;
from script.configs import Configs,SecureData

# PRÓPRIO TRATAMENTO DE ERRORS

class DataNotFoundError(Exception):
    pass
class IncorrectMasterPassword(Exception):
    pass

app = typer.Typer(help = manager.getWord('header'))
add_app = typer.Typer(help = "ADD METHOD")
list_app = typer.Typer(help = "LIST METHOD")
edit_app = typer.Typer(help = "EDIT METHOD")
configure_app = typer.Typer(help="CONFIFURE METHOD")
delete_app = typer.Typer(help= "DELETE METHOD")
app.add_typer(add_app,name='add')
app.add_typer(list_app,name='list')
app.add_typer(edit_app,name='edit')
app.add_typer(configure_app,name="configure")
app.add_typer(delete_app,name="delete")


# FUNÇÕES DE USO NOS COMANDOS

## FUNÇÃO PARA VALIDADAR
def getSelectedAccount(throwEx = False):
    cursor = None
    open_database = None
    try:       
        data = db.execute("SELECT id,name,email FROM Accounts WHERE id = ?",(Configs.selected_account,))

        if (len(data)==0 and throwEx):
            raise DataNotFoundError("Don't found selected account")
        elif (len(data)==0):
            return None
        elif(len(data)==1):
            return data[0]

    except Exception as ex:
        if(throwEx):
            raise ex
        
def inputMasterPassword():
    return forceInput(manager.getWord("get_master_password"),rule=FIRules.filter_word,min_len=4,max_len=8,input_type="password")  

def pinCheck(master_password):
    return Secret.decrypt(master_password,SecureData.encriptedModel)
## FUNÇÃO PARA CRIPTOGRAFAR TODAS AS SENHAS PARA QUANDO POR EXEMPLO, USUÁRIO ATIVAR CRIPTOGRAFIA
def encryptAllPass(master_key):
    database = db.load()
    cursor = database.cursor()
    cursor.execute("SELECT id,service,password FROM Services WHERE password IS NOT NULL")
    services = cursor.fetchall()

    for item in services:
        new_password = Secret.encrypt(master_key, item[2])
        cursor.execute("UPDATE Services SET password = ? WHERE id = ?",(new_password,item[0]))
    cursor.close()
    db.close()

## FUNÇÃO PARA DESCRIPTOGRAFAR TODAS AS SENHAS PARA QUANDO POR EXEMPLO, USUÁRIO DESATIVAR CRIPTOGRAFIA
def dencryptAllPass(master_key):
    database = db.load()
    cursor = database.cursor()
    cursor.execute("SELECT id,service,password FROM Services WHERE password IS NOT NULL")
    services = cursor.fetchall()

    for item in services:
        new_password = Secret.decrypt(master_key, item[2])
        if(new_password):
            cursor.execute("UPDATE Services SET password = ? WHERE id = ?",(new_password,item[0]))
        else:
            raise IncorrectMasterPassword()
    cursor.close()
    db.close()

# FUNÇÕES COMANDOS
@app.command()
def version():
    console.print(manager.getWord("header"))

## ROTA PARA SELECIONAR CONTA
@app.command()
def select(
    identifier:Annotated[str,typer.Argument(help=manager.getWord("cmd_desc_edit_account_idname"))]
):
    try:
        selected = db.search("SELECT id,name,email FROM Accounts WHERE id=? or name=? or email=? ORDER BY CASE WHEN id=? THEN 1 WHEN name=? THEN 2 WHEN email=? THEN 3 END; ",
                  (identifier,identifier,identifier,identifier,identifier,identifier),identifier)
        if(selected):
            Configs.massUpdate(selected_account = selected[0])
            word = manager.getWord("success_context_set").format(account=selected[1])
            console.print(word,highlight=False)
    except Exception:
        console.print(manager.getWord("error_general"))
    finally:
        db.close()   
        
## ROTA PARA ADICIONAR NOVA CONTA NO SISTEMA
@add_app.command()
def account(
    name:Annotated[str,typer.Argument(help=manager.getWord("cmd_desc_add_account"))],
    email:Annotated[Optional[str],typer.Option("--email","-e", help=manager.getWord("cmd_desc_add_account_email"))] = None
):    
    cursor = None
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
        if(cursor):
            cursor.close()
        db.close()

## ROTA PARA ADICIONAR NOVOS SERVIÇOS
@add_app.command()
def service(
    service:Annotated[str,typer.Argument(help=manager.getWord("cmd_desc_add_service_name"))],
    password:Annotated[Optional[str],typer.Option("--password","-p",help=manager.getWord("cmd_desc_add_service_pass"))]=None,
    master_password:Annotated[Optional[str],typer.Option("--pin","-sp",help=manager.getWord("cmd_desc_pin"))]=None
):
    cursor = None
    try:
        selected = getSelectedAccount(True)
        
        if(not password):
            password = forceInput(manager.getWord("add_service_password_request"),rule=FIRules.filter_word,min_len=1,inputType='password')
        if(SecureData.securityLevel == 1):
            if not master_password:
                master_password = inputMasterPassword()        
            if(not pinCheck(master_password)):
                return
            password = Secret.encrypt(master_password,password)
        database = db.load()
        cursor = database.cursor()
        cursor.execute("INSERT INTO Services(accountId,service,password) VALUES(?,?,?)",(
            selected[0], # ID DA CONTA SELECIONADA
            service, # NOME DO NOVO SERVIÇO
            password # SENHA DO NOVO SERVIÇO
            ))
    except DataNotFoundError:
        console.print(manager.getWord("error_no_context"))
        return
    except Exception as ex:
        raise ex
        console.print(manager.getWord("error_general"))
    finally:
        db.close()

# ROTA PARA DELETAR CONTAS
@delete_app.command()
def account(
    identifier:Annotated[str,typer.Argument(help=manager.getWord("cmd_desc_edit_account_idname"))]
):
    try:
    
        selected = db.search("SELECT id,name,email FROM Accounts WHERE id=? or name=? or email=? ORDER BY CASE WHEN id=? THEN 1 WHEN name=? THEN 2 WHEN email=? THEN 3 END; ",
                  (identifier,identifier,identifier,identifier,identifier,identifier),identifier)
        db.execute("DELETE FROM Accounts WHERE id = ?",(selected[0],))
        db.execute("DELETE FROM Services WHERE id = ?",(selected[0],))
        
    except:
        console.print(manager.getWord("error_general"))

@delete_app.command()
def service(
    identifier:Annotated[str,typer.Argument(help=manager.getWord("cmd_desc_edit_account_idname"))]
):
    try:
        
        account = getSelectedAccount(True)
        selected = db.search("SELECT id,service FROM Services WHERE accountId = ? and id=? or service=? ORDER BY CASE WHEN id=? THEN 1 WHEN service=? THEN 2 END; ",
                  (account[0],identifier,identifier,identifier,identifier),identifier)
        
        db.execute("DELETE FROM Services WHERE id = ?",(selected[0],))
        print('deletado com sucesso')
        db.close()
    except DataNotFoundError:
        console.print(manager.getWord("error_no_context"))
    except Exception as ex:
       
        console.print(manager.getWord("error_general"))
    
## ROTA PARA LISTAR AS CONTAS O SISTEMA
@list_app.command()
def accounts(
    page : Annotated[
        Optional[int],
        typer.Option('--page','-p',help=manager.getWord("cmd_desc_edit_account_page"))
        ] = 1,
    
):    
    database = None
    cursor = None
    try:
        database = db.load()
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

@list_app.command()
def services(
    page : Annotated[
        Optional[int],
        typer.Option('--page','-p',help=manager.getWord("cmd_desc_edit_account_page"))
        ] = 1,
    reveal : Annotated[
        bool,
        typer.Option("--reveal","-r")
    ] = False
):    
    database = None
    cursor = None
    try: 
        selected_account = getSelectedAccount(True)
    except DataNotFoundError:
        console.print(manager.getWord("error_no_context"))
        return 
    try:
        database = db.load()
        cursor = database.cursor()
        cursor.execute("SELECT Count(*) FROM Services")
        count = cursor.fetchall()[0][0]
        maxpage = math.ceil(count/10) if count>0 else 0
        
        if((page>maxpage and maxpage>0) or page<=0):
            message = manager.getWord("error_no_page")
            message = message.format(max_page=maxpage)
            console.print(message)
            return
        elif(maxpage==0):
            console.print(manager.getWord("error_no_service_listed"),highlight=False)
            return
        
        output_data = []
        query_params = (selected_account[0], 10,(page-1)*10)
        if(not reveal):
            cursor.execute("SELECT id,service FROM Services  WHERE accountId = ? ORDER BY id LIMIT ? OFFSET ?",query_params)
            data = cursor.fetchall()
            output_data = data
        else:
            if(SecureData.securityLevel == 1):
                master_password = inputMasterPassword()
                cursor.execute("SELECT id,service,password FROM Services WHERE accountId = ? ORDER BY id LIMIT ? OFFSET ?",query_params)
                data = cursor.fetchall()
                for i in data:
                    new_data = list(i)
                    decrypted_key = Secret.decrypt(master_password,new_data[2])
                    if(not decrypted_key):
                        return
                    new_data[2] = decrypted_key
                    output_data.append(new_data)
            else:
                cursor.execute("SELECT id,service,password FROM Services WHERE accountId = ? ORDER BY  id LIMIT ? OFFSET ?",query_params)
                data = cursor.fetchall()
                output_data = data
        output = Table(
            title=f"Lista de contas - Página {page} ... 1",
            box=rich.box.ROUNDED,
            header_style="bold bright_blue", 
            row_styles=["none"],
            caption="Use 'mypass add' para adicionar novas contas.",
            show_lines=True,
            padding=(0,3))
        output.add_column(manager.getWord("id_word").upper(), style="dim", width=6, justify="center")
        output.add_column(manager.getWord("service_word").upper(), style="white",justify="center")
        output.add_column(manager.getWord("password_word").upper(), style="white",justify="center")
        for line in output_data:
            output.add_row(str(line[0]),str(line[1]if len(line)>1 and line[1] else "Unknown"),str(line[2] if len(line)>2 and line[2] else Configs.password_mask))
        console.print(output,highlight=False) 

    except Exception as ex:
        raise ex
        console.print(manager.getWord("error_general"))
    finally:
        if(database):
            database.commit()
            database.close()

## COMANDO PARA EDITAR CONTAS DO SISTEMA
@edit_app.command()
def account(
    identifier:Annotated[str,typer.Argument(help=manager.getWord("cmd_desc_edit_account_idname"))],
    name:Annotated[Optional[str],typer.Option("--name","-n", help=manager.getWord("cmd_desc_edit_account_name"))] = None,
    email:Annotated[Optional[str],typer.Option("--email","-e", help=manager.getWord("cmd_desc_edit_account_email"))] = None
):    
    cursor = None

    if(not email and not name):
         console.print(manager.getWord("error_no_edit_data"),highlight=False)
         return
    try:
        selected = db.search("SELECT id,name,email FROM Accounts WHERE id=? or name=? or email=? ORDER BY CASE WHEN id=? THEN 1 WHEN name=? THEN 2 WHEN email=? THEN 3 END; ",
                  (identifier,identifier,identifier,identifier,identifier,identifier),identifier)
        if(selected):
            new_list = list(selected)
            edits = {}
            new_list[1] = name if name else new_list[1]
            new_list[2] = email if email else new_list[2]
            word = manager.getWord("generic_edit_quest").format(
                last_data=f"({', '.join([str(i) for i in selected])})",
                new_data = f"({', '.join([str(i) for i in new_list])})"
            )
          
            choose = forceInput(word,['y','n'])
            if(choose == 'y'):
                cursor = db.database.cursor()
                cursor.execute(f'UPDATE Accounts SET name = ? , email = ? WHERE id = ?',(new_list[1],new_list[2],new_list[0]))
                word = manager.getWord("success_edit")
                console.print(word)
                
    except Exception as ex:
        console.print(manager.getWord("error_general"))
        raise ex
    finally:
        if(cursor):
            cursor.close()
        db.close()

## ROTA PARA TROCA DE LINGUAGEM DO SISTEMA
@configure_app.command()
def lang(
    lang:Annotated[str,typer.Argument(help=manager.getWord("cmd_desc_lang"))],
):
    langs,message = manager.listLangs()
    if(lang in langs):
        manager.changeLang(lang)
        console.print(manager.getWord("success_edit"))
    else:
        console.print(manager.getWord("invalid_lang"),highlight=False)
        console.print(message)

@configure_app.command()
def security(
    level:Annotated[Optional[str],typer.Option("--level","-l", help=manager.getWord("cmd_desc_edit_account_email"))] = None,
):
    levels = (0,1)
    last_level = SecureData.securityLevel
    if(not level or level not in levels):
        
        level = int(forceInput(manager.getWord("sec_level_message"),[str(level) for level in levels]))
    
    if(last_level!=level):
        try:
            if(level==1):
                master_password = ""
                confirm_password = "n"
                while master_password!=confirm_password:
                    master_password = forceInput(manager.getWord("new_master_password"),rule=FIRules.filter_word,min_len=4,max_len=8,input_type="password")
                    confirm_password= forceInput(manager.getWord("confirm_master_password"),rule=FIRules.filter_word,min_len=4,max_len=8,input_type="password")
                    if(master_password!=confirm_password):
                        console.print(manager.getWord("unmatch_passwords"))
                choose = forceInput(manager.getWord("generic_edit_quest2"),('y','n'))
                if(choose == 'y'):
                    encryptAllPass(master_password)
                    SecureData.massUpdate(
                        encriptedModel = Secret.encrypt(master_password,"example"),
                        securityLevel = 1
                    )
                else:
                    return
            elif(level==0):
                master_password = ""
                confirm_password = "n"
                while master_password!=confirm_password:
                    master_password = inputMasterPassword()
                    confirm_password= forceInput(manager.getWord("confirm_master_password"),rule=FIRules.filter_word,min_len=4,max_len=8,input_type="password")
                    if(master_password!=confirm_password):
                        console.print(manager.getWord("unmatch_passwords"))
                choose = forceInput(manager.getWord("generic_edit_quest2"),('y','n'))
                if(choose == 'y'):
                    dencryptAllPass(master_password)
                    SecureData.massUpdate(
                        encriptedModel = None,
                        securityLevel = 0
                    )

                else:
                    return
                
        except Exception as ex:
            raise ex
            pass

@configure_app.command()
def passwordMask(
    mask:Annotated[str,typer.Argument(help=manager.getWord("cmd_desc_password_mask"))]
):
    Configs.password_mask = mask
    Configs.save()

if __name__ == "__main__":
    app()
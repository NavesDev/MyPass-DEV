import sqlite3,os,rich;
from rich.console import Console;
from rich.table import Table;
from script.langs import manager;
console = Console()

class _Db():
    name = 'user.db'
    locate = 'data'
    database=None
    def __init__(self):
        ## Criando instâncias básicas de Banco de dados
        os.makedirs(self.locate,exist_ok=True)
        database = sqlite3.connect(f"{self.locate}/{self.name}")
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
        pass
    def load(self):
        # LOADING DB ASSETS
        self.close()
        try:
            self.database = sqlite3.connect(f"{self.locate}/{self.name}")
            return self.database
        except Exception:
            raise Exception("DB connection failure")
    def close(self):
        try:
            if(self.database):
                self.database.commit()
                self.database.close()
                self.database = None
        except Exception:
            raise Exception("DB close failure")
        
    def search(self,query:str, queryParams,paramID = None):
        cursor = None
        try:
            ## FAZENDO A BUSCA
            if(not self.database):
                self.load()
            cursor = self.database.cursor()
            cursor.execute(query,queryParams)
            data = cursor.fetchall()

            ## SELECIONANDO O CORRETO DA BUSCA
            if(len(data)>1):
                choose = ''
                while choose!='n' and choose!='y':
                    word = manager.getWord("cmd_desc_edit_account_more_than_one").format(first_item= ", ".join(str(item) for item in data[0])) 
                    console.print(word,highlight=False)
                    choose = input().strip()
                    choose = choose.lower()

                if(choose=='n'):
                    if(len(data)==2):
                        ## SE FOR SOMENTE DOIS ELEMENTOS ELE VAI PUXAR O SEGUNDO
                        word = manager.getWord("success_search").format(item= ", ".join(str(item) for item in data[1])) 
                        console.print(word,highlight=False)
                        return data[1]
                    
                    ## LISTA DE OPÇÕES A SEREM ESCOLHIDAS
                    index = 1
                    output = Table(title=manager.getWord("search_list"),
                        box=rich.box.ROUNDED,
                        header_style="bold bright_blue", 
                        row_styles=[""],
                        caption=manager.getWord("search_quest"),
                        show_lines=True,
                        padding=(0,3))
                    output.add_column(manager.getWord("search_id").upper(), style="grey54",justify='center')
                    output.add_column(manager.getWord("search_data").upper(),style='white')
                    newList = {}
                    for item in data[1:]:
                        newList[str(index)] = item
                        output.add_row(str(index),", ".join(str(i) for i in item))
                        index+= 1
                    console.print(output)
                    choose = input()
                    choose = choose.strip()
                    
                    if(newList.get(choose)):
                        word = manager.getWord("success_search").format(item= ", ".join(str(item) for item in newList[choose])) 
                        console.print(word,highlight=False)
                        return newList[choose]
                    else:
                        word = manager.getWord("error_search").format(num_item=choose) 
                        console.print(word,highlight=False)
                        return False
                else:
                    word = manager.getWord("success_search").format(item= ", ".join(str(item) for item in data[0])) 
                    console.print(word,highlight=False)
                    return data[0]
            elif(len(data)==1):
                word = manager.getWord("success_search").format(item= ", ".join(str(item) for item in data[0])) 
                console.print(word,highlight=False)
                return data[0]
            else:
                word = manager.getWord("error_search").format(num_item = paramID)
                console.print(word, highlight=False) 
                return False

        except Exception as ex:
            print(ex)
            raise Exception("Search failure") from ex
        finally:
            if(cursor):
                cursor.close()
          
        
db = _Db()

def forceInput(text:str,responses:list[str]):
    choose = None
    while choose not in responses:
        console.print(text,highlight=False)
        choose = input().strip()
    return choose

import sqlite3,os,rich,json,base64,getpass;
from rich.console import Console;
from rich.table import Table;
from script.langs import manager;
from cryptography.fernet import Fernet;
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from script.configs import Configs,SecureData;
from script.constants import SECRET_DIR;


console = Console()

# CÓDIGO PARA CRIPTOGRAFAR DADOS COM BASE EM UMA SENHA MESTRA
class _Secret:
    def __init__(self):
        pass
    def _kdf(self):
        return PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32, # O Fernet precisa de uma chave de 32 bytes
            salt=base64.b64decode(SecureData.salt),
            iterations=480000,
            backend=default_backend()
        )  
    def encrypt(self,master_password,data_to_crip):
        # CRIPTOGRAFA OS DADOS COM BASE NA SENHA MESTRA
        crip_key = base64.urlsafe_b64encode(self._kdf().derive(master_password.encode("utf-8")))
        fernet = Fernet(crip_key)
        return fernet.encrypt(data_to_crip.encode("utf-8")).decode()
    def decrypt(self,master_password:str,encodeKey:str):
        # DESCRIPTOGRAFA OS DADOS SOMENTE SE HOUVER A SENHA MESTRA
        try:
            cripKey = base64.urlsafe_b64encode(self._kdf().derive(master_password.encode("utf-8")))
            fernet = Fernet(cripKey)
            return fernet.decrypt(encodeKey.encode()).decode()
        except Exception as ex:

            console.print(manager.getWord("error_wrong_key"),highlight=False)
            return False
            
Secret = _Secret()
default_account_name = "UserDefault"

# CLASSE PARA GERÊNCIAR BANCO DE DADOS
class _Db:
    name = 'user.db'
    locate = SECRET_DIR / 'data'
    database = None

    def __init__(self):
        ## CRIANDO INSTÂNCIAS BÁSICAS NO BANCO DE DADOS

        os.makedirs(self.locate,exist_ok=True)
        database = sqlite3.connect(self.locate / self.name)
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
        if Configs.selected_account == None:
            cursor.execute(f"""
                INSERT INTO Accounts(name) VALUES( '{default_account_name}');
            """) 
            Configs.massUpdate(selected_account = cursor.lastrowid)
        

        database.commit()
        database.close()
        pass
    def execute(self,query,query_params = ()):
        try:
            self.load()
            cursor = self.database.cursor()
            cursor.execute(query,query_params)
            self.database.commit()
            return cursor.fetchall()
        finally:
            cursor.close()
    def load(self):
        # CARREGAR E ENTREGAR BANCO DE DADOS
        self.close()
        try:
            self.database = sqlite3.connect(f"{self.locate}/{self.name}")
            return self.database
        except Exception:
            raise Exception("DB connection failure")
    def close(self):
        try:
            if(self.database):
                try:
                    self.database.commit()
                except:
                    pass
                self.database.close()
                self.database = None
        except Exception as ex:
            raise ex
        
    def search(self,query:str, queryParams,paramID = None):
    
        try:
            ## FAZENDO A BUSCA
            
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
                    
                    ## EMITE UMA LISTA DE OPÇÕES DA BUSCA
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
                    new_list = {}
                    for item in data[1:]:
                        new_list[str(index)] = item
                        output.add_row(str(index),", ".join(str(i) for i in item))
                        index+= 1
                    console.print(output)
                    choose = input()
                    choose = choose.strip()
                    
                    if(new_list.get(choose)):
                        word = manager.getWord("success_search").format(item= ", ".join(str(item) for item in new_list[choose])) 
                        console.print(word,highlight=False)
                        return new_list[choose]
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

# CLASSE DE REGRAS DO FORCE INPUT PARA FACILITAR A VISIBILADE
class FIRules():
    ## SOMETE PALAVRAS PRÉ SELECIONADAS
    selected_words = 0
    ## PALAVRAS COM FILTROS (Ex.: mais de seis letras)
    filter_word = 1
    ## SENHA SECRETA
    
    ## VALIDAR A PALAVRA, VERIFICANDO SE ELA OBEDECE A TODOS OS FILTROS
    def checkFilters(word,filters:dict = {}):
        ### FILTROS
        #### TAMANHO MÁXIMO DA PALAVRA
        max_len = filters.get("max_len")
        if(max_len and len(word)>max_len):
            return False
        #### TAMANHO MÍNIMO DA PALAVRA
        min_len = filters.get("min_len")
        if(min_len and len(word)<min_len):
            return False
        return True

# UM INPUT QUE SÓ PARA QUANDO RECEBE RESPOSTAS ADEQUADAS
def forceInput(text:str,responses:list[str] = None,rule:int = FIRules.selected_words,**kwargs):
    choose = None
    if(rule == FIRules.selected_words):
        while choose not in responses:
            console.print(text,highlight=False)
            choose = input().strip()
    elif(rule == FIRules.filter_word):
        valid_word = False
        while not valid_word:
            console.print(text,highlight=False)
            input_type = kwargs.get("input_type")
            if(input_type and input_type=="password"):
                choose = getpass.getpass("> ")
            else:
                choose = input().strip()
            if(FIRules.checkFilters(choose,kwargs)):
                valid_word = True
    return choose

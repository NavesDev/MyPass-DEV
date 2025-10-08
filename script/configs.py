from platformdirs import user_data_dir;
import os,json,base64;

from rich.console import Console;
from script.constants import SECRET_DIR;
console = Console()

class _Configs:
    # CONFIGURAÇÕES DO SISTEMA
    def __init__(self):
        stored = None
        try:
            with open("config.json","r") as r:
                stored = json.load(r)
        except FileNotFoundError:
            pass
        except Exception:
            console.print("error: config.json", style='red')
            raise Exception("error: some error on config.json")
        
        values = stored or {}
        self.lang = values.get("lang","pt-br")
        self.selected_account = values.get("selected_account",None)
        self.password_mask = values.get("password_mask","[bold]***[/bold]")
        pass
    def massUpdate(self, **kwargs):
        for i,value in kwargs.items():
            if(i!= "massUpdate"):
                setattr(self,i,value)
        self.save()
    def save(self):
        try:
            with open("config.json","w") as w:
                json.dump(self.__dict__,w,indent=4)
        except Exception:
            console.print("error: config.json", style='red')
            raise Exception("error: some error on saving config.json")


# DADOS SEGUROS QUE NÃO DEVEM SER PERDIDOS
# CASO HOUVER PERDA, SENHAS NÃO PODERAM SER DESCRIPTOGRAFADAS
class _SecureData:
        def __init__(self):
        
            stored = None
            os.makedirs(SECRET_DIR,exist_ok=True)

            try:
                with open(SECRET_DIR / "secureData.json","r") as r:
                    stored = json.load(r)
            except FileNotFoundError:
                pass
            except Exception:
                console.print("error: secureData.json", style='red')
                raise Exception("error: some error on secureData.json")
            
            values = stored or {}
            self.salt = values.get("salt")
            if(self.salt is None):
                self.salt = base64.b64encode(os.urandom(16)).decode('utf-8')
            self.securityLevel = values.get("securityLevel",None)
            self.encriptedModel = values.get("encriptedModel",None)
            if(not stored):
                self.save()
            
        def massUpdate(self, **kwargs):
            for i,value in kwargs.items():
                if(i!= "massUpdate"):
                    setattr(self,i,value)
            self.save()
            
        def save(self):
            # SALVAR AS CONFIGURAÇÕES NO ARQUIVO
            print(self.__dict__)
            try:
                with open(SECRET_DIR / "secureData.json","w") as w:
                    json.dump(self.__dict__,w,indent=4)
            except Exception as ex:
                console.print("error:secureData.json", style='red')
                print(ex)
                raise Exception("error: some error on saving secureData.json")

Configs = _Configs()
Configs.save()
SecureData = _SecureData()

import constants, math
from rich.text import Text;
from rich.panel import Panel;
from rich.console import Console;
console = Console()
langsBook = {
    "pt-br": {
    "header": f"[bold]--- MyPass {constants.getVersion()} ---[/bold]",
    "usage": "Uso: passmanager [COMANDO] [ARGUMENTOS]",
    "commands_title": "Comandos Principais:",
    "commands_footer": "Página ",
    
    # Comandos de Ajuda e Visualização
    "cmd_desc_help": "help <página>\n  Mostra os comandos do script.",
    "cmd_desc_list": "list accounts\n  Lista todas as contas que você pode selecionar.",
    "cmd_desc_current": "current\n  Mostra qual conta está selecionada no momento.",
    "cmd_desc_show": "show [--reveal]\n  Mostra os serviços da conta ativa. Use a flag --reveal para também exibir as senhas.",
    "cmd_desc_copy": "copy --service <serviço> ou --id <id>\n  Copia a senha de determinado serviço da conta ativa.",
    
    # Comandos de Gerenciamento de Contexto e Idioma
    "cmd_desc_select": "select <conta>\n  Define a conta ativa para os comandos seguintes.",
    "cmd_desc_lang": "lang <idioma>\n  Muda o idioma da interface (ex: pt-br, en-us).",  # NOVO
    
    # Comandos de Edição e Adição
    "cmd_desc_add": "add --service <serviço>\n  Adiciona um novo serviço à conta ativa, e permite adicionar uma senha.",
    "cmd_desc_edit_service": "edit --service <serviço> ou --id <id>\n  Edita um serviço e seus dados da conta ativa.",
    "cmd_desc_edit_account": "edit account\n  Edita uma conta e seus dados.",
    # Comandos de Deleção (PERIGOSOS!)
    "cmd_desc_delete_service": "delete --service <serviço> ou --id <id>\n  Deleta um serviço específico da conta ativa.", # NOVO
    "cmd_desc_delete_account": "delete account <conta>\n  DELETA PERMANENTEMENTE uma conta e todas as senhas nela. (CUIDADO!)", # NOVO
    
    # Mensagens de Status
    "error_no_context": "❌ Erro: Nenhuma conta selecionada. Use 'passmanager select <conta>' para definir um contexto.",
    "success_context_set": "✅ Contexto definido para: {account}"
}
}

class langManager:
    def __init__(self,lang,book):
        self.lang = lang
        self.langsBook = book
        pass
    def changeLang(self,newlang):
        self.lang = newlang

    def getWord(self,wordIndex):
        return self.langsBook[self.lang][wordIndex]

    def getHelpMenu(self,page=1):
        context = self.langsBook[self.lang]
        numPerPage = 5
        
        commands = [value for key, value in context.items() if "cmd_desc" in key]
        maxPage = math.ceil(len(commands)/numPerPage) if commands else 1
        minIndex = (page-1)*numPerPage
        maxIndex = minIndex+numPerPage
        thisCommands = commands[minIndex:maxIndex]
        menu = Text()
        for i in thisCommands:
            temp = i.split("\n")
            name = temp[0]
            desc = temp[1]
            menu.append(f"  {name}", style="bold cyan")
            menu.append(f"{desc}\n", style="white")
        footer = Text(f"{context["commands_footer"]}{page}...{maxPage}",justify="right",style="dim")
        
        output = Panel(Text("\n").join([menu,footer]),title=f"✅ [bold]{context['commands_title']}[/bold] ✅",border_style="white",padding=(1,1)) 
        
        return output

manager = langManager("pt-br",langsBook)
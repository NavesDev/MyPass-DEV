import script.constants as constants,math;
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
    "cmd_desc_list_accounts": " Lista todas as contas que você pode selecionar.",
    "cmd_desc_current": "current\n  Mostra qual conta está selecionada no momento.",
    "cmd_desc_list_services": "Mostra os serviços da conta ativa. Use a flag --reveal para também exibir as senhas.",
    "cmd_desc_copy": "copy --service <serviço> ou --id <id>\n  Copia a senha de determinado serviço da conta ativa.",
    
    # Comandos de Gerenciamento de Contexto e Idioma
    "cmd_desc_select": "select <conta>\n  Define a conta ativa para os comandos seguintes.",
    "cmd_desc_lang": "lang <idioma>\n  Muda o idioma da interface (ex: pt-br, en-us).",  # NOVO
    
    # Comandos de Edição e Adição
    "cmd_desc_add": "Adiciona um novo serviço à conta ativa, e permite adicionar uma senha.",
    "cmd_desc_add_account": "Adiciona uma nova conta a aplicação.",
    "cmd_desc_add_account_email": "Adiciona um email a conta que está sendo criada",
    "cmd_desc_edit_service": "edit service [--service] <serviço> [--id <id>] [--password <senha>]\n  Edita um serviço e seus dados da conta ativa.",
    "cmd_desc_edit_account": "Edita uma conta e seus dados.",
    "generic_edit_quest":"[bold]Deseja prosseguir com as alterações?[/bold]\n[grey54]{last_data}[/grey54] ➡️  {new_data}\n(y) Sim; (n) Não",
    "cmd_desc_edit_account_page": "Define a página da lista.",
    "cmd_desc_edit_account_idname":"O parâmetro de identificação da conta a ser buscada",
    "cmd_desc_edit_account_name":"Novo nome da conta (Opcional)",
    "cmd_desc_edit_account_email":"Novo email da conta (Opcional)",
    "cmd_desc_edit_account_more_than_one":"[khaki1]👥 Mais de um item encontrado pela busca![/khaki1]\nDeseja prosseguir com [bold]{first_item}[/bold] ?\n(y) Sim; (n) Não",
    # Comandos de Deleção (PERIGOSOS!)
    "cmd_desc_delete_service": "delete service --service <serviço> ou --id <id>\n  Deleta um serviço específico da conta ativa.", # NOVO
    "cmd_desc_delete_account": "delete account <conta>\n  DELETA PERMANENTEMENTE uma conta e todas as senhas nela. (CUIDADO!)", # NOVO
    
    # Mensagens de Status
    "error_no_page": "[red]❌ Página não encontrada! Tente de 1...{max_page}[/red]",
    "error_no_account_listed":"[white]💤 [khaki1]Nenhuma conta encontrada![/khaki1] Use [grey54]<mypass add account>[/grey54] para adicionar uma conta![/white]",
    "error_no_context": "❌ Erro: Nenhuma conta selecionada. Use 'passmanager select <conta>' para definir um contexto.",
    "success_account_create": "✅ Usuário criado com succeso:[bold] {account}, {email}[/bold]",
    "success_context_set": "✅ Contexto definido para: {account}",
    "error_general": "[bold red]❌ Erro: Erro inesperado[/bold red]",
    "error_no_edit_data": "[bold red]❌ Erro: Não há nenhuma edição para ser feita! [/bold red]\nUtilize [grey54]<edit account --help>[/grey54] para saber mais",
    "double_account":"[khaki1]Já existe uma conta com esse nome! Deseja continuar?[/khaki1]\n(y) Sim; (n) Não",
    "success_edit":"[bold green]✅ Alterações feitas com sucesso[/bold green]",
    "success_search":"✅ Item selecionado com sucesso: [bold]{item}[/bold]\n",
    "error_search":"[bold red]❌ Erro: nehum item encontrado por [/bold red]<{num_item}>",
    # Constantes
    "no_email":"[bold gold1]<sem email registrado>[/bold gold1]",
    "id_word":"Id",
    'search_list':"Lista de itens",
    'search_quest':"Insira o número do item requisitado",
    'name_word':"Conta",
    'email_word':"Email",
    "search_id":"Item",
    'search_data':"Dados do item",
    "notFoundEmail":"[khaki1]NÃO REGISTRADO[/khaki1]"
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
        if(page>maxPage or page<1):
            return Text(self.langsBook[self.lang]["error_no_page"],style='Bold Red')
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
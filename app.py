
import pandas as pd
import panel as pn
from datetime import date, datetime
from typing import Optional
from decimal import Decimal


from python.database import SessionLocal, create_tables, Pessoa, Familia
from python.crud import (
    create_pessoa, get_pessoa, get_pessoas, update_pessoa, delete_pessoa,
    create_familia, get_familia, get_familias, update_familia, delete_familia,
    execute_raw_query
)

pn.extension('tabulator') # Extensão para tabelas interativas


# Função para obter uma nova sessão de banco de dados
def get_db_session():
    return SessionLocal()

print("Backend e modelos carregados com sucesso!")



# Widgets de entrada para Família
nome_familia_input = pn.widgets.TextInput(name='Nome da Família', width=300)
endereco_input = pn.widgets.TextInput(name='Endereço', width=300)
bairro_input = pn.widgets.TextInput(name='Bairro', width=300)
cidade_input = pn.widgets.TextInput(name='Cidade', width=300)
estado_input = pn.widgets.TextInput(name='Estado (Ex: SP)', width=300)
cep_input = pn.widgets.TextInput(name='CEP (Ex: 00000-000)', width=300)
telefone_familia_input = pn.widgets.TextInput(name='Telefone da Família (Ex: (DD) 9XXXX-XXXX)', width=300)
renda_mensal_input = pn.widgets.FloatInput(name='Renda Mensal (R$)', start=0.0, step=0.01, width=300)
status_vulnerabilidade_checkbox = pn.widgets.Checkbox(name='Status de Vulnerabilidade', value=False)
observacoes_familia_input = pn.widgets.TextAreaInput(name='Observações da Família', width=300, height=100)

cadastrar_familia_button = pn.widgets.Button(name='Cadastrar Família', button_type='primary')
mensagem_familia = pn.pane.Markdown("")

@pn.depends(cadastrar_familia_button, watch=True)
def _cadastrar_familia(event):
    db = get_db_session()
    try:
        # Validação básica de campos obrigatórios
        if not nome_familia_input.value or not endereco_input.value or not cep_input.value or not telefone_familia_input.value:
            mensagem_familia.object = "<span style='color: red;'>Por favor, preencha todos os campos obrigatórios (Nome, Endereço, CEP, Telefone).</span>"
            return

        
        renda = None
        if renda_mensal_input.value is not None:
            try:
                renda = Decimal(str(renda_mensal_input.value))
            except Exception:
                mensagem_familia.object = "<span style='color: red;'>Renda Mensal inválida. Use um número.</span>"
                return

        familia = create_familia(
            db=db,
            nome_familia=nome_familia_input.value,
            endereco=endereco_input.value,
            bairro=bairro_input.value,
            cidade=cidade_input.value,
            estado=estado_input.value,
            cep=cep_input.value,
            telefone=telefone_familia_input.value,
            renda_mensal=renda,
            status_vulnerabilidade=status_vulnerabilidade_checkbox.value,
            observacoes=observacoes_familia_input.value
        )
        mensagem_familia.object = f"<span style='color: green;'>Família '{familia.nome_familia}' (ID: {familia.id_familia}) cadastrada com sucesso!</span>"

        nome_familia_input.value = ""
        endereco_input.value = ""
        bairro_input.value = ""
        cidade_input.value = ""
        estado_input.value = ""
        cep_input.value = ""
        telefone_familia_input.value = ""
        renda_mensal_input.value = 0.0
        status_vulnerabilidade_checkbox.value = False
        observacoes_familia_input.value = ""
        update_familias_table()
    except Exception as e:
        mensagem_familia.object = f"<span style='color: red;'>Erro ao cadastrar família: {e}</span>"
    finally:
        db.close()

cadastrar_familia_button.on_click(_cadastrar_familia)

# Layout para cadastro de família
cadastro_familia_layout = pn.Column(
    pn.pane.Markdown("## Cadastro de Família"),
    nome_familia_input,
    endereco_input,
    bairro_input,
    cidade_input,
    estado_input,
    cep_input,
    telefone_familia_input,
    renda_mensal_input,
    status_vulnerabilidade_checkbox,
    observacoes_familia_input,
    cadastrar_familia_button,
    mensagem_familia
)


familias_data = pn.widgets.Tabulator(value=pd.DataFrame([]), layout='fit_columns', selectable=True, width=800, height=300)
mensagem_listagem_familia = pn.pane.Markdown("")

# Widgets para edição de família
familia_id_edit_input = pn.widgets.IntInput(name='ID da Família para Editar/Deletar', start=1, width=300)
nome_familia_edit_input = pn.widgets.TextInput(name='Novo Nome da Família', width=300)
endereco_edit_input = pn.widgets.TextInput(name='Novo Endereço', width=300)
status_vulnerabilidade_edit_checkbox = pn.widgets.Checkbox(name='Novo Status de Vulnerabilidade', value=False)
atualizar_familia_button = pn.widgets.Button(name='Atualizar Família', button_type='warning')
deletar_familia_button = pn.widgets.Button(name='Deletar Família', button_type='danger')

def update_familias_table():
    db = get_db_session()
    try:
        familias = get_familias(db)
        # Converte a lista de objetos Familia para uma lista de dicionários para o Tabulator
        data = []
        for f in familias:
            data.append({
                'ID': f.id_familia,
                'Nome': f.nome_familia,
                'Endereço': f.endereco,
                'Bairro': f.bairro,
                'Cidade': f.cidade,
                'Estado': f.estado,
                'CEP': f.cep,
                'Telefone': f.telefone,
                'Renda Mensal': float(f.renda_mensal) if f.renda_mensal is not None else None,
                'Data Cadastro': f.data_cadastro.strftime('%Y-%m-%d') if f.data_cadastro else '',
                'Vulnerável': 'Sim' if f.status_vulnerabilidade else 'Não',
                'Observações': f.observacoes
            })
        familias_data.value = pd.DataFrame(data)
        mensagem_listagem_familia.object = ""
    except Exception as e:
        mensagem_listagem_familia.object = f"<span style='color: red;'>Erro ao carregar famílias: {e}</span>"
    finally:
        db.close()

# Carrega as famílias ao iniciar
update_familias_table()

@pn.depends(atualizar_familia_button, watch=True)
def _atualizar_familia(event):
    db = get_db_session()
    try:
        familia_id = familia_id_edit_input.value
        if not familia_id:
            mensagem_listagem_familia.object = "<span style='color: red;'>Por favor, insira um ID de família para atualizar.</span>"
            return

        updated_familia = update_familia(
            db=db,
            familia_id=familia_id,
            nome_familia=nome_familia_edit_input.value if nome_familia_edit_input.value else None,
            endereco=endereco_edit_input.value if endereco_edit_input.value else None,
            status_vulnerabilidade=status_vulnerabilidade_edit_checkbox.value
        )
        if updated_familia:
            mensagem_listagem_familia.object = f"<span style='color: green;'>Família ID {familia_id} atualizada com sucesso!</span>"
            update_familias_table()
        else:
            mensagem_listagem_familia.object = f"<span style='color: orange;'>Família ID {familia_id} não encontrada.</span>"
    except Exception as e:
        mensagem_listagem_familia.object = f"<span style='color: red;'>Erro ao atualizar família: {e}</span>"
    finally:
        db.close()

@pn.depends(deletar_familia_button, watch=True)
def _deletar_familia(event):
    db = get_db_session()
    try:
        familia_id = familia_id_edit_input.value
        if not familia_id:
            mensagem_listagem_familia.object = "<span style='color: red;'>Por favor, insira um ID de família para deletar.</span>"
            return

        if delete_familia(db, familia_id):
            mensagem_listagem_familia.object = f"<span style='color: green;'>Família ID {familia_id} deletada com sucesso!</span>"
            update_familias_table()
        else:
            mensagem_listagem_familia.object = f"<span style='color: orange;'>Família ID {familia_id} não encontrada.</span>"
    except Exception as e:
        mensagem_listagem_familia.object = f"<span style='color: red;'>Erro ao deletar família: {e}</span>"
    finally:
        db.close()

atualizar_familia_button.on_click(_atualizar_familia)
deletar_familia_button.on_click(_deletar_familia)

# Layout para listagem e edição de família
listagem_edicao_familia_layout = pn.Column(
    pn.pane.Markdown("## Famílias Cadastradas"),
    pn.Row(pn.widgets.Button(name='Recarregar Famílias', button_type='default', on_click=lambda event: update_familias_table()), width=800),
    familias_data,
    pn.pane.Markdown("### Editar/Deletar Família"),
    familia_id_edit_input,
    nome_familia_edit_input,
    endereco_edit_input,
    status_vulnerabilidade_edit_checkbox,
    pn.Row(atualizar_familia_button, deletar_familia_button),
    mensagem_listagem_familia
)


# Widgets de entrada para Pessoa
nome_completo_pessoa_input = pn.widgets.TextInput(name='Nome Completo', width=300)
data_nasc_pessoa_input = pn.widgets.DatePicker(name='Data de Nascimento', value=date.today(), width=300)
cpf_pessoa_input = pn.widgets.TextInput(name='CPF (Ex: 000.000.000-00)', width=300)
rg_pessoa_input = pn.widgets.TextInput(name='RG', width=300)
genero_pessoa_input = pn.widgets.Select(name='Gênero', options=['Masculino', 'Feminino', 'Outro', 'Não Informar'], width=300)
email_pessoa_input = pn.widgets.TextInput(name='Email', width=300)
telefone_pessoa_input = pn.widgets.TextInput(name='Telefone (Ex: (DD) 9XXXX-XXXX)', width=300)

cadastrar_pessoa_button = pn.widgets.Button(name='Cadastrar Pessoa', button_type='primary')
mensagem_pessoa = pn.pane.Markdown("")

@pn.depends(cadastrar_pessoa_button, watch=True)
def _cadastrar_pessoa(event):
    db = get_db_session()
    try:
        if not nome_completo_pessoa_input.value or not cpf_pessoa_input.value or not email_pessoa_input.value:
            mensagem_pessoa.object = "<span style='color: red;'>Por favor, preencha Nome Completo, CPF e Email.</span>"
            return

        pessoa = create_pessoa(
            db=db,
            nome_completo=nome_completo_pessoa_input.value,
            data_nasc=data_nasc_pessoa_input.value,
            cpf=cpf_pessoa_input.value,
            rg=rg_pessoa_input.value if rg_pessoa_input.value else None,
            genero=genero_pessoa_input.value,
            email=email_pessoa_input.value,
            telefone=telefone_pessoa_input.value if telefone_pessoa_input.value else None
        )
        mensagem_pessoa.object = f"<span style='color: green;'>Pessoa '{pessoa.nome_completo}' (ID: {pessoa.id_pessoa}) cadastrada com sucesso!</span>"
        # Limpa os campos
        nome_completo_pessoa_input.value = ""
        data_nasc_pessoa_input.value = date.today()
        cpf_pessoa_input.value = ""
        rg_pessoa_input.value = ""
        genero_pessoa_input.value = 'Não Informar'
        email_pessoa_input.value = ""
        telefone_pessoa_input.value = ""
       
        update_pessoas_table()
    except Exception as e:
        mensagem_pessoa.object = f"<span style='color: red;'>Erro ao cadastrar pessoa: {e}</span>"
    finally:
        db.close()

cadastrar_pessoa_button.on_click(_cadastrar_pessoa)


cadastro_pessoa_layout = pn.Column(
    pn.pane.Markdown("## Cadastro de Pessoa"),
    nome_completo_pessoa_input,
    data_nasc_pessoa_input,
    cpf_pessoa_input,
    rg_pessoa_input,
    genero_pessoa_input,
    email_pessoa_input,
    telefone_pessoa_input,
    cadastrar_pessoa_button,
    mensagem_pessoa
)


pessoas_data = pn.widgets.Tabulator(value=pd.DataFrame([]), layout='fit_columns', selectable=True, width=800, height=300)
mensagem_listagem_pessoa = pn.pane.Markdown("")


pessoa_id_edit_input = pn.widgets.IntInput(name='ID da Pessoa para Editar/Deletar', start=1, width=300)
nome_completo_edit_input = pn.widgets.TextInput(name='Novo Nome Completo', width=300)
email_edit_input = pn.widgets.TextInput(name='Novo Email', width=300)
atualizar_pessoa_button = pn.widgets.Button(name='Atualizar Pessoa', button_type='warning')
deletar_pessoa_button = pn.widgets.Button(name='Deletar Pessoa', button_type='danger')

def update_pessoas_table():
    db = get_db_session()
    try:
        pessoas = get_pessoas(db)
        data = []
        for p in pessoas:
            data.append({
                'ID': p.id_pessoa,
                'Nome Completo': p.nome_completo,
                'Data Nasc.': p.data_nasc.strftime('%Y-%m-%d') if p.data_nasc else '',
                'CPF': p.cpf,
                'RG': p.rg,
                'Gênero': p.genero,
                'Email': p.email,
                'Telefone': p.telefone
            })
        pessoas_data.value = pd.DataFrame(data)
        mensagem_listagem_pessoa.object = ""
    except Exception as e:
        mensagem_listagem_pessoa.object = f"<span style='color: red;'>Erro ao carregar pessoas: {e}</span>"
    finally:
        db.close()


update_pessoas_table()

@pn.depends(atualizar_pessoa_button, watch=True)
def _atualizar_pessoa(event):
    db = get_db_session()
    try:
        pessoa_id = pessoa_id_edit_input.value
        if not pessoa_id:
            mensagem_listagem_pessoa.object = "<span style='color: red;'>Por favor, insira um ID de pessoa para atualizar.</span>"
            return

        updated_pessoa = update_pessoa(
            db=db,
            pessoa_id=pessoa_id,
            nome_completo=nome_completo_edit_input.value if nome_completo_edit_input.value else None,
            email=email_edit_input.value if email_edit_input.value else None
        )
        if updated_pessoa:
            mensagem_listagem_pessoa.object = f"<span style='color: green;'>Pessoa ID {pessoa_id} atualizada com sucesso!</span>"
            update_pessoas_table()
        else:
            mensagem_listagem_pessoa.object = f"<span style='color: orange;'>Pessoa ID {pessoa_id} não encontrada.</span>"
    except Exception as e:
        mensagem_listagem_pessoa.object = f"<span style='color: red;'>Erro ao atualizar pessoa: {e}</span>"
    finally:
        db.close()

@pn.depends(deletar_pessoa_button, watch=True)
def _deletar_pessoa(event):
    db = get_db_session()
    try:
        pessoa_id = pessoa_id_edit_input.value
        if not pessoa_id:
            mensagem_listagem_pessoa.object = "<span style='color: red;'>Por favor, insira um ID de pessoa para deletar.</span>"
            return

        if delete_pessoa(db, pessoa_id):
            mensagem_listagem_pessoa.object = f"<span style='color: green;'>Pessoa ID {pessoa_id} deletada com sucesso!</span>"
            update_pessoas_table()
        else:
            mensagem_listagem_pessoa.object = f"<span style='color: orange;'>Pessoa ID {pessoa_id} não encontrada.</span>"
    except Exception as e:
        mensagem_listagem_pessoa.object = f"<span style='color: red;'>Erro ao deletar pessoa: {e}</span>"
    finally:
        db.close()

atualizar_pessoa_button.on_click(_atualizar_pessoa)
deletar_pessoa_button.on_click(_deletar_pessoa)


listagem_edicao_pessoa_layout = pn.Column(
    pn.pane.Markdown("## Pessoas Cadastradas"),
    pn.Row(pn.widgets.Button(name='Recarregar Pessoas', button_type='default', on_click=lambda event: update_pessoas_table()), width=800),
    pessoas_data,
    pn.pane.Markdown("### Editar/Deletar Pessoa"),
    pessoa_id_edit_input,
    nome_completo_edit_input,
    email_edit_input,
    pn.Row(atualizar_pessoa_button, deletar_pessoa_button),
    mensagem_listagem_pessoa
)




raw_query_input = pn.widgets.TextAreaInput(name='Consulta SQL Bruta', value="SELECT * FROM familia LIMIT 5;", width=800, height=150)
execute_raw_query_button = pn.widgets.Button(name='Executar Consulta', button_type='success')
raw_query_output = pn.pane.Markdown("")
raw_query_results_table = pn.widgets.Tabulator(value=pd.DataFrame([]), layout='fit_columns', width=800, height=300)

@pn.depends(execute_raw_query_button, watch=True)
def _execute_raw_query(event):
    try:
        results = execute_raw_query(raw_query_input.value)
        if results:
            raw_query_results_table.value = results
            raw_query_output.object = "<span style='color: green;'>Consulta executada com sucesso!</span>"
        else:
            raw_query_results_table.value = []
            raw_query_output.object = "<span style='color: orange;'>Consulta executada, mas sem resultados ou não é uma consulta SELECT.</span>"
    except Exception as e:
        raw_query_output.object = f"<span style='color: red;'>Erro ao executar consulta: {e}</span>"

execute_raw_query_button.on_click(_execute_raw_query)

raw_query_layout = pn.Column(
    pn.pane.Markdown("## Consulta SQL Bruta"),
    raw_query_input,
    execute_raw_query_button,
    raw_query_output,
    raw_query_results_table
)


tabs = pn.Tabs(
    ('Cadastro Família', cadastro_familia_layout),
    ('Gerenciar Famílias', listagem_edicao_familia_layout),
    ('Cadastro Pessoa', cadastro_pessoa_layout),
    ('Gerenciar Pessoas', listagem_edicao_pessoa_layout),
    ('SQL Bruto', raw_query_layout)
)


#  tabs.show(port=5007)
tabs.show()

print("Aplicação Panel iniciada. Verifique seu navegador para a interface.")
print("Você pode fechar esta janela do terminal para parar a aplicação.")


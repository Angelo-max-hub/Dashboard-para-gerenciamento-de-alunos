from dash import MATCH, Dash, html, callback, Input, Output, State, dcc, ALL, no_update
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import pandas as pd
from pandas.api.types import is_numeric_dtype
import plotly.express as px
import plotly.io as pio

# Temas.
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server
pio.templates.default = "plotly_dark"

# Extrair dados do banco de dados.
alunos_df = pd.read_csv("data/alunos.csv", encoding="utf-8")

# ID para os inputs de formulário de inserção de alunos.
id_input_novo_aluno = lambda x: {"type": "input-novo-aluno", "index": x}
# =====================================================================================
# .. Layout do app.
# =====================================================================================
app.layout = dbc.Container([
    html.H1(children= "Gerenciamento de turmas"),
    html.P("Se quiser adicionar um novo aluno a tabela abaixo, clique no botão a seguir."),
    html.P("Para ordenar a tabela de acordo com uma coluna, clique no título da coluna."),
    # Botão para ativar o formulário de inserção  e botão para pesquisa de aluno.
    dbc.Row(
        [
        dbc.Col(dbc.Button("Adicionar aluno", id="button-input")),
        dbc.Col(dbc.Button("Pesquisar", id="button-find", color="secondary"), width="auto")
        ],
        className="mb-2",
        justify="between"
    ),
    
    
    # .. Modais.
    dbc.Modal(id={"type": "modal", "index": "modal-alerta-aluno-inserido"}),
    dbc.Modal(id="modal-pesquisa", fullscreen=True, is_open=False, scrollable=True,
              children=[
                  dbc.ModalHeader(dbc.ModalTitle("Pesquisar aluno.")),
                  dbc.ModalBody([
                      dbc.Label("Nome do aluno"),
                      dbc.Input(type="text", id="modal-pesquisar-input-aluno",
                                placeholder="Somente o primeiro nome"),
                      dbc.FormText("Insira o nome do aluno pesquisado no campo acima.")
                  ]),
                  dbc.Container(id="modal-pesquisar-output",
                                className="bg-secondary justify-content-center p-3",
                                style={"overflowX": "auto", "maxHeight": "300px"}),
                  dbc.ModalFooter([
                      dbc.Button("Buscar aluno", id="button-buscar-aluno")
                  ])
              ]),
    
    # Formulário para inserção de novos alunos.
    dbc.Collapse(
        dbc.Form([
            finput1_nome:= dbc.Input(placeholder="Nome",
                      id={"type": "input-novo-aluno", "index": "nome"}),
            finput2_idade:= dbc.Input(placeholder="Idade",
                      id={"type": "input-novo-aluno", "index": "idade"}),
            finput3_genero:= dbc.Input(placeholder="Gênero",
                      id={"type": "input-novo-aluno", "index": "genero"}),
            finput4_notafinal:= dbc.Input(placeholder="Nota final",
                      id={"type": "input-novo-aluno", "index": "notafinal"}),
            finput5_turma:= dbc.Input(placeholder="Turma",
                      id={"type": "input-novo-aluno", "index": "turma"}),
            dbc.Button("Salvar", id="button-save", className="mt-2 mb-2"),
        ]),
        is_open=False,
        id="form"
    ),
    # Tabela para os alunos.
    dag.AgGrid(
        id="tabela-alunos",
        rowData=alunos_df.to_dict("records"),
        columnDefs= [{"field": i } for i in alunos_df.columns]
    ),
    # Gráficos.
    html.H1("Gráficos", className="mt-3"),
    html.P('Você pode alterar o eixo "y" dos gráficos com os botões abaixo.'),

    # Menu para escolher itens.
    dbc.Alert(id={"type": "modal", "index": "alerta-grafico-erro"},
              color="warning", is_open=False),
    dbc.RadioItems(
        id="radio-x-graficos",
        className="btn-group mt-3 mb-3",
        inputClassName="btn-check",
        labelClassName="btn btn-outline-primary",
        inline=True,
        options=[{"label": i, "value": i} for i in alunos_df.columns if not i == "Turma"],
        value="Idade"
    ),
    dbc.Row([
        dbc.Col(dcc.Graph(id="histograma")),
        dbc.Col(dcc.Graph(id="distribuicao"))
    ]),
    


    # Armazenamento para o dataset lido.
    dcc.Store(id="alunos-dataset", data=alunos_df.to_json(date_format="iso",
                                                          orient="split"))
])

# =====================================================================================
# .. Callbacks.
# =====================================================================================

## Atualizar itens da tabela de alunos.
@callback(
    Output("tabela-alunos", "rowData"),
    Input("alunos-dataset", "data")
)
def atualizar_tabela_alunos(alunos_dataset):
    alunos_df = pd.read_json(alunos_dataset, orient="split")

    return alunos_df.to_dict("records")


## Exibir formulário para adicionar novas pessoas a tabela.
@callback(
    [Output(component_id="form", component_property="is_open"),
     Output("button-input", "children")],
    Input(component_id="button-input", component_property="n_clicks"),
    State(component_id="form", component_property="is_open"),
    prevent_initial_call=True
)
def exibir_form_adicionar_pessoa(n_clicks, is_open):
    is_open = not is_open
    if is_open:
        nome_botao = "Fechar"
    else:
        nome_botao = "Adicionar aluno"
    return is_open, nome_botao

# Exibir modal sempre que seu conteúdo for alterado.
@callback(
    Output({"type": "modal", "index": MATCH}, "is_open"),
    Input({"type": "modal", "index": MATCH}, "children"),
    prevent_initial_call=True
)
def exibir_modal(modal_children):
    return bool(modal_children)

# Salvar dados inseridos em formulário e ativar o modal de "sucesso."
@callback([
    Output({"type": "input-novo-aluno", "index": ALL}, "value"),
    Output({"type": "modal", "index": "modal-alerta-aluno-inserido"}, "children"),
    Output("alunos-dataset", "data")
],
    Input("button-save", "n_clicks"),
    # Inputs do formulário de inserção.
    State(finput1_nome, "value"),
    State(finput2_idade, "value"),
    State(finput3_genero, "value"),
    State(finput4_notafinal, "value"),
    State(finput5_turma, "value"),
        
    State("alunos-dataset", "data"),
    prevent_initial_call=True
)
def salvar_dados_aluno(n_clicks,
                       nome1,
                       idade2,
                       genero3,
                       notafinal4,
                       turma5,
                       alunos_store
                       ):
    # Adicionar o novo aluno.
    alunos_df = pd.read_json(alunos_store, orient="split")
    alunos_df.loc[len(alunos_df), ["Nome",
                                   "Idade",
                                   "Gênero",
                                   "Nota final",
                                   "Turma"]] = [nome1, idade2, genero3, notafinal4, turma5]
    alunos_df.to_csv("data/alunos.csv", index=False, encoding="utf-8")

    # Exibir modal.
    modal_content = [
        dbc.ModalHeader(dbc.ModalTitle("Pronto")),
        dbc.ModalBody("Aluno adicionado com sucesso.")
    ]
    
    return ["", "", "", "", ""], modal_content, alunos_df.to_json(orient="split", date_format="iso")


# Histograma e scatter.
@callback(
    Output("histograma", "figure"),
    Output("distribuicao", "figure"),
    Output({"type": "modal", "index": "alerta-grafico-erro"}, "children"),
    Input("alunos-dataset", "data"),
    Input("radio-x-graficos", "value")
)

def gerar_graficos(alunos_store, value):
    # Conteúdo de alerta caso ele não seja necessário.
    alerta_conteudo = ""

    # Cria os graficos.
    # Verifica se o eixo escolhido é numérico e, portanto, suportado pelo histograma.
    # Caso contrário, não atualiza e exibe um alerta.
    alunos_df = pd.read_json(alunos_store, orient="split")
    if is_numeric_dtype(alunos_df[value]):
        fig_histo = px.histogram(alunos_df, x="Turma", y=value, title=f"{value} por turma")
        
        # Permitir scroll horizontal no histograma.
        fig_histo.update_xaxes(rangeslider_visible=True)
        # Animar gráficos.
        fig_histo.update_layout(
        transition= {
            'duration': 1000, 'easing': "cubic-in-out"
        })
        
    else:
        fig_histo = no_update
        alerta_conteudo = \
            """O eixo escolhido é uma coluna com texto, então não é possivel exibí-la em
            um histograma. """
        

    # Gráfico de pizza.
    if alunos_df[value].nunique() <= 50:
        fig_pie = px.pie(alunos_df, names=value, title=f"{value} por turma")
        fig_pie.update_layout(
            transition={
                'duration': 1000, 'easing': "cubic-in-out"
            }
        )
    else:
        fig_pie = no_update
        alerta_conteudo = """
        A coluna escolhida tem itens demais para ser representada por uma pizza. """

    return fig_histo, fig_pie, alerta_conteudo

# Botão de pesquisar alunos.
@callback(
    Output("modal-pesquisa", "is_open"),
    Input("button-find", "n_clicks"),
)
def abrir_modal_pesquisar(n_clicks):
    if n_clicks is not None:
        return True

@callback(
    Output("modal-pesquisar-output", "children"),
    Input("button-buscar-aluno", "n_clicks"),
    State("modal-pesquisar-input-aluno", "value"),
    State("alunos-dataset", "data"),
    prevent_init_call=True
)
def buscar_aluno_em_modal(n_clicks, input_nome_value, alunos_dataset):
    alunos_df = pd.read_json(alunos_dataset, orient="split")
    alunos_filtrados = alunos_df.loc[alunos_df["Nome"] == input_nome_value]

    if len(alunos_filtrados) == 0:
        return html.H1("Nenhum aluno encontrado com esse nome.")
    conteudo_output = []
    for _, linha_aluno in alunos_filtrados.iterrows():
        conteudo_output.append(html.H2("Aluno encontrado."))
        conteudo_output.extend(
            [html.P(f"{chave}: {valor}") for chave, valor in linha_aluno.items()]
        )

    return conteudo_output

if __name__ == "__main__":
    app.run(debug=True)

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import html
from datetime import datetime

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Emissor Comercial",
    page_icon="🧾",
    layout="wide"
)

# ============================================================
# ESTADOS
# ============================================================

defaults = {
    "produtos": [],
    "numero_nota": 5001,
    "documento_emitido": False,
    "html_emitido": "",
    "numero_emitido": None,
}

for chave, valor in defaults.items():
    if chave not in st.session_state:
        st.session_state[chave] = valor

# ============================================================
# DADOS FIXOS DAS LOJAS
# ============================================================

LOJAS = {
    "Colina Matriz": {
        "razao": "COLINA BIKE CENTER (MATRIZ)",
        "endereco": "RUA XV DE NOVEMBRO, 7535",
        "cidade": "JOINVILLE - SC",
        "cep": "89237-001",
        "fone": "(47) 9 99110-6252",
    },
    "Colina Filial": {
        "razao": "COLINA BIKE CENTER (FILIAL)",
        "endereco": "RUA SÃO PAULO, 1182 - SALA 18",
        "cidade": "JOINVILLE - SC",
        "cep": "89202-200",
        "fone": "(47) 9 9243-5997",
    },
}

# ============================================================
# FUNÇÕES UTILITÁRIAS
# ============================================================

def esc(texto):
    return html.escape(str(texto or ""))


def moeda(valor):
    return (
        f"R$ {float(valor):,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def numero_br(valor):
    return (
        f"{float(valor):,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def reordenar_itens():
    for i, item in enumerate(st.session_state.produtos, start=1):
        item["Item"] = i


def adicionar_item(nome, ncm, qtd, valor):
    st.session_state.produtos.append(
        {
            "Item": len(st.session_state.produtos) + 1,
            "Produto": nome.strip(),
            "NCM": ncm.strip() or "8712.00.10",
            "Qtd": int(qtd),
            "Valor Unit.": float(valor),
            "Total": int(qtd) * float(valor),
        }
    )


def remover_item(indice):
    if 0 <= indice < len(st.session_state.produtos):
        st.session_state.produtos.pop(indice)
        reordenar_itens()


def gerar_html_documento(
    loja,
    numero,
    serie,
    nome_cli,
    cpf_cli,
    endereco_cli,
    cidade_cli,
    cep_cli,
    telefone_cli,
    email_cli,
    vendedor,
    forma_pagamento,
    produtos,
    frete,
    desconto,
    observacoes,
):
    total_produtos = sum(float(i["Total"]) for i in produtos)
    total_final = max(0.0, total_produtos + float(frete) - float(desconto))

    # Apenas demonstrativos internos
    icms_estimado = total_produtos * 0.17
    ipi_estimado = total_produtos * 0.065

    linhas = ""
    for item in produtos:
        linhas += f"""
        <tr>
            <td class="c">{item['Item']}</td>
            <td>{esc(item['Produto'])}</td>
            <td class="c">{esc(item['NCM'])}</td>
            <td class="c">{item['Qtd']}</td>
            <td class="r">{moeda(item['Valor Unit.'])}</td>
            <td class="r"><b>{moeda(item['Total'])}</b></td>
        </tr>
        """

    data_emissao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    obs = esc(observacoes).replace("\n", "<br>") if observacoes.strip() else "Sem observações."

    return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Documento {numero:06d}</title>

<style>
    @page {{
        size: A4 portrait;
        margin: 8mm;
    }}

    * {{
        box-sizing: border-box;
    }}

    body {{
        margin: 0;
        padding: 0;
        font-family: Arial, Helvetica, sans-serif;
        color: #111;
        background: white;
        font-size: 10px;
    }}

    .doc {{
        width: 100%;
        max-width: 194mm;
        margin: auto;
        background: white;
    }}

    .toolbar {{
        position: sticky;
        top: 0;
        z-index: 1000;
        display: flex;
        gap: 10px;
        justify-content: center;
        padding: 12px;
        margin-bottom: 12px;
        background: #f4f6f8;
        border: 1px solid #d8dde3;
        border-radius: 10px;
    }}

    .btn-print {{
        border: 0;
        background: #111827;
        color: white;
        font-size: 14px;
        font-weight: 700;
        padding: 11px 22px;
        border-radius: 8px;
        cursor: pointer;
    }}

    .btn-print:hover {{
        opacity: .9;
    }}

    .hint {{
        align-self: center;
        color: #475569;
        font-size: 12px;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 7px;
    }}

    td, th {{
        border: 1px solid #222;
        padding: 5px;
        vertical-align: middle;
    }}

    .cabecalho td {{
        height: 27mm;
    }}

    .emitente {{
        width: 45%;
        font-size: 10px;
        line-height: 1.45;
    }}

    .tipo {{
        width: 30%;
        text-align: center;
        background: #f0f0f0;
    }}

    .numero {{
        width: 25%;
        text-align: center;
        line-height: 1.6;
    }}

    .danfe {{
        font-size: 19px;
        font-weight: 800;
        letter-spacing: .5px;
    }}

    .mini {{
        font-size: 8px;
    }}

    .section {{
        background: #e9ecef;
        font-weight: 700;
        letter-spacing: .2px;
    }}

    .label {{
        font-size: 7px;
        text-transform: uppercase;
        color: #333;
        margin-bottom: 3px;
    }}

    .value {{
        font-size: 10px;
        font-weight: 700;
    }}

    .c {{
        text-align: center;
    }}

    .r {{
        text-align: right;
    }}

    .produtos th {{
        background: #e9ecef;
        text-align: center;
        font-size: 9px;
    }}

    .produtos td {{
        min-height: 7mm;
    }}

    .totais .valor-destaque {{
        font-size: 13px;
        font-weight: 800;
    }}

    .obs {{
        min-height: 25mm;
        vertical-align: top;
        line-height: 1.45;
    }}

    .rodape {{
        border: 1px solid #222;
        padding: 6px;
        text-align: center;
        font-size: 7.5px;
        line-height: 1.4;
    }}

    .assinatura {{
        margin-top: 12mm;
        display: flex;
        justify-content: space-between;
        gap: 20mm;
    }}

    .assinatura > div {{
        flex: 1;
        border-top: 1px solid #333;
        padding-top: 4px;
        text-align: center;
        font-size: 8px;
    }}

    @media print {{
        .toolbar {{
            display: none !important;
        }}

        body {{
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }}

        .doc {{
            max-width: none;
        }}
    }}
</style>
</head>

<body>

<div class="toolbar">
    <button class="btn-print" onclick="window.print()">
        🖨️ IMPRIMIR DOCUMENTO
    </button>
    <div class="hint">
        A impressão acontece nesta própria tela, sem download e sem pop-up.
    </div>
</div>

<div class="doc">

    <table class="cabecalho">
        <tr>
            <td class="emitente">
                <b>{esc(loja['razao'])}</b><br>
                {esc(loja['endereco'])}<br>
                {esc(loja['cidade'])} | CEP {esc(loja['cep'])}<br>
                Fone: {esc(loja['fone'])}
            </td>

            <td class="tipo">
                <div class="danfe">DANFE</div>
                <div class="mini">DOCUMENTO AUXILIAR</div>
                <br>
                <b>DOCUMENTO COMERCIAL</b>
            </td>

            <td class="numero">
                <b>Nº {numero:06d}</b><br>
                SÉRIE {esc(serie)}<br>
                <span class="mini">Emitido em {data_emissao}</span>
            </td>
        </tr>
    </table>

    <table>
        <tr>
            <td colspan="4" class="section">DESTINATÁRIO / REMETENTE</td>
        </tr>

        <tr>
            <td colspan="3">
                <div class="label">Nome / Razão Social</div>
                <div class="value">{esc(nome_cli or "NÃO INFORMADO")}</div>
            </td>
            <td>
                <div class="label">CPF / CNPJ</div>
                <div class="value">{esc(cpf_cli or "NÃO INFORMADO")}</div>
            </td>
        </tr>

        <tr>
            <td colspan="2">
                <div class="label">Endereço</div>
                <div>{esc(endereco_cli or "NÃO INFORMADO")}</div>
            </td>

            <td>
                <div class="label">Cidade / UF</div>
                <div>{esc(cidade_cli or "NÃO INFORMADO")}</div>
            </td>

            <td>
                <div class="label">CEP</div>
                <div>{esc(cep_cli or "NÃO INFORMADO")}</div>
            </td>
        </tr>

        <tr>
            <td colspan="2">
                <div class="label">Telefone</div>
                <div>{esc(telefone_cli or "NÃO INFORMADO")}</div>
            </td>

            <td colspan="2">
                <div class="label">E-mail</div>
                <div>{esc(email_cli or "NÃO INFORMADO")}</div>
            </td>
        </tr>
    </table>

    <table>
        <tr>
            <td colspan="4" class="section">DADOS DA OPERAÇÃO</td>
        </tr>
        <tr>
            <td>
                <div class="label">Vendedor</div>
                <div class="value">{esc(vendedor or "NÃO INFORMADO")}</div>
            </td>
            <td>
                <div class="label">Forma de pagamento</div>
                <div class="value">{esc(forma_pagamento)}</div>
            </td>
            <td>
                <div class="label">Número</div>
                <div class="value">{numero:06d}</div>
            </td>
            <td>
                <div class="label">Série</div>
                <div class="value">{esc(serie)}</div>
            </td>
        </tr>
    </table>

    <table class="produtos">
        <tr>
            <th width="7%">ITEM</th>
            <th width="42%">DESCRIÇÃO DO PRODUTO</th>
            <th width="15%">NCM</th>
            <th width="8%">QTD.</th>
            <th width="14%">V. UNIT.</th>
            <th width="14%">V. TOTAL</th>
        </tr>
        {linhas}
    </table>

    <table class="totais">
        <tr>
            <td colspan="5" class="section">TOTAIS</td>
        </tr>
        <tr>
            <td>
                <div class="label">Produtos</div>
                <div class="value">{moeda(total_produtos)}</div>
            </td>
            <td>
                <div class="label">Frete</div>
                <div class="value">{moeda(frete)}</div>
            </td>
            <td>
                <div class="label">Desconto</div>
                <div class="value">{moeda(desconto)}</div>
            </td>
            <td>
                <div class="label">ICMS demonstrativo</div>
                <div class="value">{moeda(icms_estimado)}</div>
            </td>
            <td>
                <div class="label">Total do documento</div>
                <div class="valor-destaque">{moeda(total_final)}</div>
            </td>
        </tr>
    </table>

    <table>
        <tr>
            <td class="section">INFORMAÇÕES COMPLEMENTARES</td>
        </tr>
        <tr>
            <td class="obs">
                <b>Observações:</b><br>
                {obs}
                <br><br>
                <span class="mini">
                    ICMS e IPI exibidos apenas como demonstrativos internos.
                    IPI demonstrativo: {moeda(ipi_estimado)}.
                </span>
            </td>
        </tr>
    </table>

    <div class="assinatura">
        <div>Assinatura / responsável pela emissão</div>
        <div>Assinatura do cliente / recebedor</div>
    </div>

    <div class="rodape">
        <b>DOCUMENTO COMERCIAL PARA CONTROLE INTERNO</b><br>
        Este documento não substitui NF-e, NFC-e ou outro documento fiscal
        autorizado pela Secretaria da Fazenda.
    </div>

</div>

</body>
</html>
"""


# ============================================================
# ESTILO DO APP
# ============================================================

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 3rem;
        }

        div[data-testid="stMetric"] {
            background: rgba(240,242,246,.55);
            border: 1px solid rgba(120,120,120,.15);
            padding: 12px;
            border-radius: 12px;
        }

        .app-title {
            padding: 14px 18px;
            border-radius: 14px;
            background: #f3f4f6;
            border: 1px solid #e5e7eb;
            margin-bottom: 18px;
        }

        .app-title h1 {
            margin: 0;
            font-size: 28px;
        }

        .app-title p {
            margin: 4px 0 0 0;
            color: #475569;
        }
    </style>

    <div class="app-title">
        <h1>🧾 Emissor Comercial</h1>
        <p>Cadastro, emissão e impressão direta em layout DANFE.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("🏢 Unidade emissora")

loja_nome = st.sidebar.radio(
    "Selecione a loja",
    list(LOJAS.keys())
)

loja = LOJAS[loja_nome]

st.sidebar.divider()

st.sidebar.subheader("🔢 Documento")

numero_input = st.sidebar.number_input(
    "Número",
    min_value=1,
    value=int(st.session_state.numero_nota),
    step=1
)
st.session_state.numero_nota = int(numero_input)

serie = st.sidebar.text_input("Série", value="02", max_chars=5)

st.sidebar.divider()

st.sidebar.subheader("👤 Cliente")

nome_cli = st.sidebar.text_input("Nome / Razão Social")
cpf_cli = st.sidebar.text_input("CPF / CNPJ")
endereco_cli = st.sidebar.text_input("Endereço")
cidade_cli = st.sidebar.text_input("Cidade / UF", value="Joinville - SC")
cep_cli = st.sidebar.text_input("CEP")
telefone_cli = st.sidebar.text_input("Telefone")
email_cli = st.sidebar.text_input("E-mail")

st.sidebar.divider()

st.sidebar.subheader("🧑‍💼 Operação")

vendedor = st.sidebar.text_input("Vendedor")
forma_pagamento = st.sidebar.selectbox(
    "Forma de pagamento",
    [
        "Não informado",
        "Dinheiro",
        "PIX",
        "Cartão de Débito",
        "Cartão de Crédito",
        "Boleto",
        "Transferência",
        "Outro",
    ]
)

# ============================================================
# PRODUTOS
# ============================================================

st.subheader("📦 Itens do documento")

with st.container(border=True):
    c1, c2, c3, c4 = st.columns([4, 2, 1.2, 1.7])

    with c1:
        produto = st.text_input(
            "Descrição do produto",
            key="novo_produto",
            placeholder="Ex.: Bicicleta MTB aro 29"
        )

    with c2:
        ncm = st.text_input(
            "NCM",
            key="novo_ncm",
            value="8712.00.10"
        )

    with c3:
        qtd = st.number_input(
            "Quantidade",
            min_value=1,
            value=1,
            step=1,
            key="nova_qtd"
        )

    with c4:
        valor_unitario = st.number_input(
            "Valor unitário",
            min_value=0.0,
            value=0.0,
            step=1.0,
            format="%.2f",
            key="novo_valor"
        )

    if st.button(
        "➕ Adicionar produto",
        type="primary",
        use_container_width=True
    ):
        if not produto.strip():
            st.error("Informe a descrição do produto.")
        elif valor_unitario <= 0:
            st.error("O valor unitário deve ser maior que zero.")
        else:
            adicionar_item(produto, ncm, qtd, valor_unitario)
            st.session_state.documento_emitido = False
            st.success("Produto adicionado.")
            st.rerun()

if st.session_state.produtos:
    df = pd.DataFrame(st.session_state.produtos)

    st.dataframe(
        df[["Item", "Produto", "NCM", "Qtd", "Valor Unit.", "Total"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Valor Unit.": st.column_config.NumberColumn(
                "Valor Unit.",
                format="R$ %.2f"
            ),
            "Total": st.column_config.NumberColumn(
                "Total",
                format="R$ %.2f"
            ),
        },
    )

    with st.expander("🗑️ Remover item"):
        opcoes = [
            f"{i + 1} - {item['Produto']}"
            for i, item in enumerate(st.session_state.produtos)
        ]

        item_remover = st.selectbox(
            "Selecione o item",
            opcoes
        )

        c_rem1, c_rem2 = st.columns(2)

        with c_rem1:
            if st.button(
                "Remover selecionado",
                use_container_width=True
            ):
                indice = opcoes.index(item_remover)
                remover_item(indice)
                st.session_state.documento_emitido = False
                st.rerun()

        with c_rem2:
            if st.button(
                "Limpar todos",
                use_container_width=True
            ):
                st.session_state.produtos = []
                st.session_state.documento_emitido = False
                st.rerun()

else:
    st.info("Nenhum produto adicionado.")

# ============================================================
# VALORES DA OPERAÇÃO
# ============================================================

st.subheader("💰 Valores adicionais")

cv1, cv2, cv3 = st.columns(3)

with cv1:
    frete = st.number_input(
        "Frete",
        min_value=0.0,
        value=0.0,
        format="%.2f"
    )

with cv2:
    desconto = st.number_input(
        "Desconto",
        min_value=0.0,
        value=0.0,
        format="%.2f"
    )

with cv3:
    total_produtos = sum(
        float(i["Total"]) for i in st.session_state.produtos
    )
    total_documento = max(
        0.0,
        total_produtos + float(frete) - float(desconto)
    )

    st.metric(
        "Total do documento",
        moeda(total_documento)
    )

observacoes = st.text_area(
    "📝 Observações",
    placeholder="Informações adicionais do documento..."
)

# ============================================================
# RESUMO
# ============================================================

m1, m2, m3, m4 = st.columns(4)

m1.metric("Itens", len(st.session_state.produtos))
m2.metric("Produtos", moeda(total_produtos))
m3.metric("Frete", moeda(frete))
m4.metric("Total", moeda(total_documento))

# ============================================================
# EMISSÃO
# ============================================================

st.divider()
st.subheader("🖨️ Emitir e imprimir")

st.caption(
    "Esta versão não usa download nem pop-up. "
    "A impressão é feita dentro do próprio documento exibido abaixo."
)

emitir = st.button(
    "🧾 GERAR DOCUMENTO PARA IMPRESSÃO",
    type="primary",
    use_container_width=True,
    disabled=not bool(st.session_state.produtos)
)

if emitir:
    erros = []

    if not nome_cli.strip():
        erros.append("Nome / Razão Social")

    if not cpf_cli.strip():
        erros.append("CPF / CNPJ")

    if not endereco_cli.strip():
        erros.append("Endereço")

    if not st.session_state.produtos:
        erros.append("Produtos")

    if erros:
        st.error(
            "Preencha antes de emitir: " + ", ".join(erros)
        )
    else:
        html_emitido = gerar_html_documento(
            loja=loja,
            numero=int(st.session_state.numero_nota),
            serie=serie,
            nome_cli=nome_cli,
            cpf_cli=cpf_cli,
            endereco_cli=endereco_cli,
            cidade_cli=cidade_cli,
            cep_cli=cep_cli,
            telefone_cli=telefone_cli,
            email_cli=email_cli,
            vendedor=vendedor,
            forma_pagamento=forma_pagamento,
            produtos=st.session_state.produtos,
            frete=frete,
            desconto=desconto,
            observacoes=observacoes,
        )

        st.session_state.html_emitido = html_emitido
        st.session_state.numero_emitido = int(
            st.session_state.numero_nota
        )
        st.session_state.documento_emitido = True

# ============================================================
# ÁREA DE IMPRESSÃO
# ============================================================

if st.session_state.documento_emitido:
    st.success(
        f"Documento nº {st.session_state.numero_emitido:06d} "
        "gerado. Use o botão IMPRIMIR DOCUMENTO dentro da prévia."
    )

    components.html(
        st.session_state.html_emitido,
        height=1100,
        scrolling=True
    )

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button(
            "✅ Finalizar emissão e avançar número",
            use_container_width=True
        ):
            st.session_state.numero_nota = (
                int(st.session_state.numero_emitido) + 1
            )
            st.session_state.documento_emitido = False
            st.session_state.html_emitido = ""
            st.session_state.numero_emitido = None
            st.rerun()

    with col_b:
        if st.button(
            "✏️ Voltar para editar",
            use_container_width=True
        ):
            st.session_state.documento_emitido = False
            st.rerun()

# ============================================================
# AVISO
# ============================================================

st.divider()

st.caption(
    "Este aplicativo gera documento comercial para controle interno. "
    "Ele não transmite NF-e/NFC-e à SEFAZ e não substitui documento fiscal oficial."
)

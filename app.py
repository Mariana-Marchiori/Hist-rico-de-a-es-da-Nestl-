
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==================================================
# CONFIGURAÇÃO
# ==================================================

st.set_page_config(
    page_title="Histórico da Nestlé",
    page_icon="📊",
    layout="wide"
)

VERMELHO = "#E31837"
VERMELHO_ESCURO = "#A50F2D"
VERMELHO_CLARO = "#FCE8EC"
BRANCO = "#FFFFFF"
CINZA = "#666666"

st.markdown("""
<style>
.stApp {
    background-color: #FFFFFF;
    color: #292929;
}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}
.hero {
    background: linear-gradient(120deg, #A50F2D, #E31837);
    padding: 30px;
    border-radius: 16px;
    color: white;
    margin-bottom: 22px;
}
.hero h1 {
    color: white;
    font-size: 36px;
    margin-bottom: 8px;
}
.hero p {
    color: white;
    font-size: 16px;
    margin-bottom: 0;
}
div[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #F0C5CD;
    border-top: 4px solid #E31837;
    border-radius: 10px;
    padding: 16px;
}
div[data-testid="stMetricLabel"] {
    color: #666666;
}
h2, h3 {
    color: #A50F2D;
}
div[data-testid="stExpander"] {
    border-color: #F0C5CD;
}
.stDownloadButton button {
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

TEMA = "plotly_white"

# ==================================================
# CABEÇALHO
# ==================================================

st.markdown("""
<div class="hero">
    <h1>Histórico da Nestlé</h1>
    <p>
        Evolução histórica, indicadores de desempenho e análise
        dos resultados ao longo dos anos.
    </p>
    <hr style="border-color: rgba(255,255,255,0.4);">
    <p>
        <strong>Integrantes:</strong> Beatriz Neres,
        Mariana Marchiori, Luiza Romeiro e Monalisa Silva
    </p>
    <p>
        <strong>Professor orientador:</strong> Felipe Garbin
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown(
    "Este painel permite explorar os dados históricos da empresa. "
    "Os resultados e as conclusões dependem das informações "
    "presentes no arquivo CSV enviado."
)

# ==================================================
# UPLOAD
# ==================================================

from pathlib import Path
import pandas as pd
import streamlit as st

caminho_csv = Path(__file__).parent / "Nestle_historical_data.csv"

df = pd.read_csv(caminho_csv)

#########################################

st.markdown("""
### 🏢 Conheça a Nestlé

A Nestlé é uma empresa multinacional do setor de alimentos e bebidas, fundada na Suíça.
Seu portfólio inclui produtos como cafés, chocolates, laticínios, cereais e alimentos para
diferentes etapas da vida. Neste projeto, o dashboard ajuda a observar dados históricos
relacionados à empresa e a entender como os indicadores variam ao longo dos anos.
""")

if arquivo is None:
    st.info(
        "Envie o CSV para visualizar os gráficos, comparar anos "
        "e consultar as cinco principais informações."
    )

    st.markdown("### O que você encontrará no painel")

    c1, c2, c3 = st.columns(3)

    c1.markdown(
        "**📈 Evolução histórica**\n\n"
        "Veja como um indicador muda ao longo do tempo."
    )

    c2.markdown(
        "**📊 Variação anual**\n\n"
        "Identifique períodos de crescimento ou queda."
    )

    c3.markdown(
        "Escolha o ano de sua preferência"
        "Consulte os cinco principais resultados do período."
    )

else:
    try:
        # ==================================================
        # LEITURA E TRATAMENTO
        # ==================================================

        df = pd.read_csv(arquivo)
        df.columns = df.columns.astype(str).str.strip()

        if df.empty:
            st.warning("O arquivo está vazio.")
            st.stop()

        if len(df.columns) == 0:
            st.warning("O arquivo não possui colunas.")
            st.stop()

        # Identificar colunas de datas e anos
        nomes_ano = {"ano", "anos", "year", "years"}
        nomes_data = {
            "data", "date", "datetime", "timestamp",
            "data de referência", "data referencia"
        }

        colunas_ano = [
            c for c in df.columns
            if c.strip().lower() in nomes_ano
        ]

        colunas_data = [
            c for c in df.columns
            if c.strip().lower() in nomes_data
        ]

        # Converter anos para números, quando possível
        for c in colunas_ano:
            df[c] = pd.to_numeric(df[c], errors="coerce")

        # Converter datas para um fuso comum e remover o fuso.
        # Isso evita o erro de fusos horários mistos.
        datas_convertidas = {}

        for c in colunas_data:
            datas_convertidas[c] = pd.to_datetime(
                df[c],
                errors="coerce",
                utc=True
            ).dt.tz_localize(None)

        # Preparar lista de colunas temporais válidas
        colunas_temporais = colunas_ano + colunas_data

        # Reconhecer outras colunas que já contenham datas
        for c in df.columns:
            if (
                c not in colunas_temporais
                and pd.api.types.is_datetime64_any_dtype(df[c])
            ):
                colunas_temporais.append(c)
                datas_convertidas[c] = pd.to_datetime(
                    df[c], errors="coerce", utc=True
                ).dt.tz_localize(None)

        # Criar uma coluna interna para o ano da análise
        # sem modificar o valor original das colunas de data.
        coluna_tempo = None

        if colunas_temporais:
            # Seleção automática da coluna temporal para manter a interface simples.
            # Se houver uma coluna chamada Ano, ela tem prioridade; caso contrário,
            # é usada a primeira coluna de data reconhecida.
            coluna_tempo = (
                colunas_ano[0] if colunas_ano
                else colunas_temporais[0]
            )

            if coluna_tempo in colunas_ano:
                df["_Ano_analise"] = df[coluna_tempo].where(
                    df[coluna_tempo].between(1800, 2200)
                )
            elif coluna_tempo in datas_convertidas:
                df["_Ano_analise"] = (
                    datas_convertidas[coluna_tempo].dt.year
                )
            else:
                df["_Ano_analise"] = pd.to_datetime(
                    df[coluna_tempo], errors="coerce", utc=True
                ).dt.year

        else:
            st.error(
                "Não encontrei uma coluna de ano ou data. "
                "O arquivo precisa conter um período histórico "
                "para gerar os gráficos de evolução."
            )
            st.stop()

        # Identificar colunas numéricas
        colunas_numericas = df.select_dtypes(
            include="number"
        ).columns.tolist()

        colunas_metricas = [
            c for c in colunas_numericas
            if c not in colunas_ano
            and c != "_Ano_analise"
        ]

        if not colunas_metricas:
            st.error(
                "Não encontrei indicadores numéricos para analisar. "
                "Verifique se os valores de receita, vendas ou "
                "outros indicadores estão em formato numérico."
            )
            st.stop()

        # Identificar categorias
        colunas_categoricas = [
            c for c in df.select_dtypes(
                include=["object", "category", "string"]
            ).columns
            if c not in colunas_temporais
        ]

        # ==================================================
        # FILTROS
        # ==================================================

        st.subheader("⚙️ Personalize sua análise")
        st.caption(
            "Escolha o dado que deseja acompanhar. Os gráficos e o resumo "
            "serão atualizados automaticamente."
        )

        descricoes_colunas = {
            "ticker": "Ticker — código usado para identificar um ativo na bolsa.",
            "symbol": "Símbolo — código que identifica o ativo.",
            "date": "Data — dia em que o registro foi feito.",
            "datetime": "Data e hora — momento do registro.",
            "year": "Ano — ano ao qual o dado se refere.",
            "revenue": "Receita — dinheiro obtido com vendas e serviços.",
            "sales": "Vendas — quantidade ou valor de produtos vendidos, conforme a base.",
            "profit": "Lucro — valor que sobra após descontar os custos e despesas considerados.",
            "net income": "Lucro líquido — resultado após custos, despesas e impostos.",
            "price": "Preço — valor registrado para o ativo ou produto.",
            "volume": "Volume — quantidade negociada ou registrada, conforme a base.",
            "market cap": "Valor de mercado — valor estimado da empresa na bolsa.",
            "close": "Fechamento — preço do ativo no fim do período de negociação.",
            "open": "Abertura — preço do ativo no início do período de negociação.",
            "high": "Máxima — maior preço registrado no período.",
            "low": "Mínima — menor preço registrado no período.",
            "dividends": "Dividendos — valores distribuídos aos acionistas, se presentes na base.",
            "stock splits": "Desdobramentos — eventos em que ações são divididas em mais unidades."
        }

        def nome_amigavel(coluna):
            chave = str(coluna).strip().lower().replace("_", " ")
            return descricoes_colunas.get(chave, f"{coluna} — indicador numérico disponível no arquivo.")

        metrica = st.selectbox(
            "Indicador principal",
            colunas_metricas,
            format_func=nome_amigavel,
            help="Exemplos: receita, lucro, preço ou volume. A descrição ajuda a entender o que cada coluna representa."
        )
        agregacao = "Média"

        base = df.dropna(subset=["_Ano_analise"]).copy()
        base["_Ano_analise"] = base["_Ano_analise"].astype(int)

        anos_disponiveis = sorted(
            base["_Ano_analise"].unique().tolist()
        )

        if not anos_disponiveis:
            st.error("Não foram encontrados anos válidos.")
            st.stop()

        # A análise considera automaticamente todos os anos disponíveis.
        base_periodo = base.copy()

        anos_filtrados = sorted(
            base_periodo["_Ano_analise"].unique().tolist()
        )

        if not anos_filtrados:
            st.warning("Não existem dados no intervalo selecionado.")
            st.stop()

        ano_selecionado = st.selectbox(
            "Ano para o resumo e o Top 5",
            anos_filtrados,
            index=len(anos_filtrados) - 1,
            help="Escolha o ano que deseja consultar no resumo."
        )

        dados_ano = base_periodo[
            base_periodo["_Ano_analise"] == ano_selecionado
        ].copy()

        funcao = "mean"

        # ==================================================
        # INDICADORES DO ANO SELECIONADO
        # ==================================================

        st.divider()
        st.subheader(f"📌 Resumo de {ano_selecionado}")

        valor_ano = dados_ano[metrica].agg(funcao)

        serie = (
            base_periodo.groupby("_Ano_analise")[metrica]
            .agg(funcao)
            .sort_index()
        )

        serie_valida = serie.dropna()

        if ano_selecionado in serie.index:
            posicao = list(serie.index).index(ano_selecionado)
            anos_anteriores = serie.index[:posicao]

            if len(anos_anteriores):
                ano_anterior = anos_anteriores[-1]
                valor_anterior = serie.loc[ano_anterior]

                if (
                    pd.notna(valor_ano)
                    and pd.notna(valor_anterior)
                    and valor_anterior != 0
                ):
                    variacao = (
                        (valor_ano - valor_anterior)
                        / abs(valor_anterior)
                    ) * 100
                    variacao_texto = f"{variacao:+.2f}%"
                else:
                    variacao_texto = "Não calculável"
            else:
                variacao_texto = "Sem ano anterior"
        else:
            variacao_texto = "Sem dados"

        a, b, c, d = st.columns(4)

        a.metric("Ano selecionado", str(ano_selecionado))
        b.metric("Registros no ano", f"{len(dados_ano):,}".replace(",", "."))
        c.metric(
            f"{agregacao}: {metrica}",
            f"{valor_ano:,.2f}" if pd.notna(valor_ano) else "N/D"
        )
        d.metric("Variação anual", variacao_texto)

        st.caption(
            "A variação compara o indicador do ano selecionado com "
            "o ano anterior disponível no período. Uma variação "
            "positiva representa aumento numérico, não necessariamente "
            "melhora no desempenho do negócio."
        )

        # Texto interpretativo automático: descreve os dados, sem inventar causas.
        if pd.notna(valor_ano) and not serie_valida.empty:
            maior_ano = int(serie_valida.idxmax())
            menor_ano = int(serie_valida.idxmin())
            partes = [
                f"Em {ano_selecionado}, a média de **{metrica}** foi "
                f"**{valor_ano:,.2f}**."
            ]
            if variacao_texto not in ("Sem ano anterior", "Não calculável", "Sem dados"):
                if variacao > 0:
                    partes.append(
                        f"Isso representa um aumento de **{variacao:.2f}%** "
                        f"em relação a {int(ano_anterior)}."
                    )
                elif variacao < 0:
                    partes.append(
                        f"Isso representa uma redução de **{abs(variacao):.2f}%** "
                        f"em relação a {int(ano_anterior)}."
                    )
                else:
                    partes.append(
                        f"O valor ficou estável em relação a {int(ano_anterior)}."
                    )
            else:
                partes.append(
                    "Não há dados anteriores válidos suficientes para calcular "
                    "a variação percentual deste ano."
                )
            if ano_selecionado == maior_ano:
                partes.append("Este é o maior valor médio observado na série disponível.")
            elif ano_selecionado == menor_ano:
                partes.append("Este é o menor valor médio observado na série disponível.")
            partes.append(
                "Esses resultados descrevem o comportamento dos dados, mas não "
                "comprovam por si só quais acontecimentos causaram a mudança."
            )
            st.markdown(" ".join(partes))

        # ==================================================
        # GRÁFICO 1 — EVOLUÇÃO HISTÓRICA
        # ==================================================

        st.divider()
        st.subheader("📈 Evolução histórica")

        evolucao = serie_valida.rename("Valor").reset_index()
        evolucao = evolucao.rename(
            columns={"_Ano_analise": "Ano"}
        )

        fig_evolucao = px.line(
            evolucao,
            x="Ano",
            y="Valor",
            markers=True,
            title=f"Evolução anual de {metrica}",
            labels={
                "Ano": "Ano",
                "Valor": f"{metrica} ({agregacao.lower()})"
            },
            template=TEMA,
            color_discrete_sequence=[VERMELHO]
        )

        fig_evolucao.update_traces(
            name=metrica,
            line=dict(width=3),
            marker=dict(size=8),
            hovertemplate=(
                "Ano: %{x}<br>"
                + metrica + ": %{y:,.2f}<extra></extra>"
            )
        )

        fig_evolucao.update_layout(
            xaxis=dict(dtick=1, title="Ano"),
            yaxis_title=f"{metrica} ({agregacao.lower()})",
            showlegend=True,
            legend_title_text="Indicador",
            margin=dict(l=20, r=20, t=65, b=20)
        )

        st.plotly_chart(fig_evolucao, use_container_width=True)

        st.markdown(
            "**Como interpretar:** cada ponto representa o resultado "
            "do indicador em um ano. A linha facilita identificar "
            "períodos de alta, queda ou estabilidade. Passe o cursor "
            "sobre um ponto para consultar o valor."
        )

        # ==================================================
        # GRÁFICO 2 — VARIAÇÃO ANUAL
        # ==================================================

        st.subheader("📊 Variação percentual anual")

        variacao_df = (
            serie.pct_change(fill_method=None)
            .mul(100)
            .rename("Variação (%)")
            .reset_index()
        )

        variacao_df = variacao_df.dropna()
        variacao_df = variacao_df.rename(
            columns={"_Ano_analise": "Ano"}
        )

        if not variacao_df.empty:
            variacao_df["Resultado"] = variacao_df[
                "Variação (%)"
            ].apply(
                lambda x: "Aumento" if x > 0
                else "Queda" if x < 0
                else "Estabilidade"
            )

            fig_variacao = px.bar(
                variacao_df,
                x="Ano",
                y="Variação (%)",
                color="Resultado",
                color_discrete_map={
                    "Aumento": VERMELHO,
                    "Queda": "#8B8B8B",
                    "Estabilidade": "#D9A0AA"
                },
                title="Quanto o indicador variou em relação ao ano anterior",
                labels={
                    "Ano": "Ano",
                    "Variação (%)": "Variação (%)",
                    "Resultado": "Comportamento"
                },
                template=TEMA
            )

            fig_variacao.add_hline(
                y=0,
                line_dash="dash",
                line_color=CINZA
            )

            fig_variacao.update_layout(
                xaxis=dict(dtick=1),
                legend_title_text="Resultado",
                margin=dict(l=20, r=20, t=65, b=20)
            )

            st.plotly_chart(
                fig_variacao,
                use_container_width=True
            )

            st.markdown(
                "**Como interpretar:** barras acima de zero indicam "
                "aumento em relação ao ano anterior; abaixo de zero "
                "indicam redução. A variação percentual não pode ser "
                "calculada quando o valor anterior é zero ou inexistente."
            )
        else:
            st.info(
                "São necessários pelo menos dois anos com valores "
                "válidos para calcular a variação."
            )


        # ==================================================
        # COMPARAÇÃO DE INDICADORES
        # ==================================================

        if len(colunas_metricas) >= 2:
            st.divider()
            st.subheader("🔍 Comparação entre indicadores")

            st.markdown(
                "Escolha um único indicador para visualizar sua evolução "
                "com mais clareza, sem misturar categorias diferentes."
            )

            indicador_comparacao = st.selectbox(
                "Escolha um indicador",
                colunas_metricas,
                index=colunas_metricas.index(metrica),
                key="indicador_comparacao",
                format_func=nome_amigavel
            )
            indicadores = [indicador_comparacao]

            if indicadores:
                comp = (
                    base_periodo.groupby("_Ano_analise")[indicadores]
                    .agg(funcao)
                    .reset_index()
                    .melt(
                        id_vars="_Ano_analise",
                        var_name="Indicador",
                        value_name="Valor"
                    )
                    .rename(columns={"_Ano_analise": "Ano"})
                )

                fig_comp = px.line(
                    comp,
                    x="Ano",
                    y="Valor",
                    color="Indicador",
                    markers=True,
                    title="Evolução comparativa dos indicadores",
                    labels={
                        "Ano": "Ano",
                        "Valor": "Valor do indicador",
                        "Indicador": "Indicador"
                    },
                    template=TEMA,
                    color_discrete_sequence=[
                        VERMELHO, "#666666", "#D9A0AA",
                        "#A50F2D", "#B8B8B8"
                    ]
                )

                fig_comp.update_layout(
                    xaxis=dict(dtick=1),
                    legend_title_text="Indicadores",
                    hovermode="x unified"
                )

                st.plotly_chart(
                    fig_comp,
                    use_container_width=True
                )

                st.caption(
                    "Cada linha representa um indicador diferente. "
                    "Se as métricas tiverem escalas ou unidades muito "
                    "diferentes, a comparação visual direta pode "
                    "ser enganosa."
                )

        # ==================================================
        # QUALIDADE DOS DADOS
        # ==================================================

        with st.expander("🧹 Qualidade e estrutura dos dados"):
            st.markdown(
                "Esta seção apresenta verificações técnicas do CSV. "
                "Ela ajuda a identificar problemas que podem afetar "
                "a interpretação dos resultados."
            )

            duplicados_total = int(df.duplicated().sum())
            nulos_total = int(df.isnull().sum().sum())

            q1, q2 = st.columns(2)
            q1.metric("Registros duplicados", duplicados_total)
            q2.metric("Valores nulos", nulos_total)

            st.markdown("**Valores nulos por coluna**")

            nulos = (
                df.isnull().sum()
                .rename("Quantidade de valores nulos")
                .reset_index()
            )

            nulos.columns = [
                "Coluna",
                "Quantidade de valores nulos"
            ]

            st.dataframe(
                nulos,
                use_container_width=True,
                hide_index=True
            )

            st.markdown("**Registros duplicados**")

            duplicadas = df[df.duplicated(keep=False)]

            if duplicadas.empty:
                st.success("Nenhum registro duplicado encontrado.")
            else:
                st.dataframe(
                    duplicadas,
                    use_container_width=True,
                    hide_index=True
                )

            st.markdown("**O que significa cada coluna?**")
            explicacoes = []
            for coluna in df.drop(columns=["_Ano_analise"], errors="ignore").columns:
                explicacoes.append({
                    "Coluna": coluna,
                    "Explicação simples": nome_amigavel(coluna)
                })
            st.dataframe(
                pd.DataFrame(explicacoes),
                use_container_width=True,
                hide_index=True
            )

            st.markdown("**Prévia do arquivo original**")
            st.caption("A tabela abaixo mostra até 20 linhas do CSV enviado, sem alterar os dados originais.")
            st.dataframe(
                df.drop(columns=["_Ano_analise"], errors="ignore").head(20),
                use_container_width=True,
                hide_index=True
            )

        with st.expander("❓ Perguntas sobre o projeto", expanded=False):
            st.markdown("""
            ### Créditos

            **Integrantes:** Beatriz Neres, Mariana Marchiori, Luiza Romeiro e Monalisa Silva  
            **Professor orientador:** Felipe Garbin

            ---

            Esta seção reúne **todas as perguntas e respostas do documento obrigatório**, organizadas pelas aulas.

            ### Aula 1 – Escolher e compreender os dados

            **1. Qual é o tema do projeto?**

            O tema é o histórico da empresa Nestlé, com foco na evolução de indicadores ao longo dos anos.

            **2. Qual é o objetivo do projeto?**

            Criar um dashboard interativo para visualizar e analisar dados históricos da Nestlé, permitindo acompanhar indicadores, comparar períodos e identificar aumentos e reduções.

            **3. Qual base de dados será utilizada?**

            Será utilizado um arquivo CSV contendo dados históricos da Nestlé. A fonte original e a confiabilidade dos dados precisam ser verificadas, pois não estão identificadas no código enviado.

            **4. Quais são as duas perguntas que o projeto pretende responder?**

            - Como o indicador escolhido evoluiu ao longo dos anos?
            - Em quais anos houve aumento ou redução percentual do indicador em relação ao ano anterior?

            ### Aula 2 – Upload e tratamento dos dados

            **5. Quais ferramentas foram utilizadas?**

            - **Python:** linguagem de programação.
            - **Pandas:** leitura, organização e tratamento dos dados.
            - **Plotly Express:** criação dos gráficos interativos.
            - **Streamlit:** criação da interface do dashboard.

            **6. Como o arquivo CSV é carregado?**

            O arquivo é enviado pelo usuário por meio de `st.file_uploader()` e lido pelo Pandas com `pd.read_csv(arquivo)`.

            **7. Quais tratamentos são realizados nos dados?**

            O código remove espaços extras dos nomes das colunas, converte os anos para números quando possível e converte datas para o formato adequado. Também cria uma coluna interna para identificar o ano da análise e verifica valores ausentes e registros duplicados.

            **8. Por que é importante verificar a qualidade dos dados?**

            Porque valores ausentes, duplicados ou em formatos incorretos podem prejudicar os cálculos, os gráficos e a interpretação dos resultados.

            ### Aula 3 – Criar os gráficos

            **9. Quais gráficos foram criados no projeto?**

            Foram criados dois gráficos principais:

            - **Gráfico de linha:** apresenta a evolução histórica do indicador escolhido ao longo dos anos.
            - **Gráfico de barras:** apresenta a variação percentual do indicador em relação ao ano anterior, mostrando aumentos e reduções.

            O código também permite criar um gráfico adicional para comparar diferentes indicadores.

            **10. Qual é a importância desses gráficos?**

            O gráfico de linha facilita a visualização das tendências ao longo do tempo. Já o gráfico de barras permite identificar os anos em que o indicador aumentou, diminuiu ou permaneceu estável.

            **11. Quais indicadores numéricos são apresentados?**

            O dashboard apresenta o ano selecionado, a quantidade de registros, a soma ou média do indicador escolhido e a variação percentual em relação ao ano anterior disponível.

            **12. Como os gráficos foram criados?**

            Os gráficos foram desenvolvidos com a biblioteca Plotly Express, utilizando `px.line()` para o gráfico de linha e `px.bar()` para o gráfico de barras. A exibição é feita com `st.plotly_chart()`.

            ### Aula 4 – Transformar gráficos em informação

            **13. O que os gráficos mostram?**

            O gráfico de evolução histórica mostra como o indicador escolhido varia ao longo dos anos. O gráfico de variação percentual mostra a diferença entre o resultado de um ano e o do ano anterior.

            **14. Quais foram os principais resultados encontrados?**

            Os resultados dependem do arquivo CSV carregado no dashboard. Sem os dados, não é possível afirmar quais anos apresentaram os maiores valores ou os maiores aumentos e reduções.

            **15. Como explicar os gráficos em linguagem simples?**

            O gráfico de linha permite observar se o indicador da Nestlé aumentou, diminuiu ou permaneceu relativamente estável ao longo dos anos. O gráfico de barras complementa essa análise, mostrando a variação percentual entre períodos consecutivos.

            **16. Qual é a importância de não inventar causas para os resultados?**

            É importante porque os dados mostram valores e possíveis padrões, mas não comprovam, por si só, as causas das mudanças observadas. As conclusões devem ser baseadas nas informações disponíveis.

            ### Aula 5 – Validar e finalizar

            **17. Como o dashboard foi testado?**

            O código prevê o carregamento de um arquivo CSV, a visualização dos dados, a seleção de indicadores, a escolha do período de análise e a geração dos gráficos. Também verifica se existem dados válidos para realizar os cálculos. Para confirmar o funcionamento, é necessário executar a aplicação e testar essas funcionalidades com um CSV real.

            **18. Como a Inteligência Artificial ajudou no desenvolvimento?**

            A Inteligência Artificial pode ajudar a estruturar o código Python, sugerir gráficos adequados, identificar possíveis erros e explicar os resultados. Neste projeto, ela pode apoiar a criação do dashboard e a compreensão das funções utilizadas.

            **19. Qual foi o problema encontrado, qual prompt foi utilizado e qual foi a solução?**

            - **Problema:** desenvolver um dashboard capaz de analisar dados históricos e apresentar gráficos interativos.
            - **Prompt utilizado:** “Ajude-me a desenvolver um dashboard com Python, Pandas, Plotly e Streamlit para analisar dados históricos da Nestlé. Explique o código e sugira gráficos para visualizar a evolução anual e a variação percentual dos indicadores.”
            - **Sugestão da IA:** utilizar o Pandas para tratar os dados, o Plotly para criar os gráficos e o Streamlit para montar a aplicação.
            - **O que foi feito:** foi desenvolvido um código com upload de CSV, filtros, indicadores numéricos, gráficos históricos e verificações da qualidade dos dados.
            - **Como verificar:** executar a aplicação, carregar o arquivo CSV e conferir se os valores calculados correspondem aos dados originais.

            **Observação sobre a pergunta 19:** essa resposta descreve uma forma de registrar o uso da IA, não comprova que esse prompt específico tenha sido utilizado durante o desenvolvimento.

            **20. O que precisa ser corrigido ou melhorado no projeto?**

            O código já apresenta as funcionalidades principais, mas há alguns pontos que merecem atenção:

            - Informar a fonte original dos dados da Nestlé.
            - Testar o carregamento de diferentes arquivos CSV.
            - Verificar se as datas e os valores numéricos são interpretados corretamente.
            - Conferir se os gráficos e os cálculos correspondem aos dados originais.
            - Corrigir a mensagem de apresentação do terceiro bloco inicial, que está sem espaço entre as duas frases.

            ### Resumo para a apresentação oral

            **21. O que investigamos?**

            Investigamos a evolução histórica de indicadores da Nestlé, buscando compreender como seus valores mudam ao longo dos anos.

            **22. Qual base utilizamos?**

            Utilizamos um arquivo CSV com dados históricos da Nestlé. A fonte precisa ser identificada e confirmada.

            **23. O que os dados mostraram?**

            O dashboard foi desenvolvido para mostrar a evolução anual dos indicadores e as variações percentuais entre os anos. Os resultados específicos dependem dos dados carregados.

            **24. Onde a IA ajudou?**

            A IA auxiliou na elaboração do código, na organização dos dados, na criação dos gráficos e na identificação de possíveis melhorias na aplicação.
            """)

        st.divider()

        st.caption(
            "Histórico da Nestlé | Visualização baseada nos dados "
            "fornecidos pelo usuário. Os valores não representam "
            "necessariamente resultados financeiros oficiais."
        )
        st.markdown(
            "**Créditos:** Beatriz Neres · Mariana Marchiori · Luiza Romeiro · Monalisa Silva  \\n"
            "**Professor orientador:** Felipe Garbin"
        )

    except Exception as erro:
        st.error(f"Não foi possível analisar o arquivo: {erro}")

        st.info(
            "Confira o formato do CSV, os nomes das colunas, "
            "os tipos de dados e a existência de uma coluna de ano "
            "ou data e de ao menos um indicador numérico."
        )

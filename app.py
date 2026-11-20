import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da página e layout do Streamlit
st.set_page_config(
    page_title="Dashboard de Salários — Imersão Dados",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS customizado para garantir um visual elegante, limpo e profissional
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    div[data-testid="stMetric"] {
        background-color: #1e222b;
        padding: 15px 20px;
        border-radius: 10px;
        border: 1px solid #2e333d;
        text-align: center;
    }
    div[data-testid="stMetric"] label {
        color: #8a929e !important;
        font-size: 14px !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #00d48a !important;
        font-size: 28px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Carregamento dos dados com cacheamento para otimizar a performance
@st.cache_data(show_spinner=False)
def load_data():
    try:
        url = "https://raw.githubusercontent.com/guilhermeonrails/data-jobs/refs/heads/main/salaries.csv"
        df = pd.read_csv(url)

        # Processo de limpeza e formatação equivalente às aulas anteriores
        df = df.rename(columns={
            'work_year': 'ano',
            'experience_level': 'senioridade',
            'employment_type': 'contrato',
            'job_title': 'cargo',
            'salary': 'salario',
            'salary_currency': 'moeda',
            'salary_in_usd': 'usd',
            'employee_residence': 'residencia',
            'remote_ratio': 'remoto',
            'company_location': 'empresa',
            'company_size': 'tamanho_empresa'
        })

        df_limpo = df.dropna().copy()
        df_limpo['ano'] = df_limpo['ano'].astype('int64')
        df_limpo['salario'] = df_limpo['salario'].astype('float64')

        # Padronização de rótulos categóricos
        df_limpo['senioridade'] = df_limpo['senioridade'].replace({
            'SE': 'Senior',
            'MI': 'Pleno',
            'EN': 'Junior',
            'EX': 'Executivo'
        })
        df_limpo['contrato'] = df_limpo['contrato'].replace({
            'FT': 'Tempo Integral',
            'PT': 'Tempo Parcial',
            'FL': 'Freelancer',
            'CT': 'Contrato'
        })
        df_limpo['remoto'] = df_limpo['remoto'].replace({
            0: 'Presencial',
            50: 'Hibrido',
            100: 'Remoto'
        })
        return df_limpo
    except Exception as e:
        st.error(f"Erro ao conectar com a base de dados: {e}")
        return pd.DataFrame()

df = load_data()

# Título do Dashboard
st.title("💼 Análise Salarial de Profissionais da Área de Dados")
st.markdown("Este dashboard dinâmico foi construído para apresentar insights profissionais e visuais sobre a remuneração de profissionais da área de dados, desenvolvido como extensão de um estudo guiado da Imersão Dados com Python da Alura.")

if df.empty:
    st.warning("Nenhum dado pôde ser carregado. Verifique a conexão com o repositório original.")
else:
    # 3. Filtros interativos na barra lateral (Sidebar)
    st.sidebar.header("⚙️ Filtros de Pesquisa")

    anos_disponiveis = sorted(list(df['ano'].unique()))
    ano_selecionado = st.sidebar.multiselect("Selecione o(s) Ano(s)", options=anos_disponiveis, default=anos_disponiveis)

    cargos_disponiveis = sorted(list(df['cargo'].unique()))
    cargo_selecionado = st.sidebar.multiselect("Selecione o(s) Cargo(s)", options=cargos_disponiveis, default=[])

    senioridades_disponiveis = ['Junior', 'Pleno', 'Senior', 'Executivo']
    senioridade_selecionada = st.sidebar.multiselect("Selecione a(s) Senioridade(s)", options=senioridades_disponiveis, default=senioridades_disponiveis)

    modalidades_disponiveis = list(df['remoto'].unique())
    modalidade_selecionada = st.sidebar.multiselect("Selecione a(s) Modalidade(s)", options=modalidades_disponiveis, default=modalidades_disponiveis)

    # Filtragem progressiva do dataframe
    df_filtrado = df.copy()
    df_filtrado = df_filtrado[df_filtrado['ano'].isin(ano_selecionado)]
    if cargo_selecionado:
        df_filtrado = df_filtrado[df_filtrado['cargo'].isin(cargo_selecionado)]
    df_filtrado = df_filtrado[df_filtrado['senioridade'].isin(senioridade_selecionada)]
    df_filtrado = df_filtrado[df_filtrado['remoto'].isin(modalidade_selecionada)]

    # Prevenção de filtros vazios
    if df_filtrado.empty:
        st.warning("⚠️ Nenhum registro encontrado com a combinação de filtros selecionada.")
    else:
        # 4. Indicadores de Performance (KPIs)
        st.markdown("### 📈 Indicadores Gerais")
        col1, col2, col3, col4 = st.columns(4)

        media_salario = df_filtrado['usd'].mean()
        mediana_salario = df_filtrado['usd'].median()
        total_registros = len(df_filtrado)
        total_cargos = df_filtrado['cargo'].nunique()

        col1.metric("Salário Médio Anual", f"US$ {media_salario:,.2f}")
        col2.metric("Salário Mediano", f"US$ {mediana_salario:,.2f}")
        col3.metric("Registros Analisados", f"{total_registros:,}")
        col4.metric("Cargos Distintos", f"{total_cargos}")

        st.write("---")

        # 5. Visualizações gráficas interativas em seções
        st.markdown("### 📊 Visualizações e Distribuições")

        g_col1, g_col2 = st.columns(2)

        with g_col1:
            st.subheader("Salário Médio por Senioridade")
            ordem_senioridade = [s for s in ['Junior', 'Pleno', 'Senior', 'Executivo'] if s in df_filtrado['senioridade'].unique()]
            df_sen_media = df_filtrado.groupby('senioridade')['usd'].mean().reindex(ordem_senioridade).reset_index()
            fig_sen = px.bar(
                df_sen_media,
                x='senioridade',
                y='usd',
                labels={'senioridade': 'Senioridade', 'usd': 'Média Salarial (USD)'},
                color='senioridade',
                color_discrete_sequence=px.colors.sequential.Tealgrn,
                template='plotly_dark'
            )
            fig_sen.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig_sen, use_container_width=True)

        with g_col2:
            st.subheader("Top 10 Cargos mais Frequentes")
            top_cargos = df_filtrado['cargo'].value_counts().head(10).reset_index()
            top_cargos.columns = ['cargo', 'quantidade']
            fig_cargos = px.bar(
                top_cargos,
                y='cargo',
                x='quantidade',
                orientation='h',
                text='quantidade',
                color_discrete_sequence=['#8b83ee'],
                template='plotly_dark'
            )
            fig_cargos.update_traces(
                texttemplate='%{x:,.0f}',
                textposition='outside',
                cliponaxis=False,
                hovertemplate='<b>%{y}</b><br>Registros: %{x:,.0f}<extra></extra>'
            )
            fig_cargos.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                xaxis_title='Quantidade de registros',
                margin=dict(r=65),
                height=350,
                showlegend=False
            )
            st.plotly_chart(fig_cargos, use_container_width=True)

        g_col3, g_col4 = st.columns(2)

        with g_col3:
            st.subheader("Distribuição Salarial (Frequência)")
            fig_dist = px.histogram(
                df_filtrado,
                x='usd',
                nbins=40,
                color_discrete_sequence=['#00d48a'],
                marginal='box',
                template='plotly_dark'
            )
            fig_dist.update_layout(
                xaxis_title='Salário Anual em USD',
                yaxis_title='Frequência',
                height=350
            )
            st.plotly_chart(fig_dist, use_container_width=True)

        with g_col4:
            st.subheader("Proporção de Trabalho Remoto / Presencial")
            remoto_counts = df_filtrado['remoto'].value_counts().reset_index()
            remoto_counts.columns = ['tipo_trabalho', 'quantidade']
            remoto_counts['percentual'] = 100 * remoto_counts['quantidade'] / remoto_counts['quantidade'].sum()
            remoto_counts['legenda'] = remoto_counts.apply(
                lambda r: f"{r['tipo_trabalho']} — {r['percentual']:.1f}% ({int(r['quantidade']):,} registros)",
                axis=1
            )
            fig_pie = px.pie(
                remoto_counts,
                names='legenda',
                values='quantidade',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Prism,
                template='plotly_dark',
                custom_data=['tipo_trabalho', 'quantidade']
            )
            fig_pie.update_traces(
                textinfo='percent',
                textposition='inside',
                hovertemplate='<b>%{customdata[0]}</b><br>Registros: %{value:,.0f}<br>Percentual: %{percent}<extra></extra>'
            )
            fig_pie.update_layout(height=350, legend_title_text='Modalidade · % · registros')
            st.plotly_chart(fig_pie, use_container_width=True)

        # Comparação Salarial entre Países
        st.write("---")
        st.subheader("🌍 Média Salarial por Localidade da Empresa (Top 10 Países)")
        df_paises = df_filtrado.groupby('empresa')['usd'].agg(['mean', 'count']).reset_index()
        df_paises = df_paises[df_paises['count'] > 5].sort_values(by='mean', ascending=False).head(10)

        if not df_paises.empty:
            fig_paises = px.bar(
                df_paises,
                x='empresa',
                y='mean',
                hover_data=['count'],
                labels={'empresa': 'País da Empresa', 'mean': 'Salário Médio (USD)', 'count': 'Amostras'},
                color='mean',
                color_continuous_scale=px.colors.sequential.Viridis,
                template='plotly_dark'
            )
            fig_paises.update_layout(height=380)
            st.plotly_chart(fig_paises, use_container_width=True)
        else:
            st.info("Dados insuficientes de comparação para países com volume de amostras representativo nesta filtragem.")

        # 6. Exibição e exportação de dados em tabela
        st.write("---")
        st.markdown("### 🗄️ Detalhes dos Dados Filtrados")
        st.dataframe(df_filtrado, use_container_width=True)

        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar base filtrada como CSV",
            data=csv,
            file_name='salarios_dados_filtrados.csv',
            mime='text/csv',
        )


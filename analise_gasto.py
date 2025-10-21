#!/usr/bin/env python3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

plt.style.use('ggplot')


def limpar_dados(df: pd.DataFrame) -> pd.DataFrame:
    """Remove linhas com valores ausentes ou duplicados."""
    colunas_manter = ['Contas a Pagar', 'Valor', 'Pagamento', 'Status']
    df_limpo = df[colunas_manter].copy()

    df_limpo.dropna(subset=['Valor', 'Pagamento', 'Contas a Pagar'], inplace=True)

    df_limpo['Valor'] = pd.to_numeric(df_limpo['Valor'], errors='coerce')
    df_limpo.dropna(subset=['Valor'], inplace=True)

    df_limpo['Data de Pagamento'] = pd.to_datetime(df_limpo['Pagamento'], errors='coerce')
    df_limpo.dropna(subset=['Data de Pagamento'], inplace=True)

    df_limpo.drop(columns=['Pagamento', 'Status'], inplace=True)
    return df_limpo


def analisar_gastos_mensais(df_limpo: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    df_analise = df_limpo.copy()
    df_analise['MesAno'] = df_analise['Data de Pagamento'].dt.to_period('M')

    gastos_mensais = df_analise.groupby('MesAno')['Valor'].sum().sort_values(ascending=False).reset_index()
    gastos_mensais['MesAno'] = gastos_mensais['MesAno'].astype(str)
    gastos_mensais.rename(columns={'Valor': 'Gasto Total'}, inplace=True)

    maior_gasto_mes = gastos_mensais.iloc[0]['MesAno']
    return maior_gasto_mes, gastos_mensais


def analisar_itens_mais_caros(df_limpo: pd.DataFrame, top_n: int = 20) -> tuple[str, pd.DataFrame]:
    gastos_por_item = df_limpo.groupby('Contas a Pagar')['Valor'].sum().sort_values(ascending=False).reset_index()
    gastos_por_item.rename(columns={'Valor': 'Gasto Acumulado'}, inplace=True)
    item_mais_caro = gastos_por_item.iloc[0]['Contas a Pagar']
    return item_mais_caro, gastos_por_item.head(top_n)


def gerar_e_salvar_grafico(data: pd.DataFrame, x_col: str, y_col: str, titulo: str, nome_arquivo: str, is_horizontal: bool = False):
    caminho_pasta = 'image'
    os.makedirs(caminho_pasta, exist_ok=True)
    caminho_completo = os.path.join(caminho_pasta, f"{nome_arquivo}.png")

    fig, ax = plt.subplots(figsize=(10, 6))
    if is_horizontal:
        ax.barh(data[x_col], data[y_col], color='skyblue')
        ax.set_xlabel(y_col)
        ax.set_ylabel(x_col)
        ax.invert_yaxis()
    else:
        ax.bar(data[x_col], data[y_col], color='lightcoral')
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

    ax.set_title(titulo, fontsize=14, fontweight='bold')
    ax.grid(axis='y', linestyle='--')

    try:
        plt.savefig(caminho_completo, bbox_inches='tight')
        plt.close(fig)
    except Exception as e:
        print(f"Erro: Não foi possível salvar o gráfico em {caminho_completo}: {e}")


if __name__ == "__main__":
    file_name = "Contas_Pessoais.xlsx"
    try:
        df_original = pd.read_excel(file_name)
        df_analise = limpar_dados(df_original)
        assert not df_analise.empty, f"ERRO: O DataFrame resultante da limpeza está vazio. Verifique se há dados pagos em {file_name}."

        maior_mes, gastos_mensais_df = analisar_gastos_mensais(df_analise)
        item_mais_caro, top_itens_df = analisar_itens_mais_caros(df_analise, top_n=20)

        gerar_e_salvar_grafico(
            data=gastos_mensais_df.sort_values(by='MesAno'),
            x_col='MesAno',
            y_col='Gasto Total',
            titulo='Gasto Total Mensal (Apenas Contas Pagas)',
            nome_arquivo='gastos_mensais_totais'
        )

        gerar_e_salvar_grafico(
            data=top_itens_df,
            x_col='Contas a Pagar',
            y_col='Gasto Acumulado',
            titulo='Top 20 Contas Mais Caras (Gasto Acumulado)',
            nome_arquivo='top_20_contas_mais_caras',
            is_horizontal=True
        )

        print("\n--- Análise Concluída ---")
        print(f"O mês com o maior gasto total foi: {maior_mes}")
        print(f"O item com o maior gasto acumulado foi: {item_mais_caro}")
        print("Gráficos salvos na pasta 'image/'.\n")

    except FileNotFoundError:
        print(f"ERRO: O arquivo '{file_name}' não foi encontrado. Verifique o caminho e tente novamente.")
    except Exception as e:
        print(f"ERRO CRÍTICO no fluxo principal: {e}")

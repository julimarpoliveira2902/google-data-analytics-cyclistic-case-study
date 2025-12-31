
import pandas as pd
import glob
import os

# 1. Localizando os arquivos CSV na pasta
caminho_pasta = "dados_brutos"
arquivos_csv = glob.glob(os.path.join(caminho_pasta, "*.csv"))

print(f"Encontrados {len(arquivos_csv)} arquivos. Iniciando unificação...")

# 2. Lendo todos os arquivos e unindo-os em uma única tabela (DataFrame)
lista_df = [pd.read_csv(f) for f in arquivos_csv]
df_trips = pd.concat(lista_df, ignore_index=True)

# 3. Convertendo as colunas de tempo para o formato correto do Python
df_trips['started_at'] = pd.to_datetime(df_trips['started_at'])
df_trips['ended_at'] = pd.to_datetime(df_trips['ended_at'])

# 4. Criando a coluna 'ride_length' (Duração da viagem) [cite: 124]
# Calculando a diferença entre o fim e o início [cite: 125]
df_trips['ride_length'] = (df_trips['ended_at'] - df_trips['started_at']).dt.total_seconds()

# 5. Criando a coluna 'day_of_week' (Dia da semana) [cite: 126]
# O .dayofweek do Pandas retorna 0 para Segunda e 6 para Domingo
df_trips['day_of_week'] = df_trips['started_at'].dt.dayofweek + 1

# 6. Limpeza de dados (Fase de Processamento) [cite: 104, 151]
# Removendo viagens com duração negativa ou igual a zero (erros de sistema)
df_limpo = df_trips[df_trips['ride_length'] > 0].copy()

print("\n" + "="*50)
print("RELATÓRIO DE PROCESSAMENTO")
print("="*50)
print(f"Total de registros brutos: {len(df_trips)}")
print(f"Total de registros limpos: {len(df_limpo)}")
print(f"Registros inválidos removidos: {len(df_trips) - len(df_limpo)}")
print("\nPrimeiras linhas da tabela final:")
print(df_limpo[['ride_id', 'member_casual', 'ride_length', 'day_of_week']].head())

# --- CONTINUAÇÃO ANÁLISE ESTATÍSTICA ---

print("\n" + "="*50)
print("ANÁLISE DESCRITIVA: MEMBROS VS CASUAIS")
print("="*50)

# 1. Calculando a média de duração da viagem (em segundos)
# O groupby separa os dados entre membros e casuais
media_viagem = df_limpo.groupby('member_casual')['ride_length'].mean()
print("Duração Média da Viagem (em segundos):")
print(media_viagem)

# 2. Calculando o dia da semana mais frequente (Moda)
# Isso nos diz em qual dia cada grupo mais usa a bicicleta
dia_favorito = df_limpo.groupby('member_casual')['day_of_week'].agg(lambda x: x.mode().iloc[0])
print("\nDia da Semana Favorito (1=Dom, 7=Sáb):")
print(dia_favorito)

# 3. Contando o total de viagens para cada tipo
total_viagens = df_limpo['member_casual'].value_counts()
print("\nVolume Total de Viagens:")
print(total_viagens)

import matplotlib.pyplot as plt

# --- VISUALIZAÇÃO (SHARE) ---

# --- PREPARANDO OS DADOS PARA O GRÁFICO 1 (Duração Média) ---
resumo_duracao = df_limpo.groupby('member_casual')['ride_length'].mean() / 60 # Convertendo para minutos
categorias = resumo_duracao.index # 'casual' e 'member'
valores = resumo_duracao.values

# --- CRIANDO O COMBO DE GRÁFICOS (Duração + Volume) ---
print("\nGerando imagem final de portfólio... Aguarde.")
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))

# 1. GRÁFICO DE CIMA: Duração Média
ax1.bar(categorias, valores, color=['orange', 'blue'])
ax1.set_title('Duração Média das Viagens (Minutos)', fontsize=14, fontweight='bold')
ax1.set_ylabel('Minutos')

# 2. GRÁFICO DE BAIXO: Volume Semanal
# Criando a tabela para o gráfico de barras agrupadas
volume_semanal = df_limpo.groupby(['day_of_week', 'member_casual']).size().unstack()
volume_semanal.plot(kind='bar', ax=ax2, color=['orange', 'blue'], width=0.8)
ax2.set_title('Volume Total de Viagens por Dia da Semana', fontsize=14, fontweight='bold')
ax2.set_ylabel('Número de Viagens (em milhões)')
ax2.set_xticklabels(['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'], rotation=0)
ax2.legend(title='Tipo de Usuário')

# Ajustes de layout
plt.tight_layout(pad=5.0)

# SALVAMENTO FINAL
plt.savefig('analise_completa_cyclistic.png', dpi=300, bbox_inches='tight')
print("Sucesso! Imagem 'analise_completa_cyclistic.png' salva na pasta do projeto.")

plt.show()

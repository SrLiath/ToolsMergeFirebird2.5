# import fdb

# # Conexão com o banco de dados
# con = fdb.connect(
#     dsn='C:\\Users\\guima\\jojo\\ToolsMergeFirebird2.5\\filho.gdb',
#     user='SYSDBA',
#     password='masterkey',
#     charset='NONE'
# )

# # Obtém o cursor
# cur = con.cursor()

# # Nome do arquivo de saída
# output_file = 'inserts.sql'

# # Abre o arquivo para escrita
# with open(output_file, 'w') as f:

#     # Obtém uma lista de todas as tabelas, excluindo aquelas que começam com 'RDB$'
#     cur.execute("SELECT rdb$relation_name FROM rdb$relations WHERE rdb$view_blr IS NULL AND NOT rdb$relation_name STARTING WITH 'RDB$'")
#     tables = [row[0] for row in cur.fetchall()]

#     # Itera sobre todas as tabelas
#     for table_name in tables:

#         # Obtém as informações sobre as colunas da tabela na ordem correta
#         cur.execute(f"SELECT RDB$FIELD_NAME as COLUMN_NAME FROM RDB$RELATION_FIELDS WHERE RDB$RELATION_NAME = '{table_name}' ORDER BY RDB$FIELD_POSITION")
#         column_names = [row[0] for row in cur.fetchall()]

#         # Monta a instrução SQL para inserção
#         for row in cur.execute(f"SELECT * FROM {table_name}"):
#             values_dict = {col_name: value for col_name, value in zip(column_names, row)}
#             insert_sql = f'INSERT INTO {table_name} ({", ".join(column_names)}) VALUES ({", ".join([str(values_dict[col]) if values_dict[col] is not None else "NULL" for col in column_names])});\n'
#             f.write(insert_sql)

#             # Mostra o conteúdo da tabela
#             print(f'Conteúdo da tabela {table_name}:')
#             for column, value in values_dict.items():
#                 print(f'{column}: {value}')

# # Fecha a conexão com o banco de dados
# con.close()

# print(f'Arquivo {output_file} gerado com sucesso.')


######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
######################################################################################################################################

def repor_valor(trecho_sql, campo, valor_inicial, arquivo_saida):
    # Encontrar todas as instâncias do padrão INSERT INTO (...) VALUES (...);
    matches = re.finditer(r"INSERT INTO (\w+) \(([^)]+)\) VALUES \(([^)]+)\);", trecho_sql)

    novo_trecho_sql = ""

    with open(arquivo_saida, 'w') as f_out:
        for match in matches:
            tabela = match.group(1)
            campos = match.group(2).split(', ')
            valores = match.group(3).split(', ')

            if campo in campos:
                indice_campo = campos.index(campo)
                valores_substituidos = [str(valor_inicial) if i == indice_campo else valor for i, valor in enumerate(valores)]
                valor_inicial += 1

                nova_linha = f"INSERT INTO {tabela} ({', '.join(campos)}) VALUES ({', '.join(valores_substituidos)});\n"
                novo_trecho_sql += nova_linha

                # Salvar substituições no arquivo
                f_out.write(f"{valores[indice_campo]} = {valores_substituidos[indice_campo]}\n")

    return novo_trecho_sql

def processar_arquivo_sql(arquivo_entrada, campo, valor_inicial):
    with open(arquivo_entrada, 'r') as f_in:
        trecho_sql = f_in.read()

    novo_trecho_sql = repor_valor(trecho_sql, campo, valor_inicial, f'ids//{campo}.txt')

    # Adicionar ao final do arquivo SQL os valores que não contêm o campo 'id'
    sem_id_matches = re.finditer(r"INSERT INTO (\w+) \(([^)]+)\) VALUES \(([^)]+)\);", trecho_sql)
    sem_id_valores = []

    for match in sem_id_matches:
        tabela = match.group(1)
        campos = match.group(2).split(', ')

        if campo not in campos:
            sem_id_valores.append(match.group())

    if sem_id_valores:
        novo_trecho_sql += '\n----------\n'.join(sem_id_valores) + '\n'

    with open(arquivo_entrada, 'w') as f_in:
        f_in.write(novo_trecho_sql)

# ESPECIFICAÇÂO MANUAL
# arquivo_sql = 'teste.sql'
# campo_substituir = 'id'
# valor_inicial = 10

# processar_arquivo_sql(arquivo_sql, campo_substituir, valor_inicial)

# ######################################################################################################################################
# ######################################################################################################################################
# ######################################################################################################################################
# ######################################################################################################################################



# def repor_valor2(trecho_sql, campo, valor_substituir):
#     # Encontrar todas as instâncias do padrão INSERT INTO (...) VALUES (...);
#     matches = re.finditer(r"INSERT INTO (\w+) \(([^)]+)\) VALUES \(([^)]+)\);", trecho_sql)

#     novo_trecho_sql = ""

#     for match in matches:
#         tabela = match.group(1)
#         campos = match.group(2).split(', ')
#         valores = match.group(3).split(', ')

#         if campo in campos:
#             indice_campo = campos.index(campo)
#             valores[indice_campo] = valor_substituir

#         nova_linha = f"INSERT INTO {tabela} ({', '.join(campos)}) VALUES ({', '.join(valores)});\n"
#         novo_trecho_sql += nova_linha

#     return novo_trecho_sql

# def aplicar_substituicoes(pasta_ids, pasta_tables, linhas_consecutivas_sem_coluna=5):
#     for arquivo_id in os.listdir(pasta_ids):
#         if arquivo_id.endswith(".txt"):
#             caminho_id = os.path.join(pasta_ids, arquivo_id)

#             with open(caminho_id, 'r') as f_id:
#                 linhas_id = f_id.readlines()

#             campo = linhas_id[0].split(' = ')[0]
#             valor_substituir = linhas_id[-1].split(' = ')[1].strip()

#             contagem_sem_coluna = 0

#             for arquivo_table in os.listdir(pasta_tables):
#                 if arquivo_table.endswith(".sql"):
#                     caminho_table = os.path.join(pasta_tables, arquivo_table)

#                     with open(caminho_table, 'r') as f_table:
#                         trecho_sql = f_table.read()

#                     novo_trecho_sql = repor_valor2(trecho_sql, campo, valor_substituir)

#                     with open(caminho_table, 'w') as f_table:
#                         f_table.write(novo_trecho_sql)

#                     if campo not in trecho_sql:
#                         contagem_sem_coluna += 1
#                     else:
#                         contagem_sem_coluna = 0

#                     if contagem_sem_coluna >= linhas_consecutivas_sem_coluna:
#                         break

# # Replaces generalizado
# # pasta_ids = 'ids'
# # pasta_tables = 'tables'

# # aplicar_substituicoes(pasta_ids, pasta_tables)

# ######################################################################################################################################
# ######################################################################################################################################
# ######################################################################################################################################
# ######################################################################################################################################


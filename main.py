import re
import os
import fdb

# Substitua pelos seus próprios detalhes de conexão
database = 'pai.gdb'
user = 'SYSDBA'
password = 'masterkey'

# Conecte-se ao banco de dados local (não é necessário o parâmetro "host")
con = fdb.connect(dsn=database, user=user, password=password)

# Crie um diretório para armazenar os arquivos de especificação
output_folder = 'tables'
os.makedirs(output_folder, exist_ok=True)

# Obtenha informações sobre as tabelas no banco de dados
cursor = con.cursor()
cursor.execute("SELECT rdb$relation_name FROM rdb$relations WHERE rdb$view_blr IS NULL")
tables = cursor.fetchall()

for table in tables:
    table_name = table[0]
    output_file = os.path.join(output_folder, f"{table_name}_especificacao.sql")

    with open(output_file, 'w') as file:
        file.write(f"CREATE TABLE {table_name} (\n")

        # Obtenha informações sobre os campos da tabela com tipos
        cursor.execute("""
            SELECT
              TRIM(rf.rdb$field_name) || ' ' ||
              IIF(rdb$field_source LIKE 'RDB$%',
                DECODE(f.rdb$field_type, 
                  7,  'SMALLINT',
                  8,  'INTEGER',
                  9,  'QUAD',
                  10, 'FLOAT',
                  11, 'D_FLOAT',
                  12, 'DATE',
                  13, 'TIME',
                  14, 'CHAR',
                  16, 'INT64',
                  27, 'DOUBLE',
                  35, 'TIMESTAMP',
                  37, 'VARCHAR',
                  40, 'CSTRING',
                  261, 'BLOB',
                  'UNKNOWN'
                ),
                TRIM(rdb$field_source)) ||
              IIF((rdb$field_source LIKE 'RDB$%') AND (f.rdb$field_type IN (37, 14)),
                '(' || f.rdb$field_length || ')',
                '') ||
              IIF((f.rdb$null_flag = 1) OR (rf.rdb$null_flag = 1), 
                ' NOT NULL', '')
            FROM
              rdb$relation_fields rf JOIN rdb$fields f
                ON f.rdb$field_name = rf.rdb$field_source
            WHERE
              rf.rdb$relation_name = ?""", (table_name,))
        
        fields = cursor.fetchall()

        for i, field_spec in enumerate(fields):
            file.write(f"  {field_spec[0]}")
            if i < len(fields) - 1:
                file.write(",\n")
            else:
                file.write("\n")

        file.write(");\n")

# Feche a conexão com o banco de dados
con.close()

print(f"Especificações das tabelas escritas na pasta {output_folder}")

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

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
######################################################################################################################################



def repor_valor2(trecho_sql, campo, valor_substituir):
    # Encontrar todas as instâncias do padrão INSERT INTO (...) VALUES (...);
    matches = re.finditer(r"INSERT INTO (\w+) \(([^)]+)\) VALUES \(([^)]+)\);", trecho_sql)

    novo_trecho_sql = ""

    for match in matches:
        tabela = match.group(1)
        campos = match.group(2).split(', ')
        valores = match.group(3).split(', ')

        if campo in campos:
            indice_campo = campos.index(campo)
            valores[indice_campo] = valor_substituir

        nova_linha = f"INSERT INTO {tabela} ({', '.join(campos)}) VALUES ({', '.join(valores)});\n"
        novo_trecho_sql += nova_linha

    return novo_trecho_sql

def aplicar_substituicoes(pasta_ids, pasta_tables, linhas_consecutivas_sem_coluna=5):
    for arquivo_id in os.listdir(pasta_ids):
        if arquivo_id.endswith(".txt"):
            caminho_id = os.path.join(pasta_ids, arquivo_id)

            with open(caminho_id, 'r') as f_id:
                linhas_id = f_id.readlines()

            campo = linhas_id[0].split(' = ')[0]
            valor_substituir = linhas_id[-1].split(' = ')[1].strip()

            contagem_sem_coluna = 0

            for arquivo_table in os.listdir(pasta_tables):
                if arquivo_table.endswith(".sql"):
                    caminho_table = os.path.join(pasta_tables, arquivo_table)

                    with open(caminho_table, 'r') as f_table:
                        trecho_sql = f_table.read()

                    novo_trecho_sql = repor_valor2(trecho_sql, campo, valor_substituir)

                    with open(caminho_table, 'w') as f_table:
                        f_table.write(novo_trecho_sql)

                    if campo not in trecho_sql:
                        contagem_sem_coluna += 1
                    else:
                        contagem_sem_coluna = 0

                    if contagem_sem_coluna >= linhas_consecutivas_sem_coluna:
                        break

# Replaces generalizado
# pasta_ids = 'ids'
# pasta_tables = 'tables'

# aplicar_substituicoes(pasta_ids, pasta_tables)

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
######################################################################################################################################


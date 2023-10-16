import fdb

# Conexão com o banco de dados
con = fdb.connect(
    dsn='pai.gdb',
    user='SYSDBA',
    password='masterkey',
    charset='NONE'
)

# Obtém o cursor
cur = con.cursor()

# Nome do arquivo de saída
output_file = 'inserts.sql'

# Abre o arquivo para escrita
with open(output_file, 'w') as f:

    # Obtém uma lista de todas as tabelas, excluindo aquelas que começam com 'RDB$'
    cur.execute("SELECT rdb$relation_name FROM rdb$relations WHERE rdb$view_blr IS NULL AND NOT rdb$relation_name STARTING WITH 'RDB$'")
    tables = [row[0] for row in cur.fetchall()]

    # Itera sobre todas as tabelas
    for table_name in tables:

        # Obtém as informações sobre as colunas da tabela na ordem correta
        cur.execute(f"SELECT RDB$FIELD_NAME as COLUMN_NAME FROM RDB$RELATION_FIELDS WHERE RDB$RELATION_NAME = '{table_name}' ORDER BY RDB$FIELD_POSITION")
        column_names = [row[0] for row in cur.fetchall()]

        # Monta a instrução SQL para inserção
        for row in cur.execute(f"SELECT * FROM {table_name}"):
            values_dict = {col_name: value for col_name, value in zip(column_names, row)}
            insert_sql = f'INSERT INTO {table_name} ({", ".join(column_names)}) VALUES ({", ".join([str(values_dict[col]) if values_dict[col] is not None else "NULL" for col in column_names])});\n'
            f.write(insert_sql)

            # Mostra o conteúdo da tabela
            print(f'Conteúdo da tabela {table_name}:')
            for column, value in values_dict.items():
                print(f'{column}: {value}')

# Fecha a conexão com o banco de dados
con.close()

print(f'Arquivo {output_file} gerado com sucesso.')

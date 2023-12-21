import fdb

# Conexão com o banco de dados
con = fdb.connect(
    dsn='CONVERTPAI.GDB',
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
        cur.execute("""
            SELECT
                RF.RDB$FIELD_NAME FIELD_NAME,
                CASE F.RDB$FIELD_TYPE
                    WHEN 7 THEN
                        CASE F.RDB$FIELD_SUB_TYPE
                            WHEN 0 THEN 'SMALLINT'
                            WHEN 1 THEN 'NUMERIC(' || F.RDB$FIELD_PRECISION || ', ' || (-F.RDB$FIELD_SCALE) || ')'
                            WHEN 2 THEN 'DECIMAL'
                        END
                    WHEN 8 THEN
                        CASE F.RDB$FIELD_SUB_TYPE
                            WHEN 0 THEN 'INTEGER'
                            WHEN 1 THEN 'NUMERIC('  || F.RDB$FIELD_PRECISION || ', ' || (-F.RDB$FIELD_SCALE) || ')'
                            WHEN 2 THEN 'DECIMAL'
                        END
                    WHEN 9 THEN 'QUAD'
                    WHEN 10 THEN 'FLOAT'
                    WHEN 12 THEN 'DATE'
                    WHEN 13 THEN 'TIME'
                    WHEN 14 THEN 'CHAR(' || F.RDB$FIELD_LENGTH || ')'
                    WHEN 16 THEN
                        CASE F.RDB$FIELD_SUB_TYPE
                            WHEN 0 THEN 'BIGINT'
                            WHEN 1 THEN 'NUMERIC(' || F.RDB$FIELD_PRECISION || ', ' || (-F.RDB$FIELD_SCALE) || ')'
                            WHEN 2 THEN 'DECIMAL'
                        END
                    WHEN 27 THEN 'DOUBLE'
                    WHEN 35 THEN 'TIMESTAMP'
                    WHEN 37 THEN 'VARCHAR(' || F.RDB$FIELD_LENGTH || ')'
                    WHEN 40 THEN 'CSTRING' || F.RDB$FIELD_LENGTH || ')'
                    WHEN 45 THEN 'BLOB_ID'
                    WHEN 261 THEN 'BLOB SUB_TYPE ' || F.RDB$FIELD_SUB_TYPE
                    ELSE 'RDB$FIELD_TYPE: ' || F.RDB$FIELD_TYPE || '?'
                END FIELD_TYPE,
                IIF(COALESCE(RF.RDB$NULL_FLAG, 0) = 0, NULL, 'NOT NULL') FIELD_NULL,
                CH.RDB$CHARACTER_SET_NAME FIELD_CHARSET,
                DCO.RDB$COLLATION_NAME FIELD_COLLATION,
                COALESCE(RF.RDB$DEFAULT_SOURCE, F.RDB$DEFAULT_SOURCE) FIELD_DEFAULT,
                F.RDB$VALIDATION_SOURCE FIELD_CHECK,
                RF.RDB$DESCRIPTION FIELD_DESCRIPTION
            FROM RDB$RELATION_FIELDS RF
            JOIN RDB$FIELDS F ON (F.RDB$FIELD_NAME = RF.RDB$FIELD_SOURCE)
            LEFT OUTER JOIN RDB$CHARACTER_SETS CH ON (CH.RDB$CHARACTER_SET_ID = F.RDB$CHARACTER_SET_ID)
            LEFT OUTER JOIN RDB$COLLATIONS DCO ON ((DCO.RDB$COLLATION_ID = F.RDB$COLLATION_ID) AND (DCO.RDB$CHARACTER_SET_ID = F.RDB$CHARACTER_SET_ID))
            WHERE (RF.RDB$RELATION_NAME = ?) AND (COALESCE(RF.RDB$SYSTEM_FLAG, 0) = 0)
            ORDER BY RF.RDB$FIELD_POSITION
        """, (table_name,))

        columns_info = cur.fetchall()
        column_names = [row[0] for row in columns_info]
        column_types = {row[0]: row[1] for row in columns_info}

        # Monta a instrução SQL para inserção
        for row in cur.execute(f"SELECT * FROM {table_name}"):
            values_dict = {col_name: value for col_name, value in zip(column_names, row)}
            formatted_values = []

            for col_name in column_names:
                value = values_dict[col_name]

                # Adiciona aspas para strings ou date
                if value is not None and "CHAR" in column_types[col_name]:
                    formatted_values.append(f"'{value}'")
                elif value is not None and "VARCHAR" in column_types[col_name]:
                    formatted_values.append(f"'{value}'")
                elif value is not None and "TIME" in column_types[col_name]:
                    formatted_values.append(f"'{value}'")
                elif value is not None and "DATE" in column_types[col_name]:
                    formatted_values.append(f"'{value}'")
                elif value is not None and "TIMESTAMP" in column_types[col_name]:
                    formatted_values.append(f"'{value}'")
                else:
                    formatted_values.append(str(value) if value is not None else "NULL")

            insert_sql = f'INSERT INTO {table_name} ({", ".join(column_names)}) VALUES ({", ".join(formatted_values)});\n'
            f.write(insert_sql)

            # Mostra o conteúdo da tabela
            print(f'Conteúdo da tabela {table_name}:')
            for column, value in values_dict.items():
                print(f'{column}: {value}')

# Fecha a conexão com o banco de dados
con.close()

print(f'Arquivo {output_file} gerado com sucesso.')

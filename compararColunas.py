import fdb

# Substitua pelos seus próprios detalhes de conexão para o primeiro banco
database1 = 'filho.gdb'
user1 = 'SYSDBA'
password1 = 'masterkey'

# Substitua pelos seus próprios detalhes de conexão para o segundo banco
database2 = 'pai.gdb'
user2 = 'SYSDBA'
password2 = 'masterkey'

# Mapeamento de códigos de tipo para nomes de tipo legíveis
type_mapping = {
    7: 'SMALLINT',
    8: 'INTEGER',
    9: 'QUAD',
    10: 'FLOAT',
    11: 'D_FLOAT',
    12: 'DATE',
    13: 'TIME',
    14: 'CHAR',
    16: 'INT64',
    27: 'DOUBLE',
    35: 'TIMESTAMP',
    37: 'VARCHAR',
    40: 'CSTRING',
    261: 'BLOB'
}

# Conecte-se ao primeiro banco de dados
con1 = fdb.connect(dsn=database1, user=user1, password=password1)

# Conecte-se ao segundo banco de dados
con2 = fdb.connect(dsn=database2, user=user2, password=password2)

# Obtenha informações sobre as tabelas no primeiro banco de dados
cursor1 = con1.cursor()
cursor1.execute("SELECT rdb$relation_name FROM rdb$relations WHERE rdb$view_blr IS NULL")
tables1 = [table[0] for table in cursor1.fetchall()]

# Obtenha informações sobre as tabelas no segundo banco de dados
cursor2 = con2.cursor()
cursor2.execute("SELECT rdb$relation_name FROM rdb$relations WHERE rdb$view_blr IS NULL")
tables2 = [table[0] for table in cursor2.fetchall()]

# Compare as tabelas entre os dois bancos de dados
for table in set(tables1):
    if table not in tables2:
        print(f"Tabela '{table}' existe apenas no primeiro banco")

for table in set(tables2):
    if table not in tables1:
        print(f"Tabela '{table}' existe apenas no segundo banco")

# Compare as colunas em tabelas comuns
common_tables = set(tables1) & set(tables2)

for table in common_tables:
    # Obtenha informações sobre as colunas da tabela no primeiro banco
    cursor1.execute(f"""
        SELECT
            rf.rdb$field_name,
            f.rdb$field_type,
            f.rdb$field_length,
            rf.rdb$null_flag
        FROM
            rdb$relation_fields rf
        JOIN
            rdb$fields f ON f.rdb$field_name = rf.rdb$field_source
        WHERE
            rf.rdb$relation_name = ?
    """, (table,))
    columns1 = {column[0]: (type_mapping.get(column[1], 'Unknown'), column[2], column[3] == 1) for column in cursor1.fetchall()}

    # Obtenha informações sobre as colunas da tabela no segundo banco
    cursor2.execute(f"""
        SELECT
            rf.rdb$field_name,
            f.rdb$field_type,
            f.rdb$field_length,
            rf.rdb$null_flag
        FROM
            rdb$relation_fields rf
        JOIN
            rdb$fields f ON f.rdb$field_name = rf.rdb$field_source
        WHERE
            rf.rdb$relation_name = ?
    """, (table,))
    columns2 = {column[0]: (type_mapping.get(column[1], 'Unknown'), column[2], column[3] == 1) for column in cursor2.fetchall()}

    # Compare as colunas entre os dois bancos de dados
    for column in set(columns1.keys()) | set(columns2.keys()):
        column1 = columns1.get(column)
        column2 = columns2.get(column)

        if column1 != column2:
            if column1 is None:
                print(f"Coluna '{column}' na tabela '{table}' existe apenas no segundo banco")
            elif column2 is None:
                print(f"Coluna '{column}' na tabela '{table}' existe apenas no primeiro banco")
            else:
                column1_type, column1_length, column1_not_null = column1
                column2_type, column2_length, column2_not_null = column2

                if not column1_not_null:
                    print(f"Coluna '{column}' na tabela '{table}' no primeiro banco não é NOT NULL")
                if not column2_not_null:
                    print(f"Coluna '{column}' na tabela '{table}' no segundo banco não é NOT NULL")

                if (column1_type, column1_length) != (column2_type, column2_length):
                    print(f"Diferença na coluna '{column}' da tabela '{table}':")
                    print(f"No primeiro banco: {column1_type}, {column1_length}")
                    print(f"No segundo banco: {column2_type}, {column2_length}")

# Feche as conexões com os bancos de dados
con1.close()
con2.close()

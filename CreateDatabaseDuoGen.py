import fdb

# Substitua pelos seus próprios detalhes de conexão para o primeiro e segundo bancos
database1 = 'filho.gdb'
user1 = 'SYSDBA'
password1 = 'masterkey'

database2 = 'pai.gdb'
user2 = 'SYSDBA'
password2 = 'masterkey'

# Conecte-se ao primeiro banco de dados local (não é necessário o parâmetro "host")
con1 = fdb.connect(dsn=database1, user=user1, password=password1)

# Conecte-se ao segundo banco de dados local (não é necessário o parâmetro "host")
con2 = fdb.connect(dsn=database2, user=user2, password=password2)

# Crie um arquivo para gravar a especificação combinada
output_file = 'especificacao_banco_combinada.sql'

with open(output_file, 'w') as file:
    # Obtenha informações sobre as tabelas no primeiro banco de dados
    cursor1 = con1.cursor()
    cursor1.execute("SELECT rdb$relation_name FROM rdb$relations WHERE rdb$view_blr IS NULL")
    tables1 = cursor1.fetchall()

    # Crie um conjunto para rastrear as tabelas existentes
    existing_tables = set()

    for table in tables1:
        table_name = table[0]
        file.write(f"CREATE TABLE {table_name} (\n")

        # Obtenha informações sobre os campos da tabela com tipos do primeiro banco
        cursor1.execute("""
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

        fields = cursor1.fetchall()

        for i, field_spec in enumerate(fields):
            file.write(f"  {field_spec[0]}")
            if i < len(fields) - 1:
                file.write(",\n")
            else:
                file.write("\n")

        file.write(");\n")

        existing_tables.add(table_name)

    # Obtenha informações sobre as tabelas no segundo banco de dados
    cursor2 = con2.cursor()
    cursor2.execute("SELECT rdb$relation_name FROM rdb$relations WHERE rdb$view_blr IS NULL")
    tables2 = cursor2.fetchall()

    for table in tables2:
        table_name = table[0]
        if table_name not in existing_tables:
            file.write(f"CREATE TABLE {table_name} (\n")

            # Obtenha informações sobre os campos da tabela com tipos do segundo banco
            cursor2.execute("""
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

            fields = cursor2.fetchall()

            for i, field_spec in enumerate(fields):
                file.write(f"  {field_spec[0]}")
                if i < len(fields) - 1:
                    file.write(",\n")
                else:
                    file.write("\n")

            file.write(");\n")

# Feche as conexões com os bancos de dados
con1.close()
con2.close()

print(f"Especificação dos bancos combinada e escrita em {output_file}")

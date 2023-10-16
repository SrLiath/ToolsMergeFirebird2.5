import fdb


# Crie um arquivo para gravar as especificações
output_file = 'especificacao_banco.txt'
# Substitua pelos seus próprios detalhes de conexão
database = '../neto.gdb'
user = 'SYSDBA'
password = 'masterkey'

# Conecte-se ao banco de dados local (não é necessário o parâmetro "host")
con = fdb.connect(dsn=database, user=user, password=password)
with open(output_file, 'w') as file:
    # Obtenha informações sobre as tabelas no banco de dados
    cursor = con.cursor()
    cursor.execute("SELECT rdb$relation_name FROM rdb$relations WHERE rdb$view_blr IS NULL")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        file.write(f"Tabela: {table_name}\n")

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
                  261, 'BLOB'),
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

        for field_spec in fields:
            file.write(f"  Campo: {field_spec[0]}\n")

# Feche a conexão com o banco de dados
con.close()

print(f"Especificação do banco escrita em {output_file}")

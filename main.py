import fdb

# Configuração do banco de dados
database_path = 'dataficha.gdb'
user = 'SYSDBA'
password = 'masterkey'
charset = 'NONE'

# Arquivo SQL de entrada
sql_file_path = 'newOrder.sql'

# Arquivo para armazenar os erros
errors_file_path = 'erros.txt'

def execute_sql(sql, line_number):
    try:
        # Conecta ao banco de dados
        con = fdb.connect(dsn=database_path, user=user, password=password, charset=charset)
        cur = con.cursor()

        # Executa o SQL
        cur.execute(sql)

        # Comita as alterações
        con.commit()

        # Fecha a conexão
        con.close()

    except fdb.Error as e:
        # Grava o erro no arquivo de erros junto com a linha
        with open(errors_file_path, 'a') as errors_file:
            errors_file.write(f"Linha {line_number}: {sql}\n")
            errors_file.write(f"Descrição do erro: {e}\n\n")

if __name__ == '__main__':
    # Lê o arquivo SQL e executa cada linha
    with open(sql_file_path, 'r') as sql_file:
        sql_lines = sql_file.readlines()

        for line_number, line in enumerate(sql_lines, start=1):
            # Remove espaços em branco e quebras de linha
            sql_line = line.strip()

            # Executa a SQL
            execute_sql(sql_line, line_number)

    print("Execução concluída. Verifique o arquivo de erros se houver problemas.")

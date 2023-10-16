import fdb

# Defina as informações de conexão para os dois bancos de dados
# Defina as informações de conexão para os dois bancos de dados
dsn1 = 'filho.gdb'
dsn2 = 'PAI.GDB'
user = 'SYSDBA'
password = 'masterkey'

# Função para obter as tabelas de um banco de dados
def obter_tabelas(dsn):
    try:
        con = fdb.connect(dsn=dsn, user=user, password=password)
        cursor = con.cursor()
        cursor.execute("SELECT rdb$relation_name FROM rdb$relations WHERE rdb$view_blr IS NULL AND (rdb$system_flag IS NULL OR rdb$system_flag = 0)")
        tabelas = [row[0] for row in cursor.fetchall()]
        cursor.close()
        con.close()
        return tabelas
    except fdb.Error as e:
        print(f"Erro ao conectar ao banco de dados {dsn}: {e}")
        return []

# Obtenha a lista de tabelas para ambos os bancos de dados
tabelas_banco1 = obter_tabelas(dsn1)
tabelas_banco2 = obter_tabelas(dsn2)

# Determine as tabelas em comum
tabelas_comuns = set(tabelas_banco1) & set(tabelas_banco2)

# Exiba as relações entre as tabelas
for tabela in tabelas_comuns:
    print(f"{tabela} <-> {tabela}")

for tabela in list(set(tabelas_banco1) - tabelas_comuns):
    print(f"{tabela} -> new")

for tabela in list(set(tabelas_banco2) - tabelas_comuns):
    print(f"new <- {tabela}")

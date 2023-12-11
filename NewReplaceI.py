import re

def alterar(nome_arquivo, coluna_desejada, novo_numero, arquivo_novo):
    linhas_modificadas = []
    contador = novo_numero
    mapeamento_valores = {}

    with open(nome_arquivo, 'r') as arquivo:
        for linha in arquivo:
            # Encontrar as colunas e valores
            match = re.search(r"INSERT INTO ([\w\s]+)\(([^)]+)\) VALUES \(([^)]+)\);", linha)
            if match:
                tabela_original = match.group(1)
                colunas = match.group(2).split(', ')
                valores_brutos = match.group(3).split(',')

                # Processar os valores para lidar com vírgulas dentro de aspas ou apóstrofos
                valores = []
                valor_temporario = ''
                dentro_aspas = False

                for valor_bruto in valores_brutos:
                    valor_temporario += valor_bruto
                    dentro_aspas = not dentro_aspas if valor_bruto.count('"') % 2 == 1 else dentro_aspas
                    dentro_aspas = not dentro_aspas if valor_bruto.count("'") % 2 == 1 else dentro_aspas

                    if not dentro_aspas:
                        valores.append(valor_temporario.strip())
                        valor_temporario = ''

                # Encontrar a posição da coluna desejada
                if coluna_desejada in colunas:
                    posicao_coluna = colunas.index(coluna_desejada)

                    # Verificar se a posição existe nos valores
                    if posicao_coluna < len(valores):
                        valor_antigo = valores[posicao_coluna]
                        valor_novo = str(contador)

                        # Substituir o valor na posição específica
                        valores[posicao_coluna] = valor_novo

                        # Incrementar o contador
                        contador += 1

                        # Reconstruir a linha com o novo valor
                        nova_linha = f"INSERT INTO {tabela_original} ({', '.join(colunas)}) VALUES ({', '.join(valores)});"
                        linhas_modificadas.append(nova_linha + '\n')

                        # Armazenar no mapeamento
                        mapeamento_valores[valor_antigo] = valor_novo
                    else:
                        linhas_modificadas.append(linha)
                else:
                    linhas_modificadas.append(linha)
            else:
                linhas_modificadas.append(linha)

    # Sobrescrever o arquivo original com as linhas modificadas
    with open(nome_arquivo, 'w') as arquivo:
        arquivo.writelines(linhas_modificadas)

    # Criar o arquivo de mapeamento
    with open(arquivo_novo, 'w') as novo_arquivo:
        for valor_antigo, valor_novo in mapeamento_valores.items():
            novo_arquivo.write(f"{valor_antigo} = {valor_novo}\n")

# Exemplo de uso
alterar('teste.txt', 'ID', 999, 'ID.txt')

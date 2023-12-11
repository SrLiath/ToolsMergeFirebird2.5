import re
import os

def aplicar_substituicoes(arquivo_sql, pasta_substituicoes):
    # Criar um dicionário para armazenar as substituições
    substituicoes = {}

    # Ler os arquivos de substituição
    for arquivo_substituicao in os.listdir(pasta_substituicoes):
        caminho_arquivo = os.path.join(pasta_substituicoes, arquivo_substituicao)
        if os.path.isfile(caminho_arquivo):
            with open(caminho_arquivo, 'r') as arquivo_sub:
                for linha in arquivo_sub:
                    antigo_valor, novo_valor = map(str.strip, linha.split('='))
                    substituicoes[antigo_valor] = novo_valor

    # Aplicar as substituições ao arquivo SQL
    with open(arquivo_sql, 'r') as arquivo:
        linhas_modificadas = []
        for linha in arquivo:
            for antigo_valor, novo_valor in substituicoes.items():
                # Substituir o valor antigo pelo novo na linha
                linha = linha.replace(antigo_valor, novo_valor)

            linhas_modificadas.append(linha)

    # Sobrescrever o arquivo SQL com as linhas modificadas
    with open(arquivo_sql, 'w') as arquivo:
        arquivo.writelines(linhas_modificadas)

# Exemplo de uso
aplicar_substituicoes('teste.txt', 'testeids')

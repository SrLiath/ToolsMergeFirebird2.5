import re
import os

def alterar(sql_statement):
    try:
        i = 0
        match = re.search(r"INSERT\s+INTO\s+(\w+)\s*\((.*?)\)\s*VALUES\s*\((.*?)\);", sql_statement)

        if match:
            table_name = match.group(1)
            columns = match.group(2)
            values = match.group(3)

            columns_array = [col.strip() for col in columns.split(',')]
            values_array = [val.strip() for val in values.split(',')]
        else:
            return  # Exit the function if no match is found

        for column in columns_array:
            file_path = os.path.join('ids', f'{column}.txt')

            if os.path.exists(file_path):
                with open(file_path, 'r') as file:
                    for line in file:
                        partes = line.split(' = ')
                        if len(partes) == 2:
                            valor1, valor2 = partes
                            if valor1 == values_array[i]:
                                values_array[i] = valor2.strip()
                        else:
                            continue

            else:
                continue

            i += 1

        # Create a new INSERT statement
        new_insert = f"INSERT INTO {table_name} ({', '.join(columns_array)}) VALUES ({', '.join(values_array)});"
        with open('insertsNew.sql', 'a') as arquivo:
            arquivo.write(new_insert + '\n')

    except Exception as e:
        print(f"Erro: {e}")

file_path = 'teste.sql'
with open(file_path, 'r') as file:
    lines = file.readlines()

total_lines = len(lines)

for i, line in enumerate(lines, 1):
    remaining_lines = total_lines - i
    print(f"Linhas restantes: {remaining_lines}")
    alterar(line.strip())
    
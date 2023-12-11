import subprocess
import os
import zipfile

def disconnect_and_shutdown(database_path, user, password):
    command = [
        'gfix',
        '-user', user,
        '-password', password,
        '-shut', 'full',
        '-force', '0',
        database_path
    ]

    subprocess.run(command)

def compact_files(directory, output_zip):
    with zipfile.ZipFile(output_zip, 'w') as zipf:
        for file in os.listdir(directory):
            if file.lower().endswith(".gdb"):
                file_path = os.path.join(directory, file)
                zipf.write(file_path, os.path.basename(file_path))

if __name__ == "__main__":
    diretorio = '.'
    user = 'SYSDBA'
    password = 'masterkey'
    output_zip = ' Banco.zip'

    print('Iniciado')

    for file in os.listdir(diretorio):
        if file.lower().endswith(".gdb"):
            database_path = os.path.join(diretorio, file)
            disconnect_and_shutdown(database_path, user, password)
            print(f'Desconectado usando gfix para: {database_path}')

    compact_files(diretorio, output_zip)

    print(f'Arquivos compactados em: {output_zip}')


import os
import threading

import numpy as np
from flask import Flask, render_template, request, redirect, url_for, flash
import DAO
import face_recognition as fc

app = Flask(__name__)
app.secret_key = "chave_secreta"

@app.route('/')
def index():
    return render_template('index.html')

def comparar_rosto(face_encoding, banco_encodings, resultados):
    lock = threading.Lock()
    for nome, encoding_banco in banco_encodings.items():
        if fc.compare_faces([encoding_banco], face_encoding, tolerance=0.6)[0]:
            with lock:
                resultados.append(nome)
            break

@app.route('/reconhecimento', methods=['POST'])
def reconhecer_rosto():
    if 'imagem' not in request.files:
        flash("Nenhum arquivo enviado.")
        return redirect(url_for('index'))

    file = request.files['imagem']

    if file.filename == '':
        flash("Nenhuma imagem selecionada.")
        return redirect(url_for('index'))

    face_image = fc.load_image_file(file)
    image_array = np.array(face_image)

    altura, largura, _ = image_array.shape
    meio_altura, meio_largura = altura // 2, largura // 2

    partes = [
        image_array[:meio_altura, :meio_largura],
        image_array[:meio_altura, meio_largura:],
        image_array[meio_altura:, :meio_largura],
        image_array[meio_altura:, meio_largura:]
    ]

    banco_encodings = DAO.obter_encodings()

    resultados = {}
    threads = []

    for i in range(4):
        thread = threading.Thread(target=processar_parte_imagem, args=(partes[i], banco_encodings, resultados, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    for i, face_encoding in enumerate(face_encodings):
        encontrado = False

        for nome, encoding_banco in banco_encodings.items():
            resultado = fc.compare_faces([encoding_banco], face_encoding, tolerance=0.6)

            if resultado[0]:
                flash(f"Rosto {i + 1}: {nome} identificado com sucesso!")
                encontrado = True
                break

        if not encontrado:
            flash(f"Rosto {i + 1}: Não identificado no banco de dados.")

    return redirect(url_for('index'))

@app.route('/cadastrarRosto', methods=['POST'])
def cadastrar_rosto():
    if 'cadastrarimagem' not in request.files:
        flash("Nenhum arquivo enviado.")
        return redirect(url_for('index'))

    file = request.files['cadastrarimagem']
    nome = request.form['nome']

    if file.filename == '':
        flash("Nenhuma imagem selecionada.")
        return redirect(url_for('index'))

    img_data = file.read()
    DAO.insert_image(img_data, nome)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)

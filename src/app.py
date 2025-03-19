import os
from flask import Flask, render_template, request, redirect, url_for, flash
import DAO
import face_recognition as fc

app = Flask(__name__)
app.secret_key = "chave_secreta"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reconhecimento', methods=['POST'])
def reconhecer_rosto():
    if 'imagem' not in request.files:
        flash("Nenhum arquivo enviado.")
        return redirect(url_for('index'))

    file = request.files['imagem']

    if file.filename == '':
        flash("Nenhuma imagem selecionada.")
        return redirect(url_for('index'))

    # Lê a imagem enviada pelo usuário
    face_image = fc.load_image_file(file)
    face_encodings = fc.face_encodings(face_image)

    if not face_encodings:
        flash("Nenhum rosto encontrado na imagem fornecida.")
        return redirect(url_for('index'))

    # Obtém os encodings armazenados no banco de dados
    banco_encodings = DAO.obter_encodings()

    # Percorre cada rosto detectado na imagem enviada
    for i, face_encoding in enumerate(face_encodings):
        encontrado = False

        # Compara com todas as imagens do banco de dados
        for nome, encoding_banco in banco_encodings.items():
            resultado = fc.compare_faces([encoding_banco], face_encoding, tolerance=0.6)

            if resultado[0]:
                flash(f"Rosto {i + 1}: {nome} identificado com sucesso!")
                encontrado = True
                break  # Para a busca ao encontrar um rosto correspondente

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

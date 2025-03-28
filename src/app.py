import os
import threading
from flask import Flask, render_template, request, redirect, url_for, flash
import DAO
import face_recognition as fc
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = os.urandom(24)

def comparar_rosto(face_encoding, banco_encodings, resultados, lock):
    for nome, encoding_banco in banco_encodings.items():
        if fc.compare_faces([encoding_banco], face_encoding, tolerance=0.6)[0]:
            with lock:
                resultados.append(nome)
            break


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

    try:
        face_image = fc.load_image_file(file)
        face_encodings = fc.face_encodings(face_image)

        if not face_encodings:
            flash("Nenhum rosto detectado.")
            return redirect(url_for('index'))

        banco_encodings = DAO.obter_encodings()
        resultados = []
        lock = threading.Lock()

        threads = []
        for face_encoding in face_encodings:
            thread = threading.Thread(target=comparar_rosto, args=(face_encoding, banco_encodings, resultados, lock))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        if resultados:
            flash(f"Rosto(s) identificado(s): {', '.join(resultados)}")
        else:
            flash("Nenhum rosto identificado.")

        return redirect(url_for('index'))

    except Exception as e:
        flash(f"Erro no reconhecimento: {str(e)}")
        return redirect(url_for('index'))


@app.route('/cadastrarRosto', methods=['POST'])
def cadastrar_rosto():
    if 'cadastrarimagem' not in request.files or 'nome' not in request.form:
        return redirect(url_for('index'))

    file = request.files['cadastrarimagem']
    nome = request.form['nome']

    if file.filename == '':
        return redirect(url_for('index'))

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        face_image = fc.load_image_file(filepath)
        face_encodings = fc.face_encodings(face_image)

        if not face_encodings:
            flash("Nenhum rosto detectado na imagem enviada.")
            return redirect(url_for('index'))

        DAO.insert_image(filepath, nome)
        flash("Rosto cadastrado com sucesso!")
        return redirect(url_for('index'))
    except Exception as e:
        flash(f"Erro no cadastro: {str(e)}")
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)

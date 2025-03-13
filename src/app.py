from flask import Flask, render_template, request, redirect, url_for
import DAO
import face_recognition as fc

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reconhecimento', methods=['POST'])
def reconhecer_rosto():
    file = request.files['imagem']
    face_image = fc.load_image_file(file)
    face_encodings = fc.face_encodings(face_image)

    if not face_encodings:
        print("Nenhum rosto encontrado na imagem fornecida.")
        return redirect(url_for('index'))

    banco_encodings = DAO.obter_encodings()

    for i, face_encoding in enumerate(face_encodings):
        encontrado = False
        for nome, encoding_banco in banco_encodings.items():
            resultado = fc.compare_faces([encoding_banco], face_encoding)
            if resultado[0]:
                print(f"Rosto {i + 1}: {nome} está presente na imagem.")
                encontrado = True
                break

        if not encontrado:
            print(f"Rosto {i + 1}: Não identificado no banco de dados.")

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
import psycopg2
from PIL import Image
from io import BytesIO
import face_recognition as fc
import io

DB_CONFIG = {
    "dbname": "reconhecimentoFacial",
    "user": "postgres",
    "password": "daw1112",
    "host": "localhost",
    "port": "5432"
}


def conexaodb():
    return psycopg2.connect(**DB_CONFIG)


def insert_image(image_path, name):
    with conexaodb() as conn:
        with conn.cursor() as cursor:
            with open(image_path, 'rb') as file:
                img_data = file.read()

            cursor.execute('''
                INSERT INTO images (name, image) VALUES (%s, %s)
            ''', (name, psycopg2.Binary(img_data)))


def retornar_image_id(image_id):
    with conexaodb() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT image FROM images WHERE id = %s', (image_id,))
            img_data = cursor.fetchone()

            if img_data:
                return Image.open(BytesIO(img_data[0]))
            else:
                print("Nenhuma imagem encontrada para o ID fornecido.")
                return None


def retornar_image_name(image_name):
    with conexaodb() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT image FROM images WHERE name = %s', (image_name,))
            img_data = cursor.fetchone()

            if img_data:
                return Image.open(BytesIO(img_data[0]))
            else:
                print("Nenhuma imagem encontrada para o nome fornecido.")
                return None


def obter_encodings():
    banco_encodings = {}

    with conexaodb() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name, image FROM images")
            imagens = cur.fetchall()

    for img_nome, img_bin in imagens:
        img_io = io.BytesIO(img_bin)
        face_unknown = fc.load_image_file(img_io)
        face_unknown_encodings = fc.face_encodings(face_unknown)

        if face_unknown_encodings:
            banco_encodings[img_nome] = face_unknown_encodings[0]
        else:
            print(f"Aviso: Nenhum rosto detectado na imagem de {img_nome}, ignorando.")

    return banco_encodings

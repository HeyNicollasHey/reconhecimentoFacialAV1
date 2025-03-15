import psycopg2
from PIL import Image
from io import BytesIO
import face_recognition as fc
import io
def conexaodb():
    conn = psycopg2.connect(
        dbname="reconhecimentoFacial",
        user="postgres",
        password="1234",
        host="localhost",
        port="5432"
    )
    return conn
def insert_image(image_data, name):
    conn = conexaodb()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO images (name, image) VALUES (%s, %s)",
            (name, psycopg2.Binary(image_data))  # Convertendo para formato binário
        )
        conn.commit()
    except Exception as e:
        print(f"Erro ao inserir imagem: {e}")
    finally:
        cursor.close()
        conn.close()

def retornar_image_id(image_id):
    conn = conexaodb()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT image FROM images WHERE id = %s
    ''', (image_id,))

    img_data = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    img = Image.open(BytesIO(img_data))

    return img

def retornar_image_name(image_name):
    conn = conexaodb()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT image FROM images WHERE name = %s
    ''', (image_name,))

    img_data = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    img = Image.open(BytesIO(img_data))

    return img

def obter_encodings():
    conn = conexaodb()
    cur = conn.cursor()
    cur.execute("SELECT name, image FROM images")
    imagens = cur.fetchall()
    cur.close()
    conn.close()

    banco_encodings = {}
    for img_nome, img_bin in imagens:
        img_io = io.BytesIO(img_bin)
        face_unknown = fc.load_image_file(img_io)
        face_unknown_encodings = fc.face_encodings(face_unknown)
        if face_unknown_encodings:
            banco_encodings[img_nome] = face_unknown_encodings[0]

    return banco_encodings

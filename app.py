from flask import Flask, render_template, request, redirect, send_from_directory, url_for
from flask_mail import Mail, Message
from datetime import datetime
import pytz
import csv
import os

app = Flask(__name__)

# Configuración de correo
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'soporte@cloudsoftware.com.co'
app.config['MAIL_PASSWORD'] = 'zuig guvt xgzj rwlq'  # App password
app.config['MAIL_DEFAULT_SENDER'] = 'soporte@cloudsoftware.com.co'
mail = Mail(app)

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

CSV_FILE = 'incidentes.csv'
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'fecha_reporte', 'nombre', 'correo', 'telefono', 'empresa',
                         'tipo_problema', 'descripcion', 'archivo', 'estado', 'respuesta', 'archivo_respuesta'])

def now_colombia():
    tz = pytz.timezone('America/Bogota')
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

@app.route('/', methods=['GET', 'POST'])
def soporte():
    empresas = [
        '', 'Adela', 'Acomedios', 'Aldas', 'Asoredes', 'Big Media', 'Cafam', 'Century', 'CNM',
        'Contructora de Marcas', 'DORTIZ', 'Elite', 'Factorial', 'Grupo One', 'Zelva',
        'Integracion', 'Inversiones CNM', 'JH Hoyos', 'Jaime Uribe', 'Maproges',
        'Media Agency', 'Media Plus', 'Multimedios', 'New Sapiens', 'OMV',
        'Quintero y Quintero', 'Servimedios', 'Teleantioquia', 'TBWA'
    ]
    tipos_problema = ['Caso', 'Solicitud', 'Mejora']

    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        telefono = request.form['telefono']
        empresa = request.form['empresa']
        tipo_problema = request.form['tipo_problema']
        descripcion = request.form['descripcion']
        fecha_reporte = now_colombia()
        estado = 'pendiente'
        respuesta = ''
        archivo_respuesta = ''

        archivo = request.files.get('archivo')
        archivo_nombre = ''
        if archivo and archivo.filename:
            archivo_nombre = f"{datetime.now().timestamp()}_{archivo.filename}"
            archivo.save(os.path.join(UPLOAD_FOLDER, archivo_nombre))

        with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
            existing = list(csv.reader(f))
            next_id = len(existing)

        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([next_id, fecha_reporte, nombre, correo, telefono, empresa,
                             tipo_problema, descripcion, archivo_nombre, estado, respuesta, archivo_respuesta])

        # Enviar correo a soporte
        msg = Message('Nuevo caso reportado', recipients=['soporte@cloudsoftware.com.co'])
        msg.body = f"""Nuevo caso recibido:

Nombre: {nombre}
Correo: {correo}
Teléfono: {telefono}
Empresa: {empresa}
Tipo: {tipo_problema}
Descripción: {descripcion}
"""
        mail.send(msg)

        return redirect('/gracias')

    return render_template('formulario.html', empresas=empresas, tipos_problema=tipos_problema)

@app.route('/gracias')
def gracias():
    return render_template('gracias.html')

@app.route('/admin')
def admin():
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        data = list(csv.DictReader(f))
    return render_template('admin.html', incidentes=data)

@app.route('/responder/<int:incidente_id>', methods=['GET', 'POST'])
def responder(incidente_id):
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        data = list(csv.DictReader(f))

    incidente = data[incidente_id]

    if request.method == 'POST':
        respuesta = request.form['respuesta']
        archivo = request.files.get('archivo_respuesta')
        archivo_nombre = ''
        if archivo and archivo.filename:
            archivo_nombre = f"respuesta_{datetime.now().timestamp()}_{archivo.filename}"
            archivo.save(os.path.join(UPLOAD_FOLDER, archivo_nombre))

        incidente['respuesta'] = respuesta
        incidente['archivo_respuesta'] = archivo_nombre
        incidente['estado'] = 'cerrado'

        # Guardar cambios
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['id', 'fecha_reporte', 'nombre', 'correo', 'telefono', 'empresa',
                          'tipo_problema', 'descripcion', 'archivo', 'estado', 'respuesta', 'archivo_respuesta']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)

        # Enviar correo al cliente
        msg = Message('Respuesta a su caso', recipients=[incidente['correo']])
        msg.body = f"""Hola {incidente['nombre']},

Hemos respondido su caso:

Respuesta:
{respuesta}

Gracias por contactarnos.
"""
        if archivo_nombre:
            with app.open_resource(os.path.join(UPLOAD_FOLDER, archivo_nombre)) as fp:
                msg.attach(archivo.filename, archivo.content_type, fp.read())

        mail.send(msg)

        return redirect('/admin')

    return render_template('responder.html', incidente=incidente)

@app.route('/vaciar', methods=['GET', 'POST'])
def vaciar():
    if request.method == 'POST':
        clave = request.form.get('clave')
        if clave == '940402':
            with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'fecha_reporte', 'nombre', 'correo', 'telefono', 'empresa',
                                 'tipo_problema', 'descripcion', 'archivo', 'estado', 'respuesta', 'archivo_respuesta'])
            return "Base de datos vaciada correctamente."
        else:
            return "Clave incorrecta.", 403
    return '''
        <form method="POST">
            <label>Clave para vaciar:</label>
            <input type="password" name="clave">
            <input type="submit" value="Vaciar">
        </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)

# app.py
from flask import Flask, render_template, request, redirect
from flask_mail import Mail, Message
from datetime import datetime
import pytz
import os
import csv

app = Flask(__name__)

# Configuración de correo
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'soporte@cloudsoftware.com.co'
app.config['MAIL_PASSWORD'] = 'zuig guvt xgzj rwlq'
app.config['MAIL_DEFAULT_SENDER'] = 'soporte@cloudsoftware.com.co'
mail = Mail(app)

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
CSV_FILE = 'incidentes.csv'

empresas = [
    '', 'Adela', 'Acomedios', 'Aldas', 'Asoredes', 'Big Media', 'Cafam', 'Century', 'CNM',
    'Contructora de Marcas', 'DORTIZ', 'Elite', 'Factorial', 'Grupo One', 'Zelva',
    'Integracion', 'Inversiones CNM', 'JH Hoyos', 'Jaime Uribe', 'Maproges',
    'Media Agency', 'Media Plus', 'Multimedios', 'New Sapiens', 'OMV',
    'Quintero y Quintero', 'Servimedios', 'Teleantioquia', 'TBWA'
]
tipos_problema = ['Caso', 'Solicitud', 'Mejora']

def now_colombia():
    tz = pytz.timezone('America/Bogota')
    return datetime.now(tz)

@app.route('/', methods=['GET', 'POST'])
def soporte():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        telefono = request.form['telefono']
        empresa = request.form['empresa']
        tipo_problema = request.form['tipo_problema']
        descripcion = request.form['descripcion']
        fecha_reporte = now_colombia().strftime("%Y-%m-%d %H:%M:%S")
        estado = 'pendiente'

        archivo = request.files.get('archivo')
        archivo_nombre = ''
        if archivo and archivo.filename:
            archivo_nombre = f"{datetime.now().timestamp()}_{archivo.filename}"
            archivo.save(os.path.join(UPLOAD_FOLDER, archivo_nombre))

        # Guardar en CSV
        nueva_fila = [fecha_reporte, nombre, correo, telefono, empresa, tipo_problema, descripcion, archivo_nombre, estado]
        archivo_existe = os.path.exists(CSV_FILE)
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not archivo_existe:
                writer.writerow(['Fecha', 'Nombre', 'Correo', 'Telefono', 'Empresa', 'Tipo', 'Descripcion', 'Archivo', 'Estado'])
            writer.writerow(nueva_fila)

        # Enviar correo
        msg = Message("Nuevo incidente reportado", recipients=['soporte@cloudsoftware.com.co'])
        msg.body = f"""Se ha reportado un nuevo incidente:

Nombre: {nombre}
Correo: {correo}
Teléfono: {telefono}
Empresa: {empresa}
Tipo de caso: {tipo_problema}
Descripción: {descripcion}
Estado: {estado}
"""
        with open(CSV_FILE, 'rb') as f:
            msg.attach("incidentes.csv", "text/csv", f.read())

        if archivo_nombre:
            ruta_archivo = os.path.join(UPLOAD_FOLDER, archivo_nombre)
            with open(ruta_archivo, 'rb') as f:
                msg.attach(archivo.filename, archivo.content_type or 'application/octet-stream', f.read())

        mail.send(msg)

        return redirect('/gracias')

    return render_template('formulario.html', empresas=empresas, tipos_problema=tipos_problema)

@app.route('/gracias')
def gracias():
    return render_template('gracias.html')

@app.route('/admin')
def admin():
    incidentes = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            incidentes = list(reader)
    return render_template('admin.html', incidentes=incidentes)

if __name__ == '__main__':
    app.run(debug=True)

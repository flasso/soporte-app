# -*- coding: utf-8 -*-
gunicorn app:app
from flask import Flask, render_template, request, redirect, send_from_directory
from flask_mail import Mail, Message
from datetime import datetime
import pytz
import os
import csv

app = Flask(__name__)

# Configuración correo
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'soporte@cloudsoftware.com.co'
app.config['MAIL_PASSWORD'] = 'zuig guvt xgzj rwlq'
app.config['MAIL_DEFAULT_SENDER'] = 'soporte@cloudsoftware.com.co'

mail = Mail(app)

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

CSV_FILE = 'casos.csv'

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
            archivo_path = os.path.join(UPLOAD_FOLDER, archivo_nombre)
            archivo.save(archivo_path)
        else:
            archivo_path = None

        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([fecha_reporte, nombre, correo, telefono, empresa, tipo_problema, descripcion, archivo_nombre, estado])

        # Enviar correo a soporte
        msg = Message('Nuevo caso reportado', recipients=['soporte@cloudsoftware.com.co'])
        msg.body = f"""
Nuevo caso de soporte:

Nombre: {nombre}
Correo: {correo}
Teléfono: {telefono}
Empresa: {empresa}
Tipo: {tipo_problema}
Descripción: {descripcion}
"""
        if archivo_path:
            msg.attach(archivo.filename, archivo.mimetype, open(archivo_path, 'rb').read())
        mail.send(msg)

        return redirect('/gracias')

    empresas = ['', 'Adela', 'Acomedios', 'Aldas', 'Asoredes', 'Big Media', 'Cafam', 'Century', 'CNM']
    tipos_problema = ['Caso', 'Solicitud', 'Mejora']
    return render_template('formulario.html', empresas=empresas, tipos_problema=tipos_problema)

@app.route('/gracias')
def gracias():
    return render_template('gracias.html')

@app.route('/admin')
def admin():
    casos = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            # Manejar el error si la fila no tiene suficientes columnas
            try:
                for i, row in enumerate(reader, start=1):
                    # Asumiendo que el estado es la 9na columna (índice 8)
                    if len(row) > 8:
                        casos.append({'id': i, 'fecha': row[0], 'nombre': row[1], 'empresa': row[4], 'estado': row[8]})
                    else:
                        # Si la fila es muy corta, no la procesamos o le damos valores por defecto
                        casos.append({'id': i, 'fecha': row[0], 'nombre': row[1], 'empresa': row[4], 'estado': 'desconocido'})
            except IndexError:
                # Omitir filas mal formadas
                pass
    return render_template('admin.html', casos=casos)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# La siguiente línea se usa para desarrollo local. En Render, Gunicorn se encarga de esto.
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=10000)
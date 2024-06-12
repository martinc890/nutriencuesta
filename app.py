import os
import tempfile
from fastapi import FastAPI, Form, HTTPException, Response
from fastapi.responses import HTMLResponse, JSONResponse,StreamingResponse
from fastapi.staticfiles import StaticFiles
from matplotlib import pyplot as plt
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import base64
import csv


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import pymssql

# Detalles de conexión a SQL Server
servidor = '23141200.database.windows.net'
base_datos = 'integrador'
usuario = 'Sebastian-Admin'
contraseña = '2024Integrador'

# Crear conexión usando pymssql
conn = pymssql.connect(server=servidor, user=usuario, password=contraseña, database=base_datos)


# Rutas para archivos HTML
pagina_Resultado = os.path.join(os.path.dirname(__file__), 'HTML/paginaResultados.html')
directorio_css = os.path.join(os.path.dirname(__file__), 'CSS')
prueba4_html = os.path.join(os.path.dirname(__file__), 'HTML/paginaEncuesta.html')
html_directorio_final = os.path.join(os.path.dirname(__file__), 'HTML/finalEncuesta.html')

# Montar directorio estático
app.mount("/static", StaticFiles(directory=directorio_css), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_form():
    with open(prueba4_html, encoding="utf-8") as f:
        content = f.read()
        return HTMLResponse(content=content, headers={"Content-Type": "text/html; charset=utf-8"})

@app.post("/submit")
async def read_form(
    birth_year: Optional[int] = Form(...),
    gender: Optional[str] = Form(...),
    textura: Optional[str] = Form(...),
    consistencia: Optional[int] = Form(...),
    satisfactionRange: Optional[int] = Form(...),
    satisfactionRange_4: Optional[int] = Form(...),
    satisfactionRange_5: Optional[int] = Form(...),
    humedad: Optional[str] = Form(...),
    sabores: Optional[str] = Form(...),
    respuesta7: str = Form(...)
):
    try:
        # Llamar al procedimiento almacenado para insertar datos
        query = """
        EXEC InsertEncuesta @edad=%s, @genero=%s, @textura=%s, @consistencia=%s, @chocolate=%s, @atraccion=%s, @expectativa=%s, @humedad=%s, @sabores=%s, @respuesta=%s
        """
        valores = (birth_year, gender, textura, consistencia, satisfactionRange, satisfactionRange_4, satisfactionRange_5, humedad, sabores, respuesta7)

        with conn.cursor() as cursor:
            cursor.execute(query, valores)
            conn.commit()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return Response(status_code=303, headers={"Location": "/finalEncuesta.html"})

@app.get("/finalEncuesta.html", response_class=HTMLResponse)
async def get_final_encuesta():
    with open(html_directorio_final, encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content=content)

def generar_grafico_barras(respuestas,etiquetas):
    fig, ax = plt.subplots()
    ax.bar(etiquetas, respuestas.values())
    ax.set_xlabel('Respuestas')
    ax.set_ylabel('Cantidad')
    ax.set_title('Textura')
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig

def obtener_datos_encuestas():
    query = "SELECT chocolate, atraccion, expectativa FROM encuestas"
    categorias = ['chocolate', 'atraccion', 'expectativa']
    datos_encuestas = {categoria: [] for categoria in categorias}

    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            for i, categoria in enumerate(categorias):
                datos_encuestas[categoria].append(row[i])

    return categorias, datos_encuestas





@app.get("/ver_grafico", response_class=HTMLResponse)
async def get_form():
    with open(pagina_Resultado, encoding="utf-8") as f:
        content = f.read()
        return HTMLResponse(content=content, headers={"Content-Type": "text/html; charset=utf-8"})

#########################################################################################
    
def obtener_datos_pregunta1():
    query = "SELECT textura FROM encuestas"
    respuestas = {
        "Esponjoso": 0,
        "Crujiente": 0,
        "Blando": 0,
        "Duro": 0,
    }

    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            if row[0] in respuestas:
                respuestas[row[0]] += 1
    
    return respuestas


@app.get("/graph/pregunta1", response_class=JSONResponse)
async def get_graph_pregunta1():
    respuestas = obtener_datos_pregunta1()
    etiquetas = list(respuestas.keys())
    imagen_barras = generar_grafico_barras(respuestas,etiquetas)
    
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
        imagen_barras.savefig(tmpfile.name, format="png")

    with open(tmpfile.name, "rb") as image_file:
        imagen_base64_barra_pregunta_uno = base64.b64encode(image_file.read()).decode("utf-8")

    return {"imagen_base64_barra_pregunta_uno": imagen_base64_barra_pregunta_uno}

#########################################################################################

def obtener_datos_pregunta2():
    query = "SELECT consistencia FROM encuestas"
    total_respuestas = 0
    respuestas_consistencia = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            if row[0] in respuestas_consistencia:
                respuestas_consistencia[row[0]] += 1
                total_respuestas += 1
    # Imprimir los datos
    print("Respuestas de consistencia:", respuestas_consistencia)
    print("Total de respuestas:", total_respuestas)
    


   
    porcentajes_consistencia = {str(key): (value / total_respuestas) * 100 for key, value in respuestas_consistencia.items()}
    return porcentajes_consistencia

def generar_grafico_torta_dos(porcentajes_consistencia):
    fig, ax = plt.subplots()
    ax.pie(porcentajes_consistencia.values(), labels=porcentajes_consistencia.keys(), autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax.set_title('Valoración de la consistencia')
    return fig

@app.get("/graph/pregunta2", response_class=JSONResponse)
async def get_graph_pregunta2():
    porcentajes_consistencia = obtener_datos_pregunta2()
    imagen_barras = generar_grafico_torta_dos(porcentajes_consistencia)
    
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
        imagen_barras.savefig(tmpfile.name, format="png")

    with open(tmpfile.name, "rb") as image_file:
        imagen_base64_barra_pregunta_dos = base64.b64encode(image_file.read()).decode("utf-8")

    return {"imagen_base64_barra_pregunta_dos": imagen_base64_barra_pregunta_dos}

#########################################################################################

def obtener_datos_chocolate():
    query = "SELECT chocolate FROM encuestas"
    total_respuestas = 0
    respuestas_chocolate = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            if row[0] in respuestas_chocolate:
                respuestas_chocolate[row[0]] += 1
                total_respuestas += 1
    


    # Calcular los porcentajes
    porcentajes_chocolate = {str(key): (value / total_respuestas) * 100 for key, value in respuestas_chocolate.items()}
    
    return porcentajes_chocolate

def generar_grafico_torta_chocolate(porcentajes_chocolate):
    fig, ax = plt.subplots()
    ax.pie(porcentajes_chocolate.values(), labels=porcentajes_chocolate.keys(), autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax.set_title('Valoración del Chocolate')
    return fig

@app.get("/chocolate", response_class=JSONResponse)
async def get_graph_chocolate():
    porcentajes_chocolate = obtener_datos_chocolate()
    imagen_torta_chocolate = generar_grafico_torta_chocolate(porcentajes_chocolate)
    
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
        imagen_torta_chocolate.savefig(tmpfile.name, format="png")

    with open(tmpfile.name, "rb") as image_file:
        imagen_base64_chocolate = base64.b64encode(image_file.read()).decode("utf-8")

    return {"imagen_base64_chocolate": imagen_base64_chocolate}

#########################################################################################

def obtener_datos_atraccion():
    query = "SELECT atraccion FROM encuestas"
    total_respuestas = 0
    respuestas_atraccion = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            if row[0] in respuestas_atraccion:
                respuestas_atraccion[row[0]] += 1
                total_respuestas += 1

    # Calcular los porcentajes
    porcentajes_atraccion = {str(key): (value / total_respuestas) * 100 for key, value in respuestas_atraccion.items()}
    
    return porcentajes_atraccion

def generar_grafico_torta_atraccion(porcentajes_atraccion):
    fig, ax = plt.subplots()
    ax.pie(porcentajes_atraccion.values(), labels=porcentajes_atraccion.keys(), autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax.set_title('Valoración de la atraccion')
    return fig

@app.get("/atraccion", response_class=JSONResponse)
async def get_graph_atraccion():
    porcentajes_atraccion = obtener_datos_atraccion()
    imagen_torta_atraccion = generar_grafico_torta_atraccion(porcentajes_atraccion)
    
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
        imagen_torta_atraccion.savefig(tmpfile.name, format="png")

    with open(tmpfile.name, "rb") as image_file:
        imagen_base64_atraccion = base64.b64encode(image_file.read()).decode("utf-8")

    return {"imagen_base64_atraccion": imagen_base64_atraccion}

#########################################################################################

def obtener_datos_expectativa():
    query = "SELECT expectativa FROM encuestas"
    total_respuestas = 0
    respuestas_expectativa = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            if row[0] in respuestas_expectativa:
                respuestas_expectativa[row[0]] += 1
                total_respuestas += 1

    # Calcular los porcentajes
    porcentajes_expectativa = {str(key): (value / total_respuestas) * 100 for key, value in respuestas_expectativa.items()}

    return porcentajes_expectativa


def generar_grafico_torta_expectativa(porcentajes_expectativa):
    fig, ax = plt.subplots()
    ax.pie(porcentajes_expectativa.values(), labels=porcentajes_expectativa.keys(), autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax.set_title('Valoración de las Expectativas')
    return fig

@app.get("/expectativa", response_class=JSONResponse)
async def get_graph_expectativa():
    porcentajes_expectativa = obtener_datos_expectativa()
    imagen_torta_expectativa = generar_grafico_torta_expectativa(porcentajes_expectativa)
    
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
        imagen_torta_expectativa.savefig(tmpfile.name, format="png")

    with open(tmpfile.name, "rb") as image_file:
        imagen_base64_expectativa = base64.b64encode(image_file.read()).decode("utf-8")

    return {"imagen_base64_expectativa": imagen_base64_expectativa}

#########################################################################################

def obtener_datos_pregunta7():
    respuestas = {"Dulce": 0, "Amargo": 0, "Salado": 0, "Ácido": 0}
    query = "SELECT sabores FROM encuestas"

    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            if row[0] in respuestas:
                respuestas[row[0]] += 1

    return respuestas

def generar_grafico_barras_sabores(respuestas,etiquetas):
    fig, ax = plt.subplots()
    ax.bar(etiquetas, respuestas.values())
    ax.set_xlabel('Respuestas')
    ax.set_ylabel('Cantidad')
    ax.set_title('Respuestas a la Pregunta 7')
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig

@app.get("/graph/sabores", response_class=JSONResponse)
async def get_graph_pregunta7():
    respuestas = obtener_datos_pregunta7()
    etiquetas = list(respuestas.keys())
    imagen_barras = generar_grafico_barras_sabores(respuestas,etiquetas)
    
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
        imagen_barras.savefig(tmpfile.name, format="png")

    with open(tmpfile.name, "rb") as image_file:
        imagen_base64_barra_pregunta_siete = base64.b64encode(image_file.read()).decode("utf-8")

    return {"imagen_base64_barra_pregunta_siete": imagen_base64_barra_pregunta_siete}

#########################################################################################



# Agrega esta nueva ruta

@app.get("/download_csv")
async def download_csv():
    # Consulta para obtener los datos de la base de datos
    query = """
    SELECT edad, genero, textura, consistencia, chocolate, atraccion, expectativa, humedad, sabores, respuesta 
    FROM encuestas
    """

    # Ejecutar la consulta y obtener los datos
    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    # Crear un archivo temporal para almacenar el archivo CSV
    with tempfile.NamedTemporaryFile(mode='w', newline='', delete=False) as tmpfile:
        fieldnames = ["Edad", "Genero", "Textura", "Consistencia", "Chocolate", "Atraccion", "Expectativa", "Humedad", "Sabores", "Respuesta"]
        writer = csv.DictWriter(tmpfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "Edad": row[0],
                "Genero": row[1],
                "Textura": row[2],
                "Consistencia": row[3],
                "Chocolate": row[4],
                "Atraccion": row[5],
                "Expectativa": row[6],
                "Humedad": row[7],
                "Sabores": row[8],
                "Respuesta": row[9]
            })

    # Crear una respuesta de streaming para devolver el archivo CSV
    def iterfile():
        with open(tmpfile.name, mode="r") as file:
            yield from file

    return StreamingResponse(iterfile(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=encuestas.csv"})





if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)

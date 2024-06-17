import os
import tempfile
from fastapi import FastAPI, Form, HTTPException, Response,Query
from fastapi.responses import HTMLResponse, JSONResponse,StreamingResponse
from fastapi.staticfiles import StaticFiles
from matplotlib import pyplot as plt
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import base64
import csv
from abc import ABC,abstractmethod

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
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return Response(status_code=303, headers={"Location": "/finalEncuesta.html"})

@app.get("/finalEncuesta.html", response_class=HTMLResponse)
async def get_final_encuesta():
    with open(html_directorio_final, encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content=content)
#Empleo del patron Factory
class Grafico (ABC):
    @abstractmethod
    def generar(self,data):
        pass

class GraficoBarras(Grafico):
    def generar(self,data,titulo):
        colores_marron = ['#D2B48C', '#A0522D', '#8B4513', '#563527']
        fig, ax = plt.subplots()
        ax.bar(data.keys(), data.values(),color=colores_marron)
        ax.set_xlabel('Respuestas')
        ax.set_ylabel('Cantidad')
        ax.set_title(titulo)
        plt.xticks(rotation=45)
        plt.tight_layout()
        return fig
class GraficoTorta(Grafico):
    def generar(self, data,titulo):
        colores_marron = ['#D2B48C', '#A0522D', '#8B4513', '#563527', '#800000']
        fig, ax = plt.subplots()
        ax.pie(data.values(), labels=data.keys(), autopct='%1.1f%%', startangle=90,colors=colores_marron)
        ax.axis('equal')
        ax.set_title(titulo)
        return fig
class FabricaGraficos:
    def crear_grafico(self, tipo):
        if tipo == 'barras':
            return GraficoBarras()
        elif tipo == 'torta':
            return GraficoTorta()
        else:
            raise ValueError(f"Tipo de gráfico '{tipo}' no es válido.")


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
async def get_graph_pregunta1(titulo: str= Query("Textura")):
    respuestas = obtener_datos_pregunta1()
    fabrica=FabricaGraficos()
    grafico=fabrica.crear_grafico('barras')
    imagen_barras=grafico.generar(respuestas,titulo)
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


@app.get("/graph/pregunta2", response_class=JSONResponse)
async def get_graph_pregunta2(titulo: str= Query("Consistencia")):
    fabrica=FabricaGraficos()
    grafico=fabrica.crear_grafico('torta')
    porcentajes_consistencia = obtener_datos_pregunta2()
    imagen_torta = grafico.generar(porcentajes_consistencia,titulo)
    
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
        imagen_torta.savefig(tmpfile.name, format="png")

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


@app.get("/chocolate", response_class=JSONResponse)
async def get_graph_chocolate(titulo: str= Query("Sabor a chocolate")):
    fabrica=FabricaGraficos()
    grafico=fabrica.crear_grafico('torta')
    porcentajes_chocolate = obtener_datos_chocolate()
    imagen_torta_chocolate = grafico.generar(porcentajes_chocolate,titulo)
    
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

@app.get("/atraccion", response_class=JSONResponse)
async def get_graph_atraccion(titulo: str= Query("Atraccion del Producto")):
    fabrica=FabricaGraficos()
    grafico=fabrica.crear_grafico('torta')
    porcentajes_atraccion = obtener_datos_atraccion()
    imagen_torta_atraccion = grafico.generar(porcentajes_atraccion,titulo)
    
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

@app.get("/expectativa", response_class=JSONResponse)
async def get_graph_expectativa(titulo: str= Query("Expectativa")):
    fabrica=FabricaGraficos()
    grafico=fabrica.crear_grafico('torta')
    porcentajes_expectativa = obtener_datos_expectativa()
    imagen_torta_expectativa = grafico.generar(porcentajes_expectativa,titulo)
    
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


@app.get("/graph/sabores", response_class=JSONResponse)
async def get_graph_pregunta7(titulo: str= Query("Sabores")):
    fabrica=FabricaGraficos()
    grafico=fabrica.crear_grafico('barras')
    respuestas = obtener_datos_pregunta7()
    imagen_barras = grafico.generar(respuestas,titulo)
    
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

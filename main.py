import os
import joblib  
import pandas as pd
from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta

# 📌 Crear la API
app = FastAPI()

# 📌 Cargar todos los modelos al iniciar la API
modelos = {}
modelos_path = os.path.join(os.path.dirname(__file__), "modelos_productos/")

if not os.path.exists(modelos_path):
    raise Exception("⚠️ No se encontró la carpeta de modelos.")

print("📂 Archivos encontrados en la carpeta:")
for archivo in os.listdir(modelos_path):
    print(f"  - {archivo}")

for archivo in os.listdir(modelos_path):
    if archivo.endswith(".pkl"):
        try:
            producto = archivo.replace("modelo_arima_", "").replace(".pkl", "")
            with open(os.path.join(modelos_path, archivo), "rb") as f:
                modelos[producto] = joblib.load(f)  
                print(f"✅ Modelo cargado exitosamente: {archivo}")
        except Exception as e:
            print(f"❌ Error al cargar {archivo}: {str(e)}")

if not modelos:
    raise Exception("⚠️ No se pudo cargar ningún modelo.")

print(f"✅ Modelos cargados: {list(modelos.keys())}")

# 📌 Endpoint para predecir ventas
@app.get("/predecir/{codigo_producto}")
async def predecir_ventas(codigo_producto: str, meses: int = 1, periodo: str = "mes"):
    if codigo_producto not in modelos:
        raise HTTPException(status_code=404, detail="Modelo no encontrado para el producto.")

    modelo = modelos[codigo_producto]

    # 📌 Crear fechas futuras
    fecha_actual = datetime.today()
    dias_futuros = meses * 30
    fechas_futuras = [fecha_actual + timedelta(days=i) for i in range(dias_futuros)]

    # 📌 Hacer predicción
    steps = len(fechas_futuras)
    predicciones = modelo.forecast(steps=steps)  # Predicciones para el periodo futuro

    # 📌 Crear un DataFrame con las fechas y las predicciones
    forecast = pd.DataFrame({
        "fecha": fechas_futuras,
        "cantidad_predicha": predicciones
    })

    # 📌 Formatear la salida según el periodo solicitado
    if periodo == "semana":
        forecast["semana"] = forecast["fecha"].dt.strftime("%Y-%U")  # Año-Semana
        resultado = forecast.groupby("semana")["cantidad_predicha"].sum().reset_index()
        resultado.rename(columns={"semana": "periodo"}, inplace=True)

    elif periodo == "mes":
        forecast["mes"] = forecast["fecha"].dt.strftime("%Y-%m")  # Año-Mes
        resultado = forecast.groupby("mes")["cantidad_predicha"].sum().reset_index()
        resultado.rename(columns={"mes": "periodo"}, inplace=True)

    else:
        raise HTTPException(status_code=400, detail="Periodo no válido. Usa 'semana' o 'mes'.")

    return resultado.to_dict(orient="records")

# 📌 Iniciar la API
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
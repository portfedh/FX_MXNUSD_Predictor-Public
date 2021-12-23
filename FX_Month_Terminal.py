# Importing Modules
######################
import datetime as dt
import requests
import pandas as pd
import os

# Variables
###########
# Token de Consulta Banxico
token = os.environ.get("token_banxico")
# Token de Consulta Banxico
fix = "SF63528"
# FX FIX
obligaciones = "SF60653"
# FX para Solventar Obligaciones

# Fechas
########
today = dt.date.today()  # - dt.timedelta(21)  ## Para pruebas
print("Today is = " + str(today))
# Fecha actual
first_day = today.replace(day=1)
print("The first day of this month is = " + str(first_day))
# Primer dia del mes
week_day = today.weekday()
# Dia de la semana
print(("Today is day number: "
       + str(week_day)
       + "\n(Date range is 0 to 6)"))


# Funcion de descarga de datos
##############################
# Funcion de Descarga
def descarga_bmx_serie(serie, fechainicio, fechafin, token):
    try:
        # Al site de banxico se le añaden los datos de consulta
        url = (
               "https://www.banxico.org.mx/SieAPIRest/service/v1/series/"
               + serie
               + "/datos/"
               + fechainicio
               + "/"
               + fechafin
               )
        print(url)
        # Se le tienen que pasar Headers
        headers = {"Bmx-Token": token}
        # Se pasa el token de banxico en un diccionario.
        response = requests.get(url, headers=headers)
        # Se pasa como un request con metodo get
        status = response.status_code
        # Se le solicita el codigo de respuesta al servidor.
        if status == 200:
            # Si el estatus esta Ok armar el dataframe
            raw_data = response.json()
            # Se guarda la respuesta como una variable.
            data = raw_data["bmx"]["series"][0]["datos"]
            # Se filtra el json
            # Se accesa el diccionario con los datos
            global df
            # Hacemos que la variable global para poder accesarla despues
            df = pd.DataFrame(data)
            # Creamos un dataframe con la informacion
            df["dato"] = df["dato"].apply(lambda x: float(x))
            # Volvemos los datos floats en vez de strings
            df["fecha"] = pd.to_datetime(df["fecha"], format="%d/%m/%Y")
            # Volvemos las fechas a formato fecha
            df.columns = ["Fecha", "Tipo de Cambio"]
            # Cambia el nombre de la columna "dato"  por tipo de cambio
            print("A-Ok")
            return df
            # Regresa el dataframe
        else:
            # Si el estatus esta mal imprimir el error en la terminal.
            print(status)
    except Exception:
        print("An exception occurred:\n")
        print(Exception)


# Descargando Tipo de Cambio: Obligaciones
##########################################
fx_obligaciones = descarga_bmx_serie(obligaciones,
                                     str(first_day),
                                     str(today),
                                     token
                                     )
df.set_index("Fecha", inplace=True)

# Mostrar el data frame
fx_obligaciones

# Descargando Tipo de Cambio: FIX
###################################
# Para la fecha inicial, nos vamos 4 dias hacia atras.
# Por si la busqueda se ejecuta el primer dia de mes y cae en fin de semana.
fx_fix = descarga_bmx_serie(fix,
                            str(first_day - dt.timedelta(4)),
                            str(today),
                            token
                            )
df.set_index("Fecha", inplace=True)


# Creando el Dataframe para FX Obligaciones Futuras
####################################################
# Crear un dataframe vacio con las columnas
fx_obligaciones_f = pd.DataFrame(columns=["Fecha", "Tipo de Cambio"])

# Volver los valores de fecha datetime en ves de string
datetime_series = pd.to_datetime(fx_obligaciones_f["Fecha"])
datetime_index = pd.DatetimeIndex(datetime_series.values)
fx_obligaciones_f = (fx_obligaciones_f
                     .set_index(datetime_index)
                     .rename_axis("Fecha", axis=1)
                     )
fx_obligaciones_f.drop("Fecha", axis=1, inplace=True)

# Sacando el FX Obligaciones de los proximos dias
#################################################
day_plus1 = today + dt.timedelta(1)
day_plus2 = today + dt.timedelta(2)
day_plus3 = today + dt.timedelta(3)
day_plus4 = today + dt.timedelta(4)

if week_day == 4:
    # Codigo si fecha cae en viernes
    ################################
    # Valores de tipo de cambio FIX a añadir
    fx_fix_1d = fx_fix["Tipo de Cambio"].iloc[-1]  # FIX ayer
    fx_fix_2d = fx_fix["Tipo de Cambio"].iloc[-2]  # FIX antier

    fx_obligaciones_plus1 = {"Tipo de Cambio": fx_fix_2d}
    fx_obligaciones_plus2 = {"Tipo de Cambio": fx_fix_2d}
    fx_obligaciones_plus3 = {"Tipo de Cambio": fx_fix_2d}
    fx_obligaciones_plus4 = {"Tipo de Cambio": fx_fix_1d}

    # Añadir valores al dataframe fx_obligaciones_f
    fx_obligaciones_f = fx_obligaciones_f.append(
        pd.DataFrame(fx_obligaciones_plus1, index=[day_plus1])
    )
    fx_obligaciones_f = fx_obligaciones_f.append(
        pd.DataFrame(fx_obligaciones_plus2, index=[day_plus2])
    )
    fx_obligaciones_f = fx_obligaciones_f.append(
        pd.DataFrame(fx_obligaciones_plus3, index=[day_plus3])
    )
    fx_obligaciones_f = fx_obligaciones_f.append(
        pd.DataFrame(fx_obligaciones_plus4, index=[day_plus4])
    )

    # Transformar valores a datetime
    fx_obligaciones_f.index = pd.to_datetime(fx_obligaciones_f.index)

elif week_day == 5:
    # Codigo si fecha cae en Sabado
    ###############################
    # Valores de tipo de cambio FIX a añadir
    fx_fix_1d = fx_fix["Tipo de Cambio"].iloc[-1]  # FIX ayer
    fx_fix_2d = fx_fix["Tipo de Cambio"].iloc[-2]  # FIX antier

    fx_obligaciones_plus1 = {"Tipo de Cambio": fx_fix_2d}
    fx_obligaciones_plus2 = {"Tipo de Cambio": fx_fix_2d}
    fx_obligaciones_plus3 = {"Tipo de Cambio": fx_fix_1d}

    # Añadir valores al dataframe fx_obligaciones_f
    fx_obligaciones_f = fx_obligaciones_f.append(
        pd.DataFrame(fx_obligaciones_plus1, index=[day_plus1])
    )
    fx_obligaciones_f = fx_obligaciones_f.append(
        pd.DataFrame(fx_obligaciones_plus2, index=[day_plus2])
    )
    fx_obligaciones_f = fx_obligaciones_f.append(
        pd.DataFrame(fx_obligaciones_plus3, index=[day_plus3])
    )

    # Transformar valores a datetime
    fx_obligaciones_f.index = pd.to_datetime(fx_obligaciones_f.index)

else:
    # Codigo si fecha cae en Lunes a Jueves o Domingo
    #################################################
    # Valores de tipo de cambio FIX a añadir
    fx_fix_1d = fx_fix["Tipo de Cambio"].iloc[-1]  # FIX ayer
    fx_fix_2d = fx_fix["Tipo de Cambio"].iloc[-2]  # FIX antier

    fx_obligaciones_plus1 = {"Tipo de Cambio": fx_fix_2d}
    fx_obligaciones_plus2 = {"Tipo de Cambio": fx_fix_1d}

    # Añadir valores al dataframe fx_obligaciones_f
    fx_obligaciones_f = fx_obligaciones_f.append(
        pd.DataFrame(fx_obligaciones_plus1, index=[day_plus1])
    )
    fx_obligaciones_f = fx_obligaciones_f.append(
        pd.DataFrame(fx_obligaciones_plus2, index=[day_plus2])
    )

    # Transformar valores a datetime
    fx_obligaciones_f.index = pd.to_datetime(fx_obligaciones_f.index)


# Juntando Fx Obligaciones con Fx Obligaciones Futuras
######################################################

fx_join = pd.concat([fx_obligaciones, fx_obligaciones_f], axis=0)
fx_join.index.name = "Fecha"

# Mostramos la informacion sin el indice
print("\n")
print(fx_join.to_string(index=True))
print("\n")

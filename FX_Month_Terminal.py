# Importing Modules
######################
import datetime as dt
import requests
import pandas as pd
import smtplib
import os

# Variables
###########
# Token de Consulta Banxico
token = os.environ.get("token_banxico")

# Clave de Descarga Banxico
fix = "SF63528"  # Fecha de Determinacion (FIX)
obligaciones = "SF60653"  # Para Solventar Obligaciones

# Fechas
########
# Fecha actual
today = dt.date.today()  # - dt.timedelta(21)  ## Para pruebas
print("Today is = "+str(today))

# Primer dia del mes
first_day = today.replace(day=1)
print("The first day of this month is = "+str(first_day))

# Dia de la semana
week_day = today.weekday()
print("Today is day number: "+str(week_day)+"\n(Date range is 0 to 6)")


# Funcion de Descarga de datos de Banxico
#########################################

# Funcion de Descarga
def descarga_bmx_serie(serie, fechainicio, fechafin, token):
    try:
        # Al site de banxico se le pegan los datos de consulta
        url = ("https://www.banxico.org.mx/SieAPIRest/service/v1/series/"
               +serie+"/datos/"+fechainicio+"/"+fechafin)
        print(url)

        # Se le tienen que pasar Headers
        # Se pasa el token de banxico en un diccionario.
        # Se pasa como un Request con metodo Get
        # Se le solicita el codigo de respuesta al servidor.
        headers = {"Bmx-Token": token}
        response = requests.get(url, headers=headers)
        status = response.status_code

        # Si el estatus esta Ok armar el dataframe
        # Si el estatus esta mal imprimir el Error en la consulta.
        if status == 200:
            # Si el codigo es correcto pasa la respuesta a formato Json
            raw_data = response.json()

            # Pasamos las llaves en el Json para crear la serie de datos.
            data = raw_data["bmx"]["series"][0]["datos"]

            # Creamos con la serie un dataframe
            # Volvemos los datos floats en vez de strings
            # Volvemos las fechas a formato fecha
            # Volvemos la fecha la columna indice (Deshabilidado)
            # Regresa el Dataframe
            # Cambia el nombre de la columna "dato"  por tipo de cambio
            global df
            df = pd.DataFrame(data)
            df["dato"] = df["dato"].apply(lambda x: float(x))
            df["fecha"] = pd.to_datetime(df["fecha"], format="%d/%m/%Y")
            df.columns = ['Fecha', 'Tipo de Cambio']
            print("A-Ok")
            return(df)
        else:
            print(status)
    except Exception:
        print("An exception occurred")


# Descargando Tipo de Cambio: Obligaciones
##########################################
fx_obligaciones = descarga_bmx_serie(obligaciones, str(first_day), str(today), token)
df.set_index('Fecha', inplace=True)

# Mostrar el Data Frame
fx_obligaciones

# # Descargando Tipo de Cambio: FIX
###################################

# Para la fecha inicial, nos vamos 4 dias hacia atras.
# Por si la busqueda se ejecuta el primer dia de mes y cae en fin de semana.
fx_fix = descarga_bmx_serie(fix, str(first_day - dt.timedelta(4)), str(today), token)
df.set_index('Fecha', inplace=True)

# Mostrar el Data Frame
fx_fix


# Creando el Dataframe para FX Obligaciones Futuras
####################################################

# Create an empty dataframe with column names
fx_obligaciones_f = pd.DataFrame(columns=['Fecha', 'Tipo de Cambio'])

# Volver los valores de fecha un datetime y no un string
datetime_series = pd.to_datetime(fx_obligaciones_f['Fecha'])
datetime_series = pd.to_datetime(fx_obligaciones_f['Fecha'])
datetime_index = pd.DatetimeIndex(datetime_series.values)
fx_obligaciones_f = fx_obligaciones_f.set_index(datetime_index).rename_axis('Fecha', axis=1)
fx_obligaciones_f.drop('Fecha', axis=1, inplace=True)

fx_obligaciones_f

# Sacando el FX Obligaciones de los proximos dias
#################################################
# Fechas Futuras
day_plus1 = today + dt.timedelta(1)
day_plus2 = today + dt.timedelta(2)
day_plus3 = today + dt.timedelta(3)
day_plus4 = today + dt.timedelta(4)

if week_day == 4:
    ######## Codigo si fecha cae en viernes ########
    # Valores de tipo de cambio Fix a añadir
    fx_fix_1d = fx_fix['Tipo de Cambio'].iloc[-1]  # Fix ayer
    fx_fix_2d = fx_fix['Tipo de Cambio'].iloc[-2]  # Fix antier

    fx_obligaciones_plus1 = {"Tipo de Cambio": fx_fix_2d}
    fx_obligaciones_plus2 = {"Tipo de Cambio": fx_fix_2d}
    fx_obligaciones_plus3 = {"Tipo de Cambio": fx_fix_2d}
    fx_obligaciones_plus4 = {"Tipo de Cambio": fx_fix_1d}

    # Create a new dataframe with these rows
    fx_obligaciones_f = fx_obligaciones_f.append(pd.DataFrame(fx_obligaciones_plus1, index=[day_plus1]))
    fx_obligaciones_f = fx_obligaciones_f.append(pd.DataFrame(fx_obligaciones_plus2, index=[day_plus2]))
    fx_obligaciones_f = fx_obligaciones_f.append(pd.DataFrame(fx_obligaciones_plus3, index=[day_plus3]))
    fx_obligaciones_f = fx_obligaciones_f.append(pd.DataFrame(fx_obligaciones_plus4, index=[day_plus4]))

    # Transform dates to datetime format
    fx_obligaciones_f.index = pd.to_datetime(fx_obligaciones_f.index)

elif week_day == 5:
    ######## Codigo si fecha cae en Sabado ########
    # Valores de tipo de cambio Fix a añadir
    fx_fix_1d = fx_fix['Tipo de Cambio'].iloc[-1]  # Fix ayer
    fx_fix_2d = fx_fix['Tipo de Cambio'].iloc[-2]  # Fix antier

    fx_obligaciones_plus1 = {"Tipo de Cambio": fx_fix_2d}
    fx_obligaciones_plus2 = {"Tipo de Cambio": fx_fix_2d}
    fx_obligaciones_plus3 = {"Tipo de Cambio": fx_fix_1d}

    # Create a new dataframe with these rows
    fx_obligaciones_f = fx_obligaciones_f.append(pd.DataFrame(fx_obligaciones_plus1, index=[day_plus1]))
    fx_obligaciones_f = fx_obligaciones_f.append(pd.DataFrame(fx_obligaciones_plus2, index=[day_plus2]))
    fx_obligaciones_f = fx_obligaciones_f.append(pd.DataFrame(fx_obligaciones_plus3, index=[day_plus3]))

    # Transform dates to datetime format
    fx_obligaciones_f.index = pd.to_datetime(fx_obligaciones_f.index)

else:
    ######## Codigo si fecha cae en Lunes-Jueves o Domingo ########
    # Valores de tipo de cambio Fix a añadir
    fx_fix_1d = fx_fix['Tipo de Cambio'].iloc[-1]  # Fix ayer
    fx_fix_2d = fx_fix['Tipo de Cambio'].iloc[-2]  # Fix antier

    fx_obligaciones_plus1 = {"Tipo de Cambio": fx_fix_2d}
    fx_obligaciones_plus2 = {"Tipo de Cambio": fx_fix_1d}

    # Create a new dataframe with these rows
    fx_obligaciones_f = fx_obligaciones_f.append(pd.DataFrame(fx_obligaciones_plus1, index=[day_plus1]))
    fx_obligaciones_f = fx_obligaciones_f.append(pd.DataFrame(fx_obligaciones_plus2, index=[day_plus2]))

    # Transform dates to datetime format
    fx_obligaciones_f.index = pd.to_datetime(fx_obligaciones_f.index)

fx_obligaciones_f


# Juntando Fx Obligaciones con Fx Obligaciones Futuras
######################################################

# Juntar fx_obligaciones y fx_obligaciones_f
fx_join = pd.concat([fx_obligaciones, fx_obligaciones_f], axis=0)
fx_join.index.name='Fecha'
fx_join


# Mostramos la informacion sin el indice
print("\n")
print(fx_join.to_string(index=True))
print("\n")

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import random, datetime

driver = webdriver.Firefox()

driver.get("http://127.0.0.1:8000/procesos/carga_modifica/1/")

campo_enfermedad = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "enfermedad"))
)
select_enfermedad = Select(campo_enfermedad)
opciones_enfermedad = [o.text for o in select_enfermedad.options]
enfermedad_seleccionada = random.choice(opciones_enfermedad[1:])
select_enfermedad.select_by_visible_text(enfermedad_seleccionada)

campo_base = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "base"))
)
select_base = Select(campo_base)
opciones_base = [o.text for o in select_base.options]
base_seleccionada = random.choice(opciones_base[1:])  
select_base.select_by_visible_text(base_seleccionada)

campo_ambulancia = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "ambulancia"))
)
select_ambulancia = Select(campo_ambulancia)
opciones_ambulancia = [o.text for o in select_ambulancia.options]
ambulancia_seleccionada = random.choice(opciones_ambulancia[1:]) 
select_ambulancia.select_by_visible_text(ambulancia_seleccionada)

fecha_inicio = datetime.datetime.now() - datetime.timedelta(days=30)
fecha_fin = datetime.datetime.now()
fecha_salida = fecha_inicio + datetime.timedelta(
    seconds=random.randint(0, int((fecha_fin - fecha_inicio).total_seconds())),
)


campo_fecha_salida = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "fecha_salida"))
)
campo_fecha_salida.send_keys(fecha_salida.strftime("%Y-%m-%dT%H:%M"))

fecha_llegada = fecha_salida + datetime.timedelta(
    seconds=random.randint(0, 3600)
)

campo_fecha_llegada = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "fecha_llegada"))
)
campo_fecha_llegada.send_keys(fecha_llegada.strftime("%Y-%m-%dT%H:%M"))

fecha_retorno = fecha_llegada + datetime.timedelta(
    seconds=random.randint(0, 3600)
)

campo_fecha_retorno = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "fecha_retorno"))
)
campo_fecha_retorno.send_keys(fecha_retorno.strftime("%Y-%m-%dT%H:%M"))

# Lista de apellidos y nombres
apellidos = ["Pérez", "García", "Martínez", "Rodríguez", "González"]
nombres = ["Juan", "María", "Pedro", "Ana", "Luis"]

campo_nombre = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "nombre"))
)
campo_nombre.send_keys(random.choice(nombres))

campo_apellido_paterno = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "apellido_paterno"))
)
campo_apellido_paterno.send_keys(random.choice(apellidos))

campo_apellido_materno = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "apellido_materno"))
)
campo_apellido_materno.send_keys(random.choice(apellidos))

campo_telefono = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "telefono"))
)
campo_telefono.send_keys(str(random.randint(1000000000, 9999999999)))

campo_domicilio = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "domicilio"))
)
select_domicilio = Select(campo_domicilio)
opciones_domicilio = [o.text for o in select_domicilio.options]
domicilio_seleccionado = random.choice(opciones_domicilio[1:])
select_domicilio.select_by_visible_text(domicilio_seleccionado)

campo_colonia = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "colonia"))
)
select_colonia = Select(campo_colonia)
opciones_colonia = [o.text for o in select_colonia.options]
colonia_seleccionada = random.choice(opciones_colonia[1:]) 
select_colonia.select_by_visible_text(colonia_seleccionada)

campo_numero = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "domicilio_numero"))
)
campo_numero.send_keys(str(random.randint(1, 100)))

campo_estatura = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "estatura"))
)
campo_estatura.send_keys(str(round(random.uniform(1.50, 2.00), 2)))

campo_edad = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "edad"))
)
campo_edad.send_keys(str(random.randint(18, 100)))

campo_ropa = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "ropa"))
)
campo_ropa.send_keys("Camisa blanca y pantalón negro")

antecedente = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "antecedente"))
)
antecedente.send_keys("Se partió su cola")

sintoma = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "sintoma"))
)
sintoma.send_keys("Se partió su cola")


campo_hospital = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "hospital"))
)
select_hospital = Select(campo_hospital)
opciones_hospital = [o.text for o in select_hospital.options]
hospital_seleccionada = random.choice(opciones_hospital[1:])  
select_hospital.select_by_visible_text(hospital_seleccionada)

responsable = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "nombre_respon_hospital"))
)
responsable.send_keys("Hectir")

campo_fecha_ultima = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "fecha_ultima_comida"))
)
campo_fecha_ultima.send_keys(fecha_retorno.strftime("%Y-%m-%dT%H:%M"))

agrente = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "nombre_agente"))
)
agrente.send_keys("Hectir")

numagrente = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "numero_agente"))
)
numagrente.send_keys("10")

pulso = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "pulso"))
)
pulso.send_keys("80")

respiracion = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "respiracion"))
)
respiracion.send_keys("16")

hemorragia = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "hemorragia"))
)
hemorragia.send_keys("No")

dolor = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "dolor"))
)
dolor.send_keys("Moderado")

ta_inicial = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "presion_inicial"))
)
ta_inicial.send_keys("120/80")

ta_posterior = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "presion_posterior"))
)
ta_posterior.send_keys("118/78")

destroxtix = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "destroxtix"))
)
destroxtix.send_keys("90")

oximetria = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "oximetria"))
)
oximetria.send_keys("98")

temperatura = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "temperatura"))
)
temperatura.send_keys("36.6")

apertura_ojos = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "apertura_ojos_glasgow"))
)
apertura_ojos.send_keys("Espontánea")

respuesta_verbal = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "respuesta_verbal_glasgow"))
)
respuesta_verbal.send_keys("Orientado")

respuesta_motora = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "respuesta_motora_glasgow"))
)
respuesta_motora.send_keys("Obedece órdenes")

campo_marca_vehiculo = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "marca_vehiculo"))
)
select_marca_vehiculo = Select(campo_marca_vehiculo)
opciones_marca = [o.text for o in select_marca_vehiculo.options]
marca_seleccionada = random.choice(opciones_marca[1:])
select_marca_vehiculo.select_by_visible_text(marca_seleccionada)

campo_color = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "color_vehiculo"))
)
colores_disponibles = ["Rojo", "Azul", "Negro", "Blanco", "Gris", "Verde"]
color_seleccionado = random.choice(colores_disponibles)
campo_color.send_keys(color_seleccionado)

campo_placa = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "placa_vehiculo"))
)
letras = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))
numeros = ''.join(random.choices('0123456789', k=3))
placa_generada = f"{letras}{numeros}"
campo_placa.send_keys(placa_generada)

# Campo para descripcion_pertenencias
campo_descripcion_pertenencias = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "descripcion_pertenencias"))
)
campo_descripcion_pertenencias.send_keys("Cartera, teléfono móvil, llaves")

campo_sexo_acompanante = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "sexo_acompanante"))
)
sexo_seleccionado = random.choice(["Masculino", "Femenino"])
campo_sexo_acompanante.send_keys(sexo_seleccionado)

campo_edad = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "edad_acompanante"))
)
edad_seleccionada = str(random.randint(18, 80))  # Edad entre 18 y 80
campo_edad.send_keys(edad_seleccionada)

# Campo para parentesco
campo_parentesco = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "parentesco_acompanante"))
)
parentescos_posibles = ["Padre", "Madre", "Hermano", "Hermana", "Cónyuge", "Hijo", "Hija", "Amigo"]
parentesco_seleccionado = random.choice(parentescos_posibles)
campo_parentesco.send_keys(parentesco_seleccionado)

# Campo para nombre
campo_nombre = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "nombre_acompanante"))
)
nombres_posibles = ["Juan Pérez", "María González", "Carlos López", "Ana Martínez", "Luis Ramírez", "Sofía Torres"]
nombre_seleccionado = random.choice(nombres_posibles)
campo_nombre.send_keys(nombre_seleccionado)

# Campo para domicilio
campo_domicilio = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "domicilio_acompanante"))
)
domicilios_posibles = [
    "Calle 123 #45-67, Bogotá",
    "Avenida Principal 890, Medellín",
    "Carrera 7 #12-34, Cali",
    "Calle Luna 56, Barranquilla"
]
domicilio_seleccionado = random.choice(domicilios_posibles)
campo_domicilio.send_keys(domicilio_seleccionado)
# Mantén el navegador abierto
input("Presiona Enter para cerrar el navegador...")
driver.quit()

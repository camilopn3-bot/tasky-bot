import discord
from discord.ext import commands
import random
from datetime import datetime
import os
from flask import Flask
from threading import Thread

# --- MINI SERVIDOR WEB PARA ENGAÑAR A RENDER ---
app = Flask(__name__)
@app.route('/')
def home():
    return "¡Tasky está vivo y funcionando!"
def run_server():
    app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run_server)
    t.start()

# --- CÓDIGO DE TASKY ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

roles_catering = [
    (
        "**PASTELES Y POSTRES**\n"
        "• Leer los BEOs y anotar el número de orden de Pasteles/Galletas/Brownies/Postres\n"
        "• Preguntar si se ordenaron pasteles y galletas para el día siguiente; si no, hornear galletas y pasteles para el día siguiente\n"
        "• Servir en charola, envolver y etiquetar con el número de orden los pasteles/galletas/brownies/postres del día siguiente\n"
        "• Etiquetar y envolver las cajas de sobrantes de Pasteles/Galletas/Brownies/Postres al final del día (antes de irse a casa)"
    ),
    (
        "**REABASTECIMIENTO DEL ÁREA DE PREPARACIÓN Y SNACKS**\n"
        "• Reabastecer el área de preparación de canastas\n"
        "• Leer los BEOs y anotar el número de orden para el 'Build Your Own Snack' del día siguiente + envolver y etiquetar los snacks para el día siguiente (si aplica)\n"
        "• Organizar y reabastecer el estante de snacks\n"
        "• Hacer inventario de los snacks y avisarle a los líderes qué se está agotando"
    ),
    (
        "**ESTACIÓN DE CAFÉ**\n"
        "• Reabastecer el contenedor de café (regular y descafeinado) + revisar el inventario de café y filtros\n"
        "• Llenar los Cambros de 12 cuartos (1 regular, 1 descafeinado) con filtros de café prellenados y apilarlos dentro del Cambro para un fácil acceso\n"
        "• Llenar y etiquetar las cremeras con la fecha de caducidad, el tipo de leche adentro y el número de orden en la parte inferior del contenedor\n"
        "• Limpiar, desinfectar y organizar la estación de café de catering + los contenedores de crema y las cafeteras"
    ),
    (
        "**BEBIDAS Y REFRIGERADOR GRANDE (WALK-IN)**\n"
        "• Contar las cajas de brownies y asegurarse siempre de que haya 4 regulares y 2 libres de gluten descongelándose en el walk-in. Si hay menos que eso, sacar cajas del congelador y ponerlas en nuestro estante del walk-in.\n"
        "• Reabastecer, consolidar y tirar (si están vacías) todas las cajas de bebidas, incluyendo aguas naturales, aguas minerales, sodas, jugos y tés\n"
        "• Rellenar los estantes de bebidas en el walk-in AL MENOS 4 veces al día y asegurarse de que esté completamente abastecido antes de terminar su turno\n"
        "• Preparar canastas con las bebidas necesarias para la mañana siguiente y etiquetarlas con el número de orden usando cinta y papel"
    ),
    (
        "**SANITIZACIÓN Y MANTENIMIENTO DE ESTACIÓN**\n"
        "• Tomar las cubetas de desinfectante y detergente; rellenar con desinfectante y detergente nuevo cada 2 horas y etiquetarlas con la hora en que se rellenó + iniciales.\n"
        "• Rellenar las toallas secas, guantes si es necesario, caja de pinzas, contenedor de cucharas y el área de preparación de catering\n"
        "• Limpiar cuchillos y soportes (solo 1 cuchillo por soporte)\n"
        "• Lavar y desinfectar el fregadero cada 2 horas; se deben quitar las manchas de café + asegurarse de que no haya comida en el fregadero"
    ),
    (
        "**DECORACIÓN, BLANCOS Y STERNOS**\n"
        "• Guardar la decoración, elevadores y dispensadores / dispensador de té plateado en los estantes que les corresponden + organizar el área\n"
        "• Doblar y envolver los manteles/lienzos y ponerlos en el estante de blancos en el vestidor\n"
        "• Abrir y consolidar las cajas de sternos hasta 3-4 estuches y ponerlos en una canasta + organizar el área de sternos\n"
        "• Poner todos los manteles sucios en bolsas blancas para blancos y moverlos fuera del área de paso"
    )
]

roles_disponibles = roles_catering.copy()
ultimo_dia = datetime.now().date()
active_tasks = {}

@bot.event
async def on_ready():
    print(f'¡Tasky ({bot.user}) está listo en Render!')

@bot.command()
async def task(ctx):
    global roles_disponibles, ultimo_dia
    
    dia_actual = datetime.now().date()
    if dia_actual != ultimo_dia:
        roles_disponibles = roles_catering.copy()
        ultimo_dia = dia_actual
        active_tasks.clear()

    if ctx.author.id in active_tasks:
        await ctx.send(f"🚫 {ctx.author.mention}, ya se te ha asignado una tarea previamente. No podrás pedir una nueva hasta que termines la que se te asignó escribiendo **`!terminar`**.")
        return

    if not roles_disponibles:
        await ctx.send("🚫 ¡Las tareas de hoy ya se han agotado por completo! Vuelve a intentarlo mañana.")
        return

    rol_elegido = random.choice(roles_disponibles)
    roles_disponibles.remove(rol_elegido)
    active_tasks[ctx.author.id] = rol_elegido

    mensaje = (
        f"{ctx.author.mention}, tu tarea asignada es:\n\n{rol_elegido}\n\n"
        "📌 **Nota importante:** Si usted tiene alguna pregunta sobre cómo hacer o dónde encontrar lo que necesita, "
        "por favor verifique con su capitán de catering asignado.\n\n"
        "⚠️ **Aviso de Auditoría:** Recuerde que usted es responsable de adjuntar evidencia de lo realizado según su tarea asignada, "
        "y no es opcional; de lo contrario, debe adjuntar la razón del por qué no realizó su tarea, "
        "así su supervisor y manejador pueden auditar su actividad."
    )
    await ctx.send(mensaje)

@bot.command()
async def terminar(ctx):
    if ctx.author.id in active_tasks:
        del active_tasks[ctx.author.id]
        await ctx.send(f"✅ {ctx.author.mention}, has completado y liberado tu tarea. Ya puedes solicitar una nueva con **`!task`** cuando corresponda.")
    else:
        await ctx.send(f"ℹ️ {ctx.author.mention}, no tienes ninguna tarea activa registrada en este momento.")

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))

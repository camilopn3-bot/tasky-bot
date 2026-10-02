import discord
from discord.ext import commands
import random
from datetime import datetime, timedelta
import os
from flask import Flask
from threading import Thread

# --- MINI SERVIDOR WEB PARA RENDER ---
app = Flask(__name__)
@app.route('/')
def home():
    return "¡Tasky está vivo y funcionando versión PRO Memoria de Tareas!"

def run_server():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_server)
    t.start()

# --- CONFIGURACIÓN DE TASKY ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Permite al bot ver a todos en el servidor
bot = commands.Bot(command_prefix='!', intents=intents)

roles_catering = [
    (
        "**PASTELES Y POSTRES**\n"
        "• Leer los BEOs y anotar el número de orden de Pasteles/Galletas/Brownies/Postres\n"
        "• Preguntar si se ordenaron pasteles y galletas para el día siguiente; si no, hornear para el día siguiente\n"
        "• Servir en charola, envolver y etiquetar con el número de orden los postres del día siguiente\n"
        "• Etiquetar y envolver las cajas de sobrantes de postres al final del día (antes de irse a casa)"
    ),
    (
        "**REABASTECIMIENTO DEL ÁREA DE PREPARACIÓN Y SNACKS**\n"
        "• Reabastecer el área de preparación de canastas\n"
        "• Leer los BEOs y anotar el número de orden para el 'Build Your Own Snack' del día siguiente + envolver y etiquetar\n"
        "• Organizar y reabastecer el estante de snacks\n"
        "• Hacer inventario de los snacks y avisarle a los líderes qué se está agotando"
    ),
    (
        "**ESTACIÓN DE CAFÉ**\n"
        "• Reabastecer el contenedor de café (regular y descafeinado) + revisar inventario\n"
        "• Llenar los Cambros de 12 cuartos con filtros de café prellenados y apilarlos dentro del Cambro\n"
        "• Llenar y etiquetar las cremeras con fecha de caducidad, tipo de leche y número de orden\n"
        "• Limpiar, desinfectar y organizar la estación de café + contenedores y cafeteras"
    ),
    (
        "**BEBIDAS Y REFRIGERADOR GRANDE (WALK-IN)**\n"
        "• Contar cajas de brownies y asegurar siempre 4 regulares y 2 libres de gluten descongelándose.\n"
        "• Reabastecer, consolidar y tirar cajas de bebidas (aguas, sodas, jugos, tés)\n"
        "• Rellenar estantes de bebidas en el walk-in AL MENOS 4 veces al día (debe quedar lleno al irse)\n"
        "• Preparar canastas con las bebidas para la mañana siguiente y etiquetarlas"
    ),
    (
        "**SANITIZACIÓN Y MANTENIMIENTO DE ESTACIÓN**\n"
        "• Tomar cubetas, rellenar con desinfectante y detergente nuevo cada 2 horas (etiquetar con hora e iniciales).\n"
        "• Rellenar toallas secas, guantes, caja de pinzas, cucharas y área de preparación\n"
        "• Limpiar cuchillos y soportes (solo 1 cuchillo por soporte)\n"
        "• Lavar y desinfectar el fregadero cada 2 horas; sin manchas ni restos de comida"
    ),
    (
        "**DECORACIÓN, BLANCOS Y STERNOS**\n"
        "• Guardar decoración, elevadores y dispensadores en sus estantes + organizar el área\n"
        "• Doblar y envolver manteles/lienzos y ponerlos en el estante del vestidor\n"
        "• Abrir y consolidar cajas de sternos (hasta 3-4 estuches en canasta) + organizar área\n"
        "• Poner todos los manteles sucios en bolsas blancas y moverlos fuera del paso"
    )
]

roles_disponibles = roles_catering.copy()
usuarios_estado = {} # Ahora guardará el estado Y la tarea específica

def obtener_fecha_california():
    hora_utc = datetime.utcnow()
    hora_california = hora_utc - timedelta(hours=7)
    return hora_california.date()

ultimo_dia = obtener_fecha_california()

def verificar_cambio_de_dia():
    global roles_disponibles, ultimo_dia, usuarios_estado
    dia_actual = obtener_fecha_california()
    if dia_actual != ultimo_dia:
        roles_disponibles = roles_catering.copy()
        ultimo_dia = dia_actual
        usuarios_estado.clear()

async def motor_asignar_tarea(ctx, miembro: discord.Member):
    global roles_disponibles, usuarios_estado
    
    if miembro.id in usuarios_estado:
        estado = usuarios_estado[miembro.id]["estado"]
        titulo = usuarios_estado[miembro.id]["tarea"].split('\n')[0] # Saca solo el título de la tarea
        if estado == "pendiente":
            await ctx.send(f"🚫 {miembro.mention} ya tiene una tarea asignada hoy / already has a task today: {titulo}")
        elif estado == "terminada":
            await ctx.send(f"✅ {miembro.mention} ya completó su tarea del día / already completed today's task: {titulo}")
        return False

    if not roles_disponibles:
        await ctx.send(f"🚫 ¡Las tareas de hoy se han agotado! / Tasks are sold out! No pude asignarle a {miembro.mention}.")
        return False

    rol_elegido = random.choice(roles_disponibles)
    roles_disponibles.remove(rol_elegido) # ¡AQUÍ SE BORRA LA TAREA DEL DÍA!
    
    # Se guarda que está pendiente y QUÉ tarea le tocó
    usuarios_estado[miembro.id] = {"estado": "pendiente", "tarea": rol_elegido}

    mensaje = (
        f"{miembro.mention}, tu tarea asignada es:\n\n{rol_elegido}\n\n"
        "📌 **Nota importante:** Si usted tiene alguna pregunta sobre cómo hacer o dónde encontrar lo que necesita, "
        "por favor verifique con su capitán de catering asignado.\n\n"
        "⚠️ **Aviso de Auditoría / Audit Notice:** Recuerde que usted es responsable de adjuntar evidencia de lo realizado según su tarea asignada, "
        "y no es opcional; de lo contrario, debe adjuntar la razón del por qué no realizó su tarea."
    )
    await ctx.send(mensaje)
    return True

@bot.event
async def on_ready():
    print(f'¡Tasky ({bot.user}) conectado y con Memoria Activa!')

# ----------------------------------------------------
# COMANDOS REGULARES PARA EL EQUIPO (!task, !tarea)
# ----------------------------------------------------
@bot.command(aliases=['tarea'])
async def task(ctx, *, argumento: str = None):
    verificar_cambio_de_dia()
    
    if argumento and argumento.lower() in ["terminada", "terminado", "terminar", "done"]:
        await ctx.invoke(bot.get_command('terminar'))
        return
        
    if ctx.message.mentions:
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("🚫 Solo los administradores pueden asignar tareas a otras personas / Only admins can assign tasks.")
            return
        
        for miembro in ctx.message.mentions:
            await motor_asignar_tarea(ctx, miembro)
        return

    await motor_asignar_tarea(ctx, ctx.author)

# ----------------------------------------------------
# COMANDO PARA TERMINAR (!terminar, !done)
# ----------------------------------------------------
@bot.command(aliases=['done', 'listo'])
async def terminar(ctx):
    verificar_cambio_de_dia()
    
    if ctx.author.id in usuarios_estado:
        if usuarios_estado[ctx.author.id]["estado"] == "pendiente":
            usuarios_estado[ctx.author.id]["estado"] = "terminada"
            
            mensaje_rojo = (
                f"✅ {ctx.author.mention}, has marcado tu tarea como completada. ¡Buen trabajo! Quedas liberado por hoy.\n\n"
                "```ansi\n"
                "\u001b[1;31m🛑 POR FAVOR ASEGÚRATE DE HACER CHECK OUT CON TU SUPERVISOR ANTES DE IRTE A CASA / PLEASE MAKE SURE TO CHECK OUT WITH YOUR SUPERVISOR BEFORE LEAVING 🛑\u001b[0m\n"
                "```"
            )
            await ctx.send(mensaje_rojo)
        else:
            titulo = usuarios_estado[ctx.author.id]["tarea"].split('\n')[0]
            await ctx.send(f"ℹ️ {ctx.author.mention}, ya habías marcado tu tarea como completada / you already completed your task: {titulo}")
    else:
        await ctx.send(f"ℹ️ {ctx.author.mention}, no tienes ninguna tarea asignada el día de hoy / you have no task assigned today.")

# ----------------------------------------------------
# COMANDO INTELIGENTE PARA MANAGERS (!assign, !repartir)
# ----------------------------------------------------
@bot.command(aliases=['assign', 'asignartodos'])
@commands.has_permissions(administrator=True)
async def repartir(ctx):
    verificar_cambio_de_dia()
    
    if not roles_disponibles:
        await ctx.send("🚫 No quedan tareas disponibles para repartir / No tasks left to assign.")
        return

    if not ctx.message.mentions and not ctx.message.role_mentions:
        await ctx.send("🚫 Debes mencionar a quién quieres asignarle tareas. Ejemplo: `!assign @Team` o `!assign @Milo`")
        return

    miembros_a_asignar = set()
    ya_tienen_tarea = set()

    for rol in ctx.message.role_mentions:
        for miembro in rol.members:
            if not miembro.bot:
                if miembro.id not in usuarios_estado:
                    miembros_a_asignar.add(miembro)
                else:
                    ya_tienen_tarea.add(miembro)

    for miembro in ctx.message.mentions:
        if not miembro.bot:
            if miembro.id not in usuarios_estado:
                miembros_a_asignar.add(miembro)
            else:
                ya_tienen_tarea.add(miembro)

    # Si alguien ya tenía tarea, se lo avisamos a la jefa mostrándole el título
    if ya_tienen_tarea:
        mensajes_ya_tienen = []
        for m in ya_tienen_tarea:
            titulo = usuarios_estado[m.id]["tarea"].split('\n')[0]
            estado_texto = "Completada" if usuarios_estado[m.id]["estado"] == "terminada" else "Pendiente"
            mensajes_ya_tienen.append(f"• {m.mention}: {titulo} ({estado_texto})")
            
        texto_aviso = "ℹ️ **Aviso / Notice:** Los siguientes miembros ya tenían una tarea asignada previamente:\n" + "\n".join(mensajes_ya_tienen)
        await ctx.send(texto_aviso)

    miembros_lista = list(miembros_a_asignar)

    if not miembros_lista:
        await ctx.send("ℹ️ No hay miembros libres sin tarea para asignar en este momento / No available members without tasks to assign.")
        return

    await ctx.send("🎲 **¡Repartiendo las tareas restantes al azar / Assigning random tasks!** 🎲")
    
    random.shuffle(miembros_lista)
    asignados = 0
    
    for miembro in miembros_lista:
        if not roles_disponibles:
            break
        exito = await motor_asignar_tarea(ctx, miembro)
        if exito:
            asignados += 1
            
    await ctx.send(f"✅ Se han asignado {asignados} tareas automáticas al equipo / {asignados} tasks successfully assigned.")

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))

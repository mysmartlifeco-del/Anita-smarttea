"""
ANITA - ASISTENTE PERSONAL DE ANA MILENA GÓMEZ
Sistema Omnicanal de Gestión de Redes Sociales

Gestiona: Instagram DM, Facebook Messenger, TikTok DM, Comentarios Públicos
Objetivo: Canalización masiva a WhatsApp

Autor: SmartTea® Detox SAS
Versión: 1.0.0
"""

import os
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum
import anthropic
from dotenv import load_dotenv

load_dotenv()


class TipoCanal(Enum):
    """Tipos de canales de comunicación"""
    INSTAGRAM_DM = "instagram_dm"
    FACEBOOK_MESSENGER = "facebook_messenger"
    TIKTOK_DM = "tiktok_dm"
    COMENTARIO_PUBLICO = "comentario_publico"
    COMENTARIO_PAUTA = "comentario_pauta"


class SentimientoComentario(Enum):
    """Clasificación de sentimiento"""
    POSITIVO = "positivo"
    NEGATIVO = "negativo"
    NEUTRO = "neutro"
    DUDA = "duda"
    PRECIO = "precio"


class AgenteAnita:
    """
    Agente ANITA - Asistente Personal de Ana Milena Gómez
    Gestión omnicanal de redes sociales con canalización a WhatsApp
    """
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("❌ ANTHROPIC_API_KEY no encontrada en .env")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"
        
        # Configuración
        self.nombre = "Anita"
        self.gerente = "Ana Milena Gómez"
        self.whatsapp_url = "https://wa.me/573105056737"
        self.kommo_template_video = "1517745476065875"
        
        # Estadísticas
        self.interacciones = {
            "comentarios_publicos": 0,
            "mensajes_privados": 0,
            "canalizaciones_whatsapp": 0,
            "crisis_manejadas": 0
        }
        
        print(f"✅ Agente ANITA inicializado")
        print(f"👤 Asistente de: {self.gerente}")
        print(f"📱 WhatsApp: {self.whatsapp_url}")
    
    def _construir_prompt_sistema(self) -> str:
        """Construye el prompt del sistema para ANITA"""
        return f"""Eres ANITA, la asistente personal de la Gerente Ana Milena Gómez de SmartTea® Detox SAS.

# IDENTIDAD Y MISIÓN
- Nombre: Anita
- Rol: Asistente Personal de Ana Milena Gómez
- Misión: Gestionar TODA la interacción en redes sociales y canalizar a WhatsApp
- Filosofía: "Hacemos castillos con las piedras" - Transforma quejas en soluciones

# ALCANCE OPERATIVO (OMNICANAL)
Respondes en:
- ✅ Mensajes Directos (DM) de Instagram y TikTok
- ✅ Inbox / Messenger de Facebook
- ✅ Comentarios en posts orgánicos y anuncios de Pauta

# PERSONALIDAD
- Tono: Humano, cálido, profesional y clínico
- Presentación: "Hola, soy Anita, la asistente personal de Ana Milena Gómez"
- Actitud: Empática, solucionadora, orientada a resultados
- Estilo: Cercana pero profesional, usa emojis con moderación

# PROTOCOLO DE RESPUESTA A COMENTARIOS PÚBLICOS

Analiza el sentimiento ANTES de responder:

## 1. COMENTARIO POSITIVO/ELOGIO:
```
¡Qué alegría! 😍 Soy Anita, la asistente de la gerente. 
Te dejé un detalle profesional en tu privado para que sigamos creciendo. 
¡Revísalo!
```

## 2. COMENTARIO NEGATIVO/CRÍTICA:
```
Entiendo tu posición. Soy Anita, la asistente de la gerente. 
Para Ana Milena tu experiencia es prioridad; te acabo de escribir al 
privado para darte una solución directa. ¡Estamos contigo!
```

## 3. DUDA/PREGUNTA/INFO:
```
¡Hola! Es un gusto. Soy Anita. Te envié el protocolo técnico de 
Reseteo Biológico al privado para que veas los beneficios en cabina. 
¡Echa un vistazo!
```

## 4. PREGUNTA POR PRECIO:
```
¡Hola! Soy Anita. Por exclusividad del gremio, los márgenes y valores 
se manejan únicamente por nuestra línea privada. Te escribí al privado 
con la información técnica. ¡Revísala!
```

# PROTOCOLO DE CONVERSIÓN EN DM (PRIVADO)

Flujo de 4 pasos para canalizar a WhatsApp:

## PASO 1: Saludo Humano
```
¡Hola! ¿Cómo estás? Es un placer saludarte. 

Soy Anita, la asistente personal de nuestra gerente Ana Milena Gómez. 
Para nosotros eres muy importante.
```

## PASO 2: Video Nativo (Plantilla Kommo)
```
[EJECUTAR: Envío de PLANTILLA ID: {self.kommo_template_video}]
```

## PASO 3: Texto de Apoyo
```
Antes de hablar con la gerente, ella quiere que veas nuestro producto 
Premium: la Fase Cero® SmartTea. 

Mira este video sobre el Reseteo Biológico que desinflama mucosas y 
prepara la microbiota. Es el protocolo que está revolucionando el gremio.
```

## PASO 4: Canalización a WhatsApp
```
Ana Milena está atendiendo al gremio, pero le pedí que te dé prioridad. 

Dale clic aquí para recibir el catálogo técnico y beneficios VIP:
{self.whatsapp_url}

¿Te parece bien que te contacte por ahí? 😊
```

# RESTRICCIONES TÉCNICAS (BLINDAJE)

⛔ PROHIBIDO:
1. Dar precios por redes sociales o comentarios públicos
2. Mencionar la palabra "video" en comentarios públicos (di "información técnica" o "detalle")
3. Compartir listas de precios fuera de WhatsApp
4. Dar información de cuenta bancaria por redes sociales

✅ PERMITIDO:
1. Hablar del Protocolo Fase Cero®
2. Mencionar "Reseteo Biológico"
3. Hablar de beneficios clínicos
4. Canalizar a WhatsApp para información comercial

# MANEJO DE CRISIS

Si detectas:
- Queja grave
- Problema con producto
- Insatisfacción del cliente
- Comentario negativo viral

Responde con:
```
Entiendo perfectamente tu situación y lamento que hayas tenido esta 
experiencia. Soy Anita, la asistente de Ana Milena Gómez.

Tu caso es prioridad para nosotros. Te acabo de escribir al privado 
para darte una solución inmediata y personalizada.

Estamos comprometidos con tu satisfacción. 💚
```

# FORMATO DE RESPUESTA

Siempre estructura tus respuestas así:

1. **Identificación del canal** (público/privado)
2. **Análisis de sentimiento** (si es comentario público)
3. **Respuesta apropiada** según el protocolo
4. **Acción de seguimiento** (enviar DM, canalizar WhatsApp)

# REGLAS DE COMUNICACIÓN

1. **Sé humana** - No suenes como bot
2. **Sé empática** - Entiende la emoción del usuario
3. **Sé breve en público** - Comentarios cortos y directos
4. **Sé completa en privado** - DMs con información detallada
5. **Canaliza siempre** - El objetivo final es WhatsApp
6. **Usa emojis** - Con moderación y contexto apropiado
7. **Menciona a Ana Milena** - Genera autoridad y confianza

¡Tu misión es convertir cada interacción en una oportunidad de negocio! 🚀"""

    def analizar_sentimiento(self, texto: str) -> SentimientoComentario:
        """
        Analiza el sentimiento de un comentario
        
        Args:
            texto: Texto del comentario
        
        Returns:
            SentimientoComentario clasificado
        """
        texto_lower = texto.lower()
        
        # Palabras clave para clasificación
        palabras_positivas = ["excelente", "gracias", "genial", "perfecto", "increíble", 
                             "maravilloso", "funciona", "resultados", "recomiendo", "amor"]
        palabras_negativas = ["malo", "terrible", "estafa", "no funciona", "decepción",
                             "fraude", "mentira", "devolver", "queja", "problema"]
        palabras_precio = ["precio", "costo", "cuanto", "cuánto", "valor", "pagar",
                          "inversión", "cuánto cuesta", "cuanto vale"]
        palabras_duda = ["cómo", "como", "dónde", "donde", "cuándo", "cuando",
                        "qué", "que", "funciona", "sirve", "ayuda"]
        
        # Clasificación por prioridad
        if any(palabra in texto_lower for palabra in palabras_precio):
            return SentimientoComentario.PRECIO
        elif any(palabra in texto_lower for palabra in palabras_negativas):
            return SentimientoComentario.NEGATIVO
        elif any(palabra in texto_lower for palabra in palabras_positivas):
            return SentimientoComentario.POSITIVO
        elif any(palabra in texto_lower for palabra in palabras_duda):
            return SentimientoComentario.DUDA
        else:
            return SentimientoComentario.NEUTRO
    
    def generar_respuesta_comentario_publico(self, comentario: str, 
                                            sentimiento: Optional[SentimientoComentario] = None) -> str:
        """
        Genera respuesta para comentario público según sentimiento
        
        Args:
            comentario: Texto del comentario
            sentimiento: Sentimiento detectado (opcional, se analiza si no se provee)
        
        Returns:
            Respuesta apropiada para comentario público
        """
        if not sentimiento:
            sentimiento = self.analizar_sentimiento(comentario)
        
        self.interacciones["comentarios_publicos"] += 1
        
        if sentimiento == SentimientoComentario.POSITIVO:
            return (
                "¡Qué alegría! 😍 Soy Anita, la asistente de la gerente. "
                "Te dejé un detalle profesional en tu privado para que sigamos creciendo. "
                "¡Revísalo!"
            )
        
        elif sentimiento == SentimientoComentario.NEGATIVO:
            self.interacciones["crisis_manejadas"] += 1
            return (
                "Entiendo tu posición. Soy Anita, la asistente de la gerente. "
                "Para Ana Milena tu experiencia es prioridad; te acabo de escribir al "
                "privado para darte una solución directa. ¡Estamos contigo!"
            )
        
        elif sentimiento == SentimientoComentario.PRECIO:
            return (
                "¡Hola! Soy Anita. Por exclusividad del gremio, los márgenes y valores "
                "se manejan únicamente por nuestra línea privada. Te escribí al privado "
                "con la información técnica. ¡Revísala!"
            )
        
        elif sentimiento == SentimientoComentario.DUDA:
            return (
                "¡Hola! Es un gusto. Soy Anita. Te envié el protocolo técnico de "
                "Reseteo Biológico al privado para que veas los beneficios en cabina. "
                "¡Echa un vistazo!"
            )
        
        else:  # NEUTRO
            return (
                "¡Hola! Soy Anita, la asistente de Ana Milena Gómez. "
                "Te envié información detallada al privado. ¡Revísala! 😊"
            )
    
    def generar_mensaje_dm_inicial(self, nombre_usuario: Optional[str] = None) -> Dict:
        """
        Genera el mensaje inicial para DM (flujo de 4 pasos)
        
        Args:
            nombre_usuario: Nombre del usuario (opcional)
        
        Returns:
            Dict con los 4 pasos del flujo
        """
        self.interacciones["mensajes_privados"] += 1
        
        saludo = f"¡Hola{' ' + nombre_usuario if nombre_usuario else ''}! ¿Cómo estás?"
        
        return {
            "paso_1_saludo": f"""{saludo} Es un placer saludarte.

Soy Anita, la asistente personal de nuestra gerente Ana Milena Gómez. 
Para nosotros eres muy importante.""",
            
            "paso_2_video": {
                "accion": "ENVIAR_PLANTILLA_KOMMO",
                "template_id": self.kommo_template_video,
                "nota": "Enviar video nativo de Fase Cero® desde Kommo"
            },
            
            "paso_3_contexto": """Antes de hablar con la gerente, ella quiere que veas nuestro producto Premium: la Fase Cero® SmartTea.

Mira este video sobre el Reseteo Biológico que desinflama mucosas y prepara la microbiota. Es el protocolo que está revolucionando el gremio.""",
            
            "paso_4_canalizacion": f"""Ana Milena está atendiendo al gremio, pero le pedí que te dé prioridad.

Dale clic aquí para recibir el catálogo técnico y beneficios VIP:
{self.whatsapp_url}

¿Te parece bien que te contacte por ahí? 😊"""
        }
    
    def procesar_interaccion(self, mensaje: str, canal: TipoCanal, 
                            nombre_usuario: Optional[str] = None) -> Dict:
        """
        Procesa una interacción completa según el canal
        
        Args:
            mensaje: Mensaje del usuario
            canal: Tipo de canal (DM o comentario público)
            nombre_usuario: Nombre del usuario (opcional)
        
        Returns:
            Dict con respuesta y acciones a tomar
        """
        resultado = {
            "canal": canal.value,
            "mensaje_original": mensaje,
            "timestamp": datetime.now().isoformat(),
            "usuario": nombre_usuario
        }
        
        # Si es comentario público
        if canal in [TipoCanal.COMENTARIO_PUBLICO, TipoCanal.COMENTARIO_PAUTA]:
            sentimiento = self.analizar_sentimiento(mensaje)
            respuesta_publica = self.generar_respuesta_comentario_publico(mensaje, sentimiento)
            mensaje_dm = self.generar_mensaje_dm_inicial(nombre_usuario)
            
            resultado.update({
                "sentimiento": sentimiento.value,
                "respuesta_publica": respuesta_publica,
                "mensaje_dm": mensaje_dm,
                "accion": "RESPONDER_PUBLICO_Y_ENVIAR_DM"
            })
        
        # Si es mensaje directo
        else:
            mensaje_dm = self.generar_mensaje_dm_inicial(nombre_usuario)
            self.interacciones["canalizaciones_whatsapp"] += 1
            
            resultado.update({
                "mensaje_dm": mensaje_dm,
                "accion": "ENVIAR_FLUJO_DM_COMPLETO"
            })
        
        return resultado
    
    def generar_respuesta_ia(self, mensaje: str, contexto: Optional[str] = None) -> str:
        """
        Genera una respuesta personalizada usando IA para casos especiales
        
        Args:
            mensaje: Mensaje del usuario
            contexto: Contexto adicional (opcional)
        
        Returns:
            Respuesta generada por IA
        """
        prompt_usuario = f"""Mensaje del usuario: {mensaje}

{f'Contexto: {contexto}' if contexto else ''}

Genera una respuesta apropiada siguiendo el protocolo de ANITA."""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                system=self._construir_prompt_sistema(),
                messages=[{
                    "role": "user",
                    "content": prompt_usuario
                }]
            )
            
            return response.content[0].text
        
        except Exception as e:
            print(f"❌ Error al generar respuesta IA: {str(e)}")
            return self.generar_mensaje_dm_inicial()["paso_1_saludo"]
    
    def obtener_estadisticas(self) -> Dict:
        """Retorna estadísticas de interacciones"""
        total = sum(self.interacciones.values())
        
        return {
            **self.interacciones,
            "total_interacciones": total,
            "tasa_canalizacion": (
                (self.interacciones["canalizaciones_whatsapp"] / total * 100)
                if total > 0 else 0
            )
        }
    
    def generar_reporte(self) -> str:
        """Genera reporte de actividad"""
        stats = self.obtener_estadisticas()
        
        reporte = "=" * 60 + "\n"
        reporte += "📊 REPORTE DE ACTIVIDAD - ANITA\n"
        reporte += "=" * 60 + "\n\n"
        reporte += f"👤 Asistente de: {self.gerente}\n"
        reporte += f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        reporte += "📈 ESTADÍSTICAS:\n"
        reporte += f"   💬 Comentarios públicos: {stats['comentarios_publicos']}\n"
        reporte += f"   📨 Mensajes privados: {stats['mensajes_privados']}\n"
        reporte += f"   📱 Canalizaciones WhatsApp: {stats['canalizaciones_whatsapp']}\n"
        reporte += f"   🔴 Crisis manejadas: {stats['crisis_manejadas']}\n"
        reporte += f"   📊 Total interacciones: {stats['total_interacciones']}\n"
        reporte += f"   ✅ Tasa canalización: {stats['tasa_canalizacion']:.1f}%\n"
        reporte += "\n" + "=" * 60 + "\n"
        
        return reporte


def main():
    """Función principal para probar el agente ANITA"""
    print("=" * 60)
    print("👤 ANITA - ASISTENTE PERSONAL ANA MILENA GÓMEZ")
    print("=" * 60)
    print()
    
    # Inicializar agente
    anita = AgenteAnita()
    
    print("\n📋 COMANDOS DISPONIBLES:")
    print("  - Escribe un comentario o mensaje para simular")
    print("  - 'stats' - Ver estadísticas")
    print("  - 'reporte' - Generar reporte completo")
    print("  - 'salir' - Cerrar el sistema")
    print()
    
    while True:
        try:
            # Menú de selección de canal
            print("\n" + "=" * 60)
            print("SELECCIONA EL CANAL:")
            print("1. Comentario Público (Instagram/Facebook)")
            print("2. Comentario en Pauta")
            print("3. Mensaje Directo (DM)")
            print("4. Ver estadísticas")
            print("5. Salir")
            print("=" * 60)
            
            opcion = input("\nOpción: ").strip()
            
            if opcion == "5" or opcion.lower() == "salir":
                print("\n" + anita.generar_reporte())
                print("👋 Cerrando ANITA...")
                break
            
            elif opcion == "4" or opcion.lower() == "stats":
                print("\n" + anita.generar_reporte())
                continue
            
            elif opcion in ["1", "2", "3"]:
                # Obtener mensaje del usuario
                mensaje = input("\n💬 Mensaje del usuario: ").strip()
                
                if not mensaje:
                    continue
                
                nombre = input("👤 Nombre del usuario (opcional): ").strip() or None
                
                # Determinar canal
                if opcion == "1":
                    canal = TipoCanal.COMENTARIO_PUBLICO
                elif opcion == "2":
                    canal = TipoCanal.COMENTARIO_PAUTA
                else:
                    canal = TipoCanal.INSTAGRAM_DM
                
                # Procesar interacción
                print("\n⏳ Procesando...")
                resultado = anita.procesar_interaccion(mensaje, canal, nombre)
                
                # Mostrar resultado
                print(f"\n{'='*60}")
                print(f"📍 CANAL: {resultado['canal'].upper()}")
                print(f"{'='*60}")
                
                if "sentimiento" in resultado:
                    print(f"\n🎭 SENTIMIENTO DETECTADO: {resultado['sentimiento'].upper()}")
                
                if "respuesta_publica" in resultado:
                    print(f"\n📢 RESPUESTA PÚBLICA:")
                    print(f"   {resultado['respuesta_publica']}")
                
                if "mensaje_dm" in resultado:
                    print(f"\n📨 MENSAJE PRIVADO (DM):")
                    print(f"\n   PASO 1 - Saludo:")
                    print(f"   {resultado['mensaje_dm']['paso_1_saludo']}")
                    print(f"\n   PASO 2 - Video:")
                    print(f"   {resultado['mensaje_dm']['paso_2_video']['nota']}")
                    print(f"   Template ID: {resultado['mensaje_dm']['paso_2_video']['template_id']}")
                    print(f"\n   PASO 3 - Contexto:")
                    print(f"   {resultado['mensaje_dm']['paso_3_contexto']}")
                    print(f"\n   PASO 4 - Canalización WhatsApp:")
                    print(f"   {resultado['mensaje_dm']['paso_4_canalizacion']}")
                
                print(f"\n✅ ACCIÓN: {resultado['accion']}")
            
            else:
                print("❌ Opción inválida")
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrumpido por usuario")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()

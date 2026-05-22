"""
🔥 AGENTE ANITA - LEADS FRÍOS CON SINCRONIZACIÓN
Maneja la respuesta automática a leads fríos de WhatsApp con delay de sincronización
"""

import os
import time
import requests
import anthropic
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
KOMMO_ACCESS_TOKEN = os.getenv("KOMMO_ACCESS_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
KOMMO_BASE_URL = "https://infosmartteadetoxcom.kommo.com/api/v4"

# IDs de Kommo (actualizar con tus valores reales)
PIPELINE_PLAN_VIP = 8588506
STATUS_CONVERSACIONES_NUEVAS = 67668394
FIELD_ID_AGENTE = 123456  # Cambiar por tu field_id real
FIELD_ID_FECHA_CONTACTO = 123457  # Cambiar por tu field_id real

# Configuración de delay
DELAY_SINCRONIZACION = 8  # segundos


class AnitaLeadsFrios:
    """Agente ANITA para responder a leads fríos con sincronización"""
    
    def __init__(self):
        self.kommo_headers = {
            "Authorization": f"Bearer {KOMMO_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        self.anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
    def log(self, mensaje: str, nivel: str = "INFO"):
        """Log con timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{nivel}] {mensaje}")
    
    def esperar_sincronizacion(self, segundos: int = DELAY_SINCRONIZACION):
        """
        Espera crítica para que Kommo termine de sincronizar el lead
        """
        self.log(f"⏱️ Esperando {segundos} segundos para sincronización de Kommo...")
        time.sleep(segundos)
        self.log("✅ Sincronización completada")
    
    def obtener_lead_completo(self, lead_id: int) -> Optional[Dict]:
        """
        Obtiene el lead completo con contactos desde Kommo
        """
        try:
            url = f"{KOMMO_BASE_URL}/leads/{lead_id}?with=contacts"
            response = requests.get(url, headers=self.kommo_headers)
            response.raise_for_status()
            
            lead = response.json()
            self.log(f"✅ Lead {lead_id} obtenido correctamente")
            return lead
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Error obteniendo lead {lead_id}: {str(e)}", "ERROR")
            return None
    
    def extraer_datos_contacto(self, lead: Dict) -> Tuple[Optional[int], Optional[str], Optional[str]]:
        """
        Extrae contact_id, nombre y teléfono del lead
        Retorna: (contact_id, nombre, telefono)
        """
        try:
            contacts = lead.get("_embedded", {}).get("contacts", [])
            
            if not contacts:
                self.log("⚠️ Lead sin contactos asociados", "WARNING")
                return None, None, None
            
            contact = contacts[0]
            contact_id = contact.get("id")
            contact_name = contact.get("name", "Cliente")
            
            # Buscar el campo de teléfono
            phone_number = None
            custom_fields = contact.get("custom_fields_values", [])
            
            for field in custom_fields:
                if field.get("field_code") == "PHONE":
                    values = field.get("values", [])
                    if values:
                        phone_number = values[0].get("value", "")
                        # Limpiar el número (quitar espacios, guiones, paréntesis)
                        phone_number = ''.join(filter(lambda x: x.isdigit() or x == '+', phone_number))
                        break
            
            self.log(f"📞 Contacto extraído: {contact_name} - {phone_number}")
            return contact_id, contact_name, phone_number
            
        except Exception as e:
            self.log(f"❌ Error extrayendo datos del contacto: {str(e)}", "ERROR")
            return None, None, None
    
    def buscar_duplicados(self, phone_number: str, lead_id_actual: int) -> Tuple[bool, int, Optional[Dict]]:
        """
        Busca si el teléfono ya existe en otros leads
        Retorna: (es_duplicado, cantidad_duplicados, info_duplicado)
        """
        try:
            url = f"{KOMMO_BASE_URL}/contacts"
            params = {"query": phone_number}
            response = requests.get(url, headers=self.kommo_headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            contacts = data.get("_embedded", {}).get("contacts", [])
            
            # Filtrar contactos que tengan leads diferentes al actual
            duplicados = []
            for contact in contacts:
                leads = contact.get("_embedded", {}).get("leads", [])
                for lead in leads:
                    if lead.get("id") != lead_id_actual:
                        duplicados.append({
                            "contact_id": contact.get("id"),
                            "contact_name": contact.get("name"),
                            "lead_id": lead.get("id"),
                            "lead_name": lead.get("name"),
                            "pipeline_id": lead.get("pipeline_id"),
                            "status_id": lead.get("status_id")
                        })
            
            es_duplicado = len(duplicados) > 0
            
            if es_duplicado:
                self.log(f"⚠️ DUPLICADO DETECTADO: {len(duplicados)} lead(s) existente(s)", "WARNING")
            else:
                self.log("✅ Lead nuevo verificado (no duplicado)")
            
            return es_duplicado, len(duplicados), duplicados[0] if duplicados else None
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Error buscando duplicados: {str(e)}", "ERROR")
            return False, 0, None
    
    def obtener_chat_id(self, phone_number: str) -> Optional[str]:
        """
        Obtiene el chat_id de WhatsApp para el número de teléfono
        """
        try:
            url = f"{KOMMO_BASE_URL}/chats"
            params = {"filter[chat_id]": phone_number}
            response = requests.get(url, headers=self.kommo_headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            chats = data.get("_embedded", {}).get("chats", [])
            
            if chats:
                chat_id = chats[0].get("id")
                self.log(f"✅ Chat ID obtenido: {chat_id}")
                return chat_id
            else:
                self.log("⚠️ Chat de WhatsApp no encontrado", "WARNING")
                return None
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Error obteniendo chat_id: {str(e)}", "ERROR")
            return None
    
    def generar_respuesta_anita(self, nombre_contacto: str) -> str:
        """
        Genera respuesta personalizada usando Claude Sonnet 4
        """
        try:
            self.log(f"🤖 Generando respuesta para {nombre_contacto}...")
            
            system_prompt = """Eres ANITA, la asistente virtual de SmartTea Detox. Tu misión es dar la bienvenida cálida a esteticistas que escriben por primera vez desde anuncios de Facebook/Instagram.

CONTEXTO:
- La persona acaba de ver un anuncio sobre el Plan VIP para Esteticistas
- Es su primer contacto con SmartTea
- Necesitas calificarla rápidamente y agendar una llamada

TONO:
- Cálido, profesional y entusiasta
- Usa emojis moderadamente (2-3 por mensaje)
- Mensajes cortos (máximo 3 líneas)
- Tutea siempre

ESTRUCTURA DEL MENSAJE:
1. Saludo personalizado con su nombre
2. Confirmar que vio el anuncio del Plan VIP
3. Pregunta de calificación: ¿Tiene centro de estética o trabaja independiente?
4. Mencionar beneficio clave: Descuentos hasta 40% + capacitación

NO MENCIONES:
- Precios específicos
- Detalles técnicos del producto
- Promociones que no conozcas"""

            message = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Genera un mensaje de bienvenida para {nombre_contacto}. Es una esteticista que acaba de escribir por WhatsApp desde un anuncio de Facebook sobre el Plan VIP para Esteticistas."
                    }
                ]
            )
            
            respuesta = message.content[0].text
            self.log(f"✅ Respuesta generada: {respuesta[:50]}...")
            return respuesta
            
        except Exception as e:
            self.log(f"❌ Error generando respuesta con Claude: {str(e)}", "ERROR")
            # Respuesta de fallback
            return f"¡Hola {nombre_contacto}! 👋 Gracias por tu interés en el Plan VIP para Esteticistas. ¿Tienes centro de estética o trabajas independiente? 💼✨"
    
    def enviar_mensaje_whatsapp(self, chat_id: str, mensaje: str) -> bool:
        """
        Envía mensaje a WhatsApp vía Kommo
        """
        try:
            url = f"{KOMMO_BASE_URL}/chats/{chat_id}/messages"
            payload = {"text": mensaje}
            
            response = requests.post(url, headers=self.kommo_headers, json=payload)
            response.raise_for_status()
            
            self.log("✅ Mensaje enviado a WhatsApp correctamente")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Error enviando mensaje a WhatsApp: {str(e)}", "ERROR")
            return False
    
    def crear_nota_kommo(self, lead_id: int, texto: str) -> bool:
        """
        Crea una nota en el lead de Kommo
        """
        try:
            url = f"{KOMMO_BASE_URL}/leads/{lead_id}/notes"
            payload = {
                "note_type": "common",
                "params": {
                    "text": texto
                }
            }
            
            response = requests.post(url, headers=self.kommo_headers, json=payload)
            response.raise_for_status()
            
            self.log("✅ Nota creada en Kommo")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Error creando nota en Kommo: {str(e)}", "ERROR")
            return False
    
    def etiquetar_lead(self, lead_id: int, agente: str, timestamp: str) -> bool:
        """
        Actualiza campos personalizados del lead
        """
        try:
            url = f"{KOMMO_BASE_URL}/leads/{lead_id}"
            payload = {
                "custom_fields_values": [
                    {
                        "field_id": FIELD_ID_AGENTE,
                        "values": [{"value": agente}]
                    },
                    {
                        "field_id": FIELD_ID_FECHA_CONTACTO,
                        "values": [{"value": timestamp}]
                    }
                ]
            }
            
            response = requests.patch(url, headers=self.kommo_headers, json=payload)
            response.raise_for_status()
            
            self.log("✅ Lead etiquetado correctamente")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Error etiquetando lead: {str(e)}", "ERROR")
            return False
    
    def procesar_lead_frio(self, lead_id: int, pipeline_id: int, status_id: int) -> Dict:
        """
        Procesa un lead frío completo con toda la lógica de sincronización
        
        Retorna un diccionario con el resultado del procesamiento
        """
        resultado = {
            "success": False,
            "lead_id": lead_id,
            "reason": None,
            "message": None,
            "anita_responded": False
        }
        
        self.log(f"\n{'='*60}")
        self.log(f"🔥 PROCESANDO LEAD FRÍO: {lead_id}")
        self.log(f"{'='*60}")
        
        # 1. Verificar pipeline y etapa
        if pipeline_id != PIPELINE_PLAN_VIP or status_id != STATUS_CONVERSACIONES_NUEVAS:
            self.log(f"⚠️ Lead no está en el pipeline/etapa correcta", "WARNING")
            resultado["reason"] = "wrong_pipeline"
            resultado["message"] = "Lead no está en el pipeline correcto"
            return resultado
        
        # 2. DELAY CRÍTICO: Esperar sincronización de Kommo
        self.esperar_sincronizacion()
        
        # 3. Obtener lead completo
        lead = self.obtener_lead_completo(lead_id)
        if not lead:
            resultado["reason"] = "lead_not_found"
            resultado["message"] = "No se pudo obtener el lead de Kommo"
            return resultado
        
        # 4. Extraer datos del contacto
        contact_id, contact_name, phone_number = self.extraer_datos_contacto(lead)
        
        if not phone_number:
            self.log("❌ Contacto sin teléfono - creando nota de error", "ERROR")
            self.crear_nota_kommo(
                lead_id,
                "⚠️ ERROR: Contacto sin teléfono\n\nEl lead no tiene número de teléfono registrado.\nNo se puede verificar duplicados ni enviar mensajes."
            )
            resultado["reason"] = "no_phone"
            resultado["message"] = "Contacto sin teléfono"
            return resultado
        
        # 5. Buscar duplicados
        es_duplicado, cantidad, info_duplicado = self.buscar_duplicados(phone_number, lead_id)
        
        if es_duplicado:
            self.log("⚠️ Lead duplicado detectado - NO se enviará respuesta automática", "WARNING")
            nota_duplicado = f"""⚠️ LEAD DUPLICADO DETECTADO

Teléfono: {phone_number}
Contacto existente: {info_duplicado.get('contact_name')}
Lead existente ID: {info_duplicado.get('lead_id')}
Leads asociados: {cantidad}

🚫 ANITA no respondió automáticamente.
Acción requerida: Revisar manualmente."""
            
            self.crear_nota_kommo(lead_id, nota_duplicado)
            resultado["reason"] = "duplicate"
            resultado["message"] = "Lead duplicado - requiere revisión manual"
            return resultado
        
        # 6. Obtener chat_id de WhatsApp
        chat_id = self.obtener_chat_id(phone_number)
        
        if not chat_id:
            self.log("❌ Chat de WhatsApp no encontrado", "ERROR")
            self.crear_nota_kommo(
                lead_id,
                "⚠️ ERROR: Chat de WhatsApp no encontrado\n\nNo se pudo obtener el chat_id para este lead.\nVerificar integración de WhatsApp Business con Kommo."
            )
            resultado["reason"] = "no_chat"
            resultado["message"] = "Chat de WhatsApp no encontrado"
            return resultado
        
        # 7. Generar respuesta con ANITA
        respuesta_anita = self.generar_respuesta_anita(contact_name or "Cliente")
        
        # 8. Enviar mensaje a WhatsApp
        mensaje_enviado = self.enviar_mensaje_whatsapp(chat_id, respuesta_anita)
        
        if not mensaje_enviado:
            resultado["reason"] = "send_failed"
            resultado["message"] = "Error enviando mensaje a WhatsApp"
            return resultado
        
        # 9. Guardar nota en Kommo
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nota_exito = f"""🤖 ANITA respondió automáticamente:

{respuesta_anita}

---
Lead verificado: ✅ No duplicado
Origen: WhatsApp (Lead Frío)
Timestamp: {timestamp}"""
        
        self.crear_nota_kommo(lead_id, nota_exito)
        
        # 10. Etiquetar lead
        self.etiquetar_lead(lead_id, "ANITA - Primer Contacto", timestamp)
        
        # 11. Resultado exitoso
        self.log(f"\n{'='*60}")
        self.log(f"✅ LEAD {lead_id} PROCESADO EXITOSAMENTE")
        self.log(f"{'='*60}\n")
        
        resultado["success"] = True
        resultado["message"] = "Lead procesado correctamente"
        resultado["anita_responded"] = True
        resultado["contact_name"] = contact_name
        resultado["phone_number"] = phone_number
        resultado["respuesta"] = respuesta_anita
        
        return resultado


def webhook_handler(webhook_data: Dict) -> Dict:
    """
    Handler para procesar webhooks de Kommo
    Simula el endpoint que recibiría n8n
    """
    try:
        # Extraer datos del webhook
        leads_add = webhook_data.get("leads", {}).get("add", [])
        
        if not leads_add:
            return {
                "success": False,
                "reason": "no_leads",
                "message": "No hay leads en el webhook"
            }
        
        lead_data = leads_add[0]
        lead_id = lead_data.get("id")
        pipeline_id = lead_data.get("pipeline_id")
        status_id = lead_data.get("status_id")
        
        # Procesar con ANITA
        anita = AnitaLeadsFrios()
        resultado = anita.procesar_lead_frio(lead_id, pipeline_id, status_id)
        
        return resultado
        
    except Exception as e:
        print(f"❌ Error en webhook_handler: {str(e)}")
        return {
            "success": False,
            "reason": "exception",
            "message": str(e)
        }


# ============================================
# EJEMPLO DE USO
# ============================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔥 AGENTE ANITA - LEADS FRÍOS CON SINCRONIZACIÓN")
    print("="*60 + "\n")
    
    # Ejemplo 1: Procesar un lead directamente
    print("📋 EJEMPLO 1: Procesar lead directamente\n")
    
    anita = AnitaLeadsFrios()
    
    # Simular un lead (reemplaza con un ID real de tu Kommo)
    lead_id_ejemplo = 12345678  # Cambiar por un lead_id real
    pipeline_id = PIPELINE_PLAN_VIP
    status_id = STATUS_CONVERSACIONES_NUEVAS
    
    # resultado = anita.procesar_lead_frio(lead_id_ejemplo, pipeline_id, status_id)
    # print(f"\n📊 Resultado: {resultado}")
    
    # Ejemplo 2: Simular webhook de Kommo
    print("\n" + "="*60)
    print("📋 EJEMPLO 2: Simular webhook de Kommo\n")
    
    webhook_simulado = {
        "leads": {
            "add": [
                {
                    "id": 12345678,  # Cambiar por un lead_id real
                    "name": "Lead desde WhatsApp",
                    "status_id": STATUS_CONVERSACIONES_NUEVAS,
                    "pipeline_id": PIPELINE_PLAN_VIP,
                    "created_at": 1716324000,
                    "updated_at": 1716324000,
                    "responsible_user_id": 9876543,
                    "created_by": 9876543,
                    "account_id": 35537967
                }
            ]
        },
        "account": {
            "id": 35537967,
            "subdomain": "infosmartteadetoxcom"
        }
    }
    
    # resultado = webhook_handler(webhook_simulado)
    # print(f"\n📊 Resultado del webhook: {resultado}")
    
    print("\n" + "="*60)
    print("✅ Ejemplos listos para ejecutar")
    print("💡 Descomenta las líneas para probar con leads reales")
    print("="*60 + "\n")

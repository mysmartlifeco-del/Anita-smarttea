"""
🌐 SERVIDOR WEBHOOK PARA ANITA - LEADS FRÍOS
Servidor Flask que recibe webhooks de Kommo y procesa leads con sincronización
"""

from flask import Flask, request, jsonify
from agente_anita_leads_frios import AnitaLeadsFrios, webhook_handler
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Crear aplicación Flask
app = Flask(__name__)

# Configuración
PORT = int(os.getenv("PORT", 5000))
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "smarttea_secret_2026")


@app.route("/", methods=["GET"])
def home():
    """Endpoint de verificación"""
    return jsonify({
        "status": "online",
        "service": "ANITA Leads Fríos - Webhook Server",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "webhook": "/webhook/kommo-lead-added"
        }
    })


@app.route("/health", methods=["GET"])
def health():
    """Health check para monitoreo"""
    return jsonify({
        "status": "healthy",
        "service": "anita-leads-frios",
        "timestamp": os.popen("date").read().strip()
    })


@app.route("/webhook/kommo-lead-added", methods=["POST"])
def kommo_lead_added():
    """
    Endpoint principal que recibe webhooks de Kommo cuando se añade un lead
    """
    try:
        # Obtener datos del webhook
        webhook_data = request.get_json()
        
        if not webhook_data:
            return jsonify({
                "success": False,
                "error": "No data received"
            }), 400
        
        # Log del webhook recibido
        print("\n" + "="*60)
        print("📥 WEBHOOK RECIBIDO DE KOMMO")
        print("="*60)
        print(f"Data: {webhook_data}")
        print("="*60 + "\n")
        
        # Procesar con el handler
        resultado = webhook_handler(webhook_data)
        
        # Determinar código de respuesta HTTP
        status_code = 200 if resultado.get("success") else 400
        
        return jsonify(resultado), status_code
        
    except Exception as e:
        print(f"❌ Error procesando webhook: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/webhook/test", methods=["POST"])
def test_webhook():
    """
    Endpoint de prueba para simular webhooks sin procesar realmente
    """
    try:
        webhook_data = request.get_json()
        
        return jsonify({
            "success": True,
            "message": "Webhook de prueba recibido correctamente",
            "data_received": webhook_data
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/process-lead/<int:lead_id>", methods=["POST"])
def process_lead_manual(lead_id):
    """
    Endpoint para procesar un lead manualmente (útil para testing)
    """
    try:
        # Obtener parámetros opcionales
        data = request.get_json() or {}
        pipeline_id = data.get("pipeline_id", 8588506)
        status_id = data.get("status_id", 67668394)
        
        # Procesar lead
        anita = AnitaLeadsFrios()
        resultado = anita.procesar_lead_frio(lead_id, pipeline_id, status_id)
        
        status_code = 200 if resultado.get("success") else 400
        return jsonify(resultado), status_code
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handler para rutas no encontradas"""
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "available_endpoints": {
            "home": "/",
            "health": "/health",
            "webhook": "/webhook/kommo-lead-added",
            "test": "/webhook/test",
            "manual": "/process-lead/<lead_id>"
        }
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handler para errores internos"""
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 INICIANDO SERVIDOR WEBHOOK ANITA")
    print("="*60)
    print(f"Puerto: {PORT}")
    print(f"Endpoints disponibles:")
    print(f"  - GET  /              → Info del servicio")
    print(f"  - GET  /health        → Health check")
    print(f"  - POST /webhook/kommo-lead-added → Webhook principal")
    print(f"  - POST /webhook/test  → Webhook de prueba")
    print(f"  - POST /process-lead/<id> → Procesar lead manual")
    print("="*60 + "\n")
    
    # Iniciar servidor
    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=os.getenv("DEBUG", "false").lower() == "true"
    )

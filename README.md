# Agente Virtual con IA Local

Este asistente ahora puede funcionar sin depender de servicios en la nube mediante un modelo local servido por [Ollama](https://ollama.com/). Sigue estos pasos en Windows para habilitarlo.

## Requisitos
- Python 3.11+ y el entorno virtual ya provisto (`.venv`).
- Ollama instalado y en ejecución (`ollama serve`).
- Un modelo descargado en Ollama (por ejemplo, `llama3.2`).

## Configuración rápida
1. Instala Ollama y reinicia tu terminal.
2. Descarga un modelo compatible:
   ```powershell
   ollama run llama3.2
   ```
3. Define las variables en `.env` (o mediante `setx`):
   ```
   AGENTE_LOCAL_LLM=ollama
   AGENTE_LOCAL_MODEL=llama3.2
   AGENTE_LOCAL_BASE_URL=http://127.0.0.1:11434
   ```
4. Ejecuta el asistente en modo CLI para validar:
   ```powershell
   .\.venv\Scripts\python.exe agente.py --cli
   ```

## Prueba puntual
También puedes lanzar una pregunta directa sin iniciar la interfaz completa:
```powershell
.\.venv\Scripts\python.exe code\test_local_llm.py "¿Cuál es la capital de Francia?"
```
Si no pasas argumentos, el script usa una pregunta de ejemplo.

## Consejos
- Si deseas volver temporalmente a un proveedor remoto, desactiva `AGENTE_LOCAL_LLM` y coloca tu clave en `AGENTE_LLM_API_KEY`.
- Ajusta `AGENTE_LOCAL_TIMEOUT` en segundos si el modelo local tarda más en responder.
- Cuando `AGENTE_LOCAL_STRICT=1`, el asistente no intentará usar proveedores remotos si el modelo local falla.

## Automatización de WhatsApp Web
Puedes pedirle al asistente que envíe mensajes repetidos por WhatsApp Web (por ejemplo: *"manda un WhatsApp a Ana que diga '¡Ya vamos en camino!' tres veces"*). Para que funcione:

1. Instala las dependencias nuevas:
   ```powershell
   .\.venv\Scripts\pip.exe install -r requirements.txt
   ```
2. Asegúrate de tener Google Chrome instalado. El asistente abrirá una ventana automatizada y necesitarás iniciar sesión en [https://web.whatsapp.com](https://web.whatsapp.com) la primera vez.
3. Opcionalmente ajusta estas variables de entorno:
   - `AGENTE_WHATSAPP_ENABLED=1` para activar/desactivar la característica.
   - `AGENTE_WHATSAPP_PROFILE` para indicar dónde se guardará el perfil persistente de Chrome (por defecto `~/.miau_whatsapp`).
   - `AGENTE_WHATSAPP_WAIT` (segundos) para cambiar el tiempo máximo de espera antes de considerar que WhatsApp no cargó.
   - `AGENTE_WHATSAPP_KEEP_BROWSER=1` si quieres mantener el navegador abierto después de enviar los mensajes (útil para depurar).
   - `AGENTE_HEADLESS=1` permitirá usar Chrome en modo headless, aunque se recomienda desactivarlo para facilitar el escaneo del código QR inicial.
4. Cuando pidas envíos por WhatsApp, intenta mencionar claramente:
   - El destinatario (por ejemplo, “a Carlos” o “a +529991112233”).
   - El mensaje entre comillas o tras frases como “que diga…”.
   - El número de repeticiones (ej. “3 veces”). Si omites este dato se envía una sola vez.

Si Selenium no está instalado, la automatización responderá que no puede completarse. En ese caso vuelve a instalar las dependencias e intenta otra vez.

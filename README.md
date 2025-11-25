# Agente Virtual con IA Local

Este asistente puede ejecutarse con modelos remotos o completamente en tu máquina mediante [Ollama](https://ollama.com/). A continuación se detalla cómo preparar el entorno virtual, instalar dependencias y habilitar el modo local.

>[!NOTE]
> **Instala todas las dependencias antes de ejecutar `agente.py`.**

## 1. Crear y activar el entorno virtual
En el directorio del proyecto abre una terminal y ejecuta:

```powershell
python -m venv .venv
```

Activa el entorno:

- **Windows**
  ```powershell
  .venv\Scripts\activate
  ```
- **macOS / Linux**
  ```bash
  source .venv/bin/activate
  ```

## 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 3. Ejecutar el asistente

Modo CLI rápido:

```powershell
python agente.py --cli
```

### Prueba puntual

```powershell
python code\test_local_llm.py "¿Cuál es la capital de Francia?"
```
Si no proporcionas argumento, se usa una pregunta de ejemplo.

## 4. Configurar modelo local con Ollama

1. Instala Ollama y asegúrate de ejecutar `ollama serve`.
2. Descarga el modelo deseado:
   ```powershell
   ollama run llama3.2
   ```
3. Define las variables en `.env` o con `setx`:
   ```
   AGENTE_LOCAL_LLM=ollama
   AGENTE_LOCAL_MODEL=llama3.2
   AGENTE_LOCAL_BASE_URL=http://127.0.0.1:11434
   ```
4. Valida con:
   ```powershell
   python agente.py --cli
   ```

### Consejos

- Para volver al proveedor remoto, borra `AGENTE_LOCAL_LLM` y usa `AGENTE_LLM_API_KEY`.
- Ajusta `AGENTE_LOCAL_TIMEOUT` si el modelo local tarda más en responder.
- `AGENTE_LOCAL_STRICT=1` evita que el asistente busque un LLM remoto como respaldo.

## 5. Automatización de WhatsApp Web

Puedes solicitar envíos como: *"manda un WhatsApp a Ana que diga '¡Ya vamos en camino!' tres veces"*. Requisitos:

1. Instala Selenium y dependencias:
   ```powershell
   pip install -r requirements.txt
   ```
2. Ten Google Chrome instalado y entra en [https://web.whatsapp.com](https://web.whatsapp.com) la primera vez para vincular la cuenta.
3. Variables útiles:
   - `AGENTE_WHATSAPP_ENABLED=1` activa/desactiva la función.
   - `AGENTE_WHATSAPP_PROFILE` define la carpeta del perfil persistente (por defecto `~/.miau_whatsapp`).
   - `AGENTE_WHATSAPP_WAIT` (segundos) controla el tiempo máximo de espera.
   - `AGENTE_WHATSAPP_KEEP_BROWSER=1` mantiene el navegador abierto tras enviar mensajes.
   - `AGENTE_HEADLESS=1` usa Chrome en modo headless (solo si ya cuentas con el QR escaneado).
4. Cuando hagas la solicitud menciona:
   - Destinatario (nombre o número completo).
   - Mensaje (entre comillas o tras “que diga…”).
   - Número de repeticiones (si falta, se envía una sola vez).

Si Selenium falta, recibirás un aviso para reinstalar dependencias.

# Agente Virtual con IA Local
Asistente multimodal (voz, texto e imagen) optimizado para Windows que puede trabajar por completo sin la nube gracias a un modelo local servido por [Ollama](https://ollama.com/). También admite proveedores remotos como fallback y cuenta con automatizaciones (WhatsApp Web, recordatorios, guías curadas, etc.).

> [!IMPORTANT]
> Instala todas las dependencias dentro del entorno virtual antes de ejecutar `agente.py`.

## Tabla de contenido
1. [Resumen rápido](#resumen-rápido)
2. [Inicio rápido](#inicio-rápido)
3. [Requisitos previos](#requisitos-previos)
4. [Instalación paso a paso](#instalación-paso-a-paso)
5. [Dependencias principales](#dependencias-principales)
6. [Modelos locales con Ollama](#modelos-locales-con-ollama)
7. [Modelos remotos y fallback](#modelos-remotos-y-fallback)
8. [Variables de entorno](#variables-de-entorno)
9. [Ejecución y pruebas](#ejecución-y-pruebas)
10. [Automatización de WhatsApp Web](#automatización-de-whatsapp-web)
11. [Solución de problemas](#solución-de-problemas)

## Resumen rápido
- Voz y chat: reconoce comandos por micrófono (SpeechRecognition + PyAudio) y responde con síntesis (pyttsx3).
- LLM local: usa Ollama con modelos ligeros (`llama3.2`, `llama3.1:8b`, etc.) sin exponer datos a la nube.
- Fallback remoto opcional: OpenAI, OpenRouter u otra API compatible con OpenAI.
- Automaciones: temporizadores, búsquedas, recetas, recomendaciones de hardware/anime y envío de mensajes por WhatsApp Web vía Selenium.

## Inicio rápido
1. Crea el entorno virtual (solo la primera vez):
   ```powershell
   python -m venv .venv
   ```
2. Activa el entorno:
   - **Windows:** `.\.venv\Scripts\activate`
   - **macOS/Linux:** `source .venv/bin/activate`
3. Instala dependencias: `pip install -r requirements.txt`
4. Ejecuta el asistente en CLI: `python agente.py --cli`
5. Prueba el LLM local directamente: `python code\test_local_llm.py "¿Cuál es la capital de Francia?"`

## Requisitos previos
- Windows 10/11 de 64 bits con permisos de instalación.
- [Python 3.11+](https://www.python.org/downloads/) y `pip`.
- [Git](https://git-scm.com/download/win) para clonar el repositorio.
- [Ollama](https://ollama.com/download) instalado y con `ollama serve` en ejecución.
- [Google Chrome](https://www.google.com/chrome/) para las automatizaciones con Selenium.
- Micrófono funcional si utilizarás el modo voz.
- Opcional: GPU compatible para acelerar modelos locales grandes.

## Instalación paso a paso
1. **Clona el repositorio y entra en la carpeta:**
   ```powershell
   git clone https://github.com/JazielTaekwondo/AgenteVirtual_AsistenteDeVoz.git
   cd AgenteVirtual_AsistenteDeVoz
   ```
2. **(Opcional) Crea un entorno virtual limpio:**
   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\activate
   ```
   > Si el directorio `.venv` ya existe, basta con activarlo.
3. **Instala todas las librerías del proyecto:**
   ```powershell
   .\.venv\Scripts\pip.exe install --upgrade pip
   .\.venv\Scripts\pip.exe install -r requirements.txt
   ```
4. **Crea o edita el archivo `.env`** en la raíz con las variables descritas más abajo.
5. **Verifica PyAudio/portaudio.** Si aparece un error al instalar, descarga el `.whl` adecuado desde [whl.win](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) y ejecútalo con `pip install`.

## Dependencias principales
| Tipo | Librería | Motivo |
| --- | --- | --- |
| Reconocimiento de voz | `SpeechRecognition`, `PyAudio` | Capturar comandos hablados |
| Texto a voz | `pyttsx3` | Respuestas habladas sin conexión |
| LLM/API | `openai`, `httpx`, `requests` | Compatibilidad con APIs estilo OpenAI |
| Automatización | `selenium`, `webdriver-manager` | WhatsApp Web y tareas en navegador |
| Visión | `opencv-python`, `numpy`, `Pillow` (opcional) | Análisis básico de imágenes |
| Búsquedas/web | `duckduckgo-search`, `beautifulsoup4`, `tqdm` | Consultas externas controladas |

Todas están listadas en `requirements.txt`; reinstala con el comando del paso 3 si hace falta.

## Modelos locales con Ollama
1. Instala Ollama y abre una terminal aparte.
2. Ejecuta el servidor:
   ```powershell
   ollama serve
   ```
3. Descarga al menos un modelo compatible (ejemplo `llama3.2`):
   ```powershell
   ollama pull llama3.2
   ```
4. (Opcional) Importa tu propio modelo `GGUF` copiándolo a `tools/ollama/` y luego:
   ```powershell
   ollama create mi-modelo -f tools/ollama/mi-modelo.Modelfile
   ```
5. Comprueba que la API local responde:
   ```powershell
   curl http://localhost:11434/api/tags
   ```

## Modelos remotos y fallback
- Obtén la API key de tu proveedor (OpenAI, OpenRouter, Groq, etc.).
- Define `AGENTE_LLM_API_KEY`, `AGENTE_LLM_MODEL` y, si aplica, `AGENTE_LLM_BASE_URL`.
- Ajusta `AGENTE_LOCAL_STRICT=0` para permitir que el asistente cambie a un proveedor remoto si el modelo local falla o tarda demasiado.
- Borra/omite `AGENTE_LOCAL_LLM` para operar solo con proveedores remotos.

## Variables de entorno
Configura estas variables en `.env` o mediante `setx` en Windows:

| Variable | Descripción |
| --- | --- |
| `AGENTE_LOCAL_LLM=ollama` | Activa el modo local con Ollama (usa `none` para deshabilitarlo). |
| `AGENTE_LOCAL_MODEL=llama3.2` | Nombre exacto del modelo cargado en Ollama. |
| `AGENTE_LOCAL_BASE_URL=http://127.0.0.1:11434` | URL del servidor Ollama. |
| `AGENTE_LOCAL_TIMEOUT=60` | Tiempo máximo (s) de espera antes de marcar error. |
| `AGENTE_LOCAL_STRICT=1` | Evita usar fallback remoto cuando vale `1`. |
| `AGENTE_LLM_API_KEY=` | API key para proveedores remotos. |
| `AGENTE_LLM_MODEL=gpt-4o-mini` | Modelo remoto principal. |
| `AGENTE_LLM_FALLBACK_MODEL=anthropic/claude-3.5-sonnet` | Modelo secundario para errores. |
| `AGENTE_LLM_BASE_URL=` | URL de la API remota (vacío para OpenAI oficial). |
| `AGENTE_HEADLESS=0` | Activa el modo headless de Chrome cuando vale `1`. |
| `AGENTE_WHATSAPP_ENABLED=1` | Habilita el envío por WhatsApp Web. |
| `AGENTE_WHATSAPP_PROFILE=%USERPROFILE%\\.miau_whatsapp` | Carpeta del perfil persistente. |
| `AGENTE_WHATSAPP_WAIT=45` | Tiempo máximo (s) para cargar WhatsApp Web. |
| `AGENTE_WHATSAPP_KEEP_BROWSER=0` | Mantiene el navegador abierto después de enviar. |
| `AGENTE_VISION_CAPTION=1` | Controla el captioning de imágenes (requiere OpenCV). |

## Ejecución y pruebas
- **Interfaz gráfica (por defecto):**
  ```powershell
  .\.venv\Scripts\python.exe agente.py
  ```
- **Forzar CLI:**
  ```powershell
  .\.venv\Scripts\python.exe agente.py --cli
  ```
- **Probar solo el modelo local:**
  ```powershell
  .\.venv\Scripts\python.exe code\test_local_llm.py "¿Cuál es la capital de Francia?"
  ```
  (Si no proporcionas argumento, el script usa una pregunta de ejemplo.)

En modo voz, el CLI te pedirá elegir `voz` o `chat`. En la GUI puedes alternar diciendo “modo voz activado” o “modo voz desactivado”.

## Automatización de WhatsApp Web
Este asistente puede enviar mensajes repetidos por WhatsApp Web mediante Selenium. Requisitos:

1. Tener Google Chrome instalado y actualizado.
2. Ejecutar `pip install -r requirements.txt` para instalar Selenium y `webdriver-manager`.
3. Iniciar sesión manualmente la primera vez que se abra `https://web.whatsapp.com` para guardar el QR en el perfil persistente.
4. Ajustar variables como:
   - `AGENTE_WHATSAPP_ENABLED=1`
   - `AGENTE_WHATSAPP_PROFILE=%USERPROFILE%\\.miau_whatsapp`
   - `AGENTE_HEADLESS=0` (recomendado mientras configuras)
   - `AGENTE_WHATSAPP_WAIT=45`
   - `AGENTE_WHATSAPP_KEEP_BROWSER=0`

Al solicitar envíos especifica claramente:
- Destinatario (nombre o número completo).
- Mensaje (entre comillas o tras frases como “que diga ...”).
- Número de repeticiones (si se omite, se envía una sola vez).

Si Selenium o ChromeDriver no están disponibles, el asistente avisará que no puede completar la acción.

## Solución de problemas
- **El micrófono no aparece:** revisa los dispositivos de entrada en Windows y vuelve a ejecutar el asistente.
- **PyAudio no se instala:** usa el `.whl` oficial de Christoph Gohlke para tu versión de Python/arquitectura.
- **Ollama no responde:** confirma que `ollama serve` esté activo y que `AGENTE_LOCAL_BASE_URL` apunte a `http://127.0.0.1:11434`.
- **WhatsApp no abre o se queda esperando:** elimina la carpeta `%USERPROFILE%\\.miau_whatsapp` para reiniciar la sesión y vuelve a escanear el código QR.
- **Quiero volver al proveedor remoto:** establece `AGENTE_LOCAL_STRICT=0`, omite `AGENTE_LOCAL_*` y define `AGENTE_LLM_API_KEY` junto con `AGENTE_LLM_MODEL`.

Con estos pasos cualquier usuario que clone el repositorio puede levantar el asistente, elegir si usa un modelo local u otro proveedor y habilitar las automatizaciones disponibles.
 

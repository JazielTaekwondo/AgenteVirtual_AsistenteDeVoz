# Agente Virtual con IA Local

Asistente multimodal (voz, texto e imagen) optimizado para Windows que puede trabajar por completo sin la nube gracias a un modelo local servido por [Ollama](https://ollama.com/). También admite proveedores remotos como fallback y cuenta con automatizaciones (WhatsApp Web, recordatorios, guías curadas, etc.).

## Tabla de contenido
1. [Resumen rápido](#resumen-rápido)
2. [Requisitos previos](#requisitos-previos)
3. [Instalación paso a paso](#instalación-paso-a-paso)
4. [Dependencias principales](#dependencias-principales)
5. [Modelos locales con Ollama](#modelos-locales-con-ollama)
6. [Modelos remotos y fallback](#modelos-remotos-y-fallback)
7. [Variables de entorno](#variables-de-entorno)
8. [Ejecución y pruebas](#ejecución-y-pruebas)
9. [Automatización de WhatsApp Web](#automatización-de-whatsapp-web)
10. [Solución de problemas](#solución-de-problemas)

## Resumen rápido
- Voz y chat: reconoce comandos por micrófono (SpeechRecognition + PyAudio) y responde con síntesis (pyttsx3).
- LLM local: usa Ollama con modelos ligeros (`llama3.2`, `llama3.1:8b`, etc.) sin exponer datos a la nube.
- Fallback remoto opcional: OpenAI, OpenRouter u otra API compatible con OpenAI.
- Automaciones: temporizadores, búsquedas, recetas, recomendaciones de hardware/anime y envío de mensajes por WhatsApp Web vía Selenium.

## Requisitos previos
- Windows 10/11 de 64 bits con acceso de administrador para instalar dependencias.
- [Python 3.11+](https://www.python.org/downloads/) y `pip`. El repositorio ya incluye el entorno virtual `.venv`, pero puedes regenerarlo.
- [Git](https://git-scm.com/download/win) para clonar el proyecto.
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
   > Nota: Si ya existe `.venv`, basta con activarlo.
3. **Instala todas las librerías del proyecto:**
   ```powershell
   .\.venv\Scripts\pip.exe install --upgrade pip
   .\.venv\Scripts\pip.exe install -r requirements.txt
   ```
4. **Copia/crea tu archivo `.env`** en la raíz y completa los valores descritos más abajo.
5. **Verifica la instalación de audio (PyAudio)**. Si obtienes errores de `portaudio`, instala el paquete oficial desde [whl.win](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) y vuelve a ejecutar `pip install`.

## Dependencias principales
| Tipo | Librería | Motivo |
| --- | --- | --- |
| Reconocimiento de voz | `SpeechRecognition`, `PyAudio` | Capturar comandos hablados |
| Texto a voz | `pyttsx3` | Respuestas habladas sin conexión |
| LLM/API | `openai`, `httpx`, `requests` | Compatibilidad con APIs estilo OpenAI |
| Automatización | `selenium`, `webdriver-manager` | WhatsApp Web y otras tareas en navegador |
| Visión | `opencv-python`, `numpy`, `Pillow` (opcional) | Análisis básico de imágenes |
| Búsquedas y scraping | `duckduckgo-search`, `beautifulsoup4`, `tqdm` | Consultas externas controladas |

Todas vienen listadas en `requirements.txt`; reinstala con el comando del paso 3 si falta alguna.

## Modelos locales con Ollama
1. Instala Ollama, abre una terminal nueva y corre el servidor:
   ```powershell
   ollama serve
   ```
2. Descarga al menos un modelo compatible (ejemplo `llama3.2`):
   ```powershell
   ollama pull llama3.2
   ```
3. (Opcional) Importa tu propio modelo `GGUF` copiándolo a `tools/ollama/` y ejecutando `ollama create`.
4. Confirma que la API local responde:
   ```powershell
   curl http://localhost:11434/api/tags
   ```

## Modelos remotos y fallback
Si deseas volver a un proveedor remoto o dejar un fallback automático:
- Crea un API key del proveedor (OpenAI, OpenRouter, Groq, etc.).
- Define `AGENTE_LLM_API_KEY`, `AGENTE_LLM_MODEL` y `AGENTE_LLM_BASE_URL` (cuando proceda).
- Ajusta `AGENTE_LOCAL_STRICT=0` para permitir que el asistente pruebe proveedores remotos si el modelo local falla o queda sin capacidad.

## Variables de entorno
Guarda estos valores en `.env` (usa `setx` para definirlos de forma global si lo prefieres):

| Variable | Descripción |
| --- | --- |
| `AGENTE_LOCAL_LLM=ollama` | Activa el modo local con Ollama. Coloca `none` para deshabilitarlo. |
| `AGENTE_LOCAL_MODEL=llama3.2` | Nombre exacto del modelo cargado en Ollama. |
| `AGENTE_LOCAL_BASE_URL=http://127.0.0.1:11434` | URL del servidor Ollama. |
| `AGENTE_LOCAL_TIMEOUT=60` | Tiempo máximo (s) para esperar respuesta local. |
| `AGENTE_LOCAL_STRICT=1` | Cuando es `1`, no se usa fallback remoto. |
| `AGENTE_LLM_API_KEY=` | API key del proveedor remoto (solo si se usará). |
| `AGENTE_LLM_MODEL=gpt-4o-mini` | Modelo remoto principal. |
| `AGENTE_LLM_FALLBACK_MODEL=anthropic/claude-3.5-sonnet` | Modelo secundario si el primero falla. |
| `AGENTE_LLM_BASE_URL=` | URL de la API remota (dejar vacío para OpenAI oficial). |
| `AGENTE_HEADLESS=0` | Activa/desactiva ejecución headless de Chrome. |
| `AGENTE_WHATSAPP_ENABLED=1` | Habilita la automatización de WhatsApp. |
| `AGENTE_WHATSAPP_PROFILE=%USERPROFILE%\.miau_whatsapp` | Carpeta para persistir la sesión de WhatsApp Web. |
| `AGENTE_WHATSAPP_WAIT=45` | Tiempo máximo para que cargue la página antes de abortar. |
| `AGENTE_WHATSAPP_KEEP_BROWSER=0` | Deja el navegador abierto tras enviar mensajes. |
| `AGENTE_VISION_CAPTION=1` | Controla si se hace caption de imágenes (requiere `opencv-python`). |

## Ejecución y pruebas
- **GUI (modo por defecto):**
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
  (El script usa una pregunta por defecto si no pasas argumentos.)

Si usas voz, al iniciar el CLI el asistente te preguntará si prefieres modo `voz` o `chat`. En GUI puedes alternar diciendo “modo voz activado/desactivado”.

## Automatización de WhatsApp Web
Este asistente puede enviar mensajes repetidos a través de WhatsApp Web con Selenium. Para que funcione:

1. Verifica que Chrome esté instalado y actualizado.
2. Asegúrate de haber corrido `pip install -r requirements.txt` (instala Selenium y `webdriver-manager`).
3. Inicia sesión manualmente la primera vez que se abra `https://web.whatsapp.com` para que el perfil persistente guarde el QR.
4. Ajusta variables según tus necesidades:
   - `AGENTE_WHATSAPP_ENABLED=1`
   - `AGENTE_WHATSAPP_PROFILE=%USERPROFILE%\.miau_whatsapp`
   - `AGENTE_HEADLESS=0` (recomendado para depurar)

Cuando solicites un mensaje indica claramente:
- Destinatario (`"manda un WhatsApp a Ana"` o `"a +529991112233"`).
- Contenido (`"que diga '¡Ya vamos en camino!'"`).
- Cantidad de repeticiones (`"tres veces"`).

Si Selenium o ChromeDriver no están disponibles, el asistente responderá que no puede completar la acción; reinstala dependencias y vuelve a intentar.

## Solución de problemas
- **El micrófono no aparece:** revisa panel de Control de Sonido y confirma permisos de Windows; luego ejecuta nuevamente el asistente.
- **PyAudio falla al instalarse:** descarga el `.whl` acorde a tu versión de Python desde la página de Christoph Gohlke y luego ejecuta `pip install nombre_del_archivo.whl`.
- **Ollama no responde:** verifica que `ollama serve` esté activo y que `AGENTE_LOCAL_BASE_URL` apunte al puerto correcto (por defecto 11434).
- **WhatsApp no abre:** borra la carpeta del perfil (`%USERPROFILE%\.miau_whatsapp`) para reiniciar la sesión y vuelve a escanear el código QR.
- **Necesito volver a un proveedor remoto:** pon `AGENTE_LOCAL_STRICT=0`, comenta las variables `AGENTE_LOCAL_*` y define `AGENTE_LLM_API_KEY` junto con `AGENTE_LLM_MODEL`.

Con estos pasos cualquier usuario que clone el repositorio puede levantar el asistente, elegir si usa un modelo local u otro proveedor y habilitar las automatizaciones disponibles.

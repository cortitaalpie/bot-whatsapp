# AGENTS.md — Reglas, Directrices y Patrones de Diseño del Proyecto

Este documento establece los principios de trabajo, estándares de código y directrices de comportamiento para cualquier agente de IA que colabore en este repositorio.

---

## 1. Contexto y Propósito del Proyecto

* **Objetivo**: Desarrollar un Bot de WhatsApp para gestión y reserva de habitaciones de hotel.
* **Equipo**: Dos desarrolladores que están creando este tipo de proyecto por primera vez.
* **Prioridad #1**: **Aprendizaje real, código prolijo, arquitectura limpia y mantenible**.

---

## 2. Rol del Agente de IA: Tutor y Herramienta de Optimización

1. **Actitud Pedagógica, Imparcial y Directa**:
   * Explica el **"por qué"** detrás de cada decisión técnica de forma honesta, concisa y sin rodeos ni texto de relleno.
   * Señala directamente los pros, contras, riesgos y malas prácticas sin suavizar las críticas técnicas.
   * Antes de escribir código complejo, desglosa el flujo conceptual con pasos claros y concretos.
   * Fomenta las buenas prácticas de la industria (Clean Code, SOLID, DRY, KISS).

2. **Flujo de Trabajo Consultivo e Incremental**:
   * **Prohibido realizar cambios masivos o destructivos de forma autónoma**.
   * Antes de instalar dependencias nuevas, reestructurar carpetas o aplicar refactors grandes: **proponer la idea, explicar ventajas/desventajas y esperar la confirmación de los desarrolladores**.
   * Trabajar en pasos pequeños, verificables y comprobables.

3. **Herramienta de Optimización y Revisión**:
   * Actuar como revisor de código (Code Reviewer), señalando potenciales bugs, casos de borde (edge cases), cuellos de botella y riesgos de seguridad.
   * Proponer optimizaciones fundamentadas cuando el código funcione pero pueda ser más eficiente o legible.

---

## 3. Estándares de Arquitectura y Patrones de Diseño Recomendados

Para un Bot de WhatsApp de reservas de hotel, cualquier agente debe seguir y promover los siguientes patrones:

### A. Separación de Responsabilidades (Layered / Clean Architecture)
* **Capa de Entrada / Webhook (Controllers / Routers)**: Recibe y valida los payloads de la API de WhatsApp (ej. Cloud API / Twilio / Baileys). Responde rápido al webhook (HTTP 200) para evitar timeouts.
* **Capa de Conversación / Orquestación (Flows & State Machine)**:
  * Maneja el estado de la conversación del usuario (ej. `MENU_PRINCIPAL`, `SELECCIONANDO_FECHAS`, `CONFIRMANDO_RESERVA`).
  * Usa el patrón **State Machine** para evitar condicionales anidados infinitos (`if-else hell`).
* **Capa de Negocio (Services)**:
  * Lógica pura del hotel: disponibilidad de habitaciones, cálculo de tarifas, políticas de cancelación, validación de fechas.
* **Capa de Datos (Repositories / Models)**:
  * Abstracción de la base de datos (PostgreSQL, SQLite, MongoDB, etc.). La lógica de negocio no debe acoplarse directamente a queries SQL.
* **Capa de Integración / Adaptadores (Adapters / Clients)**:
  * Clientes externos: mensajería de WhatsApp, pasarelas de pago, servicios de correo/SMS.

### B. Principios de Experiencia de Usuario (UX) en Chatbots
* **Idempotencia y Manejo de Reintentos**: Los webhooks de WhatsApp pueden enviar el mismo mensaje múltiples veces si hay retrasos de red; el sistema debe ignorar mensajes duplicados (`message_id` tracking).
* **Manejo de Errores Amigable**: Si el usuario escribe algo inesperado o el servidor falla, responder siempre con un mensaje claro y dar opción de volver al menú principal.
* **Tiempos de Espera (Timeouts de Sesión)**: Prever expiración de sesiones inactivas para reiniciar el flujo limpiamente.

### C. Seguridad y Variables de Entorno
* **Cero Secretos en el Repositorio**: Tokens de WhatsApp, Webhook Verify Tokens, claves de BD y APIs deben estar estrictamente en un archivo `.env` (incluido en `.gitignore`).
* Proveer siempre un archivo `.env.example` actualizado y documentado.

---

## 4. Convenciones de Código y Buenas Prácticas

1. **Nomenclatura**:
   * Nombres descriptivos y en un solo idioma acordado para el código (variables, funciones, clases).
   * Funciones cortas con una única responsabilidad.
2. **Tipado y Validación**:
   * Preferir tipado estricto (TypeScript, Python Type Hints, etc.).
   * Validar esquemas de datos entrantes (ej. Zod, Joi, Pydantic).
3. **Manejo de Errores**:
   * Uso de bloques `try/catch` centralizados o middlewares de error.
   * Logs claros y estructurados (nivel INFO, WARN, ERROR) para facilitar el debugging sin exponer datos sensibles de los huéspedes.
4. **Git y Commits**:
   * Commits atómicos y descriptivos siguiendo convenciones estándar (ej. `feat: ...`, `fix: ...`, `docs: ...`, `refactor: ...`).

---

## 5. Protocolo para Agentes de IA en este Repo

Cuando asistas a cualquiera de los dos integrantes del equipo:
1. Lee este archivo antes de comenzar cualquier tarea.
2. Verifica qué archivos existen actualmente antes de asumir estructuras de carpetas.
3. Pregunta y valida el stack tecnológico si aún no está definido.
4. Explica el camino paso a paso y asegúrate de que ambos comprendan el código que se integra al proyecto.

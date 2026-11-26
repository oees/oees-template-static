# Plantilla de web estática de OEES

Esta plantilla sirve para crear una web pública sencilla: páginas, textos, imágenes y partes interactivas que funcionan en el navegador. No tiene servidor ni base de datos.

Si tu web necesita guardar datos de visitantes (formularios, registros) o tiene usuarios que inician sesión, usa la plantilla de Django (`oees-template`). Claude te dice cuál necesitas.

Si tu web es solo para empleados de OEES y no guarda datos, no necesitas esta plantilla. Claude la prepara para Alexandria, la plataforma interna de OEES, y la publicas tú.

## Cómo trabajar

1. Abre Claude en modo Cowork. La skill `oees-web-infra` tiene que estar activada.
2. Explica qué web quieres. Claude te dice qué plantilla descargar.
3. Descarga esta plantilla: en GitHub, pulsa **Code** y después **Download ZIP**.
4. Crea una carpeta para tus webs, por ejemplo `Webs` en Documentos. Descomprime el zip dentro.
5. Da a Claude acceso a la carpeta `Webs`. Claude construye la web ahí y te enseña cómo queda.
6. Para seguir otro día, abre Cowork con la misma carpeta.
7. Cuando la web esté lista, pide a Claude el zip para tecnología. Envíalo al equipo de tecnología. Tecnología la revisa y la publica.
8. Después de publicarla, tecnología te devuelve un zip nuevo. Dáselo a Claude antes del siguiente cambio.

Si trabajas en un chat y no en Cowork, sube el zip al chat. Para seguir otro día, sube el último zip que te dio Claude.

## Tres reglas

- No pongas contraseñas, claves ni tokens en ningún archivo.
- No uses datos reales de clientes, ni siquiera para probar. Usa datos inventados.
- No hagas el zip a mano. Pide a Claude que lo genere: así no incluye archivos que no deben salir de tu equipo.

## Para el equipo de tecnología

- [`HANDOFF.md`](HANDOFF.md): qué contiene la web y qué hay que revisar.
- [`docs/deploy-runbook.md`](docs/deploy-runbook.md): cómo importar el zip y publicar la web.
- [`docs/troubleshooting.md`](docs/troubleshooting.md): qué hacer si falla un despliegue.

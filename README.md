# FPCMerch

Tienda Virtual de prendas y accesorios de fútbol construida con Python, Django, SQLite, plantillas HTML, CSS y JavaScript. La aplicación es multipágina y procesa catálogo, autenticación, carrito, pedidos y formularios en el servidor.

## Requisitos y tecnologías

- Windows 10/11, CMD o PowerShell.
- Python 3.11 o superior, con `pip` (el proyecto fue verificado con Python 3.12.14).
- Django 5.2.17 LTS, Pillow 12.1.0, Requests 2.32.5, WhiteNoise y el cliente de PostgreSQL. Las dependencias de ejecución están fijadas en `requirements.txt`.
- SQLite, incluido con Python; Visual Studio Code recomendado.

Si `python` o `py` no aparecen en PowerShell, instala Python 3.11+ desde [python.org](https://www.python.org/downloads/windows/) y activa **Add python.exe to PATH** durante la instalación. Cierra y vuelve a abrir VS Code después.

## Instalación en VS Code (PowerShell)

Abre la carpeta del proyecto en VS Code y ejecuta estos comandos en la terminal integrada:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py import_legacy_catalog
python manage.py runserver 8000
```

El archivo `.env.example` selecciona `devFPCMerch.db` como base SQLite activa. Déjalo en la raíz del proyecto. `migrate` agrega las tablas de Django sin borrar las tablas originales; `import_legacy_catalog` adapta `categorias`, `productos` y `producto_tallas` al catálogo de Django. La importación se puede repetir y no elimina productos. Para editar el catálogo después, usa Django Admin o `/gestion/productos/`.

To run the existing project from **CMD** instead of PowerShell:

```cmd
cd /d "C:\Users\jsmen\Documents\FPCMerchF"
call .venv\Scripts\activate.bat
python manage.py migrate
python manage.py import_legacy_catalog
python manage.py runserver 8000
```

La base original guarda nombres de imágenes, no sus bytes. El importador busca los archivos en `media/products/`; las imágenes faltantes se reportan y el producto usa la imagen de respaldo. Las cuentas y pedidos heredados permanecen en sus tablas originales. `python manage.py seed_demo` es opcional y agrega un catálogo ilustrativo separado de 89 productos.

Si PowerShell dice que `py` no existe, usa `python -m venv .venv` después de instalar Python. Si la activación se bloquea por la política de PowerShell, ejecuta `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` en una terminal de PowerShell de tu usuario y vuelve a activar el entorno. También puedes evitar la activación ejecutando `.\.venv\Scripts\python.exe manage.py ...`.

Abre <http://127.0.0.1:8000/>. Para cambiar el puerto, por ejemplo a 8080, inicia con `python manage.py runserver 8080`.

## Configuración

Al copiar `.env.example` a `.env`, sustituye `SECRET_KEY` por una clave privada larga antes de publicar el sitio. Django lee `SECRET_KEY`, `DEBUG` y `ALLOWED_HOSTS` de ese archivo. En desarrollo, `DEBUG=True` y los hosts locales vienen configurados como ejemplo.

La base activa se configura con `DATABASE_NAME` en `.env` (en este proyecto, `devFPCMerch.db`). Las imágenes subidas se guardan en `media/products/`. `seed_demo` genera imágenes PNG ilustrativas con Pillow. Puedes subir imágenes JPG o PNG de hasta 5 MB desde `/admin/` o `/gestion/productos/`.

### Cuenta de demostración

- Cliente: `cliente@fpcmerch.test`
- Sin contraseña predeterminada. Asígnale una local con `python manage.py changepassword cliente@fpcmerch.test` si necesitas probar esa cuenta.

El usuario cliente de demostración sirve para probar el inicio de sesión. El proyecto no crea automáticamente un administrador en una base nueva. Crea uno con `python manage.py createsuperuser`; el campo de acceso es el correo electrónico. Restablece su clave con `python manage.py changepassword correo@ejemplo.com`. Si habilitas el superusuario de demostración dentro de `seed_demo`, define `FPCMERCH_CREATE_SUPERUSER=1` y `FPCMERCH_DEMO_SUPERUSER_PASSWORD` en el entorno. Usa credenciales distintas antes de desplegar el sitio.

## Comandos de desarrollo

```
python manage.py makemigrations
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py test
python manage.py check
```

La migración `apps/users/migrations/0001_initial.py` define el usuario personalizado antes que el resto de las apps. Si partes de una base de datos limpia, aplica migraciones en el orden normal con `migrate`; no cambies `AUTH_USER_MODEL` después de la primera migración.

## Funcionalidades implementadas

- Inicio con carrusel CSS/JS, seis categorías con conteos desde la BD, destacados editables en Admin, banner informativo y sección de confianza.
- Catálogo con búsqueda, categoría, precio, talla, ordenamiento, paginación y detalle de producto.
- Usuario Django propio: correo único como login, teléfono y ciudad; registro, sesión, recuperación de contraseña por correo de consola y perfil.
- Carrito de sesión para visitantes y carrito persistido en BD para usuarios. Al autenticarse, combina cantidades con el carrito de su cuenta, sin exceder existencias.
- Checkout autenticado con dirección, ciudad, teléfono, envío y método de pago simulado. Los pedidos descuentan stock en una transacción atómica con actualizaciones condicionales `F()` compatibles con SQLite.
- Django Admin y CRUD de productos para personal autorizado en `/gestion/productos/`.
- Mensajes de contacto, páginas informativas, errores 400/403/404/500 y endpoints JSON propios en `/api/`, con API pública de catálogo versionada en `/api/v1/`.
- Conversión de referencia USD/COP consultada desde el servidor en el detalle del producto y almacenada en caché por seis horas. Si no responde el servicio, se omite el valor aproximado y la página sigue disponible.

### Servicio externo requerido

La consulta de tasa usa [open.er-api.com](https://open.er-api.com/v6/latest/USD), endpoint público sin clave ni cuenta. Para que aparezca el precio aproximado en USD, permite conexión saliente a ese host; no se requiere configuración de credenciales. Si el equipo no tiene internet, la tienda funciona y muestra que la conversión no está disponible. El envío de recuperación de contraseña usa el backend de correo de consola: copia el enlace que aparece en la terminal de `runserver` y ábrelo en el mismo navegador.

## API del catálogo

Para esta tienda conviene una API REST propia de solo lectura para categorías y productos. El proyecto ya usa Django y tiene modelos para esos datos; servir JSON desde Django reutiliza esa lógica, añade pocos componentes y no requiere claves. Una pasarela como Wompi o Mercado Pago sería una fase distinta: necesita una cuenta de comercio, credenciales de prueba/producción y webhooks para confirmar pagos. El checkout actual simula el pago y no debe marcarse como cobrado por una API de catálogo.

La API nueva usa vistas JSON de Django (sin añadir Django REST Framework ni otras dependencias) y no requiere claves:

| Método | Endpoint | Función |
| --- | --- | --- |
| GET | `/api/v1/categories/` | Categorías con conteo de productos activos. |
| GET | `/api/v1/products/` | Productos activos, con paginación y filtros. |
| GET | `/api/v1/products/<slug>/` | Detalle, tallas y stock disponible. |

Filtros de productos: `q`, `categoria`, `precio_max`, `talla`, `orden` y `page`. Prueba desde CMD con `curl.exe`:

```cmd
curl.exe "http://127.0.0.1:8000/api/v1/categories/"
curl.exe "http://127.0.0.1:8000/api/v1/products/?q=colombia&categoria=camisetas"
curl.exe "http://127.0.0.1:8000/api/v1/products/camiseta-colombia-titular-2025/"
```

Las rutas JSON anteriores (`/api/productos/`, `/api/categorias/`, búsqueda y carrito) continúan disponibles. La conversión USD/COP usa el servicio externo descrito arriba; la API pública de catálogo no consume servicios de pago.

Para pagos reales, Wompi y Mercado Pago notifican cambios de transacción a la tienda mediante webhooks; Mercado Pago también describe la validación de firma de esas notificaciones. Esa integración requiere credenciales de una cuenta de comercio, un endpoint HTTPS público y pruebas de webhooks, por eso no se agrega a este checkout simulado. Consulta la documentación oficial de [eventos de Wompi](https://docs.wompi.co/docs/colombia/eventos/) y [webhooks de Mercado Pago](https://www.mercadopago.com.co/developers/es/docs/checkout-api-orders/notifications?scope=prod) antes de iniciar esa fase.

## Paleta visual

Los colores están centralizados en `:root` al inicio de `static/css/globals.css`. Los tonos principales son: fondo gris azulado `#eaf0f4`, superficie `#f7f9fb`, azul pizarra `#536f82`, verde turquesa apagado `#496b6e`, texto `#263946` y bordes `#d1dce4`. Los botones oscuros usan `#3f6268`; los avisos de error usan `#895761`.

## Acceso al administrador y guía de prueba

`/admin/` es el panel interno de Django para gestionar datos. Inicia sesión con el correo y contraseña de un superusuario; una cuenta cliente normal no tiene permisos. Para crear o recuperar uno en CMD:

```cmd
python manage.py createsuperuser
python manage.py changepassword admin@fpcmerch.local
```

Para probar el sitio desde cero en la terminal CMD de VS Code:

1. Abre la carpeta del proyecto y ejecuta `call .venv\Scripts\activate.bat`.
2. Ejecuta `python manage.py migrate` y luego `python manage.py import_legacy_catalog`. El primer comando prepara las tablas; el segundo carga el catálogo existente.
3. Ejecuta `python manage.py runserver 8000` y abre <http://127.0.0.1:8000/>. Debes ver la portada, menú y categorías.
4. Abre <http://127.0.0.1:8000/catalogo/>. Debes ver productos con precio y tallas. Abre un producto para revisar su descripción, imagen y stock. Busca `colombia` o filtra con `?categoria=camisetas`.
5. En una ficha, elige una talla disponible y pulsa **Agregar al carrito**. Abre <http://127.0.0.1:8000/carrito/>; el producto, talla, cantidad y subtotal deben aparecer.
6. Registra una cuenta en <http://127.0.0.1:8000/cuenta/registro/> o inicia sesión en <http://127.0.0.1:8000/cuenta/entrar/>. Abre <http://127.0.0.1:8000/checkout/>; completa la dirección y confirma. Se crea un pedido de prueba y se descuenta stock, pero no se cobra dinero.
7. Abre <http://127.0.0.1:8000/admin/> e inicia sesión como superusuario. En **Products**, crea, edita y elimina un producto de prueba; confirma los cambios en el catálogo. También puedes usar el panel `/gestion/productos/`.
8. Ejecuta los tres comandos `curl.exe` de la sección API. Debes recibir JSON con categorías, productos filtrados y el detalle con tallas/stock.

Si aparece `no such table`, detén el servidor y ejecuta `python manage.py migrate`. Si el catálogo queda vacío, confirma que `.env` contiene `DATABASE_NAME=devFPCMerch.db` y ejecuta de nuevo `python manage.py import_legacy_catalog`. Si una imagen da 404, confirma que el nombre de archivo esté en `media/products/` y vuelve a importar. Si el login del admin falla, ejecuta `python manage.py changepassword admin@fpcmerch.local` o crea otra cuenta con `createsuperuser`. Si un paso da error, copia el mensaje completo de la terminal y verifica que VS Code tenga activa `.venv`.

## Datos ilustrativos y límites

`seed_demo` crea 89 productos en estas cantidades: Camisetas 24, Pantalones 12, Chaquetas 8, Uniformes 10, Medias 15 y Accesorios 20. Los nombres, descripciones, fotos placeholder y precios son contenido de prueba.

El umbral de envío gratis está fijado en `$150.000 COP`. `SHIPPING_FLAT_RATE` en `fpcmerch/settings.py` fija la tarifa inicial de ejemplo en `$12.000 COP`. La conversión de moneda y los importes comerciales deben verificarse antes de cualquier operación real.

Los indicadores «más de 500 productos», «entrega en 48 horas», «4,9 estrellas / 2.800 reseñas», devoluciones en 30 días, pago seguro, dirección, teléfono, horarios, mapa, políticas, FAQ y guía de tallas son datos de referencia/ilustrativos; no representan reseñas verificadas, una pasarela de pago, certificaciones ni compromisos comerciales comprobados. «Nueva temporada 2025» se conserva como texto de diseño. El checkout no cobra ni solicita datos bancarios.

## Frontend, backend y servidor

El frontend está en plantillas Django bajo `templates/`, CSS en `static/css/` y módulos ES bajo `static/js/`. JavaScript mejora el carrusel, el menú, los avisos, el drawer, el buscador y las llamadas `fetch`; los precios, stock y pedidos se calculan y validan en el backend. Las apps de Django organizan modelos, formularios, vistas, servicios y rutas bajo `apps/`.

En local, `python manage.py runserver` sirve la interfaz y los archivos estáticos y medios. Para producción, la configuración incluida usa Gunicorn, WhiteNoise, PostgreSQL mediante `DATABASE_URL` y Cloudinary para los medios; SQLite y el almacenamiento local permanecen activos al desarrollar sin esas variables.

## Despliegue gratuito en Render

El plan elegido sirve para una demostración o proyecto académico. Render Free duerme el servicio después de 15 minutos sin tráfico y su disco local es temporal. Por eso se recomienda conectar Neon Free para PostgreSQL y Cloudinary Free para imágenes. No uses Render Postgres Free para datos que deban durar: vence a los 30 días. Neon Free ofrece hoy 1 GB y 100 CU-horas al mes; Cloudinary ofrece 25 créditos al mes. Revisa los límites de los proveedores antes de un uso comercial.

### Servicios que debes crear manualmente

1. Crea un repositorio GitHub **privado** para la tienda. En CMD, desde la carpeta del proyecto:

   ```cmd
   git init
   git add .
   git status
   git commit -m "Preparar FPCMerch para despliegue"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
   git push -u origin main
   ```

   Antes del `commit`, comprueba que `.env`, `.venv`, `devFPCMerch.db`, `db.sqlite3` y copias de la base no aparecen en `git status`. `.gitignore` los excluye; el fixture del catálogo y las 18 imágenes actuales sí se suben. No subas contraseñas ni bases SQLite.

2. En [Neon](https://neon.com/), crea un proyecto PostgreSQL gratuito y copia la cadena de conexión desde **Connect**. Guárdala como secreto; Django ejecutará las migraciones automáticamente en el build.
3. En [Cloudinary](https://cloudinary.com/), crea una cuenta gratuita y copia **API Environment variable** (`CLOUDINARY_URL`) desde el Dashboard. Es una credencial privada; no la pegues en archivos versionados.
4. En [Render](https://render.com/), crea una cuenta, pulsa **New → Blueprint**, conecta GitHub y elige el repositorio. Render detecta `render.yaml`. Cuando solicite valores para `DATABASE_URL` y `CLOUDINARY_URL`, pega las cadenas obtenidas de Neon y Cloudinary. Render genera `SECRET_KEY`; el manifiesto deja `DEBUG=False`.
5. Espera el build y la publicación. El build instala dependencias, aplica migraciones, carga el fixture solo si el catálogo está vacío, sube a Cloudinary las imágenes que falten y ejecuta `collectstatic`. Gunicorn inicia el sitio.

### Variables de producción

| Variable | Valor |
| --- | --- |
| `SECRET_KEY` | La genera Render con `generateValue`; no la inventes ni la guardes en Git. |
| `DEBUG` | `False`. |
| `ALLOWED_HOSTS` | `.onrender.com`; Render agrega el hostname asignado a la aplicación. |
| `CSRF_TRUSTED_ORIGINS` | `https://*.onrender.com`. |
| `DATABASE_URL` | Cadena privada de conexión PostgreSQL copiada desde Neon. |
| `CLOUDINARY_URL` | Cadena privada API Environment variable copiada desde Cloudinary. |
| `EXTERNAL_RATE_URL` | `https://open.er-api.com/v6/latest/USD`; es pública y no requiere clave. |

Si vas a usar un dominio propio, añade su host a `ALLOWED_HOSTS` y su origen completo con `https://` a `CSRF_TRUSTED_ORIGINS` en Render.

### Cuenta administradora en producción

Render Free no ofrece una consola de shell para el servicio. Crea el superusuario desde CMD local conectándote temporalmente a Neon; no cambies el `.env` local:

```cmd
set /p DATABASE_URL=Pega la URL de conexión de Neon y pulsa Enter:
call .venv\Scripts\activate.bat
python manage.py createsuperuser
set DATABASE_URL=
```

En el formulario, usa el correo como nombre de inicio de sesión. En `createsuperuser`, la clave queda enmascarada y no se incluye en el historial. Abre `https://TU-SERVICIO.onrender.com/admin/` e inicia con el correo y la clave que acabas de definir. No reutilices claves locales.

### Prueba después de publicar

1. Abre la URL `.onrender.com`; si estaba inactiva, espera aproximadamente un minuto a que despierte.
2. Abre `/catalogo/`, una ficha de producto y confirma que cargan estilos, imagen, precio y stock.
3. Prueba registro, inicio de sesión y cierre de sesión; comprueba que vuelves a la portada como visitante.
4. Inicia sesión en `/admin/`, cambia temporalmente el precio de un producto, guarda y verifica el nuevo precio en `/catalogo/` y su ficha. El admin y el sitio usan la misma Neon.
5. Consulta `/api/v1/categories/`, `/api/v1/products/` y un detalle `/api/v1/products/SLUG/`; deben responder JSON y la propiedad `image` debe ser una URL de Cloudinary.
6. En Render abre **Logs** y revisa el build y los registros del servicio. En Neon revisa que el proyecto no haya excedido sus horas; en Cloudinary confirma que aparecen las imágenes.

Si hay error 500, busca el traceback más reciente en **Logs**. `DisallowedHost` se corrige incluyendo el hostname en `ALLOWED_HOSTS`; `CSRF verification failed` requiere añadir el origen HTTPS correcto a `CSRF_TRUSTED_ORIGINS`; estáticos ausentes requieren revisar `collectstatic`/WhiteNoise; imágenes ausentes requieren comprobar `CLOUDINARY_URL`, los nombres de `media/products/img/` y que el build haya terminado `sync_catalog_images`; un error de base exige revisar que Neon esté activo y `DATABASE_URL` sea su cadena correcta, con SSL. No publiques esas cadenas en reportes.

### Limitaciones y cuidado de datos

Render Free tiene 512 MB de RAM y 0,1 CPU, duerme tras 15 minutos, su primer arranque tarda cerca de un minuto y el almacenamiento del contenedor se pierde al reiniciar. No puede guardar SQLite ni cargas de imágenes de forma permanente; Cloudinary resuelve esto para las imágenes y Neon mantiene los datos relacionales. Neon suspende el cómputo tras unos cinco minutos sin actividad y despierta con la siguiente consulta; sus 100 CU-horas mensuales y 1 GB bastan para probar el proyecto, no son garantía para una tienda comercial. Cloudinary comparte sus 25 créditos entre almacenamiento, transformaciones y ancho de banda. El checkout actual simula el pago, no cobra.

Para entregar a un cliente, configura dominio propio, correo real para notificaciones y recuperación, un plan con disponibilidad continua, backups verificados de PostgreSQL y almacenamiento multimedia con límites/retención adecuados. El plan gratuito no debe ser el único respaldo de ventas reales.

## Estructura

```text
fpcmerch/                         configuración Django, URLs, WSGI y ASGI
apps/users/                       modelo de usuario, login, registro y perfil
apps/products/                    categorías, productos, tallas, catálogo y CRUD
apps/cart/                        carrito de sesión/usuario y reglas de existencias
apps/orders/                      pedidos, líneas y checkout transaccional
apps/contact/                     formulario y mensajes de contacto
apps/pages/                       inicio, contenido informativo y errores
apps/api/                         endpoints JSON y cliente HTTP de tasa de cambio
templates/                        páginas HTML y componentes compartidos
static/css/ static/js/             estilos y módulos del navegador
media/products/                   imágenes subidas o placeholders generados
docs/                              entrega académica, diagrama ER y evidencias
manage.py                         comandos de Django
requirements.txt .env.example      dependencias y configuración de ejemplo
```


# Rissos Anghell Store

Tienda personal de Benjamín Espinoza hecha en Streamlit.

## Ejecutar en tu computador

```bash
pip install -r requirements.txt
streamlit run app.py
```

Se abre en http://localhost:8501

## Tu foto

Dos opciones:
1. Guarda tu foto como `assets/benjamin.jpg` (también sirve .png o .webp), o
2. Entra como Administrador › Ajustes › "Tu foto" y súbela desde ahí.

Una foto vertical se ve mejor en el marco de arco.

## Administrador

- Contraseña inicial: `anghell2026`
- Cámbiala apenas entres: Administrador › Ajustes › Contraseña de administrador.
- (Opcional) En Streamlit Cloud puedes definirla en Secrets: `ADMIN_PASSWORD = "tu-clave"`

## Cómo registrar una venta (ej: Pepito compró la polera roja)

1. Pepito crea su cuenta en la tienda (o tú lo agregas en Clientes › "Agregar un cliente manualmente").
2. Entras como Administrador › Registrar venta.
3. Eliges a Pepito, el producto, cantidad, precio y fecha. Puedes marcar el producto como Agotado en el mismo paso.
4. En Clientes ves el ranking de quién te compra más y el perfil de cada uno con su historial.

## Dónde se guardan los datos

Todo queda en la carpeta `data/` (`db.json` + `images/`). Se crea sola la primera vez,
con 6 productos de ejemplo que puedes editar o borrar.

Importante si la publicas en Streamlit Community Cloud: ese servidor borra los archivos
cuando la app se reinicia o la actualizas. Descarga respaldos seguido desde Ajustes, o
pásate a una base de datos externa (por ejemplo Supabase) para uso real.

## Link de los productos

El botón "Consultar" arma un correo con el link directo del producto. Si publicas la app,
pega su dirección en Administrador › Ajustes › Link de la tienda para que los links
apunten al lugar correcto.

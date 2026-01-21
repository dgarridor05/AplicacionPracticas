# Resumen de Cambios - Rediseño UI "App Nativa"

Este documento detalla los cambios realizados en el proyecto para transformar la interfaz web en una experiencia similar a una aplicación nativa móvil (Mobile-First), enfocada en Ciencias del Deporte y Psicología.

## 1. Archivos Modificados

### `templates/base.html`
Este archivo recibió una reescritura casi total para implementar el nuevo sistema de diseño.

*   **Tipografía**:
    *   Se agregaron las fuentes **Montserrat** (para títulos y energía) y **Open Sans** (para textos largos y lectura cómoda) desde Google Fonts.
*   **Paleta de Colores (Variables CSS)**:
    *   Se definieron variables globales en `:root` para fácil mantenimiento:
        *   `--color-green`: #1A8E53 (Salud)
        *   `--color-orange`: #F7931E (Energía)
        *   `--color-blue`: #0078AE (Confianza)
        *   `--color-pink`: #E5679A (Empatía)
*   **Navegación Dual**:
    *   **Móvil**: Se creó una **Barra de Navegación Inferior (Bottom Bar)** fija, con iconos grandes y fácil alcance para el pulgar.
    *   **Escritorio**: Se mantuvo una barra superior, pero rediseñada con efectos de **Glassmorphism** (cristal esmerilado).
    *   Se utiliza `@media` query para mostrar u ocultar la barra correspondiente según el dispositivo.
*   **Estilos Visuales (Look & Feel)**:
    *   **Bordes**: Se aumentaron los radios de borde a `20px` en tarjetas y contenedores para una apariencia más amigable y moderna.
    *   **Sombras**: Se reemplazaron los bordes duros por sombras suaves y difusas (`box-shadow`).
    *   **Botones**: Se transformaron en estilo "píldora" (completamente redondeados).
    *   **Micro-interacciones**: Se añadió un efecto de reducción de tamaño (`scale(0.98)`) al hacer clic en botones y tarjetas para dar feedback táctil.
*   **Configuración del Viewport**:
    *   Se actualizó la etiqueta `<meta name="viewport">` para evitar el zoom automático en inputs y mejorar la sensación de app nativa.

## 2. Cambios en el Entorno

### Dependencias
*   **Instalación de `python-dotenv`**:
    *   Se detectó que el proyecto fallaba al iniciar porque faltaba esta librería. Se instaló ejecutando `pip install python-dotenv` para permitir la carga correcta de variables de entorno desde el archivo `.env`.

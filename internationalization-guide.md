# Guía de Internacionalización para WayPool

Este documento proporciona una guía para implementar la internacionalización en todas las páginas de la aplicación WayPool.

## Idiomas Soportados

Actualmente, la aplicación soporta los siguientes idiomas:

- Español (es)
- Inglés (en)
- Francés (fr)
- Alemán (de)
- 

## Estructura de Traducciones

Las traducciones se organizan en archivos específicos para cada página o funcionalidad principal:

```
client/src/translations/
├── add-liquidity.ts
├── algorithm.ts
├── analytics.ts
├── dashboard.ts
├── how-it-works.ts
├── index.ts (archivo central)
├── landing.ts
├── legal-terms.ts
├── menu.ts
├── nfts.ts
├── podcast.ts
├── positions.ts
├── referrals.ts
├── settings.ts
├── support.ts
└── transfers.ts
```

## Cómo Agregar Nuevas Traducciones

### Paso 1: Crear un Archivo de Traducción

Para cada nueva página, crea un archivo de traducción en `client/src/translations/` siguiendo este patrón:

```typescript
// Traducciones para la página X

export interface XTranslations {
  // Agrupa las claves por secciones o categorías
  // Títulos y encabezados
  title: string;
  subtitle: string;
  
  // Otras secciones...
}

export const xTranslations = {
  es: {
    // Traducciones en español
    title: "Título en Español",
    subtitle: "Subtítulo en Español",
    // ...
  },
  en: {
    // Traducciones en inglés
    title: "Title in English",
    subtitle: "Subtitle in English",
    // ...
  },
  fr: {
    // Traducciones en francés
    title: "Titre en Français",
    subtitle: "Sous-titre en Français",
    // ...
  },
  de: {
    // Traducciones en alemán
    title: "Titel auf Deutsch",
    subtitle: "Untertitel auf Deutsch",
    // ...
  }
};
```

### Paso 2: Registrar el Archivo en el Índice

Actualiza `client/src/translations/index.ts` para importar y exportar las nuevas traducciones:

```typescript
import { xTranslations } from './x';

// Añade a la exportación de traducciones
export const translations = {
  // Traducciones existentes...
  x: xTranslations,
};
```

### Paso 3: Usar las Traducciones en los Componentes

En tu componente/página, utiliza el hook `useLanguage` para acceder a las traducciones:

```typescript
import { useLanguage } from "@/context/language-context";

function MyComponent() {
  const { language } = useLanguage();
  const t = (key: string) => {
    // Obtener traducciones para la página actual
    const translations = allTranslations.x[language];
    return translations[key] || key;
  };
  
  return (
    <div>
      <h1>{t('title')}</h1>
      <p>{t('subtitle')}</p>
      {/* ... */}
    </div>
  );
}
```

## Mejores Prácticas

1. **Organiza las traducciones por categorías** dentro de cada archivo para facilitar su mantenimiento.
2. **Usa claves descriptivas** que indiquen claramente el propósito del texto.
3. **Mantén la consistencia** en la terminología entre diferentes archivos.
4. **Proporciona traducciones para todos los idiomas soportados** - Siempre incluye todos los idiomas del selector.
5. **Verifica textos que puedan tener longitudes variables** en diferentes idiomas y asegúrate de que la interfaz se adapte correctamente.
6. **Usa palabras comunes** del archivo central para elementos como botones, mensajes de estado, etc.
7. **Usa siempre inglés como idioma predeterminado** - El inglés debe ser el idioma base para todas las traducciones.

## Patrón de Renderizado de Traducciones

Para componentes que no utilizan los hooks de traducción, implementa siempre el siguiente patrón de renderizado condicional:

```jsx
{language === 'en' ? 'English Text' : 
 language === 'es' ? 'Spanish Text' : 
 language === 'fr' ? 'French Text' : 
 'German Text'}
```

Este patrón debe aplicarse consistentemente en todos los componentes para mantener una internacionalización uniforme en toda la aplicación.

## Verificación de Traducciones Faltantes

Puedes utilizar la función `checkMissingTranslations()` exportada desde `client/src/translations/index.ts` para identificar traducciones faltantes en cualquier idioma.

```typescript
import { checkMissingTranslations } from "@/translations";

// En alguna parte del código para depuración
console.log(checkMissingTranslations());
```

## Proceso para Internacionalizar Páginas Existentes

1. **Identifica los textos estáticos** en la página.
2. **Crea un archivo de traducción** para la página si no existe.
3. **Reemplaza los textos estáticos** con llamadas a la función de traducción.
4. **Prueba la página en todos los idiomas** para verificar que se muestra correctamente.

## Proceso para Agregar Nuevos Idiomas

1. **Actualiza `SUPPORTED_LANGUAGES`** en `client/src/translations/index.ts`.
2. **Agrega traducciones para el nuevo idioma** en todos los archivos de traducción.
3. **Actualiza el selector de idioma** en la interfaz para incluir el nuevo idioma.
4. **Prueba la aplicación** en el nuevo idioma.
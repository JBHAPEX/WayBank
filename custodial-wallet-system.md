# Sistema de Wallet Custodiado WayPool

## Descripción General

El sistema de wallet custodiado de WayPool proporciona una solución segura para usuarios que desean gestionar activos blockchain sin tener que manejar directamente claves privadas. Este documento técnico describe la arquitectura, mecanismos de seguridad, y procesos críticos del sistema, incluyendo la implementación mejorada de frases semilla para recuperación.

## Arquitectura del Sistema

### Componentes Principales

1. **Gestión de Wallets Custodiados**
   - Creación de wallets con claves privadas cifradas
   - Almacenamiento seguro de datos sensibles
   - Gestión de sesiones y autenticación

2. **Sistema de Recuperación**
   - Recuperación por correo electrónico
   - Recuperación por frase semilla única
   - Tokens de recuperación con tiempo limitado

3. **Base de Datos**
   - Tablas para wallets custodiados
   - Tablas para sesiones
   - Tablas para tokens de recuperación
   - Tabla para frases semilla (wallet_seed_phrases)

## Implementación de Seguridad de Frases Semilla

### Generación de Frases Semilla

El sistema utiliza un generador de frases semilla determinista y criptográficamente seguro que:

1. **Garantiza unicidad por wallet**: Cada dirección de wallet tiene una frase semilla única y exclusiva.
2. **Utiliza estándares BIP39**: Las frases se generan utilizando el wordlist estándar BIP39 en inglés.
3. **Aplica hashing criptográfico**: Uso de HMAC-SHA512 para derivar frases a partir de la dirección.
4. **Mantiene compatibilidad**: Sistema dual que soporta tanto frases en inglés (nuevas) como en español (legacy).

```javascript
// Ejemplo simplificado del generador de frases semilla
function generateEnglishSeedPhrase(walletAddress) {
  // Normalizar la dirección
  const normalizedAddress = walletAddress.toLowerCase().replace('0x', '');
  
  // Derivar clave usando HMAC-SHA512
  const hmac = crypto.createHmac('sha512', seedGeneratorConfig.salt);
  hmac.update(normalizedAddress);
  const addressHmac = hmac.digest('hex');
  
  // Seleccionar 12 palabras del wordlist BIP39 en inglés
  const seedWords = [];
  for (let i = 0; i < 12; i++) {
    const segment = addressHmac.substring(i * 8, (i * 8) + 8);
    const segmentValue = parseInt(segment, 16);
    const wordIndex = segmentValue % ENGLISH_WORDLIST.length;
    seedWords.push(ENGLISH_WORDLIST[wordIndex]);
  }
  
  return seedWords.join(' ');
}
```

### Verificación de Frases Semilla

El sistema implementa un mecanismo de verificación de varias etapas que:

1. **Verifica frases en múltiples idiomas**: Compatible con frases en inglés (actuales) y español (legacy).
2. **Utiliza comparaciones seguras**: Implementa técnicas para prevenir ataques de temporización.
3. **Admite múltiples formatos**: Normaliza las entradas para hacer la verificación robusta frente a variaciones de mayúsculas/minúsculas o espacios adicionales.

```javascript
// Ejemplo simplificado del verificador de frases semilla
function verifySeedPhrase(seedPhrase, walletAddress) {
  // Normalizar la frase semilla ingresada
  const normalizedInput = seedPhrase.trim().toLowerCase();
  
  // MÉTODO 1: Verificar en inglés (método principal)
  const englishPhrase = generateEnglishSeedPhrase(walletAddress).toLowerCase();
  if (normalizedInput === englishPhrase) {
    return true;
  }
  
  // MÉTODO 2: Verificar en español (compatibilidad retroactiva)
  const spanishPhrase = generateSpanishSeedPhrase(walletAddress).toLowerCase();
  if (normalizedInput === spanishPhrase) {
    return true;
  }
  
  return false;
}
```

### Almacenamiento Seguro

1. **Base de datos específica**: Las frases semilla se almacenan en una tabla dedicada (`wallet_seed_phrases`).
2. **Sin almacenamiento innecesario**: Las frases solo se generan cuando se solicitan, reduciendo el riesgo de exposición.
3. **Asociación directa**: Cada frase está vinculada a una dirección de wallet específica.

## Flujo de Recuperación

### Recuperación por Frase Semilla

1. El usuario inicia el proceso de recuperación seleccionando "Recuperar con frase semilla"
2. Introduce su frase semilla de 12 palabras en el formulario
3. El sistema verifica la frase contra todas las wallets:
   - Primero comprueba si coincide con la frase generada en inglés
   - Si no hay coincidencia, verifica con la frase en español (compatibilidad)
4. Al encontrar coincidencia, el usuario puede establecer una nueva contraseña
5. El sistema actualiza las credenciales y establece una nueva sesión

### Recuperación por Email

1. El usuario solicita recuperación proporcionando su correo electrónico
2. El sistema genera un token de recuperación con tiempo limitado
3. Se envía un correo electrónico con un enlace seguro
4. Al acceder al enlace, el usuario puede establecer una nueva contraseña
5. El token se marca como utilizado para prevenir reutilización

## Mejoras de Seguridad Implementadas

### Actualizaciones Recientes

1. **Migración a BIP39 estándar**: Implementación del wordlist en inglés para nuevas frases semilla.
2. **Compatibilidad dual**: Sistema que verifica tanto frases en inglés como en español.
3. **Protección contra timing attacks**: Uso de comparaciones de tiempo constante.
4. **Verificación progresiva**: Comprobación de frases legítimas sin exponer información sensible.
5. **Mensajes de error genéricos**: Prevención de enumeración de wallets.

### Consideraciones adicionales

1. **Prevención de fuerza bruta**: Limitación de intentos de recuperación.
2. **Auditoría de operaciones**: Registro de intentos de recuperación (exitosos y fallidos).
3. **Aislamiento de datos**: Separación de datos sensibles y no sensibles.

## Esquema de la Base de Datos

```sql
-- Tabla principal de wallets custodiados
CREATE TABLE custodial_wallets (
  id SERIAL PRIMARY KEY,
  address VARCHAR(255) NOT NULL UNIQUE,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  salt VARCHAR(255) NOT NULL,
  encrypted_private_key TEXT NOT NULL,
  encryption_iv VARCHAR(255) NOT NULL,
  active BOOLEAN DEFAULT TRUE,
  last_login_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);

-- Tabla para almacenar frases semilla
CREATE TABLE wallet_seed_phrases (
  id SERIAL PRIMARY KEY,
  wallet_address VARCHAR(255) NOT NULL UNIQUE,
  seed_phrase TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabla para tokens de recuperación
CREATE TABLE custodial_recovery_tokens (
  id SERIAL PRIMARY KEY,
  wallet_id INTEGER NOT NULL,
  email VARCHAR(255) NOT NULL,
  recovery_token VARCHAR(255) NOT NULL UNIQUE,
  expires_at TIMESTAMP NOT NULL,
  used BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (wallet_id) REFERENCES custodial_wallets(id) ON DELETE CASCADE
);
```

## Consideraciones de Seguridad

1. **Protección de datos**: Las claves privadas nunca se almacenan en texto plano.
2. **Aislamiento de componentes**: Separación entre la lógica de autenticación y la gestión de wallets.
3. **Defensa en profundidad**: Múltiples capas de validación y autenticación.
4. **Frases semilla seguras**: Generación determinista pero criptográficamente segura.
5. **Compatibilidad retroactiva**: Soporte para sistemas anteriores sin comprometer la seguridad.

## Conclusión

El sistema de wallet custodiado WayPool proporciona una solución robusta que equilibra seguridad y facilidad de uso. Las mejoras implementadas en el sistema de frases semilla aseguran que los usuarios puedan recuperar sus wallets de manera segura, mientras que el sistema mantiene la compatibilidad con implementaciones anteriores.

La migración a frases semilla en inglés siguiendo el estándar BIP39 refuerza la seguridad y la interoperabilidad del sistema, permitiendo una mayor flexibilidad para futuras expansiones y mejoras.
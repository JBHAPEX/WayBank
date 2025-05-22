# Sistema de Wallets Custodiales WayPool

## Introducción

El sistema de wallets custodiales de WayPool ofrece una forma segura y accesible para gestionar criptomonedas sin la necesidad de manejar claves privadas o frases semilla. Este documento explica el funcionamiento, características y estado actual del sistema, incluyendo las mejoras de seguridad implementadas y la compatibilidad con múltiples redes blockchain.

## Estado actual del sistema (Mayo 2025)

### Auditoría de seguridad

La auditoría realizada en Mayo 2025 ha detectado y corregido las siguientes vulnerabilidades críticas:

1. **Vulnerabilidad de semillas estáticas**: Se identificó y corrigió un problema crítico donde todas las wallets custodiadas compartían la misma frase semilla hardcodeada en el código, lo que comprometía la seguridad de todos los fondos.

2. **Implementación incompleta del sistema de transferencias**: Se ha completado la implementación del sistema de descifrado de claves privadas para permitir transferencias seguras desde los wallets custodiados.

### Mejoras implementadas

1. **Generación única de semillas**: Cada wallet ahora tiene su propia frase semilla única y segura, generada criptográficamente y almacenada de forma cifrada en la base de datos.

2. **Sistema de descifrado seguro**: Se ha implementado un sistema completo de cifrado/descifrado utilizando AES-256-GCM con la variable de entorno `WALLET_MASTER_KEY` como clave maestra.

3. **Verificación de sesión mejorada**: Mejora en el sistema de verificación de sesiones para garantizar que solo los propietarios legítimos puedan acceder a sus wallets.

4. **Transferencias funcionales**: Los usuarios ahora pueden transferir ETH, tokens ERC20 y NFTs desde sus wallets custodiados a cualquier dirección.

### Estado de las wallets existentes

- **Seguridad de wallets antiguos**: Todos los wallets creados antes de esta actualización mantienen sus claves privadas originales y ahora son seguros para su uso.

- **Compatibilidad retrospectiva**: No se requieren acciones por parte de los usuarios existentes; sus wallets siguen funcionando con la nueva implementación de seguridad.

- **Datos de wallets**: Cada wallet custodiado en la base de datos contiene:
  - `encrypted_private_key`: Clave privada cifrada única para cada usuario
  - `encryption_iv`: Vector de inicialización para el cifrado (único por wallet)
  - `salt`: Sal criptográfica única para el proceso de cifrado

## Características principales

### Seguridad y accesibilidad

- **Gestión de claves centralizada**: WayPool almacena las claves privadas de forma segura y única para cada usuario.
- **Autenticación mediante contraseña**: Los usuarios acceden a sus fondos utilizando contraseñas personalizadas.
- **Recuperación vía email y OTP**: En caso de olvidar la contraseña, los usuarios pueden recuperar el acceso mediante un proceso de verificación por email y código OTP.
- **Cifrado AES-256-GCM**: Las claves privadas se almacenan utilizando cifrado de grado militar.

### Compatibilidad multi-red

El sistema de wallets WayPool es compatible con las siguientes redes blockchain:

- Ethereum (Mainnet)
- Polygon
- Arbitrum
- Optimism
- Base
- Avalanche
- Unichain (nueva integración)
- Monero (a través del conector especializado)

### Detección de tokens

- **Tokens estándar**: Reconocimiento automático de tokens populares (USDC, USDT, ETH, MATIC, etc.).
- **Tokens personalizados**: Posibilidad de añadir manualmente tokens menos comunes.
- **Tiempo de detección**: 1-3 minutos para la mayoría de las transacciones, dependiendo de la congestión de la red.

## Arquitectura del sistema de wallets

### Componentes principales

1. **Módulo de gestión de claves**
   - `server/custodial-wallet/service.ts`: Gestión principal de wallets custodiales
   - `server/custodial-wallet/transfer-service.ts`: Servicio de transferencias seguras
   - `server/api-wallet-seed.js`: API para la gestión de frases semilla (ahora con generación única)
   - `server/unique-seed-generator.js`: Generación de frases semilla determinísticas y únicas

2. **Sistema de cifrado/descifrado**
   - Algoritmo: AES-256-GCM
   - Clave maestra: Almacenada como variable de entorno `WALLET_MASTER_KEY`
   - Vector de inicialización: Único para cada wallet, almacenado junto con la clave privada cifrada
   - Salt: Valor único por wallet para añadir entropía adicional

3. **Base de datos**
   - Tabla `wallet_seed_phrases`: Almacena las frases semilla cifradas
   - Tabla `wallet_private_keys`: Almacena las claves privadas cifradas
   - Columnas de seguridad: `encrypted_private_key`, `encryption_iv`, `salt`

### Flujo de funcionamiento

#### Creación y acceso a wallets

1. **Registro de wallet**: 
   - El usuario proporciona una contraseña segura
   - El sistema genera una frase semilla única
   - Se deriva la clave privada desde la semilla
   - La clave privada se cifra con AES-256-GCM usando `WALLET_MASTER_KEY`
   - Se almacena en la base de datos junto con IV y salt únicos

2. **Inicio de sesión**: 
   - El acceso se realiza mediante la dirección del wallet y la contraseña establecida
   - El sistema verifica la contraseña y genera un token de sesión temporal

3. **Sesiones**: 
   - El sistema genera tokens de sesión únicos para mantener la autenticación
   - Las sesiones tienen un tiempo de vida limitado por seguridad

#### Transferencia de fondos

1. **Solicitud de transferencia**:
   - El usuario especifica el activo, cantidad y dirección destino
   - El sistema verifica la sesión y los permisos del usuario

2. **Descifrado de clave privada**:
   - Se recupera la clave privada cifrada, IV y salt desde la base de datos
   - Se utiliza `WALLET_MASTER_KEY` para descifrar la clave privada
   - El proceso se realiza en memoria y la clave privada nunca se almacena descifrada

3. **Firma y envío de transacción**:
   - Se firma la transacción con la clave privada descifrada
   - Se envía la transacción firmada a la red blockchain
   - Se registra la transacción en el histórico del usuario

4. **Verificación y confirmación**:
   - El sistema monitorea la transacción hasta su confirmación
   - Se notifica al usuario sobre el estado de la transacción

## Consideraciones importantes

### Ventajas

- **Facilidad de uso**: Ideal para usuarios nuevos en el ecosistema blockchain.
- **Seguridad mejorada**: Reducción del riesgo de pérdida de fondos por errores de usuario.
- **Experiencia simplificada**: No es necesario gestionar múltiples claves privadas o frases semilla.
- **Transferencias seguras**: Sistema completo para transferir activos digitales con seguridad.

### Limitaciones

- **Custodia centralizada**: La gestión de claves está centralizada en WayPool, contrario al principio "not your keys, not your coins".
- **Dependencia del servicio**: El acceso a los fondos depende de la disponibilidad del servicio WayPool.
- **No exportable**: Las claves privadas y frases semilla no se proporcionan a los usuarios.

### Riesgos

- Una vez transferidos los fondos a un wallet WayPool, no es posible recuperarlos mediante métodos tradicionales de recuperación de wallet (frase semilla de 12 palabras).
- La seguridad de los fondos depende de la robustez de la infraestructura de WayPool y de la seguridad de la contraseña establecida por el usuario.
- La clave maestra del sistema (`WALLET_MASTER_KEY`) debe mantenerse absolutamente segura, ya que su compromiso podría afectar a todos los wallets.

## Recomendaciones para usuarios

- Utilizar contraseñas fuertes y únicas para proteger el acceso al wallet.
- Mantener actualizada la información de contacto para la recuperación por email.
- Realizar copias de seguridad de las contraseñas utilizando gestores de contraseñas seguros.
- Verificar las direcciones de destino antes de realizar transferencias.
- Para cantidades importantes, considerar utilizar wallets no custodiales con control total sobre las claves privadas.

## Plan de desarrollo futuro

Las siguientes mejoras están planificadas para implementarse en el sistema de wallets:

1. **Sistema de exportación opcional**: Permitir a los usuarios avanzados exportar sus frases semilla con las advertencias y protecciones adecuadas.

2. **Autenticación de múltiples factores**: Añadir opciones adicionales de MFA incluyendo autenticación por app, SMS y hardware.

3. **Firmas Multi-sig**: Implementar un sistema opcional de firmas múltiples para wallets de alta seguridad.

4. **Auditoría blockchain**: Mejorar la transparencia mediante un sistema de verificación pública de saldos.

5. **Límites de transferencia personalizables**: Permitir a los usuarios establecer límites diarios de transferencia para mejorar la seguridad.
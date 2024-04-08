# HULK Compiler

## Autores

Amananda Noris Hernández C412

Juan Miguel Pérez Martínez C412

Marcos Antonio Pérez Lorenzo C412

## Subproyectos

Para utilizar los subproyectos (los generadores de lexer y parser) abra una terminal en la carpeta \[subprojecto\]/src/ y ejecute

 - Lexer ([LLEX](https://github.com/MarcosHCK/llex)): luajit llex.lua \[plantilla\] > \[archivo de salida\]
 - Parser ([LCC](https://github.com/MarcosHCK/lcc)): luajit lcc.lua \[plantilla\] > \[archivo de salida\]

## Paso 1: Lexer

El lexer se encarga de tomar una secuencia de caracteres (el código fuente) y dividirla en tokens, que son las unidades básicas de significado en un lenguaje de programación. Cada token representa una palabra clave, un identificador, un operador, un delimitador, o cualquier otro elemento que tenga significado en el lenguaje.

El proceso de análisis léxico se realiza en un bucle que lee caracteres de la entrada, los procesa según las reglas definidas, y produce tokens cuando encuentra una coincidencia. Si se encuentra un token válido, se genera y se devuelve. Si se encuentra un carácter que no coincide con ninguna regla, se lanza una excepción `LexerException`.

### Expresiones regulares

Las expresiones regulares, también conocidas como regex o regexp, son una herramienta poderosa y versátil en programación que permite buscar y manipular patrones de texto de manera eficiente. Se componen de caracteres literales, que representan a sí mismos, y metacaracteres, que tienen significados especiales y permiten definir reglas y condiciones más complejas que las simples coincidencias de texto.

Las expresiones regulares se construyen utilizando operadores como la unión, la concatenación y la clausura de Kleene. Estos operadores permiten combinar y repetir patrones de texto para formar expresiones más complejas. Cada expresión regular tiene un autómata finito asociado, lo que significa que puede representar un conjunto finito de cadenas de texto. Los metacaracteres son fundamentales en las expresiones regulares, ya que permiten definir patrones más complejos.

### Algoritmo de Thompson

El algoritmo de Thompson, también conocido como el algoritmo McNaughton-Yamada-Thompson, es un método utilizado en ciencias de la computación para transformar una expresión regular en un autómata finito no determinista (NFA) equivalente. Este NFA puede ser utilizado para hacer coincidir cadenas de texto con la expresión regular. El algoritmo es de interés práctico ya que permite compilar expresiones regulares en NFAs, y desde un punto de vista teórico, es parte de la demostración de que ambas representaciones aceptan exactamente los mismos lenguajes, es decir, los lenguajes regulares.

El algoritmo de Thompson trabaja de manera recursiva, dividiendo una expresión regular en sus subexpresiones constituyentes, a partir de las cuales se construirá el NFA utilizando un conjunto de reglas específicas. Para una expresión regular \(E\), el NFA resultante \(A\) con la función de transición \(\Delta\) cumple con las siguientes propiedades:

- \(A\) tiene exactamente un estado inicial \(q_0\), que no es accesible desde ningún otro estado. Es decir, para cualquier estado \(q\) y cualquier letra \(a\), \(\Delta(q,a)\) no contiene \(q_0\).
- \(A\) tiene exactamente un estado final \(q_f\), que no es co-accesible desde ningún otro estado. Es decir, para cualquier letra \(a\), \(\Delta(q_f,a)=\emptyset\).
- El número de estados de \(A\) es \(2s - c\), donde \(c\) es el número de concatenación de la expresión regular \(E\) y \(s\) es el número de símbolos aparte de los paréntesis (es decir, \(|\), \(*\), \(a\) y \(\epsilon\)). Esto significa que el número de estados es lineal en el tamaño de \(E\).
- El número de transiciones que salen de cualquier estado es a lo sumo dos.

Dado que un NFA de \(m\) estados y a lo sumo \(e\) transiciones desde cada estado puede hacer coincidir una cadena de longitud \(n\) en tiempo \(O(emn)\), un NFA de Thompson puede hacer coincidir patrones en tiempo lineal, asumiendo un alfabeto de tamaño fijo .

Este algoritmo es fundamental en el procesamiento de texto y en la construcción de herramientas de búsqueda avanzada, ya que permite convertir expresiones regulares complejas en estructuras de datos que pueden ser ejecutadas eficientemente por computadoras. Además, una vez construido el NFA, puede ser convertido en un autómata finito determinista (DFA) mediante la construcción de potencia y luego minimizado para obtener un autómata óptimo correspondiente a la expresión regular dada .

### Algoritmo de Powerset

El algoritmo de Power Set Construction, también conocido como construcción de conjunto potencia o construcción de subconjunto, es un método fundamental en la teoría de autómatas y en el diseño de compiladores en ciencias de la computación. Se utiliza para convertir un autómata finito no determinista (NFA) en un autómata finito determinista (DFA) equivalente.

El algoritmo de Power Set Construction se basa en los principios de la teoría de conjuntos y puede resultar en un número total de estados en el DFA igual al conjunto potencia de los estados del NFA.

El algoritmo funciona creando un nuevo estado en el DFA para cada subconjunto de estados del NFA original. Este nuevo estado se determina siguiendo las transiciones de la NFA de cada estado en el subconjunto. Si alguno de estos estados es un estado de aceptación en el NFA, entonces el nuevo estado también se considera un estado de aceptación en el DFA. Este proceso se repite hasta que se hayan considerado todos los subconjuntos posibles de los estados del NFA.

En resumen, el algoritmo de Power Set Construction es esencial en la teoría de autómatas y en el diseño de compiladores, ya que permite convertir autómatas no deterministas en autómatas deterministas equivalentes, mejorando así la eficiencia en la compilación de lenguajes de alto nivel en código comprensible por máquinas y en la coincidencia de cadenas para expresiones regulares.

![Ejemplo de automata producido](1.jpg "Ejemplo de automata producido")
![Ejemplo de automata producido](2.jpg "Ejemplo de automata producido")
![Ejemplo de automata producido](3.jpg "Ejemplo de automata producido")
![Ejemplo de automata producido](4.jpg "Ejemplo de automata producido")

### Posibles mejoras del lexer

Consideramos que con mayor tiempo para la realizacion del proyectos pudieramos incorporar algoritmos para la optimizacion del automata, como puede ser el algoritmo de Brzozowski.

#### Algoritmo de Brzozowski

Este algoritmo es particularmente útil para la minimización de autómatas finitos deterministas (DFA) y se basa en la construcción de autómatas no deterministas (NFA) para el lenguaje inverso del autómata original. Luego, se utiliza el algoritmo de PowerSet para convertir este NFA en un DFA, que es el autómata mínimo para el lenguaje original .

El algoritmo de Brzozowski funciona de la siguiente manera:

1. Conversión del DFA original a NFA para el lenguaje inverso: Se invierten todas las flechas del DFA original y se intercambian los roles de los estados iniciales y de aceptación. Esto resulta en un NFA que reconoce el lenguaje inverso del original.

2. Aplicación del algoritmo de PowerSet al NFA: Se utiliza el algoritmo de PowerSet para convertir el NFA del lenguaje inverso en un DFA. Este DFA es equivalente al autómata mínimo para el lenguaje inverso.

3. Conversión del DFA del lenguaje inverso a NFA para el lenguaje original: Se repite el proceso de inversión y aplicación del algoritmo de PowerSet para obtener el autómata mínimo para el lenguaje original.

Este algoritmo es eficaz para minimizar DFA, aunque su complejidad en el peor de los casos es exponencial. Sin embargo, en muchas prácticas, el algoritmo de Brzozowski puede realizar la minimización más rápido de lo que sugiere su complejidad en el peor caso .

## Paso 2: Gramatica y Parser

### Parser LR(1) canonico

Los parsers LR(1) son una variante de los parsers LR, que son parsers de tipo bottom-up utilizados para analizar gramáticas libres de contexto en tiempo lineal.

El término "LR(1)" se refiere a la capacidad del parser de leer la entrada de izquierda a derecha (L), producir una derivación por la derecha en reversa (R), y utilizar hasta 1 símbolo de entrada no consumido (lookahead) para tomar decisiones de análisis. Esto permite al parser determinar la acción correcta a tomar en cada paso del análisis sin necesidad de retroceder o adivinar.

La construcción de las tablas de análisis LR(1) se realiza de manera similar a las tablas LR(0), pero con la adición de un terminal de lookahead en cada ítem. Esto significa que, a diferencia de los parsers LR(0), un ítem puede llevar a diferentes acciones dependiendo del terminal que siga, lo que permite una mayor precisión en la toma de decisiones durante el análisis.

Los parsers LR(1) son determinísticos, lo que significa que producen un único análisis correcto sin necesidad de retroceso o adivinación, lo que los hace ideales para el procesamiento de lenguajes de programación. Sin embargo, su complejidad en el peor de los casos puede ser alta, especialmente para gramáticas grandes, debido al crecimiento exponencial del número de estados en la máquina de estados finita que representan el parser .

### Construccion de la tabla

La construcción de la tabla de análisis en un parser LR(1) canónico sigue un proceso específico que se basa en la construcción de ítems LR(1) y la generación de estados a partir de estos ítems. El proceso paso a paso seria:

1. Generación de ítems LR(1): Los ítems LR(1) son pares de la forma [P, a], donde P es una producción de la gramática con un punto en alguna posición de la derecha (rhs) y a es un símbolo de lookahead (o EOF). El punto en un ítem indica la posición actual en la derivación. Por ejemplo, [A→β•γ, a] significa que el input visto hasta ahora es consistente con el uso de A → βγ inmediatamente después del símbolo en la cima de la pila, y que el parser ha reconocido β  .

2. Construcción de estados : A partir de los ítems LR(1), se generan estados del parser. Cada estado representa un conjunto de ítems LR(1). La construcción de estados se realiza utilizando las funciones de clausura y goto, que determinan los estados a los que se puede llegar a partir de un estado dado mediante una transición con un símbolo terminal o no terminal  .

3. Construcción de la tabla de análisis : Para cada estado, se determina la acción a tomar para cada símbolo terminal y no terminal. Las acciones pueden ser:
   - Shift : Transición a otro estado usando un símbolo terminal.
   - Goto : Transición a otro estado usando un no-terminal.
   - Reduce : Aplicar una producción de la gramática para reducir el símbolo en la cima de la pila y reemplazarlo por el lado izquierdo de la producción, utilizando el símbolo de lookahead para determinar la acción correcta  .

La construcción de la tabla de análisis LR(1) es un proceso iterativo que comienza con un conjunto inicial de ítems LR(1) y genera estados y acciones basadas en estos ítems. Este proceso es fundamental para la implementación de parsers LR(1) canónicos, permitiendo el análisis de gramáticas libres de contexto de manera eficiente y determinista .

### Gramatica

Nuestra gramatica esta estructurada de forma tal que no existen conflictos shift/reduce o reduce/reduce, basandonos en el correcto funcionamiento del parser.

### Posibles mejoras del parser

Consideramos que con mayor tiempo para la realizacion del proyectos pudieramos incorporar algoritmos parala resolucion de conflictos.

Manejo de conflictos : Durante la construcción de la tabla de análisis, pueden surgir conflictos, como conflictos shift/reduce o reduce/reduce. Estos conflictos ocurren cuando hay múltiples acciones posibles para un símbolo dado en un estado. La resolución de estos conflictos es crucial para la correcta construcción de la tabla de análisis y el funcionamiento del parser.

## Paso 3: Chequeo semantico

El chequeo semántico se utiliza para verificar la corrección de tipos en un programa, asegurando que las operaciones se realicen entre tipos compatibles y que las variables y funciones se utilicen de manera adecuada, que los tipos de datos sean correctos y que las variables estén definidas antes de su uso. Esto es una parte crucial del proceso de compilación o interpretación, ya que ayuda a detectar errores antes de la ejecución del código. Se recorre el AST y realizan comprobaciones específicas para cada tipo de nodo, como operadores binarios, bloques de código, accesos a miembros de clases, declaraciones condicionales, constantes, asignaciones destructivas, declaraciones de funciones, invocaciones de funciones, declaraciones `let`, valores nuevos, parámetros, declaraciones de protocolos, declaraciones de tipos, operadores unarios y valores de variables. Se gestiona el alcance de tipos y variables en un contexto.

## Patron visitor

El patrón Visitor es un patrón de diseño de comportamiento que permite separar algoritmos de los objetos sobre los que operan. Este patrón es especialmente útil en el chequeo semántico, donde se necesita realizar operaciones sobre una estructura de objetos compleja, como un árbol de sintaxis abstracta (AST), sin modificar las clases de los objetos en sí.

El patrón Visitor se compone de dos partes principales:

1. Elementos : Son los objetos sobre los que se realizarán las operaciones. Cada elemento debe implementar un método de "aceptación" que acepta un objeto visitante.

2. Visitantes : Son objetos que implementan una interfaz de visitante, que define un conjunto de métodos visitantes. Cada método visitante corresponde a una clase de elemento y realiza una operación específica sobre ese tipo de elemento.

El proceso de chequeo semántico con el patrón Visitor implica los siguientes pasos:

- Definición de la interfaz de visitante : Se define una interfaz de visitante con un método visitante para cada tipo de elemento en la estructura de objetos.

- Implementación de los métodos visitantes : Se implementan los métodos visitantes en una o más clases visitantes concretas. Cada método visitante realiza una operación específica, como verificar la semántica de un tipo de elemento.

- Aceptación de visitantes : Cada elemento en la estructura de objetos implementa el método de aceptación, que acepta un objeto visitante y delega la operación a este visitante.

- Visita de elementos : El cliente crea un objeto visitante concreto y lo pasa a los elementos de la estructura de objetos a través del método de aceptación. Los elementos invocan el método visitante correspondiente en el visitante, permitiendo que el visitante realice la operación específica sobre el elemento.

El patrón Visitor es especialmente útil en el chequeo semántico porque permite añadir nuevas operaciones a la estructura de objetos sin modificar las clases de los objetos. Esto es crucial en el chequeo semántico, donde las operaciones pueden variar ampliamente y las clases de objetos pueden cambiar con frecuencia.

Además, el patrón Visitor facilita la separación de la lógica de negocio de comportamientos auxiliares, manteniendo las clases primarias de la aplicación centradas en sus trabajos principales. Esto es beneficioso en el chequeo semántico, donde la lógica de negocio y los detalles de implementación pueden ser complejos y desacoplarlos puede mejorar la mantenibilidad y la escalabilidad del código.

## Paso 4: Generacion de codigo

### LLVM

LLVM (Low Level Virtual Machine) es un conjunto de proyectos de código abierto que proporciona una infraestructura de compilación de código de nivel intermedio (IR) y herramientas para optimizar, analizar y generar código de bajo nivel. LLVM es ampliamente utilizado en el desarrollo de lenguajes de programación y compiladores debido a su flexibilidad y eficiencia.

LLVM es conocido por su capacidad para generar código de alto rendimiento y su soporte para una amplia gama de optimizaciones. Además, LLVM proporciona una API en C++ que permite a los desarrolladores interactuar con el IR de LLVM y las herramientas de optimización.

#### LLVMlite

Es una biblioteca ligera de enlaces de Python para LLVM, diseñada específicamente para escribir compiladores JIT (Just-In-Time) y utilizada principalmente por Numba, un compilador JIT para Python. Esta biblioteca proporciona una interfaz de Python para LLVM, permitiendo a los desarrolladores interactuar con el IR (Intermediate Representation) de LLVM, optimizar el código y compilarlo en tiempo de ejecución.

El enfoque de llvmlite se centra en ser ligero y eficiente, proporcionando solo las partes necesarias de la API de LLVM que son relevantes para la creación de compiladores JIT. Esto incluye:

- Un pequeño envoltorio C alrededor de las partes de la API de LLVM C++ que no están expuestas por la API de LLVM C.
- Un envoltorio Python puro alrededor de la API de LLVM C.
- Una implementación pura de Python del subconjunto del constructor de IR de LLVM que se necesita para Numba.

## Consideraciones generales: Lua en los generadores

Escogimos Lua para programar los generadores de parser y lexer debido a:

1. Flexibilidad y Extensibilidad : Lua es un lenguaje de programación ligero y dinámico, lo que lo hace muy flexible para adaptarse a diferentes gramáticas y estructuras de lenguaje. Esto es especialmente útil en el desarrollo de generadores de parser y lexer, donde la capacidad de adaptarse a diferentes dominios específicos es crucial .

2. Sintaxis Simple y Clara : La sintaxis de Lua es simple y clara, lo que facilita la lectura y escritura de código. Esto es beneficioso en el desarrollo de DCL, donde la claridad y la facilidad de uso son importantes para los usuarios finales.

3. Integración con Herramientas Existentes : Lua es un lenguaje de scripting que se puede integrar fácilmente con otros lenguajes de programación y herramientas. Esto permite a los desarrolladores aprovechar las bibliotecas y herramientas existentes para el análisis léxico y sintáctico, y luego utilizar Lua para implementar la lógica específica de su DCL .

4. Comunidad Activa y Recursos Disponibles : Lua tiene una comunidad activa y una amplia gama de recursos disponibles, incluyendo bibliotecas y herramientas para el análisis léxico y sintáctico. Esto facilita el acceso a soluciones y ejemplos prácticos que pueden servir como punto de partida para el desarrollo de generadores de parser y lexer .

5. Creación de DSLs : Lua permite la creación de lenguajes de dominio específico (DSL, por sus siglas en inglés) a través de la construcción de mini-lenguajes dentro del lenguaje host. Esto es particularmente útil en el desarrollo de DCL, donde se requiere una sintaxis y semántica específicas para un dominio particular .

En resumen, Lua ofrece una combinación de simplicidad, flexibilidad, y facilidad de integración que lo hace atractivo para el desarrollo de generadores de parser y lexer, especialmente en el contexto de lenguajes de dominio restringido. Además, su capacidad para trabajar con DSLs y la disponibilidad de recursos y herramientas en la comunidad hacen que sea una opción sólida para este tipo de proyectos.

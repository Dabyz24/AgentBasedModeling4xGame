## TO DO ✔ ❌

[✔] 1. Crear un arbol de tecnologias para que puedan invertir en ello (2 o 3 que mejoren algun aspecto)

[✔] 2. Hacer que los agentes tengan distinto color y para poder identificarlo poner un cuadro de color en el HTML.
- Si quiero revertirlo solo tengo que cambiar en server la parte de color del html y en model y agente la lista de colores y los getters y setters

[✔] 3. Hacer que las peleas resten recursos a algunos y los sumen al ganador

[✔] 4. Modificar los agentes para poder introducir comportamientos en cada uno de los agentes 
- [✔] 4.1 Deshacer estatico añadiendo la opcion de aparecer random de los agentes y de los planetas
- [✔] 4.2 Quitar todas las variables creadas únicamente para el Q-learning y limpiar todas las variables innutilizadas 
- [✔] 4.3 Crear las condiciones para que cada agente no decida aleatorio y lo haga basandose en una lógica 

[✔] 5. Ver como poder introducir codigo de manera dinamica para poder crear nuevas funcionalidades (alianzas)
- [✔] 5.1 Introducir una nueva funcionalidad en el step 50 para cambiar el funcionamiento del agente (sin método)

[✔] 6 Introducción y eliminación de manera dinámica de agentes 
- [✔] 6.1 Añadir de manera dinámica agentes a la ejecución
- [✔] 6.2 Posibilidad de perder planetas si se da cierta condición (Si pierden un combate y tienen un planeta se resetea un planeta aleatorio de su propiedad)
- [✔] 6.3 Eliminar agentes que bajen de un umbral ciertos puntos (si no consigue cierta media de puntos en un número de turnos lo elimino)

[✔] 7. Probar cual es el factor limitante en la simulación (Porque solo aparecen 4 agentes en 50000 ejecuciones)
- [✔] 7.1 Hacer que las fabricas no den puntos estelares
- [✔] 7.2 Hacer que los planetas den puntos estelares en funcion del numero de planetas que tengas
- [✔] 7.3. Guardar la semilla de una ejecución para poder estudiarla en un txt 

[✔] 8. Cambiar los comportamientos a algo más genérico (Objeto) para no tener que ponerlo tan estricto en el condicional 
- [✔] 8.1 Cambiar la lógica de los comportamientos para no hacerlo en el step tan estricto, con polimorfismos y tecnicas mas avanzadas de POO
- [✔] 8.2 Añadir una lista de prioridades para los comportamientos (meter las upgrades ahí)

[✔] 9. Que el agente sea capaz de interactuar con su entorno
- [✔] 9.1 Que el agente sepa quien es el ganador y los recursos de cada agente
- [✔] 9.2 Que el agente pueda cambiar su lista de prioridades si se dan ciertas condiciones 
- [✔] 9.3 El comportamiento del agente tiene que depender del entorno del agente para poder cambiar sus listas de prioridades
  - [✔] 9.3.1 Establecer las listas de prioridades para cada tipo de situaciones que se pueden dar en la simulación, haciendo métodos polimorficos
  - [✔] 9.3.2 Dependiendo de los elementos que tenga en su radio de movimiento, elegir una de las listas de prioridades o la otra

[ ] 10. Crear una manera para poder introducir de manera dinamica en ejecucion un agente cuando yo quiera (Boton o alguna manera de hacerlo) 

[] 11. Introducir alguna mecanica dinamicamente como si se le hubiese ocurrido al agente (como donar algunos recursos o poder comprar a agentes para que le protejan)
- [] 11.1 Crear diferentes tipos de agentes con un comportamiento y unas mutaciones especificas
- [] 11.2 Modificar el changeBehaviour de esos agentes "mutados" para que se comporten como yo quiera teniendo en cuenta su entorno

[] 12. Estructurar la memoria de TFG
- [] 12.1 Estudiar y comentar los resultados de los experimentos con agentes mutados para poder comprobar como sería el comportamiento si se introdujese un algoritmo genetico que modificara la estructura de los agentes 

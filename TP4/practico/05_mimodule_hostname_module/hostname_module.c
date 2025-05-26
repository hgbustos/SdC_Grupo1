#include <linux/module.h>   /* Requerido por todos los módulos */
#include <linux/kernel.h>   /* Definición de KERN_INFO */
#include <linux/utsname.h>  /* Para init_utsname() */

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Modulo que imprime el hostname - TP4 SdeC"); 
MODULE_AUTHOR("Grupo1"); 

/* Función que se invoca cuando se carga el módulo en el kernel */
static int hostname_module_init(void) // Nombre de función opcionalmente cambiado
{
    printk(KERN_INFO "Hola desde el modulo del Grupo1! El hostname es: %s\n", init_utsname()->nodename); // CAMBIA "Javi"
    printk(KERN_INFO "Modulo personalizado hostname_module cargado en el kernel.\n");
    return 0;
}

/* Función que se invoca cuando se descarga el módulo del kernel */
static void hostname_module_exit(void) // Nombre de función opcionalmente cambiado
{
    printk(KERN_INFO "Modulo personalizado hostname_module descargado del kernel.\n");
}

/* Declaración de funciones init y exit */
module_init(hostname_module_init);
module_exit(hostname_module_exit);
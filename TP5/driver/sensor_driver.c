#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/uaccess.h>
#include <linux/slab.h>

#define DEVICE_NAME "sensor_cdd" 
#define CLASS_NAME  "sdecc_sensor"  
#define SERIAL_PORT_DEVICE "/dev/ttyUSB0" 

// =================== Variables Globales ===================
static dev_t dev_num;            
static struct class *sdecc_class = NULL; 
static struct cdev sensor_cdev;  
// El struct file del puerto serie, gestionado en init/exit.
static struct file *serial_port_filp = NULL; 

// =================== Declaraciones de Funciones ===================
static int     my_open(struct inode *inode, struct file *file);
static int     my_release(struct inode *inode, struct file *file);
static ssize_t my_write(struct file *filp_cdd, const char __user *user_buf, size_t user_len, loff_t *off);

static char *sensor_devnode(const struct device *dev, umode_t *mode) {
    if (mode) *mode = 0666; 
    return NULL; 
}

static struct file_operations fops = {
    .owner   = THIS_MODULE,
    .open    = my_open,
    .release = my_release,
    .write   = my_write,
};

// =================== Implementaciones de fops ===================
static int my_open(struct inode *inode, struct file *file_cdd) {
    printk(KERN_INFO "SensorDriver: Dispositivo /dev/%s abierto (v0.5.3).\n", DEVICE_NAME);
    return 0; 
}

static int my_release(struct inode *inode, struct file *file_cdd) {
    printk(KERN_INFO "SensorDriver: Dispositivo /dev/%s cerrado.\n", DEVICE_NAME);
    return 0; 
}

static ssize_t my_write(struct file *filp_cdd, const char __user *user_buf, size_t user_len, loff_t *off) {
    char *kernel_buf;
    ssize_t written_count;
    loff_t offset = 0;

    if (unlikely(!serial_port_filp)) {
        printk(KERN_ALERT "SensorDriver: my_write: el filp del puerto serie es NULO.\n");
        return -EIO;
    }
    // Límite de tamaño por seguridad
    if (user_len == 0 || user_len > 64) {
        return -EINVAL; // Invalid argument
    }

    // +1 para el terminador '\n'
    kernel_buf = kmalloc(user_len + 1, GFP_KERNEL);
    if (!kernel_buf) return -ENOMEM;

    if (copy_from_user(kernel_buf, user_buf, user_len)) {
        kfree(kernel_buf);
        return -EFAULT;
    }
    kernel_buf[user_len] = '\n';
    
    // Usamos kernel_write para escribir en el archivo del puerto serie
    written_count = kernel_write(serial_port_filp, kernel_buf, user_len + 1, &offset);
    
    kfree(kernel_buf);

    if (written_count < 0) {
        printk(KERN_ALERT "SensorDriver: Error en kernel_write: %zd\n", written_count);
        return written_count; // Devolver el código de error si lo hubo
    }

    // Aqui se devuelve la cantidad de bytes que el usuario pidió escribir.
    // Esto evita el error "invalid length" en la aplicación.
    return user_len;
}

// =================== Init y Exit  =====================
static int __init sensor_driver_init(void) {
    int result;
    printk(KERN_INFO "SensorDriver: Cargando módulo (Version 0.5.3).\n");

    // Abrir el puerto serie y mantenerlo abierto
    printk(KERN_INFO "SensorDriver: Abriendo %s para uso exclusivo del driver...\n", SERIAL_PORT_DEVICE);
    serial_port_filp = filp_open(SERIAL_PORT_DEVICE, O_RDWR | O_NOCTTY, 0); 
    if (IS_ERR(serial_port_filp)) {
        result = PTR_ERR(serial_port_filp);
        printk(KERN_ALERT "SensorDriver: No se pudo abrir %s. ¿ESP32 conectado? Error %d\n", SERIAL_PORT_DEVICE, result);
        return result;
    }
    
    // Crear el dispositivo de caracteres
    result = alloc_chrdev_region(&dev_num, 0, 1, DEVICE_NAME);
    if (result < 0) goto fail_filp_close;
    
    sdecc_class = class_create(CLASS_NAME); 
    if (IS_ERR(sdecc_class)) { result = PTR_ERR(sdecc_class); goto fail_unregister_chrdev; }
    sdecc_class->devnode = sensor_devnode;
    
    cdev_init(&sensor_cdev, &fops);
    sensor_cdev.owner = THIS_MODULE;
    result = cdev_add(&sensor_cdev, dev_num, 1);
    if (result < 0) goto fail_class_destroy;
    
    if (IS_ERR(device_create(sdecc_class, NULL, dev_num, NULL, DEVICE_NAME))) { result = -1; goto fail_cdev_del; }

    printk(KERN_INFO "SensorDriver: Inicialización completada. /dev/%s listo.\n", DEVICE_NAME);
    return 0;

// Rutinas de limpieza en caso de fallo
fail_cdev_del:          cdev_del(&sensor_cdev);
fail_class_destroy:     class_destroy(sdecc_class);
fail_unregister_chrdev: unregister_chrdev_region(dev_num, 1);
fail_filp_close:        filp_close(serial_port_filp, NULL);
    printk(KERN_ALERT "SensorDriver: Carga de módulo fallida, limpiando...\n");
    return result;
}

static void __exit sensor_driver_exit(void) {
    printk(KERN_INFO "SensorDriver: Descargando módulo...\n");
    device_destroy(sdecc_class, dev_num);
    cdev_del(&sensor_cdev);
    class_destroy(sdecc_class);
    unregister_chrdev_region(dev_num, 1);
    
    if (serial_port_filp) {
        filp_close(serial_port_filp, NULL);
        printk(KERN_INFO "SensorDriver: Puerto serie liberado.\n");
    }
    printk(KERN_INFO "SensorDriver: Limpieza completada.\n");
}

module_init(sensor_driver_init);
module_exit(sensor_driver_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Grupo1");
MODULE_DESCRIPTION("Driver de control para ESP32 (v0.5.3)");
MODULE_VERSION("0.5.3"); // Costó pero se pudo jaja
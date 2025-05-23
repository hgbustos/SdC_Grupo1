# !bin/bash

echo "  -> Creando objetos..."
as -g -o pmode.o pmode.S

echo "  -> Enlazando..."
ld --oformat binary -o pmode.img -T link.ld pmode.o

echo "  -> Iniciando QEMU en modo de depuración..."
gnome-terminal -- qemu-system-i386 -fda pmode.img -boot a -s -S -monitor stdio

# Open a new terminal window and execute GDB
#echo "  -> Launching GDB linked with QEMU..."
#gnome-terminal -- gdb -x gdb.gdb

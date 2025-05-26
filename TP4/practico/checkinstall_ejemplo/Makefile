CC=gcc
CFLAGS=-Wall
TARGET=hello_checkinstall
PREFIX?=/usr/local

all: $(TARGET)

$(TARGET): hello_checkinstall.c
	$(CC) $(CFLAGS) -o $(TARGET) hello_checkinstall.c

install: $(TARGET)
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	cp $(TARGET) $(DESTDIR)$(PREFIX)/bin/

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/$(TARGET)

clean:
	rm -f $(TARGET)
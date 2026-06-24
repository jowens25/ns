#!/usr/bin/make -f

CC      = gcc
CFLAGS  = -Wall -g
CPPFLAGS=
LDFLAGS = -Wl,-rpath,/usr/local/lib
LDLIBS  = -L/usr/local/lib -lft4222

SOURCES = $(wildcard *.c)
OBJECTS = $(SOURCES:.c=.o)
TARGET  = ns-programmer

PREFIX ?= /usr
DESTDIR ?=

.PHONY: all clean install static

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^ $(LDLIBS)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

static: LDFLAGS =
static: LDLIBS = -L/usr/local/lib -lft4222 -ldl -lpthread -lrt -lstdc++
static: CFLAGS += -static
static: clean $(TARGET)

install: $(TARGET)
	install -D -m 755 $(TARGET) $(DESTDIR)$(PREFIX)/bin/$(TARGET)

clean:
	rm -f $(TARGET) $(OBJECTS)
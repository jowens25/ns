package lib

import (
	"embed"
	"io/fs"
	"strings"
)

//go:embed configs/*
var configFiles embed.FS

func GetEmbeddedConfigLines(filename string) ([]string, error) {
	// Option A: Use fs.Sub + ReadFile
	configFS, err := fs.Sub(configFiles, "configs")
	if err != nil {
		return nil, err
	}

	content, err := fs.ReadFile(configFS, "snmpd.conf") // no "configs/" prefix needed after Sub
	if err != nil {
		return nil, err
	}
	return strings.Split(string(content), "\n"), nil
}

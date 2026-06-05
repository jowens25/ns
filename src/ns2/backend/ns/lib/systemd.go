package lib

import (
	"context"
	"fmt"

	"github.com/coreos/go-systemd/v22/dbus"

	"github.com/rs/zerolog/log"
)

func _stopUnit(unit string) error {
	conn, err := dbus.NewSystemConnectionContext(context.Background())
	if err != nil {
		return fmt.Errorf("dbus connect: %w", err)
	}
	defer conn.Close()

	resultCh := make(chan string, 1)
	_, err = conn.StopUnitContext(context.Background(), unit, "replace", resultCh)
	if err != nil {
		return fmt.Errorf("stop %s: %w", unit, err)
	}

	result := <-resultCh // blocks until systemd confirms the unit is stopped
	if result != "done" {
		return fmt.Errorf("stop %s result: %s", unit, result)
	}

	log.Printf("stopped %s successfully\n", unit)
	return nil
}

func _startUnit(unit string) error {
	conn, err := dbus.NewSystemConnectionContext(context.Background())
	if err != nil {
		return fmt.Errorf("dbus connect: %w", err)
	}
	defer conn.Close()

	resultCh := make(chan string, 1)
	_, err = conn.StartUnitContext(context.Background(), unit, "replace", resultCh)
	if err != nil {
		return fmt.Errorf("start %s: %w", unit, err)
	}

	result := <-resultCh // blocks until systemd confirms the unit is stopped
	if result != "done" {
		return fmt.Errorf("start %s result: %s", unit, result)
	}

	log.Debug().Msgf("started %s successfully", unit)
	return nil
}

func _restartUnit(unit string) error {

	log.Info().Msgf("_restartUnit: %s", unit)

	conn, err := dbus.NewSystemConnectionContext(context.Background())
	if err != nil {
		panic(err)
	}
	defer conn.Close()

	_, err = conn.RestartUnitContext(context.Background(), unit, "replace", nil)

	if err != nil {
		return err
	}

	return nil
}

func _getUnitStatus(unit string) (string, error) {

	units := []string{unit}
	conn, err := dbus.NewSystemConnectionContext(context.Background())
	if err != nil {
		panic(err)
	}
	defer conn.Close()

	status, err := conn.ListUnitsByNamesContext(context.Background(), units)

	if err != nil {
		return "none", err
	}

	return status[0].ActiveState, nil
}

///////////////////////////////
/// CLI END POINTS

func Start(u string) string {
	err := _startUnit(u)
	if err != nil {
		return err.Error()
	}
	return fmt.Sprintf("started: %s", u)
}

func Stop(u string) {
	_stopUnit(u)

}

func Restart(u string) {
	_restartUnit(u)
}

func GetUnitStatus(u string) string {

	status, err := _getUnitStatus(u)
	if err != nil {
		return err.Error()
	}
	return fmt.Sprintf("%s: %s", u, status)
}

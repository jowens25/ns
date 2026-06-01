package lib

import (
	"fmt"
	"log"
	"unicode"

	"github.com/spf13/viper"
)

type Policy struct {
	MinLength        int
	MaxLength        int
	RequireUppercase bool
	RequireLowercase bool
	RequireDigit     bool
	RequireSymbol    bool
}

func SetupNsConfig() {

	viper.SetDefault("max", 16)
	viper.SetDefault("min", 8)
	viper.SetDefault("upper", false)
	viper.SetDefault("lower", false)
	viper.SetDefault("digit", false)
	viper.SetDefault("symbol", false)
	viper.SetDefault("path", "/etc/ns/ns.yaml")

	viper.AddConfigPath("/etc/ns/")
	viper.SetConfigName("ns")
	viper.SetConfigType("yaml")

	if err := viper.ReadInConfig(); err != nil {
		if _, ok := err.(viper.ConfigFileNotFoundError); ok {
			if err := viper.SafeWriteConfig(); err != nil {
				log.Fatalf("Error creating config file: %s", err)
			}
		} else {
			log.Fatalf("Error reading config file: %s", err)
		}
	}

}

func SetPolicy(policy map[string]any) error {

	viper.Set("max", policy["max"])
	viper.Set("min", policy["min"])
	viper.Set("upper", policy["upper"])
	viper.Set("lower", policy["lower"])
	viper.Set("digit", policy["digit"])
	viper.Set("symbol", policy["symbol"])

	return viper.WriteConfig()

}

func GetPolicy() (Policy, error) {

	var policy Policy

	policy.MaxLength = viper.GetInt("max")
	policy.MinLength = viper.GetInt("min")
	policy.RequireUppercase = viper.GetBool("upper")
	policy.RequireLowercase = viper.GetBool("lower")
	policy.RequireDigit = viper.GetBool("digit")
	policy.RequireSymbol = viper.GetBool("symbol")

	return policy, nil

}

func Validate(password string) (bool, error) {
	// returns isValid or reason for invalid

	policy, _ := GetPolicy()

	if len(password) > policy.MaxLength {
		return false, fmt.Errorf("password is greater than max length")
	}

	if len(password) < policy.MinLength {
		return false, fmt.Errorf("password is less than min length")
	}

	var hasUpper bool
	var hasLower bool
	var hasDigit bool
	var hasSymbol bool
	var hasSpace bool

	for _, c := range password {
		if unicode.IsUpper(c) {
			hasUpper = true
		}

		if unicode.IsLower(c) {
			hasLower = true
		}
		if unicode.IsDigit(c) {
			hasDigit = true
		}
		if unicode.IsPunct(c) || unicode.IsSymbol(c) {
			hasSymbol = true
		}
		if unicode.IsSpace(c) {
			hasSpace = true
		}
	}

	if policy.RequireUppercase && !hasUpper {
		return false, fmt.Errorf("password must have an uppercase letter")
	}

	if policy.RequireLowercase && !hasLower {
		return false, fmt.Errorf("password must have a lowercase letter")
	}

	if policy.RequireDigit && !hasDigit {
		return false, fmt.Errorf("password must have a digit")
	}

	if policy.RequireSymbol && !hasSymbol {
		return false, fmt.Errorf("password must have a symbol")
	}

	if hasSpace {
		return false, fmt.Errorf("password must not have a space or tab type characters")
	}

	return true, nil

}

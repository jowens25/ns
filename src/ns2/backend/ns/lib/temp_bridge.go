package lib

// import (
// 	"fmt"
// 	"reflect"
// 	"strings"

// 	"github.com/godbus/dbus/v5"
// )

// // Enhanced message format to include type hints
// //type DbusCall struct {
// //	Destination string          `json:"destination" binding:"required"`
// //	Path        dbus.ObjectPath `json:"path" binding:"required"`
// //	Method      string          `json:"method" binding:"required"`
// //	Args        []any           `json:"args"`
// //	Signature   string          `json:"signature" binding:"required"`
// //}

// // Convert JSON arguments to D-Bus arguments using signature
// func ToDbus(args []any, signature string) ([]any, error) {
// 	if signature == "" {
// 		return []any{}, nil
// 	}

// 	sig, err := dbus.ParseSignature(signature)
// 	if err != nil {
// 		return nil, fmt.Errorf("invalid signature: %w", err)
// 	}

// 	if len(args) != len(sig) {
// 		return nil, fmt.Errorf("argument count mismatch: got %d, signature expects %d", len(args), len(sig))
// 	}

// 	result := make([]any, len(args))

// 	for i, arg := range args {
// 		converted, err := convertJsonToDbusType(arg, sig[i])
// 		if err != nil {
// 			return nil, fmt.Errorf("arg %d: %w", i, err)
// 		}
// 		result[i] = converted
// 	}

// 	return result, nil
// }

// // Convert single JSON value to D-Bus type based on signature
// func convertJsonToDbusType(value any, sig dbus.Signature) (any, error) {
// 	sigStr := sig.String()

// 	switch sigStr {
// 	case "b": // boolean
// 		if b, ok := value.(bool); ok {
// 			return b, nil
// 		}
// 		return false, fmt.Errorf("expected bool, got %T", value)

// 	case "y": // byte (uint8)
// 		return toNumber[byte](value)

// 	case "n": // int16
// 		return toNumber[int16](value)

// 	case "q": // uint16
// 		return toNumber[uint16](value)

// 	case "i": // int32
// 		return toNumber[int32](value)

// 	case "u": // uint32
// 		return toNumber[uint32](value)

// 	case "x": // int64
// 		return toNumber[int64](value)

// 	case "t": // uint64
// 		return toNumber[uint64](value)

// 	case "d": // double
// 		return toNumber[float64](value)

// 	case "s": // string
// 		if s, ok := value.(string); ok {
// 			return s, nil
// 		}
// 		return "", fmt.Errorf("expected string, got %T", value)

// 	case "o": // object path
// 		if s, ok := value.(string); ok {
// 			return dbus.ObjectPath(s), nil
// 		}
// 		return dbus.ObjectPath(""), fmt.Errorf("expected string for object path, got %T", value)

// 	case "g": // signature
// 		if s, ok := value.(string); ok {
// 			return dbus.Signature{Str: s}, nil
// 		}
// 		return dbus.Signature{}, fmt.Errorf("expected string for signature, got %T", value)

// 	case "v": // variant
// 		return dbus.MakeVariant(value), nil

// 	default:
// 		// Handle complex types
// 		if strings.HasPrefix(sigStr, "a") {
// 			return convertArray(value, sigStr)
// 		} else if strings.HasPrefix(sigStr, "(") {
// 			return convertStruct(value, sigStr)
// 		} else if strings.HasPrefix(sigStr, "a{") {
// 			return convertDict(value, sigStr)
// 		}

// 		return nil, fmt.Errorf("unsupported D-Bus type: %s", sigStr)
// 	}
// }

// // Helper to convert JSON numbers to specific Go numeric types
// func toNumber[T int16 | uint16 | int32 | uint32 | int64 | uint64 | byte | float64](value any) (T, error) {
// 	switch v := value.(type) {
// 	case float64:
// 		return T(v), nil
// 	case int:
// 		return T(v), nil
// 	case int64:
// 		return T(v), nil
// 	default:
// 		var zero T
// 		return zero, fmt.Errorf("expected number, got %T", value)
// 	}
// }

// // Convert JSON array to D-Bus array
// func convertArray(value any, signature string) (any, error) {
// 	arr, ok := value.([]any)
// 	if !ok {
// 		return nil, fmt.Errorf("expected array, got %T", value)
// 	}

// 	// Parse element signature (remove 'a' prefix)
// 	elemSig, err := dbus.ParseSignature(signature[1:])
// 	if err != nil {
// 		return nil, err
// 	}

// 	// Special case for byte arrays (can be base64 encoded strings)
// 	if signature == "ay" {
// 		if str, ok := value.(string); ok {
// 			// Could be base64 encoded
// 			return []byte(str), nil
// 		}
// 	}

// 	result := make([]any, len(arr))
// 	for i, elem := range arr {
// 		converted, err := convertJsonToDbusType(elem, elemSig[0])
// 		if err != nil {
// 			return nil, fmt.Errorf("array element %d: %w", i, err)
// 		}
// 		result[i] = converted
// 	}

// 	return result, nil
// }

// // Convert JSON object to D-Bus struct
// func convertStruct(value any, signature string) (any, error) {
// 	arr, ok := value.([]any)
// 	if !ok {
// 		return nil, fmt.Errorf("expected array for struct, got %T", value)
// 	}

// 	// Parse struct signature
// 	// Remove '(' and ')' and parse inner types
// 	inner := signature[1 : len(signature)-1]
// 	sig, err := dbus.ParseSignature(inner)
// 	if err != nil {
// 		return nil, err
// 	}

// 	if len(arr) != len(sig) {
// 		return nil, fmt.Errorf("struct field count mismatch")
// 	}

// 	result := make([]any, len(arr))
// 	for i, elem := range arr {
// 		converted, err := convertJsonToDbusType(elem, sig[i])
// 		if err != nil {
// 			return nil, fmt.Errorf("struct field %d: %w", i, err)
// 		}
// 		result[i] = converted
// 	}

// 	return result, nil
// }

// // Convert JSON object to D-Bus dictionary
// func convertDict(value any, signature string) (any, error) {
// 	obj, ok := value.(map[string]any)
// 	if !ok {
// 		return nil, fmt.Errorf("expected object for dict, got %T", value)
// 	}

// 	// Parse dict signature a{keyType valueType}
// 	// Extract key and value signatures
// 	inner := signature[2 : len(signature)-1] // Remove "a{" and "}"

// 	// Simple parser for key-value types
// 	keySigStr := string(inner[0])
// 	valueSigStr := inner[1:]

// 	keySig, _ := dbus.ParseSignature(keySigStr)
// 	valueSig, _ := dbus.ParseSignature(valueSigStr)

// 	result := make(map[any]any)

// 	for k, v := range obj {
// 		convertedKey, err := convertJsonToDbusType(k, keySig[0])
// 		if err != nil {
// 			return nil, fmt.Errorf("dict key %s: %w", k, err)
// 		}

// 		convertedValue, err := convertJsonToDbusType(v, valueSig[0])
// 		if err != nil {
// 			return nil, fmt.Errorf("dict value for key %s: %w", k, err)
// 		}

// 		result[convertedKey] = convertedValue
// 	}

// 	return result, nil
// }

// // Convert D-Bus response to JSON-safe format
// func ToJson(dbusValue any) (any, error) {
// 	switch v := dbusValue.(type) {
// 	case dbus.Variant:
// 		return ToJson(v.Value())

// 	case []any:
// 		result := make([]any, len(v))
// 		for i, elem := range v {
// 			converted, err := ToJson(elem)
// 			if err != nil {
// 				return nil, err
// 			}
// 			result[i] = converted
// 		}
// 		return result, nil

// 	case map[any]any:
// 		result := make(map[string]any)
// 		for k, val := range v {
// 			keyStr := fmt.Sprintf("%v", k)
// 			converted, err := ToJson(val)
// 			if err != nil {
// 				return nil, err
// 			}
// 			result[keyStr] = converted
// 		}
// 		return result, nil

// 	case dbus.ObjectPath:
// 		return string(v), nil

// 	case dbus.Signature:
// 		return v.String(), nil

// 	// All basic types are JSON-safe
// 	case bool, string, byte,
// 		int16, uint16, int32, uint32, int64, uint64,
// 		float64:
// 		return v, nil

// 	default:
// 		// Use reflection for complex types
// 		rv := reflect.ValueOf(v)
// 		switch rv.Kind() {
// 		case reflect.Slice, reflect.Array:
// 			result := make([]any, rv.Len())
// 			for i := 0; i < rv.Len(); i++ {
// 				converted, err := ToJson(rv.Index(i).Interface())
// 				if err != nil {
// 					return nil, err
// 				}
// 				result[i] = converted
// 			}
// 			return result, nil

// 		case reflect.Map:
// 			result := make(map[string]any)
// 			iter := rv.MapRange()
// 			for iter.Next() {
// 				keyStr := fmt.Sprintf("%v", iter.Key().Interface())
// 				converted, err := ToJson(iter.Value().Interface())
// 				if err != nil {
// 					return nil, err
// 				}
// 				result[keyStr] = converted
// 			}
// 			return result, nil

// 		case reflect.Struct:
// 			// Convert struct to array
// 			result := make([]any, rv.NumField())
// 			for i := 0; i < rv.NumField(); i++ {
// 				converted, err := ToJson(rv.Field(i).Interface())
// 				if err != nil {
// 					return nil, err
// 				}
// 				result[i] = converted
// 			}
// 			return result, nil

// 		default:
// 			return v, nil
// 		}
// 	}
// }

// // Updated MakeDbusCall with proper type conversion
// func SafeMakeDbusCall(conn *dbus.Conn, call DbusCall) (any, error) {
// 	// Convert JSON args to D-Bus args
// 	dbusArgs, err := ToDbus(call.Args, call.Signature)
// 	if err != nil {
// 		return nil, fmt.Errorf("argument conversion failed: %w", err)
// 	}

// 	obj := conn.Object(call.Destination, call.Path)
// 	dbusCall := obj.Call(call.Method, 0, dbusArgs...)

// 	if dbusCall.Err != nil {
// 		return nil, dbusCall.Err
// 	}

// 	// Convert response to JSON-safe format
// 	if len(dbusCall.Body) == 0 {
// 		return nil, nil
// 	}

// 	if len(dbusCall.Body) == 1 {
// 		return ToJson(dbusCall.Body[0])
// 	}

// 	// Multiple return values
// 	result := make([]any, len(dbusCall.Body))
// 	for i, v := range dbusCall.Body {
// 		converted, err := ToJson(v)
// 		if err != nil {
// 			return nil, err
// 		}
// 		result[i] = converted
// 	}

// 	return result, nil
// }

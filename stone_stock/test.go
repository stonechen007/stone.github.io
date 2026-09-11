package main

import (
    "crypto/hmac"
    "crypto/sha256"
    "encoding/hex"
    "fmt"
)

func GenerateSignature(secret, payload string) (string, error) {
    h := hmac.New(sha256.New, []byte(secret))
    if _, err := h.Write([]byte(payload)); err != nil {
       return "", err
    }
    return hex.EncodeToString(h.Sum(nil)), nil
}

func main() {
	// generate signature using secret
	secret := "DERiTuMcf5MG_x4oXybNM1-8WpGOdI3H4z6laoqEb9M=" // secret key
	payload := "1312073376210944"                             // promotion id
	// 生成签名: 505ab29a32ad84746a3f68f531518a22fbe198db80a72a2837dea92e2ea7685b
	h := hmac.New(sha256.New, []byte(secret))
	if _, err := h.Write([]byte(payload)); err != nil {
		fmt.Println("error:", err)
		return
	}
	sig := hex.EncodeToString(h.Sum(nil))
	fmt.Println(sig)
}
package main

import (
    "crypto/hmac"
    "crypto/sha1"
    "encoding/base64"
    "flag"
    "fmt"
)

const ACCESS_KEY_SECRET = "必填"

var Input_pstrPolicy = flag.String("policy", "", "input policy")

func ComputeHmac(message string, secret string) string {
    key := []byte(secret)
    h := hmac.New(sha1.New, key)
    h.Write([]byte(message))
    return base64.StdEncoding.EncodeToString(h.Sum(nil))
}

func main() {
    flag.Parse()
    fmt.Print(ComputeHmac(*Input_pstrPolicy, ACCESS_KEY_SECRET))
}

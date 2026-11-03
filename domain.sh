#!/usr/bin/env bash

COMMON_TLDS=(com net org io co ai app dev xyz site online)

if [[ "$1" != "-u" || -z "$2" ]]; then
    echo "Usage: $0 -u <username> [--domains]"
    exit 1
fi

USERNAME="$2"

if [[ "$3" == "--domains" ]]; then
    echo "[*] Domain reconnaissance for: $USERNAME"
    echo

    for tld in "${COMMON_TLDS[@]}"; do
        domain="${USERNAME}.${tld}"

        if whois "$domain" 2>/dev/null | grep -qi "No match"; then
            status="AVAILABLE"
        else
            status="REGISTERED"
        fi

        printf "%-25s %s\n" "$domain" "$status"
    done

    exit 0
fi

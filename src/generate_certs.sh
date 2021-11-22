#!/bin/bash
# https://github.com/EONRaider/BCA-Phantom

# Author: EONRaider @ keybase.io/eonraider

gr='\033[0;32m' # Green
or='\033[0;33m' # Orange
nc='\033[0m'    # No style

KEY_LEN="4096"  # Key-length to be used
VALIDITY="90"   # Validity time for the certificate in days

CA_KEY_FILE="ca-key.pem"          # Certificate Authority (CA) key file
CA_CERT_FILE="ca-cert.pem"        # CA certificate file in PEM format
SUBJ_KEY_FILE="server-key.pem"    # Subject (our server) key file
SUBJ_CSR_FILE="server-csr.pem"    # Subject Certificate Signing Request (CSR)
SUBJ_CERT_FILE="server-cert.pem"  # Subject certificate file in PEM format

echo -e "\n${or}
[>>>] This script is part of the HTTPS Reverse Shell application. Check it
out at https://github.com/EONRaider/BCA-HTTPS-Reverse-Shell
${nc}"

echo -e "${gr}
[+] Step (1/2): Create our own Certificate Authority (CA). It will be used as an
entity that signs all our certificates, acting as a trusted party that our
clients and servers will rely on when authenticating connections. Fill in the
data for the creation of your own CA:
\n${nc}"

# 1. Generate a private RSA key for the Certificate Authority (CA):
openssl genrsa -out "${CA_KEY_FILE}" "${KEY_LEN}"
echo -e "${or}\n   [>] File created: \"${CA_KEY_FILE}\"${nc}\n"

# 2. Create the certificate for the Certificate Authority (CA):
echo -e "${gr}   [+] Fill in the data for the creation of your own CA. A file
named \"${CA_CERT_FILE}\" will be generated.\n${nc}"
openssl req -x509 -new -nodes -sha512 \
  -days "${VALIDITY}" \
  -key "${CA_KEY_FILE}" \
  -out "${CA_CERT_FILE}"

echo -e "\n${or}   [>] File created: \"${CA_CERT_FILE}\"${nc}\n"

echo -e "${gr}
[+] Step (2/2): Create our server's private key and use it to sign its Certificate
Signing Request (CSR). This CSR will be signed by our CA and, finally, the server
certificate will be issued.
${nc}\n"

# 3. Generate a private RSA key and a Certificate Signing Request (CSR) for the
# server (a.k.a. Subject):
echo -e "${gr}   [+] Fill in the data for the creation of the X509 certificate for
your own server. It will be signed by the CA and a file named \"${SUBJ_CERT_FILE}\"
will be generated.\n${nc}"
openssl req -nodes \
  -newkey rsa:"${KEY_LEN}" \
  -days "${VALIDITY}" \
  -keyout "${SUBJ_KEY_FILE}" \
  -out "${SUBJ_CSR_FILE}"
echo -e "${or}   [>] File created: \"${SUBJ_KEY_FILE}\"${nc}"
echo -e "${or}   [>] File created: \"${SUBJ_CSR_FILE}\"${nc}\n"

# 4. Sign the server CSR with the CA certificate and private key:
openssl x509 -req \
   -set_serial 01 \
   -days "${VALIDITY}" \
   -in "${SUBJ_CSR_FILE}" \
   -out "${SUBJ_CERT_FILE}" \
   -CA "${CA_CERT_FILE}" \
   -CAkey "${CA_KEY_FILE}"

# 5. Verify the server certificate:
openssl verify -CAfile "${CA_CERT_FILE}" "${SUBJ_CERT_FILE}"

#==PROCESS COMPLETED============================================================

echo -e "${gr}"
read -rp "[!] From now on the only files you will need are \"${SUBJ_CERT_FILE}\",
\"${CA_KEY_FILE}\" and \"${CA_CERT_FILE}\". You can safely delete all the other
files that have been generated right now or keep them for further analysis. Would
you like to delete these extra files? (Y/N) " DELYN
echo -e "${nc}"

case ${DELYN} in
  [Yy]* ) rm  "${SUBJ_KEY_FILE}" "${SUBJ_CSR_FILE}"
          echo -e "${or}   [!] SUCCESS: Extra files were deleted.\n${nc}";;
  [Nn]* ) echo -e "${or}   [!] SUCCESS: Extra files will be kept.\n${nc}";;
esac

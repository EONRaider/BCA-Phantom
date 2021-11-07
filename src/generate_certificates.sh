#!/bin/bash
# https://github.com/EONRaider/BCA-Basic-HTTPS-Reverse-Shell

# Author = 'EONRaider @ keybase.io/eonraider'

gr='\033[0;32m' # Green
or='\033[0;33m' # Orange
nc='\033[0m'    # No style

KEY_LEN="4096"  # Key-length to be used
VALID="90"      # Validity time for the certificate in days

# Names of the files that will be generated
CA_KEY_FILE="ca.key"                  # Certificate Authority key file
CA_CERT_FILE="ca.crt"                 # Certificate Authority certificate file
SUBJ_KEY_FILE="server.key"            # Subject (our server) key file
SUBJ_CSR_FILE="server.csr"            # Subject Certificate Signing Request file
SUBJ_CRT_FILE="server.crt"            # Subject Certificate File
SUBJ_CRT_READ_FILE="server-txt.crt"   # Subject Certificate File (human-readable)
SUBJ_PEM_FILE="server.pem"            # Subject PEM file

echo -e "\n${or}
[>>>] This script is part of the Basic HTTPS Reverse Shell application by BlackCode
Academy. Check it out at https://github.com/EONRaider/BCA-Basic-HTTPS-Reverse-Shell
${nc}"

#==ACTIONS TAKEN BY THE CERTIFICATE AUTHORITY==============================================
echo -e "\n${gr}
[+] Step (1/4): Create our own Certificate Authority (CA). It will be used as an
entity that signs all our certificates, acting as a trusted party that our
clients and servers will rely on when authenticating connections. Fill in the
data for the creation of your own CA:
${nc}\n"

# 1. Generate a private RSA key for the Certificate Authority (CA):
openssl genrsa -out "${CA_KEY_FILE}" "${KEY_LEN}"
echo -e "${or}\n   [>] File created: \"${CA_KEY_FILE}\"${nc}"
echo -e "${gr}   [+] Fill in the data for the creation of your own CA. A file
named \"${CA_CERT_FILE}\" will be generated.\n${nc}"

# 2. Create the certificate for the Certificate Authority (CA):
openssl req -x509 -new -nodes -key "${CA_KEY_FILE}" -sha512 -days "${VALID}" \
-out "${CA_CERT_FILE}"
echo -e "${or}\n   [>] File created: \"${CA_CERT_FILE}\"\n${nc}"

#==ACTIONS TAKEN BY THE SERVER ADMINISTRATOR===============================================
echo -e "\n${gr}
[+] Step (2/4): Create our server's private key and use it to sign its Certificate
Signing Request. This document would be remotely sent to a real CA if this
application were to be deployed in a production environment and trusted publicly.
${nc}\n"

# 3. Generate a private RSA key for the server (a.k.a. Subject):
openssl genrsa -out "${SUBJ_KEY_FILE}" "${KEY_LEN}"
echo -e "${or}\n   [>] File created: \"${SUBJ_KEY_FILE}\"${nc}"
echo -e "${gr}   [+] Fill in the data for the creation of the certificate for
your own server. A file named \"${SUBJ_CSR_FILE}\" will be generated.\n${nc}"

# 4. Create a Certificate Signing Request (CSR) for the server. This request is
# sent to the Certificate Authority (CA):
openssl req -new -key "${SUBJ_KEY_FILE}" -out "${SUBJ_CSR_FILE}"
echo -e "${or}\n   [>] File created: \"${SUBJ_CSR_FILE}\"\n${nc}"

#==ACTIONS TAKEN BY THE CERTIFICATE AUTHORITY==============================================
echo -e "\n${gr}
[+] Step (3/4): Sign the Certificate Signing Request with the CA's private key.
This process establishes that the CA has accepted our request and validated our server.
The signed certificate is now sent from the CA to the Subject. This piece of
information is public.
${nc}\n"

# 5. Sign the CSR with the CA's private key:
openssl x509 -req -in "${SUBJ_CSR_FILE}" -CA "${CA_CERT_FILE}" \
-CAkey "${CA_KEY_FILE}" -CAcreateserial -out "${SUBJ_CRT_FILE}" -days "${VALID}"
echo -e "${or}\n   [>] File created: \"${SUBJ_CRT_FILE}\"\n${nc}"

#==ACTIONS TAKEN BY THE SERVER ADMINISTRATOR===============================================
echo -e "\n${gr}
[+] Step (4/4): After receiving the signed certificate from the CA, we convert its
contents to human-readable format and, finally, append it to the server's
private key in order to generate the server's PEM file. This file is supposed
to be kept secret by the application. Any event that leads to a threat agent taking
hold of this file and its contents may lead to the impersonation of the service
being established.
${nc}\n"

# 6. Convert the Certificate's contents to text and generate a file:
openssl x509 -in "${SUBJ_CRT_FILE}" -text > "${SUBJ_CRT_READ_FILE}"
echo -e "${or}   [>] File created: \"${SUBJ_CRT_READ_FILE}\"\n${nc}"

# 7. Generate the server.pem file by concatenating the Certificate and private key files:
cat "${SUBJ_CRT_READ_FILE}" "${SUBJ_KEY_FILE}" > "${SUBJ_PEM_FILE}"
echo -e "${or}   [>] File created: \"${SUBJ_PEM_FILE}\"\n${nc}"

#==PROCESS COMPLETED======================================================================

echo -e "${gr}"
read -rp "[!] From now on the only files you will need are \"${SUBJ_PEM_FILE}\"
and \"${CA_CERT_FILE}\". You can safely delete all the other files that have been
generated right now or keep them for further analysis. Would you like to delete
these files? (Y/N) " DELYN
echo -e "${nc}\n"

case ${DELYN} in
  [Yy]* ) rm "${CA_KEY_FILE}" "${SUBJ_KEY_FILE}" "${SUBJ_CSR_FILE}" \
    "${SUBJ_CRT_FILE}" "${SUBJ_CRT_READ_FILE}" ./*.srl
    echo -e "${or}   [!] SUCCESS: Extra files were deleted.\n${nc}";;
  [Nn]* ) echo -e "${or}   [!] SUCCESS: Extra files will be kept.\n${nc}";;
esac

#=========================================================================================

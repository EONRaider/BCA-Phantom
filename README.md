# Python 3 HTTPS Reverse Shell

![Python Version](https://img.shields.io/badge/python-3.9+-blue?style=for-the-badge&logo=python)
![OS](https://img.shields.io/badge/GNU%2FLinux-red?style=for-the-badge&logo=linux)
![OS](https://img.shields.io/badge/Windows-blue?style=for-the-badge&logo=windows)

[![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/EONRaider/BCA-HTTPS-Reverse-Shell?label=CodeFactor&logo=codefactor&style=for-the-badge)](https://www.codefactor.io/repository/github/EONRaider/BCA-HTTPS-Reverse-Shell)
[![License](https://img.shields.io/github/license/EONRaider/BCA-HTTPS-Reverse-Shell?style=for-the-badge)](https://github.com/EONRaider/BCA-HTTPS-Reverse-Shell/blob/master/LICENSE)

[![Reddit](https://img.shields.io/badge/Reddit-EONRaider-FF4500?style=flat-square&logo=reddit)](https://www.reddit.com/user/eonraider)
[![Discord](https://img.shields.io/badge/Discord-EONRaider-7289DA?style=flat-square&logo=discord)](https://discord.gg/KVjWBptv)
[![Twitter](https://img.shields.io/badge/Twitter-eon__raider-38A1F3?style=flat-square&logo=twitter)](https://twitter.com/intent/follow?screen_name=eon_raider)

A **cross-platform HTTPS Reverse Shell** server and client in Python 3. Binaries for
Linux and Windows platforms can be built through an embedded script that implements
PyInstaller.

This application also includes a helper shell script that enables fast generation of
self-signed certificates for use of both servers and clients. After generation, the
server and certificate authority certificates required for encrypted connections 
are bundled in the binaries for portability and ease of execution.

## Try it out!
If you just need to see the tool in action on a local environment, simply head over 
to the [demo-files](https://github.com/EONRaider/BCA-HTTPS-Reverse-Shell/tree/master/demo-files) 
directory and download the pre-built Linux/Unix/macOS or Windows binaries.

The files are all bundled with certificates for `localhost` and work straight out-of-the-box. *Just
set them with permissions to execute and run.*

## Build
Encrypted communication through HTTPS requires at least two certificates: One for 
the server, named `server.pem` by default, and another for the certificate authority, or `ca.pem`. 
This HTTPS Reverse Shell bundles both files in binaries for fast deployment. They can be 
generated by [multiple methods](https://www.digitalocean.com/community/tutorials/openssl-essentials-working-with-ssl-certificates-private-keys-and-csrs) 
or by a simple execution of the [generate_certs.sh](https://github.com/EONRaider/BCA-HTTPS-Reverse-Shell/blob/master/src/generate_certs.sh) helper script.

Once the certificates are ready you only need to (I) install the dependencies and (II) 
run `build.py` to  build the `server` and `client` binaries.

### I. Install Dependencies
Dependency management works with both [Poetry](https://python-poetry.org/) (recommended)
and [Virtualenv](https://virtualenv.pypa.io/en/latest/)
```shell
git clone https://github.com/EONRaider/BCA-HTTPS-Reverse-Shell.git
cd BCA-HTTPS-Reverse-Shell
poetry install <--or--> pip install -r requirements.txt
```

### II. Build Server and Client binaries
The `build.py` file takes care of it all.
```shell
python build.py server --server-cert /path/to/server.pem
python build.py client --ca-cert /path/to/ca.pem
```

## Usage
![usage](https://github.com/EONRaider/static/blob/97b0e81aee6eb0f2b255a26cd138299e2361d025/https-reverse-shell/usage.gif)

## Development mode (optional)
You could optionally run the HTTPS Reverse Shell directly from a local Python 3 
interpreter. Install all dependencies and run the `server.py` and `client.py` files. 
All required certificates will be automatically generated for `localhost`.

Execute the **Server** on one shell...
```shell
python src/server/server.py localhost 4443
```

... And the **Client** on another shell:
```shell
python src/client/client.py \
--host localhost \
--port 4443 \
--ca-cert src/server/ca.pem
```

## Legal Disclaimer

The use of code contained in this repository, either in part or in its totality,
for engaging targets without prior mutual consent is illegal. **It is
the end user's responsibility to obey all applicable local, state and
federal laws.**

Developers assume **no liability** and are not
responsible for misuses or damages caused by any code contained
in this repository in any event that, accidentally or otherwise, it comes to
be utilized by a threat agent or unauthorized entity as a means to compromise
the security, privacy, confidentiality, integrity, and/or availability of
systems and their associated resources. In this context the term "compromise" is
henceforth understood as the leverage of exploitation of known or unknown vulnerabilities
present in said systems, including, but not limited to, the implementation of
security controls, human- or electronically-enabled.

The use of this code is **only** endorsed by the developers in those
circumstances directly related to **educational environments** or
**authorized penetration testing engagements** whose declared purpose is that
of finding and mitigating vulnerabilities in systems, limiting their exposure
to compromises and exploits employed by malicious agents as defined in their
respective threat models.

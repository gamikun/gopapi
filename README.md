Papi stands for "daddy" in spanish.

# Authorization
API key and secret is ciphered with a AES using a password.

# Installation

    pip install gopapi

# Usage

## Adding a DNS record to a domain

	# A record
    gopapi domain yourdomain.com add-record A subdomain 127.0.0.1
    # Where A can also be CNAME
    # 127.0.0.1 to be replaced with the actual IP

    # CNAME
    gopapi domain yourdomain.com add-record A subdomain 127.0.0.1
    # Where A can also be CNAME
    # 127.0.0.1 to be replaced with the actual IP



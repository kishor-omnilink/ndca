"""
Authentication Test
"""

from ndca.api.auth import AuthenticationManager


def main():

    auth = AuthenticationManager()

    session = auth.login()

    print()

    print("Authentication Successful")

    print("-------------------------")

    print(f"Token Type : {session.token_type}")

    print(f"Expires    : {session.expires_at}")

    print(
        f"Token      : {session.access_token[:40]}..."
    )

    auth.close()


if __name__ == "__main__":
    main()
from ndca.api.base_client import BaseApiClient


def main():

    client = BaseApiClient()

    #
    # Use the endpoint that returns network elements
    # Replace the path below with the verified NSP endpoint
    #
    response = client.get(
        "/restconf/data/network:network"
    )

    print(type(response))

    if isinstance(response, dict):
        print("REST Client Test PASSED")
        print(response.keys())

    client.close()


if __name__ == "__main__":
    main()
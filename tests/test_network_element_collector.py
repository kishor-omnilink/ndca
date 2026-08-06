from ndca.collectors.inventory.network_element_collector import (
    NetworkElementCollector,
)


def main():

    collector = NetworkElementCollector()

    response = collector.collect()

    print()

    print("Collection Successful")

    print("---------------------")

    print(type(response))

    if isinstance(response, dict):

        print()

        print("Root Keys:")

        for key in response.keys():

            print("-", key)

    collector.close()


if __name__ == "__main__":
    main()
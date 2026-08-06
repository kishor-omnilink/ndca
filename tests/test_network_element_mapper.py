from ndca.collectors.inventory.network_element_collector import (
    NetworkElementCollector,
)

from ndca.mappers.network_element_mapper import (
    NetworkElementMapper,
)


def main():

    collector = NetworkElementCollector()

    try:
        response = collector.collect()

        network_elements = NetworkElementMapper.map(response)

        print()
        print("=" * 60)
        print(f"Network Elements Found : {len(network_elements)}")
        print("=" * 60)

        if network_elements:
            ne = network_elements[0]

            print(f"NE ID               : {ne.ne_id}")
            print(f"NE Name             : {ne.ne_name}")
            print(f"Admin State         : {ne.admin_state}")
            print(f"Oper State          : {ne.oper_state}")
            print(f"Availability State  : {ne.availability_state}")
            print(f"Description         : {ne.description}")
            print(f"Source Type         : {ne.source_type}")

        print("=" * 60)

    finally:
        collector.close()


if __name__ == "__main__":
    main()
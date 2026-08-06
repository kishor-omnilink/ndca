from ndca.services.inventory_snapshot_service import (
    InventorySnapshotService,
)


def main():

    service = InventorySnapshotService()

    try:

        snapshot = service.collect()

        print()

        print("=" * 60)

        print("Inventory Snapshot")

        print("=" * 60)

        print(f"Sync ID        : {snapshot.sync_id}")

        print(f"Collected At   : {snapshot.collected_at}")

        print(f"Source         : {snapshot.source}")

        print(f"Endpoint       : {snapshot.endpoint}")

        print(f"Network Elements : {snapshot.network_element_count}")

        print("=" * 60)

    finally:

        service.close()


if __name__ == "__main__":
    main()
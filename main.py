# main.py
import time
from storage_virtual_network import StorageVirtualNetwork
from storage_virtual_node import StorageVirtualNode


def create_network_with_3_nodes():
    network = StorageVirtualNetwork()

    # Define 3 nodes
    nodes_specs = [
        {"id": "node-alpha", "cpu_capacity": 4,  "memory_capacity": 16, "storage_capacity": 500,  "bandwidth": 1000},
        {"id": "node-beta",  "cpu_capacity": 8,  "memory_capacity": 32, "storage_capacity": 2000, "bandwidth": 2500},
        {"id": "node-gamma", "cpu_capacity": 16, "memory_capacity": 64, "storage_capacity": 4000, "bandwidth": 5000},
    ]

    nodes = {}
    print("Creating 3 storage nodes automatically...\n")

    for spec in nodes_specs:
        node = StorageVirtualNode(
            node_id=spec["id"],
            cpu_capacity=spec["cpu_capacity"],
            memory_capacity=spec["memory_capacity"],
            storage_capacity=spec["storage_capacity"],
            bandwidth=spec["bandwidth"]
        )
        network.add_node(node)                    # Add to network
        nodes[spec["id"]] = node                  # Save reference

        print(f"Created node: {spec['id']} | "
              f"CPU: {spec['cpu_capacity']} vCPU | "
              f"RAM: {spec['memory_capacity']} GB | "
              f"Storage: {spec['storage_capacity']} GB | "
              f"Bandwidth: {spec['bandwidth']} Mbps")

    # Connect all nodes (full mesh)
    print("\nEstablishing network connections...")
    node_ids = list(nodes.keys())
    for i in range(len(node_ids)):
        for j in range(i + 1, len(node_ids)):
            n1, n2 = node_ids[i], node_ids[j]
            link_bw_mbps = min(nodes[n1].bandwidth // 1_000_000, nodes[n2].bandwidth // 1_000_000)
            network.connect_nodes(n1, n2, link_bw_mbps * 1_000_000)
            print(f"Connected {n1} <-> {n2} with {link_bw_mbps} Mbps link")

    return network, nodes   # This is NOW inside the function!


# ————————————————————————
# Main Program Starts Here
# ————————————————————————
if __name__ == "__main__":
    print("=" * 70)
    print(" CLOUD STORAGE NETWORK SIMULATOR - AUTO 3 NODES ".center(70))
    print("=" * 70)

    # Automatically create 3 nodes
    network, nodes = create_network_with_3_nodes()

    print("\nNetwork ready! Starting 300 MB file transfer demo...\n")

    # Start transfer: node-alpha → node-gamma
    transfer = network.initiate_file_transfer(
        source_node_id="node-alpha",
        target_node_id="node-gamma",
        file_name="large_dataset.zip",
        file_size=300 * 1024 * 1024  # 300 MB
    )

    if not transfer:
        print("Transfer failed: not enough space or invalid node")
    else:
        print(f"Transfer STARTED")
        print(f"File: {transfer.file_name}")
        print(f"Size: {transfer.total_size / 1024 / 1024:.1f} MB")
        print(f"Chunks: {len(transfer.chunks)} × {transfer.chunks[0].size / 1024 / 1024:.1f} MB each")
        print("-" * 70)

        start_time = time.time()
        transferred_chunks = 0
        total_chunks = len(transfer.chunks)

        while True:
            chunks_done, completed = network.process_file_transfer(
                source_node_id="node-alpha",
                target_node_id="node-gamma",
                file_id=transfer.file_id,
                chunks_per_step=3
            )
            transferred_chunks += chunks_done

            if chunks_done > 0:
                progress = (transferred_chunks / total_chunks) * 100
                elapsed = time.time() - start_time
                speed_mb = (transferred_chunks * transfer.chunks[0].size / 1024 / 1024) / elapsed
                print(f"Progress: {progress:6.2f}% | Speed: {speed_mb:6.2f} MB/s | "
                      f"Chunks: {transferred_chunks}/{total_chunks}")

            if completed:
                total_time = time.time() - start_time
                avg_speed = 300 / total_time
                print("\n" + " TRANSFER COMPLETED SUCCESSFULLY! ".center(70, "="))
                print(f"Total time: {total_time:.2f} seconds")
                print(f"Average speed: {avg_speed:.2f} MB/s")
                print(f"File now stored on node-gamma")
                print(f"Storage used: {nodes['node-gamma'].get_storage_utilization()['utilization_percent']:.2f}%")
                break

            time.sleep(0.01)  # Prevent CPU overload
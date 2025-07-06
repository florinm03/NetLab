from io import StringIO
from typing import List


class FrrConfig:
    def __init__(self, config_content):
        self.file_obj = StringIO(config_content)
        self.config = self._read_config()

    def _read_config(self) -> List[str]:
        self.file_obj.seek(0)  # Move to the beginning of the file
        return self.file_obj.readlines()

    def add_ospf_network(self, subnet) -> str:
        # Check if router ospf section exists
        router_ospf_index = None
        for index, line in enumerate(self.config):
            if "router ospf" in line:
                router_ospf_index = index
                break

        # If router ospf section does not exist, create it
        if router_ospf_index is None:
            self.config.append("router ospf\n")
            router_ospf_index = len(self.config) - 1

        # Add the network to router ospf section
        self.config.insert(router_ospf_index + 1, f"  network {subnet} area 0.0.0.0\n")

        return self._add_interface()

    def _add_interface(self) -> str:
        # Count existing interfaces
        interface_count = 0
        for line in self.config:
            if line.startswith("interface "):
                interface_count += 1

        # Determine the next interface name
        next_interface_name = f"eth{interface_count}"

        # Add the new interface configuration
        self.config.extend(
            [f"interface {next_interface_name}\n", "  ip ospf area 0.0.0.0\n"]
        )
        return next_interface_name

    def get_config(self) -> str:
        return "".join(self.config)

    def __str__(self):
        return "".join(self.config)

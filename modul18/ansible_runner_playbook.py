from pathlib import Path

import ansible_runner

BASE = Path(__file__).parent.resolve()
PLAYBOOK = str((BASE / "add_static_route.yaml").resolve())
INVENTORY = str((BASE / "inventory.ini").resolve())

out = ansible_runner.run(
    private_data_dir='.',
    playbook=PLAYBOOK,
    inventory=INVENTORY,
    json_mode=True,
)
print(out)

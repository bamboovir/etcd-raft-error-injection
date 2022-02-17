# Hypervisor

---

## Setup develop environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e "."
```

## Usage

```bash
hypervisor --help
hypervisor --raft_cluster_size=<num:3> --test_report_path="$(pwd)/report"
hypervisor --raft_cluster_size=<num:3> --test_report_path="$(pwd)/report" <testname>
hypervisor --raft_cluster_size=<num:3> --test_report_path="$(pwd)/report" baseline
```

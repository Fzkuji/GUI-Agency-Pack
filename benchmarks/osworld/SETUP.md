# 新机器部署指南

在另一台 macOS 上快速跑起来 OSWorld 实验。

## 1. 安装项目

```bash
pip install git+https://github.com/Fzkuji/GUI-Agent-Harness.git
```

## 2. 安装 Claude Code CLI

```bash
npm install -g @anthropic-ai/claude-code
claude login
```

## 3. Clone OSWorld

```bash
cd ~
git clone https://github.com/xlang-ai/OSWorld.git
cd OSWorld && pip install -e .
```

## 4. 拷贝 VM

把旧机器上的 `~/OSWorld/vmware_vm_data/` 整个文件夹拷到新机器同样的位置。约 44GB。

新机器需要安装 VMware Fusion。

## 5. 确认 VM IP

启动 VM，在 VM 里 `ifconfig` 看 IP。默认是 `172.16.82.132`，如果不同就跑的时候加 `--vm` 参数。

## 6. 跑实验

```bash
cd GUI-Agent-Harness

# 单个任务
python benchmarks/osworld/run_osworld_task.py 88 --max-steps 15

# 批量
bash benchmarks/osworld/run_batch.sh 1 101 multi_apps
bash benchmarks/osworld/run_batch.sh 1 26 gimp
```

## 可选：Surge 代理

如果需要 VM 联网（部分任务需要），在新机器上装 Surge 并监听 6152 端口。脚本会自动给 VM 配代理 `http://172.16.82.1:6152`。

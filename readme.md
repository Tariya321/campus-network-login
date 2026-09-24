# Campus Network Auto Login Tool / 校园网自动登录工具

English | 简介

This repository contains a small Python script to automate campus network login. It supports multiple local IPs (multi-device) and reads credentials from a local `config.ini`.

本仓库包含一个用于校园网自动登录的 Python 脚本，支持多设备（多个本机 IP）登录，并从本地 `config.ini` 读取凭据。

---

## Quick Start / 快速开始

1. Copy `config.example.ini` to `config.ini` and edit the values (replace placeholders).
   复制 `config.example.ini` 为 `config.ini` 并填写真实信息（替换占位符）。
2. Run the script:

```bash
python WanLoginer.py
```

## Watchdog / 断网监控

The watchdog checks internet access every 30 seconds. After two consecutive failures, it runs `WanLoginer.py` once; it waits for the connection to recover before re-arming. The default log is `logs/network-watchdog.log`.

watchdog 默认每 30 秒检查一次外网；连续失败两次后运行一次 `WanLoginer.py`，网络恢复后才会重新布防。默认日志位于 `logs/network-watchdog.log`。

```bash
./run_watchdog.sh
```

Useful options / 常用参数：

```bash
# Check every 20 seconds and trigger after one failure
./run_watchdog.sh --interval 20 --failure-threshold 1

# Use another URL to check connectivity
./run_watchdog.sh --check-url https://example.com
```

The launcher uses `.venv/bin/python` when present, or `python3` otherwise. Create `config.ini` as described above before enabling automatic login.

启动脚本优先使用项目内的 `.venv/bin/python`，否则使用 `python3`。启用自动登录前，请按上文配置 `config.ini`。

### Run as a systemd service / 作为 systemd 服务运行

Copy `campus-network-watchdog.service.example` to `/etc/systemd/system/campus-network-watchdog.service`. Edit `User`, `WorkingDirectory`, and `ExecStart` to match the account and absolute v3 directory on your machine, then enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now campus-network-watchdog.service
sudo systemctl status campus-network-watchdog.service
```

Follow service output with `journalctl -u campus-network-watchdog.service -f`; the watchdog also writes to `logs/network-watchdog.log`.

将 `campus-network-watchdog.service.example` 复制到 `/etc/systemd/system/campus-network-watchdog.service`，并按本机情况修改 `User`、`WorkingDirectory` 和 `ExecStart` 的绝对路径，然后启用服务。服务输出可通过 `journalctl -u campus-network-watchdog.service -f` 查看；watchdog 也会写入 `logs/network-watchdog.log`。

### NAS task scheduler / NAS 任务计划

For a NAS task scheduler, use the absolute path to this version's `run_watchdog.sh` as the startup command. The watchdog runs in the v3 directory and uses its `config.ini` and virtual environment.

在 NAS 任务计划中，可将本版本 `run_watchdog.sh` 的绝对路径设为启动命令。watchdog 会在 v3 目录下运行，并使用该目录中的 `config.ini` 和虚拟环境。

---

## Configuration / 配置说明

- Place credentials and IP entries in `[UserConfig]` section of `config.ini`.
- 将账号和 IP 配置写入 `config.ini` 的 `[UserConfig]` 节。

Examples / 示例：

```ini
[UserConfig]
username = your_student_id
password = your_password
u_ip = 192.0.2.10        ; primary device (example address)
u_ip_laptop = 192.0.2.11 ; optional additional devices
u_ip_desktop = 192.0.2.12
```

Notes / 说明：
- Configuration keys that start with `u_ip` will be picked up automatically (e.g. `u_ip`, `u_ip_2`, `u_ip_name`).
- 以 `u_ip` 开头的配置项都会被自动识别（例如 `u_ip`, `u_ip_2`, `u_ip_laptop`）。

---

## Features / 特性

- Automatic campus network login for one or multiple local IPs.
- 支持针对单个或多个 IP 的自动登录。

- Monitors internet connectivity and retries login once per outage.
- 监控外网连接，并在每次断网时触发一次登录。

- Uses OCR (ddddocr) to read the verification code when required.
- 当需要验证码时，使用 `ddddocr` 进行识别。

- Keeps credentials local (do not commit `config.ini`).
- 凭据保存在本地，`config.ini` 请勿提交到公开仓库。

---

## Security / 安全建议

- Do NOT commit `config.ini` to GitHub. Use `config.example.ini` as a template.
- 不要将 `config.ini` 提交到 GitHub，使用 `config.example.ini` 作为示例模板。

- If you accidentally committed secrets, rotate the password immediately and purge history.
- 如果不慎提交了敏感信息，请立即更换密码并清理 Git 历史。

---

## Example Output / 运行示例

```
Found 3 IP address(es) to login: 192.0.2.10 (u_ip), 192.0.2.11 (u_ip_laptop), 192.0.2.12 (u_ip_desktop)

[1/3] Attempting to login for IP: 192.0.2.10 (u_ip)
  ✓ Successfully connected for IP: 192.0.2.10 (u_ip)

[2/3] Attempting to login for IP: 192.0.2.11 (u_ip_laptop)
  ✓ Successfully connected for IP: 192.0.2.11 (u_ip_laptop)

[3/3] Attempting to login for IP: 192.0.2.12 (u_ip_desktop)
  ✓ Successfully connected for IP: 192.0.2.12 (u_ip_desktop)

==================================================
All IP addresses successfully connected!
```

---

## More / 更多

See `update.md` for a short changelog and implementation notes.
查看 `update.md` 获取更新日志和实现说明。

---

If you want, I can also help generate a concise English-only description for the GitHub repository page (short description), or add a license file. 
如需，我还可以帮你生成适合放到仓库简介（short description）的英文短句，或添加许可证文件。

---

## Requirements / 依赖

- Python 3.8+ is recommended. / 建议使用 Python 3.8 及以上。
- The script depends on a few third-party packages which can be installed via pip.

Install (recommended steps):

```bash
# create and activate virtualenv
python -m venv .venv
source .venv/bin/activate

# install dependencies
pip install -r requirements.txt
```

常用依赖说明：

- `requests` : HTTP client for making requests
- `beautifulsoup4` : HTML parsing (`bs4`)
- `ddddocr` : OCR for verification codes

安装示例（Windows PowerShell）：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

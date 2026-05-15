# Auto Login Tool / 自动登录工具

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

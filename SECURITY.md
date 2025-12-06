# Security Guidelines

## Environment Configuration

This project uses environment variables to store sensitive information like API keys and server details. **Never commit credentials to version control.**

### Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your actual credentials:
   ```bash
   # Update these with your real values
   export VASTAI_HOST="root@YOUR_ACTUAL_IP"
   export VASTAI_PORT="YOUR_ACTUAL_PORT"
   export VLLM_API_KEY="your_actual_api_key"
   ```

3. Source the environment file before running scripts:
   ```bash
   source .env
   ./run_remote_benchmark.sh vllm medium_chat "1 10 50"
   ```

## What's Protected

The following sensitive information should never be committed:

- ✅ **API Keys**: All framework API keys (vLLM, SGLang, TensorRT)
- ✅ **Server IPs**: Your Vast.ai instance IP address
- ✅ **SSH Ports**: Your Vast.ai SSH port (changes with each instance)
- ✅ **SSH Keys**: Private key files (vastai_ed25519, etc.)
- ✅ **Cloudflare Tunnels**: If using tunnels, URLs contain sensitive tokens

## Before Sharing

If you're sharing this code publicly:

1. Verify no credentials in files:
   ```bash
   grep -r "api.key\|password\|[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}" \
     --include="*.py" --include="*.sh" --include="*.md" --exclude-dir=lib
   ```

2. Check for real server IPs or API keys in documentation

3. Ensure `.env` is in `.gitignore` (it is by default)

## File Safety Status

✅ **Safe to share** (sanitized):
- All `.sh` scripts (use environment variables)
- All `.md` documentation (use placeholders)
- All `.py` files (accept credentials as arguments)

❌ **Never share**:
- `.env` file (your actual credentials)
- SSH private keys
- Any files with real IP addresses or API keys

## Reporting Security Issues

If you find exposed credentials or security issues, please:
1. Do not open a public issue
2. Contact the repository owner privately
3. Allow time for the issue to be addressed before disclosure

# -*- coding: utf-8 -*-
"""
Ertuğrul YZ - GitHub Taşıma ve Yayınlama Aracı
Depo: ertugrul34660/bahis-oyunlari
"""

import os
import sys
import json
import subprocess
import urllib.request
import urllib.error
import ctypes
from ctypes import wintypes
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Git ve kimlik bilgisi
GIT_BIN = r"C:\Users\ertug\AppData\Local\GitHubDesktop\app-3.6.10\resources\app\git\cmd\git.exe"

class CREDENTIAL(ctypes.Structure):
    _fields_ = [
        ('Flags', wintypes.DWORD), ('Type', wintypes.DWORD), ('TargetName', wintypes.LPWSTR),
        ('Comment', wintypes.LPWSTR), ('LastWritten', wintypes.FILETIME),
        ('CredentialBlobSize', wintypes.DWORD), ('CredentialBlob', ctypes.POINTER(ctypes.c_byte)),
        ('Persist', wintypes.DWORD), ('AttributeCount', wintypes.DWORD),
        ('Attributes', ctypes.c_void_p), ('TargetAlias', wintypes.LPWSTR), ('UserName', wintypes.LPWSTR),
    ]

def get_github_token():
    advapi32 = ctypes.windll.advapi32
    CredReadW = advapi32.CredReadW
    CredReadW.argtypes = [wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(ctypes.POINTER(CREDENTIAL))]
    CredReadW.restype = wintypes.BOOL

    pcred = ctypes.POINTER(CREDENTIAL)()
    if CredReadW('GitHub - https://api.github.com/ertugrul34660', 1, 0, ctypes.byref(pcred)):
        blob = bytes(ctypes.string_at(pcred.contents.CredentialBlob, pcred.contents.CredentialBlobSize))
        return blob.decode('utf-8')
    raise RuntimeError("Windows Credential Manager üzerinde GitHub belirteci bulunamadı.")


def create_github_repo(token, repo_name="bahis-oyunlari"):
    url = "https://api.github.com/user/repos"
    payload = {
        "name": repo_name,
        "description": "Ertuğrul YZ - Otonom Spor & Bahis Oyunları Analiz Motoru (Maçkolik İddaa Robotu, Quant Borsa Modeli & Öz-Öğrenme)",
        "private": False,
        "has_issues": True,
        "has_wiki": True
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"token {token}",
        "User-Agent": "Ertugrul-YZ-Agent",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    })
    try:
        with urllib.request.urlopen(req) as resp:
            res_data = json.loads(resp.read().decode('utf-8'))
            print(f"[✓] GitHub Deposu Başarıyla Oluşturuldu: {res_data.get('html_url')}")
            return res_data.get('clone_url')
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        if e.code == 422 and "name already exists" in body:
            print(f"[*] Depo zaten mevcut, var olan depoya gönderilecek: https://github.com/ertugrul34660/{repo_name}")
            return f"https://github.com/ertugrul34660/{repo_name}.git"
        else:
            raise RuntimeError(f"GitHub API Hatası ({e.code}): {body}")


def run_cmd(cmd_list, cwd=PROJECT_ROOT):
    env = os.environ.copy()
    git_dir = r"C:\Users\ertug\AppData\Local\GitHubDesktop\app-3.6.10\resources\app\git\cmd"
    env["PATH"] = git_dir + os.pathsep + env.get("PATH", "")
    res = subprocess.run(cmd_list, cwd=str(cwd), env=env, capture_output=True, text=True, encoding='utf-8')
    if res.returncode != 0:
        print(f"[!] Hata: {' '.join(cmd_list)}")
        print(f"    STDOUT: {res.stdout}")
        print(f"    STDERR: {res.stderr}")
    return res


def push_to_github():
    print("=" * 70)
    print("🚀 ERTUĞRUL YZ - GİTHUB'A PROJE TAŞIMA VE YAYINLAMA OPERASYONU")
    print("=" * 70)

    token = get_github_token()
    print("[✓] GitHub belirteci Windows Credential Manager'dan alındı (Kullanıcı: ertugrul34660).")

    repo_url = create_github_repo(token, "bahis-oyunlari")

    # 1. Git Init
    git_dir = PROJECT_ROOT / ".git"
    if not git_dir.exists():
        print("[*] Yerel git deposu başlatılıyor...")
        run_cmd([GIT_BIN, "init", "-b", "main"])
    
    # Kullanıcı ayarları
    run_cmd([GIT_BIN, "config", "user.name", "ertugrul34660"])
    run_cmd([GIT_BIN, "config", "user.email", "ertugrulkokce@gmail.com"])

    # 2. Add and Commit
    print("[*] Dosyalar git havuzuna ekleniyor...")
    run_cmd([GIT_BIN, "add", "."])
    
    print("[*] İlk sürüm taahhüt ediliyor (commit)...")
    run_cmd([GIT_BIN, "commit", "-m", "Ertuğrul YZ - Otonom Spor ve Bahis Oyunları Analiz Motoru (v1.0.0 Tam Sürüm)"])

    # 3. Remote URL belirle (geçici olarak token içeren URL ile push)
    auth_remote_url = f"https://ertugrul34660:{token}@github.com/ertugrul34660/bahis-oyunlari.git"
    clean_remote_url = "https://github.com/ertugrul34660/bahis-oyunlari.git"

    # Eski remote varsa sil
    run_cmd([GIT_BIN, "remote", "remove", "origin"])
    run_cmd([GIT_BIN, "remote", "add", "origin", auth_remote_url])

    # 4. Push
    print("[*] GitHub'a yükleniyor (git push origin main)...")
    push_res = run_cmd([GIT_BIN, "push", "-u", "origin", "main", "--force"])

    # Güvenlik: Remote URL'den token'ı temizle
    run_cmd([GIT_BIN, "remote", "set-url", "origin", clean_remote_url])

    if push_res.returncode == 0:
        print("\n" + "=" * 70)
        print("🎉 TEBRİKLER! PROJE GİTHUB'A BAŞARIYLA TAŞINDI VE YAYINLANDI!")
        print("=" * 70)
        print(f"🔗 Depo Bağlantısı: {clean_remote_url}")
        print("📦 Depo Adı      : ertugrul34660/bahis-oyunlari")
        print("🛡️ Marka         : Ertuğrul YZ Holding")
        print("=" * 70 + "\n")
        return True
    else:
        print("[!] Push işlemi sırasında hata oluştu.")
        return False


if __name__ == "__main__":
    push_to_github()

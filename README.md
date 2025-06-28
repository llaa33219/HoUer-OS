# HoUer OS

HoUer OS는 컨테이너 중심으로 동작하며 Enlightenment를 기본 DE로 사용하는 아치리눅스 기반 운영체제입니다.

![HoUer OS Logo](LOGO.png)

## 주요 특징

- **컨테이너 중심 아키텍처**: distrobox와 soda를 활용한 효율적인 애플리케이션 격리
- **Enlightenment DE**: 가벼우면서도 아름다운 데스크톱 환경
- **통합 컨테이너 관리**: HoUer Manager를 통한 직관적인 컨테이너 관리
- **크로스 플랫폼 지원**: Linux 및 Windows 애플리케이션 모두 지원
- **Wayland 우선**: 최신 디스플레이 서버 기술 지원

## 설치

### 전제 조건
- 아치리눅스 라이브 환경 (USB 또는 CD/DVD 부팅)
- 인터넷 연결
- 충분한 디스크 공간 (최소 4GB, 권장 8GB)

### 설치 방법

**⚠️ 중요: 이 설치는 Arch Linux 라이브 환경에서 수행해야 합니다**

1. **Arch Linux ISO 부팅**:
   - Arch Linux ISO를 다운로드하고 USB에 구워서 부팅
   - 라이브 환경에서 인터넷 연결 설정

2. **HoUer OS 설치 파일 다운로드**:
```bash
# 라이브 환경에서 실행
pacman -Sy git
git clone https://github.com/your-repo/houer-os.git
cd houer-os
```

3. **설치 환경 준비**:
```bash
chmod +x installer/install.sh
sudo ./installer/install.sh
```

4. **Calamares 설치 마법사 진행**:
   - 스크립트가 자동으로 Calamares 실행
   - 일반적인 Linux 설치 과정만 진행:
     - 언어 선택
     - 키보드 레이아웃
     - 파티션 설정
     - 사용자 계정 생성
     - **설치 클릭** → 모든 것이 자동으로 완료됨

5. **자동 설치 완료**:
   - Calamares가 자동으로 HoUer OS 모든 구성요소 설치
   - 재부팅하면 HoUer OS 사용 준비 완료
   - `houer-manager` 명령어로 컨테이너 관리자 실행

**📋 설치 과정 요약:**
- **준비 스크립트**: 라이브 환경에서 Calamares 설치 도구 준비
- **Calamares 1단계**: Arch Linux 기본 시스템 설치 (base, kernel, bootloader, 사용자 계정)
- **Calamares 2단계**: 자동으로 HoUer OS 구성요소 설치 (post-install 스크립트 실행)
- **완료**: 재부팅하면 HoUer OS 사용 준비 완료

**🚀 설치 과정 (모두 자동):**

**Calamares 설치 중 자동으로 진행:**
1. 기본 시스템 설치 (base, linux, bootloader)
2. HoUer OS 구성요소 자동 설치:
   - base-devel, networkmanager, git
   - Enlightenment 데스크톱 환경
   - 컨테이너 도구 (podman, distrobox, flatpak)
   - HoUer Manager (Python 기반)
   - 한국어 입력기 및 폰트
   - 최소 오디오/디스플레이 지원

**사용자 작업:** Calamares 설치 마법사만 진행 → 자동으로 모든 설정 완료

**📦 애플리케이션은 컨테이너로:**
Firefox, 개발도구, 멀티미디어 앱 등은 컨테이너로 설치하여 시스템을 깔끔하게 유지

## HoUer Manager

HoUer Manager는 HoUer OS의 핵심 컴포넌트로, 컨테이너 관리를 위한 GUI 애플리케이션입니다.

### 주요 기능

- **Linux 컨테이너 관리**: distrobox 기반 Linux 배포판 컨테이너
- **Windows 컨테이너 지원**: soda를 통한 Windows 애플리케이션 실행
- **애플리케이션 바로가기**: 컨테이너 애플리케이션의 데스크톱 바로가기 생성
- **ISO 설치**: ISO 파일에서 직접 컨테이너 생성
- **설정 관리**: 컨테이너별 개별 설정 관리

### 실행 방법

설치 후 다음 방법들로 HoUer Manager를 실행할 수 있습니다:

```bash
# 1. 명령어로 실행 (권장)
houer-manager

# 2. 짧은 명령어
houer

# 3. 옵션과 함께 실행
houer-manager --debug          # 디버그 모드
houer-manager --minimized      # 최소화 상태로 시작
houer-manager --help           # 도움말 표시
houer-manager --version        # 버전 정보

# 4. 직접 Python 실행
python3 /opt/houer-manager/houer-manager.py

# 5. 데스크톱에서 "HoUer Manager" 애플리케이션 실행
```

### 개발 환경에서 테스트

**⚠️ 주의**: 개발 환경에서는 HoUer Manager만 테스트할 수 있습니다. 실제 설치는 Arch Linux 라이브 환경에서 해야 합니다.

```bash
# HoUer Manager 개발 테스트
./test-houer-manager.sh

# HoUer Manager 직접 실행
./Manager/houer-manager

# 도움말 확인
./Manager/houer-manager --help
```

**절대 하지 말 것:**
- 현재 시스템에서 `installer/install.sh` 실행 ❌
- 개발 중인 OS에서 설치 스크립트 테스트 ❌

## 지원 배포판

### Linux 컨테이너
- Ubuntu (latest)
- Fedora (latest)
- Debian (latest)
- Arch Linux (latest)
- Alpine (latest)
- openSUSE Tumbleweed
- CentOS Stream 9

### Windows 컨테이너
- Windows 10
- Windows 11

## 시스템 요구사항

### 최소 사양
- CPU: x86_64 아키텍처
- RAM: 1GB (2GB 권장)
- 저장공간: 4GB (컨테이너용 추가 공간 필요)
- 그래픽: 통합 그래픽 또는 전용 그래픽카드

### 권장 사양
- CPU: 멀티코어 프로세서
- RAM: 4GB 이상 (컨테이너 다중 실행용)
- 저장공간: SSD 16GB 이상
- 그래픽: NVIDIA 또는 AMD 전용 그래픽카드

**💡 컨테이너 중심 설계**: HoUer OS는 최소한의 시스템만 설치하고, 애플리케이션들은 컨테이너로 실행합니다. 이를 통해 공간을 절약하고 안전하게 앱을 격리할 수 있습니다.

## 컨테이너로 애플리케이션 실행

HoUer OS는 컨테이너 중심 설계로 애플리케이션들을 격리된 환경에서 실행합니다. 다음은 주요 애플리케이션들을 컨테이너로 실행하는 방법입니다:

### 웹 브라우저 (Firefox)
```bash
# Flatpak으로 설치 (권장)
flatpak install flathub org.mozilla.firefox

# 또는 Ubuntu 컨테이너에서 실행
distrobox create --name ubuntu-apps --image ubuntu:latest
distrobox enter ubuntu-apps
sudo apt update && sudo apt install firefox
```

### 개발 환경
```bash
# Ubuntu 개발 컨테이너 생성
distrobox create --name dev-ubuntu --image ubuntu:latest
distrobox enter dev-ubuntu
sudo apt update && sudo apt install git nodejs npm python3 code

# Fedora 개발 컨테이너 생성  
distrobox create --name dev-fedora --image fedora:latest
distrobox enter dev-fedora
sudo dnf install git nodejs npm python3 code
```

### 멀티미디어 애플리케이션
```bash
# GIMP, VLC 등을 Flatpak으로
flatpak install flathub org.gimp.GIMP
flatpak install flathub org.videolan.VLC
flatpak install flathub org.audacityteam.Audacity

# 또는 컨테이너에서
distrobox create --name multimedia --image ubuntu:latest
distrobox enter multimedia
sudo apt install gimp vlc audacity
```

### 오피스 애플리케이션
```bash
# LibreOffice를 Flatpak으로 설치
flatpak install flathub org.libreoffice.LibreOffice

# 또는 컨테이너에서
distrobox enter ubuntu-apps
sudo apt install libreoffice
```

### 게임 및 엔터테인먼트
```bash
# Steam을 Flatpak으로
flatpak install flathub com.valvesoftware.Steam

# Discord
flatpak install flathub com.discordapp.Discord
```

### Windows 애플리케이션 (soda 필요시)
```bash
# 먼저 AUR 헬퍼 설치
cd /tmp && git clone https://aur.archlinux.org/yay.git
cd yay && makepkg -si --noconfirm

# soda 설치 (Windows 컨테이너)
yay -S soda-git

# Windows 애플리케이션 실행
soda run notepad.exe
```

### 직접 패키지 설치 (필요시)
시스템에 직접 설치가 필요한 경우:
```bash
# 시스템 도구들
sudo pacman -S htop neofetch gparted

# 입력기 추가
sudo pacman -S ibus-libpinyin ibus-anthy
```

## 기본 설정

### 디스플레이 서버
- 기본: Wayland
- 대체: X11 (호환성을 위해 설치됨)

### 그래픽 드라이버
- NVIDIA: 자동 감지 및 설치
- AMD: 오픈소스 드라이버 사용
- Intel: 통합 그래픽 지원

### 입력 방법
- ibus 기반 다국어 입력 지원
- 한글, 중국어, 일본어, 베트남어 입력기 포함

## 개발

### 프로젝트 구조
```
HoUer OS/
├── installer/          # 설치 스크립트
│   └── install.sh
├── Manager/            # HoUer Manager 소스코드
│   ├── core/          # 핵심 로직
│   ├── gui/           # GUI 컴포넌트
│   └── assets/        # 리소스 파일
├── docs/              # 문서
└── assets/            # 프로젝트 리소스
```

### 개발 환경 설정

1. 의존성 설치:
```bash
pip install -r requirements.txt
sudo pacman -S distrobox podman python-tk
```

2. HoUer Manager 개발 실행:
```bash
cd Manager
python3 houer-manager.py
```

## 기여하기

1. 이 저장소를 포크하세요
2. 새로운 기능 브랜치를 만드세요 (`git checkout -b feature/AmazingFeature`)
3. 변경사항을 커밋하세요 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 푸시하세요 (`git push origin feature/AmazingFeature`)
5. Pull Request를 열어주세요

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 지원

- **이슈**: GitHub Issues를 통해 버그 리포트 및 기능 요청
- **토론**: GitHub Discussions에서 커뮤니티와 소통
- **문서**: `docs/` 폴더의 추가 문서 참조

## 감사의 말

- [Arch Linux](https://archlinux.org/) - 기반 배포판
- [Enlightenment](https://www.enlightenment.org/) - 데스크톱 환경
- [distrobox](https://github.com/89luca89/distrobox) - Linux 컨테이너 관리
- [Podman](https://podman.io/) - 컨테이너 런타임
- [Calamares](https://calamares.io/) - 설치 프레임워크 
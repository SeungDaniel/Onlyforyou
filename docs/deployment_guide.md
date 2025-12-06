# ☁️ 오라클 클라우드 배포 가이드 (Oracle Cloud Deployment)

이 가이드는 **Miin 봇**을 오라클 클라우드(Oracle Cloud) 프리티어 서버에 배포하여 **24시간 중단 없이 실행**하는 방법을 설명합니다.

---

## 📋 1단계: 깃허브(GitHub) 업로드 (내 컴퓨터)

서버로 코드를 옮기는 가장 쉬운 방법은 GitHub를 이용하는 것입니다.

1.  **GitHub 저장소 생성**:
    *   [GitHub](https://github.com)에 로그인 후 'New Repository'를 클릭합니다.
    *   Repository Name을 입력하고 (예: `miin-bot`), 'Public' 또는 'Private'을 선택한 뒤 'Create repository'를 누릅니다.

2.  **코드 업로드 (터미널)**:
    프로젝트 폴더(`Miin`)에서 아래 명령어를 순서대로 입력하세요.
    ```bash
    git init
    git add .
    git commit -m "Initial commit"
    git branch -M main
    git remote add origin https://github.com/YOUR_USERNAME/miin-bot.git
    # (위 주소는 본인의 저장소 주소로 바꿔주세요!)
    git push -u origin main
    ```

---

## 🖥️ 2단계: 서버 접속 및 설정 (오라클 서버)

1.  **SSH 접속**:
    터미널에서 발급받은 키 파일(`key.key`)을 이용해 서버에 접속합니다.
    ```bash
    ssh -i /path/to/your/key.key ubuntu@YOUR_SERVER_IP
    ```

2.  **필수 프로그램 설치**:
    서버에 접속한 상태에서 아래 명령어를 입력해 Python과 Git을 설치합니다.
    ```bash
    sudo apt update
    sudo apt install python3-venv git -y
    ```

3.  **코드 다운로드**:
    ```bash
    git clone https://github.com/YOUR_USERNAME/miin-bot.git
    cd miin-bot
    ```

4.  **가상환경 설정 및 패키지 설치**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

5.  **환경 변수 설정 (.env)**:
    서버에는 `.env` 파일이 없으므로 직접 만들어야 합니다.
    ```bash
    nano .env
    ```
    *   위 명령어를 치면 편집기가 열립니다.
    *   내 컴퓨터의 `.env` 내용을 복사해서 붙여넣으세요. (`TELEGRAM_TOKEN`, `ADMIN_CHAT_ID` 포함)
    *   `Ctrl + X` -> `Y` -> `Enter`를 눌러 저장하고 나옵니다.

---

## 🚀 3단계: 24시간 무중단 실행 (Systemd)

터미널을 꺼도 봇이 계속 실행되도록 `systemd` 서비스를 등록합니다.

1.  **서비스 파일 생성**:
    ```bash
    sudo nano /etc/systemd/system/miin.service
    ```

2.  **내용 작성**:
    아래 내용을 복사해서 붙여넣으세요. (**주의**: `User`와 `WorkingDirectory` 경로는 본인 서버 환경에 맞게 확인 필요. 보통 `ubuntu` 계정이면 아래 그대로 쓰면 됩니다.)

    ```ini
    [Unit]
    Description=Miin Telegram Bot
    After=network.target

    [Service]
    User=ubuntu
    WorkingDirectory=/home/ubuntu/miin-bot
    ExecStart=/home/ubuntu/miin-bot/venv/bin/python main.py
    Restart=always
    RestartSec=10

    [Install]
    WantedBy=multi-user.target
    ```
    *   `Ctrl + X` -> `Y` -> `Enter`로 저장.

3.  **서비스 시작 및 등록**:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl start miin
    sudo systemctl enable miin
    ```

4.  **상태 확인**:
    ```bash
    sudo systemctl status miin
    ```
    *   초록색 불(`active (running)`)이 들어와 있으면 성공입니다! 🎉

---

## 🔄 업데이트 방법 (코드 수정 시)

내 컴퓨터에서 코드를 수정하고 GitHub에 올린 뒤, 서버에서 아래 명령어를 입력하면 됩니다.

```bash
# 서버 접속 후 프로젝트 폴더로 이동
cd miin-bot

# 최신 코드 받기
git pull

# 봇 재시작 (변경 사항 적용)
sudo systemctl restart miin
```

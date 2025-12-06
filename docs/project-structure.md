# 🏗️ 프로젝트 구조 (Project Structure)

Miin Health Bot의 파일 구조와 각 모듈의 역할에 대한 설명입니다.

```
Miin/
├── bot.py              # 텔레그램 봇 핸들러 및 대화 로직 (View/Controller)
├── config.py           # 환경 변수 및 설정 로드
├── main.py             # 프로그램 진입점 (Entry Point)
├── playlist.py         # 클래식 음악 플레이리스트 데이터 및 추천 로직
├── scheduler.py        # 스케줄링 및 알림 메시지 발송 (Model/Logic)
├── storage.py          # 사용자 데이터(JSON) 저장 및 로드 (Persistence)
├── utils.py            # 유틸리티 함수 (한국어 시간 파싱 등)
├── user_data.json      # 사용자 설정 데이터 저장소 (자동 생성)
├── .env                # 환경 변수 (토큰 등 보안 정보)
├── requirements.txt    # 파이썬 의존성 패키지 목록
└── docs/               # 프로젝트 문서 폴더
    ├── readme.md
    ├── project-structure.md
    ├── user-guide.md
    └── test-guide.md
```

## 📄 파일별 상세 설명

### 1. `main.py`
- **역할**: 봇 애플리케이션을 생성하고 스케줄러를 시작하는 메인 실행 파일입니다.
- **주요 기능**:
    - `bot.py`의 `create_application()` 호출
    - `scheduler.py`의 `ReminderScheduler` 초기화 및 시작
    - 봇 폴링(Polling) 시작

### 2. `bot.py`
- **역할**: 사용자와의 상호작용을 담당합니다. 명령어, 버튼 클릭, 대화 흐름을 처리합니다.
- **주요 기능**:
    - `/start`, `/guide`, `/music` 등 명령어 핸들러
    - `ConversationHandler`를 이용한 대화형 설정(`setup`) 로직
    - 인라인 버튼 콜백 처리 (`button_handler`)

### 3. `scheduler.py`
- **역할**: 정해진 시간에 알림을 보내는 스케줄링 로직을 담당합니다.
- **주요 기능**:
    - `APScheduler`를 이용한 Cron Job 관리
    - 상황별(기상, 오전, 점심, 운동) 랜덤 메시지 및 운동 미션 생성
    - `send_reminder`: 실제 텔레그램 메시지 전송 함수

### 4. `playlist.py`
- **역할**: 클래식 음악 추천을 위한 데이터와 로직을 담고 있습니다.
- **주요 기능**:
    - `PLAYLIST`: 기분별(좋음, 우울, 휴식) 유튜브 링크와 멘트가 담긴 딕셔너리
    - `get_recommendation(mood)`: 해당 무드의 곡을 랜덤으로 반환

### 5. `utils.py`
- **역할**: 헬퍼 함수 모음입니다.
- **주요 기능**:
    - `parse_korean_time(text)`: "오전 9시", "밤 10시반" 같은 한국어 자연어를 `HH:MM` 포맷으로 변환

### 6. `storage.py`
- **역할**: 데이터 영속성을 관리합니다.
- **주요 기능**:
    - `user_data.json` 파일에 사용자별 스케줄 정보를 읽고 씁니다.

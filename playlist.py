import random

# Mood Categories
MOOD_GOOD = "good"
MOOD_DEPRESSED = "depressed"
MOOD_REST = "rest"

# Curated Playlist with YouTube Links
# 사용자가 직접 링크를 채워넣을 수 있도록 구조를 잡아두었습니다.
PLAYLIST = {
    MOOD_GOOD: [
        {
            "title": "Mozart: Piano Sonata No. 16 (K.545) 1st Mvt - Maria João Pires",
            "url": "https://www.youtube.com/watch?v=kUnYGUwatpo&list=RDkUnYGUwatpo&start_radio=1",
            "message": "Miin님! 기분 좋은 날엔 이 곡이죠! 피레스의 맑은 모차르트처럼 오늘 하루도 반짝반짝 빛나세요! ✨"
        },
        {
            "title": "Liszt: Liebestraum No. 3 - Yunchan Lim",
            "url": "https://www.youtube.com/watch?v=zzvzod4ukzo&list=RDzzvzod4ukzo&start_radio=1",
            "message": "sh님의 사랑이 담긴 곡이에요! 임윤찬의 사랑의 꿈... Miin님을 위한 세레나데입니다! 💖"
        },
        {
            "title": "Chopin: Grande Valse Brillante (Op. 18) - Seong-Jin Cho",
            "url": "https://www.youtube.com/watch?v=s_O7q9RIep4&start_radio=1",
            "message": "우아하고 신나게! 랑랑의 왈츠처럼 가벼운 발걸음으로 하루를 즐기세요! 💃"
        },
        {
            "title": "Tchaikovsky: Waltz of the Flowers (Nutcracker) - Berlin Philharmonic",
            "url": "https://www.youtube.com/watch?v=VUF9g9V-Ang&list=RDVUF9g9V-Ang&start_radio=1", # 링크를 넣어주세요
            "message": "꽃들이 춤추는 것 같죠? Miin님의 하루도 이렇게 화사하고 즐거웠으면 좋겠어요! 🌸"
        },
        {
            "title": "Mendelssohn: Spring Song (Songs Without Words) - Yuja Wang",
            "url": "https://youtu.be/mGaruN5VZPA?si=UdQCyFG3-tbca__7", # 링크를 넣어주세요
            "message": "봄바람 같은 설렘을 선물할게요! Miin님 입가에 미소가 번지길 바라요! 😊"
        }
    ],
    MOOD_DEPRESSED: [
        {
            "title": "Schubert: Impromptu Op. 90 No. 3 - Krystian Zimerman",
            "url": "https://youtu.be/dMi9AHqKWWs?si=DrUVKlnXAsByb96g",
            "message": "Miin님, 마음이 무거울 땐 이 곡에 기대세요. 짐머만의 연주가 따뜻하게 안아줄 거예요. ☁️"
        },
        {
            "title": "Rachmaninoff: Piano Concerto No. 2, 2nd Mvt - 강남심포니오케스트라",
            "url": "https://youtu.be/nyse6jm4TUI?si=XMZIxX5S2BjXHZiS",
            "message": "깊은 위로가 필요할 때... 라흐마니노프가 Miin님의 마음을 어루만져 줄 거예요. 1분 클래식의 해설과 함께 들으세요. 힘내세요. ❤️"
        },
        {
            "title": "Beethoven: Piano Concerto No. 5 'Emperor', 2nd Mvt - Cho Seong Jin",
            "url": "https://youtu.be/12kG3NjjrWY?si=gL8I5F8c4BGgEiru",
            "message": "고요하고 숭고한 위로... 조성진의 황제 2악장입니다. 모든 걱정이 사라질 거예요. 🙏"
        },
        {
            "title": "Beethoven: Piano Concerto No. 5 'Emperor', 2nd Mvt - Krystian Zimerman",
            "url": "https://youtu.be/cd9rg9v25bo?si=QLJ8iix7tLoDFsyj",
            "message": "고요하고 숭고한 위로... 짐머만의 황제 2악장입니다. 모든 걱정이 사라질 거예요. 🙏"
        },
        {
            "title": "Elgar: Salut d'Amour (사랑의 인사)",
            "url": "https://youtu.be/ecM7_3rs5gU?si=WtvXanV05Tq5sndX", # 링크를 넣어주세요
            "message": "따뜻한 사랑의 인사를 전해요. sh님이 Miin님을 얼마나 아끼는지 아시죠? 힘내세요! 💕"
        }
    ],
    MOOD_REST: [
        {
            "title": "Debussy: Clair de Lune - Seong-Jin Cho",
            "url": "https://youtu.be/97_VJve7UVc?si=o4vGtRX82hgWy59k",
            "message": "달빛 아래 쉼... 조성진의 드뷔시를 들으며 잠시 눈을 감아보세요. 평온해질 거예요. 🌙"
        },
        {
            "title": "Chopin: Nocturne Op. 9 No. 2 - Maria João Pires",
            "url": "https://www.youtube.com/watch?v=Y7UTWYO25Y4&list=RDY7UTWYO25Y4&start_radio=1",
            "message": "밤의 노래... 피레스의 녹턴이 Miin님을 포근한 꿈속으로 데려갈 거예요. 푹 쉬세요. 🛌"
        },
        {
            "title": "Mozart: Piano Concerto No. 21, 2nd Mvt",
            "url": "https://www.youtube.com/watch?v=df-eLzao63I",
            "message": "구름 위를 걷는 듯한 휴식... 모차르트와 함께 힐링하세요. 🌿"
        }#,
        # {
        #     "title": "Satie: Gymnopédie No. 1 - Philippe Entremont",
        #     "url": "", # 링크를 넣어주세요
        #     "message": "아무 생각 없이 멍하니 있고 싶을 때... 이 곡이 Miin님의 쉼표가 되어줄 거예요. ☕️"
        # },
        # {
        #     "title": "Bach: Air on the G String - Berlin Philharmonic",
        #     "url": "", # 링크를 넣어주세요
        #     "message": "가장 평화로운 선율... 복잡한 마음은 내려놓고 편안하게 숨 쉬세요. 😌"
        # }
    ]
}

'''
☀️ 기분 좋아 (5곡)

모차르트 소나타 16번 (피레스)
리스트 사랑의 꿈 (임윤찬)
쇼팽 화려한 대왈츠 (랑랑)
[NEW] 차이콥스키 꽃의 왈츠
[NEW] 멘델스존 봄노래
☁️ 우울해 (5곡)

슈베르트 즉흥곡 3번 (짐머만)
라흐마니노프 피협 2번 2악장 (조성진)
베토벤 황제 2악장 (임윤찬)
[NEW] 쇼팽 빗방울 전주곡
[NEW] 엘가 사랑의 인사
🌙 쉬고 싶어 (5곡)

드뷔시 달빛 (조성진)
쇼팽 녹턴 2번 (피레스)
모차르트 피협 21번 2악장 (피레스)
[NEW] 사티 짐노페디 1번
[NEW] 바흐 G선상의 아리아
'''

def get_recommendation(mood):
    """Returns a random track for the given mood."""
    if mood in PLAYLIST:
        return random.choice(PLAYLIST[mood])
    return None

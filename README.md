# crawling
selenium library를 사용해서 crawling을 진행하고 있습니다.

# 2021.06.30.
AWS 서버에서 실행해본 결과 윈도우 환경과는 다르게 네트워크에 다양한 원인들로 인해 속도 저하가 발생하게 되는데
이러한 이유로 tiem sleep이나 wait로 페이지가 로드 되는 것을 기다리는 것이 무의미해졌습니다.

time delay를 사용하지 않고 crawling하는 방법을 고안 중입니다. (+일단은 서버에서도 돌아가도록 수정)

## 지역 기반 도서 거래 플랫폼

![서비스 링크]()(chaekhwajeom.pythonanywhere.com)

***



### 서비스 개요 

[Notion 소개 페이지]: https://www.notion.so/421cc69f43534cdbab9a735dae3c1be

* 개발기간: 2020.07 ~ 2020.12(배포)
* 기술스택: Front-End(HTML/CSS, JavaScript), Back-End(Django, AWS RDS)



### 서비스 기능

* 도서 검색 및 등록 (네이버 검색 open API 활용)
* 회원 주소 등록 기능 (Daum 도로명 주소 검색 API 활용)
* 소셜 회원가입/로그인 기능
* slack을 통한 불량 회원 신고 가능(slack API의 opensource library slacker 사용)
* 도서에 대한 리뷰 및 댓글 작성 기능
* 내 서재 관리 및 이웃의 서재 열람 가능


### 구현 내용

* 네이버 검색 open API를 활용한 도서 검색
* Daum 도로명 주소 검색 API를 활용한 주소 등록
* slack API의 opensource library slacker를 활용한 메세지 보내기
* BaseUserManaer, AbstractBaseUser 상속을 통하여 커스터마이징한 User 모델 사용
* 이메일을 활용한 회원인증 및 비밀번호 변경 방식 적용
* AWS RDS를 사용한 PSQL 데이터베이스 생성 및 연결


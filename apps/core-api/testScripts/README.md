# DB 검증 스크립트 (Sprint 1)

이 디렉토리는 Sprint 1에서 정의한 DB 스키마/제약조건이 정상 동작하는지 확인하기 위한 SQL 스크립트를 보관합니다.

## 사전 조건
- Postgres가 Docker로 실행 중이어야 합니다.
- 컨테이너 이름은 `spotlook-postgres` 기준입니다. (확인은 `docker ps`)
- DB/유저: `spotlook`

## 파일 목록
- `db_verify_sprint1.sql`
  - users, posts, hotspots, tags, post_tags, saves 테이블에 대해 최소 테스트 데이터를 삽입합니다.
  - 각 테이블 row count를 출력합니다.
  - 마지막에 `hotspots.x`에 대해 의도적으로 CHECK 제약 위반(x > 1)을 발생시켜 제약이 실제로 동작하는지 확인합니다.

## 실행 방법 (권장: 컨테이너로 복사 후 실행)
레포 루트 기준(또는 SQL 파일이 존재하는 위치 기준)에서 아래를 실행합니다.

```bash
docker cp apps/core-api/testScripts/db_verify_sprint1.sql spotlook-postgres:/tmp/db_verify_sprint1.sql
docker exec -it spotlook-postgres psql -U spotlook -d spotlook -f /tmp/db_verify_sprint1.sql
```

### 기대 결과

트랜잭션이 정상 수행되어야 합니다.

**BEGIN**

**INSERT ...**

**COMMIT**

테이블별 row count 요약이 출력되어야 합니다.

예시:
```lua
 table   | count
---------+------
 users   |  ...
 posts   |  ...
 ...
```

스크립트 마지막에 아래와 같은 에러가 발생해야 정상입니다.

**violates check constraint "ck_hotspots_x_0_1"**

이 에러는 CHECK 제약이 실제로 동작함을 확인하기 위한 “의도된 실패”입니다.

### 참고 / 트러블슈팅

**current transaction is aborted**가 보이면, BEGIN 블록 안에서 이전 쿼리가 이미 실패해 트랜잭션이 중단(abort)된 상태입니다.

인터랙티브 실행 중이라면 **ROLLBACK;** 후 원인 쿼리를 먼저 해결하세요.

개발 환경에서 반복 실행을 위해 데이터를 초기화하려면(주의: dev only):
```sql
TRUNCATE TABLE
  post_tags,
  saves,
  hotspots,
  tags,
  posts,
  users
RESTART IDENTITY CASCADE;
```
\set ON_ERROR_STOP on

BEGIN;

-- 0) 테스트 데이터(재실행 가능)
WITH u1 AS (
  INSERT INTO users (email, password_hash)
  VALUES ('test1@example.com', 'hash')
  ON CONFLICT (email) DO UPDATE SET password_hash = EXCLUDED.password_hash
  RETURNING id
),
u1_id AS (
  SELECT id FROM u1
  UNION ALL
  SELECT id FROM users WHERE email='test1@example.com'
  LIMIT 1
),
u2 AS (
  INSERT INTO users (email, password_hash)
  VALUES ('test2@example.com', 'hash')
  ON CONFLICT (email) DO UPDATE SET password_hash = EXCLUDED.password_hash
  RETURNING id
),
u2_id AS (
  SELECT id FROM u2
  UNION ALL
  SELECT id FROM users WHERE email='test2@example.com'
  LIMIT 1
),
p AS (
  INSERT INTO posts (user_id, caption, visibility, image_width, image_height)
  SELECT id, 'hello', 'public', 1000, 500 FROM u2_id
  RETURNING id
),
t AS (
  INSERT INTO tags (name)
  VALUES ('cafe')
  ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
  RETURNING id
),
tag_id AS (
  SELECT id FROM t
  UNION ALL
  SELECT id FROM tags WHERE name='cafe'
  LIMIT 1
),
hs AS (
  INSERT INTO hotspots (post_id, x, y)
  SELECT p.id, 0.25, 0.5 FROM p
  RETURNING id
),
pt AS (
  INSERT INTO post_tags (post_id, tag_id)
  SELECT p.id, tag_id.id FROM p, tag_id
  ON CONFLICT DO NOTHING
  RETURNING post_id
)
INSERT INTO saves (user_id, post_id)
SELECT u2_id.id, p.id FROM u2_id, p
ON CONFLICT DO NOTHING;

COMMIT;

-- 1) 결과 확인(간단)
SELECT 'users' AS table, count(*) FROM users
UNION ALL SELECT 'posts', count(*) FROM posts
UNION ALL SELECT 'hotspots', count(*) FROM hotspots
UNION ALL SELECT 'tags', count(*) FROM tags
UNION ALL SELECT 'post_tags', count(*) FROM post_tags
UNION ALL SELECT 'saves', count(*) FROM saves;

-- 2) 제약조건 실패 테스트(의도적으로 에러 내기)
-- hotspots 체크 위반: x > 1
-- 이 줄이 에러나면 정상. ON_ERROR_STOP 때문에 여기서 멈춤.
INSERT INTO hotspots (post_id, x, y)
SELECT id, 2.0, 0.1 FROM posts LIMIT 1;
